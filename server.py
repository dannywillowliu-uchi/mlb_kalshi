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

        # Log trade
        trade_record = {
            'timestamp': datetime.now().isoformat(),
            'side': side,
            'action': action,
            'count': count,
            'latency_ms': total_latency,
            'result': result
        }
        session_stats['trades'].append(trade_record)

        return jsonify({
            'success': True,
            'latency_ms': total_latency,
            'order': result,
            'warning': 'SLOW EXECUTION' if total_latency > 500 else None
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/positions', methods=['GET'])
def get_positions():
    """Get current positions"""
    try:
        positions = client.get_positions()

        # Filter for current ticker
        if current_ticker:
            positions = [p for p in positions if p.get('ticker') == current_ticker]

        return jsonify({
            'success': True,
            'positions': positions
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


@app.route('/api/reset-session', methods=['POST'])
def reset_session():
    """Reset session stats (between innings/games)"""
    global session_stats
    session_stats = {
        'trades': [],
        'total_pnl': 0,
        'start_time': datetime.now().isoformat()
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
