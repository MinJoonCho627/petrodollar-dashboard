# analysis/portfolio_thesis.py
# Core Portfolio Thesis Mapping & Failure Signals

CORE_PORTFOLIO = {
    "PL": {
        "name": "Planet Labs",
        "sector": "space",
        "thesis": "US space/satellite dominance in US-China tech frontier competition (AI imagery, defense/surveillance)",
        "hypothesis_link": "D-axis",  # Tech & frontier dominance
        "signal_exposure": ["D"],  # US-China tech/space dominance
        "current_price": None,
        "failure_signal": "US loses space/satellite lead OR competitor breakthrough. NOTE: also held inside TSNF (double exposure to PL).",
    },
    "COPX": {
        "name": "Copper Miners ETF",
        "sector": "energy/materials",
        "thesis": "US supply chain control via critical minerals independence",
        "hypothesis_link": "F-axis",
        "signal_exposure": ["F"],  # Energy decoupling
        "current_price": None,
        "failure_signal": "China mineral export cooperation OR supply normalization",
    },
    "URA": {
        "name": "Uranium ETF",
        "sector": "energy",
        "thesis": "Energy independence & nuclear power expansion",
        "hypothesis_link": "F-axis",
        "signal_exposure": ["F"],  # Energy decoupling
        "current_price": None,
        "status": "SOLD (2026-06-18)",
        "exit_reason": "Iran deal triggered pre-defined failure condition, confirmed 2026-06-18. Original thesis (Iran risk -> uranium premium) closed at -7.65%.",
        "failure_signal": "Renewable energy collapse OR nuclear policy reversal",
    },
    "TSES": {
        "name": "Truth Social American Energy Security ETF",
        "sector": "energy (ETF basket: Exxon, Chevron, ConocoPhillips, nuclear utils)",
        "thesis": "Trump energy doctrine -- fossil fuel expansion + nuclear revival. US energy supply dominance curbs China's cheap sanctioned-oil access.",
        "hypothesis_link": "F-axis",
        "signal_exposure": ["F"],
        "current_price": None,
        "failure_signal": "Energy policy reversal OR US-China energy normalization. NOTE: new ETF (Dec 2025), small AUM ~$10M, Trump-brand political risk.",
    },
    "TSNF": {
        "name": "Truth Social American Next Frontiers ETF",
        "sector": "tech frontier (ETF basket: Planet Labs, Intuitive Machines, Micron, Marvell)",
        "thesis": "US-China tech/space/military frontier dominance -- space, AI, semiconductors. Note: PL is a top holding (overlaps with direct PL position).",
        "hypothesis_link": "D-axis",
        "signal_exposure": ["D"],
        "current_price": None,
        "failure_signal": "China closes tech/space gap OR US loses semiconductor/AI lead. NOTE: new ETF (Dec 2025), Trump-brand political risk, double-exposure to PL.",
    },
}

SATELLITE_PORTFOLIO = {
    "HOOD": {
        "name": "Robinhood Markets",
        "sector": "finance",
        "thesis": "Personal judgment - crypto adoption + US domestic political tailwind (NOT decoupling thesis)",
        "status": "SATELLITE (Excluded from hypothesis validation)",
    },
    "IONQ": {
        "name": "IonQ",
        "sector": "technology",
        "thesis": "Personal judgment - standalone quantum computing bet (NOT decoupling thesis)",
        "status": "SATELLITE (Excluded from hypothesis validation)",
    },
    "BMNR": {
        "name": "Bitmine",
        "sector": "crypto",
        "thesis": "Personal judgment - digital currency control mechanism",
        "status": "SATELLITE (Excluded from hypothesis validation)",
    },
    "RXRX": {
        "name": "Recursion Pharma",
        "sector": "biotech",
        "thesis": "Personal judgment - AI-driven pharmaceutical independence",
        "status": "SATELLITE (Excluded from hypothesis validation)",
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

