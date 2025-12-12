import backtrader as bt

# Given parameters dict, returns a new dict with the grange params only (same order)
def getFreeParamsNames(strat_params):
    retDict = {}
    for paramName, paramValues in strat_params.items():
        if type(paramValues) is grange:
            retDict[paramName] = paramValues
    return retDict


class grange(object):
    def __init__(self,min,max,step=1,ndigits=2):
        self.min = min
        self.max = max
        self.step = step
        self.ndigits = ndigits
        self.current = self.min

    def getMin(self):
        return self.min

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= self.max:
            retVal = round(self.current,self.ndigits)
            self.current += self.step
            self.current = round(self.current, self.ndigits)  # Handle float inaccuracies
            return retVal
        raise StopIteration

    def __repr__(self):
        return f'grange({self.min},{self.max},{self.step})'

def lower_bars(dataclose,bars):     # true if each bar is lower than the previous
    
    res = True
    for i in range(0,bars):
        if dataclose[-i] >= dataclose[-i-1]:
            res = False
            break
    
    return res

def lower_bars_I(dataclose,bars):     # Intraday version with daily_closes list
    
    res = True
    for i in range(1,bars+1):
        if dataclose[-i] >= dataclose[-i-1]:
            res = False
            break
    
    return res
