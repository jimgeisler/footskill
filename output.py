import datamanager
import constants

from datetime import date

from trueskill import Rating
from trueskill import quality
import itertools

import scipy.stats as stats

# Prints the game data
def printGames():
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
		blue_players = ""
		for player_name in game['blue_team']:
			blue_players += player_name + " "
		red_players = ""
		for player_name in game['red_team']:
			red_players += player_name + " "
		print("Blue team: " + blue_players)
		print("Red team: " + red_players)
		print()

# Prints the players ranked highest to lowest rating
def printLeaderBoard(type):
	print("Leaderboard:")
	if type == 'csv':
		print("Name, , W, L, D, GP")
	elif type == 'mu':
		print("Name, Rank, Rating, GP")

	players = datamanager.getLeaderboard()
	for index, player in enumerate(players):
		if type == 'csv':
			printPlayerCSVFormat(player, index + 1)
		elif type == 'mu':
			print(player['name'] + ", %d, %f, %d" % (index + 1, constants.env.expose(Rating(mu=player['mu'], sigma=player['sigma'])), player['games_played']))
		else:
			printPlayerCommandLine(player)
				
def printPlayerCommandLine(player):
	print(player['name'] + ": (%d, %d, %d) / %d" % (player['wins'], player['losses'], player['draws'], player['games_played']))

def printPlayerCSVFormat(player, place):
	print(player['name'] + ", %d, %d, %d, %d, %d" % (place, player['wins'], player['losses'], player['draws'], player['games_played']))

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
	# print("Quality: ")
	# print(bestQuality)

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