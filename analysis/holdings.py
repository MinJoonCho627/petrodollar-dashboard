# analysis/holdings.py
# Actual brokerage holdings (Mirae Asset, USD) + Core/Satellite return separation
#
# DESIGN: Only HARD facts are stored (shares, cost). These don't change.
# Current value & return are computed LIVE from yfinance every call,
# so returns are always current -- no stale hardcoded valuations.
# Last cost sync: 2026-06-18 (from brokerage app, USD)

import yfinance as yf

# cost = total purchase amount in USD (does NOT change once bought)
HOLDINGS = {
    # --- CORE (hypothesis-validation capital) ---
    "PL":   {"name": "Planet Labs",                          "shares": 8, "cost": 122.40, "group": "core"},
    "COPX": {"name": "Global X Copper Miners ETF",           "shares": 1, "cost": 62.41,  "group": "core"},
    "TSES": {"name": "Truth Social American Energy Security", "shares": 4, "cost": 104.92, "group": "core"},
    "TSNF": {"name": "Truth Social American Next Frontiers",  "shares": 5, "cost": 136.50, "group": "core"},

    # --- SATELLITE (side bets, excluded from hypothesis validation) ---
    "HOOD": {"name": "Robinhood Markets",   "shares": 1, "cost": 74.86,  "group": "satellite"},
    "IONQ": {"name": "IonQ",                "shares": 1, "cost": 56.01,  "group": "satellite"},
    "BMNR": {"name": "Bitmine",             "shares": 7, "cost": 121.66, "group": "satellite"},
    "RXRX": {"name": "Recursion Pharma",    "shares": 6, "cost": 37.50,  "group": "satellite"},
}

CLOSED_POSITIONS = {
    "URA": {
        "name": "Uranium ETF",
        "exit_date": "2026-06-18",
        "realized_return_%": -7.65,
        "exit_reason": "Iran deal triggered pre-defined failure condition. Original thesis closed.",
    },
}


def _get_prices():
    """Fetch live prices for all held tickers. Returns {ticker: price or None}."""
    prices = {}
    for ticker in HOLDINGS:
        try:
            prices[ticker] = float(yf.Ticker(ticker).fast_info["lastPrice"])
        except Exception:
            prices[ticker] = None
    return prices


def get_position_returns(prices=None):
    """Per-position live return. Falls back gracefully if a price is missing."""
    if prices is None:
        prices = _get_prices()
    out = {}
    for ticker, h in HOLDINGS.items():
        price = prices.get(ticker)
        if price is None:
            out[ticker] = {"name": h["name"], "group": h["group"], "cost": h["cost"],
                           "value": None, "return_%": None, "price": None}
            continue
        value = h["shares"] * price
        ret = (value - h["cost"]) / h["cost"] * 100 if h["cost"] > 0 else 0.0
        out[ticker] = {"name": h["name"], "group": h["group"], "cost": h["cost"],
                       "value": round(value, 2), "return_%": round(ret, 2), "price": round(price, 2)}
    return out


def get_separated_performance(prices=None):
    """Core vs Satellite vs Total -- computed live."""
    pos = get_position_returns(prices)

    def agg(group):
        # only include positions with a valid live value
        cost = sum(p["cost"] for t, p in pos.items() if HOLDINGS[t]["group"] == group and p["value"] is not None)
        value = sum(p["value"] for t, p in pos.items() if HOLDINGS[t]["group"] == group and p["value"] is not None)
        ret = (value - cost) / cost * 100 if cost > 0 else 0.0
        return {"cost": round(cost, 2), "value": round(value, 2), "return_%": round(ret, 2)}

    core = agg("core")
    sat = agg("satellite")
    total_cost = core["cost"] + sat["cost"]
    total_value = core["value"] + sat["value"]
    total_ret = (total_value - total_cost) / total_cost * 100 if total_cost > 0 else 0.0

    return {
        "core": core,
        "satellite": sat,
        "total": {"cost": round(total_cost, 2), "value": round(total_value, 2), "return_%": round(total_ret, 2)},
        "core_capital_share_%": round(core["cost"] / total_cost * 100, 1) if total_cost > 0 else 0.0,
        "satellite_capital_share_%": round(sat["cost"] / total_cost * 100, 1) if total_cost > 0 else 0.0,
    }


if __name__ == "__main__":
    perf = get_separated_performance()
    print("=" * 60)
    print("CORE vs SATELLITE -- LIVE PERFORMANCE (yfinance)")
    print("=" * 60)
    print(f"\nCORE (hypothesis):  {perf['core']['return_%']:+.2f}%  (cost ${perf['core']['cost']}, value ${perf['core']['value']})")
    print(f"SATELLITE (side):   {perf['satellite']['return_%']:+.2f}%  (cost ${perf['satellite']['cost']}, value ${perf['satellite']['value']})")
    print(f"TOTAL (blended):    {perf['total']['return_%']:+.2f}%  (cost ${perf['total']['cost']}, value ${perf['total']['value']})")
    print(f"\nCapital split: Core {perf['core_capital_share_%']}% | Satellite {perf['satellite_capital_share_%']}%")
    print("=" * 60)
