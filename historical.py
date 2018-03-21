from math import log, exp
import ccxt
import networkx as nx
import time
import cfscrape
import concurrent.futures
import pandas as pd
import bellmanford as bf
from concurrent.futures import ThreadPoolExecutor 
from ccxt import AuthenticationError, ExchangeError, NotSupported
from ccxt import ExchangeNotAvailable, DDoSProtection, RequestTimeout

# If the exchange is unavailable, don't retry or anything, the underlying
# connection logic has already done that before throwing the exception.
# Simply abandon as a lost cause.
def initialize_exchange(ex, params = {}, verbose = False):
    try:
        ex = getattr(ccxt, ex)(params)
        ex.load_markets()
        if(verbose):
            print("Loaded exchange {}".format(ex.id))
        return ex
        # Unless you need an apiKey
    except AuthenticationError:
        if(verbose):
            print("{} needs an apiKey to load markets.".format(ex.id))
        return None
    except DDoSProtection:
        if(verbose):
            print("{} needs Cloudflare evasion.".format(ex.id))
        return initialize_exchange(ex, {'session': cfscrape.create_scraper()})
    except (ExchangeError, ExchangeNotAvailable, RequestTimeout) as err:
        if(verbose):
            print("{} - {}.".format(ex.id, err))
        return None

# Parallelized version faster by a factor of 8, almost, which is promising
# given testing on 8 cores.
# Can't use processes, must use threads because some of the locks aren't
# serializable.
def initialize_all_exes():
    with ThreadPoolExecutor() as executor:
    # Could use functools.partial to set verbose to True before mapping
        loaded = executor.map(initialize_exchange, ccxt.exchanges)
    loaded = [ex for ex in loaded if ex and ex != "bitfinex2"]
    return list(loaded)

def load_tickers(exes, markets):
    # the info key has useless crap afaict
    def get_data(ex):
        tixes = [ex.fetch_ticker(m, {'session': cfscrape.create_scraper()})
                 for m in markets]
        [t.pop('info') for t in tixes]
        df = pd.DataFrame(tixes, index = markets)
        df = df[['ask', 'bid', 'timestamp']]
        return df

    with ThreadPoolExecutor() as executor:
        tixes = executor.map(get_data, exes)
    tixes = pd.concat(tixes, keys = [x.id for x in exes],
                     names = ['exchanges', 'markets'])
    tixes.reset_index(inplace=True)
    tixes['timestamp'] = pd.to_datetime(tixes['timestamp'], unit='ms')
    return tixes

def decide(exes):
    # Get a single list of all the markets from all the exchanges
    markets = pd.concat([pd.Series(list(ex.markets.keys())) for ex in exes], axis=0)
    markets = markets.reset_index().drop('index', axis=1)[0]
    # Get the frequency count of each market (the number of exchanges it appears in)
    counts = markets.value_counts()
    # Filter out markets supported by too few exchanges
    counts = counts[counts > 10]
    markets = list(counts.index)
    # Filter exchanges based on whether all the markets picked in the previous
    # step are traded on this exchange. (As opposed to whether all markets on
    # the exchange are picked). We do this so we minimize exposure to exchanges.
    # It is hard to keep money in multiple exchanges at the same time.
    good_exes = [ex for ex in exes
                if any(m in ex.markets.keys()
                        for m in markets)]
    return good_exes, markets

# Cached results from running decide() on 03/20/2018
# markets = ['ETH/BTC', 'LTC/BTC', 'BCH/BTC', 'BTC/USD',
#            'DASH/BTC', 'BTC/EUR', 'ETH/USD', 'XRP/BTC']
# good_exes = ['bitbay', 'bitfinex', 'bitfinex2', 'bitlish', 'exmo', 'kraken']
# good_exes = [initialize_exchange(x) for x in good_exes]

# good_exes, markets = decide(exes)
# tixes = load_tickers(good_exes, markets)

# Try to find negative loops within exchanges
# Minimize number of connected components, maximize number of nodes (markets)
# Sort in descending order of markets, ascending order of connected components
# exes = initialize_all_exes()

# Find connectivity
good_exes = [x for x in exes if len(x.markets) > 10 and len(x.markets) < 200]
for ex in good_exes:
    try:
        tixes = ex.fetch_tickers()
        ms = list(tixes.keys())
        G = nx.DiGraph()
        for m in ms:
            a,b = m.split('/')
            G.add_edge(a,b, weight = log(tixes[m]['ask']))
            G.add_edge(b,a, weight = -log(tixes[m]['bid']))
        _,cycle,is_nec = bf.negative_edge_cycle(G) 
        if(is_nec):
            print("="*80)
            print(ex.id)
        while(is_nec):
            multiplier = 1
            print("Found negative edge cycle: ", cycle)
            for i in range(len(cycle)-1):
                u,v = cycle[i], cycle[i+1]
                w = G.get_edge_data(u,v)['weight']
                G.remove_edge(u,v)
                print("{} - {} has weight {}".format(u,v,exp(w)))
                multiplier *= exp(w)
            print("Multiplier is {}%".format((1/multiplier-1)*100))
            _,cycle,is_nec = bf.negative_edge_cycle(G) 
    except (NotSupported, TypeError, ValueError, AttributeError):
        pass
