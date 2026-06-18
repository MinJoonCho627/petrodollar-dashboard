# config.py
# Petrodollar Hegemony Analysis - Portfolio Configuration

PORTFOLIO = {
    # Space Sector
    "PL": {"name": "Planet Labs", "sector": "space"},
    "IONQ": {"name": "IonQ", "sector": "space"},
    
    # Finance Sector
    "HOOD": {"name": "Robinhood Markets", "sector": "finance"},
    "BMNR": {"name": "Bitmine", "sector": "finance"},
    
    # Energy Sector
    "COPX": {"name": "Copper Miners ETF", "sector": "energy"},
    "URA": {"name": "Uranium ETF", "sector": "energy"},
    "TSES": {"name": "TechX Energy", "sector": "energy"},
    "TSNF": {"name": "Transocean", "sector": "energy"},
    
    # Technology
    "RXRX": {"name": "Recursion Pharma", "sector": "technology"},
}

MACRO_INDICATORS = {
    "WTI": {"name": "WTI Crude Oil", "ticker": "CL=F"},
    "Gold": {"name": "Gold Futures", "ticker": "GC=F"},
    "SP500": {"name": "S&P 500", "ticker": "^GSPC"},
    "VIX": {"name": "VIX (Volatility Index)", "ticker": "^VIX"},
    "USD": {"name": "US Dollar ETF", "ticker": "UUP"},  # 달러 강도 대체 지표
}

SECTOR_COLORS = {
    "space": "#7B68EE",
    "energy": "#FF8C00",
    "finance": "#32CD32",
    "technology": "#1E90FF",
}

# Analysis periods
HISTORICAL_START = "2015-01-01"
TRUMP_ERA_START = "2024-11-01"

print("✅ Config loaded successfully")
# ═══════════════════════════════════════════════════════════════════════
# INITIAL HYPOTHESIS: Trump Indo-Pacific Dominance Strategy
# ═══════════════════════════════════════════════════════════════════════

INITIAL_HYPOTHESIS = {
    "name": "Trump Indo-Pacific Dominance Strategy",
    "version": "1.0",
    "created_date": "2026-06-16",
    
    "description": """
    Trump's China pressure is not a one-off trade war but a structural 
    supply-chain decoupling. Thesis concentrates on two tradeable mechanisms:
    (1) Energy/materials supply-chain realignment (F-axis: COPX, TSES, TSNF)
    (2) Persistent geopolitical tension driving surveillance/defense demand (D-axis: PL)
    Dollar hegemony & broader macro framing are treated as background context,
    NOT as direct validation signals (no pure-play position).
    """,
    
    "period": {
        "start_date": "2026-06-16",
        "end_date": "2028-02-18",
        "duration_months": 20,
    },
    
    "targets": {
        "portfolio_return_%": 30.0,
        "cagr_%": 18.0,
        "confidence_level_%": 75.0,
    },
    
    "validation_signals": [
        {"id": "B", "signal": "China Tariff > 25%", "weight": 0.20},
        {"id": "D", "signal": "Taiwan/geopolitical tension (PL exposure)", "weight": 0.20},
        {"id": "F", "signal": "Energy supply chain decoupling", "weight": 0.50},
        {"id": "H", "signal": "China growth rate < 4%", "weight": 0.10},
    ],
    
    "failure_conditions": [
        {"id": "C", "condition": "Portfolio drawdown > -20%"},
        {"id": "D_fail", "condition": "Trade deal WITH decoupling reversal (tariff cut + NO China financial opening + yuan strength). NOTE: a deal where China submits (opens financial markets, USD strengthens) = thesis SUCCESS, not failure."},
    ],
    
    "review_schedule": {
        "portfolio_level": "On every portfolio update",
        "hypothesis_level": "Every 3 months (quarterly)",
    },
}

# ═══════════════════════════════════════════════════════════════════════
# SIGNAL DEFINITIONS: 2026-06-18 Baseline
# ═══════════════════════════════════════════════════════════════════════

