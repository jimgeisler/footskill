import datamanager
import constants

from datetime import date

from trueskill import Rating
from trueskill import quality
import itertools

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
	ratings = []
	players = datamanager.getAllPlayers()
	for p in players:
		pratings = p['ratings']
		pratings.sort(key=__sortFunc)
		rating = pratings[-1]
		ratings.append(Rating(mu=rating['mu'], sigma=rating['sigma']))
	leaderboard = sorted(ratings, key=constants.env.expose, reverse=True)

	for index, leader in enumerate(leaderboard):
		for player in players:
			ratings = player['ratings']
			ratings.sort(key=__sortFunc)
			latest_rating = ratings[-1]
			rating = Rating(mu=latest_rating['mu'], sigma=latest_rating['sigma'])
			if leader == rating:
				records = player['records']
				records.sort(key=__sortFunc)
				record = records[-1]
				if type == 'csv':
					printPlayerCSVFormat(player['name'], index + 1, record)
				else:
					printPlayerCommandLine(player['name'], record)
				
def printPlayerCommandLine(name, record):
	print(name + ": (%d, %d, %d) / %d" % (record['wins'], record['losses'], record['draws'], record['games_played']))

def printPlayerCSVFormat(name, place, record):
	print(name + ", %d, %d, %d, %d, %d" % (place, record['wins'], record['losses'], record['draws'], record['games_played']))

# Generates the fairest possible teams from list of player names
# Outputs the teams and the chance of a draw
def printFairestTeams(player_names):
	print("generating teams")
	players = datamanager.getPlayers(player_names)
	total_players = len(players)
	first_team_size = round(total_players / 2)
	first_team_combos = list(itertools.combinations(players, first_team_size))

	bestTeams = []
	bestQuality = 0
	print("Total combinations " + str(len(first_team_combos)))
	for first_team in first_team_combos:
		second_team = players.copy()
		for player in first_team:
			second_team.remove(player)
		quality = __rateTheseTeams(first_team, second_team)
		if quality > bestQuality:
			bestTeams = [first_team, second_team]
			bestQuality = quality

	print("First team: ")
	print(list(map(lambda player: player['name'], bestTeams[0])))
	print("Second team: ")
	print(list(map(lambda player: player['name'], bestTeams[1])))
	print("Quality: ")
	print(bestQuality)

def __rateTheseTeams(first_team, second_team):
	team1_ratings = list(map(lambda player: Rating(mu=player['mu'], sigma=player['sigma']), first_team))
	team2_ratings = list(map(lambda player: Rating(mu=player['mu'], sigma=player['sigma']), second_team))
	return quality([team1_ratings, team2_ratings])

def __dateFromString(stringDate):
	monthdayyear = stringDate.split('/')
	return date(int(monthdayyear[2]), int(monthdayyear[0]), int(monthdayyear[1]))

def __sortFunc(e):
	return __dateFromString(e['date'])	

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