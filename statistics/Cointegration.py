import os
from statsmodels.tsa.stattools import adfuller
import numpy as np
import pandas as pd
from arch.unitroot import ADF                     # 协整关系检验
import statsmodels.api as sm
import matplotlib.pyplot as plt
from statistics import BaseStatistics


class Cointegration(BaseStatistics):

    def __init__(self, data):
        super().__init__(data)

    def process(self):
        print('This is Cointegration!')
        pair = []
        for i in self.data:
            # 获取每日收盘价格列表
            value = i['close']
            # 调用方法判断是否符合协整关系
            log_P_value = np.log(value)
            adf_value = ADF(log_P_value.diff()[1:])
            print(adf_value.summary().as_text())
            pair.append(log_P_value)

            # log_P_mstx_value.plot()
            # plt.title('图1 中国银行对数收益率序列趋势（形成期）')
            # plt.show()

            log_P_value.diff()[1:].plot()
            plt.title('图2 中国银行差分对数收益率序列趋势（形成期）')
            plt.show()

        # 按日期对齐
        # 找size最小的那个
        index_max = 0
        index_min = 0
        if pair[0].size > pair[1].size:
            index_max = 0
            index_min = 1
        else:
            index_max = 1
            index_min = 0
                
        result = pd.merge(pair[0], pair[1], left_index=True, right_index=True, how='left')
        # 将x转换为列向量形式，并添加截距项（常数项）
        X = sm.add_constant(result['close_x'])
        
        # 创建模型
        model = sm.OLS(result['close_y'], X)
        
        # 拟合模型
        results = model.fit()
        
        # 查看结果
        print(results.summary())