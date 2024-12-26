
from dataloader import BaseDataLoader

import backtrader as bt
import datetime
from longport.openapi import QuoteContext, Config, SubType, PushQuote, Period, AdjustType
import pandas as pd

class LongPortData(BaseDataLoader):
    '''
    从longport读取香港股票数据日线
    '''

    def __init__(self,isplot=True):
        super().__init__()
        config = Config.from_env()
        self.ctx = QuoteContext(config)
        self.isplot = isplot

    # 从longport在线读取数据
    def fetch_data(self, 
                   stock_ids,
                   start_time=None,
                   end_time=None):
        
        dt_start_time = datetime.datetime.strptime(start_time, "%Y%m%d")
        dt_end_time = datetime.datetime.strptime(end_time, "%Y%m%d")
        
        # 前7列必须是 ['open','high', 'low', 'close','volume', 'openinterest']
        columns = ['open','high', 'low', 'close','volume', 'openinterest' , 'datetime' , 'name']
        data_dict = {col: [] for col in columns}

        try:
            # 加载数据
            candlesticks = self.ctx.history_candlesticks_by_date(stock_ids, Period.Day, AdjustType.NoAdjust, dt_start_time, dt_end_time)
            for row in candlesticks:
                data_dict['open'].append(float(row.open))
                data_dict['high'].append(float(row.high))
                data_dict['low'].append(float(row.low))
                data_dict['close'].append(float(row.close))
                data_dict['volume'].append(float(row.volume))
                data_dict['openinterest'].append(0)
                data_dict['datetime'].append(row.timestamp)
                data_dict['name'].append(stock_ids)
            
            df = pd.DataFrame(data_dict)

            # 将日期列，设置成index
            df.index = pd.to_datetime(df.datetime, format='%Y%m%d')
            # 时间必须递增
            df = df.sort_index()


            self.data.append(bt.feeds.PandasData(name = df['name'][0],
                                                     dataname=df,
                                                     fromdate=dt_start_time,
                                                     todate=dt_end_time,
                                                     plot=self.isplot))
            
            print(df)

        except Exception as err:
            print("下载{0}完毕失败！")
            print("失败原因 = " + str(err))

        return self.data
    