import datamanager
import constants

from datetime import date

from trueskill import Rating
from trueskill import quality
from trueskill import BETA
from trueskill import SIGMA
from trueskill import MU
import trueskill
import itertools
import math

import scipy.stats as stats

# Prints the game data
def printGames():
	chance_of_draw = []
	games = datamanager.getAllGames()
	for game in games:
		if game['result'] == constants.balanced:
			print(game['date'] + " : draw")
		elif game['result'] == constants.blue:
			print(game['date'] + " : blue team wins")
		elif game['result'] == constants.red:
			print(game['date'] + " : red team wins")
		else:
			print(game['date'] + " : no result")
			continue

		blue_team_ratings = []
		red_team_ratings = []
		blue_players = ""
		for player_name in game['blue_team']:
			blue_players += player_name + " "
			player = findOrCreateNewPlayer(player_name)
			blue_team_ratings.append(player)
		red_players = ""
		for player_name in game['red_team']:
			red_players += player_name + " "
			player = findOrCreateNewPlayer(player_name)
			red_team_ratings.append(player)

		if len(game['blue_team']) > len(game['red_team']):
			player_name = "goalie"
			red_players += player_name + " "
			player = findOrCreateNewPlayer(player_name)
			red_team_ratings.append(player)
		elif len(game['red_team']) > len(game['blue_team']):
			player_name = "goalie"
			blue_players += player_name + " "
			player = findOrCreateNewPlayer(player_name)
			blue_team_ratings.append(player)

		print("Blue team: " + blue_players)
		print("Red team: " + red_players)

		quality = rateTheseTeams(blue_team_ratings, red_team_ratings)
		print("Chance Blue beats Red:")
		blue_beat_red = win_probability(blue_team_ratings, red_team_ratings)
		print(win_probability(blue_team_ratings, red_team_ratings))
		print("Chance Red beats Blue:")
		print(win_probability(red_team_ratings, blue_team_ratings))
		red_beat_blue = win_probability(red_team_ratings, blue_team_ratings)
		print("Chance of a draw:")
		print(quality)

		correct = 0
		if game['result'] == constants.balanced:
			correct = 1
		elif blue_beat_red > red_beat_blue and game['result'] == constants.blue:
			correct = 1
		elif blue_beat_red < red_beat_blue and game['result'] == constants.red:
			correct = 1

		chance_of_draw.append([quality, len(blue_team_ratings) + len(red_team_ratings), str(correct)])

		generatePlayerHistoryForGame(game)

	# print("Chance of draw per game: ")
	# print("Chance, Number of players, Outcome Predicted")
	# for info in chance_of_draw:
	# 	print(str(info[0]) + ", " + str(info[1]) + ", " + info[2])

def win_probability(team1, team2):
    delta_mu = sum(r['mu'] for r in team1) - sum(r['mu'] for r in team2)
    sum_sigma = sum(r['sigma'] ** 2 for r in itertools.chain(team1, team2))
    size = len(team1) + len(team2)
    denom = math.sqrt(size * (BETA * BETA) + sum_sigma)
    ts = trueskill.global_env()
    return ts.cdf(delta_mu / denom)

def _playerNameSorter(elem):
	return elem['name']

def printAllPlayers():
	players = datamanager.getAllPlayers()

	players.sort(key=_playerNameSorter)

	for player in players:
		print(player['name'])


# Prints the players ranked highest to lowest rating
def printLeaderBoard(type):

	games = datamanager.getAllGames()
	last_game = games[-1]
	last_date = __dateFromString(last_game['date'])
	before_last_game = games[-2]
	before_last_date = __dateFromString(before_last_game['date'])

	print("Leaderboard:")
	if type == 'csv':
		print("Name, , W, L, D, GP, Diff, Rank")
	elif type == 'mu':
		print("Name, Rank, Rating, GP")

	players = datamanager.getLeaderboard(before_last_date)
	placements = {}
	for index, player in enumerate(players):
		placements[player['name']] = index + 1

	players = datamanager.getLeaderboard(last_date)
	for index, player in enumerate(players):
		if type == 'csv':
			printPlayerCSVFormat(player, index + 1, placements[player['name']])
		elif type == 'mu':
			print(player['name'] + ", %d, %f, %d" % (index + 1, constants.env.expose(Rating(mu=player['mu'], sigma=player['sigma'])), player['games_played']))
		else:
			printPlayerCommandLine(player)	

def getPlayerPositions():
	players1 = datamanager.getLeaderboard(1)
	players2 = datamanager.getLeaderboard(2)
	placement_by_name = {}
	for index, player in enumerate(players1):
		placement_by_name[player['name']] = index

	for index, player in enumerate(players2):
		placement_by_name[player['name']] = index - placement_by_name[player['name']]

	print(placement_by_name)

		
				
