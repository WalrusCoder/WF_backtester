import datetime
import pandas as pd

import backtrader as bt

from G_lib import lower_bars
from strategies.WF import WF

class MR1_COMP(bt.Strategy, WF):    # Using bracket

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

    def buy_criteria(self):
        if self.WF:
            curDate = datetime.date.fromordinal(int(self.datas[0].datetime[0]))
            self.usableParams = self.getWFParamsForDate(curDate)
        barsLookBack = self.usableParams['barsLookBack']
        if len(self) > barsLookBack and lower_bars(self.datas[0].close,barsLookBack):
            self.log(f"Buy @ close of this bar (Cheat on Close)")
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

        if self.pendingOrder:  # an order is pending
            return

        if not self.position:
            if self.buy_criteria():
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
                    f"Bracket: Buy market @ {curClose:.3f}, " + 
                    f"Limit @ {targetPrice:.3f} ({((targetPrice/curClose)-1)*100:.2f}%), " + 
                    f"Stop @ {stopPrice:.3f} ({((stopPrice-curClose)/curClose)*100:.2f}%)")

    @classmethod
    def to_string(cls):
        return "MR1_COMP"