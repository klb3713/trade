import pytz
import requests
import json
import time
import os
import smtplib
from decimal import Decimal
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv
from longport.openapi import QuoteContext, TradeContext, Config, OrderSide, OrderType, TimeInForceType

from futu import OpenSecTradeContext, OpenQuoteContext, TrdEnv, RET_OK, TrdMarket, TrdSide
from futu import OrderType as FutuOrderType

# 加载环境变量
load_dotenv()  # 从 .env 文件加载环境变量

# --- 配置参数 ---
GET_API_URL = os.getenv("FUTU_POSITION_URL")  # 请替换为您的实际 GET 接口 URL
POLLING_INTERVAL_SECONDS = int(os.getenv("POLLING_INTERVAL_SECONDS")) # 轮询间隔（秒）

# 新增配置
PORTFOLIO_ID_NAMES = dict([item.split('|', 1) for item in os.getenv("PORTFOLIO_ID_NAMES", "").split(',')])
PORTFOLIO_ID_BANLANCES= dict([item.split('|', 1) for item in os.getenv("PORTFOLIO_ID_BANLANCES", "").split(',')])
TOTAL_BANLANCE = float(os.getenv("TOTAL_BANLANCE", "100000.00"))
if PORTFOLIO_ID_BANLANCES:
    for pid in PORTFOLIO_ID_NAMES:
        PORTFOLIO_ID_BANLANCES[pid] = float(PORTFOLIO_ID_BANLANCES.get(pid, '10000.0'))
else:
    for pid in PORTFOLIO_ID_NAMES:
        PORTFOLIO_ID_BANLANCES[pid] = TOTAL_BANLANCE / len(PORTFOLIO_ID_NAMES)
PORTFOLIO_DATA_FILES = {pid: f"last_known_stock_data_{pid}.json" for pid in PORTFOLIO_ID_NAMES}

# --- 邮件发送配置 ---
SENDER_EMAIL = os.getenv("QQ_EMAIL_SENDER_ACCOUNT") # 发件人邮箱，请替换为你的 QQ 邮箱
SENDER_PASSWORD = os.getenv("QQ_EMAIL_SENDER_PASSWORD") # 从环境变量中读取授权码
RECEIVER_EMAIL = os.getenv("QQ_EMAIL_RECEIVER_ACCOUNT") # 收件人邮箱
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465 # QQ 邮箱 SMTP 服务的 SSL 端口


