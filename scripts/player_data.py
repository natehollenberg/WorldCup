import requests
from bs4 import BeautifulSoup
import pandas as pd

seasons = ['2015-2016', '2016-2017', '2017-2018']

squads = {}
df_full = None
squad_names = {}
country_names = {}

r = requests.get(f'https://fbref.com/en/squads/')
soup = BeautifulSoup(r.text)

table = soup.find('table')
rows = table.findAll('th', attrs={'data-stat': 'country'})
for row in rows[1:]:
    link = next(row.children).attrs['href']
    country = link.split('/')[4]
    country_name = link.split('/')[5]

    squads[country] = []
    country_names[country] = country_name

for league in squads:
    r = requests.get(f'https://fbref.com/en/squads/country/{league}')
    soup = BeautifulSoup(r.text)

    table = soup.find('table')
    rows = table.findAll('th', attrs={'data-stat': 'squad'})
    for row in rows[1:]:
        link = next(row.children).attrs['href']
        squad = link.split('/')[3]
        squad_name = link.split('/')[4]

        squads[league].append(squad)
        squad_names[squad] = squad_name

for season in seasons:
    for league in squads:
        for squad in squads[league]:
            print(squad_names[squad])
            r = requests.get(f'https://fbref.com/en/squads/{squad}/{season}')
            soup = BeautifulSoup(r.text)

            table = soup.find('table')
            if table is None:
                continue
            cols = table.find_all('tr')[1].find_all('th')
            cols = [col.text for col in cols]
            body = soup.find('table').tbody

            data = {}

            for row in body.find_all('tr'):
                for item in row.find_all('th') + row.find_all('td'):
                    stat = item.attrs['data-stat']
                    if data.get(stat):
                        data[stat].append(item.text)
                    else:
                        data[stat] = [item.text]

            df_new = pd.DataFrame(data)

            df_new['season'] = pd.Series([season for i in range(len(df_new))])
            df_new['team'] = pd.Series([squad_names[squad] for i in range(len(df_new))])
            df_new['team_id'] = pd.Series([squad for i in range(len(df_new))])
            df_new['country'] = pd.Series(league for i in range(len(df_new)))
            df_new['country_name'] = pd.Series(country_names[league] for i in range(len(df_new)))

            if df_full is None:
                df_full = df_new
            else:
                df_full = pd.concat([df_full, df_new], ignore_index=True)
df_full.to_csv('PlayerData.csv')
