import datamanager
import constants

import json

from trueskill import Rating
from trueskill import quality

def normalizeName(name):
	if name == 'Chris':
		return 'Chris S.'
	else:
		return name

def processFile():
	with open('./Soccer_Teams.json', 'r') as f:
	  data = json.load(f)

	sheets = data['Sheets']

	historical_data_sheet = None
	skip = '$ per player'

	for sheet in sheets:
		if sheet['Name'] == "Sheet 2":
			historical_data_sheet = sheet
			break

	tables = sheet['Tables']
	
	total_games = 0

	for table in tables:
		name = table['Name']
		records = table['Records']
		total_games += 1
		blue_team = []
		blue_team_names = []
		red_team = []
		red_team_names = []
		game_name_split = name.split()
		result = game_name_split[-1]	
		for record in records:
			player_name = normalizeName(record['Name'])
			team_name = record['TEAM']
			if player_name != skip:
			# 	player = findOrCreateNewPlayer(player_name)
			# 	__recordRecords(player, team_name, result)
				if team_name == blue:
					# blue_team.append(player)
					blue_team_names.append(player_name)
				else:
					# red_team.append(player)
					red_team_names.append(player_name)

		#recordGame(blue_team, red_team, result)
		datamanager.createNewGame(game_name_split[0], blue_team_names, red_team_names, result)

def updateRecordStructure(record, team_name, result):
	record_updates = record
	record_updates['games_played'] = int(record['games_played']) + 1
	if team_name == constants.blue:
		if result == constants.blue:
			record_updates['wins'] = int(record['wins']) + 1
		elif result == constants.red:
			record_updates['losses'] = int(record['losses']) + 1
		elif result == constants.balanced:
			record_updates['draws'] = int(record['draws']) + 1
	elif team_name == constants.red:
		if result == constants.red:
			record_updates['wins'] = int(record['wins']) + 1
		elif result == constants.blue:
			record_updates['losses'] = int(record['losses']) + 1
		elif result == constants.balanced:
			record_updates['draws'] = int(record['draws']) + 1	
	return record_updates

def __recordRecords(player, team_name, result):
	record_updates = updateRecordStructure(player, team_name, result)
	updatePlayerRecord(player['name'], record_updates)

def recordGame(blue_team, red_team, result, game_date):
	blue_team_ratings = {}
	red_team_ratings = {}
	for p in blue_team:
		blue_team_ratings[p['name']] = Rating(mu=p['mu'], sigma=p['sigma'])
	for p in red_team:
		red_team_ratings[p['name']] = Rating(mu=p['mu'], sigma=p['sigma'])
	if result == constants.balanced:
		updated_ratings = constants.env.rate([blue_team_ratings, red_team_ratings], ranks=[0,0])
	elif result == constants.blue:
		updated_ratings = constants.env.rate([blue_team_ratings, red_team_ratings], ranks=[0,1])
	elif result == constants.red:
		updated_ratings = constants.env.rate([blue_team_ratings, red_team_ratings], ranks=[1,0])
	else:
		return

	blue_team_updated_ratings = updated_ratings[0]
	red_team_updated_ratings = updated_ratings[1]
	for player_name in blue_team_updated_ratings:
		new_rating = blue_team_updated_ratings[player_name]
		datamanager.updatePlayerRating(player_name, new_rating)
		player = datamanager.findOrCreateNewPlayer(player_name)
		ratings_history = player['ratings']
		ratings_history.append({'mu': new_rating.mu, 'sigma': new_rating.sigma, 'date': game_date})
		datamanager.updatePlayerHistoricalRecordAndRating(player_name, {'ratings': ratings_history})
	for player_name in red_team_updated_ratings:
		new_rating = red_team_updated_ratings[player_name]
		datamanager.updatePlayerRating(player_name, new_rating)
		player = datamanager.findOrCreateNewPlayer(player_name)
		ratings_history = player['ratings']
		ratings_history.append({'mu': new_rating.mu, 'sigma': new_rating.sigma, 'date': game_date})
		datamanager.updatePlayerHistoricalRecordAndRating(player_name, {'ratings': ratings_history})