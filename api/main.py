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

# Import aggregators
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from aggregators import HyperliquidAPIAggregator, GitHubHistoricalAggregator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="KAMIYO Hyperliquid API",
    description="Exploit intelligence aggregator for the Hyperliquid ecosystem",
    version="1.0.0"
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

# In-memory cache (replace with Redis in production)
exploit_cache = {
    'exploits': [],
    'last_updated': None
}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "KAMIYO Hyperliquid API",
        "version": "1.0.0",
        "description": "Exploit intelligence aggregator for Hyperliquid",
        "endpoints": {
            "/exploits": "Get Hyperliquid exploits",
            "/stats": "Get statistics",
            "/health": "Health check",
            "/meta": "Get Hyperliquid metadata"
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
