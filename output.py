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

def printHighlightsForAllPlayers():
	print("Player, Teammate, Record, Improvement")
	for player in getLeaderboard():
		record = player['records'][-1]
		win_percentage = record['wins'] / record['games_played']
		name = player['name']

		teammates_records = getRecordsWithTeammates(name)
		best_teammate = ""
		best_record = 0.0

		# print(teammates_records)

		for record in teammates_records:
			teammate_name = record['name']
			record_with_mate = record['info']
			gp = record_with_mate['gp']
			wp = record_with_mate['wp']

			if gp > 5 and wp > best_record:
				best_record = wp
				best_teammate = teammate_name

		print(name + ", " + best_teammate + ", " + str(best_record) + ", " + str(best_record - win_percentage))



def getRecordsWithTeammates(player):
	games = datamanager.getAllGames()

	player_record_per_teammate = {}
	count = 0
	for game in games:
		blueteam = game['blue_team']
		redteam = game['red_team']
		result = game['result']
		team = ""
		teammates = []

		if player in blueteam:
			team = constants.blue
			count += 1
			teammates = blueteam
		elif player in redteam:
			team = constants.red
			count += 1
			teammates = redteam
		else:
			continue

		for teammate in teammates:
			if teammate == player:
				continue

			if not teammate in player_record_per_teammate:
				player_record_per_teammate[teammate] = {"w":0, "l": 0, "d": 0}
			if result == team:
				player_record_per_teammate[teammate]["w"] += 1
			elif result == constants.balanced:
				player_record_per_teammate[teammate]["d"] += 1
			else:
				player_record_per_teammate[teammate]["l"] += 1

	all_mates = []
	# print("Teammate, Wins, Losses, Draws, GP")
	for teammate_name in player_record_per_teammate:
		record = player_record_per_teammate[teammate_name]
		gp = record['w'] + record['l'] + record['d']
		wp = record['w'] / gp
		# print(teammate_name + ", " + str(record['w']) + ", " + str(record['l']) + ", " + str(record['d']) + ", " + str(gp))
		# print("win percentage: " + str(wp))
		all_mates.append({ 'name': teammate_name, 'info' : {'wp': wp, 'gp': gp }})

	return all_mates

###########

def printMostLeastPlayedWith(numberOfGames=0):
	"""
	Print a table showing each player's most and least frequently played with teammates.
	Shows the percentage of games together when both players were present.
	Only includes other players with 5+ games together.

	Args:
		numberOfGames: If > 0, only considers the last N games. If 0, uses all games.
	"""
	print("Most and Least Played With Teammates")
	if numberOfGames > 0:
		print(f"(Last {numberOfGames} games)")
	print("Player, Most Played With, % Together, Games Together, Least Played With, % Together, Games Together")

	leaderboard = getLeaderboard()

	for player in leaderboard:
		player_name = player['name']

		# Skip goalie
		if player_name == "goalie":
			continue

		# Skip players with fewer than 10 games
		total_games = player['records'][-1]['games_played']
		if total_games < 10:
			continue

		# Get games (filtered if numberOfGames is specified)
		all_games = datamanager.getAllGames()
		if numberOfGames > 0:
			games = all_games[-numberOfGames:] if len(all_games) >= numberOfGames else all_games
		else:
			games = all_games

		# Track for each other player:
		# - games together on same team
		# - games together total (same team OR opposing teams)
		teammate_data = {}  # {player_name: {'same_team': count, 'total_together': count}}

		for game in games:
			blueteam = game['blue_team']
			redteam = game['red_team']

			# Check if this player is in the game
			player_team = None
			if player_name in blueteam:
				player_team = 'blue'
			elif player_name in redteam:
				player_team = 'red'
			else:
				continue

			# For each other player in this game, track if same team or opposite team
			all_other_players = blueteam + redteam
			for other_player in all_other_players:
				if other_player == player_name or other_player == "goalie":
					continue

				if other_player not in teammate_data:
					teammate_data[other_player] = {'same_team': 0, 'total_together': 0}

				teammate_data[other_player]['total_together'] += 1

				# Check if on same team
				if (player_team == 'blue' and other_player in blueteam) or \
				   (player_team == 'red' and other_player in redteam):
					teammate_data[other_player]['same_team'] += 1

		# Calculate percentages and filter to those with 5+ games together
		teammate_percentages = {}
		for other_player, data in teammate_data.items():
			if data['total_together'] >= 5:
				percentage = (data['same_team'] / data['total_together']) * 100
				teammate_percentages[other_player] = {
					'percentage': percentage,
					'games_together': data['total_together']
				}

		if len(teammate_percentages) == 0:
			continue

		# Find most and least played with
		most_played = max(teammate_percentages.items(), key=lambda x: x[1]['percentage'])
		least_played = min(teammate_percentages.items(), key=lambda x: x[1]['percentage'])

		print(f"{player_name}, {most_played[0]}, {most_played[1]['percentage']:.1f}%, "
		      f"{most_played[1]['games_together']}, "
		      f"{least_played[0]}, {least_played[1]['percentage']:.1f}%, "
		      f"{least_played[1]['games_together']}")

