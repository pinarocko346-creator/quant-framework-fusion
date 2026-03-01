# 美股量化交易模块化框架

[English](README.md) | 简体中文

一个模块化、可组合的美股量化交易策略框架，支持 OpenClaw Agent 集成。

## 🎯 核心理念

将成熟的交易策略拆解为可复用的模块，像搭积木一样自由组合，快速测试不同策略组合的收益表现。

## ✨ 特色功能

- 🧩 **模块化设计**: 策略、过滤器、风险管理完全解耦
- 🔄 **自由组合**: 8个策略 × 4个过滤器 × 3个仓位管理 = 96种组合
- 📊 **完整回测**: 包含佣金、滑点、止损的真实回测
- 🤖 **AI 集成**: 与 OpenClaw Agent 无缝集成
- 📈 **生产就绪**: 包含完整的风险管理和性能评估

## 📦 内置策略模块

### 动量策略 (Momentum)
- **RSI 动量**: 基于相对强弱指标的超买超卖策略
- **双均线**: 快慢均线交叉策略
- **价格动量**: 追踪价格趋势的动量策略

### 均值回归 (Mean Reversion)
- **布林带**: 价格触及布林带边界时反向交易
- **Z-Score**: 基于统计的均值回归策略

### 趋势跟踪 (Trend Following)
- **海龟交易法**: 经典的突破跟踪系统
- **唐奇安通道**: 基于通道突破的趋势策略
- **MACD**: MACD 指标交叉策略

## 🚀 快速开始

### 1. 安装

```bash
git clone https://github.com/YOUR_USERNAME/us-stock-quant-framework.git
cd us-stock-quant-framework
pip install -r requirements.txt
```

### 2. 运行示例

```bash
python quickstart.py
```

### 3. 自定义策略

```python
from strategies import RSIMomentum
from filters import HighVolumeFilter
from risk import KellyPositionSizer
from backtest.engine import BacktestEngine
import yfinance as yf

# 获取数据
data = yf.download('AAPL', start='2023-01-01', end='2024-12-31')
data.columns = data.columns.str.lower()

# 组合策略
strategy = RSIMomentum(period=14, oversold=30, overbought=70)
filters = [HighVolumeFilter(min_volume=10_000_000)]
position_sizer = KellyPositionSizer()

# 运行回测
engine = BacktestEngine(
    strategy=strategy,
    filters=filters,
    position_sizer=position_sizer,
    initial_capital=100000
)

results = engine.run(data, symbol='AAPL')
results.print_summary()
```

## 📊 回测结果示例

```
==================================================
回测结果 - RSI动量策略
==================================================
策略名称    : RSI动量策略
初始资金    : $100,000.00
最终资金    : $125,430.00
总收益率    : 25.43%
年化收益率  : 12.15%
夏普比率    : 1.85
最大回撤    : -8.32%
胜率        : 58.33%
盈亏比      : 2.15
交易次数    : 24
==================================================
```

## 🧪 策略组合测试

框架的核心优势是可以自动测试所有策略组合：

```python
# 运行示例 3 - 自动测试所有组合
python examples/example_3_strategy_combinations.py
```

输出：
```
策略组合测试结果 (按夏普比率排序)
============================================================
组合                              总收益率  夏普比率  最大回撤
RSI + 趋势+成交量 + 凯利公式      32.5%    2.15     -6.8%
双均线 + 高成交量 + 固定10%       28.3%    1.92     -7.2%
...
```

## 🤖 OpenClaw Agent 集成

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

```
@quant-trader 回测 RSI 策略，AAPL，2023-01-01 到 2024-12-31
@quant-trader 比较所有动量策略
@quant-trader 找出最佳策略组合
```

详细文档: [OPENCLAW_INTEGRATION.md](OPENCLAW_INTEGRATION.md)

## 📁 项目结构

```
us-stock-quant-framework/
├── strategies/          # 策略模块
│   ├── momentum/        # 动量策略
│   ├── mean_reversion/  # 均值回归
│   └── trend_following/ # 趋势跟踪
├── filters/             # 过滤器模块
├── risk/                # 风险管理
├── backtest/            # 回测引擎
├── agents/              # OpenClaw Agent
├── examples/            # 使用示例
└── config.yaml          # 配置文件
```

## 📈 性能指标

框架自动计算：
- 总收益率 (Total Return)
- 年化收益率 (Annualized Return)
- 夏普比率 (Sharpe Ratio)
- 最大回撤 (Max Drawdown)
- 胜率 (Win Rate)
- 盈亏比 (Profit Factor)

## 🔧 添加新策略

```python
from strategies.base import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self, param1, param2):
        super().__init__("我的策略")
        self.param1 = param1
        self.param2 = param2

    def generate_signals(self, data):
        signals = pd.Series(0, index=data.index)
        # 你的策略逻辑
        return signals
```

## 📚 文档

- [完整文档](README.md)
- [OpenClaw 集成指南](OPENCLAW_INTEGRATION.md)
- [项目总结](PROJECT_SUMMARY.md)
- [GitHub 发布指南](GITHUB_GUIDE.md)

## 🤝 贡献

欢迎提交 Pull Request 添加新的策略模块！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingStrategy`)
3. 提交更改 (`git commit -m 'Add some AmazingStrategy'`)
4. 推送到分支 (`git push origin feature/AmazingStrategy`)
5. 创建 Pull Request

## ⚠️ 风险提示

- 历史表现不代表未来收益
- 回测结果可能存在过度拟合
- 实盘交易需要考虑更多因素
- 建议先用小资金测试
- 本框架仅供学习和研究使用

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 🌟 Star History

如果这个项目对你有帮助，请给个 Star ⭐️

## 📞 联系方式

- GitHub Issues: 报告 bug 或提出功能请求
- Discussions: 讨论策略和交易想法

---

**免责声明**: 本项目仅供教育和研究目的。使用本框架进行实盘交易的风险由使用者自行承担。
