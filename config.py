import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Hyperliquid Configuration
HYPERLIQUID_API_BASE = "https://api.hyperliquid.xyz"
HYPERLIQUID_WS_URL = "wss://api.hyperliquid.xyz/ws"

# Price Alert Configuration
TARGET_PRICE = 41.0
STANDARD_DEVIATIONS = 2.0  # Number of standard deviations for alert
UPDATE_INTERVAL_MINUTES = 30  # Regular monitoring every 30 minutes

# Statistical Analysis
PRICE_HISTORY_WINDOW = 100  # Number of price points to keep for analysis
ALERT_THRESHOLD = 0.7  # Lowered threshold for more sensitive alerts (70% probability)

# Telegram Alert Settings
ENABLE_VOICE_MESSAGES = True  # Set to False to disable voice messages
ENABLE_TEXT_ALERTS = True  # Set to False to disable text alerts
ALERT_COOLDOWN_MINUTES = 5  # Reduced cooldown for urgent alerts (5 minutes)
URGENT_ALERT_COOLDOWN_MINUTES = 1  # Very short cooldown for critical alerts (1 minute)

# Critical Alert Settings
CRITICAL_PRICE_THRESHOLD = 41.5  # Alert when price gets close to $41
STRONG_DOWNTREND_THRESHOLD = 0.85  # Alert on strong downtrends (85% probability) 