###########

def printMostLeastGamesPlayedWith(numberOfGames=0):
	"""
	Print a table showing each player's most and least games played with another person as teammates.
	This counts only games on the same team.
	Only includes other players with 5+ games as teammates.

	Args:
		numberOfGames: If > 0, only considers the last N games. If 0, uses all games.
	"""
	print("Most and Least Games Played With (Same Team)")
	if numberOfGames > 0:
		print(f"(Last {numberOfGames} games)")
	print("Player, Most Games With, Games As Teammates, Least Games With, Games As Teammates")

	leaderboard = getLeaderboard()

	for player in leaderboard:
		player_name = player['name']

		# Skip goalie
		if player_name == "goalie":
			continue

		# Skip players with fewer than 10 games
		total_games = player['records'][-1]['games_played']
		if total_games < 10:
			continue

		# Get games (filtered if numberOfGames is specified)
		all_games = datamanager.getAllGames()
		if numberOfGames > 0:
			games = all_games[-numberOfGames:] if len(all_games) >= numberOfGames else all_games
		else:
			games = all_games

		# Count how many times this player has been on the same team as each other player
		games_with_player = {}

		for game in games:
			blueteam = game['blue_team']
			redteam = game['red_team']

			# Check if this player is in the game and get their team
			player_team = None
			if player_name in blueteam:
				player_team = 'blue'
			elif player_name in redteam:
				player_team = 'red'
			else:
				continue

			# Count only teammates on the same team
			teammates = blueteam if player_team == 'blue' else redteam
			for teammate in teammates:
				if teammate == player_name or teammate == "goalie":
					continue

				if teammate not in games_with_player:
					games_with_player[teammate] = 0
				games_with_player[teammate] += 1

		# Filter to those with 5+ games together
		filtered_players = {k: v for k, v in games_with_player.items() if v >= 5}

		if len(filtered_players) == 0:
			continue

		# Find most and least games with
		most_games_with = max(filtered_players.items(), key=lambda x: x[1])
		least_games_with = min(filtered_players.items(), key=lambda x: x[1])

		print(f"{player_name}, {most_games_with[0]}, {most_games_with[1]}, "
		      f"{least_games_with[0]}, {least_games_with[1]}")

###########

def printNumberOfGames():
	games = datamanager.getAllGames()
	print(str(len(games)))

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

def getCurrentStreak(player_name):
	"""
	Calculate the current win/loss/draw streak for a player.
	Returns a string like "W3" (3 game win streak), "L2" (2 game loss streak), or "D1" (1 game draw streak)
	"""
	# Special case: goalie is a placeholder, not a real player
	if player_name == "goalie":
		return "N/A"

	games = datamanager.getAllGames(reverse=True)  # Get games in reverse order (most recent first)

	streak_type = None
	streak_count = 0

	for game in games:
		# Check if player is in this game
		player_team = None
		if player_name in game['blue_team']:
			player_team = constants.blue
		elif player_name in game['red_team']:
			player_team = constants.red
		else:
			continue  # Player not in this game

		# Determine result for this player
		result = game['result']
		if result not in ['Red', 'Blue', 'Balanced']:
			continue  # Skip games without tracked results

		if result == constants.balanced:
			current_result = 'D'
		elif result == player_team:
			current_result = 'W'
		else:
			current_result = 'L'

		# First game in streak
		if streak_type is None:
			streak_type = current_result
			streak_count = 1
		# Streak continues
		elif streak_type == current_result:
			streak_count += 1
		# Streak broken
		else:
			break

	if streak_type is None:
		return ""

	return f"{streak_type}{streak_count}"

