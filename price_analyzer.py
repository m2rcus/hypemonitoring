import numpy as np
import pandas as pd
from typing import List, Tuple, Dict
import logging
from config import TARGET_PRICE, STANDARD_DEVIATIONS, ALERT_THRESHOLD, CRITICAL_PRICE_THRESHOLD, STRONG_DOWNTREND_THRESHOLD

logger = logging.getLogger(__name__)

class PriceAnalyzer:
    def __init__(self, target_price: float = TARGET_PRICE, std_deviations: float = STANDARD_DEVIATIONS):
        self.target_price = target_price
        self.std_deviations = std_deviations
        self.price_history = []
        self.alert_sent = False
    
    def add_price(self, price: float):
        """Add a new price to the history"""
        self.price_history.append(price)
        # Keep only the last 100 prices to avoid memory issues
        if len(self.price_history) > 100:
            self.price_history = self.price_history[-100:]
    
    def calculate_statistics(self) -> Dict[str, float]:
        """Calculate statistical measures from price history"""
        if len(self.price_history) < 5:
            return {
                'mean': 0,
                'std': 0,
                'min': 0,
                'max': 0,
                'current': 0
            }
        
        prices = np.array(self.price_history)
        return {
            'mean': float(np.mean(prices)),
            'std': float(np.std(prices)),
            'min': float(np.min(prices)),
            'max': float(np.max(prices)),
            'current': float(prices[-1])
        }
    
    def predict_price_drop_probability(self) -> float:
        """Predict the probability of price dropping below target"""
        if len(self.price_history) < 10:
            return 0.0
        
        stats = self.calculate_statistics()
        current_price = stats['current']
        mean_price = stats['mean']
        std_price = stats['std']
        
        if std_price == 0:
            return 0.0
        
        # Calculate z-score for target price
        z_score = (self.target_price - mean_price) / std_price
        
        # Calculate probability using normal distribution
        # We want P(price < target_price)
        try:
            from scipy.stats import norm
            probability = norm.cdf(z_score)
            return probability
        except ImportError:
            # Fallback if scipy is not available
            # Simple approximation using error function
            import math
            probability = 0.5 * (1 + math.erf(z_score / math.sqrt(2)))
            return probability
    
    def should_alert(self) -> Tuple[bool, Dict]:
        """Determine if an alert should be sent"""
        if len(self.price_history) < 5:
            return False, {}
        
        stats = self.calculate_statistics()
        current_price = stats['current']
        
        # Check if current price is already below target
        if current_price <= self.target_price:
            return True, {
                'reason': 'current_price_below_target',
                'current_price': current_price,
                'target_price': self.target_price
            }
        
        # Check if price is within standard deviations of target
        lower_bound = stats['mean'] - (self.std_deviations * stats['std'])
        if current_price <= lower_bound:
            return True, {
                'reason': 'price_within_std_deviations',
                'current_price': current_price,
                'lower_bound': lower_bound,
                'std_deviations': self.std_deviations
            }
        
        # Check probability-based prediction
        drop_probability = self.predict_price_drop_probability()
        if drop_probability >= ALERT_THRESHOLD:
            return True, {
                'reason': 'high_drop_probability',
                'current_price': current_price,
                'drop_probability': drop_probability,
                'threshold': ALERT_THRESHOLD
            }
        
        return False, {}
    
    def is_urgent_alert(self) -> bool:
        """Determine if this is an urgent/critical alert"""
        if len(self.price_history) < 5:
            return False
        
        stats = self.calculate_statistics()
        current_price = stats['current']
        drop_probability = self.predict_price_drop_probability()
        trend = self.get_price_trend()
        
        # Critical conditions:
        # 1. Price is very close to target (within $0.50)
        # 2. Strong downtrend with high probability
        # 3. Price already below critical threshold
        
        is_critical_price = current_price <= CRITICAL_PRICE_THRESHOLD
        is_strong_downtrend = (trend == "strong_downtrend" and drop_probability >= STRONG_DOWNTREND_THRESHOLD)
        is_very_close = current_price <= (TARGET_PRICE + 0.5)
        
        return is_critical_price or is_strong_downtrend or is_very_close
    
    def get_price_trend(self) -> str:
        """Get the current price trend"""
        if len(self.price_history) < 10:
            return "insufficient_data"
        
        recent_prices = self.price_history[-10:]
        if len(recent_prices) < 2:
            return "insufficient_data"
        
        # Calculate simple moving average
        sma_5 = np.mean(recent_prices[-5:]) if len(recent_prices) >= 5 else np.mean(recent_prices)
        sma_10 = np.mean(recent_prices)
        
        current_price = recent_prices[-1]
        
        if current_price > sma_5 > sma_10:
            return "strong_uptrend"
        elif current_price > sma_5:
            return "uptrend"
        elif current_price < sma_5 < sma_10:
            return "strong_downtrend"
        elif current_price < sma_5:
            return "downtrend"
        else:
            return "sideways"
    
    def get_analysis_summary(self) -> Dict:
        """Get a comprehensive analysis summary"""
        stats = self.calculate_statistics()
        trend = self.get_price_trend()
        drop_probability = self.predict_price_drop_probability()
        should_alert, alert_info = self.should_alert()
        is_urgent = self.is_urgent_alert()
        
        return {
            'current_price': stats['current'],
            'mean_price': stats['mean'],
            'std_deviation': stats['std'],
            'price_range': {
                'min': stats['min'],
                'max': stats['max']
            },
            'trend': trend,
            'drop_probability': drop_probability,
            'target_price': self.target_price,
            'should_alert': should_alert,
            'is_urgent': is_urgent,
            'alert_info': alert_info,
            'price_history_length': len(self.price_history)
        } 