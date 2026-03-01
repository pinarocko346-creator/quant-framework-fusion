"""
示例 1: 运行单个策略回测
"""
import sys
sys.path.append('..')

import yfinance as yf
from strategies import RSIMomentum
from filters import HighVolumeFilter, TrendFilter
from risk import FixedPositionSizer, StopLossManager
from backtest.engine import BacktestEngine


def main():
    # 1. 获取数据
    print("正在获取 AAPL 数据...")
    data = yf.download('AAPL', start='2023-01-01', end='2024-12-31')
    data.columns = data.columns.str.lower()

    # 2. 配置策略
    strategy = RSIMomentum(period=14, oversold=30, overbought=70)

    # 3. 配置过滤器
    filters = [
        HighVolumeFilter(min_volume=10_000_000),  # 最小成交量 1000 万
        TrendFilter(ma_period=200)  # 200 日均线趋势过滤
    ]

    # 4. 配置风险管理
    position_sizer = FixedPositionSizer(position_pct=0.1)  # 每次 10% 资金
    stop_loss = StopLossManager(stop_type='fixed', stop_pct=0.02)  # 2% 止损

    # 5. 创建回测引擎
    engine = BacktestEngine(
        strategy=strategy,
        filters=filters,
        position_sizer=position_sizer,
        stop_loss_manager=stop_loss,
        initial_capital=100000,
        commission=0.001,  # 0.1% 佣金
        slippage=0.001  # 0.1% 滑点
    )

    # 6. 运行回测
    print("\n运行回测...")
    results = engine.run(data, symbol='AAPL')

    # 7. 打印结果
    results.print_summary()

    # 8. 查看交易记录
    print("\n最近 5 笔交易:")
    print(results.trades.tail(10))


if __name__ == '__main__':
    main()
