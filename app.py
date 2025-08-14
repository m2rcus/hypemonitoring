#!/usr/bin/env python3
"""
HypeBot - Hyperliquid Price Tracker and Alert System
Main application file for Render deployment
"""

import os
import sys
import logging
from telegram_bot import main as run_bot

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your Render environment")
        return False
    
    logger.info("Environment variables configured successfully")
    return True

async def main():
    """Main application entry point"""
    logger.info("Starting HypeBot application...")
    
    # Check environment configuration
    if not check_environment():
        logger.error("Environment check failed. Exiting.")
        return
    
    try:
        # Start the Telegram bot
        await run_bot()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 