from bs4 import BeautifulSoup
import requests
from pandas import Series
import pandas as pd

from utilities import soup_to_df, clean_missing

years = [
    1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018
]

payload = {
    'sa': 'soccer',
    'a': 'wc',
    'b': 'two',
    'o': 'r'
}

df_full = None


for y in years:
    payload['y'] = y

    r = requests.get('http://www.sportsoddshistory.com/soccer-uefa/', params=payload)
    soup = BeautifulSoup(r.text)

    df, last_i = soup_to_df(soup)

    df.to_csv(f'data/odds_{y}.csv')

    col_last = df.columns[last_i]
    df_clean = df[['Team', col_last]]
    df_clean['year'] = Series([y for i in range(len(df_clean))])

    df_clean = df_clean.rename(
        columns={
            col_last: 'final_line',
            'Team': 'team',
        }
    )

    if df_full is None:
        df_full = df_clean
    else:
        df_full = pd.concat([df_full, df_clean], ignore_index=True)

df_full = clean_missing(df_full)
df_full.to_csv('data/odds_full.csv')
