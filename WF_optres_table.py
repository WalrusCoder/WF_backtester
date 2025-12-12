import pandas as pd

from dash import html, dash_table
from dash.dash_table.Format import Format, Scheme

from WF_optres_table_CB import *

def generate_opt_results_table(df,top_header):

    # Add "id" column in order to keep original row reference after sorting
    # This will make "row_id" field available in active_cell
    df.insert(loc=0,column="id",value=[x for x in range(len(df))])

    # change to only include float analyzers
    float_analyzers_cols = ["Sharpe","MaxDD","AnnRet","NetProfit","PF"]

    # Format 2 decimal points precision
    cols_list = []
    for col in df.columns:
        if col in float_analyzers_cols:
            cur_col = [
                {"name": col, "id": col, "type":"numeric", "format":Format(precision=2, scheme=Scheme.fixed)}
            ]
        else:
            cur_col = [{"name": col, "id": col}]
        cols_list = cols_list + cur_col
    
    retVal = html.Div([
        top_header,
        dash_table.DataTable(
        id='tbl_opt_res',
        data=df.to_dict('records'),
        columns=cols_list,
        style_cell={'textAlign': 'right', 'color': 'white'},
        style_header={'textAlign': 'center', 'backgroundColor': 'rgb(30, 30, 30)','color': 'white'},
        style_data={'backgroundColor': 'rgb(50, 50, 50)','color': 'white'},
        sort_action="native",
        css=[
            {"selector": ".column-actions","rule": "order: 8"}
        ]
        )      
    ])
    return retVal

