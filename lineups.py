from bs4 import BeautifulSoup
from selenium import webdriver
import re
import random
import requests
import pandas as pd
import time
path_to_extension = '../Desktop/3.35.0_0'
chrome_options = webdriver.chrome.options.Options()
chrome_options.add_argument('load-extension=' + path_to_extension)
browser = webdriver.Chrome(executable_path=r'./chromedriver', chrome_options=chrome_options)
browser.create_options()

UAS = ("Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
       "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0",
       "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
       "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
       )

ua = UAS[random.randrange(len(UAS))]

headers = {'user-agent': ua}

seasons = ['2017-2018']
leagues = ['FA_Premier_League', 'La_Liga', 'Ligue_1']
games = {
    'game_ids': [],
    'league': [],
    'season': []
}
for league in leagues:
    for season in seasons:
        r = requests.get(f'https://www.football-lineups.com/tourn/{league}_{season}/fixture/', headers=headers)
        soup = BeautifulSoup(r.text)

        game_list = list(filter(lambda x: x.attrs.get('id') and x.attrs['id'].startswith('trfil'), soup.find_all('tr')))
        for game in game_list:
            links = game.find_all('a')
            link = list(filter(lambda x: x.attrs.get('href') and x.attrs['href'].startswith('/match/'), links))[0]
            link = link.attrs['href']
            games['game_ids'].append(link.split('/')[2])
            games['season'].append(season)
            games['league'].append(league)


data = {
    'home': [],
    'away': [],
    'league': [],
    'game_id': [],
    'season': [],
    'temp': [],
    'weather_desc': [],
    'date': []
}

players = {
    'name': [],
    'position': [],
    'team': [],
    'game_id': [],
    'player_id': []
}

form_data = {
    'goals_for': [],
    'goals_against': [],
    'team': [],
    'game_id': [],
    'date': []
}
fail_count = 0
i = 0
while i < len(games['game_ids']):
    if fail_count >= 3:
        time.sleep(120)
    browser.get(f'http://www.football-lineups.com/match/{games["game_ids"][i]}/')

    innerHTML = browser.execute_script("return document.body.innerHTML")
    soup = BeautifulSoup(innerHTML)

    try:
        teams = soup.find('tr', attrs={'itemprop': 'name'}).find_all('b')
        data['home'].append(teams[0].text)
        data['away'].append(teams[1].text)
        data['game_id'].append(i)
        data['league'].append(games['league'][i])
        data['season'].append(games['season'][i])
        date_list = []
        for link in soup.find_all('a'):
            if link.has_attr('href') and link.attrs['href'].startswith('/date'):
                date_list.append(link.text)
        data['date'].append(date_list[1])

        weather_info = soup.find_all('table', attrs={'width': 650})[0].text.split(' ')
        data['temp'].append(weather_info[-1])
        data['weather_desc'].append(weather_info[-2])

        form_raw = soup.find('span', attrs={'id': 'spsecbm'}).find('table').find_all('table')
        team_1_form, team_2_form = form_raw[0], form_raw[1]
        form_games = [team_1_form.find_all('tr')[1:], team_2_form.find_all('tr')[1:]]
        for j in range(len(form_games)):
            for game in form_games[j][1:]:
                info = game.find_all('td')
                form_data['game_id'].append(i)
                form_data['team'].append(teams[j].text)
                res = info[4].text.split('-')
                form_data['date'].append(info[0].text)
                if not info[1].text:
                    form_data['goals_for'].append(res[0])
                    form_data['goals_against'].append(res[1])
                else:
                    form_data['goals_for'].append(res[0])
                    form_data['goals_against'].append(res[1])

        divs = soup.find('span', attrs={'id': f'mt{games["game_ids"][i]}'}).find_all('div')
        player_list = list(filter(lambda x: x.find_all('a'), divs))
        for player in player_list[1:]:
            if not bool(re.match(r'\w*s\d+', player.attrs['id'])):
                if player.attrs['id'].startswith('g8m'):
                    players['team'].append(teams[0].text)
                else:
                    players['team'].append(teams[1].text)
                player_info = player.find('a')
                players['name'].append(player_info.attrs['title'])
                players['position'].append(player_info.attrs['class'][0].strip('ns'))
                players['player_id'].append(player_info.attrs['href'].split('/')[-2])
                players['game_id'].append(i)
        i += 1
        fail_count = 0
    except AttributeError:
        fail_count += 1
        browser.quit()
        browser = webdriver.Chrome(executable_path=r'./chromedriver', chrome_options=chrome_options)
        browser.create_options()
        continue

pd.DataFrame(players).to_csv('lineup_data/players_10.csv')
pd.DataFrame(form_data).to_csv('lineup_data/form_data_10.csv')
pd.DataFrame(data).to_csv('lineup_data/data_10.csv')
