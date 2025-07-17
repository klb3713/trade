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
from futu import *

# 加载环境变量
load_dotenv("template.env")

# --- 配置参数 ---
GET_API_URL = os.getenv("FUTU_POSITION_URL")
POLLING_INTERVAL_SECONDS = int(os.getenv("POLLING_INTERVAL_SECONDS"))
LOCAL_DATA_FILE = "last_known_stock_data.json"
SENDER_EMAIL = os.getenv("QQ_EMAIL_SENDER_ACCOUNT")
SENDER_PASSWORD = os.getenv("QQ_EMAIL_SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv("QQ_EMAIL_RECEIVER_ACCOUNT")
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465

class FutuTrader:
    def __init__(self, **kwargs):
        self.host = os.getenv("FUTU_OPEND_HOST", "127.0.0.1")
        self.port = int(os.getenv("FUTU_OPEND_PORT", "11111"))
        self.password = os.getenv("FUTU_PASSWORD")
        self.trd_env = TrdEnv.SIMULATE if os.getenv("FUTU_TRD_ENV", "SIMULATE") == "SIMULATE" else TrdEnv.REAL
        self.acc_index = int(os.getenv("FUTU_ACC_INDEX", "0"))
        self.trd_ctx = OpenSecTradeContext(host=self.host, port=self.port, filter_trdmarket=TrdMarket.US)
        self.quote_ctx = OpenQuoteContext(host=self.host, port=self.port)
        self.usd_balance = float(os.getenv("USD_BANLANCE", "10000.00"))
        self.loss_threshold = float(os.getenv("LOSS_THRESHOLD", "0.01"))
        self.profit_threshold = float(os.getenv("PROFIT_THRESHOLD", "0.04"))
        if self.trd_env == TrdEnv.REAL:
            if not self.password:
                raise Exception("实盘交易需要设置 FUTU_PASSWORD")
            ret, data = self.trd_ctx.unlock_trade(self.password)
            if ret != RET_OK:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 解锁交易失败: {data}")
                raise Exception("交易解锁失败")

    def check_trading_hours(self, market='US'):
        """检查美股交易时间"""
        eastern = pytz.timezone('US/Eastern')
        now = datetime.now(eastern)
        now_time = now.strftime("%H:%M")
        trading_hours = {"start": "09:30", "end": "16:00"}
        return trading_hours["start"] <= now_time <= trading_hours["end"]

    def submit_order(self, symbol, order_type, side, submitted_quantity, time_in_force, submitted_price, remark):
        """提交订单"""
        max_retries = 3
        retry_delay = 5
        futu_order_type = OrderType.MARKET if order_type == "MARKET" else OrderType.NORMAL
        futu_side = TrdSide.BUY if side == "Buy" else TrdSide.SELL
        price = 0.0 if futu_order_type == OrderType.MARKET else float(submitted_price)

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

    def check_and_trade(self):
        """止盈止损"""
        ret, positions = self.trd_ctx.position_list_query(trd_env=self.trd_env, acc_index=self.acc_index)
        if ret != RET_OK:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 获取持仓失败: {positions}")
            return

        for pos in positions.to_dict('records'):
            stock_code = pos['code']
            cost_price = float(pos['cost_price'])
            current_qty = int(pos['qty'])
            
            if current_qty == 0:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 跳过持仓为 0 的股票: {stock_code}")
                continue


            ret, quote = self.quote_ctx.get_market_snapshot([stock_code])
            if ret != RET_OK:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 获取行情失败: {stock_code}")
                continue
            current_price = round(float(quote['last_price'][0]), 2)

            if not (current_price > 0 and cost_price > 0):
                continue

            if current_price < cost_price:
                loss = (cost_price - current_price) * current_qty
                if loss / self.usd_balance > self.loss_threshold:
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 准备止损 {stock_code}，数量: {current_qty}，价格: {current_price}")
                    resp = self.submit_order(
                        symbol=stock_code,
                        order_type="LO",
                        side="Sell",
                        submitted_quantity=Decimal(current_qty),
                        time_in_force="Day",
                        submitted_price=Decimal(current_price),
                        remark=f"Auto sell {current_qty} shares"
                    )
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 止损订单提交结果: {resp}")
            elif current_price > cost_price:
                profit = (current_price - cost_price) * current_qty
                if profit / self.usd_balance > self.profit_threshold:
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 准备止盈 {stock_code}，数量: {current_qty}，价格: {current_price}")
                    resp = self.submit_order(
                        symbol=stock_code,
                        order_type="LO",
                        side="Sell",
                        submitted_quantity=Decimal(current_qty),
                        time_in_force="Day",
                        submitted_price=Decimal(current_price),
                        remark=f"Auto sell {current_qty} shares"
                    )
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 止盈订单提交结果: {resp}")

    def track_and_trade(self, json_output):
        """跟踪下单"""
        ret, positions = self.trd_ctx.position_list_query(trd_env=self.trd_env, acc_index=self.acc_index)
        if ret != RET_OK:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 获取持仓失败: {positions}")
            return

        positions_dict = {pos['code']: pos for pos in positions.to_dict('records')}

        for change in json_output.get("changes", []):
            stock_code = change["stock_code"]
            current_price = change["current_price"]
            change_type = change["change_type"]

            ret, quote = self.quote_ctx.get_market_snapshot([stock_code])
            if ret != RET_OK:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 获取行情失败: {stock_code}")
                continue
            current_price = round(float(quote['last_price'][0]), 2)

            current_position = positions_dict.get(stock_code, None)
            current_qty = int(current_position['qty']) if current_position else 0

            if current_qty == 0 and change_type != "OPEN":
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 跳过持仓为 0 且非开仓的股票: {stock_code}")
                continue

            target_ratio = change["new_ratio_percent"] / 100
            current_ratio = current_qty * current_price / self.usd_balance if current_price > 0 else 0
            if abs(current_ratio - target_ratio) < 0.05:
                continue

            target_qty = int(self.usd_balance * target_ratio / current_price) if current_price > 0 else 0
            qty_diff = target_qty - current_qty

            if change_type == "OPEN" and target_qty > 0 and current_qty == 0:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 准备开仓买入 {stock_code}，数量: {target_qty}，价格: {current_price}")
                resp = self.submit_order(
                    symbol=stock_code,
                    order_type="LO",
                    side="Buy",
                    submitted_quantity=Decimal(target_qty),
                    time_in_force="Day",
                    submitted_price=Decimal(current_price),
                    remark=f"Auto buy {target_qty} shares"
                )
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 开仓买入订单提交结果: {resp}")
            elif change_type == "CLOSE" and current_qty > 0:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 准备清仓卖出 {stock_code}，数量: {current_qty}，价格: {current_price}")
                resp = self.submit_order(
                    symbol=stock_code,
                    order_type="LO",
                    side="Sell",
                    submitted_quantity=Decimal(current_qty),
                    time_in_force="Day",
                    submitted_price=Decimal(current_price),
                    remark=f"Auto sell {current_qty} shares"
                )
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 清仓卖出订单提交结果: {resp}")
            elif change_type == "BUY" and qty_diff > 0:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 准备买入 {stock_code}，数量: {qty_diff}，价格: {current_price}")
                resp = self.submit_order(
                    symbol=stock_code,
                    order_type="LO",
                    side="Buy",
                    submitted_quantity=Decimal(qty_diff),
                    time_in_force="Day",
                    submitted_price=Decimal(current_price),
                    remark=f"Auto buy {qty_diff} shares"
                )
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 买入订单提交结果: {resp}")
            elif change_type == "SELL" and qty_diff < 0:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 准备卖出 {stock_code}，数量: {-qty_diff}，价格: {current_price}")
                resp = self.submit_order(
                    symbol=stock_code,
                    order_type="LO",
                    side="Sell",
                    submitted_quantity=Decimal(abs(qty_diff)),
                    time_in_force="Day",
                    submitted_price=Decimal(current_price),
                    remark=f"Auto sell {abs(qty_diff)} shares"
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

# --- 辅助函数 ---
def load_last_known_data():
    """从本地文件加载上次已知的数据"""
    if os.path.exists(LOCAL_DATA_FILE):
        try:
            with open(LOCAL_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 从文件 '{LOCAL_DATA_FILE}' 加载上次已知数据。")
                return data
        except json.JSONDecodeError as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 读取本地文件 '{LOCAL_DATA_FILE}' 失败（JSON 解析错误）: {e}")
            return None
        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 读取本地文件 '{LOCAL_DATA_FILE}' 失败: {e}")
            return None
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 本地文件 '{LOCAL_DATA_FILE}' 不存在，将首次从云端获取数据。")
    return None

def save_current_data(data):
    """将当前数据保存到本地文件"""
    try:
        with open(LOCAL_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 数据已保存到文件 '{LOCAL_DATA_FILE}'。")
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 保存数据到文件 '{LOCAL_DATA_FILE}' 失败: {e}")

def fetch_current_data():
    """从 GET 接口获取当前数据"""
    try:
        response = requests.get(GET_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 成功从云端获取数据。")
        return data.get('data')
    except requests.exceptions.RequestException as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 从云端获取数据失败: {e}")
        return None
    except KeyError:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 云端 JSON 数据结构不符合预期，缺少'data'字段。")
        return None

def get_changes(old_full_data, new_full_data):
    """
    识别 record_items 之间的变化
    """
    old_records = old_full_data.get('record_items', []) if old_full_data else []
    new_records = new_full_data.get('record_items', []) if new_full_data else []
    
    current_market_ratio = new_full_data.get('market_items', [{}])[0].get('ratio') if new_full_data.get('market_items') else 1

    changes = []
    old_dict = {item['stock_code']: item for item in old_records}
    new_dict = {item['stock_code']: item for item in new_records}

    for code, old_item in old_dict.items():
        if code in new_dict:
            new_item = new_dict[code]
            if json.dumps(old_item, sort_keys=True) != json.dumps(new_item, sort_keys=True):
                changes.append((old_item, new_item))
        else:
            changes.append((old_item, None))
    
    for code, new_item in new_dict.items():
        if code not in old_dict:
            changes.append((None, new_item))
            
    return changes, current_market_ratio

def send_email(subject, html_content):
    """发送 HTML 格式的邮件"""
    msg = MIMEMultipart('alternative')
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    max_retries = 3
    retry_delay = 5
    for attempt in range(max_retries):
        try:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10)
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            try:
                server.quit()  # 显式关闭连接
            except Exception as e:
                traceback.print_exc()
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 关闭 SMTP 连接时出错: {str(e)}")
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 邮件已成功发送到 {RECEIVER_EMAIL}。")
            return
        except Exception as e:
            traceback.print_exc()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 邮件发送失败，尝试 {attempt + 1}/{max_retries}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 邮件发送失败，已达最大重试次数。")

def generate_change_data(changed_items, total_market_ratio):
    """生成变化数据和邮件内容"""
    current_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    changes = []
    sections_html = []

    if not isinstance(total_market_ratio, (int, float)) or total_market_ratio == 0:
        total_market_ratio = 1

    for item_old, item_new in changed_items:
        stock_name = ""
        stock_code = ""
        market = 0
        old_total_ratio = 0
        new_total_ratio = 0
        display_current_price = 0
        display_cost_price = 0

        if item_new:
            stock_name = item_new.get('stock_name', '未知股票')
            stock_code = item_new.get('stock_code', 'UNKNOWN')
            market = item_new.get('market', 0)
        elif item_old:
            stock_name = item_old.get('stock_name', '未知股票')
            stock_code = item_old.get('stock_code', 'UNKNOWN')
            market = item_old.get('market', 0)

        stock_code_suffix = '.HK' if market == 1 else ''
        stock_code_suffix = '.US' if market == 2 else ''
        stock_code = stock_code + stock_code_suffix

        old_total_ratio = item_old.get('total_ratio', 0) if item_old else 0
        new_total_ratio = item_new.get('total_ratio', 0) if item_new else 0
        
        if item_new and item_new.get('current_price') is not None:
            display_current_price = item_new.get('current_price') / 10**9
        elif item_old and item_old.get('current_price') is not None:
            display_current_price = item_old.get('current_price') / 10**9

        if item_new and item_new.get('cost_price') is not None:
            display_cost_price = item_new.get('cost_price') / 10**9
        elif item_old and item_old.get('cost_price') is not None:
            display_cost_price = item_old.get('cost_price') / 10**9

        old_ratio_percent = old_total_ratio / total_market_ratio * 100
        new_ratio_percent = new_total_ratio / total_market_ratio * 100

        if abs(new_ratio_percent - old_ratio_percent) < 1:
            continue

        old_ratio_str = f"{old_ratio_percent:.2f}%"
        new_ratio_str = f"{new_ratio_percent:.2f}%"

        change_text = ""
        change_type = ""
        if item_old is None:
            change_text = f"0.00% -> {new_ratio_str}"
            change_type = "OPEN"
        elif item_new is None:
            change_text = f"{old_ratio_str} -> 0.00%"
            change_type = "CLOSE"
        else:
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
            "stock_name": stock_name,
            "old_ratio_percent": round(old_ratio_percent, 2),
            "new_ratio_percent": round(new_ratio_percent, 2),
            "current_price": round(display_current_price, 2),
            "cost_price": round(display_cost_price, 2),
            "change_type": change_type
        }
        changes.append(change_entry)

    if not changes:
        return None, ""

    sections_html_str = "\n".join(sections_html)
    html_template = f"""
    <div style="font-family: Arial, sans-serif; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; max-width: 600px; margin: 20px auto; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="font-size: 18px; font-weight: bold; color: #333; margin-bottom: 15px;">调仓历史 - {current_time}</div>
        <hr style="border: none; border-top: 1px solid #eee; margin-bottom: 15px;">
        {sections_html_str}
        <div style="font-size: 12px; color: #888; margin-top: 20px;">
            此邮件由自动化程序发送，请勿直接回复。
        </div>
    </div>
    """

    json_output = {
        "timestamp": current_time,
        "total_market_ratio": total_market_ratio,
        "changes": changes
    }

    return json_output, html_template

def call_trade_api(old_full_data, new_full_data, futu_trader=None, with_email=False):
    """根据数据变化生成邮件卡片并发送"""
    has_changes = False
    changed_items, total_market_ratio = get_changes(old_full_data, new_full_data)

    if changed_items:
        json_content, html_content = generate_change_data(changed_items, total_market_ratio)
        if json_content:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 检测到股票持仓数据变化！")
            print(json.dumps(json_content, indent=4, ensure_ascii=False))
            if futu_trader:
                futu_trader.track_and_trade(json_content)
            if with_email:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 准备生成邮件卡片并发送...")
                subject = f"股票持仓变动通知 - {datetime.now().strftime('%Y/%m/%d %H:%M')}"
                send_email(subject, html_content)
            has_changes = True
        else:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 股票持仓数据无变化。")
    else:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 尽管数据整体结构有变动，但record_items内容无实质变化，不发送邮件。")
    return has_changes

def main():
    """主程序逻辑"""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 股票持仓监测程序启动...", flush=True)
    last_known_full_data = load_last_known_data()
    futu_trader = FutuTrader()

    try:
        while True:
            futu_trader.check_and_trade()
            current_full_data = fetch_current_data()
            interval_seconds = POLLING_INTERVAL_SECONDS if futu_trader.check_trading_hours() else 3600
            if current_full_data is None:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 本次获取云端数据失败，等待下次轮询。")
                time.sleep(interval_seconds)
                continue

            current_record_items = current_full_data.get('record_items', [])
            last_record_items = last_known_full_data.get('record_items', []) if last_known_full_data else []

            if last_known_full_data is not None:
                if json.dumps(last_record_items, sort_keys=True) != json.dumps(current_record_items, sort_keys=True):
                    has_changes = call_trade_api(last_known_full_data, current_full_data, futu_trader, True)
                    if has_changes:
                        save_current_data(current_full_data)
                    last_known_full_data = current_full_data
                else:
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 股票持仓数据无变化。")
            else:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 上次数据为空，已将本次成功获取的云端数据保存为基准。")
                save_current_data(current_full_data)
                last_known_full_data = current_full_data

                subject = f"首次更新投资组合通知 - {datetime.now().strftime('%Y/%m/%d %H:%M')}"
                sections_html = []
                record_items = current_full_data.get('record_items', [])
                total_market_ratio = current_full_data.get('market_items', [{}])[0].get('ratio', 1)

                for item in record_items:
                    stock_name = item.get('stock_name', '未知股票')
                    stock_code = item.get('stock_code', 'UNKNOWN')
                    market = item.get('market', 0)
                    stock_code_suffix = '.HK' if market == 1 else '.US' if market == 2 else ''
                    stock_code = stock_code + stock_code_suffix
                    total_ratio = item.get('total_ratio', 0)
                    ratio_percent = total_ratio / total_market_ratio * 100 if total_market_ratio != 0 else 0
                    current_price = item.get('current_price', 0) / 10**9 if item.get('current_price') is not None else 0
                    cost_price = item.get('cost_price', 0) / 10**9 if item.get('cost_price') is not None else 0

                    sections_html.append(f"""
                    <div style="margin-bottom: 20px; padding: 10px; border-bottom: 1px dashed #eee;">
                        <div style="font-size: 16px; font-weight: bold; color: #555; margin-bottom: 5px;">{stock_name}</div>
                        <div style="font-size: 14px; color: #777; margin-bottom: 5px;">{stock_code}</div>
                        <div style="font-size: 15px; font-weight: bold; color: #007bff; margin-bottom: 5px;">持仓比例: {ratio_percent:.2f}%</div>
                        <div style="font-size: 13px; color: #999;">参考成交价: {current_price:.3f}</div>
                        <div style="font-size: 13px; color: #999;">成本价: {cost_price:.3f}</div>
                    </div>
                    """)

                sections_html_str = "\n".join(sections_html) if sections_html else "<div style='font-size: 14px; color: #555;'>暂无投资组合数据</div>"
                html_content = f"""
                <div style="font-family: Arial, sans-serif; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; max-width: 600px; margin: 20px auto; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="font-size: 18px; font-weight: bold; color: #333; margin-bottom: 15px;">首次更新投资组合 - {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}</div>
                    <hr style="border: none; border-top: 1px solid #eee; margin-bottom: 15px;">
                    {sections_html_str}
                    <div style="font-size: 12px; color: #888; margin-top: 20px;">
                        此邮件由自动化程序发送，请勿直接回复。
                    </div>
                </div>
                """
                send_email(subject, html_content)

            time.sleep(interval_seconds)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 新一轮查询开始...", flush=True)
    finally:
        futu_trader.close()

if __name__ == "__main__":
    main()