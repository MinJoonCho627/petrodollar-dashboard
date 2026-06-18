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
st.markdown("**Thesis:** US Dollar Hegemony Reinforcement Under Trump Administration")

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
    Trump administration concentrates military-economic power in Indo-Pacific to:
    1. Restructure China's economy (production → consumption)
    2. Decouple energy & supply chains from China
    3. Reinforce USD hegemony
    4. Integrate Taiwan into US supply chain
    
    **Portfolio Thesis:**
    Core 7 positions directly expose to these macro signals.
    Satellite 2 positions excluded from hypothesis validation.
    """)
    
    st.divider()
    
    # Import validators
    from analysis.hypothesis_validator import HypothesisValidator
    from analysis.benchmark_metrics import BenchmarkMetrics
    from analysis.portfolio_thesis import CORE_PORTFOLIO, SATELLITE_PORTFOLIO
    
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
            "Portfolio Return",
            f"{benchmark_result['portfolio_return_%']}%",
            f"vs SPY {benchmark_result['spy_benchmark_%']}%"
        )
    
    with col3:
        st.metric(
            "Alpha",
            f"+{benchmark_result['alpha_%']}%",
            "Excess over SPY"
        )
    
    with col4:
        st.metric(
            "Status",
            validation_result['hypothesis_status'],
            "Updated: 2026-06-18"
        )
    
    st.divider()
    
    # 2. Signal Validation
    st.subheader("📈 Signal Validation (5 Macro Indicators)")
    
    for signal_id in ["A", "B", "D", "F", "H"]:
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
    
    # 4. Risk & Benchmark Metrics
    st.subheader("⚡ Risk & Benchmark Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Sharpe Ratio", f"{benchmark_result['sharpe_ratio']}", "Risk-adjusted return")
    
    with col2:
        st.metric("Information Ratio", f"{benchmark_result['information_ratio']}", "Alpha per risk unit")
    
    with col3:
        st.metric("Sortino Ratio", f"{benchmark_result['sortino_ratio']}", "Downside risk focus")
    
    with col4:
        st.metric("Max Drawdown", f"{benchmark_result['max_drawdown_%']}%", "Worst case loss")
    
    st.divider()
    
    # 5. Portfolio Composition
    st.subheader("🎯 Portfolio Composition")
    
    col_core, col_sat = st.columns(2)
    
    with col_core:
        st.write("**CORE (Thesis-Driven):** 7 positions")
        core_tickers = list(CORE_PORTFOLIO.keys())
        for ticker in core_tickers:
            status = "✓" if CORE_PORTFOLIO[ticker].get("status", "ACTIVE") == "ACTIVE" else "✗"
            ret = CORE_PORTFOLIO[ticker].get("current_return_%", "N/A")
            st.write(f"{status} {ticker}: {ret}%")
    
    with col_sat:
        st.write("**SATELLITE (Personal):** 2 positions (Excluded)")
        for ticker, info in SATELLITE_PORTFOLIO.items():
            st.write(f"• {ticker}: {info['current_return_%']}% (Not validated)")
    
    st.divider()
    
    # 6. Next Review Date
    st.info("**Next Quarterly Review:** 2026-09-18 (3 months)")
    st.caption("Portfolio updates trigger re-validation at Tab 5")
    
    st.divider()
    
    # 2. Signal Validation
    st.subheader("📈 Signal Validation (5 Macro Indicators)")
    
    for signal_id in ["A", "B", "D", "F", "H"]:
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
    
    # 4. Risk & Benchmark Metrics
    st.subheader("⚡ Risk & Benchmark Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Sharpe Ratio", f"{benchmark_result['sharpe_ratio']}", "Risk-adjusted return")
    
    with col2:
        st.metric("Information Ratio", f"{benchmark_result['information_ratio']}", "Alpha per risk unit")
    
    with col3:
        st.metric("Sortino Ratio", f"{benchmark_result['sortino_ratio']}", "Downside risk focus")
    
    with col4:
        st.metric("Max Drawdown", f"{benchmark_result['max_drawdown_%']}%", "Worst case loss")
    
    st.divider()
    
    # 5. Portfolio Composition
    st.subheader("🎯 Portfolio Composition")
    
    col_core, col_sat = st.columns(2)
    
    with col_core:
        st.write("**CORE (Thesis-Driven):** 7 positions")
        core_tickers = list(CORE_PORTFOLIO.keys())
        for ticker in core_tickers:
            status = "✓" if CORE_PORTFOLIO[ticker].get("status", "ACTIVE") == "ACTIVE" else "✗"
            ret = CORE_PORTFOLIO[ticker].get("current_return_%", "N/A")
            st.write(f"{status} {ticker}: {ret}%")
    
    with col_sat:
        st.write("**SATELLITE (Personal):** 2 positions (Excluded)")
        for ticker, info in SATELLITE_PORTFOLIO.items():
            st.write(f"• {ticker}: {info['current_return_%']}% (Not validated)")
    
    st.divider()
    
    # 6. Next Review Date
    st.info("**Next Quarterly Review:** 2026-09-18 (3 months)")
    st.caption("Portfolio updates trigger re-validation at Tab 5")
with tab5:
    st.subheader("📔 주식일지 - 실시간 포트폴리오 업데이트")
    st.markdown("포트폴리오를 건드릴 때마다 입력 → 자동 분석")
    
    data_dir = Path("data")
    snapshots_dir = data_dir / "portfolio_snapshots"
    analysis_dir = data_dir / "period_analysis"
    
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)
    
    with st.sidebar:
        st.subheader("📊 주식일지 상태")
        
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
        entry_date = st.date_input("날짜", value=datetime.now().date(), key="tab5_date")
    with col_time:
        entry_time = st.time_input("시간", value=datetime.now().time(), key="tab5_time")
    
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
                format="%.2f",
                key=f"tab5_{ticker}"
            )
    
    st.divider()
    
    st.subheader("📌 메모")
    
    reason = st.selectbox(
        "이유",
        ["선택", "모니터링", "매수", "매도", "손절", "익절"],
        key="tab5_reason"
    )
    
    notes = st.text_area("상세 메모", height=80, key="tab5_notes")
    
    if st.button("✅ 업데이트", use_container_width=True, key="tab5_update"):
        
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
                st.info(f"""
💾 GitHub 저장:
```bash
git add data/
git commit -m "Portfolio: {entry_date.isoformat()}"
git push
```
                """)
        
        else:
            st.warning("⚠️ 첫 입력입니다. 다음 입력 시 분석이 시작됩니다.")
    
    st.divider()
    st.caption("📌 포트폴리오를 건드릴 때마다 입력하세요!")

st.divider()
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
st.caption("Data sourced from Yahoo Finance | Analysis for educational purposes only")
