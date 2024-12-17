import datamanager
import constants
from playersmanager import PlayersManager

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

playersManager = PlayersManager()

# Prints the game data
def printGames():
	printPlayersManager = PlayersManager()
	printPlayersManager.clearPlayers()
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
			player = printPlayersManager.findOrCreateNewPlayer(player_name)
			blue_team_ratings.append(player)
		red_players = ""
		for player_name in game['red_team']:
			red_players += player_name + " "
			player = printPlayersManager.findOrCreateNewPlayer(player_name)
			red_team_ratings.append(player)

		if len(game['blue_team']) > len(game['red_team']):
			player_name = "goalie"
			red_players += player_name + " "
			player = printPlayersManager.findOrCreateNewPlayer(player_name)
			red_team_ratings.append(player)
		elif len(game['red_team']) > len(game['blue_team']):
			player_name = "goalie"
			blue_players += player_name + " "
			player = printPlayersManager.findOrCreateNewPlayer(player_name)
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

		printPlayersManager.generatePlayerHistoryForGame(game)

def win_probability(team1, team2):
    delta_mu = sum(r['mu'] for r in team1) - sum(r['mu'] for r in team2)
    sum_sigma = sum(r['sigma'] ** 2 for r in itertools.chain(team1, team2))
    size = len(team1) + len(team2)
    denom = math.sqrt(size * (BETA * BETA) + sum_sigma)
    ts = trueskill.global_env()
    return ts.cdf(delta_mu / denom)

def _playerNameSorter(elem):
	return elem['name']
				
def printPlayerCommandLine(player):
	gp = player['wins'] + player['losses'] + player['draws']
	print(player['name'] + ": (%d, %d, %d) / %d" % (player['wins'], player['losses'], player['draws'], gp))

def printPlayerCSVFormat(player, place, prev_game_rank):
	gp = player['wins'] + player['losses'] + player['draws']
	diff = prev_game_rank - place
	rank = player['mu'] - 3 * player['sigma']
	print(player['name'] + ", %d, %d, %d, %d, %d, %d, %d" % (place, player['wins'], player['losses'], player['draws'], gp, diff, rank))

###########

def printFairestTeamsWithGoalies(player_names):
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

def generateTeamsWithPlayers(player_names):
	names = player_names.split(', ')
	if (len(names) % 2) != 0:
		names.append("goalie")
	players = playersManager.getPlayers(names)

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
	print("Leaderboard")
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
	players = playersManager.tempAllPlayers

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
