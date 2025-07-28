import pandas as pd
import akshare as ak

# 读取基金信息文件
fund_info_path = '/Users/klb3713/work/trade/fund_eval/fund_info.csv'
fund_df = pd.read_csv(fund_info_path)

# 获取所有基金的净值估算数据
print("正在获取基金净值估算数据...")
fund_estimation_df = ak.fund_value_estimation_em(symbol="全部")

# 显示基金代码的样本数据
print("原始基金信息文件中的基金代码样本:")
print(fund_df['基金代码'].head(10))

print("\n基金估算数据中的基金代码样本:")
print(fund_estimation_df['基金代码'].head(10))

# 检查数据类型
print(f"\n原始基金信息文件中基金代码的数据类型: {fund_df['基金代码'].dtype}")
print(f"基金估算数据中基金代码的数据类型: {fund_estimation_df['基金代码'].dtype}")

# 检查是否有任何匹配的基金代码
print(f"\n原始基金信息文件中的基金代码数量: {len(fund_df['基金代码'])}")
print(f"基金估算数据中的基金代码数量: {len(fund_estimation_df['基金代码'])}")

# 尝试查找一些匹配项
common_funds = set(fund_df['基金代码']).intersection(set(fund_estimation_df['基金代码']))
print(f"\n匹配的基金代码数量: {len(common_funds)}")
if common_funds:
    print("前10个匹配的基金代码:")
    print(list(common_funds)[:10])
else:
    print("没有找到匹配的基金代码")