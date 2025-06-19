import ccxt
import time
import logging
from typing import Tuple, Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 初始化交易所（需替换为真实的API密钥）
binance = ccxt.binance({
    'apiKey': 'YOUR_BINANCE_API_KEY',
    'secret': 'YOUR_BINANCE_SECRET',
    'enableRateLimit': True,
})
okx = ccxt.okx({
    'apiKey': 'YOUR_OKX_API_KEY',
    'secret': 'YOUR_OKX_SECRET',
    'enableRateLimit': True,
})

# 参数设置
SYMBOL = 'BTC/USDT'
TRADE_AMOUNT = 0.01  # 每次交易0.01 BTC
TRADE_FEE = 0.001  # 假设手续费0.1%
TRANSFER_FEE = 0.0005  # 假设提币费0.0005 BTC
MIN_PROFIT = 50  # 最小利润阈值（美元）
MAX_SLIPPAGE = 0.005  # 最大滑点5%
COOLDOWN = 60  # 下单失败后冷却时间（秒）
MAX_RETRIES = 3  # 最大重试次数

def fetch_orderbook(exchange: ccxt.Exchange, symbol: str) -> Tuple[Optional[float], Optional[float]]:
    """获取订单簿数据"""
    for _ in range(MAX_RETRIES):
        try:
            orderbook = exchange.fetch_order_book(symbol)
            bid = orderbook['bids'][0][0]  # 最高买入价
            ask = orderbook['asks'][0][0]  # 最低卖出价
            return bid, ask
        except Exception as e:
            logging.error(f"Error fetching orderbook from {exchange.name}: {e}")
            time.sleep(1)
    return None, None

def check_balance(exchange: ccxt.Exchange, asset: str, min_amount: float) -> bool:
    """检查账户余额是否足够"""
    try:
        balance = exchange.fetch_balance()
        available = balance['free'].get(asset, 0)
        if available < min_amount:
            logging.warning(f"Insufficient {asset} balance on {exchange.name}: {available} < {min_amount}")
            return False
        return True
    except Exception as e:
        logging.error(f"Error checking balance on {exchange.name}: {e}")
        return False

def place_order(exchange: ccxt.Exchange, symbol: str, side: str, amount: float, price: float) -> bool:
    """下单并验证执行结果"""
    try:
        order = exchange.create_order(symbol, 'limit', side, amount, price)
        logging.info(f"Order placed on {exchange.name}: {side} {amount} {symbol} @ {price}")
        
        # 等待订单成交（简单实现，实际需异步处理）
        time.sleep(2)
        order_status = exchange.fetch_order(order['id'], symbol)
        if order_status['status'] == 'closed':
            logging.info(f"Order executed successfully on {exchange.name}: {order_status['filled']} filled")
            return True
        else:
            logging.warning(f"Order not fully executed on {exchange.name}: {order_status['status']}")
            return False
    except Exception as e:
        logging.error(f"Error placing order on {exchange.name}: {e}")
        return False

def calculate_arbitrage(binance_bid: float, binance_ask: float, okx_bid: float, okx_ask: float) -> Tuple[float, float, str]:
    """计算套利机会并返回方向"""
    profit_b_to_o = (okx_bid * (1 - TRADE_FEE)) - (binance_ask * (1 + TRADE_FEE)) - (TRANSFER_FEE * binance_ask)
    profit_o_to_b = (binance_bid * (1 - TRADE_FEE)) - (okx_ask * (1 + TRADE_FEE)) - (TRANSFER_FEE * binance_ask)
    
    if profit_b_to_o > profit_o_to_b and profit_b_to_o > MIN_PROFIT:
        return profit_b_to_o, binance_ask, "binance_to_okx"
    elif profit_o_to_b > MIN_PROFIT:
        return profit_o_to_b, okx_ask, "okx_to_binance"
    return 0, 0, "no_opportunity"

def execute_arbitrage(buy_exchange: ccxt.Exchange, sell_exchange: ccxt.Exchange, buy_price: float, sell_price: float) -> bool:
    """执行套利交易"""
    # 检查滑点
    current_buy_bid, current_buy_ask = fetch_orderbook(buy_exchange, SYMBOL)
    current_sell_bid, current_sell_ask = fetch_orderbook(sell_exchange, SYMBOL)
    if (abs(current_buy_ask - buy_price) / buy_price > MAX_SLIPPAGE or 
        abs(current_sell_bid - sell_price) / sell_price > MAX_SLIPPAGE):
        logging.warning("Excessive slippage detected, aborting trade.")
        return False

    # 检查余额
    if not check_balance(buy_exchange, 'USDT', TRADE_AMOUNT * buy_price):
        return False
    if not check_balance(sell_exchange, 'BTC', TRADE_AMOUNT):
        return False

    # 下单：买入
    buy_success = place_order(buy_exchange, SYMBOL, 'buy', TRADE_AMOUNT, buy_price)
    if not buy_success:
        return False

    # 下单：卖出
    sell_success = place_order(sell_exchange, SYMBOL, 'sell', TRADE_AMOUNT, sell_price)
    if not sell_success:
        logging.warning("Sell order failed, manual intervention required.")
        return False

    return True

def main():
    last_trade_time = 0
    while True:
        binance_bid, binance_ask = fetch_orderbook(binance, SYMBOL)
        okx_bid, okx_ask = fetch_orderbook(okx, SYMBOL)
        
        if None in [binance_bid, binance_ask, okx_bid, okx_ask]:
            time.sleep(5)
            continue
        
        profit, buy_price, direction = calculate_arbitrage(binance_bid, binance_ask, okx_bid, okx_ask)
        
        current_time = time.time()
        if profit > MIN_PROFIT and (current_time - last_trade_time) > COOLDOWN:
            logging.info(f"Arbitrage Opportunity: Profit = {profit:.2f} USDT, Direction = {direction}")
            
            if direction == "binance_to_okx":
                success = execute_arbitrage(binance, okx, buy_price, okx_bid)
            elif direction == "okx_to_binance":
                success = execute_arbitrage(okx, binance, buy_price, binance_bid)
            else:
                success = False
            
            if success:
                logging.info(f"Arbitrage executed successfully! Profit: {profit:.2f} USDT")
                last_trade_time = current_time
            else:
                logging.warning("Arbitrage execution failed, entering cooldown.")
                time.sleep(COOLDOWN)
        else:
            logging.info("No profitable opportunity or in cooldown.")
        
        time.sleep(5)

if __name__ == "__main__":
    main()