# HypeBot - Hyperliquid Price Tracker & Alert System

A Telegram bot that tracks Hyperliquid cryptocurrency prices and sends alerts when the price is likely to drop below a specified threshold (default: $41).

## Features

- 🤖 **Real-time Price Tracking**: Monitors Hyperliquid cryptocurrency prices
- 📊 **Statistical Analysis**: Uses standard deviations and probability analysis
- 🚨 **Smart Alerts**: Sends alerts when price is likely to drop below target
- 🔊 **Voice Message Alerts**: Sends voice messages through Telegram for urgent alerts
- 📱 **Text Alerts**: Sends text alerts through Telegram
- ⏰ **Regular Updates**: Sends price updates every 30 minutes
- 🚨 **CRITICAL Alerts**: Immediate alerts for urgent situations
- 📈 **Trend Analysis**: Provides price trend information
- 🔧 **Configurable**: Easy to customize target price and alert thresholds

## How It Works

The bot uses statistical analysis to predict potential price drops:

1. **Current Price Check**: Alerts if price is already below $41
2. **Standard Deviation Analysis**: Alerts if price is within 2 standard deviations of target
3. **Probability Prediction**: Alerts if there's >80% probability of dropping below target
4. **Regular Monitoring**: Sends updates every 30 minutes
5. **CRITICAL Alerts**: Immediate alerts when price drops below $41.50 or shows strong downtrend

## Setup Instructions

### 1. Create a Telegram Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow the instructions
3. Save your bot token (you'll need this later)
4. Start a chat with your bot and send `/start`

### 2. Get Your Chat ID

1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. It will reply with your chat ID
3. Save this chat ID (you'll need this later)



### 3. Deploy on Render

#### Option A: Using Render Dashboard

1. Fork or clone this repository to your GitHub account
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" → "Web Service"
4. Connect your GitHub repository
5. Configure the service:
   - **Name**: `hypebot` (or any name you prefer)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
6. Add environment variables:
   - `TELEGRAM_BOT_TOKEN`: Your bot token from step 1
   - `TELEGRAM_CHAT_ID`: Your chat ID from step 2
7. Click "Create Web Service"

#### Option B: Using render.yaml (Recommended)

1. Fork or clone this repository to your GitHub account
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" → "Blueprint"
4. Connect your GitHub repository
5. Render will automatically detect the `render.yaml` file
6. Add your environment variables when prompted
7. Click "Apply"

### 4. Local Development (Optional)

If you want to run the bot locally:

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd hypebot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   ```

4. Run the bot:
   ```bash
   python app.py
   ```

## Configuration

You can customize the bot behavior by modifying `config.py`:

```python
# Price Alert Configuration
TARGET_PRICE = 41.0  # Target price to monitor
STANDARD_DEVIATIONS = 2.0  # Number of standard deviations for alert
UPDATE_INTERVAL_MINUTES = 30  # Regular monitoring every 30 minutes

# Statistical Analysis
ALERT_THRESHOLD = 0.7  # Confidence threshold for price drop prediction (70%)

# Telegram Alert Settings
ENABLE_VOICE_MESSAGES = True  # Set to False to disable voice messages
ENABLE_TEXT_ALERTS = True  # Set to False to disable text alerts
ALERT_COOLDOWN_MINUTES = 5  # Regular alert cooldown (5 minutes)
URGENT_ALERT_COOLDOWN_MINUTES = 1  # Critical alert cooldown (1 minute)

# Critical Alert Settings
CRITICAL_PRICE_THRESHOLD = 41.5  # Alert when price gets close to $41
STRONG_DOWNTREND_THRESHOLD = 0.85  # Alert on strong downtrends (85% probability)
```

## Bot Commands

Once the bot is running, you can use these commands:

- `/start` - Welcome message and bot introduction
- `/status` - Get current price and analysis
- `/settings` - View current bot configuration
- `/testvoice` - Test voice message functionality
- `/help` - Show help information

## Example Messages

### Regular Update
```
✅ Hyperliquid Price Status

💰 Current Price: $42.50
📊 Trend: ↗️ Uptrend
🎯 Target Price: $41.00
📈 Drop Probability: 15.2%

📊 Statistics:
• Mean Price: $43.20
• Std Deviation: $2.10
• Price Range: $40.50 - $45.80

⏰ Last Updated: 2024-01-15 14:30:00
```

### Alert Message
```
🚨 PRICE ALERT!

Hyperliquid price is showing signs of dropping below $41.00

💰 Current Price: $41.20
📊 Drop Probability: 85.3%
📈 Trend: ↘️ Downtrend

⚠️ Reason: High Drop Probability

⏰ Time: 2024-01-15 14:30:00
```

## Technical Details

- **Framework**: Python with python-telegram-bot
- **Price Data**: Hyperliquid API
- **Analysis**: Statistical analysis using numpy and pandas
- **Voice Messages**: gTTS (Google Text-to-Speech) for voice alerts
- **Deployment**: Render (free tier compatible)
- **Monitoring**: Continuous price tracking with configurable intervals

## Troubleshooting

### Common Issues

1. **Bot not responding**: Check if the bot token is correct
2. **No alerts received**: Verify your chat ID is correct
3. **Voice messages not working**: Check TTS engine configuration
4. **Price data errors**: Hyperliquid API might be temporarily unavailable
5. **Deployment fails**: Ensure all environment variables are set in Render

### Logs

Check the Render logs for detailed error information:
1. Go to your service in Render Dashboard
2. Click on "Logs" tab
3. Look for any error messages

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License. 