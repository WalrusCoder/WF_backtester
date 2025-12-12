


'''
import datetime

# 731603.3958333334

print(round(731603.3958333334,6))

def OrdinalToDatetime(ordinal):
    plaindate = datetime.date.fromordinal(int(ordinal))
    date_time = datetime.datetime.combine(plaindate, datetime.datetime.min.time())
    date_time = date_time + datetime.timedelta(days=ordinal-int(ordinal))
    return date_time.replace(microsecond=0)

dt = OrdinalToDatetime(731603.3958333334)
print(dt)
'''
'''
import pandas as pd

df = pd.read_csv('SPY.csv',index_col='date',parse_dates=True)
df = df[['open','high','low','close']].head()
print(df)
jdf = df.to_json()
print(df.to_json())

rdf = pd.read_json(jdf)
rdf.index.name = 'date'
print(rdf)
'''