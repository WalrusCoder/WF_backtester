import pickle
import pandas as pd
import datetime

from dash import Input, Output, State, no_update, callback

from backtest import do_backtest

@callback(
    Output('data_store','data'),
    Input('data_path','children'),
    Input('data_store','data'))
def CB_loadData(path,data):
    data_df = pd.read_csv(path,index_col='date',parse_dates=True)[['open','high','low','close']]
    startDateTime = data_df.index[0]
    endDateTime = data_df.index[-1]
    # Create date objects from the datetime data (ignore HHMMSS)
    startDate = datetime.date(startDateTime.year, startDateTime.month, startDateTime.day)
    endDate = datetime.date(endDateTime.year, endDateTime.month, endDateTime.day)
    return data_df.to_json()

@callback(
    Output('opt-N-params-status','children'),
    Input('opt-N-params-graph','clickData'),     #everything below that was Input
    State('strat-params','children'),
    State('plotted_param_1','children'),
    State('plotted_param_2','children'),
    State('symbol','children'),
    State('startdate','children'),
    State('enddate','children'),
    State('strategy','children'),
    State('cheat-on-close','children'),
    State('data_store','data'),
    prevent_initial_call=True)  # Make sure this does not get called before CB_loadData()
def CB_opt_N_params_graph_click(clickData,
                                strat_params,
                                plotted_param_1,
                                plotted_param_2,
                                symbol,
                                startdate,
                                enddate,
                                strategy,
                                CheatOnClose,
                                json_data):
    if clickData is None:
        return no_update
    else:
        points = clickData['points'][0]
        x = points['x']
        y = points['y']

        # Moving from p_multi:
        # {'barsLookBack':2, 'targetPCT':grange(1.0,3,0.5), 'stopPCT':grange(1,2,0.5)}
        # to backtest_params_data: 
        # {'barsLookBack':2, 'targetPCT':2.0, 'stopPCT':1}
        # Only update parameters that were optimized (there might be MANY fixed parameters)

        backtest_params_data = pickle.loads(bytes(strat_params,encoding='latin1'))
        backtest_params_data[plotted_param_1] = y
        backtest_params_data[plotted_param_2] = x

        strategy = pickle.loads(bytes(strategy,encoding='latin1'))
        data_df = pd.read_json(json_data)
        data_df.index.name = 'date'

        do_backtest(symbol,
                    strategy,
                    backtest_params_data,
                    data_df,
                    startdate,
                    enddate,
                    CheatOnClose=CheatOnClose,
                    plot=True)

        return (f"{plotted_param_1}: {x}, {plotted_param_2}: {y}")