
class WF:

    def __init__(self):
        pass

    def printWFParams(self):
        for index, row in self.df_pack.iterrows():
            fromDate = row['fromDate']
            toDate = row['toDate']
            retStr = f"{fromDate} - {toDate}: "
            paramsSeries = row.iloc[2:]
            for ind,val in paramsSeries.items():
                retStr = retStr + f"{ind} = {val} | "
            print(retStr)

    def getWFParamsForDate(self,curDate):
        strD = str(curDate)
        query = f"'{strD}' >= fromDate and '{strD}' <= toDate"
        df_curPeriod = self.df_pack.query(query)    # Search for params for date
        if len(df_curPeriod) == 1:
            paramsSeries = df_curPeriod.iloc[0,2:]    # Starting from the third column
            retDict = {}
            for ind,val in paramsSeries.items():
                retDict[ind] = val
            return retDict
        return None

    def log(self, txt, dt=None):
        if self.do_log:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))