def printPlayerCommandLine(player):
	gp = player['wins'] + player['losses'] + player['draws']
	print(player['name'] + ": (%d, %d, %d) / %d" % (player['wins'], player['losses'], player['draws'], gp))

def printPlayerCSVFormat(player, place, prev_game_rank):
	gp = player['wins'] + player['losses'] + player['draws']
	diff = prev_game_rank - place
	rank = player['mu'] - 3 * player['sigma']
	print(player['name'] + ", %d, %d, %d, %d, %d, %d, %d" % (place, player['wins'], player['losses'], player['draws'], gp, diff, rank))

# Generates the fairest possible teams from list of player names
# Outputs the teams and the chance of a draw
def printFairestTeams(player_names):
	print("Name,Team")
	total_players = len(player_names)
	first_team_size = round(total_players / 2)

	# print("Total combinations " + str(len(first_team_combos)))
	generatedTeams = datamanager.generateTeamsWithPlayers(player_names)
	redTeam = generatedTeams["redTeam"]
	blueTeam = generatedTeams["blueTeam"]
	quality = generatedTeams["quality"]

	for player in blueTeam:
		print(player['name'] + ",Blue")
	for player in redTeam:
		print(player['name'] + ",Red")
	print("Quality: ")
	print(quality)

def __dateFromString(stringDate):
	monthdayyear = stringDate.split('/')
	return date(int(monthdayyear[2]), int(monthdayyear[0]), int(monthdayyear[1]))

def __sortFunc(e):
	return __dateFromString(e['date'])	

def printPlayerDistribution(names):
	players = datamanager.getPlayers(names)
	player_ratings = {}
	for player in players:
		ratings = player['ratings']
		ratings.sort(key=__sortFunc)
		rating = ratings[-1]
		mu = rating['mu']
		sigma = rating['sigma']
		player_ratings[player['name']] = {'mu': mu, 'sigma':sigma}

	for n in range(75):
		values_to_print = ""
		first_line = ""
		for player in players:
			player_name = player['name']
			first_line += player_name + ", "
			rating = player_ratings[player_name]
			values_to_print += "%.4f" % (stats.norm.pdf(n, rating['mu'], rating['sigma'])) + ", "
		if n ==0:
			print(first_line[:-2])
		print(values_to_print[:-2])


###########

tempAllPlayers = []

def findOrCreateNewPlayer(player_name):
	players = list(filter(lambda p: p['name'] == player_name, tempAllPlayers))
	player = newPlayerStructure(player_name)
	if len(players) > 0:
		player = players[0]
	else:
		tempAllPlayers.append(player)
	return player

def newPlayerStructure(name):
	new_player = {}
	new_player['name'] = name
	new_player['games_played'] = 0
	new_player['wins'] = 0
	new_player['losses'] = 0
	new_player['draws'] = 0

	# Rating is represented by mu and sigma
	rating = Rating()
	new_player['mu'] = rating.mu
	new_player['sigma'] = rating.sigma

	# Historical data - starting record and rating
	new_player['records'] = []
	new_player['ratings'] = []	
	return new_player

def updatePlayerRecord(name, record_history):
	players = list(filter(lambda p: p['name'] == name, tempAllPlayers))
	player = players[0]
	player['records'] = record_history

def updatePlayerRecords(player, team_name, result, game_date):
	record_history = []
	if 'records' in player:
		record_history = player['records']
	latest_record = {'wins': 0, 'losses': 0, 'draws': 0, 'games_played': 0}
	if record_history != []:
		record_history.sort(key=__sortFunc)
		latest_record = record_history[-1]
		
	new_record = updateRecordStructure(latest_record, team_name, result)
	new_record['date'] = game_date

	record_history.append(new_record)
	
	updatePlayerRecord(player['name'], record_history)

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

def printFairestTeamsWithGoalies(player_names):
	games = datamanager.getAllGames()
	for game in games:
		if game['result'] in ['Red', 'Blue', 'Balanced']:
			generatePlayerHistoryForGame(game)

	generateTeamsWithPlayers(player_names)
	print(" -=-= First Best =-=- ")
	print("Name,Team")
	total_players = len(player_names)

	generatedTeams = generateTeamsWithPlayers(player_names)
	redTeam = generatedTeams["redTeam"]
	blueTeam = generatedTeams["blueTeam"]
	quality = generatedTeams["quality"]

	secondBestRedTeam = generatedTeams["secondBestRed"]
	secondBestBlueTeam = generatedTeams["secondBestBlue"]
	secondBestQuality = generatedTeams["secondBestQuality"]

	for player in blueTeam:
		print(player['name'] + ",Blue")
	for player in redTeam:
		print(player['name'] + ",Red")
	print("Quality: ")
	print(quality)

	print(" -=-= Second Best =-=- ")
	print("Name,Team")
	for player in secondBestBlueTeam:
		print(player['name'] + ",Blue")
	for player in secondBestRedTeam:
		print(player['name'] + ",Red")
	print("Quality: ")
	print(secondBestQuality)

