# Coc Builder Base Bot

Projekt z botem do automatyzacji Builder Base. Glowna wersja znajduje sie w `src/bot_pico_2_fazy.py`.

## Struktura

```text
src/
  bot_pico_2_fazy.py        # aktualny bot Pico, wersja V70.0

assets/templates/
  *.png                     # obrazki uzywane przez OpenCV/template matching

tools/
  koordynaty.py             # pomocniczy lokalizator pozycji kursora

debug/
  *.png, *.jpg              # lokalne zrzuty/debug, domyslnie ignorowane przez Git
```

## Instalacja

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Uruchamianie

Aktualny bot:

```powershell
python .\src\bot_pico_2_fazy.py
```

Pomocniczy podglad pozycji kursora:

```powershell
python .\tools\koordynaty.py
```

## Konfiguracja

Najwazniejsze parametry sa na gorze plikow w `src/`. Dla wersji Pico sprawdz zwlaszcza:

- `PICO_PORT`, domyslnie `COM11`
- czasy sesji i przerw
- progi confidence dla rozpoznawania obrazkow
- wspolrzedne triggera drugiej fazy

Obrazki rozpoznawane przez OpenCV sa trzymane w `assets/templates/`. Aktywne skrypty uzywaja sciezek wzgledem katalogu projektu, wiec nie trzeba trzymac PNG w glownym folderze.

## Mikrokontroler

Projekt uzywa mikrokontrolera jako warstwy inputu. Python nie wykonuje klikniec bezposrednio w grze: analizuje ekran, wybiera akcje, a potem wysyla proste komendy przez port szeregowy do Pico.

Po stronie mikrokontrolera powinien dzialac firmware, ktory:

- laczy sie z komputerem jako urzadzenie USB HID Mouse
- odbiera komendy tekstowe przez Serial z predkoscia `115200`
- wykonuje ruchy myszy, klikniecia i przeciaganie jako fizyczny input

Protokol uzywany przez `src/bot_pico_2_fazy.py`:

```text
M dx dy    # relatywny ruch myszy o dx, dy
C          # pojedyncze klikniecie lewym przyciskiem
D          # przytrzymanie lewego przycisku
U          # puszczenie lewego przycisku
```

Kazda komenda jest wysylana jako osobna linia zakonczona `\n`. Przyklad: `M 12 -4`.

Kod firmware mikrokontrolera nie jest obecnie czescia repozytorium. Ten projekt zaklada, ze Pico jest juz wgrane i dostepne pod portem ustawionym w `PICO_PORT`.

## Pierwszy push na GitHub

Repozytorium Git jest juz zainicjalizowane lokalnie. Po utworzeniu pustego repo na GitHubie:

```powershell
git add .
git commit -m "Initial project cleanup"
git branch -M main
git remote add origin https://github.com/TWOJ_LOGIN/TWOJE_REPO.git
git push -u origin main
```
