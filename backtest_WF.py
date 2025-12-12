import pandas as pd
import sys, time

import core
from strategies.MR1_COMP import MR1_COMP
from strategies.MR0_COMP import MR0_COMP
from strategies.MR1_COMP_I import MR1_COMP_I

import backtrader as bt
from grfx import plotPriceData, plotEquityCurve

def backtest_walk_forward(symbol,strategy,params_names,WF_params_data,data_df,startDate,endDate,CheatOnClose):

    columns = ["fromDate","toDate"] + list(params_names)
    params_df = pd.DataFrame(WF_params_data, columns=columns)

    wf_params_pack = {'pack': params_df.to_dict()}

    print(f"Backtesting WF - {strategy.to_string()} - {wf_params_pack}")
    print("Init Cerbero with COC = ",CheatOnClose)    

    # Run the backtest
    data0 = bt.feeds.PandasData(dataname=data_df)
    cerebro = core.initCerebro(symbol,data0,set_coc=CheatOnClose)
    cerebro.addstrategy(strategy,WF=True,**wf_params_pack)
    strats = cerebro.run()

    # Analyze
    analyzers_df = core.getMetricsForStrategy(strats)
    numTrades = analyzers_df["#Trades"][0]

    title = f"<b>{symbol}</b> | {startDate} to {endDate} | {numTrades} trades"

    # Plot trades
    plotPriceData(data_df,strats,title,params_df)

    # Plot Equity Curve
    equity_df = core.getEquityCurveForStrategy(strats,"Equity")
    plotEquityCurve(equity_df,strats,title,params_df)

    print(analyzers_df)
    return analyzers_df

# ---------------------------------------------------------------------

if __name__ == '__main__':

    SYMBOL = 'SPY'
    #STRATEGY = MR0_COMP
    #CHEAT_ON_CLOSE = True

    STRATEGY = MR1_COMP_I
    CHEAT_ON_CLOSE = False

    #startdate = '1995-01-01'; enddate = '1995-12-31'
    '''
    WF_params_data = [["1995-01-01","1995-03-31",2, 2.0, 1.5],
                    ["1995-04-01",  "1995-06-30",2, 2.5, 1.5],
                    ["1995-07-01",  "1995-09-30",2, 1.0, 0.5],
                    ["1995-10-01",  "1995-12-31",2, 3.0, 2.0]]
    analyzers_df = backtest_walk_forward(
        symbol,MR1_COMP,['barsLookBack','targetPCT','stopPCT'],
        WF_params_data,startdate,enddate,CheatOnClose=CHEAT_ON_CLOSE)
    #{'barsLookBack': 2,'targetPCT':2.0,'stopPCT': 2.0}
    '''
    
    Option = 3

    if Option == 1:
        STARTDATE = '1995-01-01'; ENDDATE = '1995-12-31'
        data_df = core.loadDataBySource("YFinance",SYMBOL,startdate=STARTDATE,enddate=ENDDATE)
        WF_params_data = [  ["1995-01-01","1995-03-31",2,2],
                            ["1995-04-01","1995-06-30",3,10],
                            ["1995-07-01","1995-09-30",2,7],
                            ["1995-10-01","1995-12-31",3,5]]
    elif Option == 2:
        data_df = core.loadDataBySource("CSV",SYMBOL,"SPY.csv")
        STARTDATE = data_df.index[0]; ENDDATE = data_df.index[-1]
        WF_params_data = [  ["2004-01-23","2004-02-29",2,2],
                            ["2004-03-01","2004-04-15",3,10],
                            ["2004-04-16","2004-05-28",2,5]]
    else:
        data_df = core.loadDataBySource("First","SPY","data/SPY_first_30min_partial.txt")
        STARTDATE = data_df.index[0]; ENDDATE = data_df.index[-1] 
        WF_params_data = [  ["2005-01-03","2005-09-29",2, 1.0, 0.5],
                            ["2005-09-30","2006-06-20",2, 2.0, 1.0],
                            ["2006-06-21","2007-02-26",2, 2.5, 1.5]]

    analyzers_df = backtest_walk_forward(
        SYMBOL,STRATEGY,['barsLookBack','targetPCT','stopPCT'],
        WF_params_data,data_df,STARTDATE,ENDDATE,CheatOnClose=CHEAT_ON_CLOSE)

    '''
    analyzers_df = backtest_walk_forward(
        SYMBOL,STRATEGY,['barsLookBack','barsToHold'],
        WF_params_data,data_df,STARTDATE,ENDDATE,CheatOnClose=CHEAT_ON_CLOSE)
    '''
    
    print(analyzers_df)