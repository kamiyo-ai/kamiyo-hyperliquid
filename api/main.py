# -*- coding: utf-8 -*-
"""
KAMIYO Hyperliquid API
FastAPI server for Hyperliquid exploit intelligence
"""

from fastapi import FastAPI, Query, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import logging
import os
import hashlib
import json
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import aggregators and monitors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from aggregators import HyperliquidAPIAggregator, GitHubHistoricalAggregator
from monitors import HLPVaultMonitor, LiquidationAnalyzer, OracleMonitor
from database.integration import get_db_integration
from api.auth import get_api_key, AuthenticationStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
# Default: 60 requests per minute per IP
# Can be overridden with RATE_LIMIT environment variable
limiter = Limiter(key_func=get_remote_address, default_limits=[os.getenv("RATE_LIMIT", "60/minute")])

# Initialize FastAPI app
app = FastAPI(
    title="KAMIYO Hyperliquid Security Intelligence",
    description="Real-time security monitoring and exploit detection for Hyperliquid ecosystem",
    version="2.0.0"
)

# Add rate limit handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
# SECURITY: For production, set ALLOWED_ORIGINS environment variable to specific domains
# Example: ALLOWED_ORIGINS="https://kamiyo.io,https://app.kamiyo.io"
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,  # Changed from True to prevent CSRF when using wildcard origins
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Initialize aggregators
hyperliquid_agg = HyperliquidAPIAggregator()
github_agg = GitHubHistoricalAggregator()

# Initialize security monitors
hlp_monitor = HLPVaultMonitor()
liquidation_analyzer = LiquidationAnalyzer()
oracle_monitor = OracleMonitor()

# Initialize database integration
try:
    db_integration = get_db_integration()
    logger.info("Database integration enabled for API")
except Exception as e:
    logger.warning(f"Database integration disabled: {e}")
    db_integration = None

# In-memory cache (replace with Redis in production)
exploit_cache = {
    'exploits': [],
    'last_updated': None
}

security_cache = {
    'events': [],
    'last_scan': None
}

# Application startup time
app_start_time = datetime.now(timezone.utc)


def _generate_exploit_id(exploit: Dict[str, Any]) -> str:
    """
    Generate a unique ID for an exploit event

    For exploits with tx_hash, use that as the ID.
    For non-transaction events (monitor alerts), generate a hash based on key attributes.

    Args:
        exploit: Exploit data dictionary

    Returns:
        Unique identifier string
    """
    # If tx_hash exists, use it
    tx_hash = exploit.get('tx_hash')
    if tx_hash:
        return tx_hash

    # For non-transaction events, generate composite key
    # Use source, timestamp, amount, and description to create unique hash
    composite_data = {
        'source': exploit.get('source', ''),
        'timestamp': str(exploit.get('timestamp', '')),
        'amount_usd': exploit.get('amount_usd', 0),
        'description': exploit.get('description', '')[:100],  # First 100 chars
        'category': exploit.get('category', ''),
        'protocol': exploit.get('protocol', '')
    }

    # Create hash from composite data
    data_str = json.dumps(composite_data, sort_keys=True, default=str)
    return hashlib.sha256(data_str.encode()).hexdigest()[:16]


@app.get("/")
@limiter.limit("100/minute")
async def root(request: Request):
    """Root endpoint"""
    auth_status = AuthenticationStatus.get_status()

    return {
        "name": "KAMIYO Hyperliquid Security Intelligence",
        "version": "2.0.0",
        "description": "Real-time security monitoring and exploit detection for Hyperliquid ecosystem",
        "authentication": auth_status,
        "features": [
            "HLP Vault Health Monitoring",
            "Liquidation Pattern Analysis",
            "Oracle Deviation Detection",
            "Multi-source Exploit Aggregation",
            "Real-time Security Alerts",
            "Database Persistence",
            "WebSocket Real-time Monitoring",
            "Multi-channel Alert System"
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
                "/security/hlp-vault/history": "Historical HLP vault snapshots",
                "/security/oracle-deviations": "Active oracle price deviations",
                "/security/oracle-deviations/history": "Historical oracle deviations",
                "/security/liquidation-patterns": "Detected liquidation patterns",
                "/security/events": "Security events and alerts",
                "/security/events/database": "Security events from database"
            }
        },
        "documentation": "https://github.com/kamiyo/kamiyo-hyperliquid"
    }


