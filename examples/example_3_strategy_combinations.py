"""
示例 3: 策略组合测试 - 测试不同模块组合
"""
import sys
sys.path.append('..')

import yfinance as yf
import pandas as pd
from itertools import product
from strategies import RSIMomentum, DualMovingAverage
from filters import HighVolumeFilter, LowVolatilityFilter, TrendFilter
from risk import FixedPositionSizer, KellyPositionSizer
from backtest.engine import BacktestEngine


def test_combinations():
    # 获取数据
    print("正在获取数据...")
    data = yf.download('QQQ', start='2022-01-01', end='2024-12-31')
    data.columns = data.columns.str.lower()

    # 定义模块
    strategies = [
        ('RSI', RSIMomentum()),
        ('双均线', DualMovingAverage())
    ]

    filter_combinations = [
        ('无过滤', []),
        ('高成交量', [HighVolumeFilter(min_volume=50_000_000)]),
        ('低波动', [LowVolatilityFilter(max_volatility=0.03)]),
        ('趋势+成交量', [TrendFilter(), HighVolumeFilter(min_volume=50_000_000)])
    ]

    position_sizers = [
        ('固定10%', FixedPositionSizer(0.1)),
        ('凯利公式', KellyPositionSizer(win_rate=0.55, avg_win=1.5, avg_loss=1.0))
    ]

    results_list = []

    # 测试所有组合
    total_combinations = len(strategies) * len(filter_combinations) * len(position_sizers)
    current = 0

    for (strat_name, strategy), (filter_name, filters), (sizer_name, sizer) in product(
        strategies, filter_combinations, position_sizers
    ):
        current += 1
        combo_name = f"{strat_name} + {filter_name} + {sizer_name}"
        print(f"\n[{current}/{total_combinations}] 测试组合: {combo_name}")

        try:
            engine = BacktestEngine(
                strategy=strategy,
                filters=filters,
                position_sizer=sizer,
                initial_capital=100000,
                commission=0.001,
                slippage=0.001
            )

            results = engine.run(data, symbol='QQQ')

            results_list.append({
                '组合': combo_name,
                '策略': strat_name,
                '过滤器': filter_name,
                '仓位管理': sizer_name,
                '总收益率': results.total_return,
                '年化收益率': results.annualized_return,
                '夏普比率': results.sharpe_ratio,
                '最大回撤': results.max_drawdown,
                '胜率': results.win_rate,
                '交易次数': len(results.trades[results.trades['type'] == 'SELL'])
            })

        except Exception as e:
            print(f"  错误: {e}")
            continue

    # 创建结果 DataFrame
    results_df = pd.DataFrame(results_list)

    # 按夏普比率排序
    results_df = results_df.sort_values('夏普比率', ascending=False)

    # 格式化显示
    display_df = results_df.copy()
    display_df['总收益率'] = display_df['总收益率'].apply(lambda x: f"{x:.2%}")
    display_df['年化收益率'] = display_df['年化收益率'].apply(lambda x: f"{x:.2%}")
    display_df['夏普比率'] = display_df['夏普比率'].apply(lambda x: f"{x:.2f}")
    display_df['最大回撤'] = display_df['最大回撤'].apply(lambda x: f"{x:.2%}")
    display_df['胜率'] = display_df['胜率'].apply(lambda x: f"{x:.2%}")

    print("\n" + "="*120)
    print("策略组合测试结果 (按夏普比率排序)")
    print("="*120)
    print(display_df.to_string(index=False))
    print("="*120)

    # 显示最佳组合
    best = results_df.iloc[0]
    print(f"\n🏆 最佳组合 (夏普比率最高):")
    print(f"   组合: {best['组合']}")
    print(f"   总收益率: {best['总收益率']:.2%}")
    print(f"   年化收益率: {best['年化收益率']:.2%}")
    print(f"   夏普比率: {best['夏普比率']:.2f}")
    print(f"   最大回撤: {best['最大回撤']:.2%}")
    print(f"   胜率: {best['胜率']:.2%}")

    # 保存结果
    results_df.to_csv('strategy_combinations_results.csv', index=False)
    print(f"\n结果已保存到: strategy_combinations_results.csv")


if __name__ == '__main__':
    test_combinations()
