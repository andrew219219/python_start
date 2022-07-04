import backtrader as bt
from matplotlib import style
import yfinance as yf
import pandas as pd
import datetime

BEKE_data = pd.read_csv('data/database/BEKE.csv', index_col=0, parse_dates=True)
BEKE_data.rename(columns={
        'Open': 'open', 
        'High': 'high', 
        'Low': 'low', 
        'Close': 'close', 
        'Adj Close': 'adj_close', 
        'Volume': 'volume'
    }, inplace=True)

# print(BEKE_data)
# exit()

class A_Strategy(bt.Strategy):
    
    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def next(self):
        self.log('close is %.2f' % (self.data.close[0]))
        if not self.position:
            if self.data.close[0] < self.data.close[-1]:

                if self.data.close[-1] < self.data.close[-2]:
                    self.log('BUY CREATE, %.2f' % self.data.close[0])
                    self.buy()
        else :
            # Already in the market ... we might sell
            if len(self) >= (self.bar_executed + 5):
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()
                
class SmaCross(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = dict(
        pfast=12,  # period for the fast moving average
        pslow=21  # period for the slow moving average
    )

    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.pfast)  # fast moving average
        sma2 = bt.ind.SMA(period=self.p.pslow)  # slow moving average
        self.crossover = bt.ind.CrossOver(sma1, sma2)  # crossover signal
        
        bt.ind.MACD()
        bt.ind.MACDHisto()
        # self.macd = macd.macd
        # self.signal = macd.signal
        # self.histo = 

    def next(self):
        if not self.position:  # not in the market
            if self.crossover > 0:  # if fast crosses slow to the upside
                self.buy()  # enter long

        elif self.crossover < 0:  # in the market & cross to the downside
            self.sell()  # close long position
            
class MACDStrategyClass(bt.Strategy):
    '''#平滑异同移动平均线MACD
        DIF(蓝线): 计算12天平均和26天平均的差，公式：EMA(C,12)-EMA(c,26)
       Signal(DEM或DEA或MACD) (红线): 计算macd9天均值，公式：Signal(DEM或DEA或MACD)：EMA(MACD,9)
        Histogram (柱): 计算macd与signal的差值，公式：Histogram：MACD-Signal

        period_me1=12
        period_me2=26
        period_signal=9

        macd = ema(data, me1_period) - ema(data, me2_period)
        signal = ema(macd, signal_period)
        histo = macd - signal

    '''

    def __init__(self):
        # sma源码位于indicators\macd.py
        # 指标必须要定义在策略类中的初始化函数中
        macd = bt.ind.MACD()
        self.macd = macd.macd
        self.signal = macd.signal
        self.histo = bt.ind.MACDHisto()

        self.dataclose = self.datas[0].close

        self.order = None
        self.buyprice = None
        self.buycomm = None

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_cashvalue(self, cash, value):
        self.log('Cash %s Value %s' % (cash, value))

    def notify_order(self, order):
        print(type(order), 'Is Buy ', order.isbuy())
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)


        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):

        if self.order: # 检查是否有指令等待执行,
            return

        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
        # Check if we are in the market
        if not self.getposition(self.datas[0]):

            # self.data.close是表示收盘价
            # 收盘价大于histo，买入
            if self.macd > 0 and self.signal > 0 and self.histo > 0:
                self.log('BUY CREATE,{}'.format(self.dataclose[0]))
                self.order = self.buy(self.datas[0])

        else:

            # 收盘价小于等于histo，卖出
            if self.macd <= 0 or self.signal <= 0 or self.histo <= 0:
                self.log('BUY CREATE,{}'.format(self.dataclose[0]))
                self.log('Pos size %s' % self.position.size)
                self.order = self.sell(self.datas[0])
    
if __name__ == '__main__':
    

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(1000000.0)
    cerebro.broker.setcommission(commission=0.001)
    
    # cerebro.addstrategy(A_Strategy)
    # cerebro.addstrategy(SmaCross)
    cerebro.addstrategy(MACDStrategyClass)
    cerebro.adddata(bt.feeds.PandasData(dataname = BEKE_data))
    
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    
    # data = bt.feeds.PandasData(dataname = BEKE_data)
    # cerebro.addstrategy(SMA_Strategy)
    # cerebro.adddata(data)

    # cerebro.run()
    cerebro.plot(style='candle')


