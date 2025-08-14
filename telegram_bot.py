import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime
import json
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, UPDATE_INTERVAL_MINUTES, ALERT_THRESHOLD
from hyperliquid_client import HyperliquidClient
from price_analyzer import PriceAnalyzer
from telegram_alerter import TelegramAlerter

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class HypeBot:
    def __init__(self):
        self.hyperliquid_client = HyperliquidClient()
        self.price_analyzer = PriceAnalyzer()
        self.telegram_alerter = TelegramAlerter()
        self.last_alert_time = None
        self.is_running = False
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 Welcome to HypeBot! 

I'm your Hyperliquid price tracker and alert system.

Commands:
/start - Show this message
/status - Show current price and analysis
/settings - Show current settings
/help - Show help information

I'll send you updates every 30 minutes and CRITICAL alerts immediately when the price is likely to drop below $41.
        """
        await update.message.reply_text(welcome_message)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        try:
            # Get current price
            current_price = self.hyperliquid_client.get_asset_price()
            if current_price is None:
                await update.message.reply_text("❌ Unable to fetch current price. Please try again later.")
                return
            
            # Add price to analyzer
            self.price_analyzer.add_price(current_price)
            
            # Get analysis
            analysis = self.price_analyzer.get_analysis_summary()
            
            # Format status message
            status_message = self._format_status_message(analysis)
            
            await update.message.reply_text(status_message, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Error in status command: {e}")
            await update.message.reply_text("❌ Error fetching status. Please try again.")
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command"""
        alert_status = self.telegram_alerter.get_alert_status()
        
        settings_message = f"""
⚙️ <b>Bot Settings</b>

Target Price: ${self.price_analyzer.target_price}
Standard Deviations: {self.price_analyzer.std_deviations}
Update Interval: {UPDATE_INTERVAL_MINUTES} minutes
Alert Threshold: {ALERT_THRESHOLD}

🔊 <b>Voice Message Settings:</b>
• Enabled: {'✅' if alert_status['voice_enabled'] else '❌'}
• TTS Configured: {'✅' if alert_status['tts_configured'] else '❌'}

📱 <b>Text Alert Settings:</b>
• Enabled: {'✅' if alert_status['text_enabled'] else '❌'}
• Cooldown: {alert_status['cooldown_minutes']} minutes
• Can Send Alert: {'✅' if alert_status['can_send_alert'] else '❌'}

To change settings, modify the config.py file and restart the bot.
        """
        await update.message.reply_text(settings_message, parse_mode='HTML')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📚 <b>HypeBot Help</b>

<b>What I do:</b>
• Track Hyperliquid cryptocurrency prices
• Analyze price trends and volatility
• Send alerts when price is likely to drop below $41
• Provide regular updates every 30 minutes
• Send CRITICAL alerts immediately for urgent situations
• Send voice messages and text alerts through Telegram

<b>How alerts work:</b>
• Regular monitoring every 30 minutes
• CRITICAL alerts when price drops below $41.50
• Strong downtrend alerts with >85% probability
• Price within 2 standard deviations of target
• High probability (>70%) of price dropping below target

<b>Commands:</b>
/start - Welcome message
/status - Current price and analysis
/settings - Bot configuration
/testvoice - Test voice message functionality
/help - This help message

<b>Technical Details:</b>
• Uses statistical analysis for predictions
• Monitors price history for trends
• Sends alerts via Telegram voice and text messages
• CRITICAL alerts have 1-minute cooldown
• Regular alerts have 5-minute cooldown
        """
        await update.message.reply_text(help_message, parse_mode='HTML')
    
    def _format_status_message(self, analysis: dict) -> str:
        """Format analysis data into a readable message"""
        current_price = analysis['current_price']
        trend = analysis['trend']
        drop_probability = analysis['drop_probability']
        should_alert = analysis['should_alert']
        
        # Price change indicator
        if trend == "strong_uptrend":
            trend_emoji = "📈"
        elif trend == "uptrend":
            trend_emoji = "↗️"
        elif trend == "strong_downtrend":
            trend_emoji = "📉"
        elif trend == "downtrend":
            trend_emoji = "↘️"
        else:
            trend_emoji = "➡️"
        
        # Alert indicator
        alert_emoji = "🚨" if should_alert else "✅"
        
        message = f"""
{alert_emoji} <b>Hyperliquid Price Status</b>

💰 <b>Current Price:</b> ${current_price:.2f}
📊 <b>Trend:</b> {trend_emoji} {trend.replace('_', ' ').title()}
🎯 <b>Target Price:</b> ${analysis['target_price']:.2f}
📈 <b>Drop Probability:</b> {drop_probability:.1%}

