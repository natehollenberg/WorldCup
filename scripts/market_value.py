import pandas as pd

mv = pd.read_csv('help_data/market_value.csv')
game_data = pd.read_csv('test_data_raw/game_data.csv',index_col=0)

mv['value'] = mv['value'].apply(lambda x: x.replace(',', '')).astype(float)
mv['value'] = mv['value'] * 10**6

mv_home = mv.rename(columns={'Country': 'home', 'value': 'home_market_value'})
mv_away = mv.rename(columns={'Country': 'away', 'value': 'away_market_value'})


game_data.merge(mv, )
