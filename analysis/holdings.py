# analysis/holdings.py
# Actual brokerage holdings (Mirae Asset, USD) + Core/Satellite return separation
#
# DESIGN: Each ticker holds a list of LOTS -- one lot per buy transaction,
# each with its own shares/cost/buy_date. This keeps benchmark comparisons
# (see get_benchmark_comparison) exact even when a position was built up
# over multiple purchases on different dates, instead of approximating with
# a single averaged buy_date. shares/cost at the position level are derived
# (summed) from lots, never stored directly.
#
# Hard facts (lots) live in data/holdings.json, not here. This file only
# READS/WRITES that JSON and computes LIVE value/return via yfinance.

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


def _total_shares(ticker):
    return sum(lot["shares"] for lot in HOLDINGS[ticker]["lots"])


def get_total_shares(ticker):
    """Public accessor: total shares held for a ticker, summed across lots."""
    return _total_shares(ticker)


def _total_cost(ticker):
    return sum(lot["cost"] for lot in HOLDINGS[ticker]["lots"])


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
    """Per-position live return. shares/cost are summed across all lots."""
    if prices is None:
        prices = _get_prices()
    out = {}
    for ticker, h in HOLDINGS.items():
        shares = _total_shares(ticker)
        cost = _total_cost(ticker)
        price = prices.get(ticker)
        if price is None:
            out[ticker] = {"name": h["name"], "group": h["group"], "cost": round(cost, 2),
                           "value": None, "return_%": None, "price": None}
            continue
        value = shares * price
        ret = (value - cost) / cost * 100 if cost > 0 else 0.0
        out[ticker] = {"name": h["name"], "group": h["group"], "cost": round(cost, 2),
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
# Benchmark comparison -- was the Core return actually alpha, or just beta?
# Computed PER LOT: each lot's cost is compared to investing the same dollars
# in the benchmark on that lot's own buy_date, then summed across lots/tickers.
# This stays exact even when a position was built from multiple purchases.
# ---------------------------------------------------------------------------

def _get_entry_price(ticker, date_str):
    """Closing price on date_str, or the next available trading day."""
    try:
        df = yf.download(ticker, start=date_str, progress=False, timeout=10)
        if df.empty:
            return None
        close = df["Close"].iloc[0]
        return float(close.iloc[0]) if hasattr(close, "iloc") else float(close)
    except Exception:
        return None


def get_benchmark_comparison(benchmark_tickers=("SPY", "QQQ")):
    """
    For each lot (not just each ticker), computes what its cost would be
    worth today if invested in the benchmark on that LOT's own buy_date.
    Lots without a buy_date are skipped (and reported) since no fair
    comparison is possible.
    """
    live_prices = _get_prices()
    own_returns = get_position_returns(live_prices)

    skipped = []
    for ticker, h in HOLDINGS.items():
        for lot in h["lots"]:
            if not lot.get("buy_date"):
                skipped.append({"ticker": ticker, "shares": lot["shares"], "cost": lot["cost"]})

    result = {}
    for bench in benchmark_tickers:
        bench_current_price = None
        try:
            bench_current_price = float(yf.Ticker(bench).fast_info["lastPrice"])
        except Exception:
            pass

        per_group_cost = {"core": 0.0, "satellite": 0.0}
        per_group_bench_value = {"core": 0.0, "satellite": 0.0}
        per_group_actual_value = {"core": 0.0, "satellite": 0.0}

        entry_price_cache = {}

        for ticker, h in HOLDINGS.items():
            actual = own_returns.get(ticker, {})
            if actual.get("value") is None or bench_current_price is None:
                continue

            ticker_total_cost = _total_cost(ticker)
            if ticker_total_cost <= 0:
                continue

            group = h["group"]
            for lot in h["lots"]:
                if not lot.get("buy_date"):
                    continue

                cache_key = (bench, lot["buy_date"])
                if cache_key not in entry_price_cache:
                    entry_price_cache[cache_key] = _get_entry_price(bench, lot["buy_date"])
                entry_price = entry_price_cache[cache_key]
                if entry_price is None or entry_price == 0:
                    continue

                lot_cost = lot["cost"]
                bench_shares_equiv = lot_cost / entry_price
                bench_value = bench_shares_equiv * bench_current_price

                lot_actual_value = actual["value"] * (lot_cost / ticker_total_cost)

                per_group_cost[group] += lot_cost
                per_group_bench_value[group] += bench_value
                per_group_actual_value[group] += lot_actual_value

        def _summarize(group):
            cost = per_group_cost[group]
            bench_val = per_group_bench_value[group]
            actual_val = per_group_actual_value[group]
            bench_ret = (bench_val - cost) / cost * 100 if cost > 0 else None
            actual_ret = (actual_val - cost) / cost * 100 if cost > 0 else None
            alpha = (actual_ret - bench_ret) if (bench_ret is not None and actual_ret is not None) else None
            return {
                "cost": round(cost, 2),
                "benchmark_value": round(bench_val, 2),
                "benchmark_return_%": round(bench_ret, 2) if bench_ret is not None else None,
                "actual_value": round(actual_val, 2),
                "actual_return_%": round(actual_ret, 2) if actual_ret is not None else None,
                "alpha_pp": round(alpha, 2) if alpha is not None else None,
            }

        core_summary = _summarize("core")
        sat_summary = _summarize("satellite")
        total_cost = core_summary["cost"] + sat_summary["cost"]
        total_bench_val = core_summary["benchmark_value"] + sat_summary["benchmark_value"]
        total_actual_val = core_summary["actual_value"] + sat_summary["actual_value"]
        total_bench_ret = (total_bench_val - total_cost) / total_cost * 100 if total_cost > 0 else None
        total_actual_ret = (total_actual_val - total_cost) / total_cost * 100 if total_cost > 0 else None
        total_alpha = (
            (total_actual_ret - total_bench_ret)
            if (total_bench_ret is not None and total_actual_ret is not None) else None
        )

        result[bench] = {
            "core": core_summary,
            "satellite": sat_summary,
            "total": {
                "cost": round(total_cost, 2),
                "benchmark_value": round(total_bench_val, 2),
                "benchmark_return_%": round(total_bench_ret, 2) if total_bench_ret is not None else None,
                "actual_value": round(total_actual_val, 2),
                "actual_return_%": round(total_actual_ret, 2) if total_actual_ret is not None else None,
                "alpha_pp": round(total_alpha, 2) if total_alpha is not None else None,
            },
        }

    result["skipped_lots_no_buy_date"] = skipped
    return result


# ---------------------------------------------------------------------------
# Trade recording -- for EXISTING tickers only.
# Adding a brand-new ticker is intentionally NOT supported here: deciding
# which thesis signal (A-H) it maps to, and whether it's core or satellite,
# is a judgment call that belongs in a dedicated discussion, not a form.
# ---------------------------------------------------------------------------

class TradeError(Exception):
    """Raised when a requested trade is invalid (e.g. selling more than held)."""
    pass


def record_buy(ticker, qty, amount, buy_date=None):
    """Add a NEW LOT to an EXISTING position. qty=shares, amount=USD spent.

    buy_date defaults to today. Each call creates a separate lot so the
    benchmark comparison stays exact for multi-purchase positions.
    """
    if ticker not in HOLDINGS:
        raise TradeError(
            f"'{ticker}' is not an existing holding. Adding a brand-new ticker "
            "requires a thesis discussion first, not this form."
        )
    if qty <= 0 or amount <= 0:
        raise TradeError("Quantity and amount must both be positive for a buy.")

    if buy_date is None:
        buy_date = datetime.now().date().isoformat()

    new_lot = {"shares": round(qty, 6), "cost": round(amount, 2), "buy_date": buy_date}
    HOLDINGS[ticker]["lots"].append(new_lot)

    _data["holdings"] = HOLDINGS
    _data["last_cost_sync"] = datetime.now().date().isoformat()
    _save_data(_data)

    return {
        "ticker": ticker,
        "new_lot": new_lot,
        "shares": round(_total_shares(ticker), 6),
        "cost": round(_total_cost(ticker), 2),
    }


def record_sell(ticker, qty, current_price=None, exit_reason=None):
    """Reduce or close an EXISTING position, FIFO across lots (oldest lot sold first)."""
    if ticker not in HOLDINGS:
        raise TradeError(f"'{ticker}' is not an existing holding.")
    if qty <= 0:
        raise TradeError("Quantity must be positive for a sell.")

    total_shares = _total_shares(ticker)
    if qty > total_shares + 1e-9:
        raise TradeError(f"Cannot sell {qty} shares of {ticker}; only {total_shares} held.")

    is_full_close = qty >= total_shares - 1e-9

    if current_price is None:
        try:
            current_price = float(yf.Ticker(ticker).fast_info["lastPrice"])
        except Exception:
            raise TradeError(
                f"Could not fetch a live price for {ticker}; pass current_price explicitly."
            )

    lots = HOLDINGS[ticker]["lots"]
    remaining_to_sell = qty
    total_cost_removed = 0.0
    new_lots = []

    for lot in lots:
        if remaining_to_sell <= 1e-9:
            new_lots.append(lot)
            continue

        if lot["shares"] <= remaining_to_sell + 1e-9:
            total_cost_removed += lot["cost"]
            remaining_to_sell -= lot["shares"]
        else:
            fraction_sold = remaining_to_sell / lot["shares"]
            cost_removed_from_lot = fraction_sold * lot["cost"]
            total_cost_removed += cost_removed_from_lot

            new_lots.append({
                "shares": round(lot["shares"] - remaining_to_sell, 6),
                "cost": round(lot["cost"] - cost_removed_from_lot, 2),
                "buy_date": lot["buy_date"],
            })
            remaining_to_sell = 0.0

    proceeds = qty * current_price
    realized_return_pct = (
        (proceeds - total_cost_removed) / total_cost_removed * 100 if total_cost_removed > 0 else 0.0
    )

    if is_full_close:
        if not exit_reason:
            raise TradeError(
                "Closing a position fully requires an exit_reason "
                "(the failure/exit condition being honored)."
            )
        CLOSED_POSITIONS[ticker] = {
            "name": HOLDINGS[ticker]["name"],
            "exit_date": datetime.now().date().isoformat(),
            "realized_return_%": round(realized_return_pct, 2),
            "exit_reason": exit_reason,
        }
        del HOLDINGS[ticker]
    else:
        HOLDINGS[ticker]["lots"] = new_lots

    _data["holdings"] = HOLDINGS
    _data["closed_positions"] = CLOSED_POSITIONS
    _data["last_cost_sync"] = datetime.now().date().isoformat()
    _save_data(_data)

    return {
        "ticker": ticker,
        "qty_sold": qty,
        "price": round(current_price, 2),
        "proceeds": round(proceeds, 2),
        "cost_removed": round(total_cost_removed, 2),
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
