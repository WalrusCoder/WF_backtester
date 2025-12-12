import pandas as pd

import backtrader as bt
from grfx import plot2paramsOpt
import core
from G_lib import grange, getFreeParamsNames
from strategies.MR1_COMP import MR1_COMP
from strategies.MR1_COMP_I import MR1_COMP_I

import pickle

def optimizeNParams(symbol, 
                    strategy, 
                    strat_params,
                    pandas_data,
                    startdate, enddate, 
                    CheatOnClose,
                    metric_param,
                    color_param,
                    genFig=False):

    #pandas_data = core.loadYFinanceDailyData(symbol,startdate,enddate)
    data0 = bt.feeds.PandasData(dataname=pandas_data)

    print(f"Optimizing {strategy.to_string()}: {strat_params}")
    print("Init Cerbero with COC = ",CheatOnClose)

    cerebro = core.initCerebro(symbol,data0,set_coc=CheatOnClose)
    cerebro.optstrategy(strategy,**strat_params)
    strats = cerebro.run()

    analyzers_df = pd.DataFrame()

    for x in strats:    # Analyze
        analyzers_line_df = core.getAnalyzersForStrategy(x)  # Get line DF with params and metrics
        analyzers_df = pd.concat(           # Concat the full line as new row
            [analyzers_df, analyzers_line_df], ignore_index=True)

    start, end = core.getPeriodFromData(data0)
    
    plottableParams = list(getFreeParamsNames(strat_params))

    if genFig and len(plottableParams) == 2:
        fig = plot2paramsOpt(
            analyzers_df,
            plottableParams[0],
            plottableParams[1],
            metric_param,
            color_param,
            f"<B>{symbol}</B> | <B>{strategy.to_string()}</B><br>{strat_params}",
            f"{start} to {end}",
            showFig=False)

        return analyzers_df,fig
    else:
        return analyzers_df, None

# ---------------------------------------------------------------------------

if __name__ == '__main__':

    SYMBOL = 'SPY'
    #STRATEGY = MR1_COMP
    #CHEAT_ON_CLOSE = True
    STRATEGY = MR1_COMP_I   # requires intra data
    CHEAT_ON_CLOSE = False
    DEFAULT_STRAT_PARAMS = \
        {'barsLookBack':2, 'targetPCT':grange(2.0,3,0.2), 'stopPCT':grange(1,2,0.2)}
    METRIC_PARAM = "PF"
    COLOR_PARAM = "#Trades"

    USE_DASH = True     # Applicable for options 2 and 3

    Option = 3

    if Option == 1:
        STARTDATE = '1995-01-01'; ENDDATE = '1999-12-31'
        data_df = core.loadDataBySource("YFinance",SYMBOL,startdate=STARTDATE,enddate=ENDDATE)
    elif Option == 2:
        DATA_PATH = "SPY.csv"
        data_df = core.loadDataBySource("CSV",SYMBOL,DATA_PATH)
        STARTDATE = data_df.index[0]; ENDDATE = data_df.index[-1]
    else:
        DATA_PATH = "data/SPY_first_30min_partial.txt"
        data_df = core.loadDataBySource("First","SPY",DATA_PATH)
        STARTDATE = data_df.index[0]; ENDDATE = data_df.index[-1] 

    analyzers_df, fig = optimizeNParams(
        SYMBOL, STRATEGY, DEFAULT_STRAT_PARAMS, data_df, STARTDATE, ENDDATE, 
        CHEAT_ON_CLOSE, METRIC_PARAM, COLOR_PARAM, genFig=True)

    #print(analyzers_df)

    if not USE_DASH:
        fig.show()
    else:

        from dash import Dash, dcc, html
        from optimize_N_params_CB import *

        plottableParams = list(getFreeParamsNames(DEFAULT_STRAT_PARAMS))

        app = Dash(__name__)
        app.layout = html.Div([
            dcc.Graph(id="opt-N-params-graph",figure=fig),
            html.Div(id="opt-N-params-status"),
            html.Div(id="symbol",hidden="hidden",children=SYMBOL),            
            html.Div(id="strategy",hidden="hidden",
                children=str(pickle.dumps(STRATEGY),encoding='latin1')),                
            html.Div(id="strat-params",hidden="hidden",
                children=str(pickle.dumps(DEFAULT_STRAT_PARAMS),encoding='latin1')),
            html.Div(id="plotted_param_1",hidden="hidden",children=plottableParams[0]),
            html.Div(id="plotted_param_2",hidden="hidden",children=plottableParams[1]),
            html.Div(id="startdate",hidden="hidden",children=STARTDATE),
            html.Div(id="enddate",hidden="hidden",children=ENDDATE),
            html.Div(id="cheat-on-close",hidden="hidden",children=CHEAT_ON_CLOSE),
            dcc.Store(id='data_store', storage_type='memory'),
            html.Div(id="data_path",hidden="hidden",children=DATA_PATH)
        ])
        app.run(debug=True)
