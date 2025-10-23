import logging
import sys
import os
import getpass
from decimal import Decimal, InvalidOperation
from pprint import pprint
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

def setup_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/trading_bot.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.getLogger("binance").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

class BasicBot:
    
    def __init__(self, api_key, api_secret, testnet=True):
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing BasicBot (Testnet: {testnet})")
        
        try:
            self.client = Client(api_key, api_secret, testnet=testnet)
            if testnet:
                self.client.FUTURES_URL = 'https://testnet.binancefuture.com'
                
            self.client.futures_ping()
            self.get_usdt_balance() 
            self.logger.info("Binance client initialized and connection successful.")
            
        except BinanceAPIException as e:
            self.logger.error(f"Failed to initialize Binance client or connect. "
                            f"Check API keys and network. Error: {e}")
            sys.exit(1) 
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during initialization: {e}")
            sys.exit(1)

    def _create_order(self, order_params):
        self.logger.info(f"Attempting to place order with params: {order_params}")
        try:
            order = self.client.futures_create_order(**order_params)
            self.logger.info("Order placed successfully.")
            self.logger.debug(f"Order response: {order}")
            return order
        except BinanceAPIException as e:
            self.logger.error(f"API Error placing order: {e.response.json()}")
            return None
        except BinanceOrderException as e:
            self.logger.error(f"Order Logic Error placing order: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error placing order: {e}")
            return None

    def place_market_order(self, symbol, side, quantity):
        params = {
            'symbol': symbol,
            'side': side,
            'type': 'MARKET',
            'quantity': str(quantity) 
        }
        return self._create_order(params)

    def place_limit_order(self, symbol, side, quantity, price):
        params = {
            'symbol': symbol,
            'side': side,
            'type': 'LIMIT',
            'quantity': str(quantity),
            'price': str(price),
            'timeInForce': 'GTC'  
        }
        return self._create_order(params)

    def place_stop_limit_order(self, symbol, side, quantity, price, stop_price):
        params = {
            'symbol': symbol,
            'side': side,
            'type': 'STOP_LIMIT',
            'quantity': str(quantity),
            'price': str(price),
            'stopPrice': str(stop_price),
            'timeInForce': 'GTC'
        }
        return self._create_order(params)

    def get_usdt_balance(self):
        self.logger.info("Fetching account balance...")
        try:
            balances = self.client.futures_account_balance()
            for asset in balances:
                if asset['asset'] == 'USDT':
                    available_balance = Decimal(asset['availableBalance'])
                    self.logger.info(f"USDT Available Balance: {available_balance}")
                    return available_balance
            self.logger.warning("USDT asset not found in futures account balance.")
            return Decimal('0.0')
        except BinanceAPIException as e:
            self.logger.error(f"API Error fetching balance: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching balance: {e}")
            return None

    def get_order_status(self, symbol, order_id):
        self.logger.info(f"Fetching status for order {order_id} on {symbol}...")
        try:
            order = self.client.futures_get_order(symbol=symbol, orderId=order_id)
            self.logger.info(f"Order status: {order.get('status')}")
            return order
        except BinanceAPIException as e:
            self.logger.error(f"API Error fetching order: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching order: {e}")
            return None

def _get_validated_input(prompt, validation_fn, error_msg):
    while True:
        try:
            value = input(prompt).strip()
            return validation_fn(value)
        except Exception as e:
            print(f"Invalid input: {error_msg}. Error: {e}. Please try again.")

def _validate_symbol(symbol):
    if not symbol or not symbol.isalnum(): 
        raise ValueError("Symbol cannot be empty and must be alphanumeric.")
    return symbol.upper()

def _validate_side(side):
    side = side.upper()
    if side not in ['BUY', 'SELL']:
        raise ValueError("Side must be 'BUY' or 'SELL'.")
    return side

def _validate_decimal(value):
    val = Decimal(value)
    if val <= 0:
        raise ValueError("Value must be positive.")
    return val

def _validate_order_id(value):
    if not value.isdigit():
        raise ValueError("Order ID must be a number.")
    return value

