import pandas as pd
import datetime
import matplotlib.pyplot as plt
import backtrader.analyzers as btanalyzers
import backtrader as bt


class Ketler(bt.Indicator):

    params = dict(ema=20, atr=17)

    plotinfo = dict(subplot=False)
    plotlines = dict(
        upper=dict(ls='--'),
        lower=dict(_samecolor_=True)
    )

    def __init__(self):
        self.l.expo = bt.talib.EMA(
            self.data[0].close, timeperiod=self.params.ema)
        self.l.atr = bt.talib.ATR(
            self.data.high, self.data.low, self.data.close, timeperiod=self.params.ema)
        self.l.upper = self.l.expo + self.l.atr
        self.l.lower = self.l.expo - self.l.atr


# Create a Stratey
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        # self.dataclose = self.datas[0].close
        self.ketler = Ketler()
        self.close = self.datas.close

    def next(self):
        # Simply log the closing price of the series from the reference
        if not self.position:
            if self.close[0] > self.ketler.upper[0]:
                self.order = self.order_target_percent(target=0.95)
        else:
            if self.close[0] > self.ketler.expo[0]:
                self.order = self.sell()

        self.log('Close, %.2f' % self.dataclose[0])


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    lines = ('expo', 'atr', 'upper', 'lower')
    data = bt.feeds.YahooFinanceData(
        dataname='YHOO',
        fromdate=datetime.datetime(2015, 1, 1),
        todate=datetime.datetime(2015, 12, 31),
        timeframe=bt.TimeFrame.Days)
    cerebro.adddata(data)
    cerebro.addstrategy(TestStrategy)
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0)
    cerebro.addsizer(bt.sizers.PercentSizer, percent=98)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    back = cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot(style='candle')
