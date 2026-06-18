# analysis/benchmark_metrics.py
# Benchmark & Risk-Adjusted Performance Metrics

import math
from datetime import datetime

class BenchmarkMetrics:
    """
    포트폴리오 성과를 SPY/QQQ와 비교하는 metrics 계산
    """
    
    def __init__(self):
        # 2026-06-16 ~ 2026-06-18 (2일간의 데이터)
        self.portfolio = {
            "PL": 98.96,
            "IONQ": 9.48,
            "HOOD": 30.95,
            "COPX": 42.67,
            "TSES": 15.21,
            "TSNF": 20.26,
        }  # URA는 손절로 제외
        
        self.benchmark = {
            "SPY": 12.50,
            "QQQ": 14.20,
            "DXY": -1.50,  # 달러 약세
        }
        
        self.portfolio_return = 25.50
        self.risk_free_rate = 0.045  # 4.5% annual (US 10yr Treasury)
    
    def calculate_alpha(self):
        """Alpha = 포트폴리오 수익 - SPY 수익"""
        alpha = self.portfolio_return - self.benchmark["SPY"]
        return alpha
    
    def calculate_sharpe_ratio(self, volatility=0.18):
        """
        Sharpe Ratio = (Return - Risk-Free Rate) / Volatility
        
        가정: 연간 변동성 18% (고성장 포트폴리오)
        """
        excess_return = self.portfolio_return - self.risk_free_rate
        sharpe = excess_return / volatility if volatility > 0 else 0
        return sharpe
    
    def calculate_information_ratio(self, tracking_error=0.12):
        """
        Information Ratio = Alpha / Tracking Error
        
        가정: Tracking error 12% (SPY 추종도)
        """
        alpha = self.calculate_alpha()
        ir = alpha / tracking_error if tracking_error > 0 else 0
        return ir
    
    def estimate_max_drawdown(self):
        """
        Max Drawdown 추정 (worst-case scenario)
        
        현재 상태에서 가장 큰 손실을 본 종목을 기반으로
        """
        worst_loss = -47.64  # RXRX (satellite)
        
        # Core만 보면
        core_losses = [l for l in self.portfolio.values() if l < 0]
        core_max_loss = min(core_losses) if core_losses else 0
        
        # Core weighted average drawdown
        core_weighted = abs(core_max_loss) * 0.1  # 최악 시나리오
        
        return -core_weighted
    
    def calculate_sortino_ratio(self, downside_volatility=0.08):
        """
        Sortino Ratio = (Return - Risk-Free) / Downside Volatility
        
        가정: 하방 변동성 8%
        """
        excess_return = self.portfolio_return - self.risk_free_rate
        sortino = excess_return / downside_volatility if downside_volatility > 0 else 0
        return sortino
    
    def get_performance_summary(self):
        """성과 종합 요약"""
        return {
            "portfolio_return_%": self.portfolio_return,
            "spy_benchmark_%": self.benchmark["SPY"],
            "qqq_benchmark_%": self.benchmark["QQQ"],
            "alpha_%": self.calculate_alpha(),
            "sharpe_ratio": round(self.calculate_sharpe_ratio(), 2),
            "information_ratio": round(self.calculate_information_ratio(), 2),
            "sortino_ratio": round(self.calculate_sortino_ratio(), 2),
            "max_drawdown_%": round(self.estimate_max_drawdown(), 1),
            "period": "2026-06-16 to 2026-06-18",
        }

if __name__ == "__main__":
    metrics = BenchmarkMetrics()
    summary = metrics.get_performance_summary()
    
    print("=" * 70)
    print("BENCHMARK & RISK METRICS SUMMARY")
    print("=" * 70)
    print(f"\nPortfolio Return: {summary['portfolio_return_%']}%")
    print(f"SPY Benchmark: {summary['spy_benchmark_%']}%")
    print(f"QQQ Benchmark: {summary['qqq_benchmark_%']}%")
    print(f"\nAlpha (excess over SPY): {summary['alpha_%']}%")
    print(f"Sharpe Ratio: {summary['sharpe_ratio']}")
    print(f"Information Ratio: {summary['information_ratio']}")
    print(f"Sortino Ratio: {summary['sortino_ratio']}")
    print(f"Max Drawdown: {summary['max_drawdown_%']}%")
    print(f"\nPeriod: {summary['period']}")
    print("=" * 70)
