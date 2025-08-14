import logging
import asyncio
import io
from datetime import datetime, timedelta
from typing import Optional
import gtts
from config import (
    ENABLE_VOICE_MESSAGES,
    ENABLE_TEXT_ALERTS,
    ALERT_COOLDOWN_MINUTES,
    URGENT_ALERT_COOLDOWN_MINUTES,
    CRITICAL_PRICE_THRESHOLD,
    STRONG_DOWNTREND_THRESHOLD
)

logger = logging.getLogger(__name__)

class TelegramAlerter:
    def __init__(self):
        self.last_alert_time = None
        self.tts_engine = None
        
        # Initialize text-to-speech engine
        try:
            self.tts_engine = gtts.gTTS
            logger.info("Text-to-speech engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
    
    def can_send_alert(self, is_urgent: bool = False) -> bool:
        """Check if enough time has passed since the last alert"""
        if not ENABLE_VOICE_MESSAGES and not ENABLE_TEXT_ALERTS:
            return False
        
        if self.last_alert_time is None:
            return True
        
        time_since_last_alert = datetime.now() - self.last_alert_time
        
        # Use shorter cooldown for urgent alerts
        cooldown_minutes = URGENT_ALERT_COOLDOWN_MINUTES if is_urgent else ALERT_COOLDOWN_MINUTES
        return time_since_last_alert >= timedelta(minutes=cooldown_minutes)
    
    async def send_voice_alert(self, context, analysis: dict, chat_id: str, is_urgent: bool = False) -> bool:
        """Send a voice message alert through Telegram"""
        if not ENABLE_VOICE_MESSAGES or not self.can_send_alert(is_urgent):
            return False
        
        try:
            # Create the message to speak
            message = self._create_voice_message(analysis, is_urgent)
            
            # Generate speech
            tts = self.tts_engine(text=message, lang='en', slow=False)
            
            # Save to bytes buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            # Send voice message
            await context.bot.send_voice(
                chat_id=chat_id,
                voice=audio_buffer,
                caption="🚨 HypeBot Price Alert Voice Message"
            )
            
            self.last_alert_time = datetime.now()
            logger.info("Voice alert sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send voice alert: {e}")
            return False
    
    def _create_voice_message(self, analysis: dict, is_urgent: bool = False) -> str:
        """Create the message to be spoken"""
        current_price = analysis['current_price']
        target_price = analysis['target_price']
        drop_probability = analysis['drop_probability']
        trend = analysis['trend'].replace('_', ' ').title()
        
        if is_urgent:
            urgency_prefix = "CRITICAL ALERT! "
            urgency_suffix = " IMMEDIATE ACTION REQUIRED!"
        else:
            urgency_prefix = "Alert! "
            urgency_suffix = " Please check your trading platform immediately."
        
        message = f"""
        {urgency_prefix}Hyperliquid price alert! 
        Current price is {current_price:.2f} dollars. 
        Target price is {target_price:.2f} dollars. 
        Drop probability is {drop_probability:.1%}. 
        Trend is {trend}. 
        {urgency_suffix}
        """
        
        return message
    
    async def send_text_alert(self, context, analysis: dict, chat_id: str, is_urgent: bool = False) -> bool:
        """Send a text alert through Telegram"""
        if not ENABLE_TEXT_ALERTS or not self.can_send_alert(is_urgent):
            return False
        
        try:
            alert_message = self._create_text_alert(analysis, is_urgent)
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=alert_message,
                parse_mode='HTML'
            )
            
            self.last_alert_time = datetime.now()
            logger.info("Text alert sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send text alert: {e}")
            return False
    
    def _create_text_alert(self, analysis: dict, is_urgent: bool = False) -> str:
        """Create the text alert message"""
        current_price = analysis['current_price']
        target_price = analysis['target_price']
        drop_probability = analysis['drop_probability']
        trend = analysis['trend'].replace('_', ' ').title()
        
        # Determine alert level
        if is_urgent:
            alert_level = "🚨🚨🚨 <b>CRITICAL ALERT!</b> 🚨🚨🚨"
            urgency_text = "⚠️ <b>CRITICAL:</b> IMMEDIATE ACTION REQUIRED!"
        else:
            alert_level = "🚨 <b>HYPEBOT PRICE ALERT!</b> 🚨"
            urgency_text = "⚠️ <b>URGENT:</b> Check your trading platform NOW!"
        
        alert_message = f"""
{alert_level}

💰 <b>Current Price:</b> ${current_price:.2f}
🎯 <b>Target Price:</b> ${target_price:.2f}
📊 <b>Drop Probability:</b> {drop_probability:.1%}
📈 <b>Trend:</b> {trend}

{urgency_text}

⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return alert_message
    
    async def send_status_update(self, context, analysis: dict) -> bool:
        """Send a status update through Telegram"""
        try:
            status_message = self._create_status_message(analysis)
            
            await context.bot.send_message(
                chat_id=context.bot.id,  # This will be overridden by the calling function
                text=status_message,
                parse_mode='HTML'
            )
            
            logger.info("Status update sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send status update: {e}")
            return False
    
    def _create_status_message(self, analysis: dict) -> str:
        """Create the status update message"""
        current_price = analysis['current_price']
        trend = analysis['trend'].replace('_', ' ').title()
        drop_probability = analysis['drop_probability']
        
        # Trend emoji
        if trend == "Strong Uptrend":
            trend_emoji = "📈"
        elif trend == "Uptrend":
            trend_emoji = "↗️"
        elif trend == "Strong Downtrend":
            trend_emoji = "📉"
        elif trend == "Downtrend":
            trend_emoji = "↘️"
        else:
            trend_emoji = "➡️"
        
        status_message = f"""
📊 <b>HypeBot Status Update</b>

💰 <b>Price:</b> ${current_price:.2f}
📈 <b>Trend:</b> {trend_emoji} {trend}
🎯 <b>Drop Probability:</b> {drop_probability:.1%}

⏰ <b>Updated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return status_message
    
    async def test_voice_message(self, context, chat_id: str) -> bool:
        """Send a test voice message"""
        try:
            test_message = "This is a test voice message from HypeBot. Your voice alert system is working correctly."
            
            tts = self.tts_engine(text=test_message, lang='en', slow=False)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            await context.bot.send_voice(
                chat_id=chat_id,
                voice=audio_buffer,
                caption="🔊 HypeBot Voice Test"
            )
            
            logger.info("Test voice message sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send test voice message: {e}")
            return False
    
    def get_alert_status(self) -> dict:
        """Get the status of alert configuration"""
        return {
            'voice_enabled': ENABLE_VOICE_MESSAGES,
            'text_enabled': ENABLE_TEXT_ALERTS,
            'last_alert_time': self.last_alert_time.isoformat() if self.last_alert_time else None,
            'can_send_alert': self.can_send_alert(),
            'cooldown_minutes': ALERT_COOLDOWN_MINUTES,
            'tts_configured': self.tts_engine is not None
        } 