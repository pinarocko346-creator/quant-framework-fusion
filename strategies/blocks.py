"""
K线+量能盘感积木块
"""

from typing import Optional
import pandas as pd
import numpy as np

from strategies.base import BaseStrategy, Signal


class TrendBlock(BaseStrategy):
    """趋势判断积木"""
    
    def __init__(self, params: dict = None):
        default = {'ma_short': 20, 'ma_long': 60, 'high_lookback': 20}
        if params:
            default.update(params)
        super().__init__("趋势判断", default)
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        ma_s = data['close'].rolling(self.params['ma_short']).mean()
        ma_l = data['close'].rolling(self.params['ma_long']).mean()
        
        cond1 = data['close'] > ma_s
        cond2 = ma_s > ma_l
        
        signals = pd.Series(0, index=data.index)
        signals[cond1 & cond2] = 1
        signals[~(cond1 & cond2)] = -1
        return signals
    
    def screen(self, data) -> Optional[Signal]:
        df = data.df if hasattr(data, 'df') else data
        
        # 简化: 只看均线多头排列
        ma_s = df['close'].rolling(self.params['ma_short']).mean()
        ma_l = df['close'].rolling(self.params['ma_long']).mean()
        
        cond1 = df['close'].iloc[-1] > ma_s.iloc[-1]  # 收盘价 > 短期均线
        cond2 = ma_s.iloc[-1] > ma_l.iloc[-1]  # 短期 > 长期
        
        if cond1 and cond2:
            trend_strength = (df['close'].iloc[-1] - ma_s.iloc[-1]) / ma_s.iloc[-1] * 100
            score = min(100, 60 + trend_strength * 15)
            return Signal(
                symbol=getattr(data, 'symbol', 'UNKNOWN'),
                score=score,
                reason=f"均线多头排列，趋势向上",
                metadata={"trend_strength": trend_strength}
            )
        return None


class VolumeBlock(BaseStrategy):
    """量能配合积木"""
    
    def __init__(self, params: dict = None):
        default = {'up_threshold': 1.2, 'down_threshold': 0.8, 'lookback': 5}
        if params:
            default.update(params)
        super().__init__("量能配合", default)
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        vol_ma20 = data['volume'].rolling(20).mean()
        vol_ratio = data['volume'] / vol_ma20
        
        signals = pd.Series(0, index=data.index)
        signals[vol_ratio > self.params['up_threshold']] = 1
        signals[vol_ratio < self.params['down_threshold']] = -1
        return signals
    
    def screen(self, data) -> Optional[Signal]:
        df = data.df if hasattr(data, 'df') else data
        vol_ma20 = df['volume'].rolling(20).mean()
        
        # 简化: 只看最新一天的量能
        latest_vol = df['volume'].iloc[-1]
        vol_ma20_latest = vol_ma20.iloc[-1]
        volume_ratio = latest_vol / vol_ma20_latest if vol_ma20_latest > 0 else 1
        
        # 条件: 成交量 > 20日均量 或 近期平均量能正常
        if volume_ratio > 0.8:  # 降低门槛
            score = min(100, 60 + volume_ratio * 20)
            return Signal(
                symbol=getattr(data, 'symbol', 'UNKNOWN'),
                score=score,
                reason=f"量能正常，成交量/20日均量={volume_ratio:.2f}",
                metadata={"volume_ratio": volume_ratio}
            )
        return None


class KLinePatternBlock(BaseStrategy):
    """K线形态积木"""
    
    def __init__(self, params: dict = None):
        default = {'breakout_lookback': 30, 'ma_support': 20, 'bullish_days_required': 3, 'recent_days': 5}
        if params:
            default.update(params)
        super().__init__("K线形态", default)
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        recent_high = data['high'].rolling(self.params['breakout_lookback']).max()
        breakout = data['close'] >= recent_high * 0.99
        
        bullish_days = (data['close'] > data['open']).rolling(self.params['recent_days']).sum()
        
        signals = pd.Series(0, index=data.index)
        signals[breakout & (bullish_days >= self.params['bullish_days_required'])] = 1
        return signals
    
    def screen(self, data) -> Optional[Signal]:
        df = data.df if hasattr(data, 'df') else data
        recent_high = df['high'].tail(self.params['breakout_lookback']).max()
        cond1 = df['close'].iloc[-1] >= recent_high * 0.99
        
        recent_df = df.tail(self.params['recent_days'])
        bullish_days = sum(recent_df['close'] > recent_df['open'])
        cond2 = bullish_days >= self.params['bullish_days_required']
        
        if cond1 and cond2:
            score = min(100, 70 + (bullish_days - 3) * 10)
            return Signal(
                symbol=getattr(data, 'symbol', 'UNKNOWN'),
                score=score,
                reason=f"平台突破+多方占优，近{self.params['recent_days']}日阳线{bullish_days}根",
                metadata={"breakout": cond1, "bullish_days": bullish_days}
            )
        return None


