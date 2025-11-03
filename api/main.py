# -*- coding: utf-8 -*-
"""
KAMIYO Hyperliquid API
FastAPI server for Hyperliquid exploit intelligence
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

# Import aggregators and monitors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from aggregators import HyperliquidAPIAggregator, GitHubHistoricalAggregator
from monitors import HLPVaultMonitor, LiquidationAnalyzer, OracleMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="KAMIYO Hyperliquid Security Intelligence",
    description="Real-time security monitoring and exploit detection for Hyperliquid ecosystem",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize aggregators
hyperliquid_agg = HyperliquidAPIAggregator()
github_agg = GitHubHistoricalAggregator()

# Initialize security monitors
hlp_monitor = HLPVaultMonitor()
liquidation_analyzer = LiquidationAnalyzer()
oracle_monitor = OracleMonitor()

# In-memory cache (replace with Redis in production)
exploit_cache = {
    'exploits': [],
    'last_updated': None
}

security_cache = {
    'events': [],
    'last_scan': None
}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "KAMIYO Hyperliquid Security Intelligence",
        "version": "2.0.0",
        "description": "Real-time security monitoring and exploit detection for Hyperliquid ecosystem",
        "features": [
            "HLP Vault Health Monitoring",
            "Liquidation Pattern Analysis",
            "Oracle Deviation Detection",
            "Multi-source Exploit Aggregation",
            "Real-time Security Alerts"
        ],
        "endpoints": {
            "core": {
                "/exploits": "Get detected exploits",
                "/stats": "Get statistics",
                "/health": "Health check",
                "/meta": "Get Hyperliquid metadata"
            },
            "security": {
                "/security/dashboard": "Security overview and risk scores",
                "/security/hlp-vault": "HLP vault health status",
                "/security/oracle-deviations": "Active oracle price deviations",
                "/security/events": "Security events and alerts"
            }
        }
    }


@app.get("/exploits")
async def get_exploits(
    limit: int = Query(default=100, ge=1, le=500),
    chain: Optional[str] = Query(default=None),
    min_amount: Optional[float] = Query(default=None),
    days: int = Query(default=7, ge=1, le=365)
):
    """
    Get Hyperliquid exploits

    Args:
        limit: Maximum number of exploits to return (1-500)
        chain: Filter by blockchain (default: all chains)
        min_amount: Minimum USD amount
        days: Number of days to look back

    Returns:
        List of exploits
    """
    try:
        # Check cache
        if exploit_cache['last_updated']:
            cache_age = (datetime.now() - exploit_cache['last_updated']).seconds
            if cache_age < 300:  # 5 minutes
                exploits = exploit_cache['exploits']
                logger.info(f"Returning {len(exploits)} exploits from cache")
            else:
                exploits = await _fetch_all_exploits()
        else:
            exploits = await _fetch_all_exploits()

        # Filter by chain
        if chain:
            exploits = [e for e in exploits if e.get('chain', '').lower() == chain.lower()]

        # Filter by minimum amount
        if min_amount:
            exploits = [e for e in exploits if e.get('amount_usd', 0) >= min_amount]

        # Filter by date
        cutoff_date = datetime.now() - timedelta(days=days)
        exploits = [
            e for e in exploits
            if isinstance(e.get('timestamp'), datetime) and e['timestamp'] >= cutoff_date
        ]

        # Sort by timestamp (newest first)
        exploits.sort(key=lambda x: x.get('timestamp', datetime.min), reverse=True)

        # Apply limit
        exploits = exploits[:limit]

        return {
            "success": True,
            "count": len(exploits),
            "exploits": exploits
        }

    except Exception as e:
        logger.error(f"Error fetching exploits: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """
    Get Hyperliquid exploit statistics

    Returns:
        Statistics about exploits
    """
    try:
        # Fetch exploits
        exploits = exploit_cache.get('exploits', [])

        if not exploits:
            exploits = await _fetch_all_exploits()

        # Calculate stats
        total_count = len(exploits)
        total_loss = sum(e.get('amount_usd', 0) for e in exploits)

        # Group by chain
        by_chain = {}
        for exploit in exploits:
            chain = exploit.get('chain', 'Unknown')
            if chain not in by_chain:
                by_chain[chain] = {'count': 0, 'total_usd': 0}

            by_chain[chain]['count'] += 1
            by_chain[chain]['total_usd'] += exploit.get('amount_usd', 0)

        # Group by source
        by_source = {}
        for exploit in exploits:
            source = exploit.get('source', 'Unknown')
            if source not in by_source:
                by_source[source] = {'count': 0, 'total_usd': 0}

            by_source[source]['count'] += 1
            by_source[source]['total_usd'] += exploit.get('amount_usd', 0)

        return {
            "success": True,
            "total_exploits": total_count,
            "total_loss_usd": total_loss,
            "by_chain": by_chain,
            "by_source": by_source,
            "last_updated": exploit_cache.get('last_updated')
        }

    except Exception as e:
        logger.error(f"Error calculating stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "aggregators": {
            "hyperliquid_api": "active",
            "github_historical": "active"
        }
    }


@app.get("/meta")
async def get_metadata():
    """
    Get Hyperliquid metadata (available assets, etc.)

    Returns:
        Metadata from Hyperliquid API
    """
    try:
        meta = hyperliquid_agg.get_meta()
        mids = hyperliquid_agg.get_all_mids()

        return {
            "success": True,
            "meta": meta,
            "prices": mids
        }

    except Exception as e:
        logger.error(f"Error fetching metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _fetch_all_exploits() -> List[Dict[str, Any]]:
    """
    Fetch exploits from all aggregators and update cache

    Returns:
        Combined list of exploits from all sources
    """
    all_exploits = []

    # Fetch from Hyperliquid API
    try:
        hyperliquid_exploits = hyperliquid_agg.fetch_exploits()
        all_exploits.extend(hyperliquid_exploits)
        logger.info(f"Fetched {len(hyperliquid_exploits)} exploits from Hyperliquid API")
    except Exception as e:
        logger.error(f"Error fetching from Hyperliquid API: {e}")

    # Fetch from GitHub historical data
    try:
        github_exploits = github_agg.fetch_exploits()
        all_exploits.extend(github_exploits)
        logger.info(f"Fetched {len(github_exploits)} exploits from GitHub historical data")
    except Exception as e:
        logger.error(f"Error fetching from GitHub: {e}")

    # Fetch from security monitors
    try:
        hlp_exploits = hlp_monitor.fetch_exploits()
        all_exploits.extend(hlp_exploits)
        logger.info(f"Fetched {len(hlp_exploits)} exploits from HLP monitor")
    except Exception as e:
        logger.error(f"Error fetching from HLP monitor: {e}")

    try:
        liquidation_exploits = liquidation_analyzer.fetch_exploits()
        all_exploits.extend(liquidation_exploits)
        logger.info(f"Fetched {len(liquidation_exploits)} exploits from liquidation analyzer")
    except Exception as e:
        logger.error(f"Error fetching from liquidation analyzer: {e}")

    try:
        oracle_exploits = oracle_monitor.fetch_exploits()
        all_exploits.extend(oracle_exploits)
        logger.info(f"Fetched {len(oracle_exploits)} exploits from oracle monitor")
    except Exception as e:
        logger.error(f"Error fetching from oracle monitor: {e}")

    # Deduplicate by tx_hash
    seen = set()
    unique_exploits = []
    for exploit in all_exploits:
        tx_hash = exploit.get('tx_hash')
        if tx_hash and tx_hash not in seen:
            seen.add(tx_hash)
            unique_exploits.append(exploit)

    # Update cache
    exploit_cache['exploits'] = unique_exploits
    exploit_cache['last_updated'] = datetime.now()

    logger.info(f"Total unique exploits: {len(unique_exploits)}")

    return unique_exploits


# ============================================================================
# SECURITY MONITORING ENDPOINTS
# ============================================================================

@app.get("/security/dashboard")
async def get_security_dashboard():
    """
    Get comprehensive security overview

    Returns:
        Security dashboard with risk scores, active threats, and health metrics
    """
    try:
        # Get HLP vault health
        hlp_health = hlp_monitor.get_current_health()

        # Get active oracle deviations
        oracle_deviations = oracle_monitor.get_current_deviations()

        # Get recent exploits
        recent_exploits = exploit_cache.get('exploits', [])[:10]

        # Calculate overall risk score
        risk_score = _calculate_overall_risk_score(hlp_health, oracle_deviations, recent_exploits)

        # Determine risk level
        risk_level = "LOW"
        if risk_score >= 70:
            risk_level = "CRITICAL"
        elif risk_score >= 50:
            risk_level = "HIGH"
        elif risk_score >= 30:
            risk_level = "MEDIUM"

        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "overall_risk": {
                "score": risk_score,
                "level": risk_level
            },
            "hlp_vault": {
                "is_healthy": hlp_health.is_healthy if hlp_health else True,
                "anomaly_score": hlp_health.anomaly_score if hlp_health else 0,
                "account_value": hlp_health.account_value if hlp_health else 0,
                "pnl_24h": hlp_health.pnl_24h if hlp_health else 0
            },
            "oracle_monitoring": {
                "active_deviations": len(oracle_deviations),
                "deviations": [d.to_dict() for d in oracle_deviations[:5]]
            },
            "recent_exploits": {
                "count_24h": len([e for e in recent_exploits if (datetime.now() - e.get('timestamp', datetime.min)).days < 1]),
                "total_loss_24h": sum(e.get('amount_usd', 0) for e in recent_exploits if (datetime.now() - e.get('timestamp', datetime.min)).days < 1),
                "recent": recent_exploits[:5]
            },
            "monitoring_status": {
                "hlp_monitor": "active",
                "oracle_monitor": "active",
                "liquidation_analyzer": "active"
            }
        }

    except Exception as e:
        logger.error(f"Error generating security dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/security/hlp-vault")
async def get_hlp_vault_health():
    """
    Get HLP vault health and anomaly detection

    Returns:
        Current HLP vault health metrics and risk assessment
    """
    try:
        health = hlp_monitor.get_current_health()

        if not health:
            return {
                "success": False,
                "error": "Could not fetch HLP vault data"
            }

        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "vault_address": health.vault_address,
            "health_status": {
                "is_healthy": health.is_healthy,
                "anomaly_score": health.anomaly_score,
                "health_issues": health.health_issues or []
            },
            "metrics": {
                "total_value_locked": health.total_value_locked,
                "account_value": health.account_value,
                "pnl_24h": health.pnl_24h,
                "pnl_7d": health.pnl_7d,
                "pnl_30d": health.pnl_30d
            },
            "performance": {
                "sharpe_ratio": health.sharpe_ratio,
                "max_drawdown": health.max_drawdown,
                "win_rate": health.win_rate
            },
            "risk_indicators": {
                "volatility_score": health.volatility_score,
                "loss_streak_score": health.loss_streak_score
            }
        }

    except Exception as e:
        logger.error(f"Error fetching HLP vault health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/security/oracle-deviations")
async def get_oracle_deviations(
    active_only: bool = Query(default=True)
):
    """
    Get oracle price deviations

    Args:
        active_only: Only return currently active deviations

    Returns:
        List of oracle price deviations
    """
    try:
        if active_only:
            deviations = oracle_monitor.get_current_deviations()
        else:
            # Get all recent deviations from all assets
            deviations = []
            for asset in ['BTC', 'ETH', 'SOL', 'MATIC', 'ARB', 'OP', 'AVAX']:
                history = oracle_monitor.get_deviation_history(asset, limit=10)
                deviations.extend(history)

        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "count": len(deviations),
            "deviations": [d.to_dict() for d in deviations]
        }

    except Exception as e:
        logger.error(f"Error fetching oracle deviations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/security/events")
async def get_security_events(
    severity: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200)
):
    """
    Get security events and alerts

    Args:
        severity: Filter by severity (critical, high, medium, low, info)
        limit: Maximum number of events to return

    Returns:
        List of security events
    """
    try:
        # For now, convert recent exploits to events format
        # In production, would store actual SecurityEvent objects
        exploits = exploit_cache.get('exploits', [])[:limit]

        events = []
        for exploit in exploits:
            category = exploit.get('category', '')
            exploit_severity = "medium"

            # Determine severity based on amount and category
            amount = exploit.get('amount_usd', 0)
            if amount > 5_000_000 or 'critical' in category:
                exploit_severity = "critical"
            elif amount > 1_000_000 or 'high' in category:
                exploit_severity = "high"
            elif 'manipulation' in category or 'oracle' in category:
                exploit_severity = "high"

            # Filter by severity if specified
            if severity and exploit_severity != severity.lower():
                continue

            event = {
                "event_id": exploit.get('tx_hash'),
                "timestamp": exploit.get('timestamp').isoformat() if isinstance(exploit.get('timestamp'), datetime) else exploit.get('timestamp'),
                "severity": exploit_severity,
                "threat_type": exploit.get('category', 'unknown'),
                "title": f"{exploit.get('protocol', 'Hyperliquid')} - ${exploit.get('amount_usd', 0):,.0f} detected",
                "description": exploit.get('description', ''),
                "source": exploit.get('source', 'unknown')
            }

            events.append(event)

        return {
            "success": True,
            "count": len(events),
            "events": events
        }

    except Exception as e:
        logger.error(f"Error fetching security events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _calculate_overall_risk_score(hlp_health, oracle_deviations, recent_exploits) -> float:
    """
    Calculate overall risk score for the Hyperliquid ecosystem

    Args:
        hlp_health: HLP vault health snapshot
        oracle_deviations: List of active oracle deviations
        recent_exploits: List of recent exploits

    Returns:
        Risk score 0-100
    """
    score = 0.0

    # HLP health component (0-40 points)
    if hlp_health:
        score += (hlp_health.anomaly_score / 100) * 40

    # Oracle deviation component (0-30 points)
    if oracle_deviations:
        max_oracle_risk = max([d.risk_score for d in oracle_deviations], default=0)
        score += (max_oracle_risk / 100) * 30

    # Recent exploits component (0-30 points)
    recent_24h = [e for e in recent_exploits if (datetime.now() - e.get('timestamp', datetime.min)).days < 1]
    if recent_24h:
        # More recent exploits = higher risk
        score += min(30, len(recent_24h) * 10)

    return min(100, score)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
