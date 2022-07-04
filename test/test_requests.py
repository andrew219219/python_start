import requests
r = requests.get('https://query2.finance.yahoo.com/v8/finance/chart/BEKE',
                 headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.47"})
print(r.text)