import yfinance as yf
import pandas as pd

DOW_30_TICKER = [
    "AXP",
    # "AMGN",
    # "AAPL",
    # "BA",
    # "CAT",
    # "CSCO",
    # "CVX",
    # "GS",
    # "HD",
    # "HON",
    # "IBM",
    # "INTC",
    # "JNJ",
    # "KO",
    # "JPM",
    # "MCD",
    # "MMM",
    # "MRK",
    # "MSFT",
    # "NKE",
    # "PG",
    # "TRV",
    # "UNH",
    # "CRM",
    # "VZ",
    # "V",
    # "WBA",
    # "WMT",
    # "DIS",
    # "DOW",
]
class YahooDataloader:
  #通过雅虎金融API接口提供获取日常股票数据
   def __init__(self,start_date:str,end_date:str,ticker_list:list):#构造函数，用来实例化对象
     self.start_date=start_date
     self.end_date=end_date 
     self.ticker_list=ticker_list
   def fetch_data(self,proxy=None):
     #抓取数据，返回pd.DataFrame 7 columns:A date,open,high,low,close,volume and tick symbol
     data_df=pd.DataFrame()
     for tic in self.ticker_list:
       temp_df=yf.download(tic,start=self.start_date,end=self.end_date,proxy=proxy, rounding=True)
       temp_df['tic']=tic
       data_df = pd.concat([data_df, temp_df])
    #    print("刚下载的数据：" )
    #    print(temp_df)
     print(data_df.head(5))
     data_df.sort_values(by=['Date'], inplace=True, ascending=False)

     data_df.reset_index(inplace=True) #会将原来的索引index作为新的一列,使日期作为新的一列
     print("使日期作为新的一列:")
     print(data_df.head(5))

     try:
     #修改列名
       data_df.columns=["date","open","high","low","close","adjcp","volumn","tic"]
       #使用调整后的收盘价去代替收盘价
       data_df["close"]=data_df["adjcp"]
       data_df["openinterest"]=0
        #删除调整后的收盘价那一列
       data_df=data_df.drop(labels="adjcp",axis=1)
     except NotImplementedError:
       print("the features are not supported currently")
  
     #创建一周中的天数（星期一是0,星期天是6）：Pandas.Series.dt.dayofweek
     data_df['day']=data_df['date'].dt.dayofweek
     #时间字符串转换为年月日方法,可以容易过滤
     data_df['date']=data_df.date.apply(lambda x:x.strftime("%Y-%m-%d"))
     #去除读入的数据中（DataFrame）含有NaN的行。
     data_df=data_df.dropna()
     data_df=data_df.reset_index(drop=True)#重置索引
     print("处理后的数据:")
     print(data_df.head(5))
     print("Shape of DataFrame: ", data_df.shape)
     # print("Display DataFrame: ", data_df.head())
     data_df = data_df.sort_values(by=[ "tic","date"]).reset_index(drop=True)
     data_df.to_csv("data.csv")
     return data_df
  

# StartDate_T = '2017-12-20'
# EndDate_T = '2022-05-14'
# df = YahooDataloader(start_date = StartDate_T,
#                      end_date = EndDate_T,
#                      ticker_list = DOW_30_TICKER).fetch_data()



