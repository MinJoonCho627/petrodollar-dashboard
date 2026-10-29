"""Daily price fetcher for the weekly rule check.

Reads tickers from data/holdings.json (+ SPY, QQQ benchmarks), downloads
~6 months of daily OHLC via yfinance, validates every row, and writes
prices_latest.csv + fetch_meta.json to the output directory.

Exits non-zero (and writes nothing) if any ticker is missing or any row
fails validation, so a broken data source can never feed the rule check.
"""
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

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

    for t in tickers:
        df = yf.Ticker(t).history(period=PERIOD, interval="1d", auto_adjust=False)
        if df.empty:
            problems.append(f"{t}: no data")
            continue
        for idx, r in df.iterrows():
            o, h, l, c = (float(r[k]) for k in ("Open", "High", "Low", "Close"))
            if not valid(o, h, l, c):
                problems.append(f"{t} {idx.date()}: OHLC inconsistent o={o} h={h} l={l} c={c}")
                continue
            rows.append([t, idx.date().isoformat(), round(o, 4), round(h, 4), round(l, 4), round(c, 4)])

    if problems:
        print("DATA CHECK FAILED - nothing written:")
        for p in problems:
            print("  -", p)
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
        "last_date": max(r[1] for r in rows),
    }
    (out / "fetch_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"OK: {len(rows)} rows, {len(tickers)} tickers, last date {meta['last_date']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "out"))
