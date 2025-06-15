import pandas as pd
import numpy as np
from ta.trend import EMAIndicator, SMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import logging
from time_analysis import TimeBasedAnalysis
from fundamental_analysis import FundamentalAnalysis
import time
import ta
from config import (
    TECHNICAL_INDICATORS,
    MARKET_SESSIONS,
    NOTIFICATIONS,
    ERROR_MESSAGES,
    CORRELATION_PAIRS
)

class AdvancedForexAnalysis:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.trade_history = {}
        self.time_analysis = TimeBasedAnalysis()
        self.fundamental_analysis = FundamentalAnalysis()
        self.risk_management = {
            'max_daily_trades': 3,
            'max_loss_per_trade': 0.02,  # 2% of account
            'max_daily_loss': 0.05,      # 5% of account
            'min_risk_reward': 1.5       # Minimum risk:reward ratio
        }
        
        # Define market sessions
        self.market_sessions = {
            'TOKYO': {'start': '00:00', 'end': '09:00'},
            'LONDON': {'start': '08:00', 'end': '17:00'},
            'NEW_YORK': {'start': '13:00', 'end': '22:00'},
            'SYDNEY': {'start': '22:00', 'end': '07:00'}
        }
        
        # Define volatility thresholds for different instruments
        self.volatility_thresholds = {
            'forex': 0.0005,  # 5 pips
            'gold': 0.5,      # 50 cents
            'silver': 0.05,   # 5 cents
            'oil': 0.5        # 50 cents
        }
        
        # Define correlation pairs
        self.correlation_pairs = {
            'EURUSD': ['GBPUSD', 'AUDUSD', 'NZDUSD'],
            'GBPUSD': ['EURUSD', 'EURGBP'],
            'USDJPY': ['EURJPY', 'GBPJPY'],
            'GOLD': ['SILVER', 'USDJPY'],
            'OIL': ['CADJPY', 'USDCAD']
        }

    def get_market_data(self, symbol, period='1d', interval='10m'):
        """Get market data with enhanced error handling and retry logic."""
        try:
            # Get data with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    data = yf.download(symbol, period=period, interval=interval)
                    if not data.empty:
                        return self._preprocess_data(data)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(1)
            
            raise Exception("Failed to fetch market data")
            
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return pd.DataFrame()

    def _preprocess_data(self, data):
        """Preprocess market data for analysis."""
        try:
            # Add time-based features
            data['Hour'] = data.index.hour
            data['Day'] = data.index.day_name()
            data['Month'] = data.index.month
            
            # Add price-based features
            data['Returns'] = data['Close'].pct_change()
            data['Log_Returns'] = np.log(data['Close'] / data['Close'].shift(1))
            
            # Add volatility features
            data['Volatility'] = data['Returns'].rolling(window=20).std()
            data['ATR'] = self._calculate_atr(data)
            
            # Add trend features
            data['Trend'] = self._calculate_trend(data)
            
            return data
            
        except Exception as e:
            print(f"Error preprocessing data: {e}")
            return data

    def calculate_advanced_indicators(self, data):
        """Calculate advanced technical indicators with enhanced accuracy."""
        try:
            # Basic indicators
            data['SMA_20'] = ta.trend.sma_indicator(data['Close'], window=20)
            data['SMA_50'] = ta.trend.sma_indicator(data['Close'], window=50)
            data['SMA_200'] = ta.trend.sma_indicator(data['Close'], window=200)
            
            # RSI with multiple timeframes
            data['RSI'] = ta.momentum.rsi(data['Close'], window=TECHNICAL_INDICATORS['RSI']['period'])
            data['RSI_4'] = ta.momentum.rsi(data['Close'], window=4)
            data['RSI_21'] = ta.momentum.rsi(data['Close'], window=21)
            
            # MACD with enhanced settings
            macd = ta.trend.MACD(
                data['Close'],
                window_slow=TECHNICAL_INDICATORS['MACD']['slow_period'],
                window_fast=TECHNICAL_INDICATORS['MACD']['fast_period'],
                window_sign=TECHNICAL_INDICATORS['MACD']['signal_period']
            )
            data['MACD'] = macd.macd()
            data['MACD_Signal'] = macd.macd_signal()
            data['MACD_Hist'] = macd.macd_diff()
            
            # Bollinger Bands with dynamic settings
            bollinger = ta.volatility.BollingerBands(
                data['Close'],
                window=TECHNICAL_INDICATORS['Bollinger']['period'],
                window_dev=TECHNICAL_INDICATORS['Bollinger']['std_dev']
            )
            data['BB_Upper'] = bollinger.bollinger_hband()
            data['BB_Middle'] = bollinger.bollinger_mavg()
            data['BB_Lower'] = bollinger.bollinger_lband()
            data['BB_Width'] = (data['BB_Upper'] - data['BB_Lower']) / data['BB_Middle']
            data['BB_Position'] = (data['Close'] - data['BB_Lower']) / (data['BB_Upper'] - data['BB_Lower'])
            
            # Stochastic with optimized settings
            stoch = ta.momentum.StochasticOscillator(
                data['High'],
                data['Low'],
                data['Close'],
                window=TECHNICAL_INDICATORS['Stochastic']['k_period'],
                smooth_window=TECHNICAL_INDICATORS['Stochastic']['slowing']
            )
            data['Stoch_K'] = stoch.stoch()
            data['Stoch_D'] = stoch.stoch_signal()
            
            # ATR for volatility
            data['ATR'] = ta.volatility.average_true_range(
                data['High'],
                data['Low'],
                data['Close'],
                window=TECHNICAL_INDICATORS['ATR']['period']
            )
            
            # Ichimoku Cloud
            ichimoku = ta.trend.IchimokuIndicator(
                data['High'],
                data['Low'],
                window1=TECHNICAL_INDICATORS['Ichimoku']['tenkan_period'],
                window2=TECHNICAL_INDICATORS['Ichimoku']['kijun_period'],
                window3=TECHNICAL_INDICATORS['Ichimoku']['senkou_span_b_period']
            )
            data['Ichimoku_A'] = ichimoku.ichimoku_a()
            data['Ichimoku_B'] = ichimoku.ichimoku_b()
            data['Ichimoku_Base'] = ichimoku.ichimoku_base_line()
            data['Ichimoku_Conversion'] = ichimoku.ichimoku_conversion_line()
            
            # Volume indicators
            data['OBV'] = ta.volume.on_balance_volume(data['Close'], data['Volume'])
            data['CMF'] = ta.volume.chaikin_money_flow(data['High'], data['Low'], data['Close'], data['Volume'])
            
            # Trend strength indicators
            data['ADX'] = ta.trend.adx(data['High'], data['Low'], data['Close'], window=14)
            data['CCI'] = ta.trend.cci(data['High'], data['Low'], data['Close'], window=20)
            
            # Momentum indicators
            data['ROC'] = ta.momentum.roc(data['Close'], window=10)
            data['MOM'] = ta.momentum.momentum(data['Close'], window=10)
            
            # Volatility indicators
            data['BB_Width'] = (data['BB_Upper'] - data['BB_Lower']) / data['BB_Middle']
            data['BB_Position'] = (data['Close'] - data['BB_Lower']) / (data['BB_Upper'] - data['BB_Lower'])
            
            return data
            
        except Exception as e:
            print(f"Error calculating indicators: {e}")
            return data

    def analyze_market_structure(self, data):
        """Analyze market structure with enhanced pattern recognition."""
        try:
            # Trend analysis
            data['Trend'] = self._analyze_trend(data)
            
            # Support and resistance levels
            data['Support'], data['Resistance'] = self._find_support_resistance(data)
            
            # Volatility analysis
            data['Volatility'] = self._analyze_volatility(data)
            
            # Volume analysis
            data['Volume_Trend'] = self._analyze_volume(data)
            
            # Pattern recognition
            data['Patterns'] = self._identify_patterns(data)
            
            # Market structure
            data['Market_Structure'] = self._analyze_market_structure(data)
            
            return data
            
        except Exception as e:
            print(f"Error analyzing market structure: {e}")
            return data

    def _analyze_trend(self, data):
        """Analyze market trend with multiple timeframes."""
        try:
            # Short-term trend (20 SMA)
            short_trend = np.where(data['Close'] > data['SMA_20'], 'UPTREND',
                                 np.where(data['Close'] < data['SMA_20'], 'DOWNTREND', 'SIDEWAYS'))
            
            # Medium-term trend (50 SMA)
            medium_trend = np.where(data['Close'] > data['SMA_50'], 'UPTREND',
                                  np.where(data['Close'] < data['SMA_50'], 'DOWNTREND', 'SIDEWAYS'))
            
            # Long-term trend (200 SMA)
            long_trend = np.where(data['Close'] > data['SMA_200'], 'UPTREND',
                                np.where(data['Close'] < data['SMA_200'], 'DOWNTREND', 'SIDEWAYS'))
            
            # Combine trends
            trend_strength = (short_trend == 'UPTREND').astype(int) + \
                           (medium_trend == 'UPTREND').astype(int) + \
                           (long_trend == 'UPTREND').astype(int)
            
            return np.where(trend_strength >= 2, 'UPTREND',
                          np.where(trend_strength <= 1, 'DOWNTREND', 'SIDEWAYS'))
            
        except Exception as e:
            print(f"Error analyzing trend: {e}")
            return np.array(['NEUTRAL'] * len(data))

    def _find_support_resistance(self, data):
        """Find support and resistance levels using advanced methods."""
        try:
            # Get local minima and maxima
            minima = self._find_local_minima(data['Low'].values)
            maxima = self._find_local_maxima(data['High'].values)
            
            # Calculate support levels
            support_levels = self._cluster_price_levels(data['Low'].values[minima])
            
            # Calculate resistance levels
            resistance_levels = self._cluster_price_levels(data['High'].values[maxima])
            
            return support_levels, resistance_levels
            
        except Exception as e:
            print(f"Error finding support/resistance: {e}")
            return [], []

    def _analyze_volatility(self, data):
        """Analyze market volatility."""
        try:
            # Calculate volatility metrics
            volatility = pd.DataFrame()
            
            # Historical volatility
            volatility['Historical'] = data['Returns'].rolling(window=20).std() * np.sqrt(252)
            
            # Implied volatility (if available)
            volatility['Implied'] = data['ATR'] / data['Close']
            
            # Volatility regime
            volatility['Regime'] = np.where(volatility['Historical'] > volatility['Historical'].mean() + volatility['Historical'].std(),
                                          'HIGH',
                                          np.where(volatility['Historical'] < volatility['Historical'].mean() - volatility['Historical'].std(),
                                                  'LOW', 'MEDIUM'))
            
            return volatility
            
        except Exception as e:
            print(f"Error analyzing volatility: {e}")
            return pd.DataFrame()

    def _analyze_volume(self, data):
        """Analyze trading volume patterns."""
        try:
            # Calculate volume metrics
            volume = pd.DataFrame()
            
            # Volume trend
            volume['Trend'] = np.where(data['Volume'] > data['Volume'].rolling(window=20).mean(), 'HIGH', 'LOW')
            
            # Volume relative to price
            volume['Price_Relation'] = np.where(data['Close'] > data['Close'].shift(1),
                                              np.where(data['Volume'] > data['Volume'].shift(1), 'BULLISH',
                                                      'WEAK_BULLISH'),
                                              np.where(data['Volume'] > data['Volume'].shift(1), 'BEARISH',
                                                      'WEAK_BEARISH'))
            
            # Volume profile
            volume['Profile'] = self._calculate_volume_profile(data)
            
            return volume
            
        except Exception as e:
            print(f"Error analyzing volume: {e}")
            return pd.DataFrame()

    def _calculate_volume_profile(self, data):
        """Calculate volume profile for price levels."""
        try:
            # Create price bins
            price_bins = np.linspace(data['Low'].min(), data['High'].max(), 50)
            
            # Calculate volume for each price level
            volume_profile = np.zeros_like(price_bins)
            for i in range(len(price_bins)-1):
                mask = (data['Close'] >= price_bins[i]) & (data['Close'] < price_bins[i+1])
                volume_profile[i] = data.loc[mask, 'Volume'].sum()
            
            return volume_profile
            
        except Exception as e:
            print(f"Error calculating volume profile: {e}")
            return np.array([])

    def _analyze_market_structure(self, data):
        """Analyze overall market structure."""
        try:
            structure = pd.DataFrame()
            
            # Trend structure
            structure['Trend'] = self._analyze_trend(data)
            
            # Volatility structure
            structure['Volatility'] = self._analyze_volatility(data)['Regime']
            
            # Volume structure
            structure['Volume'] = self._analyze_volume(data)['Trend']
            
            # Pattern structure
            structure['Patterns'] = self._identify_patterns(data)
            
            # Market regime
            structure['Regime'] = self._determine_market_regime(data)
            
            return structure
            
        except Exception as e:
            print(f"Error analyzing market structure: {e}")
            return pd.DataFrame()

    def _determine_market_regime(self, data):
        """Determine the current market regime."""
        try:
            # Calculate regime indicators
            trend = self._analyze_trend(data)
            volatility = self._analyze_volatility(data)['Regime']
            volume = self._analyze_volume(data)['Trend']
            
            # Combine indicators
            if trend[-1] == 'UPTREND' and volatility[-1] == 'LOW' and volume[-1] == 'HIGH':
                return 'STRONG_BULLISH'
            elif trend[-1] == 'DOWNTREND' and volatility[-1] == 'LOW' and volume[-1] == 'HIGH':
                return 'STRONG_BEARISH'
            elif trend[-1] == 'UPTREND' and volatility[-1] == 'HIGH':
                return 'VOLATILE_BULLISH'
            elif trend[-1] == 'DOWNTREND' and volatility[-1] == 'HIGH':
                return 'VOLATILE_BEARISH'
            else:
                return 'NEUTRAL'
                
        except Exception as e:
            print(f"Error determining market regime: {e}")
            return 'NEUTRAL'

    def generate_trading_signal(self, data, symbol):
        """Generate comprehensive trading signal with enhanced analysis."""
        try:
            # Get current price and indicators
            current_price = data['Close'].iloc[-1]
            
            # Technical analysis signals
            technical_signals = self._generate_technical_signals(data)
            
            # Time-based analysis
            time_analysis = self.time_analysis.analyze_time_patterns(data, symbol)
            
            # Fundamental analysis
            fundamental_analysis = self.fundamental_analysis.analyze(symbol)
            
            # Market structure analysis
            structure_analysis = self._analyze_market_structure(data)
            
            # Combine all analyses
            signal = self._combine_analyses(
                technical_signals,
                time_analysis,
                fundamental_analysis,
                structure_analysis
            )
            
            # Add signal details
            signal.update({
                'price': current_price,
                'symbol': symbol,
                'time_analysis': time_analysis,
                'fundamental_analysis': fundamental_analysis,
                'structure_analysis': structure_analysis
            })
            
            # Calculate entry, stop loss, and take profit levels
            if signal['signal'] != 'NEUTRAL':
                signal.update(self._calculate_trade_levels(data, signal['signal']))
            
            return signal
            
        except Exception as e:
            print(f"Error generating trading signal: {e}")
            return {
                'signal': 'NEUTRAL',
                'confidence': 0.0,
                'price': 0.0,
                'entry_price': 0.0,
                'stop_loss': 0.0,
                'take_profit': 0.0,
                'risk_reward_ratio': 0.0,
                'time_analysis': {},
                'fundamental_analysis': None,
                'structure_analysis': None
            }

    def _generate_technical_signals(self, data):
        """Generate technical analysis signals."""
        try:
            signals = []
            
            # RSI signals
            if data['RSI'].iloc[-1] < TECHNICAL_INDICATORS['RSI']['oversold']:
                signals.append(('BUY', 0.3))
            elif data['RSI'].iloc[-1] > TECHNICAL_INDICATORS['RSI']['overbought']:
                signals.append(('SELL', 0.3))
            
            # MACD signals
            if data['MACD'].iloc[-1] > data['MACD_Signal'].iloc[-1]:
                signals.append(('BUY', 0.2))
            elif data['MACD'].iloc[-1] < data['MACD_Signal'].iloc[-1]:
                signals.append(('SELL', 0.2))
            
            # Bollinger Bands signals
            if data['Close'].iloc[-1] < data['BB_Lower'].iloc[-1]:
                signals.append(('BUY', 0.2))
            elif data['Close'].iloc[-1] > data['BB_Upper'].iloc[-1]:
                signals.append(('SELL', 0.2))
            
            # Stochastic signals
            if data['Stoch_K'].iloc[-1] < 20 and data['Stoch_D'].iloc[-1] < 20:
                signals.append(('BUY', 0.2))
            elif data['Stoch_K'].iloc[-1] > 80 and data['Stoch_D'].iloc[-1] > 80:
                signals.append(('SELL', 0.2))
            
            # Trend signals
            if data['Trend'].iloc[-1] == 'UPTREND':
                signals.append(('BUY', 0.3))
            elif data['Trend'].iloc[-1] == 'DOWNTREND':
                signals.append(('SELL', 0.3))
            
            return signals
            
        except Exception as e:
            print(f"Error generating technical signals: {e}")
            return []

    def _combine_analyses(self, technical_signals, time_analysis, fundamental_analysis, structure_analysis):
        """Combine all analyses to generate final signal."""
        try:
            # Calculate signal weights
            buy_weight = sum(weight for signal, weight in technical_signals if signal == 'BUY')
            sell_weight = sum(weight for signal, weight in technical_signals if signal == 'SELL')
            
            # Add time analysis weight
            if time_analysis['recommendation'] == 'BUY':
                buy_weight += time_analysis['signal_strength']
            elif time_analysis['recommendation'] == 'SELL':
                sell_weight += time_analysis['signal_strength']
            
            # Add fundamental analysis weight
            if fundamental_analysis:
                if fundamental_analysis['recommendation'] == 'BUY':
                    buy_weight += fundamental_analysis['score']
                elif fundamental_analysis['recommendation'] == 'SELL':
                    sell_weight += fundamental_analysis['score']
            
            # Add structure analysis weight
            if structure_analysis['Regime'].iloc[-1] in ['STRONG_BULLISH', 'VOLATILE_BULLISH']:
                buy_weight += 0.3
            elif structure_analysis['Regime'].iloc[-1] in ['STRONG_BEARISH', 'VOLATILE_BEARISH']:
                sell_weight += 0.3
            
            # Determine final signal
            if buy_weight > sell_weight and buy_weight >= MIN_SIGNAL_CONFIDENCE:
                return {
                    'signal': 'BUY',
                    'confidence': buy_weight
                }
            elif sell_weight > buy_weight and sell_weight >= MIN_SIGNAL_CONFIDENCE:
                return {
                    'signal': 'SELL',
                    'confidence': sell_weight
                }
            else:
                return {
                    'signal': 'NEUTRAL',
                    'confidence': max(buy_weight, sell_weight)
                }
            
        except Exception as e:
            print(f"Error combining analyses: {e}")
            return {
                'signal': 'NEUTRAL',
                'confidence': 0.0
            }

    def _calculate_trade_levels(self, data, signal):
        """Calculate entry, stop loss, and take profit levels."""
        try:
            current_price = data['Close'].iloc[-1]
            atr = data['ATR'].iloc[-1]
            
            if signal == 'BUY':
                entry_price = current_price
                stop_loss = entry_price - (atr * STOP_LOSS_ATR_MULTIPLIER)
                take_profit = entry_price + (atr * TAKE_PROFIT_ATR_MULTIPLIER)
            else:
                entry_price = current_price
                stop_loss = entry_price + (atr * STOP_LOSS_ATR_MULTIPLIER)
                take_profit = entry_price - (atr * TAKE_PROFIT_ATR_MULTIPLIER)
            
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            risk_reward_ratio = reward / risk if risk != 0 else 0
            
            return {
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'risk_reward_ratio': risk_reward_ratio
            }
            
        except Exception as e:
            print(f"Error calculating trade levels: {e}")
            return {
                'entry_price': 0.0,
                'stop_loss': 0.0,
                'take_profit': 0.0,
                'risk_reward_ratio': 0.0
            }

    def _find_local_minima(self, data):
        """Find local minima in price data."""
        return np.where((data[1:-1] < data[:-2]) & (data[1:-1] < data[2:]))[0] + 1

    def _find_local_maxima(self, data):
        """Find local maxima in price data."""
        return np.where((data[1:-1] > data[:-2]) & (data[1:-1] > data[2:]))[0] + 1

    def _cluster_price_levels(self, prices):
        """Cluster price levels to find significant support/resistance."""
        try:
            from sklearn.cluster import KMeans
            
            # Reshape prices for clustering
            X = prices.reshape(-1, 1)
            
            # Determine number of clusters
            n_clusters = min(5, len(prices))
            
            # Perform clustering
            kmeans = KMeans(n_clusters=n_clusters)
            kmeans.fit(X)
            
            # Get cluster centers
            levels = kmeans.cluster_centers_.flatten()
            
            return np.sort(levels)
            
        except Exception as e:
            print(f"Error clustering price levels: {e}")
            return np.array([])

    def track_trade(self, trade_id, symbol, entry_price, stop_loss, take_profit, signal_type):
        """Track trade performance and send notifications"""
        self.trade_history[trade_id] = {
            'symbol': symbol,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'signal_type': signal_type,
            'entry_time': datetime.now(pytz.UTC),
            'status': 'OPEN',
            'exit_price': None,
            'exit_time': None,
            'profit_loss': None
        }

    def update_trade_status(self, trade_id, current_price):
        """Update trade status and generate notifications"""
        if trade_id not in self.trade_history:
            return None

        trade = self.trade_history[trade_id]
        
        # Check if stop loss or take profit was hit
        if trade['signal_type'] == 'BUY':
            if current_price <= trade['stop_loss']:
                trade['status'] = 'STOP_LOSS'
                trade['exit_price'] = current_price
                trade['exit_time'] = datetime.now(pytz.UTC)
                trade['profit_loss'] = (current_price - trade['entry_price']) / trade['entry_price']
            elif current_price >= trade['take_profit']:
                trade['status'] = 'TAKE_PROFIT'
                trade['exit_price'] = current_price
                trade['exit_time'] = datetime.now(pytz.UTC)
                trade['profit_loss'] = (current_price - trade['entry_price']) / trade['entry_price']
        else:  # SELL
            if current_price >= trade['stop_loss']:
                trade['status'] = 'STOP_LOSS'
                trade['exit_price'] = current_price
                trade['exit_time'] = datetime.now(pytz.UTC)
                trade['profit_loss'] = (trade['entry_price'] - current_price) / trade['entry_price']
            elif current_price <= trade['take_profit']:
                trade['status'] = 'TAKE_PROFIT'
                trade['exit_price'] = current_price
                trade['exit_time'] = datetime.now(pytz.UTC)
                trade['profit_loss'] = (trade['entry_price'] - current_price) / trade['entry_price']

        return trade

    def generate_trade_report(self, trade):
        """Generate detailed trade report"""
        if trade['status'] == 'OPEN':
            return None

        report = f"""
        📊 تقرير الصفقة - {trade['symbol']}
        
        نوع الصفقة: {'شراء' if trade['signal_type'] == 'BUY' else 'بيع'}
        سعر الدخول: {trade['entry_price']:.5f}
        سعر الخروج: {trade['exit_price']:.5f}
        وقت الدخول: {trade['entry_time'].strftime('%Y-%m-%d %H:%M:%S')}
        وقت الخروج: {trade['exit_time'].strftime('%Y-%m-%d %H:%M:%S')}
        
        النتيجة: {'✅ ربح' if trade['profit_loss'] > 0 else '❌ خسارة'}
        نسبة الربح/الخسارة: {trade['profit_loss']*100:.2f}%
        
        سبب الإغلاق: {'🎯 تحقيق الهدف' if trade['status'] == 'TAKE_PROFIT' else '🛑 وقف الخسارة'}
        """
        
        return report 