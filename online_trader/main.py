from datetime import datetime
import time
from LongPortData import LongPortData
import sys
from log import logger
import yaml
from strategy.TraderSelect import SelectStrategy
from orderbook.OrderBook import OrderBook

if __name__ == "__main__":

    # 读取yaml配置文件
    config_path = "/e-vepfs/wangchenan/code/trade/online_trader/config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    print("读取到的配置:", config)

    logger(config["log_name"], config["log_path"])
    logger.info("Started")

    # 配置
    stock_id = config["stock_id"]

    data = LongPortData(config)
    order_book = OrderBook(stock_id, config)
    strategy = SelectStrategy(config["strategy"]["name"])(stock_id, config)

    # 初始化data类
    data.get_last_trade_price(datetime(2025, 5, 1), stock_id)

    while True:
        logger.info("==========================")
        # 查看当前市场
        if not data.check_market(stock_id):
            # 待机60秒
            time.sleep(60)
            continue

        (price, amount, order_side) = strategy.Run()

        if order_side is not None:
            order_book.submit(
                stock_id,
                price,
                amount,
                order_side,
            )

        time.sleep(10)
        logger.info("==========================")
