# 量化交易 Agent 工具配置

## 可用工具

### 1. 策略回测工具
```python
from backtest.engine import BacktestEngine
from strategies import RSIMomentum, DualMovingAverage, BollingerBands

# 运行单个策略回测
def run_backtest(strategy_name, symbol, start_date, end_date, **params):
    # 实现回测逻辑
    pass
```

### 2. 数据获取工具
```python
import yfinance as yf

# 获取股票数据
def get_stock_data(symbol, start_date, end_date):
    data = yf.download(symbol, start=start_date, end=end_date)
    return data
```

### 3. 策略优化工具
```python
from backtest.optimizer import StrategyOptimizer

# 优化策略参数
def optimize_strategy(strategy, param_grid, data):
    optimizer = StrategyOptimizer(strategy, param_grid)
    best_params = optimizer.optimize(data)
    return best_params
```

### 4. 性能可视化工具
```python
import matplotlib.pyplot as plt

# 绘制权益曲线
def plot_equity_curve(results):
    results.equity_curve['equity'].plot()
    plt.title('Equity Curve')
    plt.show()
```

## 工具使用指南

1. **回测流程**：
   - 使用 `get_stock_data` 获取数据
   - 选择策略模块
   - 使用 `run_backtest` 运行回测
   - 分析结果

2. **策略组合测试**：
   - 定义多个策略
   - 批量运行回测
   - 比较性能指标

3. **参数优化**：
   - 定义参数网格
   - 使用 `optimize_strategy` 寻找最优参数
   - 验证结果

## 注意事项

- 确保数据质量
- 避免过度拟合
- 考虑交易成本
- 注意市场环境变化
