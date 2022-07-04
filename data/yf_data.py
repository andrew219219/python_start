import yfinance as yf
import logging
import os
import pandas as pd
import datetime
import requests

logging.basicConfig(level=logging.INFO)


class DataFetcher:

    def __init__(self, stock_code):
        if stock_code is None:
            raise "stock_code can NOT empty!"
        self.stock_code = stock_code
        self.file_path = os.path.join(os.path.dirname(
            __file__), 'database', '%s.csv' % stock_code)

    def fetch(self):
        # 文件不存在，下载全量
        if not os.path.exists(self.file_path):
            logging.info("[%s]Local CSV file is not exists!" % self.stock_code)
            self._yf_download('max')
        # 文件存在，找到最终时间，查询增量
        else:
            data = pd.read_csv(self.file_path)
            latest_date = data.values[-1][0]
            logging.info("[%s]Local CSV file is exists and latest date is %s" % (
                self.stock_code, latest_date))
            # today = datetime.date.today().isoformat()

    def _yf_download(self, period):
        data = yf.download(self.stock_code, period=period)
        if(data.shape[0] == 0):
            logging.error("remote data is none")
        else:
            data.to_csv(self.file_path)


if __name__ == '__main__':
    beke = DataFetcher('BEKE')
    # kuaishou = DataFetcher('1024.HK')
    beke.fetch()
    # kuaishou.fetch()
