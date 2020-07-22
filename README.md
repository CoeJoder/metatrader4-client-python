# MetaTrader 4 -- ZeroMQ Python Client
A Python 3 client connector and API for [MT4-ZMQ Bridge](https://github.com/CoeJoder/mt4-zeromq-bridge).

## Usage
```python
from mt4client import MT4Client

# create ZeroMQ sockets and connect to bridge
mt4 = MT4Client(host="mt4terminal")

# query MT4 terminal
balance = mt4.account().balance
currency = mt4.account().currency
symbols = mt4.symbols()

print(f"I have {balance} {currency} to trade against {len(symbols)} symbols.")
```
```commandline
> I have 768.66 USD to trade against 173 symbols.
```
