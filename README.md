# 量化交易系统

一个基于Python的量化交易系统，支持回测、实盘交易、数据分析和策略开发。

## 项目概述

本项目是一个综合性的量化交易平台，包含以下核心功能：

- **策略开发**: 多种内置交易策略（双均线、MACD、RSI、均值回归、配对交易等）
- **回测系统**: 基于Backtrader的回测框架
- **实盘交易**: 支持LongPort、富途等券商的实盘交易
- **数据获取**: 集成TuShare、AkShare、Yahoo Finance等多个数据源
- **风险控制**: 内置风险管理模块和止损机制
- **统计分析**: 协整分析、统计套利等高级分析方法
- **基金分析**: 基金数据获取和评估工具

## 项目结构

```
trade/
├── online_trader/          # 实盘交易模块
│   ├── main.py            # 实盘交易主程序
│   ├── strategy/          # 实盘交易策略
│   ├── orderbook/         # 订单管理
│   └── riskmanager/       # 风险控制
├── strategy/              # 回测策略
│   ├── DoubleSMA.py       # 双均线策略
│   ├── MACD.py           # MACD策略
│   ├── PairTrade.py      # 配对交易策略
│   └── MeanReversion.py   # 均值回归策略
├── dataloader/           # 数据加载器
│   ├── Tushare.py        # TuShare数据源
│   ├── Yahoo.py          # Yahoo Finance数据源
│   └── LongPort.py       # LongPort数据接口
├── longport_bt/          # LongPort回测适配器
├── statistics/           # 统计分析工具
├── longport_test/        # LongPort API测试
├── data/                # 历史数据目录
├── fund_eval/           # 基金评估工具
│   ├── fund_estimator.py # 基金净值估算数据更新工具
│   ├── schedule_estimator.sh # 定时任务脚本
│   ├── fund_info.csv     # 基金信息文件
│   ├── fund_info_with_estimation.csv # 带估算数据的基金信息文件
│   └── README.md         # 基金评估工具说明
└── bitcoin/             # 加密货币相关
```

## 快速开始

### 环境准备

1. **安装依赖**
   ```bash
   pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple
   ```

2. **配置环境变量**
   ```bash
   cp template.env .env
   # 编辑.env文件填入你的API密钥和配置
   ```

### 回测使用

运行MACD策略回测示例：
```python
from strategy.MACD import MACDStrategy
from backtrader import Cerebro
import pandas as pd

# 加载数据
data = pd.read_csv('data/aapl.csv')
cerebro = Cerebro()
# 添加数据和策略...
```

### 实盘交易

启动实盘交易系统：
```bash
# 配置config.yaml文件后运行
cd online_trader
python main.py
```

### 基金数据更新

基金净值估算数据更新工具会在每个工作日下午2点自动运行，获取最新的基金估算净值数据。

手动执行更新：
```bash
cd /Users/klb3713/work/trade
python fund_eval/fund_estimator.py
```

## 数据源支持

- **A股数据**: TuShare Pro、AkShare
- **美股数据**: Yahoo Finance、LongPort
- **加密货币**: CCXT交易所集成
- **实时数据**: LongPort实时行情
- **基金数据**: 东方财富网基金数据

## 内置策略详解

### 1. 双均线策略 (DoubleSMA)
- 基于短期和长期移动平均线的交叉信号
- 快速均线上穿慢速均线时买入，下穿时卖出

### 2. MACD策略
- 利用MACD线和信号线的交叉
- 结合柱状图变化判断趋势强度
- 包含趋势过滤机制

### 3. RSI+SMA组合策略
- RSI超买超卖判断 + 移动平均线趋势确认
- RSI > 70且价格跌破均线时卖出
- RSI < 30且价格上穿均线时买入

### 4. 均值回归策略
- 基于价格偏离均值的程度进行交易
- 包含波动率过滤和止损机制
- 适用于震荡市行情

### 5. 配对交易策略
- 基于协整关系的配对交易
- 价差偏离时做多低估/做空高估
- 实时价差监控和自动调仓

## 实盘交易配置

编辑 `online_trader/config.yaml`：

```yaml
stock_id: "AAPL"               # 交易标的
strategy:
  name: "MACD"                 # 策略名称
  fast_period: 12             # MACD快周期
  slow_period: 26             # MACD慢周期
  signal_period: 9            # MACD信号线周期
risk:
  max_position: 1000          # 最大持仓
  stop_loss_pct: 0.05        # 止损百分比
log_name: "trading.log"
log_path: "./logs/"
```

## API密钥配置

在 `.env` 文件中配置：

```bash
# LongPort配置
LONGPORT_APP_KEY=your_app_key
LONGPORT_APP_SECRET=your_app_secret
LONGPORT_ACCESS_TOKEN=your_access_token

# TuShare配置
TUSHARE_TOKEN=your_tushare_token
```

## 高级功能

### 协整分析

使用 `statistics.Cointegration` 进行配对交易前的协整检验：

```python
from statistics.Cointegration import CointegrationAnalysis

analyzer = CointegrationAnalysis(stock1_data, stock2_data)
result = analyzer.run_cointegration_test()
print(f"协整关系: {result.is_cointegrated}, p值: {result.p_value}")
```

### 比特币跨交易所套利

运行比特币跨交易所价格监控：
```bash
python bitcoin/cross_exchange.py
```

### 基金评估

基金净值估算数据更新工具会自动获取并更新基金的实时估算净值数据。

## 数据获取工具

### TuShare数据采集
```bash
python futu_fetch.py --symbol "000001" --start-date "2023-01-01" --output data/
```

## 开发指南

### 添加新策略

1. 在 `strategy/` 目录创建新策略文件
2. 继承 `StrategySelfBase.py` 中的基础类
3. 实现必要的方法：
   - `__init__()`: 策略初始化
   - `next()`: 交易逻辑
   - `stop()`: 策略结束时的清理工作

示例：
```python
from strategy.StrategySelfBase import StrategySelfBase

class MyStrategy(StrategySelfBase):
    def __init__(self):
        super().__init__()
        self.sma = self.sma(period=20)
    
    def next(self):
        if self.data.close > self.sma:
            self.buy()
```

### 错误处理与日志

系统使用完善的日志记录：
- 交易日志：记录所有交易行为
- 错误日志：记录系统异常和错误
- 性能日志：记录策略执行性能

## 性能优化

- **数据缓存**: 支持数据本地缓存，减少API调用
- **并行处理**: 多策略/多品种并行回测
- **内存优化**: 大数据集的流式处理
- **实时优化**: 增量数据更新机制

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可

本项目采用 MIT 许可证 - 详情请参见 [LICENSE](LICENSE) 文件。

## 免责声明

本项目仅供学习和研究使用，不构成投资建议。使用本系统进行实盘交易产生的风险由用户自行承担。请在充分了解和测试后再用于实盘交易。
或者
poetry install