📊 <b>Statistics:</b>
• Mean Price: ${analysis['mean_price']:.2f}
• Std Deviation: ${analysis['std_deviation']:.2f}
• Price Range: ${analysis['price_range']['min']:.2f} - ${analysis['price_range']['max']:.2f}

⏰ <b>Last Updated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        if should_alert:
            alert_info = analysis['alert_info']
            reason = alert_info.get('reason', 'unknown')
            message += f"\n🚨 <b>ALERT:</b> {reason.replace('_', ' ').title()}"
        
        return message
    
    async def send_alert(self, context: ContextTypes.DEFAULT_TYPE, analysis: dict):
        """Send voice and text alerts through Telegram"""
        if not TELEGRAM_CHAT_ID:
            logger.error("TELEGRAM_CHAT_ID not configured")
            return
        
        # Check if this is an urgent alert
        is_urgent = analysis.get('is_urgent', False)
        
        try:
            # Send voice alert
            voice_sent = await self.telegram_alerter.send_voice_alert(context, analysis, TELEGRAM_CHAT_ID, is_urgent)
            if voice_sent:
                logger.info(f"{'CRITICAL' if is_urgent else 'Regular'} voice alert sent successfully")
            else:
                logger.info("Voice alert skipped (cooldown or disabled)")
            
            # Send text alert
            text_sent = await self.telegram_alerter.send_text_alert(context, analysis, TELEGRAM_CHAT_ID, is_urgent)
            if text_sent:
                logger.info(f"{'CRITICAL' if is_urgent else 'Regular'} text alert sent successfully")
            else:
                logger.info("Text alert skipped (cooldown or disabled)")
                
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    async def send_regular_update(self, context: ContextTypes.DEFAULT_TYPE):
        """Send regular price update"""
        if not TELEGRAM_CHAT_ID:
            return
        
        try:
            # Get current price
            current_price = self.hyperliquid_client.get_asset_price()
            if current_price is None:
                logger.warning("Unable to fetch price for regular update")
                return
            
            # Add price to analyzer
            self.price_analyzer.add_price(current_price)
            
            # Get analysis
            analysis = self.price_analyzer.get_analysis_summary()
            
            # Check if we should send an alert
            if analysis['should_alert']:
                await self.send_alert(context, analysis)
            
            # Send regular update
            update_message = self._format_status_message(analysis)
            await context.bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=update_message,
                parse_mode='HTML'
            )
            
            logger.info(f"Regular update sent - Price: ${current_price:.2f}")
            
        except Exception as e:
            logger.error(f"Error sending regular update: {e}")
    
    async def start_monitoring(self, context: ContextTypes.DEFAULT_TYPE):
        """Start the monitoring loop with frequent updates"""
        self.is_running = True
        logger.info("Starting price monitoring with frequent updates...")
        
        while self.is_running:
            try:
                await self.send_regular_update(context)
                await asyncio.sleep(UPDATE_INTERVAL_MINUTES * 60)  # Convert minutes to seconds
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.is_running = False
        logger.info("Stopping price monitoring...")
    
    async def test_voice_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /testvoice command"""
        try:
            # Check if voice messaging is configured
            alert_status = self.telegram_alerter.get_alert_status()
            
            if not alert_status['tts_configured']:
                await update.message.reply_text(
                    "❌ Voice messaging is not configured. Please check the TTS engine setup."
                )
                return
            
            if not alert_status['voice_enabled']:
                await update.message.reply_text(
                    "❌ Voice messaging is disabled. Set ENABLE_VOICE_MESSAGES=True in config.py to enable."
                )
                return
            
            if not alert_status['can_send_alert']:
                await update.message.reply_text(
                    f"⏳ Voice messaging is in cooldown. Please wait {alert_status['cooldown_minutes']} minutes between alerts."
                )
                return
            
            # Send confirmation message
            await update.message.reply_text("🔊 Sending test voice message...")
            
            # Send the test voice message
            voice_success = await self.telegram_alerter.test_voice_message(context, update.effective_chat.id)
            
            if voice_success:
                await update.message.reply_text("✅ Test voice message sent successfully! Check your Telegram.")
            else:
                await update.message.reply_text("❌ Failed to send test voice message. Check the logs for details.")
                
        except Exception as e:
            logger.error(f"Error in test voice command: {e}")
            await update.message.reply_text("❌ Error sending test voice message. Please try again.")

async def main():
    """Main function to run the bot"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not configured")
        return
    
    # Create bot instance
    bot = HypeBot()
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("status", bot.status_command))
    application.add_handler(CommandHandler("settings", bot.settings_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("testvoice", bot.test_voice_command))
    
    # Start monitoring in background
    asyncio.create_task(bot.start_monitoring(application))
    
    # Start the bot
    logger.info("Starting HypeBot...")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main()) 