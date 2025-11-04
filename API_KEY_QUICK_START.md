# API Key Quick Start Guide

**3-minute setup for API authentication**

## Step 1: Generate Keys (30 seconds)

```bash
python api/auth.py
```

Copy the output keys.

## Step 2: Configure (1 minute)

Add to `.env`:

```bash
API_KEY_ENABLED=true
API_KEYS="your_key_1,your_key_2,your_key_3"
```

## Step 3: Restart (30 seconds)

```bash
docker-compose restart api
```

## Step 4: Test (1 minute)

### Without Key (Fails):
```bash
curl http://localhost:8000/security/dashboard
```

### With Key (Works):
```bash
curl -H "X-API-Key: YOUR_KEY_HERE" \
  http://localhost:8000/security/dashboard
```

## Usage Examples

### Bash/cURL
```bash
curl -H "X-API-Key: YOUR_KEY" http://localhost:8000/security/dashboard
```

### Python
```python
import requests

headers = {"X-API-Key": "YOUR_KEY"}
response = requests.get("http://localhost:8000/security/dashboard", headers=headers)
print(response.json())
```

### JavaScript
```javascript
fetch('http://localhost:8000/security/dashboard', {
  headers: {'X-API-Key': 'YOUR_KEY'}
})
.then(r => r.json())
.then(data => console.log(data));
```

### Query Parameter (Alternative)
```bash
curl "http://localhost:8000/security/dashboard?api_key=YOUR_KEY"
```

## Common Tasks

### Disable Authentication
```bash
# .env
API_KEY_ENABLED=false
```

### Add New Key
```bash
# Generate new key
python api/auth.py

# Add to .env (append to existing keys)
API_KEYS="old_key_1,old_key_2,NEW_KEY_3"

# Restart
docker-compose restart api
```

### Revoke Key
```bash
# Remove from .env
API_KEYS="keep_key_1,keep_key_2"  # removed revoked_key

# Restart
docker-compose restart api
```

## Protected Endpoints

These require API key when auth is enabled:
- `/security/dashboard` - Security overview
- `/security/hlp-vault` - HLP vault health
- `/security/oracle-deviations` - Oracle deviations
- `/security/liquidation-patterns` - Liquidation analysis
- `/security/events` - Security events

## Public Endpoints

These are always public (no key needed):
- `/` - API info
- `/health` - Health check
- `/exploits` - Public exploits
- `/stats` - Statistics

## Troubleshooting

**"Missing API key"** → Add key to request header/query

**"Invalid API key"** → Check key matches exactly (no typos, spaces)

**Still not working?** → Verify:
1. `API_KEY_ENABLED=true` in `.env`
2. API server restarted after config change
3. Key is in `API_KEYS` list

## Full Documentation

See `docs/AUTHENTICATION.md` for complete guide.

## Security Tips

✅ **Do:**
- Use HTTPS in production
- Store keys in environment variables
- Revoke unused keys immediately
- Generate unique keys per client

❌ **Don't:**
- Commit keys to git
- Share keys in plaintext
- Reuse keys across environments
- Hard-code keys in code
