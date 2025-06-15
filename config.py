"""
Configuration settings for the Advanced Forex Trading Bot
"""

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "7715480057:AAFwcGbgmSlIllstlr_FK6cfwDRVPdJadPk"
TELEGRAM_CHANNEL_ID = "-1002232773213"

# Bot Settings
DEFAULT_TIMEFRAME = "10m"  # Changed to 10 minutes
ANALYSIS_INTERVAL = "10m"  # Analysis every 10 minutes
RISK_PERCENTAGE = 2
MAX_TRADES = 3
NOTIFICATION_INTERVAL = "10m"

# Market Analysis Settings
TECHNICAL_ANALYSIS_WEIGHT = 0.4
FUNDAMENTAL_ANALYSIS_WEIGHT = 0.3
TIME_ANALYSIS_WEIGHT = 0.3
MIN_SIGNAL_CONFIDENCE = 0.75  # Increased for higher quality signals

# Risk Management
STOP_LOSS_ATR_MULTIPLIER = 2
TAKE_PROFIT_ATR_MULTIPLIER = 3
MAX_DAILY_TRADES = 5
MAX_OPEN_TRADES = 3
MAX_DAILY_LOSS = 5  # Maximum daily loss percentage

# Market Sessions (UTC)
MARKET_SESSIONS = {
    'TOKYO': {'start': '00:00', 'end': '09:00', 'volatility': 1.2},
    'LONDON': {'start': '08:00', 'end': '17:00', 'volatility': 1.5},
    'NEW_YORK': {'start': '13:00', 'end': '22:00', 'volatility': 1.8},
    'SYDNEY': {'start': '22:00', 'end': '07:00', 'volatility': 1.0}
}

# Supported Pairs with their characteristics
MAJOR_PAIRS = {
    'EURUSD=X': {'pip_value': 0.0001, 'spread': 0.0002, 'volatility': 1.0},
    'GBPUSD=X': {'pip_value': 0.0001, 'spread': 0.0003, 'volatility': 1.2},
    'USDJPY=X': {'pip_value': 0.01, 'spread': 0.03, 'volatility': 1.1},
    'USDCHF=X': {'pip_value': 0.0001, 'spread': 0.0003, 'volatility': 0.9},
    'AUDUSD=X': {'pip_value': 0.0001, 'spread': 0.0003, 'volatility': 1.1},
    'USDCAD=X': {'pip_value': 0.0001, 'spread': 0.0004, 'volatility': 1.0},
    'NZDUSD=X': {'pip_value': 0.0001, 'spread': 0.0004, 'volatility': 1.1}
}

CROSS_PAIRS = {
    'EURGBP=X': {'pip_value': 0.0001, 'spread': 0.0004, 'volatility': 1.2},
    'EURJPY=X': {'pip_value': 0.01, 'spread': 0.04, 'volatility': 1.3},
    'GBPJPY=X': {'pip_value': 0.01, 'spread': 0.05, 'volatility': 1.4},
    'EURCHF=X': {'pip_value': 0.0001, 'spread': 0.0004, 'volatility': 1.1},
    'AUDJPY=X': {'pip_value': 0.01, 'spread': 0.04, 'volatility': 1.2},
    'EURAUD=X': {'pip_value': 0.0001, 'spread': 0.0005, 'volatility': 1.3},
    'GBPAUD=X': {'pip_value': 0.0001, 'spread': 0.0005, 'volatility': 1.4}
}

COMMODITIES = {
    'GC=F': {'pip_value': 0.1, 'spread': 0.5, 'volatility': 1.5},  # Gold
    'SI=F': {'pip_value': 0.01, 'spread': 0.05, 'volatility': 1.3},  # Silver
    'CL=F': {'pip_value': 0.01, 'spread': 0.05, 'volatility': 1.6},  # Crude Oil
    'BZ=F': {'pip_value': 0.01, 'spread': 0.05, 'volatility': 1.6}   # Brent Oil
}

# Correlation Pairs for Analysis
CORRELATION_PAIRS = [
    ('EURUSD=X', 'GBPUSD=X'),
    ('EURUSD=X', 'USDJPY=X'),
    ('GBPUSD=X', 'USDJPY=X'),
    ('EURUSD=X', 'AUDUSD=X'),
    ('GBPUSD=X', 'EURGBP=X'),
    ('USDJPY=X', 'AUDJPY=X'),
    ('EURUSD=X', 'USDCAD=X'),
    ('GBPUSD=X', 'GBPJPY=X'),
    ('EURUSD=X', 'EURJPY=X'),
    ('USDJPY=X', 'USDCHF=X')
]

# Technical Analysis Settings
TECHNICAL_INDICATORS = {
    'RSI': {
        'period': 14,
        'overbought': 70,
        'oversold': 30
    },
    'MACD': {
        'fast_period': 12,
        'slow_period': 26,
        'signal_period': 9
    },
    'Bollinger': {
        'period': 20,
        'std_dev': 2
    },
    'Stochastic': {
        'k_period': 14,
        'd_period': 3,
        'slowing': 3
    },
    'ATR': {
        'period': 14
    },
    'Ichimoku': {
        'tenkan_period': 9,
        'kijun_period': 26,
        'senkou_span_b_period': 52,
        'displacement': 26
    }
}

