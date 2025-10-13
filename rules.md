# MLB High-Volume Latency Arbitrage - Project Rules

## Project Goal
Execute high-volume, fast-turnover arbitrage trades on Kalshi MLB markets by exploiting the ~2 second delay between live in-person game events and Kalshi's price updates. Manually buy large positions immediately after witnessing events, then sell once the MLB API and retail traders catch up, repeating this process for multiple events throughout the game.

## Core Strategy

### The Edge
- **Your advantage**: Watching live MLB games in person (fastest "feed" possible)
- **Kalshi's delay**: ~2 seconds for MLB API to update and prices to adjust
- **Profit window**: Execute large buy → hold 5-20 seconds → sell at profit
- **Repeatable**: Trade multiple scoring events per game

### Trading Cycle
1. **Witness event live** (run scored, momentum shift)
2. **Buy large position** (1000-3000 contracts) within 1 second
3. **Hold position** (5-20 seconds while market updates)
4. **Sell entire position** (take 3-7¢ profit)
5. **Wait for cooldown** (10-30 seconds)
6. **Repeat** for next event

### Event-to-Trade Mapping
| Live Event | Action | Expected Price Move | Position Size |
|------------|--------|---------------------|---------------|
| Home team scores run | BUY YES | +5-8¢ | 1500-3000 |
| Away team scores run | BUY NO | +5-8¢ | 1500-3000 |
| Big defensive play (home) | BUY YES | +2-4¢ | 1000-2000 |
| Momentum swing | Context dependent | +2-5¢ | 1000-1500 |
| Clear win probability shift | Context dependent | +3-6¢ | 1500-2500 |

## Technical Principles

### 1. Speed is Critical
- **Target execution time**: <500ms from decision to order placed
- **Maximum acceptable latency**: 1000ms total (click to fill)
- Use persistent API connections (stay authenticated throughout game)
- Pre-load market ticker before first pitch
- Use aggressive limit orders (current price + 3¢) for guaranteed fills
- Keep UI minimal and touch-optimized for stadium use

### 2. Position Sizing Strategy

**Position Accountability Level (PAL):**
- Kalshi uses Position Accountability Levels, not hard limits
- PAL for MLB markets: **$25,000 per strike, per member**
- This is a monitoring threshold where Kalshi may review your activity
- You can exceed PAL with justification

**Practical Position Sizing:**

Size based on your risk tolerance, account balance, and market liquidity.

**Example Position Sizes:**
- Small: 500-1,000 contracts
- Medium: 1,000-2,000 contracts
- Standard: 1,500-3,000 contracts
- Large: 2,000-5,000 contracts
- X-Large: 3,000-10,000 contracts
- Very Large: 10,000+ contracts

**Size Presets (Configure in UI):**
- Small: 500 contracts
- Medium: 1,000 contracts
- Standard: 1,500 contracts
- Large: 2,000 contracts
- X-Large: 3,000 contracts
- Very Large: 5,000 contracts
- Custom: Any amount you specify

### 3. Entry Rules
- **Only trade what you personally witness** - no trading on scoreboard delays
- **Verify clear line of sight** to the play before executing
- **Check orderbook depth** - ensure at least 300-500 contracts available
- **Confirm good internet connection** before each trade (>3 bars)
- **Phone/laptop battery >50%** before executing large trades
- **Wait for cooldown period** (10-30 seconds) between trades

### 4. Exit Rules

**Primary Exit Strategy: Fast Flip**
- **Hold time**: 5-20 seconds (just until Kalshi updates)
- **Profit target**: 3-7¢ per contract
- **Minimum acceptable**: +2¢ per contract
- **Maximum hold**: 30 seconds (force exit regardless)

**Exit Triggers:**
- ✅ **Profit target hit**: Price moves +5¢ → SELL immediately
- ✅ **Acceptable profit**: Price moves +3¢ after 10 seconds → SELL
- ✅ **Stop loss**: Price moves -2¢ → SELL immediately  
- ✅ **Max hold time**: 30 seconds elapsed → SELL at market
- ✅ **End of inning**: Close all positions between innings

