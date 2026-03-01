"""
策略组合配置
"""

from strategies.base import CompositeStrategy
from strategies.blocks import (
    TrendBlock, VolumeBlock, KLinePatternBlock,
    RiskFilterBlock, CANSLIMBlock, BottomBand222Block
)


def create_conservative_portfolio():
    """稳健波段版: 趋势+量能+风险过滤"""
    portfolio = CompositeStrategy("稳健波段版", mode="and")
    portfolio.add_block(TrendBlock())
    portfolio.add_block(VolumeBlock())
    portfolio.add_block(RiskFilterBlock())
    return portfolio


def create_aggressive_portfolio():
    """激进启动版: 趋势+量能+K线形态"""
    portfolio = CompositeStrategy("激进启动版", mode="and")
    portfolio.add_block(TrendBlock())
    portfolio.add_block(VolumeBlock())
    portfolio.add_block(KLinePatternBlock())
    return portfolio


def create_momentum_portfolio():
    """强化收益版: 趋势+量能+K线+动量(用CANSLIM替代)"""
    portfolio = CompositeStrategy("强化收益版", mode="and")
    portfolio.add_block(TrendBlock())
    portfolio.add_block(VolumeBlock())
    portfolio.add_block(KLinePatternBlock())
    portfolio.add_block(CANSLIMBlock())
    return portfolio


def create_canslim_portfolio():
    """CANSLIM成长策略"""
    portfolio = CompositeStrategy("CANSLIM成长", mode="and")
    portfolio.add_block(CANSLIMBlock())
    return portfolio


def create_bottom_band_portfolio():
    """抄底波段222策略"""
    portfolio = CompositeStrategy("抄底波段222", mode="and")
    portfolio.add_block(BottomBand222Block())
    return portfolio


PORTFOLIOS = {
    "conservative": create_conservative_portfolio,
    "aggressive": create_aggressive_portfolio,
    "momentum": create_momentum_portfolio,
    "canslim": create_canslim_portfolio,
    "bottom_band": create_bottom_band_portfolio,
}


def get_portfolio(name: str):
    if name not in PORTFOLIOS:
        raise ValueError(f"未知策略: {name}，可用: {list(PORTFOLIOS.keys())}")
    return PORTFOLIOS[name]()


def list_portfolios():
    return {
        "conservative": "稳健波段版 - 趋势+量能+风险过滤",
        "aggressive": "激进启动版 - 趋势+量能+K线形态",
        "momentum": "强化收益版 - 趋势+量能+K线+CANSLIM",
        "canslim": "CANSLIM成长策略",
        "bottom_band": "抄底波段222策略",
    }