SIGNAL_DEFINITIONS = {
    "B": {
        "name": "China Tariff & Trade Restrictions",
        "description": "Trump tariff pressure on China",
        "current_value": 17.5,
        "unit": "%",
        "bullish_threshold": 25.0,
        "bearish_threshold": 10.0,
        "weight": 0.20,
        "data_source": "USTR announcements, Trump statements",
        "update_frequency": "event-driven",
        "components": [
            "Average tariff rate",
            "Semiconductor export controls",
            "Rare earth restrictions",
            "Technology licensing controls",
        ],
        "interpretation": {
            "bullish": "Tariff > 25% → Active trade war escalation",
            "neutral": "Tariff 10~25% → Ongoing pressure",
            "bearish": "Tariff < 10% → Trade war cooling",
        }
    },
    
    "D": {
        "name": "Taiwan Semiconductor Supply Chain Integration",
        "description": "TSMC & Taiwan's integration into US supply chain",
        "current_value": 40.0,
        "unit": "%",
        "bullish_threshold": 65.0,
        "bearish_threshold": 35.0,
        "weight": 0.20,
        "data_source": "TSMC announcements, Taiwan gov, military activity",
        "update_frequency": "monthly/event-driven",
        "components": [
            "Arizona fab construction (20%)",
            "TSMC US investment (15%)",
            "Taiwan pro-US alignment (15%)",
            "ASML tools control (15%)",
            "Military tension assessment (20%)",
        ],
        "interpretation": {
            "bullish": "Integration > 65% → Taiwan firmly in US orbit",
            "neutral": "Integration 35~65% → Ongoing integration",
            "bearish": "Integration < 35% → China gaining leverage",
        }
    },
    
    "F": {
        "name": "Energy Supply Chain Decoupling",
        "description": "US energy independence vs China access",
        "current_value": 35.0,
        "unit": "%",
        "bullish_threshold": 55.0,
        "bearish_threshold": 30.0,
        "weight": 0.20,
        "data_source": "EIA, WTI (CL=F), OPEC+ decisions, China trade",
        "update_frequency": "daily (WTI), weekly (EIA), event-driven",
        "wti_baseline": 74.75,
        "wti_bullish": (75.0, 85.0),
        "wti_bearish": 65.0,
        "components": [
            "WTI price stability (15%)",
            "US domestic production (15%)",
            "OPEC+ distance from China (15%)",
            "Rare earth/uranium supply (15%)",
            "China energy crisis signals (15%)",
        ],
        "interpretation": {
            "bullish": "Decoupling > 55% & WTI $75~$85 → US advantage in energy",
            "neutral": "Decoupling 30~55% & WTI $70~$75 → Current state",
            "bearish": "Decoupling < 30% & WTI <$65 → China alternatives working",
        }
    },
    
    "H": {
        "name": "China Economic Pressure",
        "description": "China economic slowdown from Trump pressure",
        "current_value": 5.0,
        "unit": "%",
        "bullish_threshold": 4.0,
        "bearish_threshold": 5.5,
        "weight": 0.20,
        "data_source": "NBS GDP, Caixin PMI, China customs, unemployment surveys",
        "update_frequency": "quarterly (GDP), monthly (PMI), event-driven",
        "sub_indicators": {
            "gdp_growth": 5.0,
            "manufacturing_pmi": 49.5,
            "export_growth": 2.5,
            "youth_unemployment": 20.8,
        },
        "interpretation": {
            "bullish": "China growth < 4% → Trump pressure succeeding",
            "neutral": "China growth 4~5.5% → Moderate slowdown",
            "bearish": "China growth > 5.5% → China resilient",
        }
    },
}

# ═══════════════════════════════════════════════════════════════════════
# BASELINE SNAPSHOT: 2026-06-16
# ═══════════════════════════════════════════════════════════════════════

BASELINE_SNAPSHOT = {
    "date": "2026-06-16",
    "signals": {
        "B": 17.5,
        "D": 40.0,
        "F": 35.0,
        "H": 5.0,
    },
    "notes": "Initial hypothesis setting date",
}

# ═══════════════════════════════════════════════════════════════════════
# SIGNAL DEFINITIONS: 2026-06-18 Baseline
# ═══════════════════════════════════════════════════════════════════════

SIGNAL_DEFINITIONS = {
    "B": {
        "name": "China Tariff",
        "current_value": 17.5,
        "bullish_threshold": 25.0,
        "bearish_threshold": 10.0,
        "weight": 0.20,  # COPX 노출 (1/4)
    },
    "D": {
        "name": "Taiwan Supply Chain",
        "current_value": 40.0,
        "bullish_threshold": 65.0,
        "bearish_threshold": 35.0,
        "weight": 0.20,  # PL 노출 (1/4)
    },
    "F": {
        "name": "Energy Decoupling",
        "current_value": 35.0,
        "bullish_threshold": 55.0,
        "bearish_threshold": 30.0,
        "weight": 0.50,  # COPX, TSES, TSNF 노출 (3/4) - 핵심 베팅
        "wti_baseline": 74.75,
    },
    "H": {
        "name": "China Growth Pressure",
        "current_value": 5.0,
        "bullish_threshold": 4.0,
        "bearish_threshold": 5.5,
        "weight": 0.10,  # Synthetic 배경 지표
    },
}
