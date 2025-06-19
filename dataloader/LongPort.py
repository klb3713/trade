
from dataloader import BaseDataLoader

import backtrader as bt
import datetime
from longport.openapi import QuoteContext, Config, SubType, PushQuote, Period, AdjustType
import pandas as pd

class LongPortData(BaseDataLoader):
    '''
    从longport读取香港股票数据日线
    '''

    def __init__(self,isplot=False):
        super().__init__()
        config = Config(
            app_key="fddd1f64ad477d0aea79928c749cc581",
            app_secret="d7873d6e17dbff6c0f1bb6ccf3f5a638f044ee9b6ba7f87e92399c8e8164357e",
            access_token="m_eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJsb25nYnJpZGdlIiwic3ViIjoiYWNjZXNzX3Rva2VuIiwiZXhwIjoxNzU3ODM3MDAyLCJpYXQiOjE3NTAwNjEwMDIsImFrIjoiZmRkZDFmNjRhZDQ3N2QwYWVhNzk5MjhjNzQ5Y2M1ODEiLCJhYWlkIjoyMDUxMzYxNywiYWMiOiJsYl9wYXBlcnRyYWRpbmciLCJtaWQiOjEzNzY5MjY3LCJzaWQiOiJMVUZmbWlyREYrN0VHQzVwVmQvcGZRPT0iLCJibCI6MywidWwiOjAsImlrIjoibGJfcGFwZXJ0cmFkaW5nXzIwNTEzNjE3In0.O93MXh1QulHf-Y-OHxw6N5DhCNfzxXPPVifRFKNLnqOYnzw3C0bb4RAI80BbaxHSnlCdvBw4skQpaiphBa06Avhc0jfNopB8ZkZRuJPgowSuKHL28mxMwekYSlsU_Z204-pczXDoa1CENF1i4NSSZOuYf1UAxcgLRRDY8Py96qiYm0ng7V9N4puIEATrvEVgE05yGPmLhf9sCMTSK5Zf99svbGykngUFhLQrxZuHEe_b_HsKd1yletyDZ_xn0d_9vTHyXPXik2H_rsG-5Mni6gLYuyv5y9BtbwDonfR1OUMXGoQBqwWmq1Z0oX2lzTXurBljlkhiBW_GMalpS03ssOWZyIO6xtFlOdt0FGWtMybGVXWVexUxWcbGOskWPXrOyoof8XOnG9QUknFNj0hYLYdZAMpECkQ-un7jVoj-Bx5itJjb6Y3BP94BAuNK41mMHcxOhfwZLlGafImxX8PVkKzt6wpZjCzwN2MOB7YclWcn4uE3H1D4ierQl5Wh3mayCS2gLH6Pcpxz5OnuYEWctZ3N8B92yI7zTu5xysyEKIySYL4ZTMd_IrlYsrwHN_xYp2BOcRpt2XQB2sw7qFQCsaHQlNy1Jo6IfbgNAqeZLhhekcLOo4Wttei8cVG5hnlbQz-A7eQ64gjtbl_3aQkxgtkYHsYJ0v3b1Tez4HoG_LM",
            enable_overnight=True)
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

        dfs = []
        stock_ids = stock_ids.split(",")
        for i in stock_ids:
            print(i)
        for stock_id in stock_ids:
            data_dict = {col: [] for col in columns}

            try:
                # 加载数据
                candlesticks = self.ctx.history_candlesticks_by_date(stock_id, Period.Day, AdjustType.NoAdjust, dt_start_time, dt_end_time)
                for row in candlesticks:
                    data_dict['open'].append(float(row.open))
                    data_dict['high'].append(float(row.high))
                    data_dict['low'].append(float(row.low))
                    data_dict['close'].append(float(row.close))
                    data_dict['volume'].append(float(row.volume))
                    data_dict['openinterest'].append(0)
                    data_dict['datetime'].append(row.timestamp)
                    data_dict['name'].append(stock_id)
                
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
                dfs.append(df)

            except Exception as err:
                print("下载{0}完毕失败！")
                print("失败原因 = " + str(err))

        return self.data,dfs
    