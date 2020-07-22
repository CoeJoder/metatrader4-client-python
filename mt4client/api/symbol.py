
class SymbolTick:
    """The latest prices of a symbol in MetaTrader 4.

    Reference:
        https://docs.mql4.com/constants/structures/mqltick
    """

    def __init__(self, time: int, bid: float, ask: float, last: float, volume: int):
        self.time = time
        """The time of the last prices update."""

        self.bid = bid
        """The current bid price."""

        self.ask = ask
        """The current ask price."""

        self.last = last
        """The price of the last deal (Last)."""

        self.volume = volume
        """The volume for the current Last price."""

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"time={self.time}, "
                f"bid={self.bid}, "
                f"ask={self.ask}, "
                f"last={self.last}, "
                f"volume={self.volume})")
