# Hyperliquid Security Monitor

Real-time exploit detection for Hyperliquid DEX. Monitors HLP vault health, liquidation patterns, and oracle price deviations.

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/mizuki-tamaki/kamiyo-hyperliquid/graphs/commit-activity)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

## Overview

Independent security layer for Hyperliquid providing:

- **HLP Vault Monitor**: Detects exploitation through statistical anomaly analysis (3-sigma) and loss thresholds
- **Liquidation Analyzer**: Identifies flash loan attacks, cascade liquidations, and coordinated manipulation
- **Oracle Monitor**: Compares Hyperliquid prices against Binance/Coinbase to detect deviations

Detection latency: <5 minutes for critical events.

## Quick Start

```bash
pip install -r requirements.txt
python api/main.py
```

API available at `http://localhost:8000`

## API Endpoints

### Security Dashboard
```bash
curl http://localhost:8000/security/dashboard
```

Returns overall risk score, HLP vault health, and active oracle deviations.

### HLP Vault Health
```bash
curl http://localhost:8000/security/hlp-vault
```

Current vault metrics: TVL, 24h PnL, drawdown, anomaly score.

### Oracle Deviations
```bash
curl http://localhost:8000/security/oracle-deviations
```

Price deviations across monitored assets (BTC, ETH, SOL, MATIC, AVAX, OP, ARB).

### Security Events
```bash
curl http://localhost:8000/security/events?severity=critical&limit=10
```

Recent security events filtered by severity.

## Detection Thresholds

### HLP Vault
- **CRITICAL**: >$2M loss in 24h or >10% drawdown
- **HIGH**: >$1M loss in 24h
- **MEDIUM**: 3-sigma deviation from baseline

### Oracle
- **CRITICAL**: >1.0% price deviation sustained >30s
- **WARNING**: >0.5% price deviation sustained >30s

### Liquidation
- **Flash Loan Attack**: Large liquidation (<10s execution, >$500k)
- **Cascade**: 5+ related liquidations within 5 minutes

## Architecture

```
monitors/
  ├── hlp_vault_monitor.py     # Vault health & exploitation detection
  ├── oracle_monitor.py         # Multi-source price comparison
  └── liquidation_analyzer.py   # Liquidation pattern analysis

models/
  └── security.py               # Data models for events & metrics

api/
  └── main.py                   # FastAPI endpoints

tests/
  ├── test_production_readiness.py
  └── test_historical_hlp_incident.py
```

## Data Sources

- **Hyperliquid**: `api.hyperliquid.xyz` (vault details, prices, liquidations)
- **Binance**: `api.binance.com` (price verification)
- **Coinbase**: `api.coinbase.com` (price verification)

## Configuration

Override defaults via environment variables:

```bash
CRITICAL_LOSS_24H=2000000        # $2M
HIGH_LOSS_24H=1000000            # $1M
DRAWDOWN_CRITICAL_PCT=10.0       # 10%
ORACLE_CRITICAL_DEVIATION=1.0    # 1%
ORACLE_WARNING_DEVIATION=0.5     # 0.5%
```

## Testing

```bash
# Production readiness suite
python tests/test_production_readiness.py

# Historical incident validation (March 2025 $4M event)
python tests/test_historical_hlp_incident.py
```

All tests must pass before deployment.

## Development

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run monitors
python monitors/hlp_vault_monitor.py
python monitors/oracle_monitor.py
python monitors/liquidation_analyzer.py

# Start API
python api/main.py
```

Code style: Follow PEP 8, use type hints, maintain test coverage.

## Integration

This module integrates with the KAMIYO platform as aggregator sources #20 (HLP monitor) and #21 (Oracle monitor). See `docs/` for integration details.

## License

AGPL-3.0 with commercial restriction. See [LICENSE](LICENSE) for full terms.

**Non-commercial use:** Free under AGPL-3.0 (research, education, personal projects, non-profits <$1M revenue)

**Commercial use:** Requires separate license. Contact licensing@kamiyo.ai

## Security

Report vulnerabilities to security@kamiyo.ai. See [SECURITY.md](SECURITY.md) for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and PR guidelines.
