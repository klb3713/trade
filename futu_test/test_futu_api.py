from futu import *

trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.get_acc_list()
if ret == RET_OK:
    print(data)
    print(data['acc_id'][0])  # 取第一个账号
    print(data['acc_id'].values.tolist())  # 转为 list
else:
    print('get_acc_list error: ', data)
trd_ctx.close()

exit(0)

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret_sub, err_message = quote_ctx.subscribe(['US.AAPL'], [SubType.QUOTE], subscribe_push=False)
# 先订阅 K 线类型。订阅成功后 OpenD 将持续收到服务器的推送，False 代表暂时不需要推送给脚本
if ret_sub == RET_OK:  # 订阅成功
    ret, data = quote_ctx.get_stock_quote(['US.AAPL'])  # 获取订阅股票报价的实时数据
    if ret == RET_OK:
        print(data)
        print(data['code'][0])   # 取第一条的股票代码
        print(data['code'].values.tolist())   # 转为 list
    else:
        print('error:', data)
else:
    print('subscription failed', err_message)
quote_ctx.close()  # 关闭当条连接，OpenD 会在1分钟后自动取消相应股票相应类型的订阅


trd_ctx = OpenSecTradeContext(host='127.0.0.1', port=11111)  # 创建交易对象
print(trd_ctx.place_order(price=500.0, qty=100, code="HK.00700", trd_side=TrdSide.BUY, trd_env=TrdEnv.SIMULATE))  # 模拟交易，下单（如果是真实环境交易，在此之前需要先解锁交易密码）

trd_ctx.close()  # 关闭对象，防止连接条数用尽
