from get_all_tickers import get_tickers as gt
from get_all_tickers.get_tickers import Region


tickers = gt.get_tickers(NYSE=True, NASDAQ=True, AMEX=True)
print(tickers[:5])