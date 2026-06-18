# analysis/hypothesis_validator.py (수정 버전)

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import INITIAL_HYPOTHESIS, SIGNAL_DEFINITIONS, BASELINE_SNAPSHOT
from datetime import datetime

class HypothesisValidator:
    
    def __init__(self):
        self.hypothesis = INITIAL_HYPOTHESIS
        self.signals = SIGNAL_DEFINITIONS
        self.baseline = BASELINE_SNAPSHOT
        self.validation_history = []
    
    def calculate_signal_achievement(self, signal_id, current_value):
        """각 신호의 진행도 계산 (0-100%)"""
        if signal_id not in self.signals:
            return 0.0
        
        sig = self.signals[signal_id]
        bullish = sig["bullish_threshold"]
        bearish = sig["bearish_threshold"]
        
        # Signal H (China growth): 낮을수록 좋음
        if signal_id == "H":
            if current_value <= bullish:
                achievement = 100.0
            elif current_value >= bearish:
                achievement = 0.0
            else:
                # 중간값
                achievement = ((bearish - current_value) / (bearish - bullish)) * 100
        else:
            # 나머지 신호: 높을수록 좋음
            if current_value >= bullish:
                achievement = 100.0
            elif current_value <= bearish:
                achievement = 0.0
            else:
                achievement = ((current_value - bearish) / (bullish - bearish)) * 100
        
        return min(max(achievement, 0), 100)
    
    def validate_hypothesis(self, current_signals):
        """가설 신뢰도 계산"""
        validation_results = {}
        total_weighted_achievement = 0.0
        bullish_count = 0  # 80% 이상 신호 카운트
        
        for signal_id in ["A", "B", "D", "F", "H"]:
            sig = self.signals[signal_id]
            current_value = current_signals.get(signal_id, sig["current_value"])
            weight = sig["weight"]
            
            achievement = self.calculate_signal_achievement(signal_id, current_value)
            
            # Status
            if achievement >= 80:
                status = "✓ Bullish"
                bullish_count += 1
            elif achievement >= 50:
                status = "△ Neutral"
            else:
                status = "✗ Bearish"
            
            validation_results[signal_id] = {
                "signal_name": sig["name"],
                "current_value": current_value,
                "bullish_threshold": sig["bullish_threshold"],
                "bearish_threshold": sig["bearish_threshold"],
                "achievement_%": round(achievement, 1),
                "status": status,
                "weight": weight,
                "weighted_score": achievement * weight,
            }
            
            total_weighted_achievement += achievement * weight
        
        overall_confidence = round(total_weighted_achievement / 100.0 * 100.0, 1)
        
        # 더 현실적인 status 판정
        if overall_confidence >= 80:
            hypothesis_status = "✅ STRONG (4~5 bullish signals)"
        elif overall_confidence >= 70:
            hypothesis_status = "🟢 ON TRACK (3 bullish signals)"
        elif overall_confidence >= 50:
            hypothesis_status = "🟡 PROGRESSING (2 bullish signals)"
        elif overall_confidence >= 30:
            hypothesis_status = "🔵 EARLY STAGE (signals advancing)"
        else:
            hypothesis_status = "🔴 FAILED (signals reversing)"
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "signals": validation_results,
            "overall_confidence_%": overall_confidence,
            "bullish_signals": bullish_count,
            "hypothesis_status": hypothesis_status,
        }
        
        self.validation_history.append(result)
        return result
    
    def print_validation(self, result):
        """검증 결과 출력"""
        print("=" * 70)
        print("HYPOTHESIS VALIDATION (2026-06-18)")
        print("=" * 70)
        print(f"\nOverall Confidence: {result['overall_confidence_%']}%")
        print(f"Bullish Signals: {result['bullish_signals']}/5")
        print(f"Status: {result['hypothesis_status']}")
        
        print("\n" + "─" * 70)
        print("SIGNAL BREAKDOWN:")
        print("─" * 70)
        
        for signal_id in ["A", "B", "D", "F", "H"]:
            sig = result['signals'][signal_id]
            bar_length = int(sig['achievement_%'] / 5)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            
            print(f"\n{signal_id}. {sig['signal_name']}")
            print(f"   {bar} {sig['achievement_%']}%  {sig['status']}")
            print(f"   Current: {sig['current_value']} | Target: {sig['bullish_threshold']}")
        
        print("\n" + "=" * 70)

if __name__ == "__main__":
    validator = HypothesisValidator()
    
    current_signals = {
        "A": 28.18,
        "B": 17.5,
        "D": 40.0,
        "F": 35.0,
        "H": 5.0,
    }
    
    result = validator.validate_hypothesis(current_signals)
    validator.print_validation(result)
