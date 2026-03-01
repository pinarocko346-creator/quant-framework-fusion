"""
策略基类
所有策略模块都继承自这个基类
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import pandas as pd
import numpy as np


class BaseStrategy(ABC):
    """策略基类"""

    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        self.parameters = {}

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成交易信号

        Args:
            data: 包含 OHLCV 数据的 DataFrame

        Returns:
            pd.Series: 信号序列，1=买入，-1=卖出，0=持有
        """
        pass

    def validate_data(self, data: pd.DataFrame) -> bool:
        """验证数据格式"""
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        return all(col in data.columns for col in required_columns)

    def get_parameters(self) -> Dict:
        """获取策略参数"""
        return self.parameters

    def set_parameters(self, **kwargs):
        """设置策略参数"""
        self.parameters.update(kwargs)

    def __repr__(self):
        return f"{self.name}({self.parameters})"