class FutuTrader:
    def __init__(self, **kwargs):
        self.host = os.getenv("FUTU_OPEND_HOST", "127.0.0.1")
        self.port = int(os.getenv("FUTU_OPEND_PORT", "11111"))
        self.password = os.getenv("FUTU_PASSWORD")
        self.trd_env = TrdEnv.SIMULATE if os.getenv("FUTU_TRD_ENV", "SIMULATE") == "SIMULATE" else TrdEnv.REAL
        self.acc_index = int(os.getenv("FUTU_ACC_INDEX", "0"))
        self.trd_ctx = OpenSecTradeContext(host=self.host, port=self.port, filter_trdmarket=TrdMarket.US)
        self.quote_ctx = OpenQuoteContext(host=self.host, port=self.port)
        self.usd_balance = TOTAL_BANLANCE
        self.pid_balance = PORTFOLIO_ID_BANLANCES
        self.loss_threshold = float(os.getenv("LOSS_THRESHOLD", "0.01"))
        self.profit_threshold = float(os.getenv("PROFIT_THRESHOLD", "0.04"))
        self.stop_loss_ratio = float(os.getenv("STOP_LOSS_RATIO", "10.0"))
        self.stop_profit_ratio = float(os.getenv("STOP_PROFIT_RATIO", "20.0"))
        if self.trd_env == TrdEnv.REAL:
            if not self.password:
                raise Exception("实盘交易需要设置 FUTU_PASSWORD")
            ret, data = self.trd_ctx.unlock_trade(self.password)
            if ret != RET_OK:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 解锁交易失败: {data}")
                raise Exception("交易解锁失败")
            else:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 解锁实盘交易成功")

    def submit_order(self, symbol, order_type, side, submitted_quantity, submitted_price):
        """提交订单"""
        max_retries = 3
        retry_delay = 5
        futu_order_type = FutuOrderType.MARKET if order_type == "MARKET" else FutuOrderType.NORMAL
        futu_side = TrdSide.BUY if side == "Buy" else TrdSide.SELL
        price = 0.0 if futu_order_type == FutuOrderType.MARKET else float(submitted_price)

        for attempt in range(max_retries):
            try:
                ret, data = self.trd_ctx.place_order(
                    price=price,
                    qty=float(submitted_quantity),
                    code=symbol,
                    trd_side=futu_side,
                    order_type=futu_order_type,
                    trd_env=self.trd_env,
                    acc_index=self.acc_index
                )
                if ret == RET_OK:
                    return data
                else:
                    raise Exception(data)
            except Exception as e:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 订单提交失败，尝试 {attempt + 1}/{max_retries}: {str(e)}")
                if attempt == max_retries - 1:
                    error_msg = f"订单提交失败：{str(e)}\n股票代码：{symbol}\n操作：{futu_side}\n数量：{submitted_quantity}\n价格：{price}"
                    self.send_error_notification(error_msg)
                    raise
                time.sleep(retry_delay)

    def check_and_trade(self, last_known_datas):
        """止盈止损"""

        # 当前跟踪的所有股票
        track_stock_codes = []
        portfolio_banlance = 0.0
        for pid, position_data in last_known_datas.items():
            if position_data is None:
                continue
            portfolio_banlance = position_data['portfolio_banlance']
            stock_codes = [f"{record['stock_code_suffix']}.{record['stock_code']}" for record in position_data.get("record_items", [])]
            track_stock_codes.extend(stock_codes)
        track_stock_codes = list(set(track_stock_codes))

        ret, positions = self.trd_ctx.position_list_query(trd_env=self.trd_env, acc_index=self.acc_index)
        if ret != RET_OK:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 获取持仓失败: {positions}")
            return

        for pos in positions.to_dict('records'):
            stock_code = pos['code']
            cost_price = float(pos['cost_price'])
            current_qty = int(pos['qty'])
            can_sell_qty = int(pos['can_sell_qty'])
            pl_val = float(pos['pl_val'])
            pl_ratio = float(pos['pl_ratio'])
            nominal_price = round(float(pos['nominal_price']), 2)

            if stock_code not in track_stock_codes:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 跳过非跟踪股票: {stock_code}")
                continue
            if current_qty <= 0 or can_sell_qty <= 0:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 跳过持仓为 0 的股票: {stock_code}")
                continue

            # futu 行情要开月卡 60 美元，这里默认使用跟踪到的股价
            ret, quote = self.quote_ctx.get_market_snapshot([stock_code])
            if ret != RET_OK:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 获取行情失败: {stock_code}，使用持仓的行情报价")
                current_price = nominal_price
            else:
                current_price = round(float(quote['last_price'][0]), 2)

            trade_banlance = portfolio_banlance * 7.85 if stock_code.endswith('HK') else portfolio_banlance
            if pl_ratio < 0 and abs(pl_ratio) > self.stop_loss_ratio or abs(pl_val) / trade_banlance > self.loss_threshold:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 准备止损 {stock_code}，数量: {can_sell_qty}，价格: {current_price}")
                resp = self.submit_order(
                    symbol=stock_code,
                    order_type="NORMAL",
                    side="Sell",
                    submitted_quantity=Decimal(can_sell_qty),
                    submitted_price=Decimal(current_price)
                )
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 止损订单提交结果: {resp}")
            elif pl_ratio > 0 and pl_ratio > self.stop_profit_ratio or abs(pl_val) / trade_banlance > self.profit_threshold:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 准备止盈 {stock_code}，数量: {can_sell_qty}，价格: {current_price}")
                resp = self.submit_order(
                    symbol=stock_code,
                    order_type="NORMAL",
                    side="Sell",
                    submitted_quantity=Decimal(can_sell_qty),
                    submitted_price=Decimal(current_price)
                )
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 止盈订单提交结果: {resp}")

    def track_and_trade(self, json_output):
        """跟踪下单"""

        portfolio_id = json_output.get("portfolio_id", None)
        if portfolio_id is None:
            return
        pid_balance = self.pid_balance.get(portfolio_id, None)
        if pid_balance is None:
            return

        ret, positions = self.trd_ctx.position_list_query(trd_env=self.trd_env, acc_index=self.acc_index)
        if ret != RET_OK:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 获取持仓失败: {positions}")
            return

        positions_dict = {pos['code']: pos for pos in positions.to_dict('records')}

        for change in json_output.get("changes", []):
            stock_code = change["stock_code"]
            stock_code_suffix = change["stock_code_suffix"]
            stock_code = f"{stock_code_suffix}.{stock_code}"
            change_type = change["change_type"]
            current_price = change["current_price"]
            trade_balance = pid_balance * 7.85 if stock_code_suffix == "HK" else pid_balance

            # futu 行情要开月卡 60 美元，这里默认使用跟踪到的股价
            ret, quote = self.quote_ctx.get_market_snapshot([stock_code])
            if ret != RET_OK:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 获取行情失败: {stock_code}，使用跟踪的行情报价")
            else:
                current_price = round(float(quote['last_price'][0]), 2)

            current_position = positions_dict.get(stock_code, {})
            current_qty = int(current_position.get('qty', 0))

            if current_qty == 0 and change_type != "OPEN":
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 跳过持仓为 0 且非开仓的股票: {stock_code}")
                continue

            target_ratio = change["new_ratio_percent"] / 100
            current_ratio = current_qty * current_price / trade_balance if current_price > 0 else 0
            if abs(current_ratio - target_ratio) < 0.05:
                continue

            target_qty = int(trade_balance * target_ratio / current_price) if current_price > 0 else 0
            qty_diff = target_qty - current_qty

            if change_type == "OPEN" and target_qty > 0 and current_qty == 0:
                print(
                    f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 准备开仓买入 {stock_code}，数量: {target_qty}，价格: {current_price}")
                resp = self.submit_order(
                    symbol=stock_code,
                    order_type="NORMAL",
                    side="Buy",
                    submitted_quantity=Decimal(target_qty),
                    submitted_price=Decimal(current_price)
                )
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 开仓买入订单提交结果: {resp}")
            elif change_type == "CLOSE" and current_qty > 0:
                print(
                    f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 准备清仓卖出 {stock_code}，数量: {current_qty}，价格: {current_price}")
                resp = self.submit_order(
                    symbol=stock_code,
                    order_type="NORMAL",
                    side="Sell",
                    submitted_quantity=Decimal(current_qty),
                    submitted_price=Decimal(current_price)
                )
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 清仓卖出订单提交结果: {resp}")
            elif change_type == "BUY" and qty_diff > 0:
                print(
                    f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 准备买入 {stock_code}，数量: {qty_diff}，价格: {current_price}")
                resp = self.submit_order(
                    symbol=stock_code,
                    order_type="NORMAL",
                    side="Buy",
                    submitted_quantity=Decimal(qty_diff),
                    submitted_price=Decimal(current_price)
                )
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 买入订单提交结果: {resp}")
            elif change_type == "SELL" and qty_diff < 0:
                print(
                    f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 准备卖出 {stock_code}，数量: {-qty_diff}，价格: {current_price}")
                resp = self.submit_order(
                    symbol=stock_code,
                    order_type="NORMAL",
                    side="Sell",
                    submitted_quantity=Decimal(abs(qty_diff)),
                    submitted_price=Decimal(current_price)
                )
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 卖出订单提交结果: {resp}")
            else:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {stock_code} 无需调整，当前持仓已匹配目标")

    def send_error_notification(self, error_message):
        """错误通知邮件"""
        subject = "[紧急通知] 订单提交失败"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; max-width: 600px; margin: 20px auto; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="font-size: 18px; font-weight: bold; color: #d9534f; margin-bottom: 15px;">订单提交失败通知</div>
            <hr style="border: none; border-top: 1px solid #eee; margin-bottom: 15px;">
            <div style="font-size: 14px; color: #555; margin-bottom: 10px;">时间：{datetime.now().strftime('%Y/%m/%d %H:%M:%S')}</div>
            <div style="font-size: 14px; color: #555; margin-bottom: 10px;">错误详情：</div>
            <pre style="font-size: 13px; color: #a94442; background-color: #f2dede; border: 1px solid #ebccd1; border-radius: 4px; padding: 10px; white-space: pre-wrap; word-wrap: break-word;">
        {error_message}
            </pre>
            <div style="font-size: 12px; color: #888; margin-top: 20px;">
                此邮件由自动化程序发送，请勿直接回复。
            </div>
        </div>
        """
        msg = MIMEMultipart('alternative')
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        try:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 邮件发送失败: {str(e)}")
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 错误通知邮件已发送到 {RECEIVER_EMAIL}。")

    def close(self):
        """关闭交易和行情上下文"""
        try:
            self.trd_ctx.close()
            self.quote_ctx.close()
        except AttributeError as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 关闭上下文时出错: {e}")


class LongPortTrader():
    '''LongPort Store for backtrader'''

    def __init__(self, **kwargs):
        self.config = Config.from_env()
        self.ctx = TradeContext(self.config)
        self.quote_ctx = QuoteContext(self.config)
        self.usd_balance = TOTAL_BANLANCE
        self.pid_balance = PORTFOLIO_ID_BANLANCES
        self.loss_threshold = float(os.getenv("LOSS_THRESHOLD", "0.01"))
        self.profit_threshold = float(os.getenv("PROFIT_THRESHOLD", "0.04"))
        self.stop_loss_ratio = float(os.getenv("STOP_LOSS_RATIO", "10.0"))
        self.stop_profit_ratio = float(os.getenv("STOP_PROFIT_RATIO", "20.0"))

    def submit_order(self, symbol, order_type, side, submitted_quantity, time_in_force, submitted_price, remark):
        """
        提交订单的封装方法。

        参数:
            symbol (str): 股票代码
            order_type (OrderType): 订单类型
            side (OrderSide): 买卖方向
            submitted_quantity (Decimal): 提交数量
            time_in_force (TimeInForceType): 有效期类型
            submitted_price (Decimal): 提交价格
            remark (str): 备注信息

        返回:
            resp: API 响应对象
        """
        max_retries = 3  # 最大重试次数
        retry_delay = 5  # 重试间隔（秒）

        for attempt in range(max_retries):
            try:
                resp = self.ctx.submit_order(
                    symbol=symbol,
                    order_type=order_type,
                    side=side,
                    submitted_quantity=submitted_quantity,
                    time_in_force=time_in_force,
                    submitted_price=submitted_price,
                    remark=remark
                )
                return resp  # 如果成功，返回响应

            except requests.exceptions.RequestException as e:
                print(f"[ERROR] 订单提交失败（网络问题），尝试次数 {attempt + 1}/{max_retries}: {str(e)}")
                if attempt == max_retries - 1:
                    # 达到最大重试次数后发送邮件通知
                    error_msg = f"订单提交失败（网络问题）：{str(e)}\n股票代码：{symbol}\n操作：{side.name}\n数量：{submitted_quantity}\n价格：{submitted_price}"
                    self.send_error_notification(error_msg)
                    raise  # 抛出异常
                time.sleep(retry_delay)  # 等待后重试

            except Exception as e:
                print(f"[ERROR] 订单提交失败（未知原因），尝试次数 {attempt + 1}/{max_retries}: {str(e)}")
                if attempt == max_retries - 1:
                    # 发送邮件通知其他类型的错误
                    error_msg = f"订单提交失败（未知错误）：{str(e)}\n股票代码：{symbol}\n操作：{side.name}\n数量：{submitted_quantity}\n价格：{submitted_price}"
                    self.send_error_notification(error_msg)
                    raise  # 抛出异常
                time.sleep(retry_delay)  # 等待后重试

    def send_error_notification(self, error_message):
        """
        发送错误通知邮件
        """
        subject = "[紧急通知] 订单提交失败"
        html_content = f"""
                <div style="font-family: Arial, sans-serif; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; max-width: 600px; margin: 20px auto; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="font-size: 18px; font-weight: bold; color: #d9534f; margin-bottom: 15px;">订单提交失败通知</div>
                    <hr style="border: none; border-top: 1px solid #eee; margin-bottom: 15px;">
                    <div style="font-size: 14px; color: #555; margin-bottom: 10px;">时间：{datetime.now().strftime('%Y/%m/%d %H:%M:%S')}</div>
                    <div style="font-size: 14px; color: #555; margin-bottom: 10px;">错误详情：</div>
                    <pre style="font-size: 13px; color: #a94442; background-color: #f2dede; border: 1px solid #ebccd1; border-radius: 4px; padding: 10px; white-space: pre-wrap; word-wrap: break-word;">
        {error_message}
                    </pre>
                    <div style="font-size: 12px; color: #888; margin-top: 20px;">
                        此邮件由自动化程序发送，请勿直接回复。
                    </div>
                </div>
                """

        msg = MIMEMultipart('alternative')
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = subject

        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        try:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
        except Exception as e:
            pass
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 错误通知邮件已发送到 {RECEIVER_EMAIL}。")

    def check_and_trade(self, last_known_datas):
        """
        根据持仓情况止盈止损
        """
        for pid, position_data in last_known_datas.items():
            if position_data is None:
                continue
            portfolio_banlance = position_data['portfolio_banlance']
            stock_codes = [f"{record['stock_code']}.{record['stock_code_suffix']}" for record in position_data.get("record_items", [])]
            # 获取当前所有持仓
            current_positions = []
            resp = self.ctx.stock_positions(stock_codes)
            if resp.channels:
                current_positions = resp.channels[0].positions

            # 处理每个持仓
            for position in current_positions:
                stock_code = position.symbol
                cost_price = float(position.cost_price)
                current_qty = int(position.quantity)
                available_qty = int(position.available_quantity)
                if available_qty <= 0:
                    continue
                # 获取该股票最新的价格
                cur_quote = self.quote_ctx.quote([stock_code])[0]
                cur_quote_list = [(cur_quote.timestamp, cur_quote.last_done),
                                  (cur_quote.pre_market_quote.timestamp, cur_quote.pre_market_quote.last_done),
                                  (cur_quote.post_market_quote.timestamp, cur_quote.post_market_quote.last_done)]
                cur_quote_list.sort(key=lambda x: x[0], reverse=True)
                current_price = round(float(cur_quote_list[0][1]), 2)

                if not (current_price > 0 and cost_price > 0):
                    continue

                trade_banlance = portfolio_banlance * 7.85 if stock_code.endswith('HK') else portfolio_banlance
                if current_price < cost_price:
                    loss = (cost_price - current_price) * current_qty
                    loss_ratio = (cost_price - current_price) / cost_price * 100
                    if loss / trade_banlance > self.loss_threshold or loss_ratio > self.stop_loss_ratio:
                        # 止损逻辑
                        print(f"准备止损 {stock_code}，数量: {-available_qty}，价格: {current_price}")
                        resp = self.submit_order(
                            symbol=stock_code,
                            order_type=OrderType.LO,
                            side=OrderSide.Sell,
                            submitted_quantity=Decimal(available_qty),
                            time_in_force=TimeInForceType.Day,
                            submitted_price=Decimal(current_price),
                            remark=f"Auto sell {available_qty} shares"
                        )
                        print(f"止损订单提交结果: {resp}")
                elif current_price > cost_price:
                    profit = (current_price - cost_price) * current_qty
                    profit_ratio = (current_price - cost_price) / cost_price * 100
                    if profit / trade_banlance > self.profit_threshold or profit_ratio > self.stop_profit_ratio:
                        # 止盈逻辑
                        print(f"准备止盈 {stock_code}，数量: {-available_qty}，价格: {current_price}")
                        resp = self.submit_order(
                            symbol=stock_code,
                            order_type=OrderType.LO,
                            side=OrderSide.Sell,
                            submitted_quantity=Decimal(available_qty),
                            time_in_force=TimeInForceType.Day,
                            submitted_price=Decimal(current_price),
                            remark=f"Auto Sell {available_qty} shares"
                        )
                        print(f"止盈订单提交结果: {resp}")

    def track_and_trade(self, json_output):
        """
        根据持仓变化数据执行跟踪下单

        参数:
            json_output (dict): generate_change_data 返回的结构化数据
        """
        portfolio_id = json_output.get("portfolio_id", None)
        if portfolio_id is None:
            return
        pid_balance = self.pid_balance.get(portfolio_id, None)
        if pid_balance is None:
            return
        # 获取当前所有持仓
        current_positions = []
        resp = self.ctx.stock_positions()
        if resp.channels:
            current_positions = resp.channels[0].positions

        # 处理每个变化项
        for change in json_output.get("changes", []):
            stock_code = change["stock_code"]
            stock_code_suffix = change["stock_code_suffix"]
            stock_code = f"{stock_code}.{stock_code_suffix}"
            change_type = change["change_type"]
            trade_balance = pid_balance * 7.85 if stock_code_suffix == "HK" else pid_balance

            # 获取该股票最新的价格
            cur_quote = self.quote_ctx.quote([stock_code])[0]
            cur_quote_list = [(cur_quote.timestamp, cur_quote.last_done),
                              (cur_quote.pre_market_quote.timestamp, cur_quote.pre_market_quote.last_done),
                              (cur_quote.post_market_quote.timestamp, cur_quote.post_market_quote.last_done)]
            cur_quote_list.sort(key=lambda x: x[0], reverse=True)
            current_price = round(float(cur_quote_list[0][1]), 2)

            # 获取该股票的当前持仓
            current_position = next((pos for pos in current_positions if pos.symbol == stock_code), None)
            current_qty = int(current_position.available_quantity) if current_position else 0

            # 计算目标仓位（这里只是一个示例，实际逻辑可能更复杂）
            target_ratio = change["new_ratio_percent"] / 100  # 目标持仓比例
            current_ratio = current_qty * current_price / trade_balance
            if abs(current_ratio - target_ratio) < 0.05:
                continue

            # 假设总市值资金为账户余额的一定比例（这只是一个简单示例）
            target_qty = int(trade_balance * target_ratio / current_price) if current_price > 0 else 0

            # 计算需要买入或卖出的数量
            qty_diff = target_qty - current_qty

            # 获取最大可买入数量作为参考
            # max_purchase = self.ctx.estimate_max_purchase_quantity(
            #     symbol=stock_code,
            #     order_type=OrderType.LO,
            #     side=OrderSide.Buy,
            #     price=Decimal(current_price)
            # )
            # print(f"最大可买入数量: {max_purchase.cash_max_qty}")

            if change_type == "OPEN" and target_qty > 0 and current_qty == 0:
                print(f"准备开仓买入 {stock_code}，数量: {target_qty}，价格: {current_price}")
                # 提交买入订单（这里只是一个示例，实际应检查余额、保证金等）
                resp = self.submit_order(
                    symbol=stock_code,
                    order_type=OrderType.LO,
                    side=OrderSide.Buy,
                    submitted_quantity=Decimal(target_qty),
                    time_in_force=TimeInForceType.Day,
                    submitted_price=Decimal(current_price),
                    remark=f"Auto buy {target_qty} shares"
                )
                print(f"开仓买入订单提交结果: {resp}")
                continue

            elif change_type == "CLOSE" and current_qty > 0:
                print(f"准备清仓卖出 {stock_code}，数量: {-current_qty}，价格: {current_price}")
                resp = self.submit_order(
                    symbol=stock_code,
                    order_type=OrderType.LO,
                    side=OrderSide.Sell,
                    submitted_quantity=Decimal(current_qty),
                    time_in_force=TimeInForceType.Day,
                    submitted_price=Decimal(current_price),
                    remark=f"Auto sell {current_qty} shares"
                )
                print(f"清仓卖出订单提交结果: {resp}")
                continue

            # 执行交易
            if change_type == "BUY" and qty_diff > 0:  # 需要买入
                print(f"准备买入 {stock_code}，数量: {qty_diff}，价格: {current_price}")

                # 提交买入订单（这里只是一个示例，实际应检查余额、保证金等）
                resp = self.submit_order(
                    symbol=stock_code,
                    order_type=OrderType.LO,
                    side=OrderSide.Buy,
                    submitted_quantity=Decimal(qty_diff),
                    time_in_force=TimeInForceType.Day,
                    submitted_price=Decimal(current_price),
                    remark=f"Auto buy {qty_diff} shares"
                )
                print(f"买入订单提交结果: {resp}")

            elif change_type == "SELL" and qty_diff < 0:  # 需要卖出
                print(f"准备卖出 {stock_code}，数量: {-qty_diff}，价格: {current_price}")

                # 提交卖出订单（这里只是一个示例，实际应检查持仓）
                resp = self.submit_order(
                    symbol=stock_code,
                    order_type=OrderType.LO,
                    side=OrderSide.Sell,
                    submitted_quantity=Decimal(abs(qty_diff)),
                    time_in_force=TimeInForceType.Day,
                    submitted_price=Decimal(current_price),
                    remark=f"Auto sell {abs(qty_diff)} shares"
                )
                print(f"卖出订单提交结果: {resp}")

            else:
                print(f"{stock_code} 无需调整，当前持仓已匹配目标")


# --- 辅助函数 ---

def check_trading_hours(market='US'):
    """检查当前是否在交易时间"""
    # 获取股票市场信息
    trading_hours = {
        "US": {"start": "04:00", "end": "20:00"},  # 美股市场交易时间
        "HK": {"start": "09:30", "end": "16:00"}  # 香港市场交易时间
    }

    eastern = pytz.timezone('US/Eastern')
    hk = pytz.timezone('Asia/Hong_Kong')
    now = datetime.now(eastern) if market == "US" else datetime.now(hk)
    now_time = now.strftime("%H:%M")

    # 判断是否为周六或周日（weekday() 返回 5 表示周六，6 表示周日）
    if now.weekday() in [5, 6]:
        return False

    if trading_hours[market]["start"] <= now_time <= trading_hours[market]["end"]:
        return True
    else:
        return False

def load_last_known_data(portfolio_id):
    """从本地文件加载上次已知的数据，并确保数据格式正确。
    
    参数:
        portfolio_id (str): 组合ID，用于定位对应的本地文件
    返回:
        dict: 加载的数据，格式与 fetch_current_data 相同
    """
    local_data_file = PORTFOLIO_DATA_FILES.get(portfolio_id, f"last_known_stock_data_{portfolio_id}.json")
    
    if os.path.exists(local_data_file):
        try:
            with open(local_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 从文件 '{local_data_file}' 加载上次已知数据（组合: {portfolio_id}） 。")
                
                # 如果数据未经过预处理，则进行预处理
                if data.get('record_items') and 'stock_code_suffix' not in data['record_items'][0]:
                    processed_data = update_fetch_data(data)
                    save_current_data(processed_data, portfolio_id)
                    return processed_data
                
                return data
        except json.JSONDecodeError as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 读取本地文件 '{local_data_file}' 失败（JSON 解析错误）（组合ID: {portfolio_id}）: {e}")
            return None
        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 读取本地文件 '{local_data_file}' 失败（组合ID: {portfolio_id}）: {e}")
            return None
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 本地文件 '{local_data_file}' 不存在（组合ID: {portfolio_id}），将首次从云端获取数据。")
    return None

def save_current_data(data, portfolio_id):
    """将当前数据保存到本地文件。
    
    参数:
        data (dict): 要保存的数据
        portfolio_id (str): 组合ID，用于定位对应的本地文件
    """
    local_data_file = PORTFOLIO_DATA_FILES.get(portfolio_id, f"last_known_stock_data_{portfolio_id}.json")
    portfolio_name = PORTFOLIO_ID_NAMES.get(portfolio_id, "未知实盘")
    portfolio_banlance = PORTFOLIO_ID_BANLANCES.get(portfolio_id, 10000.0)
    data['portfolio_name'] = portfolio_name
    data['portfolio_id'] = portfolio_id
    data['portfolio_banlance'] = portfolio_banlance
    try:
        with open(local_data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 数据已保存到文件 '{local_data_file}'（组合ID: {portfolio_id}）。")
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 保存数据到文件 '{local_data_file}' 失败（组合ID: {portfolio_id}）: {e}")

def fetch_current_data(portfolio_id):
    """从 GET 接口获取当前数据并进行数据预处理，并根据组合ID过滤数据。
    
    参数:
        portfolio_id (str): 组合ID，用于过滤数据
    返回:
        dict: 预处理后的数据，包含该组合的持仓信息
    """
    try:
        # 构建带 portfolio_id 参数的 URL
        params = {
            "portfolio_id": portfolio_id,
            "language": '0'
        }
        response = requests.get(GET_API_URL, params=params, timeout=10) # 设置超时
        response.raise_for_status()  # 检查 HTTP 错误
        data = response.json()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 成功从云端获取数据（组合ID: {portfolio_id}）。")
        
        # 确保返回的数据结构正确
        if 'data' not in data:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 云端 JSON 数据结构不符合预期，缺少'data'字段（组合ID: {portfolio_id}）。")
            return None
        
        # 数据预处理
        processed_data = update_fetch_data(data.get('data'))
        
        # 返回预处理后的数据
        return processed_data
    except requests.exceptions.RequestException as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 从云端获取数据失败（组合ID: {portfolio_id}）: {e}")
        return None
    except KeyError:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 云端 JSON 数据结构不符合预期，缺少'data'字段（组合ID: {portfolio_id}）。")
        return None


def update_fetch_data(new_full_data):
    """
    对获取到的数据进行预处理，包括：
    1. 添加股票代码后缀（.HK/.US）
    2. 转换价格单位（除以10^9）
    3. 计算持仓比例
    """

    if new_full_data is None:
        return None

    market_ratio = dict([(item['market'], item['ratio']) for item in new_full_data.get('market_items', [])])

    updated_records = []
    for item_new in new_full_data.get('record_items', []):
        item_new['stock_code_suffix'] = 'HK' if item_new.get('market', 0) == 1 else ('US' if item_new.get('market', 0) == 2 else '')
        item_new['stock_code'] = item_new.get('stock_code', 'UNKNOWN')
        
        # 计算当前价格和成本价（单位转换）
        item_new['current_price'] = round(float(item_new.get('current_price', 0)) / 10**9, 2) if item_new.get('current_price') is not None else 0
        item_new['cost_price'] = round(float(item_new.get('cost_price', 0)) / 10**9, 2) if item_new.get('cost_price') is not None else 0
        
        # 计算持仓比例
        total_market_ratio = market_ratio.get(item_new.get('market', 0), 1)    # 默认为1，避免除以零
        item_new['total_ratio'] = round(float(item_new.get('total_ratio', 0)) / total_market_ratio * 100, 2) if total_market_ratio != 0 else 0
        item_new['position_ratio'] = round(float(item_new.get('position_ratio', 0)) / total_market_ratio * 100,
                                        2) if total_market_ratio != 0 else 0
        item_new['profit_and_loss_ratio'] = round(float(item_new.get('profit_and_loss_ratio', 0)) / total_market_ratio * 100,
                                        2) if total_market_ratio != 0 else 0

        
        # 添加更新后的数据到列表
        updated_records.append(item_new)

    updated_data = {
        'record_items': updated_records
    }
    # 返回更新后的数据
    return updated_data

def get_changes(old_full_data, new_full_data):
    """
    识别 record_items 之间的变化。
    参数:
        old_full_data (dict): 上一次获取的完整数据 (包含 record_items)
        new_full_data (dict): 本次获取的完整数据 (包含 record_items)
    返回:
        changed_items_list: 包含 (old_item, new_item) 对的列表，表示发生变化的股票。
                            如果某个股票是新增的，old_item 为 None；如果是删除的，new_item 为 None。
    """
    old_records = old_full_data.get('record_items', []) if old_full_data else []
    new_records = new_full_data.get('record_items', []) if new_full_data else []

    changes = []
    old_dict = {item['stock_code']: item for item in old_records}
    new_dict = {item['stock_code']: item for item in new_records}

    # 检查现有股票的变化或删除
    for code, old_item in old_dict.items():
        if code in new_dict:
            new_item = new_dict[code]
            # 比较关键字段：total_ratio、cost_price 和 current_price
            old_total_ratio = old_item.get('total_ratio', 0)
            new_total_ratio = new_item.get('total_ratio', 0)

            # 持仓比例超过1%才算变化
            if abs(old_total_ratio - new_total_ratio) > 1:
                changes.append((old_item, new_item))
        else:
            # 股票被移除
            changes.append((old_item, None))
    
    # 检查新增股票
    for code, new_item in new_dict.items():
        if code not in old_dict:
            changes.append((None, new_item))
            
    return changes

def send_email(subject, html_content):
    """
    发送 HTML 格式的邮件。
    """
    msg = MIMEMultipart('alternative')
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = subject

    msg.attach(MIMEText(html_content, 'html', 'utf-8'))

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        pass
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 邮件已成功发送到 {RECEIVER_EMAIL}。")

def generate_change_data(changed_items, portfolio_id):
    current_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')

    changes = []
    """生成每个股票变化的 HTML 片段"""
    sections_html = []

    for item_old, item_new in changed_items:
        if not item_old and not item_new:
            continue
        change_item = item_new if item_new else item_old
        # 获取股票名称和代码
        stock_name = change_item.get('stock_name', '未知股票')
        stock_code = change_item.get('stock_code', 'UNKNOWN')
        stock_code_suffix = change_item.get('stock_code_suffix', '')

        # 获取持仓比例
        old_total_ratio = item_old.get('total_ratio', 0) if item_old else 0
        new_total_ratio = item_new.get('total_ratio', 0) if item_new else 0

        # 获取参考成交价
        display_current_price = change_item.get('current_price', 0)
        # 获取成本价
        display_cost_price = change_item.get('cost_price', 0)

        old_ratio_str = f"{old_total_ratio:.2f}%"
        new_ratio_str = f"{new_total_ratio:.2f}%"

        # 根据变动类型生成不同的显示
        change_text = ""
        change_type = ""
        if item_old is None: # 新增股票
            change_text = f"0.00% -> {new_ratio_str}"
            change_type = "OPEN"
        elif item_new is None: # 删除股票
            change_text = f"{old_ratio_str} -> 0.00%"
            change_type = "CLOSE"
        else: # 股票数据变化
            change_text = f"{old_ratio_str} -> {new_ratio_str}"
            change_type = "BUY" if new_total_ratio > old_total_ratio else "SELL"

        sections_html.append(f"""
        <div style="margin-bottom: 20px; padding: 10px; border-bottom: 1px dashed #eee;">
            <div style="font-size: 16px; font-weight: bold; color: #555; margin-bottom: 5px;">{stock_name}</div>
            <div style="font-size: 14px; color: #777; margin-bottom: 5px;">{stock_code}</div>
            <div style="font-size: 15px; font-weight: bold; color: #007bff; margin-bottom: 5px;">{change_text}</div>
            <div style="font-size: 13px; color: #999;">参考成交价 {display_current_price:.3f}</div>
        </div>
        """)

        change_entry = {
            "stock_code": stock_code,
            "stock_code_suffix": stock_code_suffix,
            "stock_name": stock_name,
            "old_ratio_percent": old_total_ratio,
            "new_ratio_percent": new_total_ratio,
            "current_price": display_current_price,
            "cost_price": display_cost_price,
            "change_type": change_type
        }
        changes.append(change_entry)

    if not changes:
        return None, ""
    portfolio_name = PORTFOLIO_ID_NAMES.get(portfolio_id, "未知实盘")
    # 根据变化的数据和总市值比例创建类似图片样式的 HTML 卡片内容。
    sections_html_str = "\n".join(sections_html)
    html_template = f"""
    <div style="font-family: Arial, sans-serif; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; max-width: 600px; margin: 20px auto; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="font-size: 18px; font-weight: bold; color: #333; margin-bottom: 15px;">{portfolio_name} 调仓历史 - {current_time}</div>
        <hr style="border: none; border-top: 1px solid #eee; margin-bottom: 15px;">
        {sections_html_str}
        <div style="font-size: 12px; color: #888; margin-top: 20px;">
            此邮件由自动化程序发送，请勿直接回复。
        </div>
    </div>
    """

    json_output = {
        "timestamp": current_time,
        "portfolio_id": portfolio_id,
        "portfolio_name": portfolio_name,
        "changes": changes
    }

    return json_output, html_template


# --- 交易接口调用逻辑（修改为生成邮件并发送）---
def call_trade_api(old_full_data, new_full_data, trader=None, with_email=False, portfolio_id=""):
    """
    根据数据变化生成邮件卡片并发送。
    
    参数:
        old_full_data (dict): 上一次获取的完整数据
        new_full_data (dict): 本次获取的完整数据
        longport_trader (LongPortTrader): 交易接口实例
        with_email (bool): 是否发送邮件
        portfolio_id (str): 组合ID，用于日志和文件管理
        portfolio_name (str): 组合名称，用于邮件显示
    返回:
        bool: 是否有变化
    """
    portfolio_name = PORTFOLIO_ID_NAMES.get(portfolio_id, "未知实盘")
    has_changes = False
    # 获取变化列表和当前总市值比例
    changed_items = get_changes(old_full_data, new_full_data)
    # 只有当确实有股票发生变化时才发送邮件
    if changed_items:
        # 生成 HTML 邮件内容 和 JSON 内容
        json_content, html_content = generate_change_data(changed_items, portfolio_id)
        if json_content:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 检测到股票持仓数据变化（组合ID: {portfolio_id}）！")
            print(json.dumps(json_content, indent=4, ensure_ascii=False))
            # 仅当配置了实盘交易，才进行实盘交易
            if trader:
                trader.track_and_trade(json_content)
            if with_email:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 准备生成邮件卡片并发送（组合ID: {portfolio_id}）...")
                subject = f"【{portfolio_name}】股票持仓变动通知 - {datetime.now().strftime('%Y/%m/%d %H:%M')}"
                # 发送邮件
                send_email(subject, html_content)
            has_changes = True
        else:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 股票持仓数据无变化（组合ID: {portfolio_id}）。")
    else:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 股票持仓数据无变化（组合ID: {portfolio_id}）。")
    return has_changes


# --- 主程序逻辑 ---
def main():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 股票持仓监测程序启动...", flush=True)

    print(PORTFOLIO_ID_NAMES)
    print(PORTFOLIO_ID_BANLANCES)
    print(PORTFOLIO_DATA_FILES)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 以上是当前跟踪的实盘详情", flush=True)

    # 为每个组合创建独立的数据存储
    last_known_datas = {}
    for pid, pname in PORTFOLIO_ID_NAMES.items():
        last_known_datas[pid] = load_last_known_data(pid)

    #初始化实盘示例
    trader = None
    trader_set = os.getenv("TRADER")
    if trader_set == "longport":
        trader = LongPortTrader()
    elif trader_set == "futu":
        trader = FutuTrader()
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 券商选择：{trader_set}", flush=True)

    while True:
        trader.check_and_trade(last_known_datas)
        # 对每个组合执行检查和交易
        for pid, pname in PORTFOLIO_ID_NAMES.items():
            # 获取当前组合的数据
            current_full_data = fetch_current_data(pid)
            if current_full_data is None:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 本次获取云端数据失败（组合ID: {pid}），等待下次轮询。")
                continue

            # 获取上一次的数据
            last_known_full_data = last_known_datas.get(pid, None)
            if last_known_full_data is None:
                # 如果上次数据为空（例如首次运行或文件不存在/损坏），则直接将当前数据保存为基准
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 上次数据为空（组合ID: {pid}），已将本次成功获取的云端数据保存为基准。")
                save_current_data(current_full_data, pid)
                last_known_datas[pid] = current_full_data
                continue

            # 比较数据是否有变化
            has_changes = call_trade_api(last_known_full_data, current_full_data, trader, True, pid)
            if has_changes:
                save_current_data(current_full_data, pid)
                last_known_datas[pid] = current_full_data
        # 等待下一轮询
        interval_seconds = POLLING_INTERVAL_SECONDS if check_trading_hours() else 3600
        time.sleep(interval_seconds)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 新一轮查询开始...", flush=True)


if __name__ == "__main__":
    main()