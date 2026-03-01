"""
过滤器基类和通用过滤器
"""
from abc import ABC, abstractmethod
import pandas as pd


class BaseFilter(ABC):
    """过滤器基类"""

    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__

    @abstractmethod
    def filter(self, data: pd.DataFrame, signals: pd.Series) -> pd.Series:
        """
        过滤交易信号

        Args:
            data: 市场数据
            signals: 原始信号

        Returns:
            过滤后的信号
        """
        pass


class HighVolumeFilter(BaseFilter):
    """高成交量过滤器 - 只在成交量充足时交易"""

    def __init__(self, min_volume: int = 1000000):
        super().__init__("高成交量过滤")
        self.min_volume = min_volume

    def filter(self, data: pd.DataFrame, signals: pd.Series) -> pd.Series:
        """过滤低成交量的信号"""
        filtered_signals = signals.copy()
        filtered_signals[data['volume'] < self.min_volume] = 0
        return filtered_signals


class LowVolatilityFilter(BaseFilter):
    """低波动率过滤器 - 避免过度波动的股票"""

    def __init__(self, max_volatility: float = 0.05, period: int = 20):
        super().__init__("低波动率过滤")
        self.max_volatility = max_volatility
        self.period = period

    def filter(self, data: pd.DataFrame, signals: pd.Series) -> pd.Series:
        """过滤高波动率的信号"""
        returns = data['close'].pct_change()
        volatility = returns.rolling(window=self.period).std()

        filtered_signals = signals.copy()
        filtered_signals[volatility > self.max_volatility] = 0
        return filtered_signals


class LiquidityFilter(BaseFilter):
    """流动性过滤器 - 确保有足够的流动性"""

    def __init__(self, min_dollar_volume: float = 10000000):
        super().__init__("流动性过滤")
        self.min_dollar_volume = min_dollar_volume

    def filter(self, data: pd.DataFrame, signals: pd.Series) -> pd.Series:
        """过滤流动性不足的信号"""
        dollar_volume = data['close'] * data['volume']

        filtered_signals = signals.copy()
        filtered_signals[dollar_volume < self.min_dollar_volume] = 0
        return filtered_signals


class TrendFilter(BaseFilter):
    """趋势过滤器 - 只在趋势方向交易"""

    def __init__(self, ma_period: int = 200):
        super().__init__("趋势过滤")
        self.ma_period = ma_period

    def filter(self, data: pd.DataFrame, signals: pd.Series) -> pd.Series:
        """只保留与长期趋势一致的信号"""
        ma = data['close'].rolling(window=self.ma_period).mean()

        filtered_signals = signals.copy()
        # 只在价格高于均线时允许买入
        filtered_signals[(signals == 1) & (data['close'] < ma)] = 0
        # 只在价格低于均线时允许卖出
        filtered_signals[(signals == -1) & (data['close'] > ma)] = 0

        return filtered_signals
