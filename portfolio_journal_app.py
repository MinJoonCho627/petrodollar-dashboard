import streamlit as st
import json
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="주식일지", page_icon="📔", layout="wide")

st.title("📔 주식일지 - 실시간 포트폴리오 업데이트")
st.markdown("포트폴리오를 건드릴 때마다 입력 → 자동 분석")

data_dir = Path("data")
snapshots_dir = data_dir / "portfolio_snapshots"
analysis_dir = data_dir / "period_analysis"

snapshots_dir.mkdir(parents=True, exist_ok=True)
analysis_dir.mkdir(parents=True, exist_ok=True)

with st.sidebar:
    st.subheader("📊 현재 상태")
    
    snapshots = sorted(snapshots_dir.glob("*.json"), reverse=True)
    
    if snapshots:
        with open(snapshots[0], 'r', encoding='utf-8') as f:
            latest = json.load(f)
        
        st.write(f"**마지막:** {latest['date']} {latest['time'][:5]}")
        st.divider()
        
        for ticker, price in latest['portfolio'].items():
            if price > 0:
                st.write(f"• {ticker}: ${price:.2f}")
    else:
        st.info("아직 입력이 없습니다")

st.subheader("📝 포트폴리오 입력")

col_date, col_time = st.columns([2, 1])
with col_date:
    entry_date = st.date_input("날짜", value=datetime.now().date())
with col_time:
    entry_time = st.time_input("시간", value=datetime.now().time())

st.divider()

st.subheader("💰 종목 가격")

TICKERS = ["PL", "IONQ", "HOOD", "BMNR", "COPX", "URA", "TSES", "TSNF", "RXRX"]

portfolio = {}
cols = st.columns(3)

for i, ticker in enumerate(TICKERS):
    with cols[i % 3]:
        portfolio[ticker] = st.number_input(
            ticker,
            value=0.0,
            step=0.01,
            format="%.2f"
        )

st.divider()

st.subheader("📌 메모")

reason = st.selectbox(
    "이유",
    ["선택", "모니터링", "매수", "매도", "손절", "익절"]
)

notes = st.text_area("상세 메모", height=80)

if st.button("✅ 업데이트", use_container_width=True):
    
    snapshot = {
        "date": entry_date.isoformat(),
        "time": entry_time.isoformat(),
        "portfolio": portfolio,
        "reason": reason,
        "notes": notes,
        "timestamp": datetime.now().isoformat(),
    }
    
    snap_file = snapshots_dir / f"{entry_date.isoformat()}_{entry_time.strftime('%H-%M-%S')}.json"
    with open(snap_file, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    
    st.success(f"✅ 저장됨")
    
    snapshots = sorted(snapshots_dir.glob("*.json"))
    
    if len(snapshots) > 1:
        prev_file = None
        for snap in reversed(snapshots):
            if snap.name != snap_file.name:
                prev_file = snap
                break
        
        if prev_file:
            with open(prev_file, 'r', encoding='utf-8') as f:
                prev = json.load(f)
            
            st.info("🔄 분석 중...")
            
            changes = {}
            for ticker in TICKERS:
                prev_price = prev['portfolio'][ticker]
                curr_price = portfolio[ticker]
                
                if prev_price > 0 or curr_price > 0:
                    if prev_price > 0:
                        change_pct = ((curr_price - prev_price) / prev_price) * 100
                    else:
                        change_pct = 0
                    
                    changes[ticker] = {
                        "before": prev_price,
                        "after": curr_price,
                        "change": round(change_pct, 2),
                    }
            
            analysis = {
                "period": {
                    "start": prev['date'],
                    "end": entry_date.isoformat(),
                },
                "changes": changes,
            }
            
            analysis_file = analysis_dir / f"{prev['date']}_to_{entry_date.isoformat()}.json"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            
            st.success("✅ 분석 완료!")
            
            st.divider()
            st.subheader("📊 결과")
            
            for ticker, change in changes.items():
                if change['change'] != 0:
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        st.write(f"**{ticker}**")
                    with c2:
                        st.write(f"${change['before']:.2f}")
                    with c3:
                        st.write("→")
                    with c4:
                        if change['change'] > 0:
                            st.success(f"+{change['change']:.2f}%")
                        elif change['change'] < 0:
                            st.error(f"{change['change']:.2f}%")
                        else:
                            st.info("0%")
            
            st.divider()
            st.info("""
💾 GitHub 저장:
```bash
git add data/
git commit -m "Portfolio: {}"
git push
```
            """.format(entry_date.isoformat()))
    
    else:
        st.warning("⚠️ 첫 입력입니다. 다음 입력 시 분석이 시작됩니다.")

st.divider()
st.caption("📌 포트폴리오를 건드릴 때마다 입력하세요!")
