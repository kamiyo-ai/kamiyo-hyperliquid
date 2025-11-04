# Getting Started with KAMIYO Hyperliquid

The fastest way to start monitoring Hyperliquid security.

## 🚀 Quick Start (3 Minutes)

### Option 1: Automated Setup (Recommended)

```bash
# Run the quick-start script
./scripts/quick-start.sh
```

That's it! The script will:
- ✅ Check dependencies
- ✅ Generate secure passwords
- ✅ Start all services
- ✅ Initialize the database
- ✅ Run health checks

### Option 2: Manual Docker Setup

```bash
# 1. Configure environment
cp .env.example .env
nano .env  # Edit as needed

# 2. Start services
docker-compose up -d

# 3. Initialize database
docker-compose exec api python -c "from database import init_database; init_database(create_tables=True)"

# 4. Check health
curl http://localhost:8000/health
```

### Option 3: Using Makefile

```bash
# See all available commands
make help

# Quick start production environment
make quick-start

# Or start manually
make docker-up
make db-init
make health
```

---

## 📋 Prerequisites

**Required:**
- Docker 24.0+
- Docker Compose 2.0+

**OR for manual setup:**
- Python 3.9+
- PostgreSQL 14+
- Redis 7+ (optional)

---

## 🔧 Configuration

### Essential Settings

Edit `.env` file:

```bash
# Database (auto-generated secure password)
DATABASE_URL=postgresql://kamiyo:your_password@localhost:5432/kamiyo_hyperliquid

# API Security
ALLOWED_ORIGINS=https://yourdomain.com  # Change from * in production!
RATE_LIMIT=60/minute

# Monitoring Thresholds
CRITICAL_LOSS_24H=2000000     # $2M triggers critical alert
ORACLE_CRITICAL_DEVIATION=1.0  # 1% price deviation = critical
```

### Optional Alerts

```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Discord
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Webhook
WEBHOOK_URL=https://your-server.com/alerts
```

---

## 🎯 First Steps After Setup

### 1. Verify Everything is Running

```bash
# Check services
docker-compose ps

# Should see:
# - postgres (healthy)
# - redis (healthy)
# - api (healthy)
```

### 2. Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health | jq

# Security dashboard
curl http://localhost:8000/security/dashboard | jq

# HLP vault status
curl http://localhost:8000/security/hlp-vault | jq

# Oracle deviations
curl http://localhost:8000/security/oracle-deviations | jq
```

### 3. Access Web Interfaces

- **API Documentation:** http://localhost:8000/docs
- **Grafana (if started):** http://localhost:3000
- **Prometheus (if started):** http://localhost:9090
- **PgAdmin (if started):** http://localhost:5050

### 4. View Logs

```bash
# API logs
make logs

# All services
make logs-all

# Or directly
docker-compose logs -f api
```

---

## 📊 Understanding the Dashboard

### Security Dashboard (`/security/dashboard`)

Returns:
```json
{
  "overall_risk": {
    "score": 15.2,
    "level": "LOW"
  },
  "hlp_vault": {
    "is_healthy": true,
    "anomaly_score": 0.0,
    "account_value": 577023004.33,
    "pnl_24h": 1017239.90
  },
  "oracle_monitoring": {
    "active_deviations": 0,
    "deviations": []
  }
}
```

**Risk Levels:**
- **0-30:** 🟢 LOW - Normal operations
- **30-50:** 🟡 MEDIUM - Monitor closely
- **50-70:** 🟠 HIGH - Potential threat
- **70-100:** 🔴 CRITICAL - Active threat

### HLP Vault Health (`/security/hlp-vault`)

Monitors the Hyperliquid liquidity provider vault for:
- Large losses (>$1M = high, >$2M = critical)
- Statistical anomalies (3-sigma deviation)
- Excessive drawdowns (>10% from peak)
- Performance metrics (Sharpe ratio, win rate)

### Oracle Deviations (`/security/oracle-deviations`)

Cross-checks Hyperliquid prices against:
- Binance
- Coinbase

Alerts on:
- >0.5% deviation for >30 seconds = warning
- >1.0% deviation = critical

---

## 🛠️ Common Tasks

### View Database

```bash
# Open PostgreSQL shell
make db-shell

# List all tables
\dt

# Query HLP vault snapshots
SELECT * FROM hlp_vault_snapshots ORDER BY timestamp DESC LIMIT 10;

# Query security events
SELECT event_id, severity, title, timestamp FROM security_events ORDER BY timestamp DESC;
```

### Backup Database

```bash
# Create backup
make db-backup

# Backups saved to backups/backup_YYYYMMDD_HHMMSS.dump
```

### Monitor Performance

```bash
# Start monitoring stack
make monitoring

