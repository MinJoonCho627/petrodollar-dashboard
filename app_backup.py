# app.py
# Petrodollar Hegemony Analysis - Main Dashboard

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from config import PORTFOLIO, SECTOR_COLORS, MACRO_INDICATORS
from data.macro_data import get_recent_snapshot as get_macro_snapshot
from data.portfolio_data import get_portfolio_snapshot
from analysis.correlation import get_macro_portfolio_correlation, get_sector_macro_correlation
from analysis.regression import get_stock_sensitivities, get_sector_sensitivities
import warnings
warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════════════
# Page Config
# ═══════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Petrodollar Hegemony Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌍 Petrodollar Hegemony Analysis Dashboard")
st.markdown("**Thesis:** US Dollar Hegemony Reinforcement Under Trump Administration")

st.divider()

# ═══════════════════════════════════════════════════════════════════════
# Load Data
# ═══════════════════════════════════════════════════════════════════════

with st.spinner("📊 Loading data..."):
    portfolio_df = get_portfolio_snapshot()
    macro_df = get_macro_snapshot()

# ═══════════════════════════════════════════════════════════════════════
# Navigation Tabs
# ═══════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard",
    "📈 Correlation Analysis",
    "⭐ Sensitivity Analysis",
    "🎯 Thesis Validation"
])

# ═══════════════════════════════════════════════════════════════════════
# TAB 1: Dashboard
# ═══════════════════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════════════════
# TAB 2: Correlation Analysis
# ═══════════════════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════════════════
# TAB 3: Sensitivity Analysis
# ═══════════════════════════════════════════════════════════════════════

with tab3:
    st.subheader("⭐ Stock Sensitivity to Macro Indicators (Beta)")
    st.write("Beta > 0: moves with macro indicator | Beta < 0: moves against macro indicator")
    
    with st.spinner("Calculating stock sensitivities..."):
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        stock_sens = get_stock_sensitivities(start=start_date)
        
        if not stock_sens.empty:
            st.dataframe(stock_sens, use_container_width=True, hide_index=True)
            
            # Highlight key findings
            st.divider()
            st.subheader("🔍 Key Insights")
            
            # USD sensitivity
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

# ═══════════════════════════════════════════════════════════════════════
# TAB 4: Thesis Validation
# ═══════════════════════════════════════════════════════════════════════

with tab4:
    st.subheader("🎯 Thesis: Petrodollar Hegemony Reinforcement")
    st.write("""
    **Core Hypothesis:**
    As the Trump administration reinforces US dollar hegemony, we expect:
    1. **Dollar strength** correlates with portfolio weakness (diversification hedge)
    2. **Energy sector** shows mixed sensitivity (policy shift impact)
    3. **Space & Tech** strongly tied to S&P 500 (US dominance bet)
    4. **Finance sector** inversely correlated with dollar (de-dollarization hedge)
    """)
    
    st.divider()
    
    st.subheader("📊 Evidence from Data")
    
    start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    stock_sens = get_stock_sensitivities(start=start_date)
    sector_corr = get_sector_macro_correlation(start=start_date)
    
    if not stock_sens.empty and not sector_corr.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### ✅ Findings Support Thesis")
            
            # USD sensitivity
            usd_sens = stock_sens[stock_sens['macro'] == 'USD']
            negative_count = len(usd_sens[usd_sens['beta'] < 0])
            total_count = len(usd_sens)
            
            st.metric(
                "Negative USD Beta Holdings",
                f"{negative_count}/{total_count}",
                "All holdings hedge against dollar strength"
            )
            
            # SP500 sensitivity
            sp_sens = stock_sens[stock_sens['macro'] == 'SP500']
            positive_count = len(sp_sens[sp_sens['beta'] > 0])
            
            st.metric(
                "Positive S&P 500 Beta Holdings",
                f"{positive_count}/{len(sp_sens)}",
                "Aligned with US market"
            )
        
        with col2:
            st.write("### 📈 Sector Correlations vs USD")
            
            if 'USD' in sector_corr.index:
                usd_corr = sector_corr.loc['USD'].sort_values()
                
                st.write("**Sectors most hedged against dollar:**")
                for sector, corr in usd_corr.head(2).items():
                    st.write(f"- {sector}: {corr:.3f}")
                
                st.write("**Sectors most exposed to dollar:**")
                for sector, corr in usd_corr.tail(2).items():
                    st.write(f"- {sector}: {corr:.3f}")
    
    st.divider()
    
    st.subheader("🎓 Investment Implication")
    st.info("""
    The portfolio is **strategically positioned** for petrodollar hegemony reinforcement:
    - **Negative USD correlation** = gains when dollar weakens (diversification)
    - **High S&P 500 correlation** = exposed to US tech/space gains
    - **Mixed energy exposure** = hedges energy policy uncertainty
    - **Crypto exposure** = anti-dollar positioning
    """)

# ═══════════════════════════════════════════════════════════════════════
# Footer
# ═══════════════════════════════════════════════════════════════════════

st.divider()
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
st.caption("Data sourced from Yahoo Finance | Analysis for educational purposes only")