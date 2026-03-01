"""
回测引擎核心模块
"""
import pandas as pd
import numpy as np
from typing import List, Optional
from datetime import datetime


class BacktestEngine:
    """回测引擎"""

    def __init__(
        self,
        strategy,
        filters: List = None,
        position_sizer = None,
        stop_loss_manager = None,
        initial_capital: float = 100000,
        commission: float = 0.001,
        slippage: float = 0.001
    ):
        self.strategy = strategy
        self.filters = filters or []
        self.position_sizer = position_sizer
        self.stop_loss_manager = stop_loss_manager
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage

        # 回测状态
        self.capital = initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []

    def run(self, data: pd.DataFrame, symbol: str = "STOCK") -> 'BacktestResults':
        """
        运行回测

        Args:
            data: OHLCV 数据
            symbol: 股票代码

        Returns:
            BacktestResults 对象
        """
        # 生成原始信号
        signals = self.strategy.generate_signals(data)

        # 应用过滤器
        for filter_obj in self.filters:
            signals = filter_obj.filter(data, signals)

        # 模拟交易
        for i in range(len(data)):
            current_date = data.index[i]
            current_price = data.iloc[i]['close']
            signal = signals.iloc[i]

            # 检查止损
            if symbol in self.positions:
                self._check_stop_loss(symbol, current_price, current_date)

            # 执行信号
            if signal == 1 and symbol not in self.positions:
                # 买入信号
                self._execute_buy(symbol, current_price, current_date, data.iloc[i])

            elif signal == -1 and symbol in self.positions:
                # 卖出信号
                self._execute_sell(symbol, current_price, current_date)

            # 记录权益曲线
            equity = self._calculate_equity(current_price)
            self.equity_curve.append({
                'date': current_date,
                'equity': equity,
                'cash': self.capital,
                'positions_value': equity - self.capital
            })

        # 平掉所有持仓
        final_price = data.iloc[-1]['close']
        final_date = data.index[-1]
        if symbol in self.positions:
            self._execute_sell(symbol, final_price, final_date)

        # 生成回测结果
        return self._generate_results(data)

    def _execute_buy(self, symbol: str, price: float, date, bar_data):
        """执行买入"""
        # 计算仓位大小
        if self.position_sizer:
            shares = self.position_sizer.calculate_position_size(
                self.capital, price
            )
        else:
            # 默认使用 10% 资金
            shares = int((self.capital * 0.1) / price)

        if shares <= 0:
            return

        # 计算成本（包含滑点和佣金）
        execution_price = price * (1 + self.slippage)
        cost = shares * execution_price
        commission_cost = cost * self.commission
        total_cost = cost + commission_cost

        if total_cost > self.capital:
            return

        # 更新资金和持仓
        self.capital -= total_cost
        self.positions[symbol] = {
            'shares': shares,
            'entry_price': execution_price,
            'entry_date': date
        }

        # 记录交易
        self.trades.append({
            'symbol': symbol,
            'type': 'BUY',
            'date': date,
            'price': execution_price,
            'shares': shares,
            'cost': total_cost
        })

    def _execute_sell(self, symbol: str, price: float, date):
        """执行卖出"""
        if symbol not in self.positions:
            return

        position = self.positions[symbol]
        shares = position['shares']

        # 计算收益（包含滑点和佣金）
        execution_price = price * (1 - self.slippage)
        proceeds = shares * execution_price
        commission_cost = proceeds * self.commission
        net_proceeds = proceeds - commission_cost

        # 更新资金
        self.capital += net_proceeds

        # 计算盈亏
        pnl = net_proceeds - (position['entry_price'] * shares)
        pnl_pct = pnl / (position['entry_price'] * shares)

        # 记录交易
        self.trades.append({
            'symbol': symbol,
            'type': 'SELL',
            'date': date,
            'price': execution_price,
            'shares': shares,
            'proceeds': net_proceeds,
            'pnl': pnl,
            'pnl_pct': pnl_pct
        })

        # 移除持仓
        del self.positions[symbol]

    def _check_stop_loss(self, symbol: str, current_price: float, date):
        """检查止损"""
        if not self.stop_loss_manager or symbol not in self.positions:
            return

        position = self.positions[symbol]
        stop_price = self.stop_loss_manager.calculate_stop_loss(
            position['entry_price']
        )

        if current_price <= stop_price:
            self._execute_sell(symbol, current_price, date)

    def _calculate_equity(self, current_price: float) -> float:
        """计算当前权益"""
        positions_value = sum(
            pos['shares'] * current_price
            for pos in self.positions.values()
        )
        return self.capital + positions_value

    def _generate_results(self, data: pd.DataFrame) -> 'BacktestResults':
        """生成回测结果"""
        equity_df = pd.DataFrame(self.equity_curve).set_index('date')
        trades_df = pd.DataFrame(self.trades)

        return BacktestResults(
            equity_curve=equity_df,
            trades=trades_df,
            initial_capital=self.initial_capital,
            final_capital=equity_df.iloc[-1]['equity'],
            strategy_name=self.strategy.name
        )


