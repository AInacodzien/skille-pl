# mcp-yr

Mały serwer MCP (Streamable HTTP) do Google AI Edge Gallery. Dwa narzędzia:

- `pogoda(miejsce)` – prognoza z Yr / MET Norway (domyślnie Figgjo)
- `wikipedia(temat, jezyk)` – krótkie streszczenie artykułu (pl / no / en)

## Uruchomienie
```
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python server.py
```
Adres w aplikacji: `http://<IP-komputera>:8000/mcp`

Uwaga: serwer nie ma uwierzytelniania. Używaj w domowej sieci Wi-Fi.
