#!/usr/bin/env python3
"""
HypeBot - Alternative entry point for Render deployment
This file simply imports and runs the main application
"""

import asyncio
from app import main

if __name__ == "__main__":
    asyncio.run(main()) 