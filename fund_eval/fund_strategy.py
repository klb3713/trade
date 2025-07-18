"""
基金买卖策略实现
基于fund_strategy.md文档的策略设计
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FundData:
    """基金数据类"""
    fund_code: str
    current_nav: float  # 当前净值或预估净值
    prev_nav: float  # 前一日净值
    hist_nav: pd.Series  # 历史净值数据
    
@dataclass
class IndexData:
    """指数数据类"""
    index_code: str
    current_value: float  # 当前指数值
    prev_value: float  # 前一日收盘价
    hist_values: pd.Series  # 历史指数值

@dataclass
class Position:
    """持仓记录"""
    shares: float = 0.0  # 持有份额
    cost: float = 0.0  # 总成本
    target_return: float = 0.2  # 目标收益率，初始20%
    max_return: float = 0.0  # 历史最高收益率

class FundStrategy:
    """基金定投策略类"""
    
    def __init__(self, base_amount: float = 1000.0):
        """
        初始化策略
        
        Args:
            base_amount: 基础定投金额
        """
        self.base_amount = base_amount
        self.position = Position()
        self.trade_log = []
        
    def calculate_ma(self, values: pd.Series, window: int) -> float:
        """计算移动平均线"""
        if len(values) < window:
            return values.mean()
        return values.tail(window).mean()
    
    def get_position_profit(self, current_nav: float) -> float:
        """计算当前持仓收益率"""
        if self.position.cost <= 0:
            return 0.0
        current_value = self.position.shares * current_nav
        return (current_value - self.position.cost) / self.position.cost
    
    def should_sell(self, current_nav: float, index_data: IndexData, 
                   fund_data: FundData) -> Tuple[bool, float]:
        """
        卖出决策
        
        Returns:
            (should_sell_bool, sell_ratio)
        """
        # 更新历史最高收益率
        current_profit = self.get_position_profit(current_nav)
        self.position.max_return = max(self.position.max_return, current_profit)
        
        # 条件1：止损（清仓）
        if current_profit <= -0.10:
            logger.info(f"止损卖出: 收益率={current_profit:.2%}")
            return True, 1.0
        
        # 条件2：目标收益率止盈
        if current_profit >= self.position.target_return:
            logger.info(f"目标止盈: 收益率={current_profit:.2%}, 目标={self.position.target_return:.2%}")
            return True, 0.5
        
        # 条件3：回撤止盈
        if self.position.max_return - current_profit >= 0.10:
            logger.info(f"回撤止盈: 历史最高={self.position.max_return:.2%}, 当前={current_profit:.2%}")
            return True, 0.5
        
        # 条件4：高估卖出
        ma60 = self.calculate_ma(fund_data.hist_nav, 60)
        if current_nav > ma60 * 1.2:
            logger.info(f"高估卖出: 当前净值={current_nav}, MA60*1.2={ma60*1.2:.2f}")
            return True, 0.5
        
        return False, 0.0
    
    def calculate_buy_amount(self, current_nav: float, fund_data: FundData, 
                           index_data: IndexData) -> float:
        """
        计算买入金额
        """
        # 当日预估涨跌幅
        fund_change = (current_nav - fund_data.prev_nav) / fund_data.prev_nav
        
        # 如果当日上涨超过1%，不买入
        if fund_change > 0.01:
            return 0.0
        
        # 计算大盘涨跌幅
        index_change = (index_data.current_value - index_data.prev_value) / index_data.prev_value
        
        # 相对回撤
        relative_drawdown = fund_change - index_change
        
        # 计算MA20和MA60
        ma20 = self.calculate_ma(fund_data.hist_nav, 20)
        ma60 = self.calculate_ma(fund_data.hist_nav, 60)
        
        # 均线调整因子
        if current_nav < ma20 and current_nav < ma60:
            factor_ma = 2.0
        elif current_nav < ma20:
            factor_ma = 1.5
        elif current_nav < ma60:
            factor_ma = 1.0
        else:
            factor_ma = 0.5
        
        # 相对回撤调整因子
        factor_relative = 1 + max(0, -relative_drawdown) * 0.5
        
        # 当日跌幅额外加仓
        extra = 0.0
        if fund_change < -0.02:
            extra = 0.5 * self.base_amount
        
        buy_amount = self.base_amount * factor_ma * factor_relative + extra
        
        # 确保买入金额为正值
        buy_amount = max(0.0, buy_amount)
        
        logger.info(f"买入计算: fund_change={fund_change:.2%}, index_change={index_change:.2%}, "
                   f"ma_factor={factor_ma}, relative_factor={factor_relative:.2f}, "
                   f"extra={extra:.2f}, final_amount={buy_amount:.2f}")
        
        return buy_amount
    
    def execute_sell(self, sell_ratio: float, current_nav: float):
        """执行卖出操作"""
        if self.position.shares <= 0:
            return
        
        sell_shares = self.position.shares * sell_ratio
        sell_amount = sell_shares * current_nav
        
        # 更新持仓
        self.position.shares -= sell_shares
        self.position.cost -= sell_amount * (self.position.cost / (sell_shares * current_nav + self.position.cost))
        
        # 记录交易日志
        self.trade_log.append({
            'type': 'SELL',
            'shares': sell_shares,
            'price': current_nav,
            'amount': sell_amount,
            'profit': (sell_shares * current_nav) - (sell_shares * self.position.cost / sell_shares),
            'timestamp': pd.Timestamp.now()
        })
        
        # 更新目标收益率（如果是目标止盈的情况）
        # 注意：实际应用中可能需要不同的处理逻辑
        if sell_ratio == 0.5:
            self.position.target_return = min(0.5, self.position.target_return + 0.05)
        
        logger.info(f"卖出执行: 卖出{sell_shares:.4f}份，价格{current_nav:.4f}，金额{sell_amount:.2f}")
    
    def execute_buy(self, buy_amount: float, current_nav: float):
        """执行买入操作"""
        if buy_amount <= 0:
            return
        
        buy_shares = buy_amount / current_nav
        self.position.shares += buy_shares
        self.position.cost += buy_amount
        
        # 记录交易日志
        self.trade_log.append({
            'type': 'BUY',
            'shares': buy_shares,
            'price': current_nav,
            'amount': buy_amount,
            'timestamp': pd.Timestamp.now()
        })
        
        logger.info(f"买入执行: 买入{buy_shares:.4f}份，价格{current_nav:.4f}，金额{buy_amount:.2f}")
    
    def daily_process(self, fund_data: FundData, index_data: IndexData):
        """
        每日执行策略
        
        Args:
            fund_data: 基金数据
            index_data: 大盘指数数据
        """
        logger.info(f"开始每日策略执行 - 基金: {fund_data.fund_code}, 当前净值: {fund_data.current_nav}")
        
        # 卖出决策
        should_sell, sell_ratio = self.should_sell(fund_data.current_nav, index_data, fund_data)
        if should_sell:
            self.execute_sell(sell_ratio, fund_data.current_nav)
        
        # 买入决策
        buy_amount = self.calculate_buy_amount(fund_data.current_nav, fund_data, index_data)
        if buy_amount > 0:
            self.execute_buy(buy_amount, fund_data.current_nav)
        
        # 输出当前持仓情况
        current_profit = self.get_position_profit(fund_data.current_nav)
        current_value = self.position.shares * fund_data.current_nav
        logger.info(f"持仓更新: 份额={self.position.shares:.4f}, 成本={self.position.cost:.2f}, "
                   f"市值={current_value:.2f}, 收益率={current_profit:.2%}")
    
    def get_position_summary(self, current_nav: float) -> Dict:
        """获取持仓摘要"""
        current_value = self.position.shares * current_nav
        current_profit = self.get_position_profit(current_nav)
        
        return {
            'fund_code': 'CurrentFund',
            'shares': self.position.shares,
            'cost': self.position.cost,
            'current_value': current_value,
            'current_nav': current_nav,
            'profit_ratio': current_profit,
            'target_return': self.position.target_return,
            'max_return': self.position.max_return
        }

if __name__ == "__main__":
    # 测试示例
    strategy = FundStrategy(base_amount=1000)
    
    # 创建测试数据
    fund_code = "007339"
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    fund_nav = pd.Series(1.0 + np.random.randn(100).cumsum() * 0.01, index=dates)
    index_values = pd.Series(3000.0 + np.random.randn(100).cumsum() * 10, index=dates)
    
    # 模拟每日运行
    for i in range(1, len(dates)):
        fund_data = FundData(
            fund_code=fund_code,
            current_nav=fund_nav.iloc[i],
            prev_nav=fund_nav.iloc[i-1],
            hist_nav=fund_nav.iloc[:i+1]
        )
        
        index_data = IndexData(
            index_code="CSI300",
            current_value=index_values.iloc[i],
            prev_value=index_values.iloc[i-1],
            hist_values=index_values.iloc[:i+1]
        )
        
        strategy.daily_process(fund_data, index_data)
    
    # 输出最终结果
    final_summary = strategy.get_position_summary(fund_nav.iloc[-1])
    print("\n最终持仓情况:")
    for key, value in final_summary.items():
        if key in ['shares', 'cost', 'current_value', 'current_nav']:
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")