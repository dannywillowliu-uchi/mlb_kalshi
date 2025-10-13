"""
Flask server for MLB latency arbitrage trading
Provides REST API and serves mobile-optimized UI
"""

from flask import Flask, render_template, jsonify, request
from kalshi_client import FastKalshiClient
import time
from datetime import datetime

app = Flask(__name__)
client = FastKalshiClient()

# Global state
current_ticker = None
session_stats = {
    'trades': [],
    'total_pnl': 0,
    'start_time': None
}

# Local position tracking (updated after each trade, no API latency)
local_positions = {
    'yes': {'count': 0, 'avg_price': 0},
    'no': {'count': 0, 'avg_price': 0}
}


@app.route('/')
def index():
    """Serve mobile-optimized trading UI"""
    return render_template('index.html')


@app.route('/api/auth', methods=['POST'])
def authenticate():
    """Authenticate to Kalshi"""
    try:
        result = client.login()
        return jsonify({
            'success': True,
            'member_id': result['member_id'],
            'message': 'Authenticated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/balance', methods=['GET'])
def get_balance():
    """Get account balance"""
    try:
        balance = client.get_balance()
        return jsonify({
            'success': True,
            'balance': balance.get('balance', 0) / 100  # Convert to dollars
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/search-markets', methods=['GET'])
def search_markets():
    """Search for markets"""
    try:
        query = request.args.get('q', '')
        limit = request.args.get('limit', 50, type=int)

        print(f"[Search] Query: '{query}', Limit: {limit}")  # Debug

        result = client.search_markets(query, limit)
        markets = result['data'].get('markets', [])

        print(f"[Search] Found {len(markets)} markets")  # Debug

        # Format response for dropdown
        formatted_markets = [{
            'ticker': m.get('ticker'),
            'title': m.get('title'),
            'close_time': m.get('close_time')
        } for m in markets]

        return jsonify({
            'success': True,
            'markets': formatted_markets
        })
    except Exception as e:
        print(f"[Search] Error: {e}")  # Debug
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/ticker', methods=['POST'])
def set_ticker():
    """Set active market ticker"""
    global current_ticker
    data = request.json
    current_ticker = data.get('ticker')

    try:
        market = client.get_market(current_ticker)
        return jsonify({
            'success': True,
            'ticker': current_ticker,
            'market': market['data']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/orderbook', methods=['GET'])
def get_orderbook():
    """Get current orderbook for active ticker"""
    if not current_ticker:
        return jsonify({'success': False, 'error': 'No ticker set'}), 400

    try:
        start = time.time()
        orderbook = client.get_orderbook(current_ticker)
        depth = client.calculate_orderbook_depth(current_ticker)

        # Get highest bid prices (last element in sorted array)
        # Orderbook is sorted ascending [1¢, 2¢, ... 86¢], so -1 is the best bid
        yes_price = orderbook['yes'][-1][0] if orderbook['yes'] else None
        no_price = orderbook['no'][-1][0] if orderbook['no'] else None

        return jsonify({
            'success': True,
            'yes_price': yes_price,
            'no_price': no_price,
            'yes_depth': depth['yes_depth'],
            'no_depth': depth['no_depth'],
            'sufficient_liquidity': depth['sufficient_yes'] and depth['sufficient_no'],
            'latency_ms': (time.time() - start) * 1000
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/trade', methods=['POST'])
def execute_trade():
    """Execute trade with latency tracking"""
    if not current_ticker:
        return jsonify({'success': False, 'error': 'No ticker set'}), 400

    data = request.json
    side = data.get('side')  # 'yes' or 'no'
    action = data.get('action')  # 'buy' or 'sell'
    count = data.get('count')  # number of contracts
    current_price = data.get('current_price')  # price from UI (for buys)

    if not all([side, action, count]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400

    try:
        start_time = time.time()

        # Use current_price from UI as pre-trade reference (already fetched by price update loop)
        # This avoids extra API call before execution
        pre_trade_price = current_price if current_price else 0

        # Use quick execution methods
        if action == 'buy' and side == 'yes':
            if current_price is None:
                return jsonify({'success': False, 'error': 'Missing current_price for buy'}), 400
            result = client.quick_buy_yes(current_ticker, count, current_price)
        elif action == 'buy' and side == 'no':
            if current_price is None:
                return jsonify({'success': False, 'error': 'Missing current_price for buy'}), 400
            result = client.quick_buy_no(current_ticker, count, current_price)
        elif action == 'sell' and side == 'yes':
            result = client.quick_sell_yes(current_ticker, count)
        elif action == 'sell' and side == 'no':
            result = client.quick_sell_no(current_ticker, count)
        else:
            return jsonify({'success': False, 'error': 'Invalid side/action'}), 400

        total_latency = (time.time() - start_time) * 1000

        # Extract execution price from result
        executed_price = result.get('yes_price') or result.get('no_price', 0)

        # Calculate slippage using UI price as reference (no extra API calls)
        slippage_cents = executed_price - pre_trade_price if action == 'buy' else pre_trade_price - executed_price
        slippage_cost = (slippage_cents * count) / 100  # in dollars

        # Update local position tracking (INSTANT - no API call)
        global local_positions
        if action == 'buy':
            # Add to position
            current = local_positions[side]
            total_cost = (current['count'] * current['avg_price']) + (count * executed_price)
            new_count = current['count'] + count
            local_positions[side] = {
                'count': new_count,
                'avg_price': total_cost / new_count if new_count > 0 else 0
            }
        elif action == 'sell':
            # Reduce position
            current = local_positions[side]
            local_positions[side] = {
                'count': max(0, current['count'] - count),
                'avg_price': current['avg_price']  # Keep same avg price
            }

        # Simplified trade logging (no blocking API calls)
        trade_record = {
            'timestamp': datetime.now().isoformat(),
            'ticker': current_ticker,
            'side': side,
            'action': action,
            'count': count,
            'executed_price': executed_price,
            'pre_market_price': pre_trade_price,
            'slippage_cents': slippage_cents,
            'slippage_cost_usd': slippage_cost,
            'latency_ms': total_latency,
            'total_cost_usd': (count * executed_price) / 100,
            'order_id': result.get('order', {}).get('order_id') if 'order' in result else None
        }
        session_stats['trades'].append(trade_record)

        return jsonify({
            'success': True,
            'latency_ms': total_latency,
            'order': result,
            'warning': 'SLOW EXECUTION' if total_latency > 500 else None,
            'positions': local_positions,  # Return updated positions instantly
            'trade_log': trade_record  # Return trade details for UI display
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/positions', methods=['GET'])
def get_positions():
    """Get current positions with real-time value calculation"""
    global local_positions

    try:
        # Get current prices (this happens in background, not during trades)
        orderbook = client.get_orderbook(current_ticker) if current_ticker else {'yes': [], 'no': []}

        current_yes_price = orderbook['yes'][-1][0] if orderbook['yes'] else 0
        current_no_price = orderbook['no'][-1][0] if orderbook['no'] else 0

        # Calculate position values and P&L
        yes_pos = local_positions['yes']
        no_pos = local_positions['no']

        yes_cost = yes_pos['count'] * yes_pos['avg_price']
        no_cost = no_pos['count'] * no_pos['avg_price']

        yes_value = yes_pos['count'] * current_yes_price
        no_value = no_pos['count'] * current_no_price

        yes_pnl = yes_value - yes_cost
        no_pnl = no_value - no_cost
        total_pnl = yes_pnl + no_pnl

        total_position_value = yes_value + no_value

        return jsonify({
            'success': True,
            'positions': {
                'yes': {
                    'count': yes_pos['count'],
                    'avg_price': yes_pos['avg_price'],
                    'current_price': current_yes_price,
                    'cost': yes_cost / 100,  # Convert to dollars
                    'value': yes_value / 100,
                    'pnl': yes_pnl / 100
                },
                'no': {
                    'count': no_pos['count'],
                    'avg_price': no_pos['avg_price'],
                    'current_price': current_no_price,
                    'cost': no_cost / 100,
                    'value': no_value / 100,
                    'pnl': no_pnl / 100
                }
            },
            'total_pnl': total_pnl / 100,
            'total_position_value': total_position_value / 100
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get session statistics"""
    trades = session_stats['trades']

    if not trades:
        return jsonify({
            'success': True,
            'total_trades': 0,
            'avg_latency_ms': 0,
            'fastest_ms': 0,
            'slowest_ms': 0
        })

    latencies = [t['latency_ms'] for t in trades]

    return jsonify({
        'success': True,
        'total_trades': len(trades),
        'avg_latency_ms': sum(latencies) / len(latencies),
        'fastest_ms': min(latencies),
        'slowest_ms': max(latencies),
        'trades': trades[-10:]  # Last 10 trades
    })


@app.route('/api/trade-log', methods=['GET'])
def get_trade_log():
    """Get detailed trade log with market comparison data"""
    trades = session_stats['trades']

    if not trades:
        return jsonify({
            'success': True,
            'trades': [],
            'summary': {
                'total_trades': 0,
                'total_slippage_usd': 0,
                'avg_slippage_cents': 0,
                'total_volume_usd': 0
            }
        })

    # Calculate summary statistics
    total_slippage = sum(t.get('slippage_cost_usd', 0) for t in trades)
    avg_slippage = sum(t.get('slippage_cents', 0) for t in trades) / len(trades)
    total_volume = sum(t.get('total_cost_usd', 0) for t in trades)

    return jsonify({
        'success': True,
        'trades': trades,
        'summary': {
            'total_trades': len(trades),
            'total_slippage_usd': total_slippage,
            'avg_slippage_cents': avg_slippage,
            'total_volume_usd': total_volume
        }
    })


@app.route('/api/reset-session', methods=['POST'])
def reset_session():
    """Reset session stats (between innings/games)"""
    global session_stats, local_positions
    session_stats = {
        'trades': [],
        'total_pnl': 0,
        'start_time': datetime.now().isoformat()
    }
    # Also reset local position tracking
    local_positions = {
        'yes': {'count': 0, 'avg_price': 0},
        'no': {'count': 0, 'avg_price': 0}
    }
    return jsonify({'success': True})


if __name__ == '__main__':
    print("=" * 60)
    print("MLB KALSHI LATENCY ARBITRAGE TRADER")
    print("=" * 60)
    print("\nStarting server on http://localhost:5000")
    print("Open this URL on your phone/laptop at the stadium")
    print("\nMake sure to:")
    print("1. Create .env file with KALSHI_EMAIL and KALSHI_PASSWORD")
    print("2. Authenticate before first pitch")
    print("3. Set market ticker for the game")
    print("\n" + "=" * 60)

    # Run with host='0.0.0.0' to make accessible from phone
    app.run(host='0.0.0.0', port=5000, debug=False)
