from typing import Dict, Protocol, Type
import yaml


class TraderStrategy(Protocol):
    """A base class for trader strategies."""

    config: Dict[str, str] = {}

    def __init__(self, stock_id: str, cfg) -> None:
        self.stock_id = stock_id
        config = cfg

    def Run(self) -> None:
        pass