**Exit Execution:**
- Use aggressive sell orders (current price - 2¢) for fast fills
- Sell entire position at once (no partial exits)
- Accept small slippage for guaranteed execution speed

## Risk Management

### Risk Guidelines

**Per-Trade Guidelines:**
- Position size: Based on your risk tolerance and account size
- Stop loss trigger: -2¢ price move against you (recommended)
- Monitor position value relative to account balance

**Per-Game Guidelines:**
- Monitor cumulative losses throughout the game
- Consider stopping after losing 3 trades in a row
- Adjust position sizes based on performance

**Per-Day Guidelines:**
- Track daily P&L
- Consider stopping if experiencing significant losses
- Take breaks if feeling emotional or stressed

### Position Accountability Management

**PAL Monitoring:**
```
Current Position Value = Contracts × Entry Price
PAL Usage = Position Value ÷ $25,000
```

**PAL Awareness:**
- Monitor your position value relative to the $25K PAL threshold
- Understand that Kalshi may review activity approaching or exceeding PAL
- Be prepared to explain your strategy if contacted
- Consider your risk tolerance when sizing positions

**Multiple Position Rule:**
- If holding multiple positions across different strikes, sum all position values
- Monitor total exposure across all positions

### Pre-Trade Checks (Every Single Trade)
- [ ] Clear view of what just happened on field
- [ ] Current orderbook has sufficient liquidity for your position size
- [ ] Position size appropriate for your risk tolerance
- [ ] No existing position open (or ready to close existing first)
- [ ] Internet connection strong (test: can you load prices quickly?)
- [ ] Cooldown period elapsed (>10 seconds since last trade)
- [ ] Device battery >40%

### Prohibited Actions
- ❌ Trading on crowd reactions without seeing the play yourself
- ❌ Revenge trading after losses (increasing size to "get even")
- ❌ Adding to losing positions (no averaging down)
- ❌ Trading while distracted, emotional, or intoxicated
- ❌ Trading without verifying sufficient orderbook liquidity
- ❌ Holding positions past 30 seconds (must flip fast)
- ❌ Trading in multiple games simultaneously (focus on one)

## Pre-Game Preparation

### 24-48 Hours Before Game

**Market Research:**
1. Find game on Kalshi and identify exact market ticker
2. Verify market has good liquidity (>2,000 contracts total volume)
3. Check current odds and implied win probabilities
4. Research: teams, starting pitchers, weather, injuries, recent form
5. Estimate likely number of scoring opportunities (typical: 4-8 runs per game)

**Account Preparation:**
1. Ensure Kalshi account funded with sufficient capital
2. Decide on position sizes based on your risk tolerance
3. Verify no pending withdrawals or account restrictions
4. Check transaction history to ensure API access working

**Technical Testing:**
1. Test API execution speed from your location (target: <500ms)
2. Verify authentication tokens are fresh
3. Test mobile/laptop internet speed at home
4. Charge all devices to 100%
5. Download offline copy of market ticker (in case of connectivity issues)

### 2-3 Hours Before First Pitch

**Stadium Arrival:**
1. Arrive early to find optimal seat (clear field view, good connectivity)
2. Test stadium WiFi AND mobile data (use fastest)
3. Run speed test: aim for >5 Mbps download, <100ms ping
4. Find power outlet if available, or position portable charger

**System Setup:**
1. Launch trading app on phone or laptop
2. Authenticate to Kalshi API (verify successful login)
3. Set active market ticker in UI
4. Load current orderbook and verify prices displaying correctly
5. Test 1-2 small practice trades (25-50 contracts) to verify execution
6. Configure position size presets based on your preferences

**Final Checks:**
1. Verify UI is responsive and buttons work smoothly
2. Check device battery: should be >80% before first pitch
3. Position portable charger within easy reach
4. Silence all notifications (no distractions during game)
5. Have backup plan ready (paper trading if tech fails)

