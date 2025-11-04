# Database Integration Summary

## Overview
Complete integration of monitoring system with PostgreSQL database for persistent data storage, historical analysis, and security event tracking.

## Components Created

### 1. Database Integration Layer (`database/integration.py`)
- **DatabaseIntegration class**: Core integration with PostgreSQL
- Methods for saving monitoring data:
  - `save_hlp_snapshot()`: Store HLP vault health snapshots
  - `save_oracle_deviation()`: Store oracle price deviations
  - `save_liquidation_pattern()`: Store liquidation patterns
  - `save_security_event()`: Create security event records
- Query methods for retrieving historical data:
  - `get_recent_hlp_snapshots()`: Retrieve HLP vault history
  - `get_oracle_deviations_by_asset()`: Get oracle deviation history
  - `get_recent_liquidation_patterns()`: Get liquidation patterns
  - `get_security_events()`: Query security events with filters
  - `get_hlp_statistics()`: Get aggregated HLP vault statistics

### 2. Monitor Database Wrapper (`monitors/database_wrapper.py`)
- **MonitorDatabaseWrapper class**: Automatic persistence wrapper for monitors
- Features:
  - Auto-saves monitoring data to database
  - Creates security events for anomalies
  - Severity-based event creation:
    - HLP anomaly score ≥ 70 → Critical event
    - Oracle deviation ≥ 1.0% → Critical event
    - Liquidation suspicion score ≥ 50 → Security event
- Can be enabled/disabled via configuration

### 3. Monitor Scheduler (`monitors/scheduler.py`)
- **MonitorScheduler class**: Periodic monitor execution
- Default intervals:
  - HLP vault checks: Every 5 minutes (300s)
  - Oracle checks: Every 1 minute (60s)
  - Liquidation checks: Every 3 minutes (180s)
- Features:
  - Concurrent execution of all monitors
  - Automatic database persistence
  - Alert integration
  - Execution statistics tracking
  - Graceful shutdown handling

### 4. Docker Scheduler Service
- Added to `docker-compose.yml` as dedicated service
- Runs monitors/scheduler.py
- Configurable via environment variables:
  ```
  HLP_CHECK_INTERVAL
  ORACLE_CHECK_INTERVAL
  LIQUIDATION_CHECK_INTERVAL
  ```
- Health checks and auto-restart

### 5. API Database Endpoints
Enhanced API with 4 new database-backed endpoints:

#### `/security/hlp-vault/history`
- Get historical HLP vault snapshots
- Parameters: `limit` (1-500)
- Returns: Historical vault health data

#### `/security/oracle-deviations/history`
- Get historical oracle deviations
- Parameters: `asset`, `hours` (1-168), `limit` (1-500)
- Returns: Price deviation history

#### `/security/liquidation-patterns`
- Get detected liquidation patterns
- Parameters: `pattern_type`, `limit` (1-200)
- Returns: Flash loan and cascade liquidation patterns

#### `/security/events/database`
- Get security events from database
- Parameters: `severity`, `threat_type`, `hours` (1-168), `limit` (1-500)
- Returns: Filtered security events

#### Enhanced `/security/dashboard`
- Now includes database statistics:
  - HLP statistics (30-day aggregates)
  - Security events count (24-hour)
  - Database availability status

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Monitor Scheduler                        │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐ │
│  │ HLP Monitor  │  │ Oracle Monitor│  │ Liq. Analyzer    │ │
│  │  (5 min)     │  │   (1 min)     │  │   (3 min)        │ │
│  └──────┬───────┘  └───────┬───────┘  └────────┬─────────┘ │
│         │                  │                    │            │
│         └──────────────────┴────────────────────┘            │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │
                             ▼
               ┌──────────────────────────┐
               │ MonitorDatabaseWrapper   │
               │ - Auto-save data         │
               │ - Create security events │
               └──────────┬───────────────┘
                          │
                          ▼
                ┌──────────────────────┐
                │ DatabaseIntegration  │
                │ - Save operations    │
                │ - Query operations   │
                └──────────┬───────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │   PostgreSQL   │
                  │  - hlp_vault_  │
                  │    snapshots   │
                  │  - oracle_     │
                  │    deviations  │
                  │  - liquidation_│
                  │    patterns    │
                  │  - security_   │
                  │    events      │
                  └────────────────┘
```

## Configuration

### Environment Variables

**Database Connection:**
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
```

**Scheduler Intervals:**
```bash
HLP_CHECK_INTERVAL=300        # HLP vault checks (seconds)
ORACLE_CHECK_INTERVAL=60      # Oracle checks (seconds)
LIQUIDATION_CHECK_INTERVAL=180 # Liquidation checks (seconds)
```

**Enable/Disable:**
```bash
# Scheduler service runs by default
# To disable database, use --no-database flag
```

