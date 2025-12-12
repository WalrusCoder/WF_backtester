import datetime
import pandas as pd

import backtrader as bt

from G_lib import lower_bars
from strategies.WF import WF

class MR0_COMP(bt.Strategy, WF):

    params_types = [int,int]
    params = (('pack',''),('barsLookBack', 2),('barsToHold', 5),)
    usableParams = {'barsLookBack': 2,'barsToHold': 5}
    do_log = True

    def __init__(self,WF=False):
        self.WF = WF
        self.pendingOrder = None

        if self.WF:
            self.df_pack = pd.DataFrame().from_dict(self.params.pack)
            if self.do_log:
                self.printWFParams()
        else:
            d = self.usableParams
            d['barsLookBack'] = self.params.barsLookBack
            d['barsToHold'] = self.params.barsToHold

        self.lastExecOrder = None       # For monitoring only
        self.lastOpenTradePrice = None  # For monitoring only

    def buy_criteria(self):
        if self.WF:
            curDate = datetime.date.fromordinal(int(self.datas[0].datetime[0]))
            self.usableParams = self.getWFParamsForDate(curDate)    
        barsLookBack = self.usableParams['barsLookBack']
        if len(self) > barsLookBack and lower_bars(self.datas[0].close,barsLookBack):
            self.log(f"Buy @ close of this bar (Cheat on Close)")
            return True
        return False

    def sell_criteria(self):
        barsToHold = self.usableParams['barsToHold']
        if len(self) >= (self.bar_executed + barsToHold - 1):
            return True
        return False

    def notify_trade(self, trade):
        order_exec_price = self.lastExecOrder.executed.price
        order_exec_date = datetime.date.fromordinal(int(self.lastExecOrder.executed.dt))

        if not trade.isclosed:
            self.log(f"Bought {order_exec_date} @ {order_exec_price}")
            self.lastOpenTradePrice = order_exec_price
        else:
            pctChange = ((order_exec_price / self.lastOpenTradePrice) - 1) * 100
            self.log(
                f"trade was closed: {order_exec_date} @ {order_exec_price} [{pctChange:.2f}%]")

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:   # order's with broker
            return

        # Check if an order has been completed (broker could reject order if not enough cash)
        if order.status in [order.Completed]:
            self.bar_executed = len(self)
            self.lastExecOrder = order

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            pass

        self.pendingOrder = None   # Note no pending order

    def next(self):

        if self.pendingOrder:  # an order is pending
            return

        if not self.position:
            if self.buy_criteria():
                self.pendingOrder = self.buy()     # Keep track of the created order to avoid a 2nd order
        else:
            if self.sell_criteria():
                self.pendingOrder = self.sell()

    @classmethod
    def to_string(cls):
        return "MR0_COMP"
