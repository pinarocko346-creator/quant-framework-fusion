# 融合版量化交易框架

模块化、可组合的 A股+美股 量化交易策略框架。

## 🎯 核心特性

- **双市场支持**: A股 (akshare/baostock) + 美股 (yfinance)
- **积木化设计**: 6个策略积木自由组合
- **完整回测**: 支持策略回测和绩效评估
- **每日扫描**: 自动选股推送

## 📦 内置策略积木

### K线盘感积木
- **趋势判断**: 均线多头排列 + 高点上移
- **量能配合**: 上涨放量 + 下跌缩量
- **K线形态**: 平台突破 + 均线支撑 + 阳线占比
- **风险过滤**: 涨幅控制 + 趋势确认

### 经典策略积木
- **CANSLIM**: 成长股策略 (近新高 + 动量 + 放量)
- **抄底波段222**: 超卖反弹策略 (KDJ金叉 + 风险系数)

## 🚀 快速开始

### 安装依赖
```bash
cd quant-framework-fusion
pip install -r requirements.txt
```

### 运行扫描
```bash
# 美股扫描
python scanner.py --strategy conservative --market us

# A股扫描
python scanner.py --strategy canslim --market cn

# 带回测
python scanner.py --strategy aggressive --backtest
```

### 列出策略
```bash
python scanner.py --list
```

## 📊 预定义组合

| 组合名称 | 积木组合 | 风格 |
|---------|---------|------|
| 稳健波段版 | 趋势+量能+风险过滤 | 保守 |
| 激进启动版 | 趋势+量能+K线形态 | 积极 |
| 强化收益版 | 趋势+量能+K线+CANSLIM | 激进 |
| CANSLIM成长 | CANSLIM | 成长 |
| 抄底波段222 | 抄底波段222 | 反弹 |

## 📁 项目结构

```
quant-framework-fusion/
├── data/
│   └── fetcher.py          # 数据获取 (A股+美股)
├── strategies/
│   ├── base.py             # 策略基类
│   ├── blocks.py           # 6个策略积木
│   └── portfolios.py       # 预定义组合
├── backtest/
│   └── engine.py           # 回测引擎
└── scanner.py              # 扫描器主入口
```

## 🔧 自定义策略

```python
from strategies.base import CompositeStrategy
from strategies.blocks import TrendBlock, VolumeBlock

# 创建自定义组合
my_strategy = CompositeStrategy("我的策略", mode="and")
my_strategy.add_block(TrendBlock({'ma_short': 10, 'ma_long': 30}))
my_strategy.add_block(VolumeBlock())

# 扫描
from data.fetcher import data_fetcher
data = data_fetcher.fetch("AAPL")
signal = my_strategy.screen(data)
```

## ⚠️ 免责声明

仅供学习研究，不构成投资建议。
