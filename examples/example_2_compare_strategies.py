"""
示例 2: 比较多个策略
"""
import sys
sys.path.append('..')

import yfinance as yf
import pandas as pd
from strategies import (
    RSIMomentum,
    DualMovingAverage,
    BollingerBands,
    TurtleTrading,
    MACD
)
from backtest.engine import BacktestEngine


def compare_strategies():
    # 获取数据
    print("正在获取数据...")
    data = yf.download('SPY', start='2020-01-01', end='2024-12-31')
    data.columns = data.columns.str.lower()

    # 定义要测试的策略
    strategies = [
        RSIMomentum(period=14, oversold=30, overbought=70),
        DualMovingAverage(fast_period=20, slow_period=50),
        BollingerBands(period=20, std_dev=2.0),
        TurtleTrading(entry_period=20, exit_period=10),
        MACD(fast=12, slow=26, signal=9)
    ]

    # 存储结果
    results_list = []

    # 运行每个策略
    for strategy in strategies:
        print(f"\n测试策略: {strategy.name}")

        engine = BacktestEngine(
            strategy=strategy,
            initial_capital=100000,
            commission=0.001,
            slippage=0.001
        )

        results = engine.run(data, symbol='SPY')

        results_list.append({
            '策略': strategy.name,
            '总收益率': f"{results.total_return:.2%}",
            '年化收益率': f"{results.annualized_return:.2%}",
            '夏普比率': f"{results.sharpe_ratio:.2f}",
            '最大回撤': f"{results.max_drawdown:.2%}",
            '胜率': f"{results.win_rate:.2%}",
            '盈亏比': f"{results.profit_factor:.2f}",
            '交易次数': len(results.trades[results.trades['type'] == 'SELL'])
        })

    # 创建对比表格
    comparison_df = pd.DataFrame(results_list)

    print("\n" + "="*100)
    print("策略对比结果")
    print("="*100)
    print(comparison_df.to_string(index=False))
    print("="*100)

    # 找出最佳策略
    print("\n推荐策略:")
    print("- 最高收益: ", results_list[0]['策略'])
    print("- 最佳风险调整收益 (夏普比率): ", results_list[0]['策略'])


if __name__ == '__main__':
    compare_strategies()
