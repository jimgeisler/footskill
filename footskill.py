import sys

import datamanager
import output
import constants

outcomes = [constants.blue, constants.red, constants.balanced, constants.notTracked]

def saveGame(date, blue_team, red_team, result):
	blue_player_names = list(map(lambda name: name.strip(), blue_team.split(',')))
	red_player_names = list(map(lambda name: name.strip(), red_team.split(',')))
	datamanager.createNewGame(date, blue_player_names, red_player_names, result)

def processArguments(args):
	command = None
	arg_len = len(args)
	if arg_len >= 2:
		command = args[1]

	if command ==  'games':
		output.printGames()
	elif command == "save-game" and arg_len == 6 and args[5] in outcomes:
		saveGame(args[2], args[3], args[4], args[5])
	elif command == "teammates":
		output.printTeammates()
	elif command == "uneven-games":
		output.printUnevenGames()
	elif command == "leaderboard":
		numberOfGames = 0
		if arg_len >= 3:
			try:
				numberOfGames = int(args[2])
			except ValueError:
				print("Error: numberOfGames must be an integer")
				return
		output.printLeaderBoardWithGoalies(numberOfGames)
	elif command == "generate-teams" and arg_len == 3:
		output.printFairestTeamsWithGoalies(args[2])
	elif command == "lasttengames":
		output.printLast10games();
	elif command == "bestteammates" and arg_len == 2:
		output.printHighlightsForAllPlayers()
	elif command == "numberofgames":
		output.printNumberOfGames()
	else:
		print("Commands:")
		print(" save-game <date> <blue_players> <red_players> [Red|Blue|Balanced|Not Tracked]")
		print(" generate-teams <players>")
		print(" leaderboard [numberOfGames]")
		print(" games")
		print(" teammates")

processArguments(sys.argv)