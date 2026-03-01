"""
风险管理和仓位管理模块
"""
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np


class BasePositionSizer(ABC):
    """仓位管理基类"""

    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__

    @abstractmethod
    def calculate_position_size(self, capital: float, price: float, volatility: float = None) -> float:
        """
        计算仓位大小

        Args:
            capital: 可用资金
            price: 当前价格
            volatility: 波动率（可选）

        Returns:
            应该购买的股数
        """
        pass


class FixedPositionSizer(BasePositionSizer):
    """固定仓位管理 - 每次使用固定比例的资金"""

    def __init__(self, position_pct: float = 0.1):
        super().__init__("固定仓位")
        self.position_pct = position_pct

    def calculate_position_size(self, capital: float, price: float, volatility: float = None) -> float:
        """使用固定比例的资金"""
        position_value = capital * self.position_pct
        shares = int(position_value / price)
        return shares


class KellyPositionSizer(BasePositionSizer):
    """凯利公式仓位管理"""

    def __init__(self, win_rate: float = 0.55, avg_win: float = 1.5, avg_loss: float = 1.0, max_position: float = 0.25):
        super().__init__("凯利公式")
        self.win_rate = win_rate
        self.avg_win = avg_win
        self.avg_loss = avg_loss
        self.max_position = max_position

    def calculate_position_size(self, capital: float, price: float, volatility: float = None) -> float:
        """使用凯利公式计算仓位"""
        # Kelly % = W - [(1 - W) / R]
        # W = 胜率, R = 平均盈利/平均亏损
        kelly_pct = self.win_rate - ((1 - self.win_rate) / (self.avg_win / self.avg_loss))

        # 使用半凯利或限制最大仓位
        kelly_pct = min(kelly_pct * 0.5, self.max_position)
        kelly_pct = max(kelly_pct, 0)  # 不允许负仓位

        position_value = capital * kelly_pct
        shares = int(position_value / price)
        return shares


class VolatilityPositionSizer(BasePositionSizer):
    """基于波动率的仓位管理 - ATR 仓位"""

    def __init__(self, risk_per_trade: float = 0.02, atr_multiplier: float = 2.0):
        super().__init__("波动率仓位")
        self.risk_per_trade = risk_per_trade
        self.atr_multiplier = atr_multiplier

    def calculate_position_size(self, capital: float, price: float, volatility: float = None) -> float:
        """基于 ATR 计算仓位"""
        if volatility is None:
            # 如果没有提供波动率，使用固定 2% 风险
            risk_amount = capital * self.risk_per_trade
            shares = int(risk_amount / (price * 0.02))
        else:
            # 使用 ATR 计算止损距离
            stop_distance = volatility * self.atr_multiplier
            risk_amount = capital * self.risk_per_trade
            shares = int(risk_amount / stop_distance)

        return shares


class StopLossManager:
    """止损管理器"""

    def __init__(self, stop_type: str = "fixed", stop_pct: float = 0.02, atr_multiplier: float = 2.0):
        """
        Args:
            stop_type: 止损类型 ('fixed', 'atr', 'trailing')
            stop_pct: 固定止损百分比
            atr_multiplier: ATR 倍数
        """
        self.stop_type = stop_type
        self.stop_pct = stop_pct
        self.atr_multiplier = atr_multiplier

    def calculate_stop_loss(self, entry_price: float, atr: float = None, highest_price: float = None) -> float:
        """计算止损价格"""
        if self.stop_type == "fixed":
            return entry_price * (1 - self.stop_pct)

        elif self.stop_type == "atr" and atr is not None:
            return entry_price - (atr * self.atr_multiplier)

        elif self.stop_type == "trailing" and highest_price is not None:
            return highest_price * (1 - self.stop_pct)

        else:
            # 默认使用固定止损
            return entry_price * (1 - self.stop_pct)


class PortfolioManager:
    """组合管理器"""

    def __init__(self, max_positions: int = 10, max_sector_exposure: float = 0.3):
        self.max_positions = max_positions
        self.max_sector_exposure = max_sector_exposure
        self.positions = {}

    def can_add_position(self, symbol: str, sector: str = None) -> bool:
        """检查是否可以添加新仓位"""
        # 检查最大持仓数
        if len(self.positions) >= self.max_positions:
            return False

        # 检查行业暴露（如果提供了行业信息）
        if sector and self.max_sector_exposure:
            sector_exposure = sum(
                1 for pos in self.positions.values()
                if pos.get('sector') == sector
            ) / self.max_positions

            if sector_exposure >= self.max_sector_exposure:
                return False

        return True

    def add_position(self, symbol: str, shares: int, entry_price: float, sector: str = None):
        """添加仓位"""
        self.positions[symbol] = {
            'shares': shares,
            'entry_price': entry_price,
            'sector': sector
        }

    def remove_position(self, symbol: str):
        """移除仓位"""
        if symbol in self.positions:
            del self.positions[symbol]

    def get_position(self, symbol: str):
        """获取仓位信息"""
        return self.positions.get(symbol)
