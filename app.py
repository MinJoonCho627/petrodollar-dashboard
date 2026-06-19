# app.py
# Petrodollar Hegemony Analysis - Main Dashboard

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path
import json
sys.path.append(str(Path(__file__).parent))

from config import PORTFOLIO, SECTOR_COLORS, MACRO_INDICATORS
from data.macro_data import get_recent_snapshot as get_macro_snapshot
from data.portfolio_data import get_portfolio_snapshot
from analysis.correlation import get_macro_portfolio_correlation, get_sector_macro_correlation
from analysis.regression import get_stock_sensitivities, get_sector_sensitivities
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Petrodollar Hegemony Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌍 Petrodollar Hegemony Analysis Dashboard")
st.markdown("**Thesis:** Structural US-China Supply Chain Decoupling (Energy + Geopolitical Tension)")

st.divider()

with st.spinner("📊 Loading data..."):
    portfolio_df = get_portfolio_snapshot()
    macro_df = get_macro_snapshot()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard",
    "📈 Correlation Analysis",
    "⭐ Sensitivity Analysis",
    "🎯 Thesis Validation",
    "📔 주식일지"
])

with tab1:
    st.subheader("📈 Macro Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    for idx, row in macro_df.iterrows():
        indicator = row['indicator']
        price = row['price']
        change = row['1d_change_%']
        
        color = "normal" if change >= 0 else "inverse"
        
        with [col1, col2, col3, col4, col5][idx]:
            st.metric(
                label=indicator,
                value=f"{price}",
                delta=f"{change:.2f}%",
                delta_color=color
            )
    
    st.divider()
    
    st.subheader("📊 Portfolio Holdings")
    st.dataframe(
        portfolio_df[["ticker", "name", "sector", "price", "1d_change_%"]],
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    
    st.subheader("🎯 Sector Distribution")
    
    sector_summary = portfolio_df.groupby("sector").size().reset_index(name="count")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.bar_chart(
            data=sector_summary.set_index("sector")["count"],
            use_container_width=True
        )
    
    with col2:
        st.write("### Holdings by Sector")
        for _, row in sector_summary.iterrows():
            st.write(f"**{row['sector'].upper()}**: {row['count']} holdings")
    
    st.divider()
    
    st.subheader("📈 Top Performers")
    
    top_gainers = portfolio_df.nlargest(3, "1d_change_%")[["ticker", "1d_change_%"]]
    top_losers = portfolio_df.nsmallest(3, "1d_change_%")[["ticker", "1d_change_%"]]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 🟢 Top Gainers")
        for _, row in top_gainers.iterrows():
            st.write(f"{row['ticker']}: +{row['1d_change_%']:.2f}%")
    
    with col2:
        st.write("### 🔴 Top Losers")
        for _, row in top_losers.iterrows():
            st.write(f"{row['ticker']}: {row['1d_change_%']:.2f}%")

with tab2:
    st.subheader("📊 Correlation Matrix: Macro ↔ Portfolio")
    st.write("Shows how macro indicators correlate with individual stock prices")
    
    with st.spinner("Calculating correlations..."):
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        corr_matrix = get_macro_portfolio_correlation(start=start_date)
        
        macro_names = list(MACRO_INDICATORS.keys())
        portfolio_tickers = list(PORTFOLIO.keys())
        
        macro_portfolio_corr = corr_matrix.loc[macro_names, portfolio_tickers]
        
        st.dataframe(
            macro_portfolio_corr.round(3),
            use_container_width=True
        )
    
    st.divider()
    
    st.subheader("📈 Sector-Level Correlations")
    st.write("How macro indicators correlate with sector performance (average)")
    
    with st.spinner("Calculating sector correlations..."):
        sector_corr = get_sector_macro_correlation(start=start_date)
        
        st.dataframe(
            sector_corr.round(3),
            use_container_width=True
        )

with tab3:
    st.subheader("⭐ Stock Sensitivity to Macro Indicators (Beta)")
    st.write("Beta > 0: moves with macro indicator | Beta < 0: moves against macro indicator")
    
    with st.spinner("Calculating stock sensitivities..."):
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        stock_sens = get_stock_sensitivities(start=start_date)
        
        if not stock_sens.empty:
            st.dataframe(stock_sens, use_container_width=True, hide_index=True)
            
            st.divider()
            st.subheader("🔍 Key Insights")
            
            usd_sens = stock_sens[stock_sens['macro'] == 'USD'].nlargest(3, 'beta')
            st.write("**Most negative USD beta (most hedged against dollar weakness):**")
            for _, row in usd_sens.iterrows():
                st.write(f"- {row['stock']} ({row['sector']}): {row['beta']}")
        else:
            st.warning("No data available")
    
    st.divider()
    
    st.subheader("⭐ Sector Sensitivity to Macro Indicators")
    
    with st.spinner("Calculating sector sensitivities..."):
        sector_sens = get_sector_sensitivities(start=start_date)
        
        if not sector_sens.empty:
            st.dataframe(sector_sens, use_container_width=True, hide_index=True)
        else:
            st.warning("No data available")

with tab4:
    st.subheader("🎯 Hypothesis: Trump Indo-Pacific Dominance Strategy")
    
    st.write("""
    **Initial Hypothesis (Fixed):**
    Trump's China pressure is a structural supply-chain decoupling, not a one-off trade war.
    Two tradeable mechanisms:
    1. **F-axis:** Energy/materials supply chain realignment (COPX, TSES, TSNF)
    2. **D-axis:** Persistent geopolitical tension → surveillance/defense demand (PL)
    
    Dollar hegemony & broader macro framing = background context, NOT direct signals.
    
    **Portfolio Thesis:**
    Core 5 positions expose to validated signals (B, D, F, H).
    Satellite 4 positions (HOOD, IONQ, BMNR, RXRX) excluded from validation.
    """)
    
    st.divider()
    
    # Import validators
    from analysis.hypothesis_validator import HypothesisValidator
    from analysis.benchmark_metrics import BenchmarkMetrics
    from analysis.portfolio_thesis import CORE_PORTFOLIO, SATELLITE_PORTFOLIO
    from analysis.holdings import get_separated_performance, get_position_returns
    perf = get_separated_performance()
    
    # Calculate validation
    validator = HypothesisValidator()
    metrics = BenchmarkMetrics()
    
    current_signals = {
        "A": 28.18,
        "B": 17.5,
        "D": 40.0,
        "F": 35.0,
        "H": 5.0,
    }
    
    validation_result = validator.validate_hypothesis(current_signals)
    benchmark_result = metrics.get_performance_summary()
    
    # 1. Overall Status
    st.subheader("📊 Overall Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Hypothesis Confidence",
            f"{validation_result['overall_confidence_%']}%",
            "Target: 75%"
        )
    
    with col2:
        st.metric(
            "Core Return (Hypothesis)",
            f"{perf['core']['return_%']:+.1f}%",
            f"Capital: {perf['core_capital_share_%']}% of total"
        )
    
    with col3:
        st.metric(
            "Satellite Return (Side bets)",
            f"{perf['satellite']['return_%']:+.1f}%",
            f"Capital: {perf['satellite_capital_share_%']}% of total"
        )
    
    with col4:
        st.metric(
            "Status",
            validation_result['hypothesis_status'],
            "Updated: 2026-06-18"
        )
    
    st.divider()
    
    # 2. Signal Validation
    st.subheader("📈 Signal Validation (4 Macro Indicators)")
    
    for signal_id in ["B", "D", "F", "H"]:
        sig = validation_result['signals'][signal_id]
        
        col_left, col_right = st.columns([3, 1])
        
        with col_left:
            bar_length = int(sig['achievement_%'] / 5)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            
            st.write(f"**{signal_id}. {sig['signal_name']}**")
            st.write(f"{bar} {sig['achievement_%']}% {sig['status']}")
            st.caption(f"Target: {sig['bullish_threshold']} | Current: {sig['current_value']}")
        
        with col_right:
            st.metric("Weight", f"{sig['weight']*100:.0f}%")
    
    st.divider()
    
    # 3. Core Portfolio Thesis
    st.subheader("💼 Core Portfolio - Thesis Mapping")
    
    for ticker, info in CORE_PORTFOLIO.items():
        status = info.get("status", "ACTIVE")
        
        with st.expander(f"**{ticker}** ({status}) | Return: {info.get('current_return_%', 'N/A')}%"):
            st.write(f"**Name:** {info['name']}")
            st.write(f"**Thesis:** {info['thesis']}")
            st.write(f"**Hypothesis Link:** {info['hypothesis_link']}")
            st.write(f"**Signal Exposure:** {', '.join(info['signal_exposure'])}")
            st.warning(f"**Failure Signal:** {info['failure_signal']}")
    
    st.divider()
    
    st.info("📊 Comprehensive risk metrics and benchmark analysis will be integrated in Phase 4.")    
    # 5. Portfolio Composition
    st.subheader("🎯 Portfolio Composition")
    
    col_core, col_sat = st.columns(2)
    
    pos_returns = get_position_returns()

    with col_core:
        st.write("**CORE (Thesis-Driven):** live returns")
        for ticker, p in pos_returns.items():
            if p["group"] != "core":
                continue
            r = p["return_%"]
            mark = "✓" if (r is not None and r >= 0) else "✗"
            rtxt = f"{r:+.2f}%" if r is not None else "N/A"
            st.write(f"{mark} {ticker}: {rtxt}")
        st.caption("URA: SOLD 2026-06-18 (-7.65%, Iran-deal failure condition)")

    with col_sat:
        st.write("**SATELLITE (Personal):** excluded from validation")
        for ticker, p in pos_returns.items():
            if p["group"] != "satellite":
                continue
            r = p["return_%"]
            rtxt = f"{r:+.2f}%" if r is not None else "N/A"
            st.write(f"• {ticker}: {rtxt} (Not validated)")
    
    st.divider()
    
    # 6. Next Review Date
    st.info("**Next Quarterly Review:** 2026-09-18 (3 months)")
    st.caption("Portfolio updates trigger re-validation at Tab 5")
    
    st.divider()
    
    # 2. Signal Validation
    st.subheader("📈 Signal Validation (4 Macro Indicators)")
    
    for signal_id in ["B", "D", "F", "H"]:
        sig = validation_result['signals'][signal_id]
        
        col_left, col_right = st.columns([3, 1])
        
        with col_left:
            bar_length = int(sig['achievement_%'] / 5)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            
            st.write(f"**{signal_id}. {sig['signal_name']}**")
            st.write(f"{bar} {sig['achievement_%']}% {sig['status']}")
            st.caption(f"Target: {sig['bullish_threshold']} | Current: {sig['current_value']}")
        
        with col_right:
            st.metric("Weight", f"{sig['weight']*100:.0f}%")
    
    st.divider()
    
    # 3. Core Portfolio Thesis
    st.subheader("💼 Core Portfolio - Thesis Mapping")
    
    for ticker, info in CORE_PORTFOLIO.items():
        status = info.get("status", "ACTIVE")
        
        with st.expander(f"**{ticker}** ({status}) | Return: {info.get('current_return_%', 'N/A')}%"):
            st.write(f"**Name:** {info['name']}")
            st.write(f"**Thesis:** {info['thesis']}")
            st.write(f"**Hypothesis Link:** {info['hypothesis_link']}")
            st.write(f"**Signal Exposure:** {', '.join(info['signal_exposure'])}")
            st.warning(f"**Failure Signal:** {info['failure_signal']}")
    
    st.divider()
    
    
    # 5. Portfolio Composition
    st.subheader("🎯 Portfolio Composition")
    
    col_core, col_sat = st.columns(2)
    
    pos_returns = get_position_returns()

    with col_core:
        st.write("**CORE (Thesis-Driven):** live returns")
        for ticker, p in pos_returns.items():
            if p["group"] != "core":
                continue
            r = p["return_%"]
            mark = "✓" if (r is not None and r >= 0) else "✗"
            rtxt = f"{r:+.2f}%" if r is not None else "N/A"
            st.write(f"{mark} {ticker}: {rtxt}")
        st.caption("URA: SOLD 2026-06-18 (-7.65%, Iran-deal failure condition)")

    with col_sat:
        st.write("**SATELLITE (Personal):** excluded from validation")
        for ticker, p in pos_returns.items():
            if p["group"] != "satellite":
                continue
            r = p["return_%"]
            rtxt = f"{r:+.2f}%" if r is not None else "N/A"
            st.write(f"• {ticker}: {rtxt} (Not validated)")
    
    st.divider()
    
    # 6. Next Review Date
    st.info("**Next Quarterly Review:** 2026-09-18 (3 months)")
    st.caption("Portfolio updates trigger re-validation at Tab 5")
with tab5:
    st.subheader("📔 주식일지 - 스냅샷 기록 (Core/Satellite 분리)")
    st.markdown("그 순간의 Core/Satellite 수익률을 박제 저장 → 이전 스냅샷과 비교")

    from analysis.holdings import (
        get_separated_performance as _gsp,
        get_position_returns as _gpr,
        HOLDINGS as _HOLDINGS,
        record_buy as _record_buy,
        record_sell as _record_sell,
        TradeError as _TradeError,
    )

    data_dir = Path("data")
    snapshots_dir = data_dir / "portfolio_snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    with st.sidebar:
        st.subheader("📊 주식일지 상태")
        snapshots = sorted(snapshots_dir.glob("*.json"), reverse=True)
        if snapshots:
            with open(snapshots[0], 'r', encoding='utf-8') as f:
                latest = json.load(f)
            st.write(f"**마지막:** {latest['date']}")
            st.divider()
            st.write(f"Core: {latest['core_return_%']:+.2f}%")
            st.write(f"Satellite: {latest['satellite_return_%']:+.2f}%")
        else:
            st.info("아직 입력이 없습니다")

    st.subheader("📝 현재 시점 스냅샷")

    col_date, col_time = st.columns([2, 1])
    with col_date:
        entry_date = st.date_input("날짜", value=datetime.now().date(), key="tab5_date")
    with col_time:
        entry_time = st.time_input("시간", value=datetime.now().time(), key="tab5_time")

    st.divider()

    # 실시간 데이터 가져오기 (yfinance, holdings.py 경유 -- 수동 입력 없음)
    live_pos = _gpr()
    live_perf = _gsp()

    st.subheader("💰 현재 보유 현황 (실시간, yfinance)")
    col_c, col_s = st.columns(2)
    with col_c:
        st.metric("Core Return", f"{live_perf['core']['return_%']:+.2f}%",
                   f"Capital {live_perf['core_capital_share_%']}%")
        for t, p in live_pos.items():
            if p["group"] == "core" and p["return_%"] is not None:
                st.caption(f"{t}: ${p['price']:.2f} ({p['return_%']:+.2f}%)")
    with col_s:
        st.metric("Satellite Return", f"{live_perf['satellite']['return_%']:+.2f}%",
                   f"Capital {live_perf['satellite_capital_share_%']}%")
        for t, p in live_pos.items():
            if p["group"] == "satellite" and p["return_%"] is not None:
                st.caption(f"{t}: ${p['price']:.2f} ({p['return_%']:+.2f}%)")

    st.divider()
    st.subheader("🔁 포트폴리오 변화")

    has_trade = st.radio(
        "이번에 포트폴리오 변화 있었나요?",
        ["없음", "있음"],
        key="tab5_has_trade",
        horizontal=True,
    )

    if has_trade == "있음":
        st.caption("⚠️ 신규 종목 추가는 이 폼에서 지원하지 않습니다 -- 가설(A~H 신호) 연결 판단이 먼저 필요합니다. 새 종목이면 코드 작업 전에 먼저 논의하세요.")

        trade_type = st.radio("구분", ["매수", "매도"], key="tab5_trade_type", horizontal=True)
        trade_ticker = st.selectbox("종목", list(_HOLDINGS.keys()), key="tab5_trade_ticker")

        if trade_type == "매수":
            if "tab5_buy_form_id" not in st.session_state:
                st.session_state.tab5_buy_form_id = 0
            _bid = st.session_state.tab5_buy_form_id

            buy_qty = st.number_input("매수 수량", min_value=0.0, step=0.01, key=f"tab5_buy_qty_{_bid}")
            buy_amount = st.number_input("매수 금액 (USD)", min_value=0.0, step=0.01, key=f"tab5_buy_amount_{_bid}")

            if st.button("📥 매수 기록", key=f"tab5_buy_submit_{_bid}"):
                if buy_qty <= 0 or buy_amount <= 0:
                    st.error("❌ 수량과 금액을 0보다 크게 입력하세요.")
                else:
                    try:
                        buy_result = _record_buy(trade_ticker, buy_qty, buy_amount)
                        st.success(f"✅ {trade_ticker} 매수 기록됨: shares={buy_result['shares']}, cost=${buy_result['cost']}")
                        st.session_state.tab5_buy_form_id += 1
                        st.rerun()
                    except _TradeError as e:
                        st.error(f"❌ {e}")

        else:  # 매도
            if "tab5_sell_form_id" not in st.session_state:
                st.session_state.tab5_sell_form_id = 0
            _sid = st.session_state.tab5_sell_form_id

            current_shares = _HOLDINGS[trade_ticker]["shares"]
            st.caption(f"현재 보유: {current_shares} shares")
            sell_qty = st.number_input(
                "매도 수량", min_value=0.0, max_value=float(current_shares), step=0.01, key=f"tab5_sell_qty_{_sid}"
            )
            is_full_close = sell_qty >= current_shares - 1e-9 and sell_qty > 0
            sell_exit_reason = None
            if is_full_close:
                st.warning("⚠️ 전체 청산입니다. 사전에 정한 종료/실패 조건을 명시해야 합니다.")
                sell_exit_reason = st.text_area("청산 이유 (필수)", key=f"tab5_exit_reason_{_sid}")

            if st.button("📤 매도 기록", key=f"tab5_sell_submit_{_sid}"):
                if sell_qty <= 0:
                    st.error("❌ 매도 수량을 0보다 크게 입력하세요.")
                else:
                    try:
                        sell_result = _record_sell(
                            trade_ticker, sell_qty,
                            exit_reason=sell_exit_reason if is_full_close else None,
                        )
                        if sell_result["full_close"]:
                            st.success(
                                f"✅ {trade_ticker} 전체 청산: 실현수익률 {sell_result['realized_return_%']:+.2f}% "
                                f"(closed_positions로 이동됨)"
                            )
                        else:
                            st.success(f"✅ {trade_ticker} 일부 매도 기록됨: {sell_qty} shares @ ${sell_result['price']}")
                        st.session_state.tab5_sell_form_id += 1
                        st.rerun()
                    except _TradeError as e:
                        st.error(f"❌ {e}")

    st.divider()
    st.subheader("📌 이번 업데이트 메모")

    reason = st.selectbox("이유", ["선택", "모니터링", "매수", "매도", "손절", "익절"], key="tab5_reason")
    world_events = st.text_area("이 기간 동안의 주요 사건/뉴스", height=80, key="tab5_events",
                                  placeholder="예: 미중 정상회담, 관세 인하 발표 등")
    notes = st.text_area("내 분석/메모", height=80, key="tab5_notes")

    if st.button("✅ 스냅샷 저장", use_container_width=True, key="tab5_update"):

        snapshot = {
            "date": entry_date.isoformat(),
            "time": entry_time.isoformat(),
            "timestamp": datetime.now().isoformat(),
            "core_return_%": live_perf["core"]["return_%"],
            "satellite_return_%": live_perf["satellite"]["return_%"],
            "total_return_%": live_perf["total"]["return_%"],
            "core_capital_share_%": live_perf["core_capital_share_%"],
            "satellite_capital_share_%": live_perf["satellite_capital_share_%"],
            "positions": {t: p["return_%"] for t, p in live_pos.items() if p["return_%"] is not None},
            "reason": reason,
            "world_events": world_events,
            "notes": notes,
        }

        snap_file = snapshots_dir / f"{entry_date.isoformat()}_{entry_time.strftime('%H-%M-%S')}.json"
        with open(snap_file, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)

        st.success("✅ 스냅샷 저장됨")

        all_snaps = sorted(snapshots_dir.glob("*.json"))
        if len(all_snaps) > 1:
            prev_file = None
            for snap in reversed(all_snaps):
                if snap.name != snap_file.name:
                    prev_file = snap
                    break
            if prev_file:
                with open(prev_file, 'r', encoding='utf-8') as f:
                    prev = json.load(f)

                st.divider()
                st.subheader(f"🔄 비교: {prev['date']} → {entry_date.isoformat()}")

                core_delta = snapshot["core_return_%"] - prev.get("core_return_%", 0)
                sat_delta = snapshot["satellite_return_%"] - prev.get("satellite_return_%", 0)

                cc1, cc2 = st.columns(2)
                with cc1:
                    st.metric("Core 변화", f"{snapshot['core_return_%']:+.2f}%", f"{core_delta:+.2f}pp")
                with cc2:
                    st.metric("Satellite 변화", f"{snapshot['satellite_return_%']:+.2f}%", f"{sat_delta:+.2f}pp")

                if prev.get("world_events"):
                    st.caption(f"지난 기간 사건: {prev['world_events']}")

    st.divider()
    st.subheader("📜 과거 스냅샷 기록")
    all_snaps_display = sorted(snapshots_dir.glob("*.json"), reverse=True)
    if all_snaps_display:
        for snap_path in all_snaps_display[:10]:
            with open(snap_path, 'r', encoding='utf-8') as f:
                s = json.load(f)
            with st.expander(f"{s['date']} | Core {s.get('core_return_%', 'N/A')}% / Satellite {s.get('satellite_return_%', 'N/A')}%"):
                st.write(f"**이유:** {s.get('reason', 'N/A')}")
                if s.get('world_events'):
                    st.write(f"**사건:** {s['world_events']}")
                if s.get('notes'):
                    st.write(f"**메모:** {s['notes']}")
    else:
        st.caption("아직 저장된 스냅샷이 없습니다.")

st.divider()
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
st.caption("Data sourced from Yahoo Finance | Analysis for educational purposes only")