@app.get("/exploits")
@limiter.limit("30/minute")  # Stricter limit for expensive endpoint
async def get_exploits(
    request: Request,
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
            cache_age = (datetime.now(timezone.utc) - exploit_cache['last_updated']).total_seconds()
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
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
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
        logger.error(f"Error fetching exploits: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching exploits")


@app.get("/stats")
@limiter.limit("60/minute")
async def get_stats(request: Request):
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

        # Calculate uptime
        uptime_seconds = (datetime.now(timezone.utc) - app_start_time).total_seconds()

        # Get monitored assets from oracle monitor
        monitored_assets = ['BTC', 'ETH', 'SOL', 'MATIC', 'ARB', 'OP', 'AVAX']

        # Get alert channels configuration
        from alerts import get_alert_manager
        alert_manager = get_alert_manager()
        alert_channels_configured = sum(1 for enabled in alert_manager.enabled_channels.values() if enabled)

        return {
            "success": True,
            "total_exploits": total_count,
            "total_loss_usd": total_loss,
            "by_chain": by_chain,
            "by_source": by_source,
            "last_updated": exploit_cache.get('last_updated'),
            "monitored_assets": monitored_assets,
            "alert_channels_configured": alert_channels_configured,
            "uptime_seconds": uptime_seconds
        }

    except Exception as e:
        logger.error(f"Error calculating stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while calculating statistics")


@app.get("/health")
@limiter.limit("100/minute")
async def health_check(request: Request):
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "aggregators": {
            "hyperliquid_api": "active",
            "github_historical": "active"
        }
    }


@app.get("/meta")
@limiter.limit("60/minute")
async def get_metadata(request: Request):
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
        logger.error(f"Error fetching metadata: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching metadata")


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

    # Deduplicate by unique ID (tx_hash for transactions, generated hash for monitor events)
    seen = set()
    unique_exploits = []
    for exploit in all_exploits:
        exploit_id = _generate_exploit_id(exploit)
        if exploit_id not in seen:
            seen.add(exploit_id)
            unique_exploits.append(exploit)

    # Update cache
    exploit_cache['exploits'] = unique_exploits
    exploit_cache['last_updated'] = datetime.now(timezone.utc)

    logger.info(f"Total unique exploits: {len(unique_exploits)}")

    return unique_exploits


# ============================================================================
# SECURITY MONITORING ENDPOINTS
# ============================================================================

@app.get("/security/dashboard")
@limiter.limit("30/minute")  # Stricter limit for expensive security endpoint
async def get_security_dashboard(
    request: Request,
    api_key: Optional[str] = Depends(get_api_key)
):
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

        # Get database statistics if available
        db_stats = {}
        if db_integration:
            try:
                hlp_stats = db_integration.get_hlp_statistics(days=30)
                recent_events = db_integration.get_security_events(hours=24, limit=10)

                db_stats = {
                    "hlp_statistics_30d": hlp_stats,
                    "security_events_24h": len(recent_events),
                    "database_enabled": True
                }
            except Exception as e:
                logger.warning(f"Could not fetch database statistics: {e}")
                db_stats = {"database_enabled": False}
        else:
            db_stats = {"database_enabled": False}

        return {
            "success": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
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
                "count_24h": len([e for e in recent_exploits if (datetime.now(timezone.utc) - e.get('timestamp', datetime.min)).total_seconds() < 86400]),
                "total_loss_24h": sum(e.get('amount_usd', 0) for e in recent_exploits if (datetime.now(timezone.utc) - e.get('timestamp', datetime.min)).total_seconds() < 86400),
                "recent": recent_exploits[:5]
            },
            "monitoring_status": {
                "hlp_monitor": "active",
                "oracle_monitor": "active",
                "liquidation_analyzer": "active"
            },
            "database": db_stats
        }

    except Exception as e:
        logger.error(f"Error generating security dashboard: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while generating security dashboard")


