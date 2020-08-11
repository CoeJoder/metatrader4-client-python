from mt4client import MT4Client


def test_signal_names(mt4: MT4Client):
    signal_names = mt4.signal_names()
    assert isinstance(signal_names, list)
    assert len(signal_names) > 0
    print(f"Found {len(signal_names)} signal names. The first one: {signal_names[0]}")


def test_signals(mt4: MT4Client):
    signals = mt4.signals(*mt4.signal_names()[0:3])
    assert isinstance(signals, dict)
    assert len(signals) == 3
    print(f"Found {len(signals)} signals. The first one: {next(iter(signals.items()))}")
