"""
回测引擎 - 简化版
"""

import pandas as pd
import numpy as np
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class BacktestResults:
    """回测结果"""
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    num_trades: int
    equity_curve: pd.DataFrame
    
    def print_summary(self):
        print("\n" + "="*50)
        print("📊 回测结果")
        print("="*50)
        print(f"总收益率: {self.total_return*100:.2f}%")
        print(f"夏普比率: {self.sharpe_ratio:.2f}")
        print(f"最大回撤: {self.max_drawdown*100:.2f}%")
        print(f"胜率: {self.win_rate*100:.2f}%")
        print(f"交易次数: {self.num_trades}")
        print("="*50)


class BacktestEngine:
    """简化回测引擎"""
    
    def __init__(
        self,
        strategy,
        initial_capital: float = 100000,
        commission: float = 0.001,
        position_size: float = 0.1
    ):
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.position_size = position_size
    
    def run(self, data: pd.DataFrame, symbol: str = "STOCK") -> BacktestResults:
        """运行回测"""
        # 生成信号
        signals = self.strategy.generate_signals(data)
        
        # 模拟交易
        capital = self.initial_capital
        position = 0
        trades = []
        equity_curve = []
        
        for i in range(len(data)):
            price = data.iloc[i]['close']
            signal = signals.iloc[i]
            
            # 买入信号
            if signal == 1 and position == 0:
                shares = int((capital * self.position_size) / price)
                cost = shares * price * (1 + self.commission)
                if cost <= capital:
                    position = shares
                    capital -= cost
                    trades.append({'type': 'buy', 'price': price, 'shares': shares})
            
            # 卖出信号
            elif signal == -1 and position > 0:
                revenue = position * price * (1 - self.commission)
                capital += revenue
                trades.append({'type': 'sell', 'price': price, 'shares': position})
                position = 0
            
            # 记录权益
            equity = capital + position * price
            equity_curve.append({'date': data.index[i], 'equity': equity})
        
        # 最终平仓
        if position > 0:
            revenue = position * data.iloc[-1]['close'] * (1 - self.commission)
            capital += revenue
        
        # 计算指标
        equity_df = pd.DataFrame(equity_curve)
        total_return = (capital - self.initial_capital) / self.initial_capital
        
        # 计算夏普比率 (简化)
        if len(equity_df) > 1:
            returns = equity_df['equity'].pct_change().dropna()
            sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        else:
            sharpe = 0
        
        # 计算最大回撤
        equity_df['peak'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['peak']) / equity_df['peak']
        max_drawdown = equity_df['drawdown'].min()
        
        # 计算胜率
        buy_trades = [t for t in trades if t['type'] == 'buy']
        sell_trades = [t for t in trades if t['type'] == 'sell']
        
        wins = 0
        for i, sell in enumerate(sell_trades):
            if i < len(buy_trades):
                if sell['price'] > buy_trades[i]['price']:
                    wins += 1
        
        win_rate = wins / len(sell_trades) if sell_trades else 0
        
        return BacktestResults(
            total_return=total_return,
            sharpe_ratio=sharpe,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            num_trades=len(trades),
            equity_curve=equity_df
        )
