# OpenClaw Agent 集成指南

## 1. 配置 OpenClaw

在 `~/.openclaw/openclaw.json` 中添加量化交易 Agent：

```json
{
  "agents": {
    "list": [
      {
        "id": "quant-trader",
        "name": "量化交易员",
        "workspace": "/Users/apple/us-stock-quant-framework",
        "agentDir": "/Users/apple/us-stock-quant-framework/agents/quant_trader"
      }
    ]
  }
}
```

## 2. 启动 OpenClaw

```bash
# 启动 OpenClaw gateway
openclaw gateway start

# 或者如果使用 Discord
openclaw discord start
```

## 3. 与 Agent 交互

### 通过 Discord

```
@quant-trader 回测 RSI 策略，股票代码 AAPL，时间范围 2023-01-01 到 2024-12-31

@quant-trader 比较所有动量策略在 SPY 上的表现

@quant-trader 测试双均线策略的不同参数组合

@quant-trader 找出最佳的策略+过滤器组合
```

### 通过 API

```python
import requests

response = requests.post('http://localhost:3000/api/agents/quant-trader/chat', json={
    'message': '回测 RSI 策略，AAPL，2023 年全年'
})

print(response.json())
```

## 4. Agent 能力

### 4.1 单策略回测

```
@quant-trader 回测 [策略名称]，[股票代码]，[开始日期] 到 [结束日期]
```

支持的策略：
- RSI 动量策略
- 双均线策略
- 布林带策略
- 海龟交易法
- MACD 策略
- 唐奇安通道
- Z-Score 均值回归

### 4.2 策略对比

```
@quant-trader 比较所有动量策略
@quant-trader 比较 RSI 和双均线策略
```

### 4.3 策略组合测试

```
@quant-trader 测试所有策略+过滤器组合
@quant-trader 找出最佳组合
```

### 4.4 参数优化

```
@quant-trader 优化 RSI 策略参数
@quant-trader 找出双均线的最佳周期
```

## 5. 自定义 Agent 行为

编辑 `agents/quant_trader/IDENTITY.md` 来自定义 Agent 的行为和响应风格。

编辑 `agents/quant_trader/TOOLS.md` 来添加新的工具和功能。

## 6. 添加新策略

1. 在 `strategies/` 目录下创建新的策略模块
2. 继承 `BaseStrategy` 类
3. 实现 `generate_signals` 方法
4. 在 `strategies/__init__.py` 中导出

示例：

```python
from strategies.base import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self, param1, param2):
        super().__init__("我的策略")
        self.param1 = param1
        self.param2 = param2

    def generate_signals(self, data):
        # 你的策略逻辑
        signals = pd.Series(0, index=data.index)
        # ... 生成信号
        return signals
```

## 7. 监控和日志

Agent 的运行日志保存在：
- `~/.openclaw/workspace/logs/`

回测结果保存在：
- `~/us-stock-quant-framework/results/`

## 8. 故障排除

### Agent 无法启动

检查：
1. OpenClaw 是否正在运行
2. 配置文件路径是否正确
3. Python 依赖是否已安装

```bash
cd ~/us-stock-quant-framework
pip install -r requirements.txt
```

### 数据获取失败

确保网络连接正常，yfinance 可以访问 Yahoo Finance API。

### 回测结果异常

检查：
1. 数据质量
2. 策略参数是否合理
3. 时间范围是否足够

## 9. 性能优化

### 缓存数据

启用数据缓存以加快回测速度：

```yaml
# config.yaml
data:
  cache_enabled: true
  cache_dir: "./data/cache"
```

### 并行回测

使用多进程并行测试多个策略：

```python
from multiprocessing import Pool

def run_single_backtest(strategy):
    # 回测逻辑
    pass

with Pool(4) as p:
    results = p.map(run_single_backtest, strategies)
```

## 10. 最佳实践

1. **避免过度拟合**：使用样本外数据验证
2. **考虑交易成本**：设置合理的佣金和滑点
3. **风险管理**：始终使用止损和仓位管理
4. **多样化**：测试多个策略和市场
5. **持续监控**：定期检查策略表现
