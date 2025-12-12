import pickle

from dash import Dash, dcc, html
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc

from WF_main_CB import *
from WF_params_table import *
from __WF_defaults import *
  
app = Dash(__name__,
            external_stylesheets=[dbc.themes.DARKLY],
            background_callback_manager=background_callback_manager)
app.config.suppress_callback_exceptions=True

strPickled_p_multi = str(pickle.dumps(DEFAULT_P_MULTI),encoding='latin1')

app.layout = html.Div([
    "Symbol: ",html.B(html.Label(SYMBOL)),dmc_w_space(20),
    "Strategy: ",dmc.Text(STRATEGY.to_string(),weight="700",style={'display': 'inline-block'}),dmc.Space(h=10),
    html.Div(id='parameters',children=generateParametersTable(DEFAULT_P_MULTI)),
    dmc.Space(h=15),
    dmc.Text("From:",style={'display': 'inline-block'}), dmc_w_space(5),
    dmc.DatePicker(
        id='date-picker-from',
        minDate=DISP_STARTDATE,
        maxDate=DISP_ENDDATE,
        value=DISP_STARTDATE,
        inputFormat='DD-MM-YYYY',
        style={'width': 120, 'display': 'inline-block'},
    ), dmc_w_space(10),
    dmc.Text("To:",style={'display': 'inline-block'}), dmc_w_space(5),
    dmc.DatePicker(
        id='date-picker-to',
        minDate=DISP_STARTDATE,
        maxDate=DISP_ENDDATE,
        value=DISP_ENDDATE,
        inputFormat='DD-MM-YYYY',
        style={'width': 120, 'display': 'inline-block'},
    ), dmc_w_space(10),
    "=>",dmc_w_space(5),
    dmc.Text("",id='text-days-in-range',style={'display': 'inline-block'}),dmc_w_space(5),
    "Business days",
    dmc.Space(h=15),
    html.Div([
        html.Label("Periods:"),dmc_w_space(5),
        dcc.Input(id='input_periods',value=DEFAULT_NUM_PERIODS,type='number',min='1',step='1',size="3"),
        dmc_w_space(10),
        html.Label("IS / OOS ratio:"),dmc_w_space(5),
        dcc.Input(id='input_IO_ratio',value=DEFAULT_IO_RATIO,type='number',min='1',step='1',size="3"),
        dmc_w_space(20)," => ",dmc_w_space(20),
        html.Label("In-Sample days:"),dmc_w_space(5),
        dcc.Input(id='input_IS_days',value=DEFAULT_IS_DAYS,type='number',min='1',step='1',size="5"),dmc_w_space(10),
        html.Label("Out-of-Sample days:"),dmc_w_space(5),
        dcc.Input(id='input_OOS_days',value=DEFAULT_OOS_DAYS,type='number',min='1',step='1',size="5")
    ]), dmc.Space(h=15),
    html.Div([
        html.Button(id='submit-button', n_clicks=0, children='Generate periods')
    ]),dmc.Space(h=20),
    html.Div(id='output-periods-table'),
    html.Br(),
    html.Div(id='output-backtest-results'),
    html.Div(id='output-opt-text-results'),    
    html.Div(id='lastRowClicked',hidden='hidden'),  
    html.Div(id='strPickled_p_multi',hidden='hidden',children=strPickled_p_multi),
    html.Div(id="symbol",hidden="hidden",children=SYMBOL),       
    html.Div(id="CheatOnClose",hidden="hidden",children=CHEAT_ON_CLOSE),
    html.Div(id="strPickled_strategy",hidden="hidden",
        children=str(pickle.dumps(STRATEGY),encoding='latin1')),  
    html.Div(id="strPickled_WF_strategy",hidden="hidden",
        children=str(pickle.dumps(STRATEGY_WF),encoding='latin1')),  
    html.Div(id="metric_param", hidden="hidden",children=METRIC_PARAM),
    html.Div(id="color_param", hidden="hidden",children=COLOR_PARAM),
    dcc.Store(id='data_store', storage_type='memory'),
    html.Div(id="data_path",hidden="hidden",children=DATA_PATH),
    html.Div([
        dmc.Modal(
            id="output-opt-gfx-results",
            padding=1,
            size="auto",
            #fullScreen=True,
            centered=True,
            withCloseButton = False,
            zIndex=10000
            )
    ])
], style= {"padding": "1rem 1rem"})

if __name__ == '__main__':
    #app.run(debug=True,dev_tools_hot_reload=False,dev_tools_ui=False)
    app.run(debug=True,dev_tools_hot_reload=False)
    

