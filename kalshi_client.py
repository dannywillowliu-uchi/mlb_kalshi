"""
FastKalshiClient - High-performance Kalshi API client for latency arbitrage
Target: <500ms execution time
Uses API key authentication with RSA signatures
"""

import os
import time
import json as json_lib
import requests
import base64
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

load_dotenv()


class FastKalshiClient:
    """Optimized Kalshi client with persistent connections and API key authentication"""

    def __init__(self):
        self.base_url = os.getenv('KALSHI_API_BASE', 'https://api.elections.kalshi.com/trade-api/v2')
        self.api_key_id = os.getenv('KALSHI_API_KEY_ID')
        private_key_str = os.getenv('KALSHI_PRIVATE_KEY')

        # Load private key
        if private_key_str:
            self.private_key = serialization.load_pem_private_key(
                private_key_str.encode(),
                password=None,
                backend=default_backend()
            )
        else:
            self.private_key = None

        # Persistent session for connection reuse (reduces latency)
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

        self.member_id = None

    def _sign_request(self, method: str, path: str, body: str = "") -> tuple:
        """Sign request with private key using PSS padding"""
        timestamp = str(int(time.time() * 1000))

        # IMPORTANT: Sign with FULL path including /trade-api/v2 and query params
        full_path = "/trade-api/v2" + path

        # Create string to sign: timestamp + method + full_path (NO body)
        msg_string = timestamp + method + full_path

        # Sign with private key using PSS padding
        signature = self.private_key.sign(
            msg_string.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.DIGEST_LENGTH
            ),
            hashes.SHA256()
        )

        # Base64 encode signature
        signature_b64 = base64.b64encode(signature).decode('utf-8')

        return timestamp, signature_b64

    def _make_signed_request(self, method: str, path: str, json_data: Dict = None, params: Dict = None) -> requests.Response:
        """Make authenticated request with signature"""
        body = ""
        if json_data:
            body = json_lib.dumps(json_data)

        # Build full path with query params for signature
        full_path_for_sig = path
        if params:
            query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
            full_path_for_sig = f"{path}?{query_string}"

        timestamp, signature = self._sign_request(method, full_path_for_sig, body)

        headers = {
            'KALSHI-ACCESS-KEY': self.api_key_id,
            'KALSHI-ACCESS-SIGNATURE': signature,
            'KALSHI-ACCESS-TIMESTAMP': timestamp,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        # URL uses base_url + path (base_url already has /trade-api/v2)
        url = self.base_url + path

        if method == 'GET':
            return self.session.get(url, headers=headers, params=params)
        elif method == 'POST':
            return self.session.post(url, headers=headers, data=body)
        elif method == 'DELETE':
            return self.session.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")

    def ensure_authenticated(self):
        """Ensure valid authentication (no-op for API key auth)"""
        if not self.private_key or not self.api_key_id:
            raise Exception("API key credentials not configured")

    def login(self) -> Dict:
        """Verify API key works by fetching balance"""
        start_time = time.time()

        balance = self.get_balance()

        elapsed = (time.time() - start_time) * 1000
        print(f"✓ Authenticated in {elapsed:.0f}ms")

        return {
            'success': True,
            'balance': balance,
            'member_id': self.api_key_id  # Use API key ID as member identifier
        }

    def search_markets(self, query: str = '', limit: int = 20) -> Dict:
        """Search for markets by ticker or title"""
        self.ensure_authenticated()
        start_time = time.time()

        params = {
            'limit': str(limit),
            'status': 'open'  # Only show tradeable markets
        }

        # Add ticker prefix filter if query provided
        if query:
            # Kalshi uses 'ticker' param for prefix matching
            params['ticker'] = query.upper()

        response = self._make_signed_request('GET', '/markets', params=params)
        response.raise_for_status()

        elapsed = (time.time() - start_time) * 1000
        return {'data': response.json(), 'latency_ms': elapsed}

    def get_market(self, ticker: str) -> Dict:
        """Get market details"""
        self.ensure_authenticated()
        start_time = time.time()

        response = self._make_signed_request('GET', f'/markets/{ticker}')
        response.raise_for_status()

        elapsed = (time.time() - start_time) * 1000
        return {'data': response.json(), 'latency_ms': elapsed}

    def get_orderbook(self, ticker: str) -> Dict:
        """Get current orderbook (critical for liquidity checks)"""
        self.ensure_authenticated()
        start_time = time.time()

        response = self._make_signed_request('GET', f'/markets/{ticker}/orderbook')
        response.raise_for_status()

        data = response.json()
        elapsed = (time.time() - start_time) * 1000

        # The orderbook is nested inside 'orderbook' key
        orderbook = data.get('orderbook', {})

        return {
            'yes': orderbook.get('yes', []),
            'no': orderbook.get('no', []),
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

        response = self._make_signed_request('POST', '/portfolio/orders', order_data)
        response.raise_for_status()

        elapsed = (time.time() - start_time) * 1000
        result = response.json()
        result['execution_latency_ms'] = elapsed

        return result

    def quick_buy_yes(self, ticker: str, count: int, current_price: int, price_buffer: int = 2) -> Dict:
        """
        Quick buy YES - uses price from UI (old price) + buffer
        For latency arbitrage: buy at the price you saw BEFORE the event updates

        Args:
            ticker: Market ticker
            count: Number of contracts
            current_price: Current price from UI (in cents)
            price_buffer: Cents to add above current price (default: 2)
        """
        # Use the price passed from UI + buffer for better fill probability
        buy_price = min(99, current_price + price_buffer)

        return self.place_order(ticker, 'yes', 'buy', count, buy_price)

    def quick_buy_no(self, ticker: str, count: int, current_price: int, price_buffer: int = 2) -> Dict:
        """
        Quick buy NO - uses price from UI (old price) + buffer
        For latency arbitrage: buy at the price you saw BEFORE the event updates

        Args:
            ticker: Market ticker
            count: Number of contracts
            current_price: Current price from UI (in cents)
            price_buffer: Cents to add above current price (default: 2)
        """
        # Use the price passed from UI + buffer for better fill probability
        buy_price = min(99, current_price + price_buffer)

        return self.place_order(ticker, 'no', 'buy', count, buy_price)

    def quick_sell_yes(self, ticker: str, count: int) -> Dict:
        """Quick sell YES - market order for immediate fill"""
        # Get FRESH orderbook right before placing order
        orderbook = self.get_orderbook(ticker)

        if not orderbook['yes']:
            raise Exception("No YES orders available in orderbook")

        # Sell at highest bid (last element) for immediate fill
        best_yes_bid = orderbook['yes'][-1][0]
        sell_price = best_yes_bid

        return self.place_order(ticker, 'yes', 'sell', count, sell_price)

    def quick_sell_no(self, ticker: str, count: int) -> Dict:
        """Quick sell NO - market order for immediate fill"""
        # Get FRESH orderbook right before placing order
        orderbook = self.get_orderbook(ticker)

        if not orderbook['no']:
            raise Exception("No NO orders available in orderbook")

        # Sell at highest bid (last element) for immediate fill
        best_no_bid = orderbook['no'][-1][0]
        sell_price = best_no_bid

        return self.place_order(ticker, 'no', 'sell', count, sell_price)

    def get_positions(self) -> List[Dict]:
        """Get current open positions"""
        self.ensure_authenticated()

        response = self._make_signed_request('GET', '/portfolio/positions')
        response.raise_for_status()

        return response.json().get('positions', [])

    def get_balance(self) -> Dict:
        """Get account balance"""
        self.ensure_authenticated()

        response = self._make_signed_request('GET', '/portfolio/balance')
        response.raise_for_status()

        return response.json()

    def get_order_status(self, order_id: str) -> Dict:
        """Get status of a specific order"""
        self.ensure_authenticated()

        response = self._make_signed_request('GET', f'/portfolio/orders/{order_id}')
        response.raise_for_status()

        return response.json()

    def cancel_order(self, order_id: str) -> Dict:
        """Cancel an order"""
        self.ensure_authenticated()

        response = self._make_signed_request('DELETE', f'/portfolio/orders/{order_id}')
        response.raise_for_status()

        return response.json()

    def calculate_orderbook_depth(self, ticker: str) -> Dict:
        """Calculate available liquidity in orderbook"""
        orderbook = self.get_orderbook(ticker)

        # Orderbook format: [[price, quantity], [price, quantity], ...]
        yes_depth = sum(order[1] for order in orderbook['yes']) if orderbook['yes'] else 0
        no_depth = sum(order[1] for order in orderbook['no']) if orderbook['no'] else 0

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
