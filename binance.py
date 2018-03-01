import ccxt
import pprint 
import os

pp = pprint.PrettyPrinter(indent=4)

b = ccxt.binance({
    'apiKey': os.environ.get('BINANCE_API_KEY'),
    'secret': os.environ.get('BINANCE_SECRET'),
})

pp.pprint(b.fetch_ticker('ETH/BTC'))
