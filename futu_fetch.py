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

# 加载环境变量
load_dotenv()  # 从 .env 文件加载环境变量

# --- 配置参数 ---
GET_API_URL = os.getenv("FUTU_POSITION_URL")  # 请替换为您的实际 GET 接口 URL
TRADE_API_URL = "YOUR_TRADE_API_URL_HERE" # 请替换为您的实际交易接口 URL (如果实际有交易接口，否则可以注释)
POLLING_INTERVAL_SECONDS = 5 # 轮询间隔（秒）
LOCAL_DATA_FILE = "last_known_stock_data.json" # 存储上次数据的本地文件名

# --- 邮件发送配置 ---
SENDER_EMAIL = "klb3713@qq.com" # 发件人邮箱，请替换为你的 QQ 邮箱
SENDER_PASSWORD = os.getenv("QQ_EMAIL_SENDER_PASSWORD") # 从环境变量中读取授权码
RECEIVER_EMAIL = "klb3713@qq.com" # 收件人邮箱
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465 # QQ 邮箱 SMTP 服务的 SSL 端口


class LongPortTrader():
    '''LongPort Store for backtrader'''

    def __init__(self, **kwargs):
        self.config = Config.from_env()
        self.ctx = TradeContext(self.config)
        self.quote_ctx = QuoteContext(self.config)
        self.usd_balance = 102640.00

    def track_and_trade(self, json_output):
        """
        根据持仓变化数据执行跟踪下单

        参数:
            json_output (dict): generate_change_data 返回的结构化数据
        """

        # 获取当前所有持仓
        current_positions = []
        resp = self.ctx.stock_positions()
        if resp.channels:
            current_positions = resp.channels[0].positions

        # 处理每个变化项
        for change in json_output.get("changes", []):
            stock_code = change["stock_code"]
            current_price = change["current_price"]
            change_type = change["change_type"]

            # 获取该股票的当前持仓
            current_position = next((pos for pos in current_positions if pos.symbol == stock_code), None)
            current_qty = current_position.quantity if current_position else 0

            # 计算目标仓位（这里只是一个示例，实际逻辑可能更复杂）
            target_ratio = change["new_ratio_percent"] / 100  # 目标持仓比例

            # 假设总市值资金为账户余额的一定比例（这只是一个简单示例）
            total_capital = self.usd_balance
            target_value = total_capital * target_ratio
            target_qty = int(target_value / current_price) if current_price > 0 else 0

            # 计算需要买入或卖出的数量
            qty_diff = target_qty - current_qty

            # 获取该股票最新的价格
            cur_quote = self.quote_ctx.quote([stock_code])[0]
            cur_quote_list = [(cur_quote.timestamp, cur_quote.last_done),
                              (cur_quote.pre_market_quote.timestamp, cur_quote.pre_market_quote.last_done),
                              (cur_quote.post_market_quote.timestamp, cur_quote.post_market_quote.last_done)]
            cur_quote_list.sort(key=lambda x: x[0], reverse=True)
            online_price = cur_quote_list[0][1]
            if change_type == "OPEN" or qty_diff > 0:
                current_price = min(online_price, current_price)
            elif change_type == "CLOSE" or qty_diff < 0:
                current_price = max(online_price, current_price)

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
                resp = self.ctx.submit_order(
                    symbol=stock_code,
                    order_type=OrderType.LO,
                    side=OrderSide.Buy,
                    submitted_quantity=Decimal(target_qty),
                    time_in_force=TimeInForceType.Day,
                    submitted_price=Decimal(current_price),
                    remark=f"Auto buy {target_qty} shares"
                )
                continue

            elif change_type == "CLOSE" and current_qty > 0:
                print(f"准备清仓卖出 {stock_code}，数量: {-current_qty}，价格: {current_price}")
                resp = self.ctx.submit_order(
                    symbol=stock_code,
                    order_type=OrderType.LO,
                    side=OrderSide.Sell,
                    submitted_quantity=Decimal(current_qty),
                    time_in_force=TimeInForceType.Day,
                    submitted_price=Decimal(current_price),
                    remark=f"Auto sell {current_qty} shares"
                )
                continue

            # 执行交易
            if qty_diff > 0:  # 需要买入
                print(f"准备买入 {stock_code}，数量: {qty_diff}，价格: {current_price}")

                # 提交买入订单（这里只是一个示例，实际应检查余额、保证金等）
                resp = self.ctx.submit_order(
                    symbol=stock_code,
                    order_type=OrderType.LO,
                    side=OrderSide.Buy,
                    submitted_quantity=Decimal(qty_diff),
                    time_in_force=TimeInForceType.Day,
                    submitted_price=Decimal(current_price),
                    remark=f"Auto buy {qty_diff} shares"
                )
                print(f"买入订单提交结果: {resp}")

            elif qty_diff < 0:  # 需要卖出
                print(f"准备卖出 {stock_code}，数量: {-qty_diff}，价格: {current_price}")

                # 提交卖出订单（这里只是一个示例，实际应检查持仓）
                resp = self.ctx.submit_order(
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
def load_last_known_data():
    """从本地文件加载上次已知的数据。"""
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
    """将当前数据保存到本地文件。"""
    try:
        with open(LOCAL_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 数据已保存到文件 '{LOCAL_DATA_FILE}'。")
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 保存数据到文件 '{LOCAL_DATA_FILE}' 失败: {e}")

def fetch_current_data():
    """从 GET 接口获取当前数据。"""
    try:
        response = requests.get(GET_API_URL, timeout=10) # 设置超时
        response.raise_for_status()  # 检查 HTTP 错误
        data = response.json()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 成功从云端获取数据。")
        # 返回 data 字段的完整内容，包含 market_items 和 record_items
        return data.get('data') 
    except requests.exceptions.RequestException as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 从云端获取数据失败: {e}")
        return None
    except KeyError:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 云端 JSON 数据结构不符合预期，缺少'data'字段。")
        return None

def get_changes(old_full_data, new_full_data):
    """
    识别 record_items 之间的变化。
    参数:
        old_full_data (dict): 上一次获取的完整数据 (包含 record_items 和 market_items)
        new_full_data (dict): 本次获取的完整数据 (包含 record_items 和 market_items)
    返回:
        tuple: (changed_items_list, current_market_ratio)
               changed_items_list: 包含 (old_item, new_item) 对的列表，表示发生变化的股票。
                                   如果某个股票是新增的，old_item 为 None；如果是删除的，new_item 为 None。
               current_market_ratio: 当前美股的总市值比例，用于后续计算持仓比例。
    """
    old_records = old_full_data.get('record_items', []) if old_full_data else []
    new_records = new_full_data.get('record_items', []) if new_full_data else []
    
    current_market_ratio = new_full_data.get('market_items', [{}])[0].get('ratio') if new_full_data.get('market_items') else 1 # 默认为1，避免除以零

    changes = []
    old_dict = {item['stock_code']: item for item in old_records}
    new_dict = {item['stock_code']: item for item in new_records}

    # 检查现有股票的变化或删除
    for code, old_item in old_dict.items():
        if code in new_dict:
            new_item = new_dict[code]
            # 比较关键字段，这里简单地比较整个字典的 JSON 字符串
            # 也可以是比较您关心的特定字段，例如:
            # if old_item.get('total_ratio') != new_item.get('total_ratio') or \
            #    old_item.get('position_ratio') != new_item.get('position_ratio'):
            if json.dumps(old_item, sort_keys=True) != json.dumps(new_item, sort_keys=True):
                changes.append((old_item, new_item))
        else:
            # 股票被移除
            changes.append((old_item, None))
    
    # 检查新增股票
    for code, new_item in new_dict.items():
        if code not in old_dict:
            changes.append((None, new_item))
            
    return changes, current_market_ratio

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
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 邮件已成功发送到 {RECEIVER_EMAIL}。")
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 发送邮件失败: {e}")


def generate_change_data(changed_items, total_market_ratio):
    current_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')

    changes = []
    """生成每个股票变化的 HTML 片段"""
    sections_html = []
    
    # 确保 total_market_ratio 是一个有效数字，避免除零错误
    if not isinstance(total_market_ratio, (int, float)) or total_market_ratio == 0:
        total_market_ratio = 1 # 作为备用值，避免计算错误

    for item_old, item_new in changed_items:
        stock_name = ""
        stock_code = ""
        market = 0
        old_total_ratio = 0
        new_total_ratio = 0
        display_current_price = 0 # 用于显示的参考成交价

        # 获取股票名称和代码
        if item_new:
            stock_name = item_new.get('stock_name', '未知股票')
            stock_code = item_new.get('stock_code', 'UNKNOWN')
            market = item_new.get('market', 0)
        elif item_old: # 如果是删除的，从旧数据获取名称
            stock_name = item_old.get('stock_name', '未知股票')
            stock_code = item_old.get('stock_code', 'UNKNOWN')
            market = item_old.get('market', 0)

        stock_code_suffix = '.HK' if market == 1 else ''
        stock_code_suffix = '.US' if market == 2 else ''
        stock_code = stock_code + stock_code_suffix

        # 获取持仓比例
        old_total_ratio = item_old.get('total_ratio', 0) if item_old else 0
        new_total_ratio = item_new.get('total_ratio', 0) if item_new else 0
        
        # 获取参考成交价
        if item_new and item_new.get('current_price') is not None:
             display_current_price = item_new.get('current_price') / 10**9
        elif item_old and item_old.get('current_price') is not None: # 对于删除项，使用旧的 current_price 作为参考
             display_current_price = item_old.get('current_price') / 10**9

        # 获取参考成交价
        if item_new and item_new.get('cost_price') is not None:
             display_cost_price = item_new.get('cost_price') / 10**9
        elif item_old and item_old.get('cost_price') is not None: # 对于删除项，使用旧的 current_price 作为参考
             display_cost_price = item_old.get('cost_price') / 10**9

        old_ratio_percent = old_total_ratio / total_market_ratio * 100
        new_ratio_percent = new_total_ratio / total_market_ratio * 100

        if abs(new_ratio_percent - old_ratio_percent) < 1:
            continue

        old_ratio_str = f"{old_ratio_percent:.2f}%"
        new_ratio_str = f"{new_ratio_percent:.2f}%"

        # 根据变动类型生成不同的显示
        change_text = ""
        if item_old is None: # 新增股票
            change_text = f"0.00% -> {new_ratio_str}"
        elif item_new is None: # 删除股票
            change_text = f"{old_ratio_str} -> 0.00%"
        else: # 股票数据变化
            change_text = f"{old_ratio_str} -> {new_ratio_str}"

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
            "current_price": round(display_current_price, 3),
            "cost_price": round(display_cost_price, 3),
            "change_type": "OPEN" if item_old is None else ("CLOSE" if item_new is None else "CHANGE")
        }
        changes.append(change_entry)

    if not changes:
        return None, ""

    # 根据变化的数据和总市值比例创建类似图片样式的 HTML 卡片内容。
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


# --- 交易接口调用逻辑（修改为生成邮件并发送）---
def call_trade_api(old_full_data, new_full_data, longport_trader=None, with_email=False):
    """
    根据数据变化生成邮件卡片并发送。
    """
    # 获取变化列表和当前总市值比例
    changed_items, total_market_ratio = get_changes(old_full_data, new_full_data)

    # 只有当确实有股票发生变化时才发送邮件
    if changed_items:
        # 生成 HTML 邮件内容 和 JSON 内容
        json_content, html_content = generate_change_data(changed_items, total_market_ratio)
        if json_content:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 检测到股票持仓数据变化！")
            print(json.dumps(json_content, indent=4, ensure_ascii=False))
            if longport_trader:
                longport_trader.track_and_trade(json_content)
            if with_email:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 准备生成邮件卡片并发送...")
                subject = f"股票持仓变动通知 - {datetime.now().strftime('%Y/%m/%d %H:%M')}"
                # 发送邮件
                send_email(subject, html_content)
        else:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 股票持仓数据无变化。")
    else:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 尽管数据整体结构有变动，但record_items内容无实质变化，不发送邮件。")


# --- 主程序逻辑 ---
def main():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 股票持仓监测程序启动...", flush=True)

    last_known_full_data = load_last_known_data()
    longport_trader = LongPortTrader()

    while True:
        current_full_data = fetch_current_data() # 获取完整的 data 字段内容

        if current_full_data is None:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 本次获取云端数据失败，等待下次轮询。")
            time.sleep(POLLING_INTERVAL_SECONDS)
            continue

        # 确保 record_items 存在，否则无法比较
        current_record_items = current_full_data.get('record_items', [])
        last_record_items = last_known_full_data.get('record_items', []) if last_known_full_data else []

        if last_known_full_data is not None:
            # 比较 record_items 是否有变化
            # 这里需要一个更精确的比较，因为即使 record_items 不变，total_market_ratio 也可能变
            # 我们只在 record_items 变化时发送邮件
            
            # 使用 json.dumps 比较 record_items 的内容来判断是否真的有“股票”变化
            if json.dumps(last_record_items, sort_keys=True) != json.dumps(current_record_items, sort_keys=True):
                call_trade_api(last_known_full_data, current_full_data, longport_trader, True) # 传入完整的旧数据和新数据
                save_current_data(current_full_data)
                last_known_full_data = current_full_data
            else:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 股票持仓数据无变化。")
                # 即使 record_items 无变化，market_items 可能会变，但我们只在股票变化时通知
        else:
            # 如果上次数据为空（例如首次运行或文件不存在/损坏），则直接将当前数据保存为基准
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 上次数据为空，已将本次成功获取的云端数据保存为基准。")
            save_current_data(current_full_data)
            last_known_full_data = current_full_data

        time.sleep(POLLING_INTERVAL_SECONDS)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 新一轮查询开始...", flush=True)


if __name__ == "__main__":
    main()