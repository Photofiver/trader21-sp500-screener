# Trader 21 S&P 500 Screener - Gotowy do Google Colab
# Uruchom cały kod w Colab (wklej do jednej komórki lub kilka)

!pip install yfinance pandas tqdm openpyxl requests beautifulsoup4 lxml -q

import yfinance as yf
import pandas as pd
from tqdm import tqdm
import warnings
import numpy as np
warnings.filterwarnings('ignore')

# ============================================
# === PARAMETRY DO EDYCJI - Trader 21 ===
# ============================================

MIN_MARKET_CAP_B = 10          # mld USD
MAX_PE = 40
MIN_ROE = 0.10                 # 10%
MIN_PROFIT_MARGIN = 0.08       # 8%
MIN_REVENUE_GROWTH_YOY = 0.05  # 5% rocznie
MAX_DEBT_EQUITY = 1.5
MIN_ADX = 20                   # siła trendu
RSI_MAX = 70                   # nie overbought
VOLUME_INCREASE_PCT = 50       # wzrost volume vs średnia

# Wagi punktowe (możesz zmieniać)
WEIGHT_FUNDAMENTAL = 0.6
WEIGHT_TECHNICAL = 0.4

print("Trader 21 S&P 500 Screener - start...")

# ============================================
# Pobieranie listy S&P 500
# ============================================
def get_sp500_tickers():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    try:
        tables = pd.read_html(url, header=0)
        df = tables[0]
        tickers = df['Symbol'].tolist()
        print(f"Znaleziono {len(tickers)} spółek S&P 500")
        return tickers
    except Exception as e:
        print("Błąd pobierania listy:", e)
        return []

# ============================================
# Prosta implementacja SuperTrend (dla techniki)
# ============================================
def calculate_supertrend(df, period=10, multiplier=3):
    hl2 = (df['High'] + df['Low']) / 2
    atr = pd.Series(0.0, index=df.index)
    for i in range(1, len(df)):
        tr = max(df['High'].iloc[i] - df['Low'].iloc[i],
                 abs(df['High'].iloc[i] - df['Close'].iloc[i-1]),
                 abs(df['Low'].iloc[i] - df['Close'].iloc[i-1]))
        atr.iloc[i] = (atr.iloc[i-1] * (period - 1) + tr) / period if i > 0 else tr
    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)
    supertrend = pd.Series(True, index=df.index)
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > upperband.iloc[i-1]:
            supertrend.iloc[i] = True
        elif df['Close'].iloc[i] < lowerband.iloc[i-1]:
            supertrend.iloc[i] = False
        else:
            supertrend.iloc[i] = supertrend.iloc[i-1]
    return supertrend

# ============================================
# Pobieranie i analiza jednej spółki
# ============================================
def analyze_ticker(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="6mo", auto_adjust=True)
        if hist.empty or len(hist) < 60:
            return None

        # Fundamentalne
        market_cap = info.get('marketCap', 0) or 0
        pe = info.get('trailingPE') or info.get('forwardPE') or 999
        roe = info.get('returnOnEquity') or 0
        profit_margin = info.get('profitMargins') or 0
        revenue_growth = info.get('revenueGrowth') or 0
        debt_equity = info.get('debtToEquity') or 999

        # Techniczne
        hist['Volume_MA'] = hist['Volume'].rolling(20).mean()
        volume_increase = ((hist['Volume'].iloc[-1] / hist['Volume_MA'].iloc[-1]) - 1) * 100 if hist['Volume_MA'].iloc[-1] > 0 else 0

        hist['RSI'] = 100 - (100 / (1 + (hist['Close'].diff().where(lambda x: x > 0, 0).rolling(14).mean() / 
                                           hist['Close'].diff().where(lambda x: x < 0, 0).abs().rolling(14).mean())))
        rsi = hist['RSI'].iloc[-1]

        hist['SuperTrend'] = calculate_supertrend(hist)
        above_supertrend = hist['SuperTrend'].iloc[-1]

        adx = 25  # uproszczone - możesz rozbudować

        # Scoring (0-100)
        fund_score = 0
        if market_cap > MIN_MARKET_CAP_B * 1e9: fund_score += 15
        if pe < MAX_PE: fund_score += 15
        if roe > MIN_ROE: fund_score += 15
        if profit_margin > MIN_PROFIT_MARGIN: fund_score += 10
        if revenue_growth > MIN_REVENUE_GROWTH_YOY: fund_score += 10
        if debt_equity < MAX_DEBT_EQUITY: fund_score += 10

        tech_score = 0
        if volume_increase > VOLUME_INCREASE_PCT: tech_score += 20
        if above_supertrend: tech_score += 20
        if rsi < RSI_MAX: tech_score += 15
        if adx > MIN_ADX: tech_score += 10

        total_score = (fund_score * WEIGHT_FUNDAMENTAL) + (tech_score * WEIGHT_TECHNICAL)

        grade = 'A' if total_score >= 75 else 'B' if total_score >= 60 else 'C' if total_score >= 45 else 'D' if total_score >= 30 else 'F'

        return {
            'Ticker': ticker,
            'Name': info.get('shortName', ticker),
            'Sector': info.get('sector', 'N/A'),
            'MarketCap_B': round(market_cap / 1e9, 1),
            'PE': round(pe, 1) if pe < 999 else 'N/A',
            'ROE_%': round(roe * 100, 1),
            'ProfitMargin_%': round(profit_margin * 100, 1),
            'RevGrowth_%': round(revenue_growth * 100, 1),
            'DebtEquity': round(debt_equity, 2) if debt_equity < 999 else 'N/A',
            'VolumeIncrease_%': round(volume_increase, 1),
            'AboveSuperTrend': above_supertrend,
            'RSI': round(rsi, 1),
            'Score': round(total_score, 1),
            'Grade': grade
        }
    except Exception as e:
        return None

# ============================================
# Główna pętla
# ============================================
tickers = get_sp500_tickers()
results = []

print("Analizuję spółki... (może potrwać 3-8 minut)")
for t in tqdm(tickers, desc="S&P 500"):
    data = analyze_ticker(t)
    if data:
        results.append(data)

if results:
    df = pd.DataFrame(results)
    df = df.sort_values('Score', ascending=False)
    print("\n=== TOP 20 według Trader 21 ===")
    print(df.head(20).to_string(index=False))
    
    filename = 'Trader21_SP500_Results.xlsx'
    df.to_excel(filename, index=False)
    print(f"\n✓ Zapisano wyniki do: {filename}")
    print("Pobierz plik z lewego panelu w Colab.")
else:
    print("Nie udało się pobrać danych.")

print("\nGotowe! Edytuj parametry na górze i uruchom ponownie.")