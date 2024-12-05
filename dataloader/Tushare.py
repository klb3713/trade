
from dataloader import BaseDataLoader

import backtrader as bt
import tushare as ts
import datetime
import pandas as pd

class TushareData(BaseDataLoader):
    '''
    从Tushare读取A股票数据日线
    '''

    def __init__(self,isplot=True):
        super().__init__()
        self.pro = ts.pro_api('2f9b94e7c50c282c3688c6425d3a08ee96a2c4b0f119743bc454c0d9')
        self.isplot = isplot

    # 从tushare在线读取数据
    def fetch_data(self, 
                   stock_ids,
                   start_time=None,
                   end_time=None):
        
        dt_start_time = datetime.datetime.strptime(start_time, "%Y%m%d")
        dt_end_time = datetime.datetime.strptime(end_time, "%Y%m%d")
        
        try:
            # 加载数据
            df = self.pro.daily(ts_code=stock_ids, start_date=start_time, end_date=end_time)
            # 将日期列，设置成index
            df.index = pd.to_datetime(df.trade_date, format='%Y%m%d')
            # 时间必须递增
            df = df.sort_index()

            # 前7列必须是 ['open','high', 'low', 'close','volume', 'openinterest']
            df['openinterest']  = 0
            df=df.rename(columns={"vol": "volume"})
            # 统一股票有一个属性叫name
            df=df.rename(columns={"ts_code": "name"})
            df = df[['open','high', 'low', 'close','volume', 'openinterest','name']]
            # 获取 name 列表并去重
            class_list = list(df['name'].drop_duplicates())
            # 按照类别分文件存放数据
            for i in class_list:
                tmp = df[df['name']==i]
                self.data.append(bt.feeds.PandasData(name = i,
                                                     dataname=tmp,
                                                     fromdate=dt_start_time,
                                                     todate=dt_end_time,
                                                     plot=self.isplot))

        except Exception as err:
            print("下载{0}完毕失败！")
            print("失败原因 = " + str(err))

        return self.data
    