def _handle_place_order(bot):
    logger = logging.getLogger(__name__)
    print("\n--- Place New Order ---")
    
    try:
        symbol = _get_validated_input("Enter symbol (e.g., BTCUSDT): ", _validate_symbol, "Must be a valid symbol.")
        side = _get_validated_input("Enter side (BUY / SELL): ", _validate_side, "Must be 'BUY' or 'SELL'.")
        
        order_type = input("Enter order type (MARKET / LIMIT / STOP_LIMIT): ").upper().strip()
        
        if order_type not in ['MARKET', 'LIMIT', 'STOP_LIMIT']:
            print("Invalid order type. Aborting.")
            return

        quantity = _get_validated_input("Enter quantity (e.g., 0.001): ", _validate_decimal, "Must be a positive number.")
        
        result = None
        if order_type == 'MARKET':
            result = bot.place_market_order(symbol, side, quantity)
            
        elif order_type == 'LIMIT':
            price = _get_validated_input("Enter limit price: ", _validate_decimal, "Must be a positive number.")
            result = bot.place_limit_order(symbol, side, quantity, price)
            
        elif order_type == 'STOP_LIMIT':
            stop_price = _get_validated_input("Enter stop/trigger price: ", _validate_decimal, "Must be a positive number.")
            price = _get_validated_input("Enter limit price (once triggered): ", _validate_decimal, "Must be a positive number.")
            if (side == 'BUY' and stop_price >= price) or (side == 'SELL' and stop_price <= price):
                logger.warning(f"Unusual STOP_LIMIT prices for {side}: stopPrice {stop_price}, limitPrice {price}. "
                               f"Order might fill immediately or not at all.")
                print("Warning: Prices may lead to immediate or no fill. Proceeding...")
            result = bot.place_stop_limit_order(symbol, side, quantity, price, stop_price)
            
        if result:
            print("\n--- Order Placed Successfully ---")
            pprint(result)
        else:
            print("\n--- Order Failed to Place ---")
            
    except (InvalidOperation, ValueError) as e:
        logger.warning(f"Invalid input during order creation: {e}")
        print(f"Invalid number format. Please use valid decimals.")
    except Exception as e:
        logger.error(f"An unexpected error occurred in order flow: {e}")
        print(f"An unexpected error occurred. Check logs.")


def _handle_check_balance(bot):
    print("\n--- Checking Account Balance ---")
    balance = bot.get_usdt_balance()
    if balance is not None:
        print(f"Available USDT Balance: {balance:,.8f}")
    else:
        print("Could not retrieve balance. Check logs.")

def _handle_check_order(bot):
    print("\n--- Check Order Status ---")
    try:
        symbol = _get_validated_input("Enter symbol (e.g., BTCUSDT): ", _validate_symbol, "Must be a valid symbol.")
        order_id = _get_validated_input("Enter Order ID: ", _validate_order_id, "Must be numeric.")
        
        order = bot.get_order_status(symbol, order_id)
        
        if order:
            print("\n--- Order Details ---")
            pprint(order)
        else:
            print("\n--- Could not retrieve order ---")
            print("Please check the symbol and Order ID. See logs for details.")
            
    except Exception as e:
        logging.getLogger(__name__).error(f"An unexpected error occurred in check order flow: {e}")
        print(f"An unexpected error occurred. Check logs.")

def main_cli():
    logger = setup_logging()
    
    print("=========================================")
    print("=   Binance Futures Testnet Trading Bot =")
    print("=========================================")
    
    load_dotenv()
    
    api_key = os.environ.get('BINANCE_TEST_KEY')
    api_secret = os.environ.get('BINANCE_TEST_SECRET')
    
    if not api_key:
        print("BINANCE_TEST_KEY not found in .env file.")
        api_key = getpass.getpass('Enter Binance Testnet API Key: ')
    
    if not api_secret:
        print("BINANCE_TEST_SECRET not found in .env file.")
        api_secret = getpass.getpass('Enter Binance Testnet API Secret: ')

    if not api_key or not api_secret:
        logger.error("API Key and Secret are required. Exiting.")
        sys.exit(1)

    try:
        bot = BasicBot(api_key, api_secret, testnet=True)
        
        while True:
            print("\n--- Main Menu ---")
            print("1: Place New Order")
            print("2: Check Order Status")
            print("3: Check USDT Balance")
            print("4: Exit")
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == '1':
                _handle_place_order(bot)
            elif choice == '2':
                _handle_check_order(bot)
            elif choice == '3':
                _handle_check_balance(bot)
            elif choice == '4':
                print("Exiting. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 4.")
                
    except Exception as e:
        logger.critical(f"A critical error occurred. Exiting. Error: {e}")
        print(f"A critical error occurred: {e}. Check logs/trading_bot.log for details.")
        sys.exit(1)

if __name__ == "__main__":
    main_cli()
