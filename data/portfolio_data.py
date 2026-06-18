# data/portfolio_data.py
# Portfolio Data Collection

import yfinance as yf
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import PORTFOLIO
import warnings
warnings.filterwarnings('ignore')

def fetch_stock_data(ticker: str, start: str = "2024-01-01") -> pd.DataFrame:
    """Fetch individual stock data"""
    try:
        end = datetime.now().strftime("%Y-%m-%d")
        data = yf.download(ticker, start=start, end=end, progress=False)
        
        if data.empty:
            return pd.DataFrame()
        
        return data[['Close']].copy()
    except:
        return pd.DataFrame()

def get_portfolio_snapshot() -> pd.DataFrame:
    """Get current portfolio snapshot (current price + 1-day change)"""
    tickers = list(PORTFOLIO.keys())
    rows = []
    
    print("📈 Fetching portfolio data...")
    
    for ticker in tickers:
        print(f"  ⏳ {ticker}...", end=" ", flush=True)
        
        try:
            data = yf.download(ticker, period="5d", progress=False)
            
            if len(data) >= 2:
                current_price = data['Close'].iloc[-1].item()
                previous_price = data['Close'].iloc[-2].item()
                change_pct = ((current_price - previous_price) / previous_price) * 100
                
                rows.append({
                    "ticker": ticker,
                    "name": PORTFOLIO[ticker]["name"],
                    "sector": PORTFOLIO[ticker]["sector"],
                    "price": round(current_price, 2),
                    "1d_change_%": round(change_pct, 2),
                })
                print(f"✅")
            else:
                print(f"⚠️ No data")
        except Exception as e:
            print(f"❌")
    
    return pd.DataFrame(rows)

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Portfolio Data Collection")
    print("=" * 60)
    
    portfolio = get_portfolio_snapshot()
    print("\n📊 Portfolio Snapshot:")
    print(portfolio.to_string(index=False))
    print("=" * 60)