# Trader 21 – S&P 500 Screener

Gotowy skrypt do automatycznego przeszukiwania wszystkich spółek z S&P 500 według Twoich kryteriów Trader 21.

## Jak uruchomić w Google Colab (najłatwiej)

1. Wejdź na repo: https://github.com/Photofiver/trader21-sp500-screener
2. Kliknij plik `trader21_sp500_screener.py`
3. Kliknij przycisk **Raw** (prawy górny róg)
4. Skopiuj cały kod
5. Otwórz nowy notebook w Google Colab (colab.research.google.com)
6. Wklej kod do pierwszej komórki i uruchom (Shift+Enter)

Lub po prostu kliknij ten link i wklej kod:
https://colab.research.google.com

## Co robi skrypt
- Pobiera aktualną listę ~500 spółek S&P 500
- Analizuje dane fundamentalne i techniczne
- Stosuje filtry i scoring inspirowany Trader 21
- Zapisuje wyniki do pliku Excel (gotowy do pobrania z Colab)

## Jak dostosować kryteria
Na górze pliku `trader21_sp500_screener.py` znajdziesz sekcję **PARAMETRY DO EDYCJI** – zmień wartości według swoich zasad (P/E, ROE, wzrost, dług, volume flip, SuperTrend itp.).

## Wymagania
Działa w Google Colab bez instalacji lokalnej.

Stworzone dla Ciebie przez Grok – maj 2026