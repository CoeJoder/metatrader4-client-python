# MetaTrader 4 -- ZeroMQ Python Client
A Python 3 client connector and API for [MT4-ZMQ Bridge](https://github.com/CoeJoder/mt4-zeromq-bridge).

## Usage
```python
from mt4client import MT4Client

# create ZeroMQ sockets and connect to server
mt4 = MT4Client(host="mt4terminal")

# query the MT4 terminal
account = mt4.account()
signals = mt4.signal_names()
symbols = mt4.symbol_names()
iac = mt4.indicator("iAC", ["EURUSD", 60, 1])
eur_usd = mt4.symbol("EURUSD")

tick = eur_usd.tick()
bars = eur_usd.ohlcv(timeframe="1h")

print(f"I have {account.balance} {account.currency} to trade against {len(symbols)} symbols.\n")
print(f"{eur_usd.name} symbol:\n{eur_usd}\n")
print(f"\tThe latest tick is:\n\t{tick}\n")
print(f"\tThe latest of {len(bars)} bars is:\n\t{bars[-1]}\n")
print(f"There are {len(signals)} signals, one of which is:\n{mt4.signal(signals[0])}\n")
print(f"Results for indicator iAC(EURUSD, 60, 1): {iac}")

```
```commandline
> I have 768.66 USD to trade against 173 symbols.
> 
> EURUSD symbol:
> Symbol(name=EURUSD, point_size=1e-05, digits=5, lot_size=100000.0, tick_value=1.0, tick_size=1e-05, min_lot=0.01, lot_step=0.01, max_lot=1000.0, margin_init=0.0, margin_maintenance=0.0, margin_hedged=0.0, margin_required=1183.65, freeze_level=0.0)
> 
> 	The latest tick is:
> 	SymbolTick(time=1596206942, bid=1.18357, ask=1.18365, last=0.0, volume=0)
> 
> 	The latest of 100 bars is:
> 	OHLCV(open=1.18498, high=1.18503, low=1.18273, close=1.18357, tick_volume=2981, time=1596204000)
> 
> There are 1000 signals, one of which is:
> Signal(author_login=Antonov-EA, broker=GBE Trading Technology Ltd, broker_server=GBEbrokers-Demo, name=FibonacciBreakout, currency=EUR, date_published=1386197632, date_started=1386194045, id=21457, leverage=200, pips=-49736, rating=789, subscribers=13, trades=9869, trade_mode=<AccountTradeMode.ACCOUNT_TRADE_MODE_CONTEST: 1>, balance=21522.68, equity=21506.7, gain=115.08, max_drawdown=57.01, price=0.0, roi=114.9)
> 
> Results for indicator iAC(EURUSD, 60, 1): -0.00173214
```
