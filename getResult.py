import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from time import sleep
import csv
import re

def get_result(level,year,team_alphabet):
  # URLにパラメータをフィットさせる
  if level == 1:
    level = ""
  elif level == 2:
    level = "-farm"

  year = str(year).zfill(2)

  farm_page_url = f'https://baseball-data.com/{year}/stats{level}/hitter-{team_alphabet}/tpa-6.html'

  team_result = []

  with urllib.request.urlopen(farm_page_url) as response:
    html = response.read()
  
  soup = BeautifulSoup(html,'html.parser')
  table = soup.find('table')
  tr_list = table.find_all('tr')
  for i, tr in enumerate(tr_list):
    # 最初と最後の行は列名なので無視
    if i == 0 or i == len(tr_list) - 1:
      continue
    td_list = tr.find_all('td')
    player_farm_result = []
    player_farm_result.append(year)
    for td in td_list:
      player_farm_result.append(td.string)
    team_result.append(player_farm_result)
  sleep(1)
  return team_result

def get_after3y_result(team_farm_result,team_alphabet):
  team_after3y_result = []
  for player_farm_result in team_farm_result:
    player_after3y_result = [player_farm_result[2]]
    future_year = str(int(player_farm_result[0]) + 3)
    player_name = urllib.parse.quote_plus(player_farm_result[2], encoding='utf-8')
    player_page_url = f'https://baseball-data.com/{future_year}/player/{team_alphabet}/{player_name}'
    print(player_page_url)

    try:
      with urllib.request.urlopen(player_page_url) as response:
        html = response.read()
      soup = BeautifulSoup(html, 'html.parser')
      table = soup.find(id='tbl')

      #成績テーブルがない場合
      if table == None:
        player_after3y_result.extend(get_blank_after3y_result())
        continue
      
      td_year = table.find('td', text=re.compile('20' + future_year))

      #成績テーブルがない場合
      if td_year == None:
        player_after3y_result.extend(get_blank_after3y_result())
        continue

      tr = td_year.parent
      td_list = tr.find_all('td')
      
      for i, td in enumerate(td_list):
        if i == 2 or i == 6 or i == 9 or i == 11 or i == 20 or i == 21 or i == 22:
          player_after3y_result.append(td.string)

      print(player_after3y_result)
    except urllib.error.HTTPError as e:
      print(e.code)
      player_after3y_result.extend(get_blank_after3y_result())
    
    team_after3y_result.append(player_after3y_result)

    sleep(1)
  return team_after3y_result

#3年後のプレイヤーページが404 or 該当年の行が存在しない場合、成績を0埋めする
def get_blank_after3y_result():
  blank_after3y_result = [0] * 7
  return blank_after3y_result

def save_csv(filename,data):
  with open('./csv/' + filename, 'w') as f:
    writer = csv.writer(f, lineterminator='\n')
    writer.writerows(data)

def main():
  all_farm_result = []
  all_farm_result_header = ['西暦','背番号','選手名','2軍打率','2軍試合','2軍打席数','2軍打数','2軍安打','2軍本塁打','2軍打点','2軍盗塁','2軍四球','2軍死球','2軍三振','2軍犠打','2軍併殺打','2軍出塁率','2軍長打率','2軍OPS','2軍RC27','2軍XR27']
  all_farm_result.append(all_farm_result_header)

  all_first_team_result = []
  all_first_team_result_header = ['西暦','背番号','選手名','1軍打率','1軍試合','1軍打席数','1軍打数','1軍安打','1軍本塁打','1軍打点','1軍盗塁','1軍四球','1軍死球','1軍三振','1軍犠打','1軍併殺打','1軍出塁率','1軍長打率','1軍OPS','1軍RC27','1軍XR27']
  all_first_team_result.append(all_first_team_result_header)

  all_after3y_result = []
  all_after3y_result_header = ['選手名','3年後試合','3年後安打','3年後本塁打','3年後打点','3年後打率','3年後出塁率','3年後長打率']
  all_after3y_result.append(all_after3y_result_header)

  team_list = ['c','t','yb','g','d','s','h','l','e','bs','f','m']

  for year in range(9,15):
    for team_alphabet in team_list:
      # 2軍成績の取得
      team_farm_result = get_result(2, year, team_alphabet)
      for player_farm_result in team_farm_result:
        all_farm_result.append(player_farm_result)

      # 1軍成績の取得
      team_first_team_result = get_result(1, year, team_alphabet)
      for player_first_team_result in team_first_team_result:
        all_first_team_result.append(player_first_team_result)

      # 3年後の成績の取得
      team_after3y_result = get_after3y_result(team_farm_result,team_alphabet)
      for player_after3y_result in team_after3y_result:
        all_after3y_result.append(player_after3y_result)
  
  save_csv('farm_data.csv', all_farm_result)
  save_csv('first_team_data.csv', all_first_team_result)
  save_csv('after3y_data.csv', all_after3y_result)

if __name__ == '__main__':
  main()
