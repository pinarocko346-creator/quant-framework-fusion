"""
策略扫描器 - 主入口
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from data.fetcher import data_fetcher, MarketType
from strategies.portfolios import get_portfolio, list_portfolios
from backtest.engine import BacktestEngine


class StrategyScanner:
    """策略扫描器"""
    
    def __init__(self, market: MarketType = MarketType.US, universe_type: str = "combined"):
        self.market = market
        self.symbols = data_fetcher.fetch_universe(market, universe_type)
        print(f"📊 股票池: {len(self.symbols)} 只 ({market.value})")
    
    def scan(self, portfolio, top_n: int = 10, min_score: float = 60):
        """执行策略扫描"""
        print(f"\n🔍 执行策略: {portfolio.name}")
        
        signals = []
        total = len(self.symbols)
        
        for i, symbol in enumerate(self.symbols, 1):
            if i % 20 == 0:
                print(f"   进度: {i}/{total} ({i/total*100:.1f}%)")
            
            data = data_fetcher.fetch(symbol, period="1y")
            if data is None:
                continue
            
            signal = portfolio.screen(data)
            if signal and signal.score >= min_score:
                signals.append(signal)
        
        signals.sort(key=lambda x: x.score, reverse=True)
        print(f"\n✅ 选出 {len(signals)} 只，返回前 {min(top_n, len(signals))} 只")
        return signals[:top_n]
    
    def print_results(self, signals):
        """打印结果"""
        from datetime import datetime
        print("\n" + "="*60)
        print(f"📈 选股结果 ({datetime.now().strftime('%Y-%m-%d')})")
        print("="*60)
        
        for i, sig in enumerate(signals, 1):
            print(f"\n{i}. {sig.symbol} | 评分: {sig.score:.0f}")
            print(f"   {sig.reason}")
        
        print("\n" + "="*60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="融合版量化策略扫描器")
    parser.add_argument("--strategy", "-s", type=str, default="conservative")
    parser.add_argument("--market", "-m", type=str, default="us", choices=["us", "cn"])
    parser.add_argument("--universe", "-u", type=str, default="combined")
    parser.add_argument("--top", "-n", type=int, default=10)
    parser.add_argument("--min-score", type=float, default=60)
    parser.add_argument("--backtest", "-b", action="store_true", help="对选出的股票进行回测")
    parser.add_argument("--list", "-l", action="store_true", help="列出可用策略")
    
    args = parser.parse_args()
    
    if args.list:
        print("\n可用策略组合:")
        for key, desc in list_portfolios().items():
            print(f"  {key}: {desc}")
        return
    
    market = MarketType.US if args.market == "us" else MarketType.CN
    scanner = StrategyScanner(market=market, universe_type=args.universe)
    portfolio = get_portfolio(args.strategy)
    signals = scanner.scan(portfolio, top_n=args.top, min_score=args.min_score)
    scanner.print_results(signals)
    
    # 回测模式
    if args.backtest and signals:
        print("\n📊 开始回测...")
        engine = BacktestEngine(portfolio, initial_capital=100000)
        
        for sig in signals[:3]:  # 回测前3只
            data = data_fetcher.fetch(sig.symbol, period="2y")
            if data:
                print(f"\n回测 {sig.symbol}:")
                results = engine.run(data.df, sig.symbol)
                results.print_summary()


if __name__ == "__main__":
    main()
