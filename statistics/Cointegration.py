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
        
        # adf_test = adfuller(timesequence,autolag='AIC')
        # adf_test_output = pd.Series(dftest[0:4],index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
        
        # for key,value in adf_test[4].items():
        #     adf_test_output['Critical Value (%s)' % key] = value
        #     print(adf_test_output)       