## Usage

### Running the Scheduler

**Standalone:**
```bash
python monitors/scheduler.py
```

**With custom intervals:**
```bash
python monitors/scheduler.py \
  --hlp-interval 600 \
  --oracle-interval 30 \
  --liquidation-interval 120
```

**Without database:**
```bash
python monitors/scheduler.py --no-database
```

**Via Docker:**
```bash
docker-compose up scheduler
```

### Using the Database Wrapper

```python
from monitors.database_wrapper import get_monitor_db_wrapper
from monitors.hlp_vault_monitor import HLPVaultMonitor

# Initialize
db_wrapper = get_monitor_db_wrapper(enabled=True)
hlp_monitor = HLPVaultMonitor()

# Get health snapshot
health = hlp_monitor.get_current_health()

# Auto-save to database (creates security events if unhealthy)
db_wrapper.save_hlp_snapshot(health)
```

### Querying Historical Data

```python
from database.integration import get_db_integration

db = get_db_integration()

# Get recent HLP snapshots
snapshots = db.get_recent_hlp_snapshots(limit=100)

# Get oracle deviations for BTC (last 24h)
deviations = db.get_oracle_deviations_by_asset("BTC", hours=24)

# Get flash loan patterns
patterns = db.get_recent_liquidation_patterns(pattern_type="flash_loan")

# Get critical security events (last 24h)
events = db.get_security_events(severity="critical", hours=24)

# Get HLP statistics (last 30 days)
stats = db.get_hlp_statistics(days=30)
```

### API Endpoints

```bash
# Get HLP vault history
curl http://localhost:8000/security/hlp-vault/history?limit=100

# Get oracle deviations for BTC
curl http://localhost:8000/security/oracle-deviations/history?asset=BTC&hours=24

# Get liquidation patterns
curl http://localhost:8000/security/liquidation-patterns?pattern_type=flash_loan

# Get security events
curl http://localhost:8000/security/events/database?severity=critical&hours=24

# Enhanced dashboard with database stats
curl http://localhost:8000/security/dashboard
```

## Security Event Creation

The system automatically creates security events based on monitoring data:

### HLP Vault Events
- **Critical** (anomaly_score ≥ 70): Potential exploitation
- **High** (anomaly_score ≥ 50): Anomalous behavior
- **Medium** (anomaly_score < 50): Health issues

### Oracle Deviation Events
- **Critical** (deviation ≥ 1.0%): Potential manipulation
- **High** (deviation ≥ 0.5%): Significant deviation

### Liquidation Pattern Events
- **Critical**: Flash loan attacks
- **High**: Cascade liquidations (multiple users)
- **Medium**: Suspicious patterns

## Database Schema

### Tables Used
- `hlp_vault_snapshots`: HLP vault health snapshots
- `oracle_deviations`: Oracle price deviations
- `liquidation_patterns`: Detected liquidation patterns
- `security_events`: Security events and alerts

See `database/schema.sql` for complete schema.

## Benefits

1. **Historical Analysis**: Track trends over time
2. **Forensic Investigation**: Analyze past incidents
3. **Performance Metrics**: Measure monitor effectiveness
4. **Alert Context**: Enrich alerts with historical data
5. **API Access**: Query historical data via REST API
6. **Automated Monitoring**: Continuous background monitoring
7. **Security Events**: Centralized event tracking

## Testing

Integration tests available in `tests/integration/test_database_integration.py`

```bash
# Run integration tests
pytest tests/integration/test_database_integration.py -v
```

## Production Deployment

1. **Database**: Ensure PostgreSQL is running and schema is initialized
2. **Scheduler**: Start scheduler service via Docker Compose
3. **API**: API automatically connects to database on startup
4. **Monitoring**: Check logs for successful data persistence

```bash
# Full stack with monitoring
docker-compose up -d

# Check scheduler logs
docker logs kamiyo-scheduler -f

# Verify database persistence
docker exec -it kamiyo-postgres psql -U kamiyo -d kamiyo_hyperliquid \
  -c "SELECT COUNT(*) FROM hlp_vault_snapshots;"
```

## Performance Considerations

- Connection pooling: 5 connections by default
- Batch operations where possible
- Indexes on timestamp and foreign keys
- Automatic cleanup of old data (30-day retention)
- Graceful degradation if database unavailable

## Future Enhancements

- [ ] Real-time event streaming via WebSocket
- [ ] Advanced analytics and anomaly detection
- [ ] Machine learning model training on historical data
- [ ] Grafana dashboards for visualization
- [ ] Automated incident response workflows
- [ ] Data export/archival for compliance

---

**Status**: ✅ Complete and Operational
**Last Updated**: 2025-11-04
**Version**: 2.0.0
