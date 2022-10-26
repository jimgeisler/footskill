
import datamanager
import importutils
import constants
import output

from datetime import date

local_players = {}

def generatePlayerHistory():
	all_games = datamanager.getAllGames()

	for game in all_games:
		generatePlayerHistoryForGame(game)

def generatePlayerHistoryForGame(game):
	result = game['result']
	game_date = game['date']

	blue_players = list(map(lambda player_name: datamanager.findOrCreateNewPlayer(player_name), game['blue_team']))
	red_players = list(map(lambda player_name: datamanager.findOrCreateNewPlayer(player_name), game['red_team']))

	for player in blue_players:
		__updatePlayerRecords(player, constants.blue, result, game_date)
	for player in red_players:
		__updatePlayerRecords(player, constants.red, result, game_date)

	importutils.recordGame(blue_players, red_players, result, game_date)

def clearRecords():
	all_players = datamanager.getAllPlayers()
	for player in all_players:
		datamanager.updatePlayerRecord(player['name'], {'records': []})

def clearPlayers():
	all_players = datamanager.getAllPlayers()
	for player in all_players:
		datamanager.removePlayer(player['name'])

def __dateFromString(stringDate):
	monthdayyear = stringDate.split('/')
	return date(int(monthdayyear[2]), int(monthdayyear[0]), int(monthdayyear[1]))

def __sortFunc(e):
	return __dateFromString(e['date'])	

def __updatePlayerRecords(player, team_name, result, game_date):
	record_history = []
	if 'records' in player:
		record_history = player['records']
	latest_record = {'wins': 0, 'losses': 0, 'draws': 0, 'games_played': 0}
	if record_history != []:
		print(record_history)
		record_history.sort(key=__sortFunc)
		latest_record = record_history[-1]
		
	new_record = importutils.updateRecordStructure(latest_record, team_name, result)
	new_record['date'] = game_date

	record_history.append(new_record)
	
	datamanager.updatePlayerRecord(player['name'], {'records': record_history})


# generatePlayerHistory()
# clearPlayers()
# clearRecords()
# output.printPlayers()