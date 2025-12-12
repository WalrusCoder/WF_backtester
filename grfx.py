import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pandas.tseries.offsets import BDay

def getTradesDF(dates_index,strats):  # Return [...] from strat's buy/sell observer
    buys = strats[0].observers[1].lines.buy.plot()
    sells = strats[0].observers[1].lines.sell.plot()

    trades_df = pd.DataFrame(
        data={'Buys':buys,'Sells':sells},
        index=dates_index
    )

    #print(trades_df.to_string())
    #print(buys)

    trades_df = trades_df.dropna(how='all')     # Drop all 'nan' rows to only keep those with buy / sell
    trades_df = trades_df.reset_index()         # Turn Date from index to column
    if len(trades_df) % 2 != 0:
        trades_df = trades_df[:-1]              # Even length => trunc last
    trades_arr = np.array(trades_df).reshape(int(len(trades_df)/2),6)   # Reshape using numpy
    trades_df_r = pd.DataFrame(trades_arr)
    trades_df_r = trades_df_r.loc[:,[0,1,3,5]]  # Remove remaining Nan columns
    trades_df_r.columns = ['BuyDate','BuyPrice','SellDate','SellPrice']

    return trades_df_r

def addTradesToEquityData(fig,equity_df,strats):

    trades_df = getTradesDF(equity_df.index,strats)
    equity_df.index= pd.to_datetime(equity_df.index)

    #print(trades_df.to_string())
    #print(equity_df.to_string())

    for index,row in trades_df.iterrows():

        if row['SellPrice'] > row['BuyPrice']:
            color = "Green"
        else:
            color = "Red"

        startDate = row['BuyDate']
        endDate = row['SellDate']
        
        # Equity change displayed on the end of day of entry, so to get to the start value we plot the trade line from previous day 
        row_num = equity_df.index.get_loc(str(startDate))-1
        startDate = equity_df.index[row_num]
        startValue = equity_df.iloc[row_num]['Equity']
        endValue = equity_df.loc[str(endDate)]['Equity']
        fig.add_shape(type='line',
                    x0=startDate,
                    y0=startValue, 
                    x1=str(endDate),
                    y1=endValue,
                    line=dict(color=color))

    fig.update_shapes()
    fig.update(layout_xaxis_rangeslider_visible=False)
    
    return fig

def addTradesToPriceData(fig,price_data,strats):

    trades_df = getTradesDF(price_data.index,strats)
    for index,row in trades_df.iterrows():

        if row['SellPrice'] > row['BuyPrice']:
            color = "Green"
        else:
            color = "Red"

        fig.add_shape(type='line',
                    x0=row['BuyDate'],
                    y0=row['BuyPrice'],
                    x1=row['SellDate'],
                    y1=row['SellPrice'],
                    line=dict(color=color))

    fig.update_shapes()
    fig.update(layout_xaxis_rangeslider_visible=False)
    
    return fig

def plotPriceData(price_data,strats,title,WF_params_df=None):

    data_df_plotly = price_data.reset_index()      # Convert Date index to column
    if 'date' in data_df_plotly.columns:    # column names are lowercase
        data_df_plotly.rename(
            columns = {'date':'Date','open':'Open','high':'High','low':'Low','close':'Close'}, 
            inplace=True)

    # Plot price data
    fig = go.Figure(data=go.Ohlc(x=data_df_plotly['Date'],
                        open=data_df_plotly['Open'],
                        high=data_df_plotly['High'],
                        low=data_df_plotly['Low'],
                        close=data_df_plotly['Close']))

    fig.update_layout(title_text=title)

    # Labels with dates, params & values
    if WF_params_df is not None:
        fig = formatWFChart(fig,WF_params_df,data_df_plotly['High'].max())

    fig = addTradesToPriceData(fig,price_data,strats)

    fig.show()
    
