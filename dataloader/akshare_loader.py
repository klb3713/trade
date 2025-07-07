
import pandas as pd
from datetime import datetime
import akshare as ak
import pandas_ta as ta


class AkshareData():
    def __init__(self):
        pass

    @classmethod
    def get_fund_data(cls, symbol="018124", period="1_year"):
        df = ak.fund_open_fund_info_em(symbol=symbol, indicator="累计净值走势")

        df["trade_date"] = pd.to_datetime(df["净值日期"])
        df.set_index("trade_date", inplace=True)
        df.index.name = "Datetime"
        df.sort_index(inplace=True)
        df['Open'] = df['High'] = df['Low'] = df['Close'] = df['累计净值']
        # 设置今日的开盘价为昨日的收盘价
        df.Open = df.Close.shift(1, fill_value=1.0)

        for idx, data in df.iterrows():
            df.loc[idx, 'High'] = max(data.Open, data.Close)
            df.loc[idx, 'Low'] = min(data.Open, data.Close)

        # 保留近一年的数据用来回测
        if period == "1_year":
            one_year_ago = pd.to_datetime(datetime.now()) - pd.DateOffset(years=1)
            df = df.loc[df.index > one_year_ago]
        elif period == "3_year":
            three_years_ago = pd.to_datetime(datetime.now()) - pd.DateOffset(years=3)
            df = df.loc[df.index > three_years_ago]
        elif period == "5_year":
            five_years_ago = pd.to_datetime(datetime.now()) - pd.DateOffset(years=5)
            df = df.loc[df.index > five_years_ago]

        return df



if __name__ == '__main__':
    df = AkshareData.get_fund_data("017847", '1_year')
    print(df.head())
