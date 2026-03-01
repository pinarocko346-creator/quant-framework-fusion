"""
策略基类 - 积木化设计
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import pandas as pd
import numpy as np


@dataclass
class Signal:
    """选股信号"""
    symbol: str
    score: float  # 0-100
    reason: str
    metadata: Dict[str, Any] = None


class BaseStrategy(ABC):
    """策略基类 - 支持信号生成和选股两种模式"""
    
    def __init__(self, name: str = None, params: Dict = None):
        self.name = name or self.__class__.__name__
        self.params = params or {}
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成交易信号 (用于回测)
        Returns: 1=买入, -1=卖出, 0=持有
        """
        pass
    
    def screen(self, data) -> Optional[Signal]:
        """
        选股模式 (用于每日扫描)
        子类可覆盖此方法实现选股逻辑
        """
        signals = self.generate_signals(data.df if hasattr(data, 'df') else data)
        if signals.iloc[-1] == 1:
            return Signal(
                symbol=data.symbol if hasattr(data, 'symbol') else 'UNKNOWN',
                score=70,
                reason=f"{self.name} 买入信号",
                metadata={}
            )
        return None
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """验证数据格式"""
        required = ['open', 'high', 'low', 'close', 'volume']
        return all(col in data.columns for col in required)
    
    def set_params(self, **kwargs):
        """设置参数"""
        self.params.update(kwargs)
    
    def __repr__(self):
        return f"{self.name}({self.params})"


class CompositeStrategy:
    """组合策略 - 多个积木组合"""
    
    def __init__(self, name: str, mode: str = "and"):
        self.name = name
        self.mode = mode  # 'and' or 'or'
        self.blocks: List[BaseStrategy] = []
    
    def add_block(self, block: BaseStrategy):
        self.blocks.append(block)
    
    def screen(self, data) -> Optional[Signal]:
        """执行组合筛选"""
        if not self.blocks:
            return None
        
        signals = []
        reasons = []
        total_score = 0
        
        for block in self.blocks:
            signal = block.screen(data)
            
            if self.mode == "and":
                if signal is None:
                    return None
                signals.append(signal)
                reasons.append(f"{block.name}: {signal.reason}")
                total_score += signal.score
                
            elif self.mode == "or":
                if signal is not None:
                    signals.append(signal)
                    reasons.append(f"{block.name}: {signal.reason}")
                    total_score += signal.score
        
        if not signals:
            return None
        
        avg_score = total_score / len(signals)
        
        return Signal(
            symbol=data.symbol,
            score=avg_score,
            reason=" | ".join(reasons),
            metadata={"blocks": [b.name for b in self.blocks]}
        )
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """生成交易信号 (简化版: 取第一个策略的信号)"""
        if self.blocks:
            return self.blocks[0].generate_signals(data)
        return pd.Series(0, index=data.index)
