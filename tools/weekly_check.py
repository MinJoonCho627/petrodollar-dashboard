"""주간 점검 계산 스크립트 (결정적 계산, AI 판단 없음)

사용: python3 tools/weekly_check.py <prices_latest.csv>
prices csv 열: ticker,date,open,high,low,close (일봉)
보유·스냅샷은 저장소 data/ 에서 읽는다. 저장소 파일은 수정하지 않는다.
"""
import csv
import glob
import json
import os
import sys
from collections import defaultdict

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
COND_C = -20.0  # config.py failure_conditions C


def load_prices(path):
    rows, bad = defaultdict(list), []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                o, h, l, c = (float(r[k]) for k in ("open", "high", "low", "close"))
            except (ValueError, KeyError):
                bad.append((r.get("ticker"), r.get("date"), "숫자 아님"))
                continue
            if min(o, h, l, c) <= 0 or h < max(o, c) or l > min(o, c) or h < l:
                bad.append((r["ticker"], r["date"], f"OHLC 모순 o={o} h={h} l={l} c={c}"))
                continue
            rows[r["ticker"].upper()].append({"date": r["date"], "o": o, "h": h, "l": l, "c": c})
    for t in rows:
        rows[t].sort(key=lambda x: x["date"])
    return rows, bad


def atr(bars, n=14):
    if len(bars) < n + 1:
        return None
    trs = [max(b["h"] - b["l"], abs(b["h"] - p["c"]), abs(b["l"] - p["c"])) for p, b in zip(bars, bars[1:])]
    return sum(trs[-n:]) / n


def max_drawdown(bars):
    peak, mdd = bars[0]["c"], 0.0
    for b in bars:
        peak = max(peak, b["c"])
        mdd = min(mdd, b["c"] / peak - 1)
    return mdd * 100


def main(path):
    holdings = json.load(open(os.path.join(REPO, "data", "holdings.json"), encoding="utf-8"))["holdings"]
    prices, bad = load_prices(path)
    missing = [t for t in holdings if t not in prices]
    print(f"# 가격 파일: {os.path.basename(path)}")
    if bad:
        print(f"! 데이터 불량 {len(bad)}행 제외:")
        for b in bad:
            print("  -", *b)
    if missing:
        print(f"! 가격 없음: {', '.join(missing)} → 계산 중단 (데이터 불량)")
        return 2

    pos, grp = {}, defaultdict(lambda: [0.0, 0.0])
    for t, h in holdings.items():
        sh = sum(l["shares"] for l in h["lots"])
        cost = sum(l["cost"] for l in h["lots"])
        last = prices[t][-1]
        val = sh * last["c"]
        pos[t] = dict(group=h["group"], cost=cost, value=val, ret=(val / cost - 1) * 100,
                      asof=last["date"], close=last["c"], atr=atr(prices[t]),
                      mdd=max_drawdown(prices[t]), n=len(prices[t]))
        grp[h["group"]][0] += cost
        grp[h["group"]][1] += val

    tc = sum(v[0] for v in grp.values())
    tv = sum(v[1] for v in grp.values())
    tot = (tv / tc - 1) * 100
    snaps = sorted(glob.glob(os.path.join(REPO, "data", "portfolio_snapshots", "*.json")))
    peak = max([json.load(open(s, encoding="utf-8")).get("total_return_%", 0) for s in snaps] + [tot])
    from_peak = ((1 + tot / 100) / (1 + peak / 100) - 1) * 100
    hit = tot <= COND_C or from_peak <= COND_C

    print(f"\n## 조건 C (손실 {COND_C:.0f}%)")
    print(f"원가 대비 {tot:+.2f}% / 기록상 최고점({peak:+.2f}%, 스냅샷 {len(snaps)}개 기준) 대비 {from_peak:+.2f}% "
          f"→ {'충족 — 캡틴 확인 필요' if hit else '미충족'}")
    for g in ("core", "satellite"):
        c, v = grp[g]
        print(f"\n## {g.capitalize()}  원가 대비 {(v / c - 1) * 100:+.2f}%  (원가 비중 {c / tc * 100:.1f}%)")
        print("종목 | 기준일 | 종가 | 원가 대비 | 현재 비중 | ATR14 (종가 대비) | 기간 최대 낙폭 | 일수")
        for t, p in pos.items():
            if p["group"] != g:
                continue
            a = f"{p['atr']:.2f} ({p['atr'] / p['close'] * 100:.1f}%)" if p["atr"] else "부족"
            print(f"{t} | {p['asof']} | {p['close']:.2f} | {p['ret']:+.2f}% | {p['value'] / tv * 100:.1f}% "
                  f"| {a} | {p['mdd']:.1f}% | {p['n']}")

    for b in ("SPY", "QQQ"):
        if b in prices and len(prices[b]) > 1:
            s = prices[b]
            print(f"\n벤치마크 {b}: {s[-1]['date']} 종가 {s[-1]['c']:.2f}, 기간 수익률 {(s[-1]['c'] / s[0]['c'] - 1) * 100:+.2f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