### First Pitch Checklist
- [ ] Trading interface open and functional on device
- [ ] Market ticker set and displaying live prices
- [ ] Position size configured (default to 1,500-2,000 contracts)
- [ ] Current YES/NO prices visible and updating
- [ ] Clear view of entire baseball field
- [ ] Phone on silent mode (vibrate off)
- [ ] Portable charger connected or nearby
- [ ] Water and snacks available (stay focused, not distracted)
- [ ] Mental state: calm, focused, patient
- [ ] Ready to execute first trade within 500ms of witnessing event

## During Game Protocol

### Monitoring Between Plays
- **Primary focus**: Watch the game, not the screen
- **Price checks**: Glance at prices every 30-60 seconds during play
- **Position awareness**: Always know if you have an open position
- **Timing awareness**: Track Kalshi's update speed (is it consistent ~2 seconds?)
- **Liquidity monitoring**: Check orderbook depth periodically

### Execution Sequence (Per Event)

**Phase 1: Event Recognition (0-2 seconds)**
1. Witness scoring event or major play
2. Instant assessment: Is this clearly tradeable? (Yes/No decision in <1 second)
3. Determine direction: Will this move YES up or NO up?

**Phase 2: Entry Execution (2-3 seconds)**
1. Tap BUY button (YES or NO)
2. Confirm order submission
3. Verify fill notification
4. Note entry time mentally

**Phase 3: Position Monitoring (3-20 seconds)**
1. Watch price updates on screen
2. Track unrealized P&L
3. Watch for profit target (+5¢) or stop loss (-2¢)
4. Do NOT look away from device during this phase

**Phase 4: Exit Execution (At profit target or time limit)**
1. Tap SELL button for same side
2. Confirm order submission  
3. Verify exit fill
4. Check realized P&L

**Phase 5: Cooldown & Reset (20-30 seconds)**
1. Log mental note of trade outcome
2. Reset focus to watching game
3. Wait for cooldown period before next trade
4. Breathe and stay calm

### Between Innings (Critical Reset Period)

**Position Management:**
- Close ALL open positions at end of each inning (no exceptions)
- Review P&L for last inning
- Check total session P&L

**Technical Checks:**
- Verify internet connection still strong
- Check device battery level
- Re-authenticate to API if needed (tokens expire every 30 minutes)
- Confirm orderbook still has good liquidity

**Mental Reset:**
- Take 2-3 deep breaths
- Stretch if needed
- Assess emotional state: still calm and focused?
- Review: Did last inning's trades follow the rules?
- If 2+ losing trades in a row: consider reducing size or stopping

**Strategic Assessment:**
- Is Kalshi's update delay still consistent?
- Are retail traders becoming faster (narrowing your edge)?
- Is game still competitive (more trading opportunities)?
- Should you adjust position sizing based on results so far?

### End of Game Protocol

**Final Innings (8th-9th):**
- Reduce position sizes by 50% (higher volatility, less predictable)
- More conservative entry (only trade obvious scoring events)
- Tighter stop losses (-1¢ instead of -2¢)
- Close ALL positions before final out (no holding through settlement)

**After Final Out:**
1. Verify all positions closed
2. Check Kalshi account balance
3. Calculate total session P&L
4. Verify no pending orders still active
5. Log out of API properly

## Post-Game Analysis

### Immediate (Within 30 Minutes After Game)

**Trade Review:**
1. Count total trades executed
2. Calculate win rate (profitable trades ÷ total trades)
3. Calculate total P&L for the session
4. Identify best trade (highest profit)
5. Identify worst trade (largest loss)

**Performance Metrics:**
- Average execution time (goal: <500ms)
- Average hold time (goal: 10-15 seconds)
- Average profit per winning trade (goal: $100+)
- Average loss per losing trade (should be <$50)

### Within 24 Hours (Detailed Analysis)

**Trade-by-Trade Breakdown:**

For each trade, record:
- Timestamp and inning
- Event type (e.g., "home team scored run")
- Side traded (YES or NO)
- Position size (contracts)
- Entry price and exit price
- Price move (in cents)
- Hold time (seconds)
- P&L (dollars)
- Exit reason (profit target, stop loss, time limit)
- Execution time (milliseconds)

