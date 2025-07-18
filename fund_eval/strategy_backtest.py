"""
基金策略回测框架
提供完整的回测、评估和可视化功能
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple
import datetime
import json
from dataclasses import dataclass
import logging

from fund_strategy import FundStrategy
from data_provider import DataProvider, StrategyRunner

logger = logging.getLogger(__name__)

@dataclass
class BacktestResult:
    """回测结果数据结构"""
    fund_code: str
    strategy_name: str
    start_date: datetime.datetime
    end_date: datetime.datetime
    initial_capital: float
    final_value: float
    total_return: float
    annual_return: float
    max_drawdown: float
    sharpe_ratio: float
    volatility: float
    win_rate: float
    total_trades: int
    buy_trades: int
    sell_trades: int
    profit_factor: float
    calmar_ratio: float
    trade_log: List[Dict]
    nav_history: List[float]
    cash_history: List[float]
    position_history: List[Dict]

class StrategyBacktester:
    """策略回测器"""
    
    def __init__(self, data_provider: DataProvider = None):
        """
        初始化回测器
        
        Args:
            data_provider: 数据提供商实例
        """
        self.data_provider = data_provider or DataProvider(use_real_data=False)
        self.results = []
    
    def calculate_performance_metrics(self, trade_log: List[Dict], 
                                    nav_history: List[float]) -> Dict[str, float]:
        """
        计算绩效指标
        
        Args:
            trade_log: 交易日志
            nav_history: 净值历史
            
        Returns:
            绩效指标字典
        """
        if not nav_history:
            return {}
        
        returns = pd.Series(nav_history).pct_change().dropna()
        
        # 基本收益指标
        total_return = (nav_history[-1] - nav_history[0]) / nav_history[0]
        days_held = len(nav_history)
        annual_return = (1 + total_return) ** (365 / days_held) - 1
        
        # 波动率和夏普比率
        volatility = returns.std() * np.sqrt(252)  # 年化波动率
        if volatility > 0:
            sharpe_ratio = (annual_return - 0.03) / volatility  # 假设无风险利率3%
        else:
            sharpe_ratio = 0
        
        # 最大回撤
        cumulative_returns = (1 + returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdowns = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdowns.min()
        
        # 卡玛比率
        calmar_ratio = annual_return / abs(max_drawdown) if abs(max_drawdown) > 0 else 0
        
        # 交易指标
        trades = [t for t in trade_log if t['type'] in ['BUY', 'SELL']]
        
        # 盈亏比例
        profits = []
        for i, trade in enumerate(trades):
            if trade['type'] == 'SELL':
                # 简单计算持仓盈亏
                current_nav = trade.get('price', 0)
                if i > 0 and trades[i-1]['type'] == 'BUY':
                    buy_nav = trades[i-1].get('price', 0)
                    if buy_nav > 0:
                        profits.append((current_nav - buy_nav) / buy_nav)
        
        win_rate = sum(1 for p in profits if p > 0) / len(profits) if profits else 0
        
        # 盈亏比
        winning_trades = [p for p in profits if p > 0]
        losing_trades = [p for p in profits if p < 0]
        
        profit_factor = (sum(winning_trades) / abs(sum(losing_trades))) if losing_trades else 0
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'volatility': volatility,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'calmar_ratio': calmar_ratio,
            'days_held': days_held
        }
    
    def run_comprehensive_backtest(self, fund_codes: List[str], 
                                 base_amount: float = 1000.0,
                                 days: int = 365) -> List[BacktestResult]:
        """
        运行综合回测
        
        Args:
            fund_codes: 基金代码列表
            base_amount: 基础定投金额
            days: 回测天数
            
        Returns:
            回测结果列表
        """
        results = []
        
        runner = StrategyRunner(self.data_provider)
        
        for fund_code in fund_codes:
            logger.info(f"开始回测 {fund_code}...")
            
            # 获取数据
            try:
                fund_data, index_data = self.data_provider.get_strategy_data(
                    fund_code, days=days
                )
                
                # 初始化策略
                strategy = FundStrategy(base_amount=base_amount)
                
                # 运行回测
                nav_history = []
                cash_history = []
                position_history = []
                
                start_nav = fund_data.hist_nav.iloc[0]
                nav_history.append(start_nav)
                cash_history.append(0)  # 初始为0
                
                for i in range(1, len(fund_data.hist_nav)):
                    # 构建当日数据
                    daily_fund = type('obj', (object,), {
                        'fund_code': fund_code,
                        'current_nav': fund_data.hist_nav.iloc[i],
                        'prev_nav': fund_data.hist_nav.iloc[i-1],
                        'hist_nav': fund_data.hist_nav.iloc[:i+1]
                    })
                    
                    daily_index = type('obj', (object,), {
                        'index_code': 'CSI300',
                        'current_value': index_data.hist_values.iloc[i],
                        'prev_value': index_data.hist_values.iloc[i-1],
                        'hist_values': index_data.hist_values.iloc[:i+1]
                    })
                    
                    # 运行策略
                    strategy.daily_process(daily_fund, daily_index)
                    
                    # 记录历史数据
                    position_summary = strategy.get_position_summary(
                        fund_data.hist_nav.iloc[i]
                    )
                    nav_history.append(fund_data.hist_nav.iloc[i])
                    cash_history.append(position_summary['current_value'] 
                                      - position_summary['cost'])
                    position_history.append(position_summary)
                
                # 计算绩效指标
                metrics = self.calculate_performance_metrics(
                    strategy.trade_log, nav_history
                )
                
                # 创建回测结果
                result = BacktestResult(
                    fund_code=fund_code,
                    strategy_name="动态定投策略",
                    start_date=fund_data.hist_nav.index[0],
                    end_date=fund_data.hist_nav.index[-1],
                    initial_capital=0,  # 通过定投逐步投入
                    final_value=position_summary['current_value'],
                    total_return=metrics['total_return'],
                    annual_return=metrics['annual_return'],
                    max_drawdown=metrics['max_drawdown'],
                    sharpe_ratio=metrics['sharpe_ratio'],
                    volatility=metrics['volatility'],
                    win_rate=metrics['win_rate'],
                    total_trades=len(strategy.trade_log),
                    buy_trades=len([t for t in strategy.trade_log if t['type'] == 'BUY']),
                    sell_trades=len([t for t in strategy.trade_log if t['type'] == 'SELL']),
                    profit_factor=metrics['profit_factor'],
                    calmar_ratio=metrics['calmar_ratio'],
                    trade_log=strategy.trade_log,
                    nav_history=nav_history,
                    cash_history=cash_history,
                    position_history=position_history
                )
                
                results.append(result)
                logger.info(f"回测完成: {fund_code}")
                
            except Exception as e:
                logger.error(f"回测 {fund_code} 失败: {e}")
                continue
        
        return results
    
    def visualize_results(self, results: List[BacktestResult], save_path: str = None):
        """
        可视化回测结果
        
        Args:
            results: 回测结果列表
            save_path: 保存路径
        """
        if not results:
            logger.warning("没有可可视化的结果")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('基金策略回测结果', fontsize=16)
        
        # 1. 收益率对比
        ax1 = axes[0, 0]
        fund_codes = [r.fund_code for r in results]
        total_returns = [r.total_return * 100 for r in results]
        annual_returns = [r.annual_return * 100 for r in results]
        
        x = np.arange(len(fund_codes))
        width = 0.35
        
        ax1.bar(x - width/2, total_returns, width, label='总收益')
        ax1.bar(x + width/2, annual_returns, width, label='年化收益')
        ax1.set_xlabel('基金代码')
        ax1.set_ylabel('收益率 (%)')
        ax1.set_title('收益率对比')
        ax1.set_xticks(x)
        ax1.set_xticklabels(fund_codes, rotation=45)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 风险指标
        ax2 = axes[0, 1]
        max_drawdowns = [r.max_drawdown * 100 for r in results]
        volatilities = [r.volatility * 100 for r in results]
        
        ax2.bar(x - width/2, max_drawdowns, width, label='最大回撤', color='red', alpha=0.7)
        ax2.bar(x + width/2, volatilities, width, label='波动率', color='blue', alpha=0.7)
        ax2.set_xlabel('基金代码')
        ax2.set_ylabel('百分比 (%)')
        ax2.set_title('风险指标')
        ax2.set_xticks(x)
        ax2.set_xticklabels(fund_codes, rotation=45)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. 夏普比率 vs 收益
        ax3 = axes[1, 0]
        sharpe_ratios = [r.sharpe_ratio for r in results]
        
        scatter = ax3.scatter(total_returns, sharpe_ratios, s=100, alpha=0.7)
        for i, code in enumerate(fund_codes):
            ax3.annotate(code, (total_returns[i], sharpe_ratios[i]), 
                        xytext=(5, 5), textcoords='offset points')
        ax3.set_xlabel('总收益率 (%)')
        ax3.set_ylabel('夏普比率')
        ax3.set_title('收益与风险调整收益对比')
        ax3.grid(True, alpha=0.3)
        
        # 4. 交易统计
        ax4 = axes[1, 1]
        total_trades = [r.total_trades for r in results]
        win_rates = [r.win_rate * 100 for r in results]
        
        ax4.bar(x, total_trades, width, label='交易次数', color='green', alpha=0.7)
        ax4.set_xlabel('基金代码')
        ax4.set_ylabel('交易次数')
        ax4.set_title('交易统计')
        ax4.set_xticks(x)
        ax4.set_xticklabels(fund_codes, rotation=45)
        
        # 添加第二轴
        ax4b = ax4.twinx()
        ax4b.bar(x + width, win_rates, width, label='胜率', color='orange', alpha=0.7)
        ax4b.set_ylabel('胜率 (%)')
        
        # 合并图例
        lines1, labels1 = ax4.get_legend_handles_labels()
        lines2, labels2 = ax4b.get_legend_handles_labels()
        ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"图表已保存: {save_path}")
        
        plt.show()
    
    def generate_report(self, results: List[BacktestResult], 
                       report_path: str = "backtest_report.json"):
        """
        生成回测报告
        
        Args:
            results: 回测结果列表
            report_path: 报告保存路径
        """
        summary = {
            'backtest_summary': {
                'total_funds': len(results),
                'total_trades': sum(r.total_trades for r in results),
                'winner_count': sum(1 for r in results if r.total_return > 0),
                'loser_count': sum(1 for r in results if r.total_return <= 0),
                'average_return': np.mean([r.total_return for r in results]),
                'average_annual_return': np.mean([r.annual_return for r in results]),
                'average_sharpe': np.mean([r.sharpe_ratio for r in results]),
                'average_drawdown': np.mean([r.max_drawdown for r in results])
            },
            'detailed_results': [
                {
                    'fund_code': r.fund_code,
                    'total_return': r.total_return,
                    'annual_return': r.annual_return,
                    'max_drawdown': r.max_drawdown,
                    'sharpe_ratio': r.sharpe_ratio,
                    'win_rate': r.win_rate,
                    'total_trades': r.total_trades,
                    'profit_factor': r.profit_factor
                }
                for r in results
            ]
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"回测报告已生成: {report_path}")
        return summary

if __name__ == "__main__":
    # 运行回测示例
    fund_codes = ["007339", "017847", "005875", "001788", "002001"]
    
    backtester = StrategyBacktester()
    results = backtester.run_comprehensive_backtest(
        fund_codes, base_amount=1000, days=180
    )
    
    # 可视化结果
    backtester.visualize_results(results, "backtest_results.png")
    
    # 生成报告
    summary = backtester.generate_report(results)
    
    # 打印简要结果
    print("\n=== 回测摘要 ===")
    print(f"回测基金数量: {summary['backtest_summary']['total_funds']}")
    print(f"总交易次数: {summary['backtest_summary']['total_trades']}")
    print(f"盈利基金: {summary['backtest_summary']['winner_count']}")
    print(f"亏损基金: {summary['backtest_summary']['loser_count']}")
    print(f"平均收益率: {summary['backtest_summary']['average_return']:.2%}")
    print(f"平均年化收益率: {summary['backtest_summary']['average_annual_return']:.2%}")
    print(f"平均夏普比率: {summary['backtest_summary']['average_sharpe']:.2f}")
    print(f"平均最大回撤: {summary['backtest_summary']['average_drawdown']:.2%}")
    
    print("\n=== 详细结果 ===")
    for result in summary['detailed_results']:
        print(f"基金 {result['fund_code']}: 收益 {result['total_return']:.2%}",
              f"| 夏普 {result['sharpe_ratio']:.2f} | 回撤 {result['max_drawdown']:.2%}")
        if result['win_rate'] > 0:
            print(f"  " + "_" * 40)