"""Daily price fetcher for the weekly rule check.

Reads tickers from data/holdings.json (+ SPY, QQQ benchmarks), downloads
~6 months of daily OHLC via yfinance, validates every row, and writes
prices_latest.csv + fetch_meta.json to the output directory.

Exits non-zero (and writes nothing) if any ticker is missing, a ticker's
latest bar is invalid, or more than 5% of a ticker's rows are invalid.
Isolated bad historical rows are dropped and listed in fetch_meta.json.
Today's bar is excluded until 16:30 ET so an unfinished bar is never used.
"""
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import yfinance as yf

BENCHMARKS = ["SPY", "QQQ"]
PERIOD = "6mo"


def load_tickers(repo_root: Path) -> list[str]:
    holdings = json.loads((repo_root / "data" / "holdings.json").read_text(encoding="utf-8"))
    return sorted(holdings["holdings"].keys()) + BENCHMARKS


def valid(o: float, h: float, l: float, c: float) -> bool:
    return min(o, h, l, c) > 0 and h >= max(o, c) and l <= min(o, c) and h >= l


def main(out_dir: str) -> int:
    repo_root = Path(__file__).resolve().parent.parent
    tickers = load_tickers(repo_root)
    rows, problems = [], []

    # Drop today's bar while the U.S. session may still be open (before 16:30 ET),
    # so an unfinished intraday bar never becomes the "latest close".
    now_et = datetime.now(ZoneInfo("America/New_York"))
    session_done = now_et.hour * 60 + now_et.minute >= 16 * 60 + 30
    skipped_rows = []

    for t in tickers:
        df = yf.Ticker(t).history(period=PERIOD, interval="1d", auto_adjust=False)
        if df.empty:
            problems.append(f"{t}: no data")
            continue
        good, bad = [], []
        for idx, r in df.iterrows():
            d = idx.date()
            if d == now_et.date() and not session_done:
                continue
            o, h, l, c = (float(r[k]) for k in ("Open", "High", "Low", "Close"))
            if not valid(o, h, l, c):
                bad.append(f"{t} {d}: OHLC inconsistent o={o:.4f} h={h:.4f} l={l:.4f} c={c:.4f}")
                continue
            good.append([t, d.isoformat(), round(o, 4), round(h, 4), round(l, 4), round(c, 4)])
        if not good:
            problems.append(f"{t}: no valid rows")
            continue
        # The latest close feeds the -20% rule, so it must be a valid bar.
        if bad and bad[-1].split(" ")[1] > good[-1][1]:
            problems.append(f"{t}: latest bar invalid -> {bad[-1]}")
        # Isolated bad historical rows are dropped; widespread corruption stops the run.
        if len(bad) > 0.05 * (len(good) + len(bad)):
            problems.append(f"{t}: {len(bad)} of {len(good) + len(bad)} rows invalid")
        skipped_rows += bad
        rows += good

    if problems:
        print("DATA CHECK FAILED - nothing written:")
        for p in problems[:20]:
            print("  -", p)
            print(f"::error title=price check::{p}")  # visible as a GitHub annotation
        if len(problems) > 20:
            print(f"::error title=price check::...and {len(problems) - 20} more")
        return 1

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "prices_latest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ticker", "date", "open", "high", "low", "close"])
        w.writerows(rows)
    meta = {
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": f"yfinance {yf.__version__}",
        "period": PERIOD,
        "tickers": tickers,
        "rows": len(rows),
        "skipped_invalid_rows": skipped_rows,
        "last_date": max(r[1] for r in rows),
    }
    (out / "fetch_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    for b in skipped_rows:
        print(f"::warning title=skipped row::{b}")
    print(f"OK: {len(rows)} rows, {len(tickers)} tickers, last date {meta['last_date']}, skipped {len(skipped_rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "out"))
