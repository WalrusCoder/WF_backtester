import pandas as pd

from strategies.MR0_COMP import MR0_COMP
import backtrader as bt
from grfx import plot2paramsOpt
import core
from G_lib import grange

def optimizeTwoParams(symbol, strategy, strat_params, pandas_data, startdate, enddate, CheatOnClose, plot=True):

    print(f"Optimizing {strategy.to_string()}: {strat_params}")

    #pandas_data = core.loadYFinanceDailyData(symbol,startdate,enddate)
    data0 = bt.feeds.PandasData(dataname=pandas_data)

    print("Init Cerbero with COC =",CheatOnClose)
    cerebro = core.initCerebro(symbol, data0,set_coc=CheatOnClose)

    cerebro.optstrategy(strategy,**strat_params)
    strats = cerebro.run()

    analyzers_df = pd.DataFrame()

    for x in strats:    # Analyze
        analyzers_line_df = core.getAnalyzersForStrategy(x)  # Get line DF with params and metrics
        analyzers_df = pd.concat(           # Concat the full line as new row
            [analyzers_df, analyzers_line_df], ignore_index=True)

    p1_name = analyzers_df.columns[1]   # column 0 is "pack"
    p2_name = analyzers_df.columns[2]
    start, end = core.getPeriodFromData(data0)
    fig = plot2paramsOpt(
        analyzers_df,p1_name,p2_name,'PF','#Trades',symbol,f"{start} to {end}",showFig=False)

    if plot:
        fig.show()
        return analyzers_df
    else:
        return analyzers_df,fig

# ---------------------------------------------------------------------------

if __name__ == '__main__':
    symbol = 'SPY'
    strategy = MR0_COMP
    p_multi = {'barsLookBack': grange(2,3,1),'barsToHold': grange(1,5,1)}
    CheatOnClose = True

    Option = 2

    if Option == 1:
        startdate = '1995-01-01'; enddate = '1999-12-31'
        data_df = core.loadDataBySource("YFinance",symbol,startdate=startdate,enddate=enddate)
    elif Option == 2:
        data_df = core.loadDataBySource("CSV",symbol,"SPY.csv")
        startdate = data_df.index[0]; enddate = data_df.index[-1]
    
    analyzers_df = optimizeTwoParams(
        symbol, strategy, p_multi, data_df, startdate, enddate, CheatOnClose=CheatOnClose)

    print(analyzers_df)

