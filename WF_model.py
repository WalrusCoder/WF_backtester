import pandas as pd
from math import floor
import datetime
from pandas.tseries.offsets import BDay

import dash_mantine_components as dmc

from optimize_N_params import optimizeNParams
from backtest_WF import backtest_walk_forward
from backtest import do_backtest

from dash import DiskcacheManager

import diskcache
cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)

def sliceData(full_data_df,fromDate,toDate):
    nextDate = datetime.datetime.strptime(toDate,'%Y-%m-%d') + BDay(1)
    # checking if < toDate+BDay(1) instead of <= last day in order to include the hours of last day
    query = f"date >= '{fromDate}' and date < '{nextDate}'"
    data_df = full_data_df.query(query) 
    return data_df

# Reads csv in path and return it as df
def loadData(path): 
    df = pd.read_csv(path,index_col='date',parse_dates=True)
    return df[['open','high','low','close']]

# Checks if there was a change in metric selection and it isn't noneVal, return the row
def getMetricSelectionRow(table_data,table_data_prev,noneVal):
    if (table_data is None) or (table_data_prev) is None:
        return None
    for i in range(0,len(table_data)):
        curMetric = table_data[i]['Optimize']
        prevMetric = table_data_prev[i]['Optimize']
        if curMetric != prevMetric:
            if curMetric != noneVal:
                return table_data[i]
            return None
    return None        

def formatParamByType(param_type,param_val):
    if param_type is int:
        retVal = int(param_val)
    else:
        retVal = round(float(param_val),ndigits=2)
    # Niether int nor float: an exception!
    return retVal

def calcIODays(total_days,periods,ratio):
    OOS_days = floor(total_days / (periods + ratio))
    IS_days = ratio * OOS_days
    return IS_days,OOS_days

def dmc_w_space(px):
    return dmc.Space(w=px,style={'display': 'inline-block'})

def format_WF_params_from_table(table_data,param_names,params_types):
    WF_params_data = []
    for period in table_data:   # For each line in the main table
        dates_list = [period['OOS_from'],period['OOS_to']]
        params_values_list = []
        for param_index in range(0,len(params_types)):  # For each param type (number of param types list must be the same as param names dict keys)
            param_type = params_types[param_index]
            param_name = list(param_names)[param_index]
            param_value = period[param_name]
            params_values_list = params_values_list + [(param_type)(param_value)]
        curPeriod = dates_list + params_values_list
        WF_params_data = WF_params_data + [curPeriod]
    return WF_params_data

def format_standard_backtest_params_from_table(table_data,row,params_names,params_types):
    num_params = len(params_names)
    params_dict = dict.fromkeys(params_names)
    i = 0
    for param in params_names:
        # Convert param value from table to int of float 
        # and add to the backtest input params dict
        params_dict[param] = params_types[i](table_data[row][param])
        i =+ 1
    return params_dict

def verifyDatesAndDaysInput(val_from_date, val_to_date, IS_days, OOS_days):
    err = ""
    if (val_from_date is not None) and (val_to_date is not None):
        date_object_from = datetime.date.fromisoformat(val_from_date)
        date_object_to = datetime.date.fromisoformat(val_to_date)
        if date_object_from > date_object_to:
            err = "Error: 'From' date must be earlier than 'To' date"
        else:
            daysInRange = len(getDatesDFInRange(date_object_from,date_object_to))
            if daysInRange < int(IS_days) + int(OOS_days):
                err = "Error: Sum of IS and OOS is larger than total days in range"
    return err

def getDatesDFInRange(from_date,to_date):
    return pd.date_range(start=from_date,end=to_date,freq="B")  # Business days

# Return optimization periods in DF of ['IS_from','IS_to','OOS_from','OOS_to'] form
def generatePeriods(from_date,to_date,IS_days,OOS_days):
    df_dates = getDatesDFInRange(from_date,to_date)

    # Calculate number of periods (optimizations)
    total_days_full = len(df_dates)
    periods = floor((total_days_full - IS_days) / OOS_days)
    total_days_trimmed = IS_days + periods * OOS_days

    # Trim according to periods
    df_dates = df_dates[0:total_days_trimmed]

    list_periods = []
    for i in range(0,periods):
        index_IS_from = i * OOS_days
        index_IS_to = index_IS_from + IS_days - 1
        index_OOS_from = index_IS_to + 1
        index_OOS_to = index_OOS_from + OOS_days - 1
        IS_from = df_dates[index_IS_from]
        IS_to = df_dates[index_IS_to]
        OOS_from = df_dates[index_OOS_from]
        OOS_to = df_dates[index_OOS_to]
        list_periods = list_periods + [[IS_from,IS_to,OOS_from,OOS_to]]

    df_periods = pd.DataFrame(
        columns=['IS_from','IS_to','OOS_from','OOS_to'],
        data=list_periods)

    return df_periods

# Optimize parameters on a specific period
def optimizeRow(symbol,strategy,p_multi,data_df,CheatOnClose,fromDate,toDate,metric_param,color_param):
    analyzers_df, fig = optimizeNParams(
        symbol, 
        strategy, 
        p_multi,
        data_df,
        fromDate, 
        toDate, 
        CheatOnClose,
        metric_param,
        color_param,
        genFig=True)

    return analyzers_df, fig

def backtestRow(table_data,row,symbol,strategy,params_data,data_df,fromDate,toDate,CheatOnClose):
    params_data = format_standard_backtest_params_from_table(
                        table_data,
                        row,
                        params_data.keys(),
                        strategy.params_types)
                        
    analyzers_df = do_backtest(
                        symbol, 
                        strategy, 
                        params_data,
                        data_df,
                        fromDate, 
                        toDate,
                        CheatOnClose=CheatOnClose)
    return analyzers_df

def outputBacktestResults(bt_type,row,fromDate,toDate,df):

    trades = df["#Trades"][0]
    PF = df["PF"][0]
    annRet = df["AnnRet"][0]
    maxDD = df["MaxDD"][0]
    sharpe = df["Sharpe"][0]
    if sharpe is None:
        sharpe = 0      # No sharpe for periods smaller than a year

    return f'Backtest {bt_type} of row {row} => ' + \
            f'Trades: {trades}  |  PF: {PF:.2f}  |  Sharpe: {sharpe:.2f}  |  AnnRet: {annRet:.2f}   | MaxDD: {maxDD:.2f}'