**Trading Journal Entry Template:**
```
Date: [Date]
Game: [Away Team] @ [Home Team]
Final Score: [Score]
Market Ticker: [Ticker]

PERFORMANCE SUMMARY:
Total Trades: [X]
Winning Trades: [Y] ([Y/X]% win rate)
Losing Trades: [Z]
Session P&L: $[XXX.XX]

TRADE DETAILS:
[List each trade with above metrics]

EXECUTION QUALITY:
Avg Entry Time: [XXX]ms
Avg Hold Time: [XX]s
Fastest Trade: [XXX]ms
Slowest Trade: [XXX]ms

BEST TRADE:
[Event, size, P&L, why it worked]

WORST TRADE:
[Event, size, P&L, what went wrong]

LESSONS LEARNED:
1. [Key takeaway]
2. [Pattern noticed]
3. [Rule to add/modify]

STRATEGY ADJUSTMENTS:
[Any changes to make for next game]

TECHNICAL ISSUES:
[Any latency, connectivity, or execution problems]

EMOTIONAL STATE:
[How did you feel during trading? Calm? Stressed?]

NEXT GAME PLAN:
[Specific focus areas for improvement]
```

### Weekly Review (Every 3-5 Games)

**Aggregate Statistics:**
- Total games traded: [X]
- Total trades executed: [Y]
- Overall win rate: [Z]%
- Total P&L: $[XXX]
- Average P&L per game: $[XX]
- Best game: $[XXX]
- Worst game: $[XXX]

**Pattern Analysis:**
- Which event types most profitable? (home runs, specific innings, etc.)
- Which position sizes worked best?
- What time of day/week performed best?
- Any correlation between teams, pitchers, or game conditions?

**Edge Assessment:**
- Is Kalshi's delay still consistent at ~2 seconds?
- Are retail traders getting faster?
- Is your edge narrowing or stable?
- Should you adjust strategy based on data?

### Monthly Review

**Profitability Analysis:**
- Monthly P&L: $[XXXX]
- Games attended: [X]
- P&L per game: $[XX]
- Total capital deployed: $[XXXX]
- Return on capital: [X]%
- Comparison to monthly goal

**Risk Analysis:**
- Largest single loss: $[XX]
- Largest drawdown: $[XX]
- Number of stop-loss triggers: [X]
- Position size adherence: [X]% of trades within limits
- PAL proximity: Did you exceed 60% at any point?

**Strategy Evolution:**
- What worked well this month?
- What didn't work?
- Should position sizes change?
- Should profit targets adjust?
- Any new event types to trade or avoid?
- Technical improvements needed?

**Update This Document:**
- Add new rules based on learnings
- Modify position sizes if account grew/shrunk
- Update profit targets if edge changed
- Document new patterns discovered

## Technology Stack

### Required Components

**Core System:**
- FastKalshiClient: Persistent connection, <500ms latency, auto token refresh
- Mobile web UI: Touch-optimized, minimal latency, large buttons
- Position size presets: Quick selection (500, 1000, 1500, 2000, 3000, 5000)
- Real-time price display: Update every 1 second
- One-tap execution: BUY YES, BUY NO, SELL YES, SELL NO