def getPlayers(player_names):
	today_players = []
	for name in player_names:
		players = list(filter(lambda p: p['name'] == name, tempAllPlayers))
		if len(players) == 0:
			new_p = findOrCreateNewPlayer(name)
			today_players.append(new_p)
			tempAllPlayers.append(new_p)
		else:
			today_players.append(players[0])
	return today_players

def generateTeamsWithPlayers(player_names):
	names = player_names.split(', ')
	if (len(names) % 2) != 0:
		names.append("goalie")
	players = getPlayers(names)

	total_players = len(players)
	first_team_size = round(total_players / 2)
	first_team_combos = list(itertools.combinations(players, first_team_size))

	bestTeams = []
	bestQuality = 0
	secondBestQuality = 0
	secondBestTeams = []
	for first_team in first_team_combos:
		second_team = players.copy()
		for player in first_team:
			second_team.remove(player)
		quality = rateTheseTeams(first_team, second_team)
		if quality > bestQuality:
			secondBestTeams = bestTeams
			secondBestQuality = bestQuality
			bestTeams = [first_team, second_team]
			bestQuality = quality

	return {
		"redTeam": bestTeams[0],
		"blueTeam": bestTeams[1],
		"quality": bestQuality,
		"secondBestRed": secondBestTeams[0],
		"secondBestBlue": secondBestTeams[1],
		"secondBestQuality": secondBestQuality
	}	

def rateTheseTeams(first_team, second_team):
	team1_ratings = list(map(lambda player: Rating(mu=player['mu'], sigma=player['sigma']), first_team))
	team2_ratings = list(map(lambda player: Rating(mu=player['mu'], sigma=player['sigma']), second_team))
	return quality([team1_ratings, team2_ratings])	

def printLeaderBoardWithGoalies():
	print("With Goalies")
	games = datamanager.getAllGames()
	for game in games:
		if game['result'] in ['Red', 'Blue', 'Balanced']:
			generatePlayerHistoryForGame(game)
	print("Name, W, L, D, GP, PPG, Win %, Rank")
	csp = ', '
	for player in getLeaderboard():
		record = player['records'][-1]
		tempOutput = player['name'] + csp
		tempOutput += str(record['wins']) + csp
		tempOutput += str(record['losses']) + csp
		tempOutput += str(record['draws']) + csp
		tempOutput += str(record['games_played']) + csp
		tempOutput += str((record['wins'] * 3 + record['draws']) / record['games_played']) + csp
		tempOutput += str(record['wins'] / record['games_played']) + csp
		tempOutput += str(player['mu'] - 3 * player['sigma'])
		
		print(tempOutput)

def getLeaderboard():
	ratings = []
	players = tempAllPlayers

	for p in players:
		ratings.append(Rating(mu=p['mu'], sigma=p['sigma']))
	leaderboard = sorted(ratings, key=constants.env.expose, reverse=True)

	returnPlayerList = []
	for index, leader in enumerate(leaderboard):
		for player in players:
			rating = Rating(mu=player['mu'], sigma=player['sigma'])
			if leader == rating and not listHasPlayerByName(returnPlayerList, player['name']):
				returnPlayerList.append(player)
	return returnPlayerList

def listHasPlayerByName(players, player_name):
	for player in players:
		if player['name'] == player_name:
			return True
	return False

def generatePlayerHistoryForGame(game):
	result = game['result']
	game_date = game['date']

	blue_players = list(map(lambda player_name: findOrCreateNewPlayer(player_name), game['blue_team']))
	red_players = list(map(lambda player_name: findOrCreateNewPlayer(player_name), game['red_team']))

	if len(blue_players) > len(red_players):
		red_players.append(findOrCreateNewPlayer("goalie"))
	elif len(red_players) > len(blue_players):
		blue_players.append(findOrCreateNewPlayer("goalie"))

	if len(blue_players) > len(red_players):
		print("ISSUES")
	elif len(red_players) > len(blue_players):
		print("ISSUES")

	for player in blue_players:
		updatePlayerRecords(player, constants.blue, result, game_date)
	for player in red_players:
		updatePlayerRecords(player, constants.red, result, game_date)

	recordGame(blue_players, red_players, result, game_date)


