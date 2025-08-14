import requests
import json
import time
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class HyperliquidClient:
    def __init__(self):
        self.base_url = "https://api.hyperliquid.xyz"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'HypeBot/1.0'
        })
    
    def get_market_info(self) -> Optional[Dict]:
        """Get market information for all assets"""
        try:
            response = self.session.post(
                f"{self.base_url}/info",
                json={"type": "meta"}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching market info: {e}")
            return None
    
    def get_asset_price(self, asset_name: str = "SOL") -> Optional[float]:
        """Get current price for a specific asset (default: SOL)"""
        try:
            # Get meta info first
            meta_response = self.session.post(
                f"{self.base_url}/info",
                json={"type": "meta"}
            )
            meta_response.raise_for_status()
            meta_data = meta_response.json()
            
            # Find the asset
            asset_info = None
            for asset in meta_data.get('universe', []):
                if asset.get('name') == asset_name:
                    asset_info = asset
                    break
            
            if not asset_info:
                logger.error(f"Asset {asset_name} not found")
                return None
            
            # Get current price
            price_response = self.session.post(
                f"{self.base_url}/info",
                json={"type": "l2Book", "coin": asset_name}
            )
            price_response.raise_for_status()
            price_data = price_response.json()
            
            # Extract mid price from order book
            if price_data and 'levels' in price_data:
                levels = price_data['levels']
                if levels and len(levels) > 0:
                    best_bid = float(levels[0][0]) if levels[0] else 0
                    best_ask = float(levels[0][1]) if levels[0] else 0
                    if best_bid > 0 and best_ask > 0:
                        return (best_bid + best_ask) / 2
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching price for {asset_name}: {e}")
            return None
    
    def get_price_history(self, asset_name: str = "SOL", limit: int = 100) -> List[float]:
        """Get recent price history for an asset"""
        try:
            # For Hyperliquid, we'll simulate price history by making multiple requests
            # In a real implementation, you might want to use their websocket API
            prices = []
            for _ in range(min(limit, 10)):  # Limit to avoid rate limiting
                price = self.get_asset_price(asset_name)
                if price:
                    prices.append(price)
                time.sleep(0.1)  # Small delay between requests
            
            return prices
        except Exception as e:
            logger.error(f"Error fetching price history: {e}")
            return [] 