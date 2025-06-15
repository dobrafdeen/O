import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from config import *

class TimeBasedAnalysis:
    def __init__(self):
        self.market_sessions = MARKET_SESSIONS
        self.timezone = pytz.UTC
        
    def get_market_session(self, timestamp=None):
        """Get current market session."""
        try:
            if timestamp is None:
                timestamp = datetime.now(self.timezone)
            
            # Convert timestamp to UTC if not already
            if timestamp.tzinfo is None:
                timestamp = self.timezone.localize(timestamp)
            
            # Get current hour in UTC
            current_hour = timestamp.hour
            
            # Determine active session
            for session, hours in self.market_sessions.items():
                if hours['start'] <= current_hour < hours['end']:
                    return session
            
            return 'CLOSED'
            
        except Exception as e:
            print(f"Error getting market session: {e}")
            return 'UNKNOWN'

    def analyze_time_patterns(self, data, symbol):
        """Analyze time-based patterns in price data."""
        try:
            # Add time-based features
            data = self._add_time_features(data)
            
            # Analyze session patterns
            session_patterns = self._analyze_session_patterns(data)
            
            # Analyze intraday patterns
            intraday_patterns = self._analyze_intraday_patterns(data)
            
            # Analyze weekly patterns
            weekly_patterns = self._analyze_weekly_patterns(data)
            
            # Analyze monthly patterns
            monthly_patterns = self._analyze_monthly_patterns(data)
            
            # Combine patterns
            patterns = {
                'session': session_patterns,
                'intraday': intraday_patterns,
                'weekly': weekly_patterns,
                'monthly': monthly_patterns
            }
            
            # Generate recommendation
            recommendation = self._generate_time_recommendation(patterns)
            
            return {
                'patterns': patterns,
                'recommendation': recommendation,
                'signal_strength': self._calculate_signal_strength(patterns)
            }
            
        except Exception as e:
            print(f"Error analyzing time patterns: {e}")
            return {
                'patterns': {},
                'recommendation': 'NEUTRAL',
                'signal_strength': 0.0
            }

    def _add_time_features(self, data):
        """Add time-based features to the data."""
        try:
            # Add hour feature
            data['Hour'] = data.index.hour
            
            # Add day of week feature
            data['DayOfWeek'] = data.index.dayofweek
            
            # Add month feature
            data['Month'] = data.index.month
            
            # Add session feature
            data['Session'] = data.index.map(lambda x: self.get_market_session(x))
            
            return data
            
        except Exception as e:
            print(f"Error adding time features: {e}")
            return data

    def _analyze_session_patterns(self, data):
        """Analyze patterns during different market sessions."""
        try:
            patterns = {}
            
            for session in self.market_sessions.keys():
                # Filter data for session
                session_data = data[data['Session'] == session]
                
                if not session_data.empty:
                    # Calculate session statistics
                    patterns[session] = {
                        'volatility': self._calculate_session_volatility(session_data),
                        'trend': self._calculate_session_trend(session_data),
                        'volume': self._calculate_session_volume(session_data),
                        'profitability': self._calculate_session_profitability(session_data)
                    }
            
            return patterns
            
        except Exception as e:
            print(f"Error analyzing session patterns: {e}")
            return {}

    def _analyze_intraday_patterns(self, data):
        """Analyze intraday patterns."""
        try:
            patterns = {}
            
            # Group by hour
            hourly_data = data.groupby('Hour')
            
            for hour, group in hourly_data:
                patterns[hour] = {
                    'volatility': self._calculate_hourly_volatility(group),
                    'trend': self._calculate_hourly_trend(group),
                    'volume': self._calculate_hourly_volume(group),
                    'profitability': self._calculate_hourly_profitability(group)
                }
            
            return patterns
            
        except Exception as e:
            print(f"Error analyzing intraday patterns: {e}")
            return {}

    def _analyze_weekly_patterns(self, data):
        """Analyze weekly patterns."""
        try:
            patterns = {}
            
            # Group by day of week
            daily_data = data.groupby('DayOfWeek')
            
            for day, group in daily_data:
                patterns[day] = {
                    'volatility': self._calculate_daily_volatility(group),
                    'trend': self._calculate_daily_trend(group),
                    'volume': self._calculate_daily_volume(group),
                    'profitability': self._calculate_daily_profitability(group)
                }
            
            return patterns
            
        except Exception as e:
            print(f"Error analyzing weekly patterns: {e}")
            return {}

    def _analyze_monthly_patterns(self, data):
        """Analyze monthly patterns."""
        try:
            patterns = {}
            
            # Group by month
            monthly_data = data.groupby('Month')
            
            for month, group in monthly_data:
                patterns[month] = {
                    'volatility': self._calculate_monthly_volatility(group),
                    'trend': self._calculate_monthly_trend(group),
                    'volume': self._calculate_monthly_volume(group),
                    'profitability': self._calculate_monthly_profitability(group)
                }
            
            return patterns
            
        except Exception as e:
            print(f"Error analyzing monthly patterns: {e}")
            return {}

    def _calculate_session_volatility(self, data):
        """Calculate volatility during a session."""
        try:
            return data['Returns'].std() * np.sqrt(252)
        except Exception as e:
            print(f"Error calculating session volatility: {e}")
            return 0.0

    def _calculate_session_trend(self, data):
        """Calculate trend during a session."""
        try:
            returns = data['Returns'].mean()
            return 'UPTREND' if returns > 0 else 'DOWNTREND' if returns < 0 else 'NEUTRAL'
        except Exception as e:
            print(f"Error calculating session trend: {e}")
            return 'NEUTRAL'

    def _calculate_session_volume(self, data):
        """Calculate volume during a session."""
        try:
            return data['Volume'].mean()
        except Exception as e:
            print(f"Error calculating session volume: {e}")
            return 0.0

    def _calculate_session_profitability(self, data):
        """Calculate profitability during a session."""
        try:
            return data['Returns'].mean()
        except Exception as e:
            print(f"Error calculating session profitability: {e}")
            return 0.0

    def _calculate_hourly_volatility(self, data):
        """Calculate hourly volatility."""
        try:
            return data['Returns'].std() * np.sqrt(252)
        except Exception as e:
            print(f"Error calculating hourly volatility: {e}")
            return 0.0

    def _calculate_hourly_trend(self, data):
        """Calculate hourly trend."""
        try:
            returns = data['Returns'].mean()
            return 'UPTREND' if returns > 0 else 'DOWNTREND' if returns < 0 else 'NEUTRAL'
        except Exception as e:
            print(f"Error calculating hourly trend: {e}")
            return 'NEUTRAL'

    def _calculate_hourly_volume(self, data):
        """Calculate hourly volume."""
        try:
            return data['Volume'].mean()
        except Exception as e:
            print(f"Error calculating hourly volume: {e}")
            return 0.0

    def _calculate_hourly_profitability(self, data):
        """Calculate hourly profitability."""
        try:
            return data['Returns'].mean()
        except Exception as e:
            print(f"Error calculating hourly profitability: {e}")
            return 0.0

    def _calculate_daily_volatility(self, data):
        """Calculate daily volatility."""
        try:
            return data['Returns'].std() * np.sqrt(252)
        except Exception as e:
            print(f"Error calculating daily volatility: {e}")
            return 0.0

    def _calculate_daily_trend(self, data):
        """Calculate daily trend."""
        try:
            returns = data['Returns'].mean()
            return 'UPTREND' if returns > 0 else 'DOWNTREND' if returns < 0 else 'NEUTRAL'
        except Exception as e:
            print(f"Error calculating daily trend: {e}")
            return 'NEUTRAL'

    def _calculate_daily_volume(self, data):
        """Calculate daily volume."""
        try:
            return data['Volume'].mean()
        except Exception as e:
            print(f"Error calculating daily volume: {e}")
            return 0.0

    def _calculate_daily_profitability(self, data):
        """Calculate daily profitability."""
        try:
            return data['Returns'].mean()
        except Exception as e:
            print(f"Error calculating daily profitability: {e}")
            return 0.0

    def _calculate_monthly_volatility(self, data):
        """Calculate monthly volatility."""
        try:
            return data['Returns'].std() * np.sqrt(252)
        except Exception as e:
            print(f"Error calculating monthly volatility: {e}")
            return 0.0

    def _calculate_monthly_trend(self, data):
        """Calculate monthly trend."""
        try:
            returns = data['Returns'].mean()
            return 'UPTREND' if returns > 0 else 'DOWNTREND' if returns < 0 else 'NEUTRAL'
        except Exception as e:
            print(f"Error calculating monthly trend: {e}")
            return 'NEUTRAL'

    def _calculate_monthly_volume(self, data):
        """Calculate monthly volume."""
        try:
            return data['Volume'].mean()
        except Exception as e:
            print(f"Error calculating monthly volume: {e}")
            return 0.0

    def _calculate_monthly_profitability(self, data):
        """Calculate monthly profitability."""
        try:
            return data['Returns'].mean()
        except Exception as e:
            print(f"Error calculating monthly profitability: {e}")
            return 0.0

    def _generate_time_recommendation(self, patterns):
        """Generate trading recommendation based on time patterns."""
        try:
            # Get current session
            current_session = self.get_market_session()
            
            # Get current hour
            current_hour = datetime.now(self.timezone).hour
            
            # Get current day
            current_day = datetime.now(self.timezone).weekday()
            
            # Get current month
            current_month = datetime.now(self.timezone).month
            
            # Calculate recommendation score
            score = 0.0
            
            # Add session score
            if current_session in patterns['session']:
                session_data = patterns['session'][current_session]
                score += self._calculate_pattern_score(session_data)
            
            # Add hourly score
            if current_hour in patterns['intraday']:
                hourly_data = patterns['intraday'][current_hour]
                score += self._calculate_pattern_score(hourly_data)
            
            # Add daily score
            if current_day in patterns['weekly']:
                daily_data = patterns['weekly'][current_day]
                score += self._calculate_pattern_score(daily_data)
            
            # Add monthly score
            if current_month in patterns['monthly']:
                monthly_data = patterns['monthly'][current_month]
                score += self._calculate_pattern_score(monthly_data)
            
            # Normalize score
            score = score / 4.0
            
            # Generate recommendation
            if score >= 0.7:
                return 'STRONG_BUY'
            elif score >= 0.6:
                return 'BUY'
            elif score <= 0.3:
                return 'STRONG_SELL'
            elif score <= 0.4:
                return 'SELL'
            else:
                return 'NEUTRAL'
            
        except Exception as e:
            print(f"Error generating time recommendation: {e}")
            return 'NEUTRAL'

    def _calculate_pattern_score(self, pattern_data):
        """Calculate score from pattern data."""
        try:
            # Calculate weighted score
            score = (
                self._normalize_volatility(pattern_data['volatility']) * 0.3 +
                self._normalize_trend(pattern_data['trend']) * 0.3 +
                self._normalize_volume(pattern_data['volume']) * 0.2 +
                self._normalize_profitability(pattern_data['profitability']) * 0.2
            )
            
            return score
            
        except Exception as e:
            print(f"Error calculating pattern score: {e}")
            return 0.0

    def _normalize_volatility(self, volatility):
        """Normalize volatility value."""
        try:
            # Implement volatility normalization
            # This is a placeholder for actual implementation
            return 0.0
            
        except Exception as e:
            print(f"Error normalizing volatility: {e}")
            return 0.0

    def _normalize_trend(self, trend):
        """Normalize trend value."""
        try:
            if trend == 'UPTREND':
                return 1.0
            elif trend == 'DOWNTREND':
                return 0.0
            else:
                return 0.5
                
        except Exception as e:
            print(f"Error normalizing trend: {e}")
            return 0.5

    def _normalize_volume(self, volume):
        """Normalize volume value."""
        try:
            # Implement volume normalization
            # This is a placeholder for actual implementation
            return 0.0
            
        except Exception as e:
            print(f"Error normalizing volume: {e}")
            return 0.0

    def _normalize_profitability(self, profitability):
        """Normalize profitability value."""
        try:
            # Implement profitability normalization
            # This is a placeholder for actual implementation
            return 0.0
            
        except Exception as e:
            print(f"Error normalizing profitability: {e}")
            return 0.0

    def _calculate_signal_strength(self, patterns):
        """Calculate overall signal strength from patterns."""
        try:
            # Calculate weighted average of pattern scores
            total_score = 0.0
            total_weight = 0.0
            
            # Add session pattern score
            if patterns['session']:
                session_score = sum(self._calculate_pattern_score(data) for data in patterns['session'].values())
                total_score += session_score
                total_weight += 1.0
            
            # Add intraday pattern score
            if patterns['intraday']:
                intraday_score = sum(self._calculate_pattern_score(data) for data in patterns['intraday'].values())
                total_score += intraday_score
                total_weight += 1.0
            
            # Add weekly pattern score
            if patterns['weekly']:
                weekly_score = sum(self._calculate_pattern_score(data) for data in patterns['weekly'].values())
                total_score += weekly_score
                total_weight += 1.0
            
            # Add monthly pattern score
            if patterns['monthly']:
                monthly_score = sum(self._calculate_pattern_score(data) for data in patterns['monthly'].values())
                total_score += monthly_score
                total_weight += 1.0
            
            # Calculate final score
            if total_weight > 0:
                return total_score / total_weight
            else:
                return 0.0
                
        except Exception as e:
            print(f"Error calculating signal strength: {e}")
            return 0.0 