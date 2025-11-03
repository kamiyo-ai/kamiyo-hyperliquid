# -*- coding: utf-8 -*-
"""
Hyperliquid Official API Aggregator
Fetches liquidation and exploit data from the official Hyperliquid API
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from .base import BaseAggregator


class HyperliquidAPIAggregator(BaseAggregator):
    """Aggregator for Hyperliquid Official API - focused on exploits in the Hyperliquid ecosystem"""

    MAINNET_URL = "https://api.hyperliquid.xyz/info"
    TESTNET_URL = "https://api.hyperliquid-testnet.xyz/info"

    def __init__(self, use_testnet: bool = False):
        super().__init__("hyperliquid_api")
        self.base_url = self.TESTNET_URL if use_testnet else self.MAINNET_URL

    def fetch_exploits(self) -> List[Dict[str, Any]]:
        """
        Fetch exploits related to Hyperliquid
        This monitors for anomalous liquidations and potential exploits
        """
        exploits = []

        try:
            # Monitor for unusual liquidation patterns that might indicate exploits
            large_liquidations = self._fetch_large_liquidations()

            for liq in large_liquidations:
                exploit_data = self._analyze_for_exploit(liq)
                if exploit_data:
                    normalized = self.normalize_exploit(exploit_data)
                    if self.validate_exploit(normalized):
                        exploits.append(normalized)

            self.logger.info(f"Detected {len(exploits)} potential exploits from Hyperliquid API")

        except Exception as e:
            self.logger.error(f"Error fetching exploits: {e}")

        return exploits

    def _fetch_large_liquidations(self) -> List[Dict[str, Any]]:
        """
        Fetch large liquidations that might indicate exploits
        Returns list of liquidation data
        """
        # Placeholder - implement actual large liquidation detection
        return []

    def _analyze_for_exploit(self, liquidation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze liquidation for signs of exploit
        Large liquidations (>$1M) or unusual patterns may indicate security issues
        """
        amount_usd = float(liquidation.get('amount_usd', 0))

        # Flag large liquidations as potential exploits
        if amount_usd > 1_000_000:
            return {
                'tx_hash': liquidation.get('liquidation_id', ''),
                'chain': 'Hyperliquid',
                'protocol': 'Hyperliquid DEX',
                'amount_usd': amount_usd,
                'timestamp': liquidation.get('timestamp', datetime.now()),
                'source_url': self.base_url,
                'category': 'large_liquidation',
                'description': f"Large liquidation detected: {liquidation.get('user', '')} - {liquidation.get('asset', '')}",
                'recovery_status': 'unknown'
            }

        return None

    def get_meta(self) -> Dict[str, Any]:
        """
        Get metadata about available assets on Hyperliquid

        Returns:
            Metadata about exchange configuration
        """
        payload = {"type": "meta"}

        response = self.make_request(
            self.base_url,
            method='POST',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )

        if not response:
            return {}

        try:
            return response.json()
        except json.JSONDecodeError:
            self.logger.error("Failed to parse meta response")
            return {}

    def get_all_mids(self) -> Dict[str, float]:
        """
        Get current mid prices for all assets

        Returns:
            Dictionary mapping asset names to mid prices
        """
        payload = {"type": "allMids"}

        response = self.make_request(
            self.base_url,
            method='POST',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )

        if not response:
            return {}

        try:
            return response.json()
        except json.JSONDecodeError:
            self.logger.error("Failed to parse all mids response")
            return {}