# Access Grafana
make grafana

# Access Prometheus
make prometheus
```

### Update Configuration

```bash
# Edit .env
nano .env

# Restart to apply changes
make restart-all
```

---

## 🔍 Monitoring in Action

### Example: Detecting HLP Vault Issues

```bash
# 1. Check current health
curl http://localhost:8000/security/hlp-vault | jq '.health_status'

# 2. If anomaly detected:
{
  "is_healthy": false,
  "anomaly_score": 75.5,
  "health_issues": ["Large loss detected: $2.5M in 24h"]
}

# 3. Check security events
curl http://localhost:8000/security/events?severity=critical | jq

# 4. Review recent exploits
curl http://localhost:8000/exploits?days=1 | jq
```

### Example: Oracle Price Deviation

```bash
# Monitor for price manipulation
curl http://localhost:8000/security/oracle-deviations | jq

# If deviation found:
{
  "deviations": [{
    "asset": "BTC",
    "hyperliquid_price": 43250.00,
    "binance_price": 42800.00,
    "max_deviation_pct": 1.05,
    "duration_seconds": 45,
    "is_dangerous": true,
    "risk_score": 85
  }]
}
```

---

## 📈 Production Deployment

For production deployment, see **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** for:
- SSL/TLS setup
- Nginx configuration
- Security hardening
- Scaling strategies
- Monitoring integration
- Backup automation

---

## 🆘 Troubleshooting

### API Not Starting

```bash
# Check logs
make logs

# Common fixes:
# 1. Port 8000 in use
make port-check

# 2. Database not ready
docker-compose restart postgres
sleep 10
docker-compose restart api

# 3. Missing dependencies
make install
```

### Database Connection Issues

```bash
# Check database status
docker-compose exec postgres pg_isready -U kamiyo

# Reinitialize database
make db-init

# Check connection string in .env
echo $DATABASE_URL
```

### "No data" in Dashboard

```bash
# The monitors fetch data on demand
# First request may be slow
# Try again after 30 seconds

# Force data refresh
curl http://localhost:8000/security/hlp-vault
curl http://localhost:8000/security/oracle-deviations
```

---

## 🎓 Next Steps

### 1. Customize Thresholds

Edit `.env` to adjust detection sensitivity:

```bash
# More sensitive (catch smaller issues)
CRITICAL_LOSS_24H=1000000
ORACLE_CRITICAL_DEVIATION=0.5

# Less sensitive (only major issues)
CRITICAL_LOSS_24H=5000000
ORACLE_CRITICAL_DEVIATION=2.0
```

### 2. Set Up Alerts

Configure notification channels in `.env`:

```bash
# Get Telegram bot token
# 1. Talk to @BotFather on Telegram
# 2. Create new bot
# 3. Copy token to TELEGRAM_BOT_TOKEN

# Get chat ID
# 1. Send message to your bot
# 2. Visit: https://api.telegram.org/bot<YourBOTToken>/getUpdates
# 3. Copy chat.id to TELEGRAM_CHAT_ID
```

### 3. Integrate with Your Stack

```python
# Use as a library
from kamiyo_hyperliquid import HLPVaultMonitor

monitor = HLPVaultMonitor()
health = monitor.get_current_health()

if not health.is_healthy:
    send_alert(f"HLP Vault Issue: {health.health_issues}")
```

### 4. Add Monitored Addresses

For liquidation tracking, add addresses to monitor:

```bash
# In .env
MONITORED_ADDRESSES=0x123abc...,0x456def...,0x789ghi...
```

---

## 📚 Additional Resources

- **Full Documentation:** [README.md](README.md)
- **Deployment Guide:** [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- **Implementation Details:** [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Critical Fixes:** [🔴 CRITICAL_ISSUES_POTENTIAL_ERRORS.md](🔴%20CRITICAL_ISSUES_POTENTIAL_ERRORS.md)

---

## 💡 Pro Tips

1. **Monitor your monitoring:** Set up alerts to notify if the API itself goes down
2. **Baseline period:** Run for 30+ days to establish accurate statistical baselines
3. **Test alerts:** Manually trigger test alerts to verify notification channels work
4. **Regular backups:** Schedule daily database backups (see `make db-backup`)
5. **Update regularly:** Check for updates weekly: `git pull && make docker-rebuild`

---

## 🚀 You're Ready!

Your KAMIYO Hyperliquid Security Monitor is now running and watching for:
- ✅ HLP vault exploitation
- ✅ Oracle price manipulation
- ✅ Liquidation cascades
- ✅ Flash loan attacks
- ✅ Statistical anomalies

**Happy monitoring!** 🛡️

For questions or issues: https://github.com/mizuki-tamaki/kamiyo-hyperliquid/issues
