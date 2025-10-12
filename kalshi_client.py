"""
FastKalshiClient - High-performance Kalshi API client for latency arbitrage
Target: <500ms execution time
"""

import os
import time
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


class FastKalshiClient:
    """Optimized Kalshi client with persistent connections and auto token refresh"""

    def __init__(self):
        self.base_url = os.getenv('KALSHI_API_BASE', 'https://trading-api.kalshi.com/trade-api/v2')
        self.email = os.getenv('KALSHI_EMAIL')
        self.password = os.getenv('KALSHI_PASSWORD')

        # Persistent session for connection reuse (reduces latency)
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

        self.token = None
        self.token_expiry = None
        self.member_id = None

    def _should_refresh_token(self) -> bool:
        """Check if token needs refresh (refresh 5 minutes before expiry)"""
        if not self.token or not self.token_expiry:
            return True
        return datetime.now() >= (self.token_expiry - timedelta(minutes=5))

    def ensure_authenticated(self):
        """Ensure valid authentication, refresh if needed"""
        if self._should_refresh_token():
            self.login()

    def login(self) -> Dict:
        """Authenticate and get token"""
        start_time = time.time()

        response = self.session.post(
            f'{self.base_url}/login',
            json={'email': self.email, 'password': self.password}
        )
        response.raise_for_status()

        data = response.json()
        self.token = data['token']
        self.member_id = data['member_id']

        # Kalshi tokens expire after 30 minutes
        self.token_expiry = datetime.now() + timedelta(minutes=30)

        # Update session headers with token
        self.session.headers.update({'Authorization': f'Bearer {self.token}'})

        elapsed = (time.time() - start_time) * 1000
        print(f"✓ Authenticated in {elapsed:.0f}ms")

        return data

    def get_market(self, ticker: str) -> Dict:
        """Get market details"""
        self.ensure_authenticated()
        start_time = time.time()

        response = self.session.get(f'{self.base_url}/markets/{ticker}')
        response.raise_for_status()

        elapsed = (time.time() - start_time) * 1000
        return {'data': response.json(), 'latency_ms': elapsed}

    def get_orderbook(self, ticker: str) -> Dict:
        """Get current orderbook (critical for liquidity checks)"""
        self.ensure_authenticated()
        start_time = time.time()

        response = self.session.get(f'{self.base_url}/markets/{ticker}/orderbook')
        response.raise_for_status()

        data = response.json()
        elapsed = (time.time() - start_time) * 1000

        return {
            'yes_bids': data.get('yes', []),
            'no_bids': data.get('no', []),
            'latency_ms': elapsed
        }

    def place_order(
        self,
        ticker: str,
        side: str,  # 'yes' or 'no'
        action: str,  # 'buy' or 'sell'
        count: int,  # number of contracts
        price: int,  # price in cents (1-99)
        order_type: str = 'limit'
    ) -> Dict:
        """
        Place order with latency tracking

        Target: <500ms execution time
        """
        self.ensure_authenticated()
        start_time = time.time()

        order_data = {
            'ticker': ticker,
            'client_order_id': f'mlb_{int(time.time() * 1000)}',
            'side': side,
            'action': action,
            'count': count,
            'type': order_type,
            'yes_price' if side == 'yes' else 'no_price': price
        }

        response = self.session.post(
            f'{self.base_url}/portfolio/orders',
            json=order_data
        )
        response.raise_for_status()

        elapsed = (time.time() - start_time) * 1000
        result = response.json()
        result['execution_latency_ms'] = elapsed

        return result

    def quick_buy_yes(self, ticker: str, count: int, aggressive_cents: int = 3) -> Dict:
        """
        Quick buy YES - uses aggressive limit order for guaranteed fill
        Adds aggressive_cents to current best bid for fast execution
        """
        # Get current orderbook
        orderbook = self.get_orderbook(ticker)

        if not orderbook['yes_bids']:
            raise Exception("No YES bids available in orderbook")

        # Get best bid and add aggressive cents
        best_bid = orderbook['yes_bids'][0]['price']
        buy_price = min(99, best_bid + aggressive_cents)

        return self.place_order(ticker, 'yes', 'buy', count, buy_price)

    def quick_buy_no(self, ticker: str, count: int, aggressive_cents: int = 3) -> Dict:
        """Quick buy NO with aggressive pricing"""
        orderbook = self.get_orderbook(ticker)

        if not orderbook['no_bids']:
            raise Exception("No NO bids available in orderbook")

        best_bid = orderbook['no_bids'][0]['price']
        buy_price = min(99, best_bid + aggressive_cents)

        return self.place_order(ticker, 'no', 'buy', count, buy_price)

    def quick_sell_yes(self, ticker: str, count: int, aggressive_cents: int = 2) -> Dict:
        """Quick sell YES - aggressive pricing for fast exit"""
        orderbook = self.get_orderbook(ticker)

        if not orderbook['yes_bids']:
            raise Exception("No YES bids available in orderbook")

        best_bid = orderbook['yes_bids'][0]['price']
        sell_price = max(1, best_bid - aggressive_cents)

        return self.place_order(ticker, 'yes', 'sell', count, sell_price)

    def quick_sell_no(self, ticker: str, count: int, aggressive_cents: int = 2) -> Dict:
        """Quick sell NO - aggressive pricing for fast exit"""
        orderbook = self.get_orderbook(ticker)

        if not orderbook['no_bids']:
            raise Exception("No NO bids available in orderbook")

        best_bid = orderbook['no_bids'][0]['price']
        sell_price = max(1, best_bid - aggressive_cents)

        return self.place_order(ticker, 'no', 'sell', count, sell_price)

    def get_positions(self) -> List[Dict]:
        """Get current open positions"""
        self.ensure_authenticated()

        response = self.session.get(f'{self.base_url}/portfolio/positions')
        response.raise_for_status()

        return response.json().get('positions', [])

    def get_balance(self) -> Dict:
        """Get account balance"""
        self.ensure_authenticated()

        response = self.session.get(f'{self.base_url}/portfolio/balance')
        response.raise_for_status()

        return response.json()

    def calculate_orderbook_depth(self, ticker: str) -> Dict:
        """Calculate available liquidity in orderbook"""
        orderbook = self.get_orderbook(ticker)

        yes_depth = sum(bid.get('count', 0) for bid in orderbook['yes_bids'])
        no_depth = sum(bid.get('count', 0) for bid in orderbook['no_bids'])

        return {
            'yes_depth': yes_depth,
            'no_depth': no_depth,
            'sufficient_yes': yes_depth >= 500,
            'sufficient_no': no_depth >= 500
        }


if __name__ == '__main__':
    # Test the client
    client = FastKalshiClient()

    # Test authentication
    print("Testing authentication...")
    client.login()

    # Test balance check
    print("\nTesting balance check...")
    balance = client.get_balance()
    print(f"Balance: ${balance.get('balance', 0) / 100:.2f}")

    print("\n✓ FastKalshiClient ready for trading")
