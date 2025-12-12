import pandas as pd

import backtrader as bt

from strategies.MR1_COMP_I import MR1_COMP_I
from strategies.MR1_COMP import MR1_COMP
from strategies.MR0_COMP import MR0_COMP

import core
from grfx import plotPriceData, plotEquityCurve
from G_lib import grange

def do_backtest(symbol, strategy, params_data, data_df, startDate, endDate, CheatOnClose, plot=True):

    data0 = bt.feeds.PandasData(dataname=data_df)

    print(f"Backtesting {strategy.to_string()}: {params_data}")
    print("Init Cerbero with COC = ",CheatOnClose)

    cerebro = core.initCerebro(symbol, data0, set_coc=CheatOnClose)
    cerebro.addstrategy(strategy,**params_data)
    strats = cerebro.run()

    # Analyze results
    metrics_df = core.getMetricsForStrategy(strats)
    params_df = pd.DataFrame().from_dict([params_data])
    analyzers_df = pd.concat([params_df, metrics_df], axis=1)

    if plot:

        # Plot Equity Curve
        numTrades = analyzers_df["#Trades"][0]
        title = f"<b>{symbol}</b> | <b>{strategy.to_string()}</b> | {params_data} | {startDate} to {endDate} | {numTrades} trades"
        equity_df = core.getEquityCurveForStrategy(strats,"Equity")

        plotEquityCurve(equity_df,strats,title)
        plotPriceData(data_df,strats,title)     # Plot Trades on price chart

    print(analyzers_df)
    return analyzers_df

if __name__ == '__main__':

    symbol = 'SPY'
    #strategy = MR0_COMP; p = {'barsLookBack':2, 'barsToHold':4}
    #strategy = MR1_COMP; p = {'barsLookBack':2, 'targetPCT':2.0, 'stopPCT':1}
    strategy = MR1_COMP_I; p = {'barsLookBack':2, 'targetPCT':2.0, 'stopPCT':1}

    Option = 3

    if Option == 1:
        startdate = '1996-01-01'; enddate = '1996-12-31'
        data_df = core.loadDataBySource("YFinance","SPY",startdate=startdate,enddate=enddate)
    elif Option == 2:
        data_df = core.loadDataBySource("CSV","SPY","SPY.csv")
        startdate = data_df.index[0]; enddate = data_df.index[-1]
    else:
        data_df = core.loadDataBySource("First","SPY","data/SPY_first_30min_partial.txt")
        startdate = data_df.index[0]; enddate = data_df.index[-1]        

    analyzers_df = do_backtest(symbol,strategy,p,data_df,startdate,enddate,CheatOnClose=False)
