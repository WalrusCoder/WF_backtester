import pandas as pd

import backtrader as bt
from strategies.MR0_COMP import MR0_COMP
from strategies.MR1_COMP_I import MR1_COMP_I
import core, grfx
from G_lib import grange

def optimizeSingleParam(
        symbol, strategy, strat_params, optimized_param, pandas_data, startdate, enddate, CheatOnClose, plotCurves=True):

    print(f"Optimizing {strategy.to_string()}: {strat_params}")
    print("Init Cerbero with COC =",CheatOnClose)

    data0 = bt.feeds.PandasData(dataname=pandas_data)

    cerebro = core.initCerebro(symbol, data0, set_coc=CheatOnClose)
    cerebro.optstrategy(strategy,**strat_params)
    strats = cerebro.run()
    analyzers_df = pd.DataFrame()
    curves_df = pd.DataFrame()

    for x in strats:    # Analyze
        
        analyzers_line_df = core.getAnalyzersForStrategy(x)  # Get line DF with params and metrics
        analyzers_df = pd.concat(                       # Concat the full line as new row
            [analyzers_df, analyzers_line_df], ignore_index=True)
        
        # Find current value of optimized parameter
        cur_optimized_param_value = x[0].params._get(optimized_param)

        # Get equity curve and add it to the DF
        cur_df  = core.getEquityCurveForStrategy(x, cur_optimized_param_value)
        curves_df = pd.concat([curves_df,cur_df], axis=1)

    if plotCurves:

        title = f"<b>{symbol}</b> | {str(strategy)} | {strat_params} | {startdate} to {enddate}"

        grfx.plotEquityCurve(curves_df,
                            strats[0],
                            title,
                            columnsToPlot=curves_df.columns)

    return analyzers_df

# ---------------------------------------------------------------------------

symbol = 'SPY'
strategy = MR1_COMP_I    # Naturally Intraday-based strat can only work with intraday data
p_single = {'barsLookBack':2, 'targetPCT':grange(2,3,0.2), 'stopPCT':1.0}

#strategy = MR0_COMP
#p_single = {'barsLookBack': grange(2,5),'barsToHold': 3}

CHEAT_ON_CLOSE = False

# Find which parameter is to be optimized (type: range)
for key,value in p_single.items():
    if type(value) is grange:
        optimized_param_name = key
        break

Option = 3

if Option == 1:
    startdate = '1995-01-01'; enddate = '1999-12-31'
    data_df = core.loadDataBySource("YFinance",symbol,startdate=startdate,enddate=enddate)
    print(data_df)
elif Option == 2:
    data_df = core.loadDataBySource("CSV",symbol,"SPY.csv")
    startdate = data_df.index[0]; enddate = data_df.index[-1]
else:
    data_df = core.loadDataBySource("First","SPY","data/SPY_first_30min_partial.txt")
    startdate = data_df.index[0]; enddate = data_df.index[-1]    

analyzers_df = optimizeSingleParam(
    symbol,strategy,p_single,optimized_param_name,data_df,startdate,enddate,CheatOnClose=CHEAT_ON_CLOSE)

print(analyzers_df)