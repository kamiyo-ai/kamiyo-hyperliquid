# KAMIYO Hyperliquid

Exploit intelligence aggregator specialized for the Hyperliquid ecosystem.

## Overview

```
┌─────────┐              ┌──────────────┐              ┌───────────┐
│         │   Request    │              │   Aggregate  │           │
│ Client  │ ──────────> │   KAMIYO     │ ──────────> │Hyperliquid│
│         │              │  Hyperliquid │              │  Sources  │
└────┬────┘              └──────┬───────┘              └───────────┘
     │                          │
     │ Exploit Data             │
     │<─────────────────────────┤
     │                          │
```

## Features

- **Hyperliquid-Focused**: Specialized aggregation for Hyperliquid DEX exploits and liquidations
- **Real-Time Monitoring**: Track liquidations, exploits, and security events
- **Multi-Source**: Aggregate from Hyperliquid API, GitHub historical data, CoinGlass, and social monitoring
- **REST API**: FastAPI-powered endpoints for querying exploit and liquidation data
- **WebSocket**: Real-time streaming of new liquidations and exploits

## Architecture

### System Components

```
┌────────────────────────────────────────────────────────────────────┐
│                      Data Aggregation Layer                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                  Hyperliquid Aggregators                      │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  • Hyperliquid Official API (liquidations, positions)   │  │  │
│  │  │  • GitHub Historical Data (historical liquidations)     │  │  │
│  │  │  • CoinGlass (whale liquidations, heatmaps)            │  │  │
│  │  │  • Twitter/X (security announcements)                   │  │  │
│  │  │  • Discord/Telegram (community alerts)                  │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────┬───────────────────────────────────────┘  │
└─────────────────────────┼──────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────────────┐
│                  Normalization & Deduplication                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Standard Exploit Format                          │  │
│  │                                                               │  │
│  │  • liquidation_id, user, asset, side                         │  │
│  │  • size, liquidation_price, amount_usd                       │  │
│  │  • timestamp, source, metadata                               │  │
│  └──────────────────────┬───────────────────────────────────────┘  │
└─────────────────────────┼──────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────────────┐
│                     Storage & Caching                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  PostgreSQL (persistent)     Redis (caching)                  │  │
│  └──────────────────────┬───────────────┬───────────────────────┘  │
└─────────────────────────┼───────────────┼──────────────────────────┘
                          │               │
                          ▼               ▼
┌────────────────────────────────────────────────────────────────────┐
│                        API Layer (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  GET /liquidations    GET /exploits     GET /stats            │  │
│  │  WebSocket /stream    GET /assets       GET /health           │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/mizuki-tamaki/kamiyo-hyperliquid.git
cd kamiyo-hyperliquid

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Run API server
python api/main.py
```

### Docker Deployment

```bash
docker build -t kamiyo-hyperliquid .
docker run -p 8000:8000 kamiyo-hyperliquid
```

## API Usage

### Get Recent Liquidations

```bash
curl http://localhost:8000/liquidations?limit=10
```

### Get Hyperliquid Exploits

```bash
curl http://localhost:8000/exploits?chain=hyperliquid
```

### Stream Real-Time Liquidations

```python
import websocket

ws = websocket.create_connection("ws://localhost:8000/stream")
while True:
    data = ws.recv()
    print(f"New liquidation: {data}")
```

### Get Statistics

```bash
curl http://localhost:8000/stats/hyperliquid
```

## Supported Data Sources

| Source | Type | Data | Update Frequency |
|--------|------|------|------------------|
| Hyperliquid API | Official | Liquidations, positions | Real-time (WebSocket) |
| GitHub Historical | Official | Historical liquidations, trades | Daily CSV updates |
| CoinGlass | Third-party | Whale liquidations, heatmaps | Real-time |
| Twitter/X | Social | Security announcements | Real-time |
| Discord/Telegram | Social | Community alerts | Real-time |

## Data Format

### Liquidation Object

```json
{
  "liquidation_id": "liq-a1b2c3d4e5f6",
  "user": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "asset": "BTC-USD",
  "side": "LONG",
  "size": 1.5,
  "liquidation_price": 95000.0,
  "mark_price": 94800.0,
  "amount_usd": 142500.0,
  "leverage": 20.0,
  "timestamp": "2025-11-03T08:30:00Z",
  "source": "hyperliquid_api",
  "source_url": "https://api.hyperliquid.xyz/info",
  "metadata": {
    "margin_used": 7125.0,
    "margin_remaining": 0.0,
    "account_value": 7125.0
  }
}
```

### Exploit Object

```json
{
  "tx_hash": "0xabc123...",
  "chain": "Hyperliquid",
  "protocol": "HyperDEX",
  "amount_usd": 1500000.0,
  "timestamp": "2025-11-03T08:30:00Z",
  "source": "twitter_monitor",
  "source_url": "https://twitter.com/...",
  "category": "smart_contract",
  "description": "Reentrancy exploit on HyperDEX contract",
  "recovery_status": "partial"
}
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/kamiyo_hyperliquid

# Redis Cache
REDIS_URL=redis://localhost:6379

# API Keys (optional)
TWITTER_BEARER_TOKEN=your_token
DISCORD_BOT_TOKEN=your_token
TELEGRAM_BOT_TOKEN=your_token

# Hyperliquid Settings
HYPERLIQUID_NETWORK=mainnet  # or testnet
HYPERLIQUID_WS_URL=wss://api.hyperliquid.xyz/ws
```

## Development

### Run Tests

```bash
pytest tests/ -v
```

### Run Aggregators

```bash
# Run all aggregators
python -m aggregators.orchestrator

# Run specific aggregator
python -m aggregators.hyperliquid_api
```

### Add New Aggregator

1. Create new file in `aggregators/` directory
2. Extend `BaseLiquidationAggregator` or `BaseAggregator`
3. Implement `fetch_liquidations()` or `fetch_exploits()`
4. Add to orchestrator configuration

## Technical Details

### Aggregator Base Classes

- **BaseLiquidationAggregator**: For Hyperliquid-specific liquidation data
- **BaseAggregator**: For general exploit data (inherited from main KAMIYO)

### Normalization Pipeline

1. Fetch raw data from source
2. Parse and extract relevant fields
3. Convert to standard format (liquidation or exploit)
4. Validate required fields
5. Deduplicate by liquidation_id or tx_hash
6. Store in database and cache

### Real-Time Updates

WebSocket connections monitor:
- Hyperliquid official WebSocket API for new liquidations
- Twitter Stream API for security announcements
- Discord/Telegram channels for community alerts

## Performance

- **Aggregation Latency**: <500ms per source
- **API Response Time**: <100ms (cached), <500ms (uncached)
- **WebSocket Latency**: <50ms for new events
- **Database Queries**: Indexed on liquidation_id, user, asset, timestamp

## Security

- Rate limiting on API endpoints
- Input validation and sanitization
- SQL injection prevention (parameterized queries)
- CORS configuration for web access
- API key authentication for write operations

## Roadmap

- [ ] ML-based liquidation prediction
- [ ] Historical analysis dashboards
- [ ] Advanced filtering and search
- [ ] Export to CSV/JSON
- [ ] Email/SMS alerts for large liquidations
- [ ] Integration with DeFi analytics platforms

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- GitHub Issues: https://github.com/mizuki-tamaki/kamiyo-hyperliquid/issues
- Documentation: https://docs.kamiyo.ai/hyperliquid
- Twitter: @KAMIYOAI

## Acknowledgments

- Hyperliquid team for official API and historical data
- CoinGlass for liquidation analytics
- KAMIYO main project for aggregator framework
