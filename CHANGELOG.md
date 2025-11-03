# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- ML-based liquidation prediction
- Historical analysis dashboards
- Advanced filtering and search
- Export to CSV/JSON
- Email/SMS alerts for large liquidations
- Integration with DeFi analytics platforms

## [1.0.0] - 2025-11-03

### Added
- Initial release of KAMIYO Hyperliquid
- Base aggregator framework
- Hyperliquid Official API aggregator
  - Exploit detection from liquidation patterns
  - Metadata and price feed endpoints
  - Support for mainnet and testnet
- GitHub Historical Data aggregator
  - Historical liquidation analysis
  - Mass liquidation detection
  - Trade data fetching
- FastAPI REST API server
  - GET /exploits endpoint with filtering
  - GET /stats endpoint for statistics
  - GET /meta endpoint for Hyperliquid metadata
  - GET /health endpoint for health checks
- CORS middleware support
- In-memory caching (5-minute TTL)
- Comprehensive documentation
  - README with architecture diagrams
  - CONTRIBUTING guidelines
  - CODE_OF_CONDUCT
  - SECURITY policy
  - Architecture documentation
- GPL-3.0 license
- Python 3.11+ support
- Type hints throughout codebase
- Logging infrastructure

### Technical Details
- FastAPI 0.115.0
- Python 3.11+
- Async/await pattern
- Type safety with type hints
- Comprehensive error handling

### Data Sources
- Hyperliquid Official API (real-time)
- GitHub Historical Data (daily updates)

### API Features
- Query filtering by chain, amount, date range
- Pagination support (1-500 results)
- JSON response format
- Cache-aware responses
- Error handling with HTTP status codes

### Security
- Input validation on all endpoints
- Rate limiting ready
- CORS configuration
- Secure headers support
- No hardcoded credentials

## [0.1.0] - 2025-10-28

### Added
- Project initialization
- Repository structure
- Development environment setup

---

## Release Notes

### Version 1.0.0 - Initial Release

KAMIYO Hyperliquid v1.0.0 is the first stable release of our Hyperliquid-focused exploit intelligence aggregator.

**Highlights:**
- Production-ready exploit aggregation from Hyperliquid ecosystem
- REST API with comprehensive filtering options
- Real-time data from official Hyperliquid API
- Historical analysis from GitHub data repository
- Extensible aggregator architecture for future data sources

**Getting Started:**
```bash
git clone https://github.com/mizuki-tamaki/kamiyo-hyperliquid.git
cd kamiyo-hyperliquid
pip install -r requirements.txt
python api/main.py
```

**Documentation:**
- [README](README.md) - Project overview and quick start
- [CONTRIBUTING](CONTRIBUTING.md) - Contribution guidelines
- [SECURITY](SECURITY.md) - Security policy
- [Architecture](docs/architecture.md) - System architecture

**Community:**
- GitHub Issues: https://github.com/mizuki-tamaki/kamiyo-hyperliquid/issues
- Email: info@kamiyo.ai

---

## Migration Guides

### Upgrading to 1.0.0

This is the initial release - no migration needed.

---

## Deprecation Notices

None at this time.

---

## Known Issues

### Version 1.0.0
- In-memory cache does not persist across restarts (use Redis in production)
- Large liquidation detection is placeholder (requires production tuning)
- WebSocket streaming not yet implemented
- No authentication on API endpoints

See [GitHub Issues](https://github.com/mizuki-tamaki/kamiyo-hyperliquid/issues) for full list.

---

## Versioning Policy

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

### Pre-release Versions
- **Alpha** (x.y.z-alpha.n): Early development, unstable
- **Beta** (x.y.z-beta.n): Feature complete, testing phase
- **RC** (x.y.z-rc.n): Release candidate, final testing

---

## Support

Each major version is supported for:
- **Security fixes**: 12 months after next major release
- **Bug fixes**: 6 months after next major release
- **Feature updates**: Only in current major version

---

## Links

- [GitHub Repository](https://github.com/mizuki-tamaki/kamiyo-hyperliquid)
- [Issue Tracker](https://github.com/mizuki-tamaki/kamiyo-hyperliquid/issues)
- [Documentation](https://docs.kamiyo.ai/hyperliquid)
- [KAMIYO Main Project](https://github.com/mizuki-tamaki/kamiyo)
