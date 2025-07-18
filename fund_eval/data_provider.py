"""
数据获取模块
提供基金实时预估数据和大盘指数数据的获取
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import datetime
import logging
from dataclasses import dataclass

try:
    import akshare as ak
    HAS_AKSHARE = True
except ImportError:
    HAS_AKSHARE = False
    logging.warning("Akshare not available, using mock data")

from fund_strategy import FundData, IndexData

logger = logging.getLogger(__name__)

@dataclass
class RealTimeData:
    """实时数据类"""
    fund_nav: float
    fund_prev_nav: float
    index_value: float
    index_prev_value: float
    timestamp: datetime.datetime

class DataProvider:
    """数据提供商类"""
    
    def __init__(self, use_real_data: bool = False):
        """
        初始化数据提供商
        
        Args:
            use_real_data: 是否使用真实数据，否则使用模拟数据
        """
        self.use_real_data = use_real_data and HAS_AKSHARE
        if not HAS_AKSHARE:
            logger.warning("Akshare not found, falling back to mock data")
            self.use_real_data = False
    
    def get_fund_history(self, fund_code: str, days: int = 365) -> pd.Series:
        """
        获取基金历史净值数据
        
        Args:
            fund_code: 基金代码
            days: 历史天数
            
        Returns:
            历史净值Series
        """
        if self.use_real_data:
            try:
                # 使用akshare获取基金历史数据
                fund_df = ak.fund_etf_fund_info_em(fund=fund_code)
                if not fund_df.empty:
                    fund_df['日期'] = pd.to_datetime(fund_df['日期'])
                    fund_df = fund_df.sort_values('日期')
                    fund_df = fund_df.tail(days)
                    return pd.Series(
                        fund_df['累计净值'].values,
                        index=fund_df['日期']
                    )
            except Exception as e:
                logger.error(f"获取基金{fund_code}历史数据失败: {e}")
        
        # 模拟数据
        return self._generate_mock_fund_data(days)
    
    def get_realtime_estimate(self, fund_code: str) -> Dict[str, float]:
        """
        获取基金实时预估值
        
        Args:
            fund_code: 基金代码
            
        Returns:
            包含净值的字典
        """
        if self.use_real_data:
            try:
                # 尝试获取实时估算净值
                fund_estimate = ak.fund_etf_fund_info_em(fund=fund_code)
                if not fund_estimate.empty:
                    latest_nav = float(fund_estimate.iloc[-1]['累计净值'])
                    prev_nav = float(fund_estimate.iloc[-2]['累计净值'])
                    return {
                        'current_nav': latest_nav,
                        'prev_nav': prev_nav
                    }
            except Exception as e:
                logger.error(f"获取基金{fund_code}实时数据失败: {e}")
        
        # 返回模拟数据
        mock_data = self._generate_mock_fund_data(2)
        return {
            'current_nav': float(mock_data.iloc[-1]),
            'prev_nav': float(mock_data.iloc[-2])
        }
    
    def get_index_realtime(self, index_code: str) -> Dict[str, float]:
        """
        获取指数实时数据
        
        Args:
            index_code: 指数代码，如 'CSI300'
            
        Returns:
            包含指数值的字典
        """
        if self.use_real_data:
            try:
                # 获取沪深300指数
                if index_code == 'CSI300':
                    index_df = ak.stock_zh_index_daily(symbol="sh000300")
                elif index_code == 'CSI500':
                    index_df = ak.stock_zh_index_daily(symbol="sh000905")
                else:
                    # 默认使用沪深300
                    index_df = ak.stock_zh_index_daily(symbol="sh000300")
                
                if not index_df.empty:
                    index_df = index_df.tail(2)
                    current_value = float(index_df.iloc[-1]['close'])
                    prev_value = float(index_df.iloc[-2]['close'])
                    return {
                        'current_value': current_value,
                        'prev_value': prev_value
                    }
            except Exception as e:
                logger.error(f"获取指数{index_code}数据失败: {e}")
        
        # 返回模拟数据
        return {
            'current_value': 4000.0 + np.random.randn() * 100,
            'prev_value': 3950.0 + np.random.randn() * 100
        }
    
    def _generate_mock_fund_data(self, days: int) -> pd.Series:
        """生成模拟基金数据"""
        start_date = datetime.datetime.now() - datetime.timedelta(days=days)
        dates = pd.date_range(start=start_date, periods=days, freq='D')
        
        # 生成有趋势的随机数据，基准1.0，每日波动±2%
        returns = np.random.randn(days) * 0.01  # 每日收益率
        # 添加趋势
        trend = np.linspace(-0.1, 0.15, days)
        returns += trend * 0.01
        
        nav_values = 1.0 * (1 + returns).cumprod()
        
        return pd.Series(nav_values, index=dates)
    
    def _generate_mock_index_data(self, days: int) -> pd.Series:
        """生成模拟指数数据"""
        start_date = datetime.datetime.now() - datetime.timedelta(days=days)
        dates = pd.date_range(start=start_date, periods=days, freq='D')
        
        # 生成沪深300模拟数据，基准3000点
        returns = np.random.randn(days) * 0.015  # 指数波动更大
        values = 3000.0 * (1 + returns).cumprod()
        
        return pd.Series(values, index=dates)
    
    def get_strategy_data(self, fund_code: str, index_code: str = 'CSI300', 
                         days: int = 365) -> tuple[FundData, IndexData]:
        """
        获取策略运行所需的数据
        
        Args:
            fund_code: 基金代码
            index_code: 指数代码
            days: 历史数据天数
            
        Returns:
            (FundData, IndexData) 的元组
        """
        # 获取基金数据
        fund_hist = self.get_fund_history(fund_code, days)
        fund_realtime = self.get_realtime_estimate(fund_code)
        
        fund_data = FundData(
            fund_code=fund_code,
            current_nav=fund_realtime['current_nav'],
            prev_nav=fund_realtime['prev_nav'],
            hist_nav=fund_hist
        )
        
        # 获取指数数据
        index_realtime = self.get_index_realtime(index_code)
        index_hist = self._generate_mock_index_data(days)
        
        index_data = IndexData(
            index_code=index_code,
            current_value=index_realtime['current_value'],
            prev_value=index_realtime['prev_value'],
            hist_values=index_hist
        )
        
        return fund_data, index_data

class StrategyRunner:
    """策略运行器"""
    
    def __init__(self, data_provider: DataProvider):
        """
        初始化策略运行器
        
        Args:
            data_provider: 数据提供商实例
        """
        self.data_provider = data_provider
        
    def run_backtest(self, fund_code: str, strategy, days: int = 365, 
                    base_amount: float = 1000.0) -> Dict:
        """
        运行回测
        
        Args:
            fund_code: 基金代码
            strategy: 策略实例
            days: 回测天数
            base_amount: 基础定投金额
            
        Returns:
            回测结果字典
        """
        from fund_strategy import FundStrategy
        
        # 获取数据
        fund_data, index_data = self.data_provider.get_strategy_data(
            fund_code, days=days
        )
        
        # 运行回测
        for i in range(1, len(fund_data.hist_nav)):
            # 使用历史数据模拟每日情况
            daily_fund = FundData(
                fund_code=fund_code,
                current_nav=fund_data.hist_nav.iloc[i],
                prev_nav=fund_data.hist_nav.iloc[i-1],
                hist_nav=fund_data.hist_nav.iloc[:i+1]
            )
            
            daily_index = IndexData(
                index_code="CSI300",
                current_value=index_data.hist_values.iloc[i],
                prev_value=index_data.hist_values.iloc[i-1],
                hist_values=index_data.hist_values.iloc[:i+1]
            )
            
            strategy.daily_process(daily_fund, daily_index)
        
        # 计算回测结果
        final_nav = fund_data.hist_nav.iloc[-1]
        summary = strategy.get_position_summary(final_nav)
        
        # 计算额外指标
        profits = [trade['profit'] for trade in strategy.trade_log]
        
        return {
            'fund_code': fund_code,
            'days': days,
            'base_amount': base_amount,
            'final_position': summary,
            'total_trades': len(strategy.trade_log),
            'buy_trades': len([t for t in strategy.trade_log if t['type'] == 'BUY']),
            'sell_trades': len([t for t in strategy.trade_log if t['type'] == 'SELL']),
            'total_profit': sum(profits),
            'avg_profit': np.mean(profits) if profits else 0,
            'max_profit': max(profits) if profits else 0,
            'min_profit': min(profits) if profits else 0
        }
    
    def run_realtime(self, fund_code: str, strategy, 
                    fund_codes: List[str] = None) -> Dict:
        """
        运行实时策略
        
        Args:
            fund_code: 当前关注的基金代码
            strategy: 策略实例
            fund_codes: 基金代码列表，用于批量处理
            
        Returns:
            实时运行结果
        """
        if fund_codes is None:
            fund_codes = [fund_code]
        
        results = {}
        
        for code in fund_codes:
            fund_data, index_data = self.data_provider.get_strategy_data(
                code, days=60
            )
            
            # 运行策略
            strategy.daily_process(fund_data, index_data)
            
            results[code] = strategy.get_position_summary(fund_data.current_nav)
            
            # 重置策略位置，用于下一个基金
            from fund_strategy import FundStrategy
            strategy.position = Position()
        
        return results

if __name__ == "__main__":
    # 测试数据提供功能
    provider = DataProvider(use_real_data=False)
    
    # 获取测试数据
    fund_code = "007339"
    fund_data, index_data = provider.get_strategy_data(fund_code)
    
    print("基金数据摘要:")
    print(f"基金代码: {fund_data.fund_code}")
    print(f"当前净值: {fund_data.current_nav}")
    print(f"前日净值: {fund_data.prev_nav}")
    print(f"历史数据长度: {len(fund_data.hist_nav)}")
    
    print("\n指数数据摘要:")
    print(f"指数代码: {index_data.index_code}")
    print(f"当前值: {index_data.current_value}")
    print(f"前值: {index_data.prev_value}")
    print(f"历史数据长度: {len(index_data.hist_values)}")
    
    # 运行简单回测
    from fund_strategy import FundStrategy
    
    runner = StrategyRunner(provider)
    strategy = FundStrategy(base_amount=1000)
    
    results = runner.run_backtest(fund_code, strategy, days=30)
    
    print("\n回测结果:")
    for key, value in results.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        else:
            print(f"{key}: {value}")