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
		print("Name, , W, L, D, GP, Diff")
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
	print(player['name'] + ", %d, %d, %d, %d, %d, %d" % (place, player['wins'], player['losses'], player['draws'], gp, diff))

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
				p_string += str(together / mates[p][p]) + ", "
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