# Pattern Recognition Settings
PATTERN_SETTINGS = {
    'Double_Top_Bottom': {
        'min_distance': 20,
        'price_threshold': 0.001
    },
    'Head_Shoulders': {
        'min_distance': 30,
        'price_threshold': 0.002
    },
    'Triangle': {
        'min_points': 5,
        'max_deviation': 0.001
    },
    'Candlestick': {
        'min_body_ratio': 0.3,
        'max_shadow_ratio': 0.5
    }
}

# Notification Settings
NOTIFICATIONS = {
    'ENABLE_PRICE_ALERTS': True,
    'ENABLE_NEWS_ALERTS': True,
    'ENABLE_SESSION_ALERTS': True,
    'ENABLE_PATTERN_ALERTS': True,
    'ENABLE_SIGNAL_ALERTS': True,
    'ENABLE_ERROR_NOTIFICATIONS': True,
    'ENABLE_PERFORMANCE_ALERTS': True,
    'error_alerts': True
}

# Message Templates
MESSAGE_TEMPLATES = {
    'SIGNAL': """
🎯 <b>إشارة تداول جديدة</b> 🎯

📊 <b>معلومات الزوج</b>
━━━━━━━━━━━━━━━━━━━━━━━━
• الزوج: {symbol}
• السعر الحالي: {price:.5f}
• نوع الإشارة: {signal}
• مستوى الثقة: {confidence:.1f}%

📈 <b>التحليل الفني</b>
━━━━━━━━━━━━━━━━━━━━━━━━
• مؤشر RSI: {rsi:.2f}
• مؤشر MACD: {macd:.5f}
• مؤشر ستوكاستيك: {stoch:.2f}
• موقع السعر في بولينجر: {bb_position:.1f}%

⏰ <b>تحليل التوقيت</b>
━━━━━━━━━━━━━━━━━━━━━━━━
• الجلسة الحالية: {current_sessions}
• قوة الإشارة الزمنية: {time_strength:.1f}%
• أفضل وقت للتداول: {optimal_time}

💰 <b>توصيات التداول</b>
━━━━━━━━━━━━━━━━━━━━━━━━
• سعر الدخول: {entry_price:.5f}
• وقف الخسارة: {stop_loss:.5f}
• هدف الربح: {take_profit:.5f}
• نسبة المخاطرة/العائد: {risk_reward:.2f}

📊 <b>التحليل الأساسي</b>
━━━━━━━━━━━━━━━━━━━━━━━━
• قوة الإشارة: {fundamental_strength:.1f}%
• المشاعر السوقية: {market_sentiment}
• الأحداث القادمة: {upcoming_events}

⚠️ <b>تنبيه هام</b>
━━━━━━━━━━━━━━━━━━━━━━━━
هذه الإشارة هي توصية فقط وليست نصيحة استثمارية.
يجب عليك إجراء تحليلك الخاص قبل التداول.
    """,
    
    'ERROR': """
⚠️ <b>تنبيه خطأ</b> ⚠️
━━━━━━━━━━━━━━━━━━━━━━━━

{error_message}

🔄 <b>الإجراءات المطلوبة</b>
• يرجى المحاولة مرة أخرى
• أو التواصل مع الدعم الفني
    """,
    
    'PERFORMANCE': """
📊 <b>تقرير الأداء اليومي</b> 📊
━━━━━━━━━━━━━━━━━━━━━━━━

📈 <b>إحصائيات اليوم</b>
• عدد الإشارات: {signals_count}
• نسبة النجاح: {success_rate:.1f}%
• الربح/الخسارة: {pnl:.2f}%

🏆 <b>أفضل الأزواج</b>
{top_pairs}

⏰ <b>ملخص الجلسات</b>
{session_summary}

🔄 <b>التحديث القادم</b>
{next_update}
    """
}

# Error Messages
ERROR_MESSAGES = {
    'market_data': "عذراً، حدث خطأ أثناء جلب بيانات السوق. يرجى المحاولة مرة أخرى.",
    'analysis': "عذراً، حدث خطأ أثناء تحليل السوق. يرجى المحاولة مرة أخرى.",
    'signal': "عذراً، حدث خطأ أثناء توليد الإشارة. يرجى المحاولة مرة أخرى.",
    'notification': "عذراً، حدث خطأ أثناء إرسال الإشعار. يرجى المحاولة مرة أخرى.",
    'connection': "عذراً، حدث خطأ في الاتصال. يرجى التحقق من اتصال الإنترنت والمحاولة مرة أخرى.",
    'data_processing': "عذراً، حدث خطأ أثناء معالجة البيانات. يرجى المحاولة مرة أخرى."
}

# Logging Configuration
LOGGING = {
    'level': 'INFO',
    'file': 'forex_bot.log',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'rotation': '1 day',
    'backup_count': 7
}

# Performance Tracking
PERFORMANCE_SETTINGS = {
    'TRACK_SIGNALS': True,
    'TRACK_TRADES': True,
    'TRACK_PNL': True,
    'GENERATE_REPORTS': True,
    'REPORT_INTERVAL': '1d'
}

PERFORMANCE = PERFORMANCE_SETTINGS 