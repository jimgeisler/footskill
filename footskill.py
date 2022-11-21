import sys

import datamanager
import output
import constants
import analysis

outcomes = [constants.blue, constants.red, constants.balanced]

def processGame(date):
	game = datamanager.getGame(date)
	analysis.generatePlayerHistoryForGame(game)

def saveGame(date, blue_team, red_team, result):
	blue_player_names = list(map(lambda name: name.strip(), blue_team.split(',')))
	red_player_names = list(map(lambda name: name.strip(), red_team.split(',')))
	datamanager.createNewGame(date, blue_player_names, red_player_names, result)

def processArguments(args):
	command = None
	arg_len = len(args)
	if arg_len >= 2:
		command = args[1]

	if command == 'leaderboard':
		output.printLeaderBoard('standard')
	elif command == 'leaderboard-table':
		output.printLeaderBoard('csv')
	elif command == 'leaderboard-rating':
		output.printLeaderBoard('mu')
	elif command ==  'games':
		output.printGames()
	elif command == "save-game" and arg_len == 6 and args[5] in outcomes:
		saveGame(args[2], args[3], args[4], args[5])
	elif command == "generate-teams" and arg_len == 3:
		output.printFairestTeams(args[2])
	elif command == "player-distribution-table" and arg_len == 3:
		output.printPlayerDistribution(args[2])
	elif command == "process-game" and arg_len == 3:
		processGame(args[2])
	elif command == "new-player" and arg_len == 3:
		player = datamanager.findOrCreateNewPlayer(args[2])
		print(player)
	elif command == "player-details" and arg_len == 3:
		output.printPlayerDetails(args[2])
	else:
		print("Commands:")
		print(" leaderboard")
		print(" leaderboard-table")
		print(" leaderboard-rating")
		print(" games")
		print(" process-game <date>")
		print(" save-game <date> <blue_players> <red_players> [Red|Blue|Balanced]")
		print(" generate-teams <players>")
		print(" player-distribution-table <player_name>")
		print(" process-game <date>")
		print(" new-player <name>")
		print(" player-details <name>")

processArguments(sys.argv)