import akshare as ak
import pandas as pd

# 获取基金净值估算数据
print("正在获取基金净值估算数据...")
fund_estimation_df = ak.fund_value_estimation_em(symbol="全部")

# 显示数据的列名
print("列名:")
print(fund_estimation_df.columns.tolist())

# 显示前几行数据
print("\n前5行数据:")
print(fund_estimation_df.head())

# 显示数据形状
print("\n数据形状:")
print(fund_estimation_df.shape)