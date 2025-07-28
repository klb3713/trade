import pandas as pd
import akshare as ak
import time
from datetime import datetime

# 读取基金信息文件
fund_info_path = '/Users/klb3713/work/trade/fund_eval/fund_info.csv'
fund_df = pd.read_csv(fund_info_path)

# 创建一个新的DataFrame来存储结果
result_df = fund_df.copy()

# 添加新列用于存储净值估算数据
result_df['估算值'] = None
result_df['估算增长率'] = None
result_df['公布单位净值'] = None
result_df['公布日增长率'] = None

# 获取所有基金的净值估算数据
print("正在获取基金净值估算数据...")
fund_estimation_df = ak.fund_value_estimation_em(symbol="全部")

# 标准化基金代码格式（确保都是6位数字的字符串，不足6位的前面补0）
fund_df['基金代码'] = fund_df['基金代码'].apply(lambda x: f"{int(x):06d}")
fund_estimation_df['基金代码'] = fund_estimation_df['基金代码'].astype(str)

# 获取估算数据的日期（从列名中解析）
date_str = datetime.now().strftime('%Y-%m-%d')
est_value_col = f'{date_str}-估算数据-估算值'
est_growth_col = f'{date_str}-估算数据-估算增长率'
pub_value_col = f'{date_str}-公布数据-单位净值'
pub_growth_col = f'{date_str}-公布数据-日增长率'

# 检查列是否存在，如果不存在则使用实际的列名
actual_columns = fund_estimation_df.columns.tolist()
est_value_col_actual = [col for col in actual_columns if '估算数据-估算值' in col][0] if any('估算数据-估算值' in col for col in actual_columns) else None
est_growth_col_actual = [col for col in actual_columns if '估算数据-估算增长率' in col][0] if any('估算数据-估算增长率' in col for col in actual_columns) else None
pub_value_col_actual = [col for col in actual_columns if '公布数据-单位净值' in col][0] if any('公布数据-单位净值' in col for col in actual_columns) else None
pub_growth_col_actual = [col for col in actual_columns if '公布数据-日增长率' in col][0] if any('公布数据-日增长率' in col for col in actual_columns) else None

print(f"使用的列名:")
print(f"估算值列: {est_value_col_actual}")
print(f"估算增长率列: {est_growth_col_actual}")
print(f"公布单位净值列: {pub_value_col_actual}")
print(f"公布日增长率列: {pub_growth_col_actual}")

# 为每个基金查找对应的估算数据
found_count = 0
for index, row in fund_df.iterrows():
    fund_code = row['基金代码']
    
    # 在估算数据中查找匹配的基金
    estimation_row = fund_estimation_df[fund_estimation_df['基金代码'] == fund_code]
    
    if not estimation_row.empty:
        # 提取估算数据
        if est_value_col_actual:
            result_df.at[index, '估算值'] = estimation_row[est_value_col_actual].values[0]
        if est_growth_col_actual:
            result_df.at[index, '估算增长率'] = estimation_row[est_growth_col_actual].values[0]
        if pub_value_col_actual:
            result_df.at[index, '公布单位净值'] = estimation_row[pub_value_col_actual].values[0]
        if pub_growth_col_actual:
            result_df.at[index, '公布日增长率'] = estimation_row[pub_growth_col_actual].values[0]
        
        found_count += 1
    else:
        print(f"未找到基金 {fund_code} 的估算数据")
    
    # 添加短暂延迟以避免请求过于频繁
    time.sleep(0.01)

print(f"\n总共找到了 {found_count} 个基金的估算数据")

# 保存更新后的数据到新文件
output_path = '/Users/klb3713/work/trade/fund_eval/fund_info_with_estimation.csv'
result_df.to_csv(output_path, index=False)
print(f"数据已保存到 {output_path}")