# analysis/correlation.py
# Correlation Analysis between Macro Indicators and Portfolio Holdings

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

def fetch_historical_data(ticker: str, start: str, end: str = None) -> pd.DataFrame:
    """Fetch historical price data"""
    if end is None:
        end = datetime.now().strftime("%Y-%m-%d")
    
    try:
        data = yf.download(ticker, start=start, end=end, progress=False)
        if data.empty:
            return pd.DataFrame()
        return data[['Close']].copy()
    except:
        return pd.DataFrame()

def calculate_returns(prices: pd.Series, periods: list = [1, 5, 20]) -> pd.DataFrame:
    """Calculate daily, weekly, monthly returns"""
    returns = pd.DataFrame(index=prices.index)
    
    for period in periods:
        returns[f'return_{period}d'] = prices.pct_change(periods=period) * 100
    
    return returns

def get_macro_portfolio_correlation(start: str, end: str = None) -> pd.DataFrame:
    """
    Calculate correlation between macro indicators and portfolio holdings
    """
    if end is None:
        end = datetime.now().strftime("%Y-%m-%d")
    
    print("📊 Calculating macro-portfolio correlation...")
    
    # Fetch macro data
    macro_data = {}
    for name, info in MACRO_INDICATORS.items():
        ticker = info['ticker']
        data = fetch_historical_data(ticker, start, end)
        if not data.empty:
            macro_data[name] = data['Close']
    
    # Fetch portfolio data
    portfolio_data = {}
    for ticker in PORTFOLIO.keys():
        data = fetch_historical_data(ticker, start, end)
        if not data.empty:
            portfolio_data[ticker] = data['Close']
    
    # Combine all data
    all_data = pd.concat(list(macro_data.values()) + list(portfolio_data.values()), axis=1)
    all_data.columns = list(macro_data.keys()) + list(portfolio_data.keys())
    all_data = all_data.dropna()
    
    # Calculate correlation
    correlation_matrix = all_data.corr()
    
    return correlation_matrix

def get_sector_macro_correlation(start: str, end: str = None) -> pd.DataFrame:
    """
    Calculate correlation between macro indicators and sector performance
    """
    if end is None:
        end = datetime.now().strftime("%Y-%m-%d")
    
    print("📊 Calculating sector-macro correlation...")
    
    # Group tickers by sector
    sectors = {}
    for ticker, info in PORTFOLIO.items():
        sector = info['sector']
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(ticker)
    
    # Calculate sector returns (average of holdings)
    sector_returns = {}
    for sector, tickers in sectors.items():
        sector_prices = []
        for ticker in tickers:
            data = fetch_historical_data(ticker, start, end)
            if not data.empty:
                sector_prices.append(data['Close'])
        
        if sector_prices:
            sector_returns[sector] = pd.concat(sector_prices, axis=1).mean(axis=1)
    
    # Fetch macro data
    macro_data = {}
    for name, info in MACRO_INDICATORS.items():
        ticker = info['ticker']
        data = fetch_historical_data(ticker, start, end)
        if not data.empty:
            macro_data[name] = data['Close']
    
    # Combine and correlate
    all_data = pd.concat(list(macro_data.values()) + list(sector_returns.values()), axis=1)
    all_data.columns = list(macro_data.keys()) + list(sector_returns.keys())
    all_data = all_data.dropna()
    
    correlation_matrix = all_data.corr()
    
    # Return only macro vs sector correlations
    return correlation_matrix.loc[list(macro_data.keys()), list(sector_returns.keys())]

def get_rolling_correlation(ticker1: str, ticker2: str, start: str, window: int = 60) -> pd.DataFrame:
    """Calculate rolling correlation between two assets"""
    end = datetime.now().strftime("%Y-%m-%d")
    
    data1 = fetch_historical_data(ticker1, start, end)
    data2 = fetch_historical_data(ticker2, start, end)
    
    if data1.empty or data2.empty:
        return pd.DataFrame()
    
    # Calculate returns
    returns1 = data1['Close'].pct_change()
    returns2 = data2['Close'].pct_change()
    
    # Calculate rolling correlation
    rolling_corr = returns1.rolling(window).corr(returns2)
    
    return pd.DataFrame({
        'date': rolling_corr.index,
        'correlation': rolling_corr.values
    })

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Correlation Analysis")
    print("=" * 60)
    
    # Test 1: Macro-Portfolio correlation (1 year)
    print("\n1️⃣ Macro-Portfolio Correlation (Last 1 year):")
    start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    corr_matrix = get_macro_portfolio_correlation(start=start_date)
    
    # Show only macro vs portfolio correlations
    macro_names = list(MACRO_INDICATORS.keys())
    portfolio_tickers = list(PORTFOLIO.keys())
    
    macro_portfolio_corr = corr_matrix.loc[macro_names, portfolio_tickers]
    print(macro_portfolio_corr.round(3))
    
    # Test 2: Sector-Macro correlation
    print("\n2️⃣ Sector-Macro Correlation (Last 1 year):")
    sector_corr = get_sector_macro_correlation(start=start_date)
    print(sector_corr.round(3))
    
    print("\n" + "=" * 60)