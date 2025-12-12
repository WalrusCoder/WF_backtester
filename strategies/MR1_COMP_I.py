import datetime
import pandas as pd

import backtrader as bt

from G_lib import lower_bars_I
from strategies.WF import WF
from core import OrdinalToDatetime

# Use 30min bars
# Record daily closes at the 15:30 bar (that ends at 16:00)
#                       *** check earlier EODs during holidays ***
# This is determined accoring to NASDAQ core trading that ends at 16:00, and volume changes. Inconsistent with daily bars close.
# Evaluate entries at 15:00 bar (that ends at 15:30) and execute at next bar's open (15:30)
class MR1_COMP_I(bt.Strategy, WF):

    daily_closes = []

    params_types = [int,float,float]

    params = (('pack',""),('barsLookBack', 2),('targetPCT', 2.0),('stopPCT', 2.0),)
    usableParams = {'barsLookBack': 2,'targetPCT':2.0,'stopPCT': 2.0}
    do_log = False

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
            d['targetPCT'] = self.params.targetPCT
            d['stopPCT'] = self.params.stopPCT

        self.lastExecOrder = None       # For monitoring only
        self.lastOpenTradePrice = None  # For monitoring only

    def buy_criteria(self,curTime):
        # Bar that starts @ 15:00 and ends @ 15:30. Entry may occur at next bar's open (15:30)
        if not (curTime.hour == 15 and curTime.minute == 0):   
            return False

        if self.WF:
            curDate = datetime.date.fromordinal(int(self.datas[0].datetime[0]))
            self.usableParams = self.getWFParamsForDate(curDate)
        barsLookBack = self.usableParams['barsLookBack']

        # Current day's close for the sake of buying is approximated at 15:30
        # If in criteria, buying will take place at open of next bar
        closes_to_eval = self.daily_closes + [self.datas[0].close[0]]
        if (len(closes_to_eval) > barsLookBack) and \
            lower_bars_I(closes_to_eval,barsLookBack):
            self.log(f"Price at end of 15:00 bar: {self.datas[0].close[0]}")
            self.log(f"Buy @ open of  next bar (COC = False)")
            return True
        return False

    def notify_trade(self, trade):
        order_exec_price = self.lastExecOrder.executed.price
        order_exec_date = datetime.date.fromordinal(int(self.lastExecOrder.executed.dt))

        if not trade.isclosed:
            self.log(f"Bought {order_exec_date} @ {order_exec_price:.3f}")
            self.lastOpenTradePrice = order_exec_price
        else:
            pctChange = ((order_exec_price / self.lastOpenTradePrice) - 1) * 100
            self.log(
                f"trade was closed: {order_exec_date} @ {order_exec_price:.3f} ({pctChange:.2f}%)")

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:   # order's with broker
            return

        # Check if an order has been completed (broker could reject order if not enough cash)
        if order.status in [order.Completed]:
            self.lastExecOrder = order
            self.pendingOrder = None   # Note no pending order

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.pendingOrder = None   # Note no pending order

    def next(self):

        # Record daily closes
        curTime = OrdinalToDatetime(self.datas[0].datetime[0])

        if curTime.hour == 15 and curTime.minute == 30: 
            self.daily_closes.append(self.datas[0].close[0])
            self.log("DC: " + str(self.datas[0].close[0]))

        if self.pendingOrder:  # an order is pending
            return

        if not self.position:
            if self.buy_criteria(curTime):
                curClose = self.data.close[0]
                targetPrice = curClose * (1 + self.usableParams['targetPCT'] / 100)
                stopPrice = curClose * (1 - self.usableParams['stopPCT'] / 100)
                orders_list = self.buy_bracket(
                    exectype=bt.Order.Market,
                    stopprice=stopPrice,
                    limitprice=targetPrice
                )
                # Keep track of the created order to avoid a 2nd order
                self.pendingOrder = orders_list[0]  # orders_list has [main, stop, limit]
                self.log(
                    f"{curTime} " + 
                    f"Bracket: Buy market @ {curClose:.3f}, " + 
                    f"Limit @ {targetPrice:.3f} ({((targetPrice/curClose)-1)*100:.2f}%), " + 
                    f"Stop @ {stopPrice:.3f} ({((stopPrice-curClose)/curClose)*100:.2f}%)")

    @classmethod
    def to_string(cls):
        return "MR1_COMP_I"