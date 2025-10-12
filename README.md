# MLB Kalshi Latency Arbitrage Trader

High-performance trading system for exploiting ~2 second delays in Kalshi MLB markets by watching games live in person.

## Features

✅ **FastKalshiClient** - <500ms execution latency with persistent connections
✅ **Auto token refresh** - No manual re-authentication during games
✅ **Mobile-optimized UI** - Large touch buttons for stadium use
✅ **Real-time prices** - Updates every 1 second
✅ **Orderbook depth** - Liquidity checks before every trade
✅ **One-tap execution** - BUY YES, BUY NO, SELL YES, SELL NO
✅ **Position size presets** - 500, 1000, 1500, 2000, 3000, 5000 contracts
✅ **Execution tracking** - Monitor latency per trade
✅ **Session stats** - Track trades, avg latency, fastest/slowest

## Quick Start

### 1. Install Dependencies

```bash
cd mlb_kalshi
pip install -r requirements.txt
```

### 2. Configure Credentials

Create `.env` file:

```bash
KALSHI_EMAIL=your_email@example.com
KALSHI_PASSWORD=your_password
KALSHI_API_BASE=https://trading-api.kalshi.com/trade-api/v2
```

### 3. Run Server

```bash
python server.py
```

Server starts on `http://localhost:5000`

### 4. Access from Phone

Find your computer's IP address:

**Windows:**
```bash
ipconfig
```

**Mac/Linux:**
```bash
ifconfig
```

Then open `http://YOUR_IP:5000` on your phone browser.

## Pre-Game Checklist

### 24 Hours Before Game

1. ✅ Find MLB game market ticker on Kalshi
2. ✅ Verify market has good liquidity (>2000 contracts volume)
3. ✅ Test server and authentication
4. ✅ Charge all devices to 100%

### At Stadium (2-3 Hours Before First Pitch)

1. ✅ Test stadium WiFi AND mobile data
2. ✅ Run speed test (target: >5 Mbps, <100ms ping)
3. ✅ Open trading UI on phone/laptop
4. ✅ Authenticate to Kalshi
5. ✅ Set market ticker
6. ✅ Verify prices updating correctly
7. ✅ Place 1-2 small test trades (25-50 contracts)
8. ✅ Confirm battery >80%

## How to Use

### Setup Phase

1. **Authenticate** - Click "Authenticate to Kalshi" button
2. **Set Ticker** - Enter market ticker (e.g., `KXMLB-24NY-B`)
3. **Wait for prices** - UI will start showing live YES/NO prices

### Trading Phase

1. **Witness event** - See run scored or major play
2. **Select position size** - Tap preset (default: 1500)
3. **Execute** - Tap BUY YES / BUY NO within 1 second
4. **Wait 5-20 seconds** - Watch for price movement
5. **Exit** - Tap SELL YES / SELL NO when target hit
6. **Repeat** - Wait 10-30 seconds, then repeat

### Between Innings

- Review session stats
- Check battery level
- Verify internet connection
- Reset focus for next inning

## Critical Performance Targets

- **Execution latency**: <500ms (shown in UI)
- **Hold time**: 5-20 seconds per trade
- **Profit target**: 3-7¢ per contract
- **Stop loss**: -2¢ per contract
- **Max trades per game**: 8 trades

## Risk Management

### Per-Trade Limits
- Max position size: 5,000 contracts
- Max position value: 30% of account balance
- Max loss per trade: -$200 or -2% of account

### Per-Game Limits
- Max trades: 8
- Max loss: -$500 or -5% of account
- Stop after 3 consecutive losses

### Daily Limits
- Max loss per day: -$1,000 or -10% of account

## Troubleshooting

### Slow Execution (>500ms)
- Switch from WiFi to mobile data (or vice versa)
- Reduce position sizes by 50%
- If persists >2 seconds, stop trading (edge is gone)

### Authentication Errors
- Token auto-refreshes every 25 minutes
- If manual refresh needed, do between innings
- Never trade while auth status uncertain

### Low Liquidity Warning
- Check orderbook depth before trade
- Only trade if >500 contracts available
- Reduce position size to match liquidity

### Battery <50%
- Connect portable charger immediately
- Reduce screen brightness
- Close unnecessary apps

### Battery <20%
- Close all positions
- Stop trading
- Conserve battery

## Files

- `kalshi_client.py` - High-performance Kalshi API client
- `server.py` - Flask REST API server
- `templates/index.html` - Mobile-optimized trading UI
- `rules.md` - Complete strategy documentation
- `requirements.txt` - Python dependencies
- `.env` - Credentials (you create this)

## Technology Stack

- **Backend**: Python + Flask
- **Client**: kalshi-python SDK (modified for speed)
- **Frontend**: Vanilla JS (no frameworks = faster)
- **Design**: Mobile-first, touch-optimized

## Success Metrics

### Good Performance
- P&L: $200-$400 per game
- Win rate: 60-70%
- Avg latency: <500ms
- 4-6 trades executed

### Excellent Performance
- P&L: $500-$1,000 per game
- Win rate: 70-80%
- Avg latency: <400ms
- 5-8 trades executed
- All trades within risk limits

## Security

- Never commit `.env` file (use `.env.example` as template)
- Use HTTPS only
- Log out after each game
- Don't share credentials

## Legal & Ethical

- Only trade from jurisdictions where Kalshi is legal
- This is information arbitrage (legal and ethical)
- You're faster than their data feed (no manipulation)
- Report all profits for tax purposes
- Follow Kalshi Terms of Service

## Support

See [rules.md](rules.md) for complete strategy documentation including:
- Detailed trading rules
- Entry/exit criteria
- Position sizing formulas
- Risk management protocols
- Pre-game preparation
- Post-game analysis templates

---

**Remember:** This strategy exploits Kalshi's ~2 second API delay. If they speed up their feed, your edge disappears. Trade it while it lasts!

*Speed + Size + Discipline = Profit*
