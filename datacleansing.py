import pandas as pd

# insert dataset from github
url = 'https://raw.githubusercontent.com/sabrinalaillita/fpg-strl/master/Sales.csv?token=GHSAT0AAAAAACWII4F72LQHIB6YOAIDFQ2OZWCEUYA'
df = pd.read_csv(url, index_col=0)
print(df.head(5))

df.describe(include="all")