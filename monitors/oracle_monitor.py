# -*- coding: utf-8 -*-
"""
Oracle Deviation Monitor
Detects price manipulation by comparing Hyperliquid oracle vs external sources
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
from collections import defaultdict, deque
import hashlib

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from models.security import (
    OracleDeviation,
    SecurityEvent,
    ThreatSeverity,
    ThreatType
)
from aggregators.base import BaseAggregator

logger = logging.getLogger(__name__)


class OracleMonitor(BaseAggregator):
    """
    Monitors oracle price deviations to detect:
    - Oracle manipulation attacks
    - Price feed anomalies
    - Flash crash attempts
    - Cross-exchange arbitrage exploitation
    """

    HYPERLIQUID_API = "https://api.hyperliquid.xyz/info"
    BINANCE_API = "https://api.binance.com/api/v3/ticker/price"
    COINBASE_API = "https://api.coinbase.com/v2/prices"

    # Detection thresholds
    DEVIATION_WARNING = 0.3       # 0.3% deviation = warning
    DEVIATION_DANGER = 0.5        # 0.5% deviation = dangerous
    DEVIATION_CRITICAL = 1.0      # 1.0% deviation = critical
    SUSTAINED_DURATION_SEC = 30   # Deviation must last 30+ seconds to be suspicious

    # Asset mappings (Hyperliquid symbol -> External symbol)
    ASSET_MAPPINGS = {
        'BTC': {'binance': 'BTCUSDT', 'coinbase': 'BTC-USD'},
        'ETH': {'binance': 'ETHUSDT', 'coinbase': 'ETH-USD'},
        'SOL': {'binance': 'SOLUSDT', 'coinbase': 'SOL-USD'},
        'MATIC': {'binance': 'MATICUSDT', 'coinbase': 'MATIC-USD'},
        'ARB': {'binance': 'ARBUSDT', 'coinbase': 'ARB-USD'},
        'OP': {'binance': 'OPUSDT', 'coinbase': 'OP-USD'},
        'AVAX': {'binance': 'AVAXUSDT', 'coinbase': 'AVAX-USD'},
    }

    def __init__(self):
        super().__init__("oracle_monitor")
        # Track recent deviations per asset
        self.deviation_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.active_deviations: Dict[str, OracleDeviation] = {}

    async def fetch_exploits(self) -> List[Dict[str, Any]]:
        """
        Detect oracle manipulation exploits

        Returns:
            List of detected exploits
        """
        exploits = []

        try:
            # Get prices from all sources
            hyperliquid_prices = await self._fetch_hyperliquid_prices()
            binance_prices = await self._fetch_binance_prices()
            coinbase_prices = await self._fetch_coinbase_prices()

            if not hyperliquid_prices:
                self.logger.warning("Could not fetch Hyperliquid prices")
                return exploits

            # Compare prices for each asset
            for asset in hyperliquid_prices.keys():
                deviation = self._analyze_asset_deviation(
                    asset,
                    hyperliquid_prices.get(asset),
                    binance_prices.get(asset),
                    coinbase_prices.get(asset)
                )

                if deviation:
                    # Track deviation
                    self.deviation_history[asset].append(deviation)

                    # Check if sustained and dangerous
                    if deviation.is_dangerous:
                        # Update or create active deviation
                        if asset in self.active_deviations:
                            self.active_deviations[asset] = deviation
                        else:
                            self.active_deviations[asset] = deviation

                        # Convert to exploit if critical
                        if deviation.risk_score > 80:
                            exploit = self._deviation_to_exploit(deviation)
                            exploits.append(exploit)
                    else:
                        # Deviation resolved
                        if asset in self.active_deviations:
                            del self.active_deviations[asset]

            self.logger.info(
                f"Oracle Monitor: Checked {len(hyperliquid_prices)} assets, "
                f"{len(self.active_deviations)} active deviations, "
                f"{len(exploits)} exploits"
            )

        except Exception as e:
            self.logger.error(f"Error monitoring oracle: {e}", exc_info=True)

        return exploits

    async def _fetch_hyperliquid_prices(self) -> Dict[str, float]:
        """
        Fetch current prices from Hyperliquid

        Returns:
            Dictionary of asset -> price
        """
        payload = {"type": "allMids"}

        response = await self.make_request(
            self.HYPERLIQUID_API,
            method='POST',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )

        if not response:
            return {}

        try:
            data = response.json()
            # Convert to standard format
            prices = {}
            for asset, price_str in data.items():
                # Clean asset name (remove -USD, -PERP suffixes)
                clean_asset = asset.split('-')[0]
                try:
                    prices[clean_asset] = float(price_str)
                except (ValueError, TypeError):
                    continue

            return prices

        except Exception as e:
            self.logger.error(f"Error parsing Hyperliquid prices: {e}")
            return {}

    async def _fetch_binance_prices(self) -> Dict[str, float]:
        """
        Fetch prices from Binance

        Returns:
            Dictionary of asset -> price
        """
        try:
            response = await self.make_request(self.BINANCE_API)
            if not response:
                return {}

            data = response.json()
            prices = {}

            for item in data:
                symbol = item.get('symbol', '')
                price_str = item.get('price', '0')

                # Map back to our asset names
                for asset, mappings in self.ASSET_MAPPINGS.items():
                    if mappings.get('binance') == symbol:
                        try:
                            prices[asset] = float(price_str)
                        except (ValueError, TypeError):
                            continue
                        break

            return prices

        except Exception as e:
            self.logger.error(f"Error fetching Binance prices: {e}")
            return {}

    async def _fetch_coinbase_prices(self) -> Dict[str, float]:
        """
        Fetch prices from Coinbase

        Returns:
            Dictionary of asset -> price
        """
        prices = {}

        for asset, mappings in self.ASSET_MAPPINGS.items():
            coinbase_symbol = mappings.get('coinbase')
            if not coinbase_symbol:
                continue

            try:
                url = f"{self.COINBASE_API}/{coinbase_symbol}/spot"
                response = await self.make_request(url)

                if response:
                    data = response.json()
                    price_str = data.get('data', {}).get('amount', '0')
                    try:
                        prices[asset] = float(price_str)
                    except (ValueError, TypeError):
                        continue

            except Exception as e:
                self.logger.debug(f"Error fetching Coinbase price for {asset}: {e}")
                continue

        return prices

    def _analyze_asset_deviation(
        self,
        asset: str,
        hyperliquid_price: Optional[float],
        binance_price: Optional[float],
        coinbase_price: Optional[float]
    ) -> Optional[OracleDeviation]:
        """
        Analyze price deviation for a single asset

        Args:
            asset: Asset symbol
            hyperliquid_price: Price from Hyperliquid
            binance_price: Price from Binance (optional)
            coinbase_price: Price from Coinbase (optional)

        Returns:
            OracleDeviation object if deviation detected, else None
        """
        if not hyperliquid_price:
            return None

        # Need at least one external source
        if not binance_price and not coinbase_price:
            return None

        # Calculate deviations
        deviations = []

        if binance_price and binance_price > 0:
            dev_pct = abs((hyperliquid_price - binance_price) / binance_price * 100)
            deviations.append(dev_pct)

        if coinbase_price and coinbase_price > 0:
            dev_pct = abs((hyperliquid_price - coinbase_price) / coinbase_price * 100)
            deviations.append(dev_pct)

        # Use maximum deviation
        max_deviation = max(deviations) if deviations else 0.0

        # Check if deviation is significant
        if max_deviation < self.DEVIATION_WARNING:
            return None

        # Check if sustained
        duration_sec = 0.0
        if asset in self.active_deviations:
            prev_deviation = self.active_deviations[asset]
            duration_sec = (datetime.now(timezone.utc) - prev_deviation.timestamp).total_seconds()

        # Calculate risk score
        risk_score = self._calculate_oracle_risk_score(max_deviation, duration_sec)

        # Determine if dangerous
        is_dangerous = (
            max_deviation >= self.DEVIATION_DANGER and
            duration_sec >= self.SUSTAINED_DURATION_SEC
        )

        deviation = OracleDeviation(
            timestamp=datetime.now(timezone.utc),
            asset=asset,
            hyperliquid_price=hyperliquid_price,
            binance_price=binance_price,
            coinbase_price=coinbase_price,
            max_deviation_pct=max_deviation,
            duration_seconds=duration_sec,
            is_dangerous=is_dangerous,
            risk_score=risk_score
        )

        return deviation

    def _calculate_oracle_risk_score(self, deviation_pct: float, duration_sec: float) -> float:
        """
        Calculate risk score for oracle deviation (0-100)

        Args:
            deviation_pct: Price deviation percentage
            duration_sec: Duration of deviation

        Returns:
            Risk score 0-100
        """
        score = 0.0

        # Deviation magnitude component (0-60 points)
        if deviation_pct >= self.DEVIATION_CRITICAL:
            score += 60
        elif deviation_pct >= self.DEVIATION_DANGER:
            score += 40
        else:
            score += (deviation_pct / self.DEVIATION_WARNING) * 20

        # Duration component (0-40 points)
        if duration_sec >= 300:  # 5 minutes
            score += 40
        elif duration_sec >= 60:  # 1 minute
            score += 30
        elif duration_sec >= 30:  # 30 seconds
            score += 20
        else:
            score += (duration_sec / 30) * 10

        return min(100, score)

    def _deviation_to_exploit(self, deviation: OracleDeviation) -> Dict[str, Any]:
        """Convert oracle deviation to exploit format"""
        event_id = self._generate_deviation_id(deviation)

        severity = self._get_deviation_severity(deviation)

        return {
            'tx_hash': event_id,
            'chain': 'Hyperliquid',
            'protocol': 'Hyperliquid Oracle',
            'amount_usd': 0,  # Oracle manipulation doesn't directly show loss
            'timestamp': deviation.timestamp,
            'source': self.name,
            'source_url': 'https://app.hyperliquid.xyz',
            'category': 'oracle_manipulation',
            'description': (
                f"Oracle price deviation detected for {deviation.asset}. "
                f"Hyperliquid price: ${deviation.hyperliquid_price:,.2f}, "
                f"External sources: "
                f"Binance ${deviation.binance_price:,.2f}, "
                f"Coinbase ${deviation.coinbase_price:,.2f}. "
                f"Max deviation: {deviation.max_deviation_pct:.2f}%, "
                f"Duration: {deviation.duration_seconds:.0f}s. "
                f"Risk score: {deviation.risk_score:.0f}/100"
            ),
            'recovery_status': 'active' if deviation.is_dangerous else 'resolved'
        }

    def _get_deviation_severity(self, deviation: OracleDeviation) -> str:
        """Determine severity level of deviation"""
        if deviation.max_deviation_pct >= self.DEVIATION_CRITICAL:
            return "critical"
        elif deviation.max_deviation_pct >= self.DEVIATION_DANGER:
            return "high"
        elif deviation.max_deviation_pct >= self.DEVIATION_WARNING:
            return "medium"
        else:
            return "low"

    def _generate_deviation_id(self, deviation: OracleDeviation) -> str:
        """Generate unique deviation ID"""
        data = f"oracle_{deviation.asset}_{deviation.timestamp.isoformat()}"
        return "oracle-" + hashlib.sha256(data.encode()).hexdigest()[:16]

    def get_current_deviations(self) -> List[OracleDeviation]:
        """
        Get all currently active oracle deviations

        Returns:
            List of active deviations
        """
        return list(self.active_deviations.values())

    def get_deviation_history(self, asset: str, limit: int = 50) -> List[OracleDeviation]:
        """
        Get deviation history for an asset

        Args:
            asset: Asset symbol
            limit: Maximum number of records to return

        Returns:
            List of historical deviations
        """
        history = list(self.deviation_history.get(asset, []))
        return history[-limit:]
