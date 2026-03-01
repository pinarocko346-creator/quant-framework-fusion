#!/usr/bin/env python3
"""
快速开始脚本 - 运行一个简单的回测示例
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import yfinance as yf
    import pandas as pd
    from strategies import RSIMomentum
    from backtest.engine import BacktestEngine

    print("="*60)
    print("美股量化交易框架 - 快速开始")
    print("="*60)

    # 获取数据
    print("\n[1/4] 正在获取 SPY 数据 (2023-2024)...")
    data = yf.download('SPY', start='2023-01-01', end='2024-12-31', progress=False)
    data.columns = data.columns.str.lower()
    print(f"      获取了 {len(data)} 条数据")

    # 创建策略
    print("\n[2/4] 创建 RSI 动量策略...")
    strategy = RSIMomentum(period=14, oversold=30, overbought=70)
    print(f"      策略参数: {strategy.parameters}")

    # 创建回测引擎
    print("\n[3/4] 配置回测引擎...")
    engine = BacktestEngine(
        strategy=strategy,
        initial_capital=100000,
        commission=0.001,
        slippage=0.001
    )
    print("      初始资金: $100,000")
    print("      佣金: 0.1%")
    print("      滑点: 0.1%")

    # 运行回测
    print("\n[4/4] 运行回测...")
    results = engine.run(data, symbol='SPY')

    # 显示结果
    results.print_summary()

    print("\n✅ 快速开始完成！")
    print("\n下一步:")
    print("  1. 查看 examples/ 目录了解更多示例")
    print("  2. 阅读 README.md 了解所有可用策略")
    print("  3. 阅读 OPENCLAW_INTEGRATION.md 了解如何集成 OpenClaw Agent")

except ImportError as e:
    print(f"\n❌ 缺少依赖: {e}")
    print("\n请先安装依赖:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
