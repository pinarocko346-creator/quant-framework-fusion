# 美股量化交易模块化框架

一个模块化、可组合的美股量化交易策略框架，支持 OpenClaw Agent 集成。

## 🎯 核心理念

将成熟的交易策略拆解为可复用的模块，像搭积木一样自由组合，快速测试不同策略组合的收益表现。

## 📦 模块架构

```
strategies/          # 策略模块（核心交易逻辑）
├── momentum/        # 动量策略
├── mean_reversion/  # 均值回归策略
├── trend_following/ # 趋势跟踪策略
├── pairs_trading/   # 配对交易策略
└── breakout/        # 突破策略

signals/             # 信号生成器（技术指标）
├── technical/       # 技术指标信号
├── fundamental/     # 基本面信号
└── sentiment/       # 情绪指标信号

filters/             # 过滤器（筛选条件）
├── volume/          # 成交量过滤
├── volatility/      # 波动率过滤
├── liquidity/       # 流动性过滤
└── sector/          # 行业过滤

risk/                # 风险管理模块
├── position_sizing/ # 仓位管理
├── stop_loss/       # 止损策略
└── portfolio/       # 组合管理

backtest/            # 回测引擎
├── engine.py        # 回测核心引擎
├── metrics.py       # 性能指标计算
└── visualizer.py    # 结果可视化

data/                # 数据模块
├── providers/       # 数据源接口
└── cache/           # 数据缓存

agents/              # OpenClaw Agent 配置
└── quant_trader/    # 量化交易 Agent
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据源

```python
# config.yaml
data:
  provider: "yfinance"  # 或 alpaca, polygon 等
  cache_enabled: true
```

### 3. 组合策略示例

```python
from strategies.momentum import RSIMomentum
from filters.volume import HighVolumeFilter
from risk.position_sizing import KellyPositionSizer
from backtest.engine import BacktestEngine

# 组合策略
strategy = RSIMomentum(period=14, oversold=30, overbought=70)
volume_filter = HighVolumeFilter(min_volume=1000000)
position_sizer = KellyPositionSizer(max_position=0.1)

# 运行回测
engine = BacktestEngine(
    strategy=strategy,
    filters=[volume_filter],
    position_sizer=position_sizer,
    start_date="2020-01-01",
    end_date="2024-12-31",
    initial_capital=100000
)

results = engine.run()
print(f"总收益率: {results.total_return:.2%}")
print(f"夏普比率: {results.sharpe_ratio:.2f}")
print(f"最大回撤: {results.max_drawdown:.2%}")
```

## 📊 内置策略模块

### 1. 动量策略 (Momentum)
- **RSI 动量**: 基于相对强弱指标的超买超卖策略
- **价格动量**: 追踪价格趋势的动量策略
- **双均线**: 快慢均线交叉策略

### 2. 均值回归 (Mean Reversion)
- **布林带回归**: 价格触及布林带边界时反向交易
- **统计套利**: 基于协整关系的配对交易

### 3. 趋势跟踪 (Trend Following)
- **海龟交易法**: 经典的突破跟踪系统
- **唐奇安通道**: 基于通道突破的趋势策略

### 4. 突破策略 (Breakout)
- **52周高点突破**: 突破年度高点买入
- **成交量突破**: 结合成交量确认的突破策略

## 🔧 OpenClaw Agent 集成

### 配置 Agent

在 `~/.openclaw/openclaw.json` 中添加：

```json
{
  "agents": {
    "list": [
      {
        "id": "quant-trader",
        "name": "量化交易员",
        "workspace": "/path/to/us-stock-quant-framework",
        "agentDir": "/path/to/us-stock-quant-framework/agents/quant_trader"
      }
    ]
  }
}
```

### 使用 Agent

```bash
# 通过 Discord 或其他渠道与 Agent 交互
@quant-trader 回测 RSI 动量策略，时间范围 2023-01-01 到 2024-12-31
@quant-trader 优化双均线策略参数
@quant-trader 比较所有动量策略的表现
```

## 📈 性能指标

框架自动计算以下指标：
- 总收益率 (Total Return)
- 年化收益率 (Annualized Return)
- 夏普比率 (Sharpe Ratio)
- 最大回撤 (Max Drawdown)
- 胜率 (Win Rate)
- 盈亏比 (Profit Factor)
- 卡尔玛比率 (Calmar Ratio)

## 🧪 策略组合测试

```python
from backtest.optimizer import StrategyOptimizer

# 定义要测试的策略组合
strategies = [
    ("RSI动量", RSIMomentum()),
    ("双均线", DualMovingAverage()),
    ("布林带", BollingerBands()),
]

filters = [
    HighVolumeFilter(),
    LowVolatilityFilter(),
]

# 自动测试所有组合
optimizer = StrategyOptimizer(strategies, filters)
results = optimizer.run_all_combinations()

# 按夏普比率排序
best_combos = results.sort_by("sharpe_ratio", ascending=False)
print(best_combos.head(10))
```

## 📝 开发新策略

```python
from strategies.base import BaseStrategy

class MyCustomStrategy(BaseStrategy):
    def __init__(self, param1, param2):
        super().__init__()
        self.param1 = param1
        self.param2 = param2

    def generate_signals(self, data):
        """
        生成交易信号
        返回: 1 (买入), -1 (卖出), 0 (持有)
        """
        # 你的策略逻辑
        signals = []
        for i in range(len(data)):
            if self.should_buy(data, i):
                signals.append(1)
            elif self.should_sell(data, i):
                signals.append(-1)
            else:
                signals.append(0)
        return signals

    def should_buy(self, data, index):
        # 买入条件
        pass

    def should_sell(self, data, index):
        # 卖出条件
        pass
```

## 🤝 贡献

欢迎提交 Pull Request 添加新的策略模块！

## 📄 许可证

MIT License
