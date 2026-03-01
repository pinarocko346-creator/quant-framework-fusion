"""
融合版量化框架 - 数据模块
支持 A股(akshare/baostock) + 美股(yfinance)
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict
from enum import Enum
import pickle
import time

import pandas as pd
import numpy as np


class MarketType(Enum):
    """市场类型"""
    US = "us"
    CN = "cn"
    HK = "hk"


@dataclass
class StockData:
    """标准化股票数据结构"""
    symbol: str
    market: MarketType
    df: pd.DataFrame
    
    @property
    def close(self) -> pd.Series:
        return self.df['close']
    
    @property
    def volume(self) -> pd.Series:
        return self.df['volume']
    
    @property
    def ma5(self) -> pd.Series:
        return self.df['close'].rolling(5).mean()
    
    @property
    def ma20(self) -> pd.Series:
        return self.df['close'].rolling(20).mean()
    
    @property
    def ma60(self) -> pd.Series:
        return self.df['close'].rolling(60).mean()
    
    def recent_high(self, days: int = 30) -> float:
        return self.df['high'].tail(days).max()
    
    def recent_low(self, days: int = 30) -> float:
        return self.df['low'].tail(days).min()


class AShareDataSource:
    """A股数据源 - baostock + akshare"""
    
    def __init__(self):
        self._stock_list_cache = None
        self._bs_logged_in = False
    
    def _baostock_login(self):
        if not self._bs_logged_in:
            try:
                import baostock as bs
                result = bs.login()
                if result.error_code == '0':
                    self._bs_logged_in = True
                    return True
            except Exception as e:
                print(f"baostock登录失败: {e}")
        return self._bs_logged_in
    
    def get_stock_list(self) -> List[str]:
        """获取A股股票列表"""
        if self._stock_list_cache:
            return self._stock_list_cache
        
        # 使用硬编码的主要股票列表（避免接口问题）
        major_stocks = [
            # 金融
            'sh.600000', 'sh.601398', 'sh.601288', 'sh.601939', 'sh.601988',
            # 白酒
            'sh.600519', 'sz.000858', 'sz.000568', 'sh.600809', 'sh.603369',
            # 新能源
            'sz.002594', 'sh.601012', 'sz.300750', 'sh.600438', 'sz.002460',
            # 医药
            'sh.600276', 'sh.603259', 'sz.000538', 'sh.600436', 'sh.603392',
            # 科技
            'sh.688981', 'sh.688012', 'sz.002371', 'sh.603501', 'sh.688008',
            # 消费
            'sh.600887', 'sz.000333', 'sh.600690', 'sh.603288', 'sz.002304',
            # 军工
            'sh.600893', 'sh.600760', 'sh.600372', 'sz.000768', 'sh.600399',
            # 有色
            'sh.601899', 'sh.603993', 'sh.600111', 'sz.002460', 'sh.600362',
        ]
        
        self._stock_list_cache = list(set(major_stocks))
        print(f"📊 A股股票池: {len(self._stock_list_cache)} 只")
        return self._stock_list_cache
    
    def get_kline(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """获取K线 - 优先akshare，失败用baostock"""
        df = self._get_kline_akshare(symbol, period)
        if df is not None:
            return df
        return self._get_kline_baostock(symbol, period)
    
    def _get_kline_akshare(self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        try:
            import akshare as ak
            
            if '.' in symbol:
                symbol = symbol.split('.')[-1]
            
            end_date = datetime.now()
            if period == "1y":
                start_date = end_date - timedelta(days=365)
            elif period == "2y":
                start_date = end_date - timedelta(days=730)
            else:
                start_date = end_date - timedelta(days=365)
            
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date.strftime('%Y%m%d'),
                end_date=end_date.strftime('%Y%m%d')
            )
            
            if len(df) < 60:
                return None
            
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume'
            })[['date', 'open', 'high', 'low', 'close', 'volume']]
            
            return df
            
        except Exception as e:
            return None
    
    def _get_kline_baostock(self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        if not self._baostock_login():
            return None
        
        try:
            import baostock as bs
            
            end_date = datetime.now()
            if period == "1y":
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=365)
            
            rs = bs.query_history_k_data_plus(
                symbol,
                "date,open,high,low,close,volume",
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                frequency="d"
            )
            
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if len(data_list) < 60:
                return None
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
            
        except Exception as e:
            return None


class USDataSource:
    """美股数据源 - yfinance"""
    
    def get_stock_list(self, universe_type: str = "combined") -> List[str]:
        sp500_core = [
            'AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOGL', 'META', 'TSLA', 'BRK-B',
            'AVGO', 'WMT', 'JPM', 'V', 'MA', 'UNH', 'HD', 'PG', 'JNJ', 'LLY',
            'MRK', 'PEP', 'KO', 'ABBV', 'BAC', 'COST', 'TMO', 'DIS', 'ADBE',
            'CSCO', 'VZ', 'WFC', 'ACN', 'ABT', 'CRM', 'TXN', 'NKE', 'PM',
            'RTX', 'NEE', 'BMY', 'LIN', 'ORCL', 'UPS', 'HON', 'QCOM', 'AMGN',
            'CAT', 'SBUX', 'IBM', 'GE', 'CVX', 'BA', 'PFE', 'AMD', 'INTC',
            'AMAT', 'LRCX', 'KLAC', 'MU', 'MRVL', 'PANW', 'CRWD', 'ZS'
        ]
        
        qqq_core = [
            'NFLX', 'ADI', 'VRTX', 'MDLZ', 'ISRG', 'REGN', 'FTNT', 'OKTA',
            'DDOG', 'SNOW', 'PLTR', 'RBLX', 'U', 'DOCN', 'NET', 'FSLY'
        ]
        
        if universe_type == "sp500":
            return sp500_core
        elif universe_type == "qqq":
            return qqq_core
        else:
            return list(set(sp500_core + qqq_core))
    
    def get_kline(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if len(hist) < 60:
                return None
            
            df = hist.reset_index()
            df = df.rename(columns={
                'Date': 'date',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })[['date', 'open', 'high', 'low', 'close', 'volume']]
            
            return df
            
        except Exception as e:
            return None


class DataFetcher:
    """统一数据获取器"""
    
    def __init__(self, cache_dir: str = "./data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, StockData] = {}
        
        self.cn_source = AShareDataSource()
        self.us_source = USDataSource()
    
    def _detect_market(self, symbol: str) -> MarketType:
        if '.' in symbol or symbol.isdigit():
            return MarketType.CN
        return MarketType.US
    
    def fetch(self, symbol: str, period: str = "1y", use_cache: bool = True) -> Optional[StockData]:
        cache_key = f"{symbol}_{period}_{datetime.now().strftime('%Y%m%d')}"
        cache_path = self.cache_dir / f"{cache_key}.pkl"
        
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]
        
        if use_cache and cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    data = pickle.load(f)
                self._cache[cache_key] = data
                return data
            except:
                pass
        
        market = self._detect_market(symbol)
        
        if market == MarketType.CN:
            df = self.cn_source.get_kline(symbol, period)
        else:
            df = self.us_source.get_kline(symbol, period)
        
        if df is None or len(df) < 60:
            return None
        
        # 数据清洗
        if df[['open', 'high', 'low', 'close', 'volume']].isnull().any().any():
            return None
        
        data = StockData(symbol=symbol, market=market, df=df)
        
        if use_cache:
            self._cache[cache_key] = data
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
        
        return data
    
    def fetch_universe(self, market: MarketType = MarketType.US, universe_type: str = "combined") -> List[str]:
        if market == MarketType.CN:
            return self.cn_source.get_stock_list()
        else:
            return self.us_source.get_stock_list(universe_type)


# 全局实例
data_fetcher = DataFetcher()
