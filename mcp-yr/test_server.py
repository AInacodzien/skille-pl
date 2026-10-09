"""Test na atrapie danych (bez sieci): lista narzędzi + wywołania przez HTTP."""
import asyncio, threading, time
import server
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

MET = {"properties": {"timeseries": [
    {"time": f"2026-10-09T{h:02d}:00:00Z", "data": {
        "instant": {"details": {"air_temperature": 8.4, "wind_speed": 5.2}},
        "next_1_hours": {"summary": {"symbol_code": "partlycloudy_day"}},
        "next_6_hours": {"summary": {"symbol_code": "lightrain"},
                         "details": {"air_temperature_min": 6.0, "air_temperature_max": 9.0, "precipitation_amount": 1.3}}}}
    for h in range(0, 24)]}}
WIKI = {"title": "Mechanizm z Antykithiry", "extract": "To starożytne urządzenie. " * 100}

def fake(url, params=None, ttl=0):
    if "met.no" in url: return MET
    if "NieMa" in url:
        import httpx; raise httpx.HTTPStatusError("x", request=None, response=type("R", (), {"status_code": 404})())
    return WIKI
server.fetch_json = fake

def run():
    server.mcp.settings.host, server.mcp.settings.port = "0.0.0.0", 8765
    server.mcp.run(transport="streamable-http")
threading.Thread(target=run, daemon=True).start(); time.sleep(2)

async def main():
    async with streamablehttp_client("http://127.0.0.1:8765/mcp") as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            print("NARZĘDZIA:", [t.name for t in (await s.list_tools()).tools])
            for name, args in [("pogoda", {}), ("pogoda", {"miejsce": "Paryż"}),
                               ("wikipedia", {"temat": "Mechanizm z Antykithiry"}),
                               ("wikipedia", {"temat": "NieMa"})]:
                res = await s.call_tool(name, args)
                txt = res.content[0].text
                print(f"\n--- {name} {args} ({len(txt)} zn.)\n{txt[:500]}")
asyncio.run(main())
