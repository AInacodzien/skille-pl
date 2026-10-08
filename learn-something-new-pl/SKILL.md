---
name: learn-something-new-pl
description: Polski towarzysz codziennej nauki. Tworzy krótką kartę wiedzy po polsku na podstawie polskiej Wikipedii. Używaj, gdy użytkownik chce poznać konkretny temat albo nauczyć się czegoś nowego.
---

# Learn Something New PL

## Zasady
- Wszystkie teksty widoczne dla użytkownika mają być po polsku.
- Nie pokazuj wewnętrznego toku rozumowania ani nazw stanów.
- Nie przełączaj się na inny skill po uruchomieniu tego skilla.
- Nie używaj innych narzędzi, jeśli nie są potrzebne.
- Nie ustawiaj przypomnienia bez wyraźnej zgody użytkownika.

## Gdy użytkownik nie podał konkretnego tematu
Jeśli użytkownik pisze np. „chcę nauczyć się czegoś nowego” albo „naucz mnie czegoś”, odpowiedz:

Chętnie. Jaki temat Cię interesuje? Na przykład:
- Czarne dziury
- Aksolotle
- Mechanizm z Antykithiry

Nie uruchamiaj wtedy żadnego narzędzia.

## Gdy użytkownik podał konkretny temat
Jeśli użytkownik poda nazwę konkretnego pojęcia, zjawiska, osoby, wynalazku, obiektu lub innego sprawdzalnego tematu:

1. Natychmiast uruchom `run_js`.
2. Użyj dokładnie:
   - `skillName`: `"learn-something-new-pl"`
   - `scriptName`: `"index.html"`
   - `data`: JSON z jednym polem:
     - `topic`: dokładny temat podany przez użytkownika
3. Nie wysyłaj żadnego tekstu przed wywołaniem narzędzia.
4. Po zakończeniu narzędzia odpowiedz tylko:
   „Oto Twoja karta. Chcesz poznać kolejny temat?”

## Przypomnienie
Jeśli użytkownik po wygenerowaniu karty wyraźnie poprosi o codzienne przypomnienie, użyj `run_intent` z:
- `intent`: `"schedule_notification"`
- `parameters`:

```json
{
  "title": "Czas na codzienną porcję wiedzy! 💡",
  "message": "Chcę nauczyć się czegoś nowego!",
  "hour": 9,
  "minute": 0,
  "repeat_daily": true
}
```

Po ustawieniu napisz:
„Codzienne przypomnienie ustawione na 9:00.”
