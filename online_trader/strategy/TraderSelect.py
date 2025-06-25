from .TraderStrategy import TraderStrategy
from .NetTrader import NetTrader
from .MACD import MACD
from typing import Dict, Protocol, Type


def SelectStrategy(trade_name: str):
    """Factory"""
    localizers: Dict[str, Type[TraderStrategy]] = {
        "NetTrader": NetTrader,
        "MACD": MACD,
    }

    return localizers[trade_name]
