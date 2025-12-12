import pickle

from dash import dcc, Input, Output, State, callback, no_update

from WF_model import *
from WF_optres_table import *

# Handles table row actions (optimization, backtest)
@callback(
    Output('output-opt-text-results','children',allow_duplicate=True),
    Output('output-backtest-results','children'),
    Output('output-opt-gfx-results','children'),
    Output('output-opt-gfx-results','opened'),
    Output('lastRowClicked','children'),
    Input('tbl_main','active_cell'),
    Input('tbl_main','data'),
    State('tbl_main','data_previous'),
    State('symbol','children'),
    State('CheatOnClose','children'),
    State('strPickled_strategy','children'),
    State('strPickled_p_multi','children'),
    State('color_param','children'),
    State('data_store','data'),
    background=True,
    manager=background_callback_manager,
    prevent_initial_call=True)
def BG_CB_RowAction(active_cell,
                    table_data,
                    table_data_prev,
                    symbol,
                    CheatOnClose,
                    strPickled_strategy,
                    strPickled_p_multi,
                    color_param,
                    full_data_json):
    
    strategy = pickle.loads(bytes(strPickled_strategy,encoding='latin1'))
    p_multi = pickle.loads(bytes(strPickled_p_multi,encoding='latin1'))
    full_data_df = pd.read_json(full_data_json)
    full_data_df.index.name = 'date'

    # Optimization is triggered by dropdown metric selection
    row = getMetricSelectionRow(table_data,table_data_prev,"<OPT>")
    if row is not None:     # A metric was selected from a dropdown
        IS_fromDate = row['IS_from']
        IS_toDate = row['IS_to']
        OOS_fromDate = row['OOS_from']
        OOS_toDate = row['OOS_to']
        metricParam = row['Optimize']
        rowIndex = int(row['Ind'])
        data_df = sliceData(full_data_df,IS_fromDate,IS_toDate)

        analyzers_df, fig = optimizeRow(
            symbol,strategy,p_multi,data_df,CheatOnClose,IS_fromDate,IS_toDate,metricParam,color_param)
        
        statusStr = f"Results for optimization of row {rowIndex}:"
        opt_res_tbl = generate_opt_results_table(analyzers_df,statusStr)
        if fig is not None:
            return opt_res_tbl, no_update, dcc.Graph(id="opt-graph",figure=fig),True,rowIndex
        else:
            return opt_res_tbl, no_update, no_update,False,rowIndex

    if active_cell:
        active_cell_column_id = active_cell['column_id']
        rowIndex = active_cell['row']
        IS_fromDate = table_data[rowIndex]['IS_from']
        IS_toDate = table_data[rowIndex]['IS_to']
        OOS_fromDate = table_data[rowIndex]['OOS_from']
        OOS_toDate = table_data[rowIndex]['OOS_to']        

        if active_cell_column_id == "Backtest_IS":
            data_df = sliceData(full_data_df,IS_fromDate,IS_toDate)

            df = backtestRow(
                table_data,rowIndex,symbol,strategy,p_multi,data_df,IS_fromDate,IS_toDate,CheatOnClose)

            backtest_results = outputBacktestResults("IS",row,IS_fromDate,IS_toDate,df)
            return no_update,backtest_results,no_update,False,row

        elif active_cell_column_id == "Backtest_OOS":
            data_df = sliceData(full_data_df,OOS_fromDate,OOS_toDate)

            df = backtestRow(
                table_data,rowIndex,symbol,strategy,p_multi,data_df,OOS_fromDate,OOS_toDate,CheatOnClose)

            backtest_results = outputBacktestResults("OOS",rowIndex,OOS_fromDate,OOS_toDate,df)
            return no_update,backtest_results,no_update,False,rowIndex
        
        else:
            return no_update,no_update,no_update,False,rowIndex
    else:
        return no_update,no_update,no_update,no_update,no_update

# Handles full aggragative backtest of all periods in table
@callback(
    Output('output-backtest-results', 'children',allow_duplicate=True),
    Input('submit-button-WF','n_clicks'),
    State('tbl_main','data'),
    State('symbol','children'),
    State('strPickled_WF_strategy','children'),
    State('strPickled_p_multi','children'),
    State('data_store','data'),
    State('CheatOnClose','children'),
    background=True,
    manager=background_callback_manager,
    prevent_initial_call=True)
def BG_CB_fullBacktest(
    n_clicks,table_data,symbol,strPickled_WF_strategy,strPickled_p_multi,full_data_json,CheatOnClose):

    if n_clicks == 0:
        return

    # Unpickle strategy
    strategy_WF = pickle.loads(bytes(strPickled_WF_strategy,encoding='latin1')) 

    # Unpickle strategy parameters data and find date boundaries
    p_multi = pickle.loads(bytes(strPickled_p_multi,encoding='latin1'))
    params_names = p_multi.keys()
    WF_params_data = format_WF_params_from_table(table_data,params_names,strategy_WF.params_types)
    start = WF_params_data[0][0]; end = WF_params_data[-1][1]

    # Unjasonify the full data and slice it by WF_params periods
    full_data_df = pd.read_json(full_data_json)
    full_data_df.index.name = 'date'
    data_df = sliceData(full_data_df,start,end)
    
    df = backtest_walk_forward(
        symbol,strategy_WF,params_names,WF_params_data,data_df,start,end,CheatOnClose)

    backtest_results = "Full Backtest results: " + \
        f'{df["#Trades"][0]} trades --- PF: {df["PF"][0]:.2f} --- AnnRet: {df["AnnRet"][0]:.2f} --- MaxDD: {df["MaxDD"][0]:.2f}'    
    return backtest_results

# Handles update of parameters in table according to fig click, and styling corresponding cells
@callback(
    Output('tbl_main','style_data_conditional'),
    Output('tbl_main','data'),
    Output('tbl_main','data_previous'),
    Input('opt-graph','clickData'),
    State('opt-graph','figure'),
    State('tbl_main','data'),
    State('lastRowClicked','children'),
    prevent_initial_call=True
)
def CB_opt_graph_click(clickData,figure,tableData,lastRowClicked):
    if clickData is None:
        return no_update,no_update, None
    else:
        points = clickData['points'][0]
        x = points['x']
        y = points['y']
        
        y_param_name = figure['layout']['scene']['yaxis']['title']['text']
        x_param_name = figure['layout']['scene']['xaxis']['title']['text']

        row_index = lastRowClicked

        tableData[row_index][y_param_name] = y
        tableData[row_index][x_param_name] = x

        # Style updated cells with green bg
        style_condition = [
            {
                'if': {
                    'column_id': y_param_name,
                    'row_index': row_index
                },
                'backgroundColor': 'green',
            },
            {
                'if': {
                    'column_id': x_param_name,
                    'row_index': row_index
                },
                'backgroundColor': 'green',
            }               
        ]

        return style_condition, tableData, None
