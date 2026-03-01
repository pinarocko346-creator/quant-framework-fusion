# 融合版量化交易框架

模块化、可组合的 **A股+美股** 双市场量化交易策略框架。

## 🎯 核心特性

- **双市场支持**: A股 (akshare/baostock) + 美股 (yfinance)
- **积木化设计**: 策略积木自由组合
- **完整回测**: 支持策略回测和绩效评估
- **每日扫描**: 自动选股推送
- **OpenClaw集成**: 支持AI Agent调用

## 📦 内置模块

### A股策略积木 (6个)
- **趋势判断**: 5/20日均线金叉
- **量能配合**: 放量上涨
- **涨停基因**: 近期涨停次数 (A股独有)
- **平台突破**: 突破近期高点
- **行业龙头**: 大市值+高流动性
- **超跌反弹**: RSI超跌

### 美股策略积木 (6个)
- **趋势判断**: 均线多头排列
- **量能配合**: 量价健康度
- **K线形态**: 平台突破+支撑
- **风险过滤**: 涨幅控制
- **CANSLIM**: 成长股策略
- **抄底波段222**: 超卖反弹

### 经典策略 (8个)
- **动量策略**: RSI、双均线、价格动量
- **均值回归**: 布林带、Z-Score
- **趋势跟踪**: 海龟交易法、唐奇安通道、MACD

### 过滤器 (4个)
- 高成交量过滤
- 低波动率过滤
- 流动性过滤
- 趋势过滤

### 风险管理
- **仓位管理**: 固定、凯利公式、波动率
- **止损方式**: 固定、ATR、移动止损

## 🚀 快速开始

### 安装
```bash
git clone https://github.com/pinarocko346-creator/quant-framework-fusion.git
cd quant-framework-fusion
pip install -r requirements.txt
```

### A股扫描
```bash
python scanner.py --strategy short_term --market cn
```

### 美股扫描
```bash
python scanner.py --strategy canslim --market us
```

### 经典策略回测
```bash
python quickstart.py
python examples/example_1_single_strategy.py
```

## 📊 预定义组合

### A股组合
- **短线强势**: 趋势+量能+涨停基因
- **突破追涨**: 趋势+平台突破+量能
- **蓝筹白马**: 趋势+行业龙头
- **超跌反弹**: RSI超跌

### 美股组合
- **稳健波段版**: 趋势+量能+风险过滤
- **激进启动版**: 趋势+量能+K线形态
- **强化收益版**: 趋势+量能+K线+CANSLIM
- **CANSLIM成长**: CANSLIM策略
- **抄底波段222**: 超卖反弹

## 📁 项目结构

```
quant-framework-fusion/
├── data/
│   └── fetcher.py          # 数据获取 (A股+美股)
├── strategies/
│   ├── base.py             # 策略基类 (融合版)
│   ├── blocks.py           # 策略积木 (A股+美股)
│   ├── portfolios.py       # 预定义组合
│   ├── base_us.py          # 美股经典策略基类
│   └── ...                 # 经典策略实现
├── filters/                # 过滤器模块
├── risk/                   # 风险管理
├── backtest/
│   ├── engine.py           # 融合版回测引擎
│   └── engine_us.py        # 美股经典回测引擎
├── examples/               # 示例脚本
├── agents/                 # OpenClaw Agent配置
├── scanner.py              # 扫描器主入口
├── quickstart.py           # 快速开始
└── config.yaml             # 配置文件
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

## 📚 文档

- [README_CN.md](README_CN.md) - 中文版详细文档
- [README_US.md](README_US.md) - 美股框架原文档
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 项目总结
- [OPENCLAW_INTEGRATION.md](OPENCLAW_INTEGRATION.md) - OpenClaw集成
- [GITHUB_GUIDE.md](GITHUB_GUIDE.md) - GitHub发布指南

## ⚠️ 免责声明

仅供学习研究，不构成投资建议。
