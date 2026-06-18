# analysis/portfolio_thesis.py
# Core Portfolio Thesis Mapping & Failure Signals

CORE_PORTFOLIO = {
    "PL": {
        "name": "Planet Labs",
        "sector": "space",
        "thesis": "US space tech dominance for Indo-Pacific surveillance & defense",
        "hypothesis_link": "H3",  # Industrial supply chain
        "signal_exposure": ["D", "B"],  # Taiwan integration, tariff pressure
        "current_price": 30.44,
        "current_return_%": 98.96,
        "failure_signal": "Defense budget cuts OR competitor tech breakthrough",
    },
    "IONQ": {
        "name": "IonQ",
        "sector": "technology",
        "thesis": "US quantum computing leadership in strategic tech war",
        "hypothesis_link": "H3",
        "signal_exposure": ["B"],  # Tech export controls
        "current_price": 61.32,
        "current_return_%": 9.48,
        "failure_signal": "China quantum computing breakthrough OR US chip export easing",
    },
    "HOOD": {
        "name": "Robinhood Markets",
        "sector": "finance",
        "thesis": "USD hegemony reinforced via US financial platform dominance",
        "hypothesis_link": "H2",  # Monetary hegemony
        "signal_exposure": ["A"],  # USD strength direct impact
        "current_price": None,
        "current_return_%": 30.95,
        "failure_signal": "Dollar weakness OR US financial regulation tightening",
    },
    "COPX": {
        "name": "Copper Miners ETF",
        "sector": "energy/materials",
        "thesis": "US supply chain control via critical minerals independence",
        "hypothesis_link": "H3",
        "signal_exposure": ["F"],  # Energy decoupling
        "current_price": None,
        "current_return_%": 42.67,
        "failure_signal": "China mineral export cooperation OR supply normalization",
    },
    "URA": {
        "name": "Uranium ETF",
        "sector": "energy",
        "thesis": "Energy independence & nuclear power expansion",
        "hypothesis_link": "H3",
        "signal_exposure": ["F"],  # Energy decoupling
        "current_price": None,
        "current_return_%": -7.65,
        "status": "SOLD (2026-06-29)",
        "exit_reason": "Iran nuclear deal signal triggered failure condition",
        "failure_signal": "Renewable energy collapse OR nuclear policy reversal",
    },
    "TSES": {
        "name": "TechX Energy",
        "sector": "energy",
        "thesis": "Energy supply chain resilience through diversification",
        "hypothesis_link": "H3",
        "signal_exposure": ["F"],
        "current_price": None,
        "current_return_%": 15.21,
        "failure_signal": "Energy supply normalization OR China alternative supply secured",
    },
    "TSNF": {
        "name": "Transocean",
        "sector": "offshore energy",
        "thesis": "Maritime resource control & ocean geopolitics advantage",
        "hypothesis_link": "H3",
        "signal_exposure": ["F"],
        "current_price": None,
        "current_return_%": 20.26,
        "failure_signal": "International maritime law weakening OR China offshore expansion",
    },
}

SATELLITE_PORTFOLIO = {
    "BMNR": {
        "name": "Bitmine",
        "sector": "crypto",
        "thesis": "Personal judgment - digital currency control mechanism",
        "status": "SATELLITE (Excluded from hypothesis validation)",
        "current_return_%": -1.78,
    },
    "RXRX": {
        "name": "Recursion Pharma",
        "sector": "biotech",
        "thesis": "Personal judgment - AI-driven pharmaceutical independence",
        "status": "SATELLITE (Excluded from hypothesis validation)",
        "current_return_%": -47.64,
    },
}

PORTFOLIO_PERFORMANCE = {
    "portfolio_inception": "2026-06-16",
    "current_date": "2026-06-18",
    "core_portfolio_return_%": 25.50,
    "benchmark_spy_return_%": 12.50,
    "alpha_%": 13.00,
    "target_return_%": 30.00,
    "target_timeline": "20 months (2026-06-16 to 2028-02-18)",
}

