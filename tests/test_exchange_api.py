from ccxt.base.errors import AuthenticationError, ExchangeError
import ccxt
import pprint 
import os
import pytest

@pytest.fixture(scope='module')
def exchanges_fix():
    exchanges = []
    # LOAD IN EXCHANGES
    binance = ccxt.binance({
        'apiKey': os.environ.get('BINANCE_API_KEY'),
        'secret': os.environ.get('BINANCE_SECRET'),
    })

    bitz = ccxt.bitz({
        'apiKey': os.environ.get('BITZ_API_KEY'),
        'secret': os.environ.get('BITZ_SECRET'),
    })

    exchanges.append(binance)
    exchanges.append(bitz)

    # Warm up markets 
    #(I believe this corrects some incorrect hard coding on ccxt's part
    for ex in exchanges:
        ex.load_markets()

    return exchanges

## TESTS
def test_api_key_verified(exchanges_fix):
    # VERIFY EXCHANGES ARE ACTIVE
    for ex in exchanges_fix:
        try:
            try:
                ex.fetch_open_orders()
            except ExchangeError:
                pass
            print('=== ' + ex.name + (' ' * (12 - len(ex.name))) + ' ready ===')
        except AuthenticationError:
            print(ex.name + ' failed to load, removing from exchange list.')
            print(e)

def test_xrb_trade_pairing_exists(exchanges_fix):
    binance = exchanges_fix[0]
    # FETCH BIDS AND ASKS ACROSS ALL EXCHANGES
    ticker = binance.fetch_ticker('XRB/BTC')
    assert ticker
    assert ticker['symbol'] == 'XRB/BTC'
