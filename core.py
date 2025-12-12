import backtrader as bt
import backtrader.analyzers as btanalyzers

import pandas as pd
import yfinance as yf

import datetime
from pandas.tseries.offsets import *

import warnings
warnings.filterwarnings("ignore")

def initCerebro(symbol, data0, set_coc=False):

    cerebro = bt.Cerebro(stdstats=False, optreturn=False)   # optreturn=False to receive full strategies

    data0.plotinfo.plot = False     # Don't plot the prices
    cerebro.adddata(data0)

    cerebro.broker.cash = 10000
    cerebro.broker.setcommission(commission=0)
    cerebro.broker.set_coc(set_coc)
    #cerebro.broker.set_coo(True)

    cerebro.addsizer(bt.sizers.PercentSizer, percents=99)

    cerebro.addanalyzer(btanalyzers.DrawDown, _name = "DrawDown")
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name = "SharpeRatio")
    cerebro.addanalyzer(btanalyzers.Returns, _name = "Returns")
    cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name = "TradeAnalyzer")

    cerebro.addobserver(bt.observers.Value) # Equity curve
    cerebro.addobserver(bt.observers.BuySell)   # Trades

    return cerebro

def getAnalyzersForStrategy(x):     # Return full line DF including params and metrics
    curMetrics_df = getMetricsForStrategy(x)    # GEt DF with metrics line
    curParams_df = getParamsForStrategy(x)      # Get DF with params line
    analyzers_line_df = pd.concat(              # Concat them hotizontaly
        [curParams_df, curMetrics_df], axis=1)
    
    return analyzers_line_df

def getParamsForStrategy(x):        # Return a line DF of strategy's params
    params_names = x[0].params._getkeys()
    params_values = x[0].params._getvalues()
    return pd.DataFrame(data=[params_values], columns=params_names)

def getMetricsForStrategy(x):       # Return a line DF of metrics (without params)
    analyzers = x[0].analyzers

    tradeAnalyzer = analyzers.TradeAnalyzer.get_analysis()
    totalTrades = tradeAnalyzer['total']['total']
    moneyWon = tradeAnalyzer['won']['pnl']['total']
    moneyLost = tradeAnalyzer['lost']['pnl']['total'] * -1  # negative
    netPL = moneyWon - moneyLost
    if moneyLost > 0:
        PF = moneyWon / moneyLost
    else:
        PF = 10

    sharpe = analyzers.SharpeRatio.get_analysis()['sharperatio']
    maxDD = analyzers.DrawDown.get_analysis()['max']['drawdown']
    annRet = analyzers.Returns.get_analysis()['rnorm']

    data = [totalTrades, sharpe, maxDD, annRet, netPL, PF]
    columns = ['#Trades','Sharpe','MaxDD','AnnRet','NetProfit','PF']
    metrics_df = pd.DataFrame([data], columns = columns)

    return metrics_df

def OrdinalToDatetime(ordinal):
    plaindate = datetime.date.fromordinal(int(ordinal))
    date_time = datetime.datetime.combine(plaindate, datetime.datetime.min.time())
    date_time = date_time + datetime.timedelta(days=ordinal-int(ordinal))
    date_time = date_time.replace(second=0,microsecond=0)
    # Fixes backtrader's inaccurate fractional ordinal
    # This *** WILL FAIL *** with 1-min bars timeframe or higher res.
    if date_time.minute == 59:
        date_time = date_time.replace(minute=0)
        date_time = date_time + datetime.timedelta(hours=1)
    elif date_time.minute == 29:
        date_time = date_time.replace(minute=30)
    return date_time

def getEquityCurveForStrategy(x, columnName=""):
    # Get values from observer
    cur_curve = x[0].observers[0].lines.value.plot()

    #print(cur_curve)

    # Get time points from strategy
    #time_points = [datetime.date.fromordinal(int(v)) for v in x[0].data.datetime.array]
    time_points = [OrdinalToDatetime(v) for v in x[0].data.datetime.array]

    #print(time_points)

    return pd.DataFrame(cur_curve, 
                        index=time_points,
                        columns=[columnName])

def getPeriodFromData(data):
    timePoints = data.datetime.array 
    dateStart = str(datetime.date.fromordinal(int(timePoints[0])))
    dateEnd = str(datetime.date.fromordinal(int(timePoints[-1])))
    return dateStart,dateEnd

def loadYFinanceDailyData(symbol,fromDate,toDate):

    # Add 1 business day since yf.download does not include last day in loaded data
    toDate = datetime.date.fromisoformat(toDate) + BDay(1)
    return yf.download(symbol, fromDate, toDate)

def loadDataBySource(data_source,symbol=None,path=None,startdate=None,enddate=None):
    data_df = None
    if data_source == "First":
        data_df = pd.read_csv(path,
                            usecols=[0,1,2,3,4],
                            #names=['date','open','high','low','close'],
                            index_col='date',
                            parse_dates=['date'])
    elif data_source == "CSV":
        data_df = pd.read_csv(path,index_col='date',parse_dates=True)[['open','high','low','close']]
    elif data_source == "YFinance":
        data_df = loadYFinanceDailyData(symbol,startdate,enddate)
    return data_df