def getRatingTrend(player_name, trend_window=10):
	"""
	Calculate rating trend over the last N games.
	Returns a string like "↑15.2" (up 15.2 points) or "↓3.5" (down 3.5 points)
	"""
	# Special case: goalie is a placeholder, not a real player
	if player_name == "goalie":
		return "N/A"

	games = datamanager.getAllGames(reverse=True)

	# Build a list of this player's games with their rating after each game
	player_games = []

	# We need to replay history to get ratings at specific points
	# Use the player's records which have historical data
	players = playersManager.tempAllPlayers
	player_data = None
	for p in players:
		if p['name'] == player_name:
			player_data = p
			break

	if player_data is None or 'records' not in player_data or len(player_data['records']) == 0:
		return ""

	records = player_data['records']

	# We need to get the rating at different points in time
	# The challenge is that records don't include ratings, only win/loss/draw counts
	# We need to rebuild ratings from the PlayersManager

	# Alternative approach: compare current rating to rating N games ago
	# We'll need to rebuild the player history up to N games ago

	all_games = datamanager.getAllGames()
	player_game_count = 0

	# Count how many games this player has participated in
	for game in all_games:
		if player_name in game['blue_team'] or player_name in game['red_team']:
			if game['result'] in ['Red', 'Blue', 'Balanced']:
				player_game_count += 1

	if player_game_count < trend_window:
		# Not enough games for trend
		return ""

	# Get current rating
	current_rating = player_data['mu'] - 3 * player_data['sigma']

	# Rebuild ratings up to N games ago
	past_manager = PlayersManager()
	past_manager.clearPlayers()

	games_processed = 0
	for game in all_games:
		# Check if player is in this game
		if player_name in game['blue_team'] or player_name in game['red_team']:
			if game['result'] in ['Red', 'Blue', 'Balanced']:
				games_processed += 1

				# Stop before the last N games
				if games_processed > player_game_count - trend_window:
					break

		# Process this game
		if game['result'] in ['Red', 'Blue', 'Balanced']:
			past_manager.generatePlayerHistoryForGame(game)

	# Get the player's rating N games ago
	past_player = None
	for p in past_manager.tempAllPlayers:
		if p['name'] == player_name:
			past_player = p
			break

	if past_player is None:
		return ""

	past_rating = past_player['mu'] - 3 * past_player['sigma']
	rating_change = current_rating - past_rating

	if rating_change > 0:
		return f"↑{rating_change:.1f}"
	elif rating_change < 0:
		return f"↓{abs(rating_change):.1f}"
	else:
		return "→0.0"

def printLeaderBoardWithGoalies(numberOfGames=0):
	print("Leaderboard")
	if numberOfGames > 0:
		print(f"(Last {numberOfGames} games)")
	print("Name, W, L, D, GP, PPG, Win %, Rank, Streak, Trend")
	csp = ', '
	for player in getLeaderboard(numberOfGames):
		record = player['records'][-1]
		tempOutput = player['name'] + csp
		tempOutput += str(record['wins']) + csp
		tempOutput += str(record['losses']) + csp
		tempOutput += str(record['draws']) + csp
		tempOutput += str(record['games_played']) + csp
		tempOutput += str((record['wins'] * 3 + record['draws']) / record['games_played']) + csp
		tempOutput += str(record['wins'] / record['games_played']) + csp
		tempOutput += str(player['mu'] - 3 * player['sigma']) + csp

		# Add streak
		streak = getCurrentStreak(player['name'])
		tempOutput += streak + csp

		# Add trend (only for full leaderboard, not filtered by numberOfGames)
		if numberOfGames == 0:
			trend = getRatingTrend(player['name'])
			tempOutput += trend
		else:
			tempOutput += "N/A"

		print(tempOutput)

def getLeaderboard(numberOfGames=0):
	# If numberOfGames is specified, create a new PlayersManager with limited history
	if numberOfGames > 0:
		limitedPlayersManager = PlayersManager()
		limitedPlayersManager.clearPlayers()

		# Get only the last N games
		all_games = datamanager.getAllGames()
		recent_games = all_games[-numberOfGames:] if len(all_games) >= numberOfGames else all_games

		# Process only these recent games
		for game in recent_games:
			if game['result'] in ['Red', 'Blue', 'Balanced']:
				limitedPlayersManager.generatePlayerHistoryForGame(game)

		players = limitedPlayersManager.tempAllPlayers
	else:
		# Use full history
		players = playersManager.tempAllPlayers

	ratings = []
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
