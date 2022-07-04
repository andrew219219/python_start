from binance.spot import Spot 

client = Spot()
# Get server timestamp
print(client.time())
# Get klines of BTCUSDT at 1d interval
print(client.klines("BTCUSDT", "1d"))

# from binance.spot import Spot as Client

# client = Client(timeout = 1)
# print(client.time())