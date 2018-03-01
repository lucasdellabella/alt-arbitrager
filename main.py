from ccxt.base.errors import AuthenticationError, ExchangeError
import ccxt
import pprint 
import os

pp = pprint.PrettyPrinter(indent=4)
exchanges = []

def load_in_exchanges():
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

def verify_exchanges_are_active():
    # VERIFY EXCHANGES ARE ACTIVE
    for ex in exchanges:
        try:
            try:
                ex.fetch_open_orders()
            except ExchangeError:
                pass
            print('=== ' + ex.name + (' ' * (12 - len(ex.name))) + ' ready ===')
        except AuthenticationError:
            print(ex.name + ' failed to load, removing from exchange list.')
            print(e)

def fetch_nano_bids_asks():
    # FETCH BIDS AND ASKS ACROSS ALL EXCHANGES
    for ex in exchanges:
        ticker = ex.fetch_ticker('XRB/BTC')
        info = ticker['info']
        print('= ' + ex.name)
        print(info)

load_in_exchanges()
verify_exchanges_are_active()
fetch_nano_bids_asks()

#pp.pprint(bitz.fetch_ticker('XRB/BTC'))
#pp.pprint(binance.fetch_ticker('XRB/BTC'))