**Critical Features:**
- Orderbook depth display (verify liquidity before trade)
- Execution time tracking (monitor latency per trade)
- Session P&L display (know where you stand)
- Battery level indicator (don't run out mid-game)
- Connection status indicator (know if API is responsive)

### Code Quality Standards

**Performance Requirements:**
- All order executions must complete in <1 second total
- UI must be responsive (no lag on button presses)
- Price updates must refresh every 1 second maximum
- No memory leaks during 3+ hour game sessions

**Reliability Requirements:**
- Automatic token refresh before expiry (every 25 minutes)
- Graceful error handling (show errors, don't crash)
- Network retry logic (3 attempts with exponential backoff)
- Fallback to manual if automation fails

**Security Requirements:**
- Never hardcode credentials (use environment variables)
- Use HTTPS only (no plain HTTP)
- Log out properly after game (don't leave sessions open)

### Testing Protocol

**Before Every Game:**
1. Test execution speed (place small test trade, measure latency)
2. Verify authentication works
3. Test UI on actual device (not just desktop browser)
4. Confirm orderbook data loading correctly
5. Test all four buttons (BUY YES, BUY NO, SELL YES, SELL NO)

**Weekly Testing:**
1. Test on stadium WiFi (speeds vary by location)
2. Test on mobile data (backup connection)
3. Verify battery life (3+ hour continuous use)
4. Test extreme scenarios (1 contract, 5000 contracts)

## Success Metrics

### Per-Game Targets

**Minimum Performance (Break Even):**
- P&L: $0 to +$50
- Win rate: 40-50%
- No major rule violations

**Good Performance:**
- P&L: $200-$400 per game
- Win rate: 60-70%
- 4-6 trades executed
- Avg hold time: <15 seconds
- Avg execution time: <500ms

**Excellent Performance:**
- P&L: $500-$1,000 per game
- Win rate: 70-80%
- 5-8 trades executed
- Avg profit per winner: $150+
- Avg loss per loser: <$50
- All trades within risk limits

### Monthly Goals

**Volume Targets:**
- Games attended: 4-8 per month
- Total trades: 20-50 per month
- Active trading days: 4-8 per month

**Profitability Targets (Based on Account Size):**

$5K Account:
- Monthly target: $1,000-$2,000
- Per game target: $250-$500
- Monthly loss limit: -$500

$10K Account:
- Monthly target: $2,000-$4,000
- Per game target: $500-$1,000
- Monthly loss limit: -$1,000

$25K Account:
- Monthly target: $5,000-$10,000
- Per game target: $1,250-$2,500
- Monthly loss limit: -$2,500

$50K Account:
- Monthly target: $10,000-$20,000
- Per game target: $2,500-$5,000
- Monthly loss limit: -$5,000

**Quality Metrics:**
- Win rate: >60%
- Avg execution time: <500ms
- Avg hold time: 10-20 seconds
- Disciplined trading approach
- Stop losses honored when appropriate

### Performance Tracking Spreadsheet

**Columns to Track:**
| Date | Game | Ticker | Trades | Win% | Session P&L | Best Trade | Worst Trade | Avg Exec Time | Notes |
|------|------|--------|--------|------|-------------|------------|-------------|---------------|-------|

**Weekly Summary:**
- Total P&L
- Average win rate
- Total trades
- Position size trends
- Technical issues encountered

**Monthly Summary:**
- Total P&L
- ROI % on account
- Best game
- Worst game  
- Pattern insights
- Strategy adjustments made

## Failure Modes & Contingencies

### Internet Connection Issues

**If WiFi drops:**
1. Immediately switch to mobile data
2. Close any open positions as soon as reconnected
3. Do NOT attempt new trades until connection stable for 30+ seconds
4. Test with small trade (100 contracts) before resuming normal size

**If both connections fail:**
1. Stop trading immediately
2. Do NOT attempt to trade blindly
3. Wait for stable reconnection
4. Consider ending session if connectivity unreliable

**Prevention:**
- Always have mobile hotspot as backup
- Test both connections before game
- Sit in area with good signal strength

### API Authentication Failures

**If login fails:**
1. Attempt re-login immediately (may be temp server issue)
2. If second attempt fails, close app and restart
3. If third attempt fails, stop trading for the game
4. Contact Kalshi support after game

**If token expires mid-game:**
- App should auto-refresh every 25 minutes
- If manual refresh needed, do so between innings
- Never trade while authentication status uncertain

**Prevention:**
- Authenticate 30 minutes before first pitch
- Monitor token expiry time
- Set reminder at 20 minutes to refresh

### Execution Latency Degradation

**If execution times exceed 1 second consistently:**
1. Reduce position sizes by 50% (edge is shrinking)
2. Monitor for 2-3 trades to see if temporary
3. If persists beyond 2 seconds, stop trading (edge is gone)
4. Investigate cause: API issues, network, device performance

**Prevention:**
- Track execution time for every trade
- Set alert if latency >800ms
- Have target: <500ms average

### Consecutive Losses

**After 2 consecutive losses:**
1. Reduce position size by 50% for next trade
2. Only trade highest-confidence events (clear runs scored)
3. Tighten stop loss to -1¢

**After 3 consecutive losses:**
1. STOP TRADING for the remainder of the game
2. Do not attempt to "win it back"
3. Review what went wrong before next game
4. Consider if edge has deteriorated

**Prevention:**
- Strict adherence to entry rules (only trade what you clearly see)
- Never increase size after losses
- Accept that some games will have unfavorable conditions

### Device Battery Depletion

**If battery drops below 50%:**
1. Connect to portable charger immediately
2. Reduce screen brightness to conserve power
3. Close unnecessary apps

**If battery drops below 20%:**
1. Close all positions
2. Stop trading for the game
3. Conserve battery for emergency contact if needed

**Prevention:**
- Start game with 100% battery
- Bring 20,000mAh+ portable charger
- Test battery life during practice sessions

### Orderbook Liquidity Dries Up

**If orderbook depth <200 contracts:**
1. Reduce position size to match available liquidity
2. Only take 30-40% of visible depth
3. Expect slippage

**If orderbook depth <100 contracts:**
1. Skip the trade
2. Market is too illiquid
3. Wait for next opportunity

**Prevention:**
- Check depth before every trade
- Trade popular markets (high volume games)
- Avoid very lopsided games (90%+ probability)

## Emergency Stops

### Consider Stopping Trading If:

**Financial Triggers:**
- ❌ Experiencing significant losses that exceed your comfort level
- ❌ Down a substantial percentage of account balance
- ❌ Hit 3 consecutive stop losses

**Technical Triggers:**
- ❌ Execution time exceeds 2 seconds consistently
- ❌ Internet connection unstable (multiple disconnects)
- ❌ Device battery <20% with no charger
- ❌ API authentication issues persist

**Market Triggers:**
- ❌ Kalshi prices updating <1 second after events (edge gone)
- ❌ Orderbook liquidity consistently <200 contracts
- ❌ Unusual price movements (possible API issues)

**Personal Triggers:**
- ❌ Feeling emotional, angry, or frustrated
- ❌ Breaking your own rules repeatedly
- ❌ Unable to focus on game (distracted, tired)
- ❌ Impaired judgment (alcohol, fatigue, stress)

### Resume Trading Only When:

**After Financial Stop:**
- You've reviewed all trades and identified mistakes
- You've tested in demo mode successfully
- You've adjusted position sizes or rules as needed
- You're mentally ready (not emotional)
- At least 24 hours have passed

**After Technical Stop:**
- All systems tested and functioning properly
- Latency back under 500ms consistently
- Stable internet connection verified
- Device fully charged

**After Market Stop:**
- You've verified Kalshi's delay is back to ~2 seconds
- Orderbook liquidity has returned
- You've tested with small positions first

**After Personal Stop:**
- You're calm, focused, and clear-headed
- You've reflected on what caused emotional state
- You've committed to following rules strictly
- You're trading for the right reasons (not revenge)

## Compliance & Ethics

### Legal Considerations
- Only trade from jurisdictions where Kalshi is legal (verify for your location)
- Comply with all Kalshi Terms of Service
- Accurately report all trading profits for tax purposes
- Do not share account access with others
- Understand this is information arbitrage, not insider trading (public info, just faster)

### Ethical Guidelines
- This strategy exploits information asymmetry, which is legal and ethical
- You're simply faster than their data feed (no manipulation involved)
- Do not interfere with stadium systems, WiFi, or infrastructure
- Do not disrupt other fans' experience while trading
- Be discreet (don't advertise your activity to those around you)
- Maintain good sportsmanship regardless of trading outcomes

### Account Health & Relationship with Kalshi
- Stay well within rate limits (manual trading won't be an issue)
- Do not abuse API access
- Maintain good standing with Kalshi
- If contacted by Kalshi about trading patterns:
  - Be honest about your strategy
  - Explain you're manually trading based on live observation
  - Provide trade logs if requested
  - Be cooperative and professional
- If asked to reduce activity:
  - Comply immediately
  - Understand their perspective
  - Explore if there's an acceptable middle ground

### Position Accountability Communication
- If you consistently approach 60%+ of PAL ($15K+), expect possible inquiry
- Be prepared to explain your strategy
- Demonstrate risk management practices
- Show that you understand the markets you're trading
- Prove you have sufficient capital and sophistication

## Continuous Improvement

### After Every Game
- Update trading journal with detailed trade data
- Calculate all performance metrics
- Identify at least one thing done well and one thing to improve
- Note any technical issues for resolution
- Assess if rules need modification

### Weekly Focus
- Review aggregate statistics across all games
- Identify patterns in successful vs unsuccessful trades
- Adjust position sizing if account balance changed significantly
- Test any new features or UI improvements
- Review and optimize pre-game preparation process

### Monthly Strategy Review
- Comprehensive analysis of all trades for the month
- Calculate true ROI (accounting for time invested)
- Compare actual performance to goals
- Assess if edge is sustainable or deteriorating
- Make strategic decisions:
  - Continue with current approach?
  - Modify position sizes?
  - Change profit targets?
  - Add/remove event types to trade?
  - Invest in better technology?

### Edge Monitoring (Critical)

**Your edge depends on Kalshi's delay staying at ~2 seconds. Monitor continuously:**

**Green Zone (Edge Intact):**
- Kalshi updates 2-3 seconds after events
- Retail traders react 5-10 seconds after events
- Consistent profitable opportunities
- Action: Continue current strategy

**Yellow Zone (Edge Narrowing):**
- Kalshi updates 1-2 seconds after events
- Retail traders reacting faster
- Fewer profitable opportunities
- Action: Reduce position sizes, increase profit targets

**Red Zone (Edge Gone):**
- Kalshi updates <1 second after events
- Retail traders nearly as fast as you
- Minimal profitable opportunities
- Action: STOP this strategy, find new edge

**Monitor These Indicators:**
- Time from event to first price move
- Your win rate over time (declining = edge narrowing)
- Average profit per trade (declining = edge narrowing)
- Frequency of stop losses (increasing = edge gone)

### Strategy Evolution Options

**If edge deteriorates:**
1. Shift to different markets (other sports, events)
2. Adapt to smaller position sizes with tighter targets
3. Focus only on highest-impact events (home runs vs singles)
4. Develop additional edge (better game analysis, weather data, etc.)
5. Accept that this arbitrage opportunity had a limited lifespan

**If edge remains strong:**
1. Increase capital allocation
2. Attend more games per month
3. Refine execution to shave milliseconds
4. Develop better event recognition (faster decision-making)
5. Scale up position sizes (within risk limits)

## Document Maintenance

**Last Updated:** [Current Date]  
**Version:** 2.0 - High Volume Manual Execution  
**Next Review:** After every 5 games or monthly (whichever comes first)

**Update This Document When:**
- You discover Kalshi's delay has changed (faster or slower)
- Win rate changes significantly (±10%)
- New profitable event types identified
- New risk factors discovered
- Account balance increases/decreases significantly (adjust position sizes)
- Technology stack changes (new UI, faster execution)
- Kalshi changes their PAL or rate limit policies
- You achieve sustained profitability milestones
- Major losses occur (document what went wrong)

**Version History:**
- v1.0: Initial strategy (small positions, learning phase)
- v2.0: High-volume manual execution (current)

---

## Core Principles (Never Forget)

1. **Speed wins** - Execute in <500ms or miss the opportunity
2. **Size appropriately** - Use position sizes that match your risk tolerance
3. **Flip fast** - Hold 5-20 seconds max, then sell
4. **Repeat** - Trade multiple events per game
5. **Risk awareness** - Use stop losses strategically
6. **Monitor PAL** - Be aware of the $25K Position Accountability Level
7. **Mind your edge** - If Kalshi speeds up, your edge disappears
8. **Be disciplined** - Trade with a consistent approach

**Remember:** This is a latency arbitrage strategy with a potentially limited lifespan. Your edge exists because you're physically present and Kalshi's API is delayed. If either changes, the opportunity vanishes. Trade it while it lasts, but always be prepared for it to end.

---

*Success comes from: (1) Fast execution, (2) Appropriate position sizing, (3) Quick exits, (4) Repetition, (5) Discipline. Master these five and profit consistently.*