def updatePlayerRating(name, rating):
	players = list(filter(lambda p: p['name'] == name, tempAllPlayers))
	player = players[0]
	player['mu'] = rating.mu
	player['sigma'] = rating.sigma

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
		updatePlayerRating(player_name, new_rating)
	for player_name in red_team_updated_ratings:
		new_rating = red_team_updated_ratings[player_name]
		updatePlayerRating(player_name, new_rating)


###########

def printLast10games():
	print('last 10 games')
	num = 10
	count = 0
	games = datamanager.getAllGames()
	backward_games = sorted( enumerate(games), reverse=True )
	players = {}
	for (number, game) in backward_games:
		for player in game['blue_team']:
			if player in players:
				players[player] = players[player] + 1
			else:
				players[player] = 1
		for player in game['red_team']:
			if player in players:
				players[player] = players[player] + 1
			else:
				players[player] = 1
		count += 1
		if count == num:
			break
	print("Name, Games")
	for p in players.keys():
		print(p + ", " + str(players[p])) 

###########

def printPlayerDetails(name):
	player = datamanager.getPlayer(name)
	games = datamanager.getAllGames()
	for game in games:
		team = None
		if name in game['blue_team']:
			team = constants.blue
		elif name in game['red_team']:
			team = constants.red

		if team == None:
			continue

		print("Played in game " + game['date'])
		result = game['result']
		if result == constants.balanced:
			print("Draw")
		elif result == team:
			print("Win")
		else:
			print("Loss")

		records = player['records']
		for record in records:
			if record['date'] == game['date']:
				gp = record['wins'] + record['losses'] + record['draws']
				print("(%d, %d, %d) | %d" % (record['wins'], record['losses'], record['draws'], gp))


def gamesTogetherDict(mates, all_players):
	for player_name in all_players:
		mate_entry = {}
		if player_name in mates:
			mate_entry = mates[player_name]
		for teammate_name in all_players:
			player_entry = 1
			if teammate_name in mate_entry:
				player_entry = mate_entry[teammate_name] + 1
			mate_entry[teammate_name] = player_entry
		mates[player_name] = mate_entry
	return mates

def printTeammatesPercentageWhenBothAttend():
	mates = {}
	teammates = {}

	games = datamanager.getAllGames()
	for game in games:
		all_players = game['blue_team'] + game['red_team']
		mates = gamesTogetherDict(mates, all_players)
		teammates = gamesTogetherDict(teammates, game['blue_team'])
		teammates = gamesTogetherDict(teammates, game['red_team'])

	p_string = " , "
	for p in mates:
		p_string += p + ", "
	print(p_string)

	for p in mates:
		p_string = p + ", "
		for q in mates:
			if q in mates[p]:
				together = 0
				if q in teammates[p]:
					together = teammates[p][q]
				p_string += str(together / mates[p][q]) + ", "
			else:
				p_string += "0, "
		print(p_string)

def printUnevenGames():
	games = datamanager.getAllGames()

	print("Blue Players,Red Players,Winner,Fake Goalie Victory")

	for game in games:
		blue_players = game['blue_team']
		red_players = game['red_team']

		bpn = len(blue_players)
		rpn = len(red_players)

		result = game['result']
		condition = "yes"
		if bpn > rpn and result == 'Blue':
			condition = "no"
		elif rpn > bpn and result == 'Red':
			condition = "no"

		if (bpn > rpn or rpn > bpn) and result != "":
			print(str(bpn) + "," + str(rpn) + "," + result + "," + condition)


def printTeammates():
	mates = {}
	teammates = {}

	games = datamanager.getAllGames()
	for game in games:
		all_players = game['blue_team'] + game['red_team']
		mates = gamesTogetherDict(mates, all_players)
		teammates = gamesTogetherDict(teammates, game['blue_team'])
		teammates = gamesTogetherDict(teammates, game['red_team'])

	p_string = " , "
	for p in mates:
		p_string += p + ", "
	print(p_string)

	for p in mates:
		p_string = p + ", "
		for q in mates:
			if q in mates[p]:
				together = 0
				if q in teammates[p]:
					together = teammates[p][q]
				# p_string += str(together / mates[p][p]) + ", "
				p_string += str(together) + ", "
			else:
				p_string += "0, "
		print(p_string)


def printPlayers():
	players = datamanager.getAllPlayers()
	for player in players:
		print(player['name'])
		records = player['records']
		records.sort(key=__sortFunc)
		print(records[-1])
		ratings = player['ratings']
		ratings.sort(key=__sortFunc)
		print(ratings[-1])