@app.get("/security/hlp-vault")
@limiter.limit("60/minute")
async def get_hlp_vault_health(request: Request):
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
            "timestamp": datetime.now(timezone.utc).isoformat(),
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
        logger.error(f"Error fetching HLP vault health: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching HLP vault health")


@app.get("/security/oracle-deviations")
@limiter.limit("60/minute")
async def get_oracle_deviations(
    request: Request,
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
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "count": len(deviations),
            "deviations": [d.to_dict() for d in deviations]
        }

    except Exception as e:
        logger.error(f"Error fetching oracle deviations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching oracle deviations")


@app.get("/security/events")
@limiter.limit("60/minute")
async def get_security_events(
    request: Request,
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
        logger.error(f"Error fetching security events: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching security events")


# ============================================================================
# DATABASE-BACKED ENDPOINTS
# ============================================================================

@app.get("/security/hlp-vault/history")
@limiter.limit("30/minute")
async def get_hlp_vault_history(
    request: Request,
    limit: int = Query(default=100, ge=1, le=500)
):
    """
    Get historical HLP vault snapshots from database

    Args:
        limit: Maximum number of snapshots to return (1-500)

    Returns:
        Historical HLP vault snapshots
    """
    try:
        if not db_integration:
            raise HTTPException(
                status_code=503,
                detail="Database integration not available"
            )

        snapshots = db_integration.get_recent_hlp_snapshots(limit=limit)

        # Convert to dict format
        snapshot_data = []
        for snapshot in snapshots:
            snapshot_data.append({
                "timestamp": snapshot.timestamp.isoformat(),
                "vault_address": snapshot.vault_address,
                "account_value": float(snapshot.account_value),
                "pnl_24h": float(snapshot.pnl_24h) if snapshot.pnl_24h else None,
                "all_time_pnl": float(snapshot.all_time_pnl) if snapshot.all_time_pnl else None,
                "sharpe_ratio": float(snapshot.sharpe_ratio) if snapshot.sharpe_ratio else None,
                "max_drawdown": float(snapshot.max_drawdown),
                "anomaly_score": float(snapshot.anomaly_score),
                "is_healthy": snapshot.is_healthy,
                "health_issues": snapshot.health_issues
            })

        return {
            "success": True,
            "count": len(snapshot_data),
            "snapshots": snapshot_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching HLP vault history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching HLP vault history")


@app.get("/security/oracle-deviations/history")
@limiter.limit("30/minute")
async def get_oracle_deviation_history(
    request: Request,
    asset: Optional[str] = Query(default=None),
    hours: int = Query(default=24, ge=1, le=168),
    limit: int = Query(default=100, ge=1, le=500)
):
    """
    Get historical oracle deviations from database

    Args:
        asset: Filter by asset (e.g., BTC, ETH)
        hours: Hours of history to retrieve (1-168)
        limit: Maximum number of deviations to return (1-500)

    Returns:
        Historical oracle deviations
    """
    try:
        if not db_integration:
            raise HTTPException(
                status_code=503,
                detail="Database integration not available"
            )

        if asset:
            deviations = db_integration.get_oracle_deviations_by_asset(asset, hours=hours)
        else:
            # Get all recent deviations across all assets
            from database.models import OracleDeviation as DBOracleDeviation
            from datetime import timedelta

            session = db_integration.db.get_session()
            try:
                cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
                deviations = session.query(DBOracleDeviation)\
                    .filter(DBOracleDeviation.timestamp >= cutoff)\
                    .order_by(DBOracleDeviation.timestamp.desc())\
                    .limit(limit)\
                    .all()
            finally:
                session.close()

        # Convert to dict format
        deviation_data = []
        for deviation in deviations[:limit]:
            deviation_data.append({
                "timestamp": deviation.timestamp.isoformat(),
                "asset": deviation.asset,
                "hyperliquid_price": float(deviation.hyperliquid_price),
                "binance_price": float(deviation.binance_price) if deviation.binance_price else None,
                "coinbase_price": float(deviation.coinbase_price) if deviation.coinbase_price else None,
                "max_deviation_pct": float(deviation.max_deviation_pct),
                "max_deviation_source": deviation.max_deviation_source,
                "risk_score": float(deviation.risk_score),
                "severity": deviation.severity,
                "duration_seconds": float(deviation.duration_seconds)
            })

        return {
            "success": True,
            "count": len(deviation_data),
            "deviations": deviation_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching oracle deviation history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching oracle deviation history")


@app.get("/security/liquidation-patterns")
@limiter.limit("30/minute")
async def get_liquidation_patterns(
    request: Request,
    pattern_type: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200)
):
    """
    Get detected liquidation patterns from database

    Args:
        pattern_type: Filter by pattern type (flash_loan, cascade, etc.)
        limit: Maximum number of patterns to return (1-200)

    Returns:
        Detected liquidation patterns
    """
    try:
        if not db_integration:
            raise HTTPException(
                status_code=503,
                detail="Database integration not available"
            )

        patterns = db_integration.get_recent_liquidation_patterns(
            pattern_type=pattern_type,
            limit=limit
        )

        # Convert to dict format
        pattern_data = []
        for pattern in patterns:
            pattern_data.append({
                "id": pattern.id,
                "pattern_type": pattern.pattern_type,
                "start_time": pattern.start_time.isoformat(),
                "end_time": pattern.end_time.isoformat(),
                "duration_seconds": float(pattern.duration_seconds),
                "total_liquidated_usd": float(pattern.total_liquidated_usd),
                "affected_users": pattern.affected_users,
                "assets_involved": pattern.assets_involved,
                "suspicion_score": float(pattern.suspicion_score),
                "liquidation_count": len(pattern.liquidation_ids) if pattern.liquidation_ids else 0,
                "price_impact": pattern.price_impact
            })

        return {
            "success": True,
            "count": len(pattern_data),
            "patterns": pattern_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching liquidation patterns: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching liquidation patterns")


@app.get("/security/events/database")
@limiter.limit("30/minute")
async def get_database_security_events(
    request: Request,
    severity: Optional[str] = Query(default=None),
    threat_type: Optional[str] = Query(default=None),
    hours: int = Query(default=24, ge=1, le=168),
    limit: int = Query(default=100, ge=1, le=500)
):
    """
    Get security events from database

    Args:
        severity: Filter by severity (critical, high, medium, low, info)
        threat_type: Filter by threat type
        hours: Hours of history to retrieve (1-168)
        limit: Maximum number of events to return (1-500)

    Returns:
        Security events from database
    """
    try:
        if not db_integration:
            raise HTTPException(
                status_code=503,
                detail="Database integration not available"
            )

        events = db_integration.get_security_events(
            severity=severity,
            threat_type=threat_type,
            hours=hours,
            limit=limit
        )

        # Convert to dict format
        event_data = []
        for event in events:
            event_data.append({
                "id": event.event_id,
                "timestamp": event.timestamp.isoformat(),
                "threat_type": event.threat_type,
                "severity": event.severity,
                "title": event.title,
                "description": event.description,
                "indicators": event.indicators or {},
                "affected_addresses": event.related_addresses or [],
                "is_active": event.is_active,
                "resolved_at": event.resolved_at.isoformat() if event.resolved_at else None
            })

        return {
            "success": True,
            "count": len(event_data),
            "events": event_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching database security events: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching database security events")


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
    recent_24h = [e for e in recent_exploits if (datetime.now(timezone.utc) - e.get('timestamp', datetime.min)).total_seconds() < 86400]
    if recent_24h:
        # More recent exploits = higher risk
        score += min(30, len(recent_24h) * 10)

    return min(100, score)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