class BacktestResults:
    """回测结果"""

    def __init__(self, equity_curve: pd.DataFrame, trades: pd.DataFrame,
                 initial_capital: float, final_capital: float, strategy_name: str):
        self.equity_curve = equity_curve
        self.trades = trades
        self.initial_capital = initial_capital
        self.final_capital = final_capital
        self.strategy_name = strategy_name

    @property
    def total_return(self) -> float:
        """总收益率"""
        return (self.final_capital - self.initial_capital) / self.initial_capital

    @property
    def annualized_return(self) -> float:
        """年化收益率"""
        days = (self.equity_curve.index[-1] - self.equity_curve.index[0]).days
        years = days / 365.25
        return (self.final_capital / self.initial_capital) ** (1 / years) - 1

    @property
    def sharpe_ratio(self) -> float:
        """夏普比率"""
        returns = self.equity_curve['equity'].pct_change().dropna()
        if returns.std() == 0:
            return 0
        return np.sqrt(252) * (returns.mean() / returns.std())

    @property
    def max_drawdown(self) -> float:
        """最大回撤"""
        equity = self.equity_curve['equity']
        cummax = equity.cummax()
        drawdown = (equity - cummax) / cummax
        return drawdown.min()

    @property
    def win_rate(self) -> float:
        """胜率"""
        if len(self.trades) == 0:
            return 0
        winning_trades = self.trades[self.trades['type'] == 'SELL']['pnl'] > 0
        return winning_trades.sum() / len(self.trades[self.trades['type'] == 'SELL'])

    @property
    def profit_factor(self) -> float:
        """盈亏比"""
        sell_trades = self.trades[self.trades['type'] == 'SELL']
        if len(sell_trades) == 0:
            return 0

        gross_profit = sell_trades[sell_trades['pnl'] > 0]['pnl'].sum()
        gross_loss = abs(sell_trades[sell_trades['pnl'] < 0]['pnl'].sum())

        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0

        return gross_profit / gross_loss

    def summary(self) -> dict:
        """生成摘要"""
        return {
            '策略名称': self.strategy_name,
            '初始资金': f"${self.initial_capital:,.2f}",
            '最终资金': f"${self.final_capital:,.2f}",
            '总收益率': f"{self.total_return:.2%}",
            '年化收益率': f"{self.annualized_return:.2%}",
            '夏普比率': f"{self.sharpe_ratio:.2f}",
            '最大回撤': f"{self.max_drawdown:.2%}",
            '胜率': f"{self.win_rate:.2%}",
            '盈亏比': f"{self.profit_factor:.2f}",
            '交易次数': len(self.trades[self.trades['type'] == 'SELL'])
        }

    def print_summary(self):
        """打印摘要"""
        print(f"\n{'='*50}")
        print(f"回测结果 - {self.strategy_name}")
        print(f"{'='*50}")
        for key, value in self.summary().items():
            print(f"{key:12s}: {value}")
        print(f"{'='*50}\n")
