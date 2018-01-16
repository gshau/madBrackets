import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
import warnings
warnings.filterwarnings('ignore')

head_names = ['School', 'W-L%', 'SRS', 'SOS', 'TmPts', 'OppPts', 
              'Pace', 'ORtg', 'FTr', '3PAr', 'TS%', 'TRB%', 'AST%', 
              'STL%', 'BLK%', 'eFG%', 'TOV%', 'ORB%', 'FT/FGA']

def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


years = ['2017', '2016', '2015', '2014', '2013', '2012', '2011', '2010']

for year in years:

	print("Compiling the data for " + year)

	url = "http://www.sports-reference.com/cbb/seasons/"+year+"-advanced-school-stats.html"
	r = requests.get(url)
	data = r.text
	soup = BeautifulSoup(data, "html5lib")

	team_names = soup.findAll("td", {"data-stat": "school_name"})
	team_names = [node.getText().encode('latin-1') for node in team_names]
	team_names = [node.lower().replace(" *", "").replace(" ", "-") for node in team_names]

	team_WLpct = soup.findAll("td", {"data-stat": "win_loss_pct"})
	team_WLpct = [node.getText().encode('latin-1') for node in team_WLpct]
	team_WLpct = [num(stat) for stat in team_WLpct]

	team_srs = soup.findAll("td", {"data-stat": "srs"})
	team_srs = [node.getText().encode('latin-1') for node in team_srs]
	team_srs = [num(stat) for stat in team_srs]

	team_sos = soup.findAll("td", {"data-stat": "sos"})
	team_sos = [node.getText().encode('latin-1') for node in team_sos]
	team_sos = [num(stat) for stat in team_sos]

	team_TmPts = soup.findAll("td", {"data-stat": "pts"})
	team_TmPts = [node.getText().encode('latin-1') for node in team_TmPts]
	team_TmPts = [num(stat) for stat in team_TmPts]

	team_OppPts = soup.findAll("td", {"data-stat": "opp_pts"})
	team_OppPts = [node.getText().encode('latin-1') for node in team_OppPts]
	team_OppPts = [num(stat) for stat in team_OppPts]

	team_pace = soup.findAll("td", {"data-stat": "pace"})
	team_pace = [node.getText().encode('latin-1') for node in team_pace]
	team_pace = [num(stat) for stat in team_pace]

	team_ORtg = soup.findAll("td", {"data-stat": "off_rtg"})
	team_ORtg = [node.getText().encode('latin-1') for node in team_ORtg]
	team_ORtg = [num(stat) for stat in team_ORtg]

	team_FTr = soup.findAll("td", {"data-stat": "fta_per_fga_pct"})
	team_FTr = [node.getText().encode('latin-1') for node in team_FTr]
	team_FTr = [num(stat) for stat in team_FTr]

	team_3Ar = soup.findAll("td", {"data-stat": "fg3a_per_fga_pct"})
	team_3Ar = [node.getText().encode('latin-1') for node in team_3Ar]
	team_3Ar = [num(stat) for stat in team_3Ar]

	team_TSpct = soup.findAll("td", {"data-stat": "ts_pct"})
	team_TSpct = [node.getText().encode('latin-1') for node in team_TSpct]
	team_TSpct = [num(stat) for stat in team_TSpct]

	team_TRBpct = soup.findAll("td", {"data-stat": "trb_pct"})
	team_TRBpct = [node.getText().encode('latin-1') for node in team_TRBpct]
	team_TRBpct = [num(stat) for stat in team_TRBpct]

	team_ASTpct = soup.findAll("td", {"data-stat": "ast_pct"})
	team_ASTpct = [node.getText().encode('latin-1') for node in team_ASTpct]
	team_ASTpct = [num(stat) for stat in team_ASTpct]

	team_STLpct = soup.findAll("td", {"data-stat": "stl_pct"})
	team_STLpct = [node.getText().encode('latin-1') for node in team_STLpct]
	team_STLpct = [num(stat) for stat in team_STLpct]

	team_BLKpct = soup.findAll("td", {"data-stat": "blk_pct"})
	team_BLKpct = [node.getText().encode('latin-1') for node in team_BLKpct]
	team_BLKpct = [num(stat) for stat in team_BLKpct]

	team_eFGpct = soup.findAll("td", {"data-stat": "efg_pct"})
	team_eFGpct = [node.getText().encode('latin-1') for node in team_eFGpct]
	team_eFGpct = [num(stat) for stat in team_eFGpct]

	team_TOVpct = soup.findAll("td", {"data-stat": "tov_pct"})
	team_TOVpct = [node.getText().encode('latin-1') for node in team_TOVpct]
	team_TOVpct = [num(stat) for stat in team_TOVpct]

	team_ORBpct = soup.findAll("td", {"data-stat": "orb_pct"})
	team_ORBpct = [node.getText().encode('latin-1') for node in team_ORBpct]
	team_ORBpct = [num(stat) for stat in team_ORBpct]

	team_FTr = soup.findAll("td", {"data-stat": "ft_rate"})
	team_FTr = [node.getText().encode('latin-1') for node in team_FTr]
	team_FTr = [num(stat) for stat in team_FTr]

	stats_list = [team_names, team_WLpct, team_srs, team_sos, team_TmPts,
             team_OppPts, team_pace, team_ORtg, team_FTr, team_3Ar,
             team_TSpct, team_TRBpct, team_ASTpct, team_STLpct, 
             team_BLKpct, team_eFGpct, team_TOVpct, team_ORBpct, 
             team_FTr]

	team_dict = {}
	for i, head in enumerate(head_names):
	    team_dict[head] = stats_list[i]
	        
	team_data = pd.DataFrame(team_dict)

	team_data = team_data[head_names]

	team_data.to_csv("team_stats_"+year+".csv", index=False)

	# get results of all games
	all_games = []
	for team in team_names:
	    team = team.lower().replace(" ", "-")
	    url = "http://www.sports-reference.com/cbb/schools/"+team+"/"+year+"-schedule.html"
	    r = requests.get(url)
	    data = r.text
	    soup = BeautifulSoup(data, "html5lib")
	    
	    # opponent names
	    opp_names = soup.findAll("td", {"data-stat": "opp_name"})
	    opp_names = [node.getText().lower().replace(" ", "-") for node in opp_names]
	    
	    # result of game
	    game_result = soup.findAll("td", {"data-stat": "game_result"})
	    game_result = [node.getText() for node in game_result]
	    game_result = [0 if node == 'W' else 1 for node in game_result]
	    
	    for opp, result in zip(opp_names, game_result):
	        if opp in team_names:
	            all_games.append((team, opp, result))


	game_result_df = pd.DataFrame()
	for game in all_games:
	    team_one = team_data[team_data['School'] == game[0]]
	    team_one.reset_index(inplace=True, drop=True)
	    team_one.drop('School', axis=1, inplace=True)
	    team_two = team_data[team_data['School'] == game[1]]
	    team_two.reset_index(inplace=True, drop=True)
	    team_two.drop('School', axis=1, inplace=True)
	    game_data = pd.merge(team_one, team_two, left_index=True, right_index=True)
	    game_data['winner'] = game[2]
	    game_result_df = game_result_df.append(game_data)
	    
	game_result_df.to_csv("all_games_" + year + ".csv")