def formatWFChart(fig,WF_params_df,max_high):    # Separators and periods parameters

    for index,row in WF_params_df.iterrows():
        
        # Labels per period
        strRange = f'<b>{row["fromDate"]} - {row["toDate"]}</b>'
        strParams = ""
        for col in range(2,len(WF_params_df.columns)):  # first two columns are "fromDate" and "toDate"
            param_name = WF_params_df.columns[col]
            param_value = row[param_name]
            strParams = strParams + \
                f'{param_name}: {param_value}<BR>'
            
        label = strRange + "<br>" + strParams
        fig.add_annotation(dict(font=dict(color='black',size=15),
                                    align="left",
                                    x=row["fromDate"],
                                    y=max_high,
                                    showarrow=False,
                                    text=label,
                                    textangle=0,
                                    xanchor='left',
                                    xref="x",
                                    yref="y"))
        
        # Horiz separators of WF periods
        if index < len(WF_params_df)-1:     
            fig.add_vline(x=row[1], line_width=1, line_dash="dash", line_color="black")  

    return fig  

def plotEquityCurve(df_equity,strats,title,WF_params_df=None,columnsToPlot="Equity"):

    # Fix px.line() issue with float column names
    df_equity.columns = df_equity.columns.astype(str)
    if columnsToPlot is list:
        columnsToPlot = [str(i) for i in columnsToPlot]

    fig = px.line(
        df_equity.reset_index(names="Date"), x='Date', y=columnsToPlot, title=title)

    if WF_params_df is not None:
        fig = formatWFChart(fig,WF_params_df,df_equity["Equity"].max())
    
    if type(columnsToPlot) == str:  # A single value (not a list with several columns to plot)
        fig = addTradesToEquityData(fig,df_equity,strats)

    fig.show()

def plot2paramsOpt(df,param1_name,param2_name,metric_name,color_param_name,plot_title="",plot_subtitle = "",showFig = True):

    #-- duplicate Y, X times
    #-- duplicate X, Y times
    #-- trunc metric
    #-- contact X,Y,metric and color_param

    Y = df.loc[:,param1_name].unique()      # Get param1 unique values - 1D data
    X = df.loc[:,param2_name].unique()      # Get param2 unique values - 1D data
    lenX = len(X)
    lenY = len(Y)
    Z = df.loc[:,metric_name].values        # Get metric data (e.g. PF) - 1D data
    Z = np.array(Z).reshape(lenY, lenX)     # Reshape it to 2D

    color_arr = df.loc[:,color_param_name]                  # Get param values used for color-coding (e.g. #Trades) - 1D data
    color_arr = np.array(color_arr).reshape(len(Y), len(X)) # Reshape it to 2D
    
     # tooltip magic ----

    Y_rep = np.tile(Y,[lenX,1]).transpose()     # Repeat Y, X times
    X_rep = np.tile(X,[lenY,1])                 # Repeat X, Y times
    tooltips = np.empty([lenY,lenX],dtype='object')     # Create empty target array with objects (used for variable length strings)

    for iy, ix in np.ndindex(tooltips.shape):
        tt = param1_name + ": " + str(Y_rep[iy,ix]) + "<br>" + \
            param2_name + ": " + str(X_rep[iy,ix]) + "<br>" + \
            metric_name + ": " + str('%.2f'%Z[iy,ix]) + "<br>" + \
            color_param_name + ": " + str(color_arr[iy,ix])
        tooltips[iy,ix] = tt

    # ---

    fig_data = [go.Surface(x=X, y=Y, z=Z, surfacecolor=color_arr, text=tooltips, hoverinfo="text")]
    fig = go.Figure(data=fig_data)
    fig.update_traces(contours_z=dict(show=True, highlightcolor="limegreen",project_z=True))
    fig.update_layout(scene = dict(
                        yaxis_title = param1_name,
                        xaxis_title = param2_name,
                        zaxis_title = metric_name,
                        xaxis = dict(tickmode="array",tickvals=X),
                        yaxis = dict(tickmode="array",tickvals=Y)),
                    width=700,
                    height=580,  # 550
                    margin=dict(r=20, b=10, l=10, t=10),
                    title=go.layout.Title(
                        text=f"{plot_title}<br>{plot_subtitle}",
                        xref="paper",yref="paper",
                        x=0,y=0.98))

    if showFig:
        fig.show()
    
    return fig
