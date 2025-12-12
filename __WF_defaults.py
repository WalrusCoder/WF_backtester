
from strategies.MR1_COMP_I import MR1_COMP_I
from strategies.MR1_COMP import MR1_COMP
from strategies.MR0_COMP import MR0_COMP
from G_lib import grange

METRIC_PARAM = "PF"
COLOR_PARAM = "#Trades"
# ['#Trades','Sharpe','MaxDD','AnnRet','NetProfit','PF']

SYMBOL = 'SPY'
#DATA_PATH = 'data/SPY_first_30min_partial.txt'
DATA_PATH = 'data/SPY_first_30min_RTH.txt'
DISP_STARTDATE = '1995-01-01'   # Redundant (inferred from data file)
DISP_ENDDATE = '1996-12-31'     # Redundant (inferred from data file)
DEFAULT_IS_DAYS = 200
DEFAULT_OOS_DAYS = 100
DEFAULT_NUM_PERIODS = 3
DEFAULT_IO_RATIO = 2

#STRATEGY = MR0_COMP; STRATEGY_WF = MR0_COMP
#DEFAULT_P_MULTI = {'barsLookBack': grange(2,3,1),'barsToHold': grange(1,5,1)}

#STRATEGY = MR1_COMP; STRATEGY_WF = MR1_COMP
#DEFAULT_P_MULTI = {'barsLookBack': 2,'targetPCT': grange(0.5,2,0.5),'stopPCT': grange(1,3,0.5)}

STRATEGY = MR1_COMP_I; STRATEGY_WF = MR1_COMP_I
DEFAULT_P_MULTI = {'barsLookBack': 2,'targetPCT': grange(0.5,2,0.5),'stopPCT': grange(1,3,0.5)}

CHEAT_ON_CLOSE = False