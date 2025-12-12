import pandas as pd
import pickle

from dash import html, dash_table, callback, Input, Output, State, no_update
import dash_mantine_components as dmc

from G_lib import grange
from WF_model import *

def generateParametersTable(p_multi):

    data = []
    for key,value in p_multi.items():
        if type(value) is grange:
            curParam = [key,value.min,value.max,value.step]
        else:   # single number
            curParam = [key,value,"",""]
        data = data + [curParam]

    df = pd.DataFrame(columns=["Parameter","Min","Max","Step"], data=data)

    cols_list = [
        {'name':'Parameter','id':'Parameter','editable':False},
        {'name':'Min','id':'Min','editable':True},
        {'name':'Max','id':'Max','editable':True},
        {'name':'Step','id':'Step','editable':True},
        {'name':'Type','id':'Type','editable':False},
        {'name':'#Vals','id':'#Vals','editable':False},
        {'name':'List','id':'List','editable':False}
    ]

    retVal = html.Div([
        dash_table.DataTable(
            id='tbl_params',
            data=df.to_dict('records'), 
            columns=cols_list,
            style_table={'width': '900px'},
            style_cell={'textAlign': 'right', 'color': 'white', 'width': '70px'},
            style_header={'textAlign': 'left','backgroundColor': 'rgb(30, 30, 30)','color': 'white'},
            style_data={'backgroundColor': 'rgb(50, 50, 50)','color': 'white'},
            style_cell_conditional=[
                {'if': {'column_id': 'Parameter'},'width': '100px','textAlign':'left'},
                {'if': {'column_id': 'List'},'width': '500px','textAlign':'left'},
                {'if': {'column_id': '#Vals'},'textAlign':'center'},
                {'if': {'column_id': 'Type'},'textAlign':'center'},
            ],
            style_data_conditional=[
                {'if': {'column_id': 'List'},'backgroundColor': 'rgb(20, 20, 20)','color': 'rgb(180, 180, 180)'},
                {'if': {'column_id': '#Vals'},'backgroundColor': 'rgb(20, 20, 20)','color': 'rgb(180, 180, 180)'},
                {'if': {'column_id': 'Type'},'backgroundColor': 'rgb(20, 20, 20)','color': 'rgb(180, 180, 180)'},
            ],
            editable=True,
            css=[
                    {"selector": ".dash-spreadsheet .Select-option","rule": "color: black"},
                    {"selector": ".dash-spreadsheet .Select-value-label","rule": "color: white"},
                    {"selector": ".Select-menu-outer", "rule":"display : block !important"},
                    {'selector': 'td.cell--selected, td.focused','rule': 'background-color: #ffff99 !important'},
                    {'selector': 'td.cell--selected *, td.focused *','rule': 'color: #3C3C3C !important'}
            ]
        ),dmc.Space(h=15),
        html.Div(id="readable-p-multi"),
        dmc.Text(id='params_err',color='red',weight='700'),
    ])

    return retVal

@callback(
    Output('tbl_params','data'),
    Output('readable-p-multi','children'),
    Output('params_err','children'),
    Output('strPickled_p_multi','children'),
    Input('tbl_params','data'),
    State('strPickled_strategy','children')
)
def CB_params_tbl_change(table_data,strPickled_strategy):
    
    strategy = pickle.loads(bytes(strPickled_strategy,encoding='latin1')) 
    params_types = strategy.params_types
    p_multi = {}

    err = ""

    try:
        i = 0
        for row in table_data:
            Parameter = row['Parameter']
            param_type = params_types[i]
            row['Type'] = param_type.__name__

            Min = row['Min']; Max = row['Max']; Step = row['Step']

            numValues = 0
            listValues = []
            if (Max == '' or Max is None) and (Step == '' or Step is None):
                # Min value only => a fixed value for the param (no optimization)
                p_multi[Parameter] = formatParamByType(param_type,Min)
                listValues = p_multi[Parameter]
                numValues = 1
            else:
                Min = formatParamByType(param_type,Min)
                Max = formatParamByType(param_type,Max)
                Step = formatParamByType(param_type,Step)
                p_multi[Parameter] = grange(Min,Max,Step)
                if (Min >= Max) or (Step > Max-Min) or (Step <= 0):
                    err = f"{Parameter}: Min must be smaller than Max, Step must be positive and smaller or equal to Max-Min."
                    listValues = ""
                    numValues = 0                    
                else:
                    listValues = list(grange(Min,Max,Step))
                    numValues = len(listValues)
            row['#Vals'] = numValues
            row['List'] = str(listValues)
            i += 1

    except Exception as e:
        err = "Only int, float and empty string are accepted"

    if err == "":
        strPickled_p_multi = str(pickle.dumps(p_multi),encoding='latin1')
        return table_data,str(p_multi),"",strPickled_p_multi
    else:
        return table_data,"",err,""