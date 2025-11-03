# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-03-15

### Added
- HLP vault health monitoring with statistical anomaly detection
- Oracle price deviation tracking (Binance, Coinbase comparison)
- Liquidation pattern analyzer for flash loan and cascade detection
- FastAPI endpoints for security metrics and events
- Production test suite with historical incident validation
- Integration with KAMIYO aggregation platform

### Security
- Implemented 3-sigma statistical thresholds for anomaly detection
- Multi-source price verification to prevent oracle manipulation
- Real-time monitoring with <5 minute detection latency

### Documentation
- API endpoint reference
- Architecture overview
- Contributing guidelines
- Security policy

## [0.1.0] - 2025-03-01

### Added
- Initial project structure
- Base aggregator framework
- Security data models
- Basic monitoring capabilities
