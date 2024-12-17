import sys

import datamanager
import output
import constants

outcomes = [constants.blue, constants.red, constants.balanced]

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
		output.printLeaderBoardWithGoalies()
	elif command == "generate-teams" and arg_len == 3:
		output.printFairestTeamsWithGoalies(args[2])
	elif command == "lasttengames":
		output.printLast10games();
	else:
		print("Commands:")
		print(" save-game <date> <blue_players> <red_players> [Red|Blue|Balanced]")
		print(" generate-teams <players>")
		print(" leaderboard")
		print(" games")		
		print(" teammates")

processArguments(sys.argv)