from decimal import Decimal
from longport.openapi import TradeContext, Config

config = Config.from_env()
ctx = TradeContext(config)

ctx.replace_order(
    order_id = "709043056541253632",
    quantity = Decimal(100),
    price = Decimal(50),
)

history_orders = ctx.history_orders(
    symbol = 'YANG.US'
)

today_orders = ctx.today_orders(
    symbol = 'YANG.US'
)

stock_postions = ctx.stock_positions(['YANG.US'])

print(history_orders)
print(today_orders)