# analysis/holdings.py
# Actual brokerage holdings (Mirae Asset, USD) + Core/Satellite return separation
#
# DESIGN: Hard facts (shares, cost) live in data/holdings.json, not here.
# This file only READS/WRITES that JSON and computes LIVE value/return via yfinance.
# To update holdings via code, use record_buy()/record_sell() below --
# they keep data/holdings.json as the single source of truth.

import json
from pathlib import Path
from datetime import datetime

import yfinance as yf

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "holdings.json"


def _load_data():
    with open(_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_data(data):
    with open(_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


_data = _load_data()
HOLDINGS = _data["holdings"]
CLOSED_POSITIONS = _data["closed_positions"]
LAST_COST_SYNC = _data.get("last_cost_sync")


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


# ---------------------------------------------------------------------------
# Trade recording -- for EXISTING tickers only.
# Adding a brand-new ticker is intentionally NOT supported here: deciding
# which thesis signal (A-H) it maps to, and whether it's core or satellite,
# is a judgment call that belongs in a dedicated discussion, not a form.
# ---------------------------------------------------------------------------

class TradeError(Exception):
    """Raised when a requested trade is invalid (e.g. selling more than held)."""
    pass


def record_buy(ticker, qty, amount):
    """Add to an EXISTING position. qty=shares added, amount=USD spent (cost added).

    Raises TradeError if ticker is not an existing holding.
    """
    if ticker not in HOLDINGS:
        raise TradeError(
            f"'{ticker}' is not an existing holding. Adding a brand-new ticker "
            "requires a thesis discussion first, not this form."
        )
    if qty <= 0 or amount <= 0:
        raise TradeError("Quantity and amount must both be positive for a buy.")

    h = HOLDINGS[ticker]
    h["shares"] = round(h["shares"] + qty, 6)
    h["cost"] = round(h["cost"] + amount, 2)

    _data["holdings"] = HOLDINGS
    _data["last_cost_sync"] = datetime.now().date().isoformat()
    _save_data(_data)
    return dict(h)


def record_sell(ticker, qty, current_price=None, exit_reason=None):
    """Reduce or close an EXISTING position.

    qty: number of shares sold.
    current_price: live price at time of sale (required to compute realized
        return on a full close; if omitted, a live fetch is attempted).
    exit_reason: required when the sale fully closes the position -- this is
        the pre-defined failure/exit condition being honored (see URA case).

    Cost is reduced proportionally (average-cost-basis method), so the
    remaining position's cost basis -- and therefore its return_% -- is
    unaffected by a partial sale.

    Raises TradeError if ticker doesn't exist or qty exceeds current shares.
    """
    if ticker not in HOLDINGS:
        raise TradeError(f"'{ticker}' is not an existing holding.")
    if qty <= 0:
        raise TradeError("Quantity must be positive for a sell.")

    h = HOLDINGS[ticker]
    if qty > h["shares"] + 1e-9:
        raise TradeError(
            f"Cannot sell {qty} shares of {ticker}; only {h['shares']} held."
        )

    is_full_close = qty >= h["shares"] - 1e-9

    if current_price is None:
        try:
            current_price = float(yf.Ticker(ticker).fast_info["lastPrice"])
        except Exception:
            raise TradeError(
                f"Could not fetch a live price for {ticker}; pass current_price explicitly."
            )

    proceeds = qty * current_price
    cost_removed = (qty / h["shares"]) * h["cost"]
    realized_return_pct = (
        (proceeds - cost_removed) / cost_removed * 100 if cost_removed > 0 else 0.0
    )

    if is_full_close:
        if not exit_reason:
            raise TradeError(
                "Closing a position fully requires an exit_reason "
                "(the failure/exit condition being honored)."
            )
        CLOSED_POSITIONS[ticker] = {
            "name": h["name"],
            "exit_date": datetime.now().date().isoformat(),
            "realized_return_%": round(realized_return_pct, 2),
            "exit_reason": exit_reason,
        }
        del HOLDINGS[ticker]
    else:
        h["shares"] = round(h["shares"] - qty, 6)
        h["cost"] = round(h["cost"] - cost_removed, 2)

    _data["holdings"] = HOLDINGS
    _data["closed_positions"] = CLOSED_POSITIONS
    _data["last_cost_sync"] = datetime.now().date().isoformat()
    _save_data(_data)

    return {
        "ticker": ticker,
        "qty_sold": qty,
        "price": round(current_price, 2),
        "proceeds": round(proceeds, 2),
        "cost_removed": round(cost_removed, 2),
        "realized_return_%": round(realized_return_pct, 2),
        "full_close": is_full_close,
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
