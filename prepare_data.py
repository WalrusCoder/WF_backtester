import pandas as pd

path_orig = 'data/SPY_first_30min.txt'
path_target = 'data/SPY_first_30min_RTH.txt'

df = pd.read_csv(path_orig,
                usecols=[0,1,2,3,4],
                names=['date','open','high','low','close'],
                index_col='date',
                parse_dates=['date'])
print("Before:")
print(df)

# Only 9:30 till 15:30
df = df[
    ((df.index.hour == 9) & (df.index.minute == 30)) | 
    ((df.index.hour >= 10) & (df.index.hour < 16))
    ]

# Take first 7000 lines
'''
n = 7000
df = df.iloc[:n]
print(f"\nFirst {n} lines")
print(df.head(50))
'''

print("After:")
print(df)

df.to_csv(path_target)
