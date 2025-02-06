
from datetime import datetime
from longport.openapi import OrderStatus
import time
from LongPortData import LongPortData
import sys
import os
import logging
from logging.handlers import TimedRotatingFileHandler
logger = logging.getLogger(__name__)

def init_log(log_path):
    # 初始化log
    logger.setLevel(logging.INFO)

    # 创建一个handler，用于写入日志文件，每天一个文件，保留30天
    log_path = os.path.join(log_path,'net_trader.log')
    handler = TimedRotatingFileHandler(log_path, when='D', interval=1, backupCount=30)
    handler.setLevel(logging.INFO)

    # 创建一个输出格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # 添加handler到logger
    logger.addHandler(handler)

'''
    下单购买逻辑：
    1、查询当前价格
    2、下单购买
    3、一分钟后，追踪订单成交状态
    4、若订单未成交，撤销订单。重新下单，重复1-4
    5、若订单成交，记录成交价格
'''

if __name__ == '__main__':
    
    # 初始化log
    log_path = ""
    # 打印所有命令行参数
    print("命令行参数:")
    for arg in sys.argv:
        print(arg)
    
    # 访问特定的命令行参数
    if len(sys.argv) > 1:
        log_path = sys.argv[1]
        print("第一个参数:", sys.argv[1])

    init_log(log_path)
    logger.info('Started')


    # 配置
    stock_id = "MSTX.US"
    # stock_id = "01810.HK"
    first_amount = 200
    amount = 200
    delta_price = 0.5

    data = LongPortData()
    data.get_last_trade_price(datetime(2023, 12, 1), stock_id)

    # 删除今天的未成交订单
    data.delete_today_order(stock_id)

    order_id = None
    while True:
        # 查看当前市场
        if not data.check_market(stock_id):
            # 待机60秒
            time.sleep(60)
            continue

        # 查看仓位 空仓则下单
        if not data.check_stock_positions(stock_id):
            logger.info("not have stock position create order")
            status = OrderStatus.Unknown
            order_id = None
            while status  != OrderStatus.Filled:
                current_price = data.get_current_price([stock_id])
                order_id = data.buy(stock_id=stock_id, price=current_price, amount=first_amount, order_id=order_id)
                logger.info(order_id)

                # 暂停程序执行10秒
                time.sleep(10)

                status = data.check_order_status(order_id)

            data.last_trader_price = current_price

        # 开始网格交易
        logger.info("Start NetTrade")
        logger.info("last_trader_price: %f",data.last_trader_price)
        current_price = data.get_current_price([stock_id])
        logger.info("current_price: %f",current_price)

        current_delta = current_price - data.last_trader_price
        logger.info("current_delta: %f",current_delta)
        if current_delta > delta_price:
            order_id = data.sell(stock_id=stock_id, price=current_price, amount=amount, order_id=order_id)
           
        elif current_delta < -delta_price:
            order_id = data.buy(stock_id=stock_id, price=current_price, amount=amount, order_id=order_id)
        
        logger.info("order_id: %s",order_id)

        # 暂停程序执行10秒
        time.sleep(10)
        status = data.check_order_status(order_id)
        logger.info("status: %s",status)

        if status == OrderStatus.Filled:
            order_id = None
            data.last_trader_price = current_price