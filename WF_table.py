
from dash import html, dash_table

from WF_table_CB import *
from G_lib import grange, getFreeParamsNames

def generate_WF_table(df,p_multi,dt_format="%Y-%m-%d"):
    for col in ['IS_from','IS_to','OOS_from','OOS_to']:     # Format date
        df[col] = df[col].dt.strftime(dt_format)

    # Insert columns: index and Params button
    df_len_range = range(len(df))
    df.insert(loc=0,column="Ind", value=[f"{str(x)}" for x in df_len_range])
    df.insert(loc=3,column="Optimize",value=["<OPT>" for x in df_len_range])

    opt_metrics_dict = {'Optimize': 
        {'options': 
            [{'label':'<OPT>','value':'<OPT>'},
            {'label':'PF','value':'PF'},
            {'label':'Sharpe','value':'Sharpe'}],
        'clearable': False},
        }

    # Insert columns: optimzable parameters
    col_index = 4
    for param in p_multi:
        # Default value will be grange.min (will be selected by default in the dropdown)
        if type(p_multi[param]) is grange:
            def_val = p_multi[param].min
        else:
            def_val = p_multi[param]
        df.insert(loc=col_index,column=param,
                value=[def_val for x in df_len_range])
        col_index = col_index + 1

    # Insert column: Backtest_IS button
    df.insert(loc=col_index,column="Backtest_IS",value=["< BT_IS >" for x in df_len_range])

    col_index = col_index + 3
    # Insert column: Backtest_OOS button
    df.insert(loc=col_index,column="Backtest_OOS",value=["< BT_OOS >" for x in df_len_range])

    # Format DataTable columns
    top_header = f"Generated {len(df)} periods"
    cols_list = []
    for col in df.columns:
        if (col in p_multi) or (col=="Optimize"):
            editable = True
            presentation = 'dropdown'
        else:
            presentation = 'input'
            editable = False
        cols_list = cols_list + \
            [{"name": [col], "id": col, "presentation": presentation, "editable": editable}]

    # Populate parameters dropdowns
    freeParams = getFreeParamsNames(p_multi)
    param_dropdown_dict = dict.fromkeys(freeParams) # Create dict with the optimizable params only
    for key in param_dropdown_dict.keys():  # for every parameter
        param_options_list = []
        for option in p_multi[key]:     # Iterate on grange
            strOption = str(option)
            param_options_list = param_options_list + [{'label':strOption,'value':option}]
        options_dict = {"options": param_options_list, "clearable": False}
        param_dropdown_dict[key] = options_dict

    full_dropdown_dict = {**opt_metrics_dict, **param_dropdown_dict}

    retVal = html.Div([
        top_header,
        dash_table.DataTable(
        id='tbl_main',
        data=df.to_dict('records'), 
        columns=cols_list,
        merge_duplicate_headers=True,
        style_cell={'textAlign': 'left', 'color': 'white'},
        style_header={'backgroundColor': 'rgb(30, 30, 30)','color': 'white'},
        style_data={'backgroundColor': 'rgb(50, 50, 50)','color': 'white'},
        style_cell_conditional=[{'if': {'column_id': 'Ind'},'textAlign': 'center'},
                                {'if': {'column_id': 'Backtest_IS'},'textAlign': 'center'},
                                {'if': {'column_id': 'Backtest_OOS'},'textAlign': 'center'}
                                ],
        editable=True,
        dropdown=full_dropdown_dict,
        css=[
                {"selector": ".dash-spreadsheet .Select-option","rule": "color: black"},
                {"selector": ".dash-spreadsheet .Select-value-label","rule": "color: white"},
                {"selector": ".Select-menu-outer", "rule":"display : block !important"},
                {"selector": "td.cell--selected, td.focused","rule": "background-color: #ffff99 !important"},
                {"selector": "td.cell--selected *, td.focused *","rule": "color: #3C3C3C !important"},
                {'selector': ".dash-spreadsheet .Select-control","rule": "background-color: rgb(50, 50, 50) !important"}
        ]
        ),
        html.Br(),
        html.Div([
        html.Button(id='submit-button-WF', n_clicks=0, children='Full backtest (WF)')
        ])
    ])
    return retVal