class RiskFilterBlock(BaseStrategy):
    """风险过滤积木"""
    
    def __init__(self, params: dict = None):
        default = {'max_gain_10d': 0.30, 'ma_trend': 20, 'consecutive_bearish': 3}
        if params:
            default.update(params)
        super().__init__("风险过滤", default)
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        gain_10d = (data['close'] - data['close'].shift(10)) / data['close'].shift(10)
        ma = data['close'].rolling(self.params['ma_trend']).mean()
        
        signals = pd.Series(0, index=data.index)
        signals[(gain_10d < self.params['max_gain_10d']) & (data['close'] > ma)] = 1
        signals[(gain_10d >= self.params['max_gain_10d']) | (data['close'] <= ma)] = -1
        return signals
    
    def screen(self, data) -> Optional[Signal]:
        df = data.df if hasattr(data, 'df') else data
        gain_10d = (df['close'].iloc[-1] - df['close'].iloc[-10]) / df['close'].iloc[-10]
        ma = df['close'].rolling(self.params['ma_trend']).mean()
        
        cond1 = gain_10d < self.params['max_gain_10d']
        cond2 = df['close'].iloc[-1] > ma.iloc[-1]
        
        if cond1 and cond2:
            score = min(100, 80 - gain_10d * 100)
            return Signal(
                symbol=getattr(data, 'symbol', 'UNKNOWN'),
                score=score,
                reason=f"风险可控，近10日涨幅{gain_10d*100:.1f}%，站在MA{self.params['ma_trend']}上方",
                metadata={"gain_10d": gain_10d}
            )
        return None


class CANSLIMBlock(BaseStrategy):
    """CANSLIM策略积木"""
    
    def __init__(self, params: dict = None):
        default = {'max_dist_from_high': 0.10, 'volume_threshold': 1.2}
        if params:
            default.update(params)
        super().__init__("CANSLIM", default)
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        high_52w = data['high'].rolling(250).max()
        dist_from_high = (high_52w - data['close']) / high_52w
        price_momentum = (data['close'] - data['close'].shift(20)) / data['close'].shift(20)
        vol_ma20 = data['volume'].rolling(20).mean()
        vol_ratio = data['volume'] / vol_ma20
        ma20 = data['close'].rolling(20).mean()
        
        signals = pd.Series(0, index=data.index)
        signals[(dist_from_high < self.params['max_dist_from_high']) & 
                (price_momentum > 0.10) & 
                (vol_ratio > self.params['volume_threshold']) &
                (data['close'] > ma20)] = 1
        return signals
    
    def screen(self, data) -> Optional[Signal]:
        df = data.df if hasattr(data, 'df') else data
        high_52w = df['high'].tail(250).max()
        current_price = df['close'].iloc[-1]
        dist_from_high = (high_52w - current_price) / high_52w
        price_momentum = (current_price - df['close'].iloc[-20]) / df['close'].iloc[-20]
        vol_ma20 = df['volume'].rolling(20).mean()
        vol_ratio = df['volume'].iloc[-1] / vol_ma20.iloc[-1]
        ma20 = df['close'].rolling(20).mean()
        
        score = 0
        reasons = []
        
        if dist_from_high < self.params['max_dist_from_high']:
            score += 30
            reasons.append(f"距52周高{dist_from_high*100:.1f}%")
        
        if price_momentum > 0.10:
            score += 30
            reasons.append(f"20日涨幅{price_momentum*100:.1f}%")
        
        if vol_ratio > self.params['volume_threshold']:
            score += 20
            reasons.append(f"成交量{vol_ratio:.1f}倍")
        
        if current_price > ma20.iloc[-1]:
            score += 20
            reasons.append("趋势向上")
        
        if score >= 60:
            return Signal(
                symbol=getattr(data, 'symbol', 'UNKNOWN'),
                score=score,
                reason="CANSLIM: " + ", ".join(reasons),
                metadata={"dist_from_high": dist_from_high, "price_momentum": price_momentum}
            )
        return None


class BottomBand222Block(BaseStrategy):
    """抄底波段222策略积木"""
    
    def __init__(self, params: dict = None):
        default = {'risk_threshold': 20, 'kdj_threshold': 20}
        if params:
            default.update(params)
        super().__init__("抄底波段222", default)
    
    def _calculate_kdj(self, df: pd.DataFrame):
        low_n = df['low'].rolling(9).min()
        high_n = df['high'].rolling(9).max()
        rsv = (df['close'] - low_n) / (high_n - low_n).replace(0, np.nan) * 100
        rsv = rsv.fillna(50)
        k = rsv.ewm(alpha=1/3, adjust=False).mean()
        d = k.ewm(alpha=1/3, adjust=False).mean()
        return k, d
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        k, d = self._calculate_kdj(data)
        risk = (data['close'] - data['low'].rolling(20).min()) / (data['high'].rolling(20).max() - data['low'].rolling(20).min()) * 100
        
        golden_cross = (k.shift(1) <= d.shift(1)) & (k > d)
        below_threshold = (k < self.params['kdj_threshold']) & (d < self.params['kdj_threshold'])
        
        signals = pd.Series(0, index=data.index)
        signals[(risk < self.params['risk_threshold']) & golden_cross & below_threshold] = 1
        return signals
    
    def screen(self, data) -> Optional[Signal]:
        df = data.df if hasattr(data, 'df') else data
        k, d = self._calculate_kdj(df)
        risk = (df['close'].iloc[-1] - df['low'].tail(20).min()) / (df['high'].tail(20).max() - df['low'].tail(20).min()) * 100
        
        cond1 = risk < self.params['risk_threshold']
        cond2 = (k.iloc[-2] <= d.iloc[-2]) and (k.iloc[-1] > d.iloc[-1]) and (k.iloc[-1] < self.params['kdj_threshold'])
        change = (df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]
        cond3 = change > 0.02
        
        if cond1 and cond2 and cond3:
            score = min(100, 80 - risk + change * 100)
            return Signal(
                symbol=getattr(data, 'symbol', 'UNKNOWN'),
                score=score,
                reason=f"超卖反弹信号，风险系数{risk:.1f}，KDJ金叉，涨幅{change*100:.1f}%",
                metadata={"risk": risk, "kdj_k": k.iloc[-1]}
            )
        return None
