# analysis/regression.py

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import PORTFOLIO, MACRO_INDICATORS
import warnings
warnings.filterwarnings('ignore')

def fetch_historical_data(ticker, start, end=None):
    if end is None:
        end = datetime.now().strftime("%Y-%m-%d")
    try:
        data = yf.download(ticker, start=start, end=end, progress=False)
        if data.empty:
            return None
        return data['Close']
    except:
        return None

def calculate_returns(prices):
    return prices.pct_change() * 100

def get_stock_sensitivities(start):
    macro_tickers = list(MACRO_INDICATORS.keys())
    results = []
    
    print("📊 Calculating stock sensitivities...")
    
    for stock_ticker in PORTFOLIO.keys():
        print(f"  {stock_ticker}...", end=" ", flush=True)
        
        stock_prices = fetch_historical_data(stock_ticker, start)
        if stock_prices is None:
            print("❌")
            continue
        
        stock_returns = calculate_returns(stock_prices).dropna()
        
        for macro_name in macro_tickers:
            macro_ticker = MACRO_INDICATORS[macro_name]['ticker']
            macro_prices = fetch_historical_data(macro_ticker, start)
            
            if macro_prices is None:
                continue
            
            macro_returns = calculate_returns(macro_prices).dropna()
            aligned = pd.concat([stock_returns, macro_returns], axis=1).dropna()
            
            if len(aligned) < 30:
                continue
            
            corr = aligned.iloc[:, 0].corr(aligned.iloc[:, 1])
            beta = corr * (aligned.iloc[:, 0].std() / aligned.iloc[:, 1].std())
            
            results.append({
                'stock': stock_ticker,
                'sector': PORTFOLIO[stock_ticker]['sector'],
                'macro': macro_name,
                'beta': round(beta, 3),
            })
        
        print("✅")
    
    return pd.DataFrame(results)
def get_sector_sensitivities(start):
    """
    Calculate sector-level sensitivities
    """
    # Group by sector
    sectors = {}
    for ticker, info in PORTFOLIO.items():
        sector = info['sector']
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(ticker)
    
    macro_tickers = list(MACRO_INDICATORS.keys())
    results = []
    
    print("\n📊 Calculating sector sensitivities...")
    
    for sector, tickers in sectors.items():
        print(f"  {sector}...", end=" ", flush=True)
        
        # Get sector average returns
        sector_prices = []
        for ticker in tickers:
            prices = fetch_historical_data(ticker, start)
            if prices is not None:
                sector_prices.append(prices)
        
        if not sector_prices:
            print("❌")
            continue
        
        sector_avg = pd.concat(sector_prices, axis=1).mean(axis=1)
        sector_returns = calculate_returns(sector_avg).dropna()
        
        # Calculate sensitivities
        for macro_name in macro_tickers:
            macro_ticker = MACRO_INDICATORS[macro_name]['ticker']
            macro_prices = fetch_historical_data(macro_ticker, start)
            
            if macro_prices is None:
                continue
            
            macro_returns = calculate_returns(macro_prices).dropna()
            aligned = pd.concat([sector_returns, macro_returns], axis=1).dropna()
            
            if len(aligned) < 30:
                continue
            
            corr = aligned.iloc[:, 0].corr(aligned.iloc[:, 1])
            beta = corr * (aligned.iloc[:, 0].std() / aligned.iloc[:, 1].std())
            
            results.append({
                'sector': sector,
                'macro': macro_name,
                'beta': round(beta, 3),
            })
        
        print("✅")
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    print("=" * 60)
    print("Stock Sensitivities Test")
    print("=" * 60)
    
    start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    
    try:
        stock_sens = get_stock_sensitivities(start=start_date)
        print("\nResults:")
        print(stock_sens.to_string(index=False))
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()