import os
import logging
from datetime import datetime
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
import pandas as pd
import numpy as np
import ta
import yfinance as yf
import schedule
import time
from threading import Thread
from advanced_analysis import AdvancedForexAnalysis
import uuid
import asyncio
from config import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, DEFAULT_TIMEFRAME,
    MAJOR_PAIRS, CROSS_PAIRS, COMMODITIES, MARKET_SESSIONS,
    LOGGING, NOTIFICATIONS, MESSAGE_TEMPLATES, ERROR_MESSAGES,
    PERFORMANCE, NOTIFICATION_INTERVAL, MIN_SIGNAL_CONFIDENCE
)

# Configure logging
logging.basicConfig(
    level=LOGGING['level'],
    format=LOGGING['format'],
    filename=LOGGING['file']
)
logger = logging.getLogger(__name__)

class ForexBot:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.analysis_engine = AdvancedForexAnalysis()
        self.major_pairs = MAJOR_PAIRS
        self.cross_pairs = CROSS_PAIRS
        self.commodities = COMMODITIES
        self.supported_pairs = list(self.major_pairs.keys()) + list(self.cross_pairs.keys()) + list(self.commodities.keys())
        self.performance_tracker = {
            'signals': [],
            'trades': [],
            'pnl': 0.0
        }
        self.last_analysis_time = {}
        self.error_count = 0
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        self.session = None
        self.app = None
        self.bot = None
        self.channel_id = TELEGRAM_CHANNEL_ID
        self.token = TELEGRAM_BOT_TOKEN
        self.error_notifications = NOTIFICATIONS.get('ENABLE_ERROR_NOTIFICATIONS', True)
        self.signal_message_template = MESSAGE_TEMPLATES.get('SIGNAL', '')
        self.error_message_template = MESSAGE_TEMPLATES.get('ERROR', '')
        self.performance_message_template = MESSAGE_TEMPLATES.get('PERFORMANCE', '')
        self.error_messages = ERROR_MESSAGES
        self.logging_config = LOGGING
        self.performance_settings = PERFORMANCE
        self.initialize_telegram()
        self.initialize_session()
        self.send_welcome_message()

    def initialize_telegram(self):
        """Initialize telegram bot and application."""
        try:
            self.app = Application.builder().token(self.token).build()
            self.bot = self.app.bot
            self.logger.info("Telegram bot initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing telegram bot: {e}")
            raise

    def initialize_session(self):
        # Initialize market sessions
        self.market_sessions = MARKET_SESSIONS
        self.session = self.market_sessions.get(self.session, {})

    def send_welcome_message(self):
        # Send welcome message
        self.welcome_message = f"""
        مرحباً بك في بوت تحليل الفوركس المتقدم! 🤖
        
        📊 يمكنني تحليل:
        - أزواج العملات الرئيسية
        - أزواج العملات المتقاطعة
        - السلع (الذهب، الفضة، النفط)
        
        📈 للحصول على تحليل، أرسل رمز الزوج (مثال: EURUSD)
        
        ⏰ سأقوم بإرسال إشارات التداول تلقائياً كل {NOTIFICATION_INTERVAL} دقيقة
        
        🔍 الأزواج المدعومة:
        {", ".join([f"- {pair}" for pair in self.supported_pairs])}
        """
        self.welcome_message = self.welcome_message.format(
            supported_pairs=", ".join([f"- {pair}" for pair in self.supported_pairs])
        )

    def _init_scheduled_tasks(self):
        """Initialize scheduled analysis tasks."""
        # Schedule market analysis based on config
        schedule.every(int(NOTIFICATION_INTERVAL[:-1])).hours.do(self._scheduled_market_analysis)
        
        # Start scheduler in a separate thread
        Thread(target=self._run_scheduler, daemon=True).start()

    def _run_scheduler(self):
        """Run the scheduler in a loop."""
        while True:
            schedule.run_pending()
            time.sleep(60)

    async def _scheduled_market_analysis(self):
        """Perform scheduled market analysis and send to channel."""
        try:
            # Get current market session
            current_session = self._get_current_session()
            
            # Analyze major pairs
            for pair in self.major_pairs:
                signal = await self._analyze_pair(pair)
                if signal and signal['signal'] != 'NEUTRAL':
                    await self._send_signal_to_channel(signal)
            
            # Analyze commodities
            for commodity in self.commodities:
                signal = await self._analyze_pair(commodity)
                if signal and signal['signal'] != 'NEUTRAL':
                    await self._send_signal_to_channel(signal)
                    
        except Exception as e:
            self.logger.error(f"Error in scheduled analysis: {e}")
            if self.error_notifications:
                await self._send_error_notification("analysis")

    async def _send_signal_to_channel(self, signal):
        """Send trading signal to the channel."""
        try:
            message = self._format_signal_message(signal)
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode='HTML'
            )
        except Exception as e:
            self.logger.error(f"Error sending signal to channel: {e}")
            if self.error_notifications:
                await self._send_error_notification("notification")

    def _format_signal_message(self, signal):
        """Format trading signal message for channel."""
        return self.signal_message_template.format(
            symbol=signal['symbol'],
            signal='🟢 شراء' if signal['signal'] == 'BUY' else '🔴 بيع',
            confidence=signal['confidence']*100,
            price=signal['price'],
            entry_price=signal['entry_price'],
            stop_loss=signal['stop_loss'],
            take_profit=signal['take_profit'],
            risk_reward_ratio=signal['risk_reward_ratio'],
            time_analysis=signal['time_analysis'],
            fundamental_analysis=signal['fundamental_analysis'],
            technical_analysis=signal['technical_analysis']
        )

    async def _analyze_pair(self, pair):
        """Analyze a currency pair and generate signal."""
        try:
            # Get market data and perform analysis
            data = self.analysis_engine.get_market_data(pair, period='1d', interval=DEFAULT_TIMEFRAME)
            data = self.analysis_engine.calculate_advanced_indicators(data)
            data = self.analysis_engine.analyze_market_structure(data)
            signal = self.analysis_engine.generate_trading_signal(data, pair)
            
            if signal['signal'] != 'NEUTRAL' and signal['confidence'] >= MIN_SIGNAL_CONFIDENCE:
                signal['symbol'] = pair
                signal['technical'] = {
                    'rsi': data['RSI'].iloc[-1],
                    'macd': data['MACD'].iloc[-1],
                    'stoch': data['Stoch_K'].iloc[-1]
                }
                return signal
                
            return None
            
        except Exception as e:
            self.logger.error(f"Error analyzing pair {pair}: {e}")
            if self.error_notifications:
                await self._send_error_notification("market_data")
            return None

    def _get_current_session(self):
        """Get current market session."""
        now = datetime.now(pytz.UTC)
        current_hour = now.hour
        
        for session, times in self.market_sessions.items():
            start_hour = int(times['start'].split(':')[0])
            end_hour = int(times['end'].split(':')[0])
            
            if start_hour <= current_hour < end_hour:
                return session
                
        return None

    async def _send_error_notification(self, error_type):
        """Send error notification to channel."""
        try:
            message = self.error_messages.get(error_type, "حدث خطأ غير متوقع.")
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=f"⚠️ {message}"
            )
        except Exception as e:
            self.logger.error(f"Error sending error notification: {e}")
            if self.error_notifications:
                await self._send_error_notification("notification")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        await update.message.reply_text(self.welcome_message)

    async def analyze_market(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Analyze the current market conditions with advanced analysis."""
        try:
            symbol = context.args[0].upper() if context.args else 'EURUSD=X'
            
            # Handle special cases for commodities
            if symbol == 'GOLD':
                symbol = 'GC=F'
            elif symbol == 'SILVER':
                symbol = 'SI=F'
            elif symbol == 'OIL':
                symbol = 'CL=F'
            elif symbol == 'BRENT':
                symbol = 'BZ=F'
            else:
                # Add =X suffix for forex pairs if not present
                if not symbol.endswith('=X') and symbol not in ['GC=F', 'SI=F', 'CL=F', 'BZ=F']:
                    symbol = f"{symbol}=X"
            
            if symbol not in self.supported_pairs:
                await update.message.reply_text(
                    "عذراً، هذا الزوج غير مدعوم. الأزواج المدعومة هي:\n\n"
                    "🏦 الأزواج الرئيسية:\n" + 
                    ", ".join(self.major_pairs) + "\n\n" +
                    "🔄 الأزواج المتقاطعة:\n" + 
                    ", ".join(self.cross_pairs) + "\n\n" +
                    "💎 السلع:\n" + 
                    ", ".join(self.commodities)
                )
                return

            # Get market data and perform analysis
            data = self.analysis_engine.get_market_data(symbol, period='1d', interval=DEFAULT_TIMEFRAME)
            data = self.analysis_engine.calculate_advanced_indicators(data)
            data = self.analysis_engine.analyze_market_structure(data)
            signal = self.analysis_engine.generate_trading_signal(data, symbol)
            
            # Get analysis information
            time_analysis = signal['time_analysis']
            fundamental_analysis = signal['fundamental_analysis']
            
            # Create analysis message
            analysis = f"""
            📊 تحليل متقدم لـ {symbol}
            
            السعر الحالي: {signal['price']:.5f}
            الإشارة: {'🟢 شراء' if signal['signal'] == 'BUY' else '🔴 بيع' if signal['signal'] == 'SELL' else '⚪ محايد'}
            مستوى الثقة: {signal['confidence']*100:.1f}%
            
            📈 المؤشرات الفنية:
            RSI: {data['RSI'].iloc[-1]:.2f}
            MACD: {data['MACD'].iloc[-1]:.5f}
            مؤشر ستوكاستيك: {data['Stoch_K'].iloc[-1]:.2f}
            
            📊 مستويات بولينجر:
            العلوي: {data['BB_Upper'].iloc[-1]:.5f}
            المتوسط: {data['BB_Middle'].iloc[-1]:.5f}
            السفلي: {data['BB_Lower'].iloc[-1]:.5f}
            
            ⏰ تحليل التوقيت:
            قوة الإشارة الزمنية: {time_analysis['signal_strength']*100:.1f}%
            التوصية الزمنية: {time_analysis['recommendation']}
            الجلسات النشطة: {', '.join(time_analysis['current_sessions'])}
            
            أفضل أوقات التداول:
            الساعات: {', '.join(f"{hour}:00" for hour, _ in time_analysis['optimal_times']['best_hours'])}
            الأيام: {', '.join(day for day, _ in time_analysis['optimal_times']['best_days'])}
            الجلسات: {', '.join(session for session, _ in time_analysis['optimal_times']['best_sessions'])}
            """
            
            if fundamental_analysis:
                analysis += f"""
                
                📰 التحليل الأساسي:
                قوة الإشارة الأساسية: {fundamental_analysis['score']*100:.1f}%
                التوصية الأساسية: {fundamental_analysis['recommendation']}
                
                📅 الأحداث الاقتصادية القادمة:
                """
                
                for event in fundamental_analysis['details']['calendar_events']:
                    analysis += f"""
                    - {event['event']} ({event['currency']})
                      الأهمية: {event['importance']}
                      التوقيت: {event['time'].strftime('%Y-%m-%d %H:%M')}
                      التوقعات: {event['forecast']}
                      السابق: {event['previous']}
                    """
                
                analysis += f"""
                
                📊 تحليل المشاعر:
                المشاعر الفنية: {fundamental_analysis['details']['market_sentiment']['technical']*100:.1f}%
                المشاعر الأساسية: {fundamental_analysis['details']['market_sentiment']['fundamental']*100:.1f}%
                مشاعر الأخبار: {fundamental_analysis['details']['market_sentiment']['news']*100:.1f}%
                المشاعر العامة: {fundamental_analysis['details']['market_sentiment']['overall']*100:.1f}%
                
                🔄 الارتباطات:
                """
                
                for pair, corr in fundamental_analysis['details']['correlations'].items():
                    analysis += f"{pair}: {corr:.2f}\n"
            
            if signal['signal'] != 'NEUTRAL':
                analysis += f"""
                
                📈 توصية التداول:
                سعر الدخول: {signal['entry_price']:.5f}
                وقف الخسارة: {signal['stop_loss']:.5f}
                هدف الربح: {signal['take_profit']:.5f}
                نسبة المخاطرة/العائد: {signal['risk_reward_ratio']:.2f}
                """
                
                # Create inline keyboard for trade execution
                keyboard = [
                    [
                        InlineKeyboardButton("✅ تنفيذ الصفقة", callback_data=f"execute_{symbol}"),
                        InlineKeyboardButton("❌ تجاهل", callback_data="ignore")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(analysis, reply_markup=reply_markup)
            else:
                await update.message.reply_text(analysis)
            
        except Exception as e:
            self.logger.error(f"Error in analyze_market: {e}")
            await update.message.reply_text(self.error_messages['analysis'])

    async def handle_trade_execution(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle trade execution button press."""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("execute_"):
            symbol = query.data.split("_")[1]
            trade_id = str(uuid.uuid4())
            
            # Get latest signal
            data = self.analysis_engine.get_market_data(symbol)
            data = self.analysis_engine.calculate_advanced_indicators(data)
            signal = self.analysis_engine.generate_trading_signal(data, symbol)
            
            # Track the trade
            self.analysis_engine.track_trade(
                trade_id=trade_id,
                symbol=symbol,
                entry_price=signal['entry_price'],
                stop_loss=signal['stop_loss'],
                take_profit=signal['take_profit'],
                signal_type=signal['signal']
            )
            
            self.active_trades = {
                trade_id: {
                    'chat_id': query.message.chat_id,
                    'message_id': query.message.message_id
                }
            }
            
            await query.edit_message_text(
                text=f"{query.message.text}\n\n✅ تم تنفيذ الصفقة بنجاح!\nسيتم إرسال تحديثات حالة الصفقة تلقائياً."
            )
            
            # Start monitoring the trade
            self.start_trade_monitoring(trade_id, symbol)

    def start_trade_monitoring(self, trade_id, symbol):
        """Start monitoring a trade for updates."""
        def monitor_trade():
            while True:
                try:
                    data = self.analysis_engine.get_market_data(symbol)
                    current_price = data['Close'].iloc[-1]
                    
                    trade_update = self.analysis_engine.update_trade_status(trade_id, current_price)
                    if trade_update and trade_update['status'] != 'OPEN':
                        report = self.analysis_engine.generate_trade_report(trade_update)
                        if report:
                            # Send trade report to the user
                            context = self.app.context
                            context.bot.send_message(
                                chat_id=self.active_trades[trade_id]['chat_id'],
                                text=report
                            )
                            del self.active_trades[trade_id]
                            break
                    
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    self.logger.error(f"Error in trade monitoring: {e}")
                    break

        Thread(target=monitor_trade).start()

    async def show_active_trades(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show all active trades."""
        if not self.active_trades:
            await update.message.reply_text("لا توجد صفقات نشطة حالياً.")
            return

        message = "📊 الصفقات النشطة:\n\n"
        for trade_id, trade_info in self.active_trades.items():
            trade = self.analysis_engine.trade_history[trade_id]
            message += f"""
            زوج العملة: {trade['symbol']}
            نوع الصفقة: {'شراء' if trade['signal_type'] == 'BUY' else 'بيع'}
            سعر الدخول: {trade['entry_price']:.5f}
            وقف الخسارة: {trade['stop_loss']:.5f}
            هدف الربح: {trade['take_profit']:.5f}
            وقت الدخول: {trade['entry_time'].strftime('%Y-%m-%d %H:%M:%S')}
            ----------------------
            """
        
        await update.message.reply_text(message)

    async def show_trade_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show trade history."""
        closed_trades = [trade for trade in self.analysis_engine.trade_history.values() 
                        if trade['status'] != 'OPEN']
        
        if not closed_trades:
            await update.message.reply_text("لا يوجد سجل للصفقات السابقة.")
            return

        message = "📜 سجل الصفقات السابقة:\n\n"
        for trade in closed_trades:
            message += f"""
            زوج العملة: {trade['symbol']}
            نوع الصفقة: {'شراء' if trade['signal_type'] == 'BUY' else 'بيع'}
            النتيجة: {'✅ ربح' if trade['profit_loss'] > 0 else '❌ خسارة'}
            نسبة الربح/الخسارة: {trade['profit_loss']*100:.2f}%
            سبب الإغلاق: {'🎯 تحقيق الهدف' if trade['status'] == 'TAKE_PROFIT' else '🛑 وقف الخسارة'}
            ----------------------
            """
        
        await update.message.reply_text(message)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /help is issued."""
        help_text = """
        كيفية استخدام البوت:
        
        1. /analyze [رمز العملة] - تحليل السوق الحالي
        2. /signals - عرض إشارات التداول الحالية
        3. /trades - عرض الصفقات النشطة
        4. /history - سجل الصفقات السابقة
        5. /settings - تغيير إعدادات البوت
        6. /help - عرض هذه الرسالة
        
        يمكنك إرسال رمز العملة مباشرة للحصول على تحليل فوري.
        مثال: EURUSD
        """
        await update.message.reply_text(help_text)

async def run_scheduled_tasks():
    """Run scheduled tasks in the background."""
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

def main():
    """Start the bot."""
    try:
        # Create application
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Create bot instance
        bot = ForexBot()
        bot.app = application
        
        # Add command handlers
        application.add_handler(CommandHandler("start", bot.start))
        application.add_handler(CommandHandler("analyze", bot.analyze_market))
        application.add_handler(CommandHandler("trades", bot.show_active_trades))
        application.add_handler(CommandHandler("history", bot.show_trade_history))
        application.add_handler(CommandHandler("help", bot.help_command))
        application.add_handler(CallbackQueryHandler(bot.handle_trade_execution))
        
        # Schedule market analysis
        for pair in bot.supported_pairs:
            schedule.every(int(NOTIFICATION_INTERVAL[:-1])).hours.do(
                lambda p=pair: asyncio.create_task(bot._scheduled_market_analysis())
            )
        
        # Start the bot
        application.run_polling()
        
        # Run scheduled tasks in the background
        asyncio.run(run_scheduled_tasks())
            
    except Exception as e:
        error_message = ERROR_MESSAGES['notification'].format(error=str(e))
        logger.error(error_message)
        
        if NOTIFICATIONS['error_alerts']:
            # Create a new application instance for error notification
            error_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
            asyncio.run(error_app.bot.send_message(
                chat_id=TELEGRAM_CHANNEL_ID,
                text=error_message
            ))

if __name__ == '__main__':
    main() 