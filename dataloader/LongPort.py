
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
        config = Config(
            app_key="fddd1f64ad477d0aea79928c749cc581",
            app_secret="d7873d6e17dbff6c0f1bb6ccf3f5a638f044ee9b6ba7f87e92399c8e8164357e",
            access_token="m_eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJsb25nYnJpZGdlIiwic3ViIjoiYWNjZXNzX3Rva2VuIiwiZXhwIjoxNzQyOTk4MzQ3LCJpYXQiOjE3MzUyMjIzNDMsImFrIjoiZmRkZDFmNjRhZDQ3N2QwYWVhNzk5MjhjNzQ5Y2M1ODEiLCJhYWlkIjoyMDUxMzYxNywiYWMiOiJsYl9wYXBlcnRyYWRpbmciLCJtaWQiOjEzNzY5MjY3LCJzaWQiOiJ1N1Fxak51RWd2ZzEydzhMNkR2WmF3PT0iLCJibCI6MywidWwiOjAsImlrIjoibGJfcGFwZXJ0cmFkaW5nXzIwNTEzNjE3In0.X3C9g7KJ8F_gjyRT5EOtC1q-b6pmTGHe9_vFHz8KwKuZSIPSC7elUdyprOlWNNfKLOS5_xFhIwDCDo62WHq0KRyTqUOELfPphSMiqkk5H9nICGNJ7Oi7vzuqppuj-kZNjTerY-h1G45l68GV6Uv0VpIuukRRQ9tziteG42GweV5UKp4qGJkQYK682ORptSlXNyhnMAOry-heuubpwtmrlh-J2U-NnbiKyuvEM_U9S2NkemF_AmirZ_hGPmJSjMRhrcoAavWrO4zMIKDSFE4zKn7R4h8ow32yWpaRQVIJU_NDto-lwAshytGq0TiE5EgEU_iizzvClaASfhgSUWht6sNhj5A4UHkIcB2-S5uMHLgkaIE-Zuvy1iglN-WpEFgTllR4HqEG2G_Vt9JqLGkCRNwYoOkyYIbQkbGIbx8dVivp12N0S5GOkCcedokKL-0SbuJ2HTD-How-mPRhUGeeSwJWQyXYHTOGy4X2j60J7R8koUMGATCLxWRnU94wbVDUe3yRfYqEYmWEmM8gQkOyZC2ozWcu0zysyjLVp4stCApl1c9XiDODdQFhBgUo_MFvKMG82X826EFfYkudW4zsgRsrHj5IIz5qWj0qzkiY1BOtDfMRwkyPi_gsagUaTsSk0RrKBEvOtZXKZvWHfDO5HXsC-NQ63wVb4nTBNH-mMmk",
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
    