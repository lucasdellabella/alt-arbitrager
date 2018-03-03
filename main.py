from ccxt.base.errors import AuthenticationError, ExchangeError
import ccxt
import pprint 
import os
from warmup import *

pp = pprint.PrettyPrinter(indent=4)
#ARB_PCT_THRESH=0.05

exchanges = load_in_exchanges()
verify_exchanges_are_active(exchanges)
fetch_nano_bids_asks(exchanges)
