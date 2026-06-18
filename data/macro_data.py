# data/macro_data.py
# Macro Indicators Data Collection

import yfinance as yf
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import MACRO_INDICATORS, HISTORICAL_START
import warnings
warnings.filterwarnings('ignore')

def fetch_macro_data(ticker: str, start: str) -> pd.DataFrame:
    """Fetch macro indicator data from Yahoo Finance"""
    try:
        end = datetime.now().strftime("%Y-%m-%d")
        data = yf.download(ticker, start=start, end=end, progress=False)
        
        if data.empty:
            return pd.DataFrame()
        
        return data[['Close']].copy()
    except:
        return pd.DataFrame()

def get_all_macro_indicators(start: str = HISTORICAL_START) -> dict:
    """Fetch all macro indicators"""
    macro_data = {}
    print("📊 Fetching macro indicators...")
    
    for name, info in MACRO_INDICATORS.items():
        ticker = info['ticker']
        print(f"  ⏳ {name}...", end=" ", flush=True)
        
        data = fetch_macro_data(ticker, start)
        
        if not data.empty:
            data.columns = [name]
            macro_data[name] = data
            print(f"✅ {len(data)} records")
        else:
            print(f"⚠️ No data")
    
    return macro_data

def get_recent_snapshot() -> pd.DataFrame:
    """Get recent macro snapshot (current price + 1-day change)"""
    snapshots = []
    
    for name, info in MACRO_INDICATORS.items():
        ticker = info['ticker']
        try:
            data = yf.download(ticker, period="5d", progress=False)
            
            if len(data) >= 2:
                current_price = data['Close'].iloc[-1].item()
                previous_price = data['Close'].iloc[-2].item()
                change_pct = ((current_price - previous_price) / previous_price) * 100
                
                snapshots.append({
                    "indicator": name,
                    "price": round(current_price, 2),
                    "1d_change_%": round(change_pct, 2),
                })
        except:
            continue
    
    return pd.DataFrame(snapshots)

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Macro Data Collection")
    print("=" * 60)
    
    snapshot = get_recent_snapshot()
    print("\n📊 Recent Macro Snapshot:")
    print(snapshot.to_string(index=False))
    print("=" * 60)