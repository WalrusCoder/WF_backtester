import pickle
import datetime

from dash import callback, Input, Output, State

from WF_model import *
from WF_table import *

# Load time series data
@callback(
    Output('data_store','data'),
    Output('date-picker-from','minDate'),
    Output('date-picker-from','maxDate'),
    Output('date-picker-from','value'),
    Output('date-picker-to','minDate'),
    Output('date-picker-to','maxDate'),
    Output('date-picker-to','value'),
    Input('data_path','children'),
    Input('data_store','data'))
def CB_loadData(path,data):
    data_df = loadData(path)
    startDateTime = data_df.index[0]
    endDateTime = data_df.index[-1]
    # Create date objects from the datetime data (ignore HHMMSS)
    startDate = datetime.date(startDateTime.year, startDateTime.month, startDateTime.day)
    endDate = datetime.date(endDateTime.year, endDateTime.month, endDateTime.day)

    return data_df.to_json(),startDate,endDate,startDate,startDate,endDate,endDate

# Handles calcualation and output of business days in selected days range
@callback(
    Output('text-days-in-range','children'),
    Input('date-picker-from','value'),
    Input('date-picker-to','value'))
def CB_calcDaysInRange(date_value_from,date_value_to):
    days = len(getDatesDFInRange(date_value_from,date_value_to))
    return days

# Handles calcualation of IO and OOS days values according to periods and ratio
@callback(
    Output('input_IS_days','value'),
    Output('input_OOS_days','value'),
    Input('text-days-in-range','children'),
    Input('input_periods','value'),
    Input('input_IO_ratio','value'))
def CB_calcIODays(total_days,periods,ratio):
    IS_days, OOS_days = calcIODays(int(total_days),int(periods),int(ratio))
    return IS_days,OOS_days

# Handles sumbission of dates and IS / OOS settings
@callback(
    Output('output-periods-table', 'children'),
    Output('output-backtest-results','children',allow_duplicate=True),
    Output('output-opt-text-results','children',allow_duplicate=True),
    Input('submit-button','n_clicks'),
    State('date-picker-from', 'value'),
    State('date-picker-to', 'value'),
    State('input_IS_days','value'),
    State('input_OOS_days','value'),
    State('strPickled_p_multi','children'),
    prevent_initial_call=True)
def CB_generateTable(n_clicks,date_value_from,date_value_to,IS_days,OOS_days,strPickled_p_multi):
    # bytes(strat_params,encoding='latin1')
    p_multi = pickle.loads(bytes(strPickled_p_multi,encoding='latin1'))
    if n_clicks == 0:
        return
    err = verifyDatesAndDaysInput(date_value_from,date_value_to,IS_days,OOS_days)
    if err == "":
        df_periods = generatePeriods(date_value_from,date_value_to,int(IS_days),int(OOS_days))
        return generate_WF_table(df_periods,p_multi),"",""
    else:
        return err,"",""
