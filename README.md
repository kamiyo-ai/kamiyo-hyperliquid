# KAMIYO Hyperliquid

<div align="center">

![KAMIYO Logo](https://via.placeholder.com/200x200/4A90E2/FFFFFF?text=KAMIYO)

**Security Intelligence & Exploit Detection for Hyperliquid DEX**

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[Features](#features) • [Quick Start](#quick-start) • [Documentation](#documentation) • [API](#api-usage) • [Contributing](#contributing)

</div>

---

**Real-time security monitoring and exploit detection for the Hyperliquid DEX ecosystem.** Part of the [KAMIYO](https://kamiyo.ai) security intelligence platform - extending exploit detection from 20+ blockchain sources to Hyperliquid-specific attack vectors including HLP vault manipulation, liquidation cascades, and oracle price deviations.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Usage](#api-usage)
- [Data Sources](#supported-data-sources)
- [Configuration](#configuration)
- [Development](#development)
- [Performance](#performance)
- [Security](#security)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## 🎯 Overview

KAMIYO Hyperliquid provides **independent security monitoring** for the Hyperliquid DEX ecosystem, detecting exploits and attack patterns that affect traders, liquidity providers, and the protocol itself. As an external security intelligence layer, we can alert users to threats without creating protocol-level panic.

### 🚨 What We Detect

```mermaid
graph TB
    subgraph "Security Monitors"
        HLP[🏦 HLP Vault Monitor]
        LIQ[⚡ Liquidation Analyzer]
        ORA[📊 Oracle Monitor]
    end

    subgraph "Threat Detection"
        HLP --> T1[Vault Exploitation]
        HLP --> T2[Abnormal Losses]
        LIQ --> T3[Flash Loan Attacks]
        LIQ --> T4[Cascade Liquidations]
        ORA --> T5[Price Manipulation]
        ORA --> T6[Oracle Deviations]
    end

    subgraph "Alerts"
        T1 --> ALERT[🚨 Real-Time Alerts]
        T2 --> ALERT
        T3 --> ALERT
        T4 --> ALERT
        T5 --> ALERT
        T6 --> ALERT
    end

    ALERT --> USER[👤 Traders & LPs]

    style HLP fill:#E74C3C
    style LIQ fill:#F39C12
    style ORA fill:#3498DB
    style ALERT fill:#E74C3C
```

### 🎯 Key Capabilities

| Capability | Description | Status |
|-----------|-------------|--------|
| 🏦 **HLP Vault Monitoring** | Real-time health tracking with anomaly detection (3-sigma analysis) | ✅ Active |
| ⚡ **Liquidation Analysis** | Detects flash loans, cascades, and coordinated attacks | ✅ Active |
| 📊 **Oracle Monitoring** | Price deviation tracking vs Binance/Coinbase | ✅ Active |
| 🚨 **Security Alerts** | <15 min detection time (KAMIYO standard) | ✅ Active |
| 🔄 **Multi-Source Intel** | Aggregates from Hyperliquid + KAMIYO's 20+ sources | ✅ Active |
| 📈 **Risk Scoring** | Overall ecosystem risk score (0-100) | ✅ Active |

## ✨ Features

### 🏦 HLP Vault Health Monitor

**Protects liquidity providers from vault exploitation**

```python
# Real-time detection of
- Large losses: >$1M in 1 hour = CRITICAL alert
- Statistical anomalies: 3-sigma deviations from historical mean
- Abnormal drawdowns: >10% drawdown triggers investigation
- Suspicious PnL patterns: Would have detected the $4M HLP incident

# Example alert
{
  "severity": "CRITICAL",
  "threat_type": "hlp_exploitation",
  "title": "HLP Vault Large Loss Detected: $2,150,000",
  "description": "The HLP vault has experienced a significant loss...",
  "recommended_action": "CRITICAL: Consider pausing HLP deposits..."
}
```

**Key Metrics:**
- Account value tracking
- PnL analysis (24h, 7d, 30d)
- Sharpe ratio & maximum drawdown
- Anomaly score (0-100)

---

### ⚡ Liquidation Pattern Analyzer

**Detects liquidation-based exploits and manipulation**

```python
# Detection patterns
1. Flash Loan Attacks
   - Large liquidations within 10 seconds
   - Minimum $500k threshold
   - Same-block execution detection

2. Cascade Liquidations
   - Domino effects (5+ liquidations)
   - Progressive price decline
   - Within 5-minute window

3. Coordinated Attacks
   - Multiple large liquidations
   - Related addresses
   - Suspicious timing patterns
```

**Suspicion Scoring:**
- 0-30: Normal market activity
- 30-70: Unusual pattern, monitoring
- 70-100: Highly suspicious, alert triggered

---

### 📊 Oracle Deviation Monitor

**Protects traders from price manipulation**

```python
# Real-time comparison
Hyperliquid Price vs:
├── Binance (primary reference)
├── Coinbase (secondary reference)
└── Risk assessment

# Alert thresholds
- 0.3% deviation: Warning
- 0.5% deviation for >30s: Dangerous
- 1.0% deviation: Critical

# Example detection
{
  "asset": "BTC",
  "hyperliquid_price": 95450.00,
  "binance_price": 95000.00,
  "max_deviation_pct": 0.47,
  "duration_seconds": 45,
  "is_dangerous": true,
  "risk_score": 75
}
```

**Protects Against:**
- Oracle manipulation attacks
- Flash crash exploitation
- Price feed anomalies
- Cross-exchange arbitrage abuse

---

### 🚨 Security Dashboard

**Comprehensive risk monitoring**

- **Overall Risk Score** (0-100)
  - LOW: 0-29 (Normal operations)
  - MEDIUM: 30-49 (Minor anomalies)
  - HIGH: 50-69 (Investigate)
  - CRITICAL: 70-100 (Immediate action)

- **Real-Time Alerts**
  - Severity-based filtering
  - Multi-channel notifications
  - Actionable recommendations

- **Historical Analysis**
  - Exploit timeline
  - Attack pattern trends
  - Ecosystem health tracking

## 🏗️ Architecture

### High-Level Overview

```mermaid
graph TB
    subgraph "Data Sources"
        HL[Hyperliquid API]
        GH[GitHub Historical]
        CG[CoinGlass]
        SM[Social Media]
    end

    subgraph "KAMIYO Core"
        AGG[Aggregators]
        NORM[Normalizer]
        DEDUP[Deduplicator]
    end

    subgraph "Storage Layer"
        PG[(PostgreSQL)]
        RD[(Redis Cache)]
    end

    subgraph "API Layer"
        REST[REST API]
        WS[WebSocket]
    end

    HL --> AGG
    GH --> AGG
    CG --> AGG
    SM --> AGG

    AGG --> NORM
    NORM --> DEDUP
    DEDUP --> PG
    DEDUP --> RD

    PG --> REST
    RD --> REST
    PG --> WS
    RD --> WS

    REST --> CLIENT[👤 Client]
    WS --> CLIENT

    style AGG fill:#4A90E2
    style NORM fill:#2ECC71
    style DEDUP fill:#E67E22
    style PG fill:#9B59B6
    style RD fill:#E74C3C
    style REST fill:#1ABC9C
    style WS fill:#F39C12
```

### Data Flow

1. **Collection**: Aggregators fetch from multiple sources
2. **Normalization**: Convert to standard format
3. **Deduplication**: Remove duplicates across sources
4. **Storage**: Persist to PostgreSQL, cache in Redis
5. **API**: Serve via REST/WebSocket to clients

For detailed architecture documentation, see [docs/architecture.md](docs/architecture.md).

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- PostgreSQL 13+ (for persistent storage)
- Redis 6+ (for caching)
- Git

### Installation

```bash
# 1. Clone repository
git clone https://github.com/mizuki-tamaki/kamiyo-hyperliquid.git
cd kamiyo-hyperliquid

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your configuration (see Configuration section)

# 5. Initialize database
python scripts/init_db.py

# 6. Run API server
python api/main.py
```

The API will be available at `http://localhost:8000`

Interactive API docs: `http://localhost:8000/docs`

### 🐳 Docker Deployment

```bash
# Build image
docker build -t kamiyo-hyperliquid .

# Run with docker-compose (includes PostgreSQL and Redis)
docker-compose up -d

# Check logs
docker-compose logs -f kamiyo

# Stop services
docker-compose down
```

### ⚡ Quick Test

```bash
# Check health
curl http://localhost:8000/health

# Get recent liquidations
curl http://localhost:8000/liquidations?limit=5

# Get statistics
curl http://localhost:8000/stats/hyperliquid
```

## 🔌 API Usage

### 🚨 Security Monitoring Endpoints

#### Get Security Dashboard

**Comprehensive security overview with risk scores**

```bash
curl http://localhost:8000/security/dashboard
```

<details>
<summary>Response Example</summary>

```json
{
  "success": true,
  "timestamp": "2025-11-03T14:30:00Z",
  "overall_risk": {
    "score": 35,
    "level": "MEDIUM"
  },
  "hlp_vault": {
    "is_healthy": true,
    "anomaly_score": 25,
    "account_value": 425000000.0,
    "pnl_24h": -150000.0
  },
  "oracle_monitoring": {
    "active_deviations": 0,
    "deviations": []
  },
  "recent_exploits": {
    "count_24h": 0,
    "total_loss_24h": 0,
    "recent": []
  },
  "monitoring_status": {
    "hlp_monitor": "active",
    "oracle_monitor": "active",
    "liquidation_analyzer": "active"
  }
}
```
</details>

---

#### Get HLP Vault Health

**Real-time HLP vault monitoring and risk assessment**

```bash
curl http://localhost:8000/security/hlp-vault
```

<details>
<summary>Response Example</summary>

```json
{
  "success": true,
  "timestamp": "2025-11-03T14:30:00Z",
  "vault_address": "0xdfc24b077bc1425ad1dea75bcb6f8158e10df303",
  "health_status": {
    "is_healthy": true,
    "anomaly_score": 25.5,
    "health_issues": []
  },
  "metrics": {
    "total_value_locked": 425000000.0,
    "account_value": 425000000.0,
    "pnl_24h": -150000.0,
    "pnl_7d": 2300000.0,
    "pnl_30d": 8500000.0
  },
  "performance": {
    "sharpe_ratio": 2.45,
    "max_drawdown": 3.2,
    "win_rate": null
  },
  "risk_indicators": {
    "volatility_score": 0,
    "loss_streak_score": 0
  }
}
```
</details>

---

#### Get Oracle Deviations

**Monitor price manipulation and oracle attacks**

```bash
curl "http://localhost:8000/security/oracle-deviations?active_only=true"
```

<details>
<summary>Response Example</summary>

```json
{
  "success": true,
  "timestamp": "2025-11-03T14:30:00Z",
  "count": 1,
  "deviations": [
    {
      "timestamp": "2025-11-03T14:29:45Z",
      "asset": "BTC",
      "hyperliquid_price": 95450.0,
      "binance_price": 95000.0,
      "coinbase_price": 95020.0,
      "max_deviation_pct": 0.47,
      "duration_seconds": 45,
      "is_dangerous": false,
      "risk_score": 35
    }
  ]
}
```
</details>

---

#### Get Security Events

**Recent security events and alerts**

```bash
curl "http://localhost:8000/security/events?severity=high&limit=10"
```

<details>
<summary>Response Example</summary>

```json
{
  "success": true,
  "count": 2,
  "events": [
    {
      "event_id": "hlp-a1b2c3d4e5f6",
      "timestamp": "2025-11-03T10:15:00Z",
      "severity": "high",
      "threat_type": "hlp_exploitation",
      "title": "HLP Vault - $1,250,000 detected",
      "description": "The HLP vault has experienced a significant loss...",
      "source": "hlp_vault_monitor"
    },
    {
      "event_id": "liq-fla-789abc123def",
      "timestamp": "2025-11-03T08:42:00Z",
      "severity": "high",
      "threat_type": "liquidation_flash_loan",
      "title": "Hyperliquid DEX - $850,000 detected",
      "description": "Suspicious flash_loan liquidation pattern detected...",
      "source": "liquidation_analyzer"
    }
  ]
}
```
</details>

---

### 📊 Data & Analytics Endpoints

#### Get Recent Liquidations

```bash
curl "http://localhost:8000/liquidations?limit=10&asset=BTC-USD"
```

<details>
<summary>Response Example</summary>

```json
{
  "liquidations": [
    {
      "liquidation_id": "liq-a1b2c3d4e5f6",
      "user": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
      "asset": "BTC-USD",
      "side": "LONG",
      "size": 1.5,
      "liquidation_price": 95000.0,
      "amount_usd": 142500.0,
      "timestamp": "2025-11-03T08:30:00Z",
      "source": "hyperliquid_api"
    }
  ],
  "total": 1250,
  "page": 1,
  "limit": 10
}
```
</details>

#### Get Hyperliquid Exploits

```bash
curl "http://localhost:8000/exploits?chain=hyperliquid&min_amount=100000"
```

#### Get Statistics

```bash
curl http://localhost:8000/stats/hyperliquid
```

<details>
<summary>Response Example</summary>

```json
{
  "total_liquidations": 1250,
  "total_volume_usd": 45000000.0,
  "largest_liquidation_usd": 1500000.0,
  "most_liquidated_asset": "BTC-USD",
  "avg_liquidation_size_usd": 36000.0,
  "time_period": "24h"
}
```
</details>

#### Get Asset-Specific Data

```bash
curl http://localhost:8000/assets/BTC-USD/liquidations
```

### WebSocket Streaming

#### Real-Time Liquidation Stream

```python
import asyncio
import websockets
import json

async def stream_liquidations():
    uri = "ws://localhost:8000/stream/liquidations"
    async with websockets.connect(uri) as websocket:
        while True:
            data = await websocket.recv()
            liquidation = json.loads(data)
            print(f"New liquidation: {liquidation['asset']} - ${liquidation['amount_usd']:,.2f}")

asyncio.run(stream_liquidations())
```

#### Subscribe to Specific Assets

```python
import asyncio
import websockets
import json

async def stream_btc_liquidations():
    uri = "ws://localhost:8000/stream/liquidations?asset=BTC-USD"
    async with websockets.connect(uri) as websocket:
        while True:
            data = await websocket.recv()
            liquidation = json.loads(data)
            if liquidation['amount_usd'] > 100000:  # Large liquidations only
                print(f"🚨 LARGE LIQUIDATION: ${liquidation['amount_usd']:,.2f}")

asyncio.run(stream_btc_liquidations())
```

### Python SDK

```python
from kamiyo_hyperliquid import KamiyoClient

# Initialize client
client = KamiyoClient(api_url="http://localhost:8000")

# Get liquidations
liquidations = client.get_liquidations(limit=10, asset="BTC-USD")

# Get statistics
stats = client.get_stats(chain="hyperliquid")

# Stream real-time data
for liquidation in client.stream_liquidations(min_amount_usd=10000):
    print(f"New liquidation: {liquidation}")
```

For complete API documentation, visit: `http://localhost:8000/docs`

## 📊 Supported Data Sources

| Source | Type | Data | Update Frequency | Status |
|--------|------|------|------------------|--------|
| 🔵 Hyperliquid API | Official | Liquidations, positions, funding | Real-time (WebSocket) | ✅ Active |
| 📂 GitHub Historical | Official | Historical liquidations, trades | Daily CSV updates | ✅ Active |
| 🐋 CoinGlass | Third-party | Whale liquidations, heatmaps | Real-time | ✅ Active |
| 🐦 Twitter/X | Social | Security announcements, alerts | Real-time | ⚠️ Optional |
| 💬 Discord/Telegram | Social | Community alerts, discussions | Real-time | ⚠️ Optional |

### Data Source Details

#### Hyperliquid Official API
- **WebSocket**: Real-time liquidation events
- **REST API**: Historical data, user positions, funding rates
- **Rate Limits**: None (public endpoints)
- **Documentation**: https://hyperliquid.xyz/docs

#### GitHub Historical Data
- **Repository**: hyperliquid-dex/historical-data
- **Format**: Daily CSV exports
- **Coverage**: Complete liquidation history since launch
- **Update Schedule**: Daily at 00:00 UTC

#### CoinGlass Analytics
- **Features**: Whale tracking, liquidation heatmaps, OI analysis
- **API**: Requires API key (optional)
- **Free Tier**: 100 requests/day
- **Paid Tier**: Unlimited requests

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

## 📚 Documentation

- **[Architecture](docs/architecture.md)**: System design, data flows, and component details
- **[API Reference](http://localhost:8000/docs)**: Interactive OpenAPI documentation
- **[CONTRIBUTING](CONTRIBUTING.md)**: Development setup and contribution guidelines
- **[SECURITY](SECURITY.md)**: Security policy and vulnerability reporting
- **[CHANGELOG](CHANGELOG.md)**: Version history and release notes
- **[CODE OF CONDUCT](CODE_OF_CONDUCT.md)**: Community guidelines

### Additional Resources

- **Examples**: See `examples/` directory for usage samples
- **Tests**: See `tests/` directory for test cases
- **Scripts**: See `scripts/` directory for utilities

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for:

- Code of Conduct
- Development setup
- Pull request process
- Coding standards
- Testing requirements

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run tests (`pytest tests/`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

### Key Points

- ✅ **Freedom to use**: Use for any purpose
- ✅ **Freedom to study**: Access to source code
- ✅ **Freedom to modify**: Make changes and improvements
- ✅ **Freedom to distribute**: Share with others
- ⚠️ **Copyleft**: Derivative works must also be GPL-3.0

For commercial licensing options, please contact us.

## 💬 Support

### Getting Help

- **📖 Documentation**: Read the [docs](docs/) directory
- **🐛 Bug Reports**: [GitHub Issues](https://github.com/mizuki-tamaki/kamiyo-hyperliquid/issues)
- **💡 Feature Requests**: [GitHub Discussions](https://github.com/mizuki-tamaki/kamiyo-hyperliquid/discussions)
- **🔒 Security Issues**: See [SECURITY.md](SECURITY.md)

### Community

- **Twitter/X**: [@KAMIYOAI](https://twitter.com/KAMIYOAI)
- **Discord**: [Join our server](https://discord.gg/kamiyo)
- **Telegram**: [@kamiyo_community](https://t.me/kamiyo_community)

### Professional Support

For commercial support, custom integrations, or consulting:
- Email: support@kamiyo.ai
- Website: https://kamiyo.ai

## 🙏 Acknowledgments

- **Hyperliquid Team**: For excellent API and historical data access
- **CoinGlass**: For comprehensive liquidation analytics
- **KAMIYO Project**: For the core aggregator framework
- **Contributors**: Thank you to all our [contributors](https://github.com/mizuki-tamaki/kamiyo-hyperliquid/graphs/contributors)

## ⭐ Star History

If you find this project useful, please consider giving it a star!

[![Star History Chart](https://api.star-history.com/svg?repos=mizuki-tamaki/kamiyo-hyperliquid&type=Date)](https://star-history.com/#mizuki-tamaki/kamiyo-hyperliquid&Date)

---

<div align="center">

**Built with ❤️ for the Hyperliquid community**

[⬆ Back to Top](#kamiyo-hyperliquid)

</div>
