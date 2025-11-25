import sys

import datamanager
import output
import constants
from playersmanager import PlayersManager

outcomes = [constants.blue, constants.red, constants.balanced, constants.notTracked]

def saveGame(date, blue_team, red_team, result):
	blue_player_names = list(map(lambda name: name.strip(), blue_team.split(',')))
	red_player_names = list(map(lambda name: name.strip(), red_team.split(',')))
	datamanager.createNewGame(date, blue_player_names, red_player_names, result)

def addPlayer(player_name, template_player_name=None):
	"""
	Add a new player to the database with an optional starting rating based on a template player.
	If template_player_name is provided, the new player will start with that player's mu (skill)
	but with default sigma (high uncertainty) so their rating adjusts quickly as they play.
	"""
	# Create a PlayersManager to get current ratings from game history
	pm = PlayersManager()

	if template_player_name:
		# Find the template player's current rating
		template_player = None
		for player in pm.tempAllPlayers:
			if player['name'] == template_player_name:
				template_player = player
				break

		if template_player is None:
			print(f"Error: Template player '{template_player_name}' not found in game history")
			return

		# Use template's mu but default sigma for high uncertainty
		from trueskill import Rating
		default_rating = Rating()
		default_sigma = default_rating.sigma

		# Add the new player with the template's mu and default sigma
		datamanager.addPlayerWithStartingRating(
			player_name,
			template_player['mu'],
			default_sigma
		)
		print(f"Player '{player_name}' will start with:")
		print(f"  mu (skill) = {template_player['mu']:.2f} (from {template_player_name})")
		print(f"  sigma (uncertainty) = {default_sigma:.2f} (default - will adjust quickly)")
	else:
		# Just add with default rating (which is what happens anyway, but we confirm it)
		print(f"Player '{player_name}' will start with default rating when they play their first game")
		print("To set a starting rating, use: add-player <player_name> <template_player>")

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
	elif command == "generate-teams" and arg_len >= 3:
		# Parse optional --clone arguments
		clone_pairs = {}
		player_list_arg = args[2]

		# Check for --clone option
		if arg_len >= 4 and args[3] == "--clone":
			# Parse clone pairs: --clone new1 template1 new2 template2 ...
			clone_args = args[4:]
			if len(clone_args) < 2 or len(clone_args) % 2 != 0:
				print("Error: --clone requires pairs of arguments (new_player template_player)")
				return

			# Build dictionary of clone pairs
			for i in range(0, len(clone_args), 2):
				new_player = clone_args[i]
				template_player = clone_args[i + 1]
				clone_pairs[new_player] = template_player

		output.printFairestTeamsWithGoalies(player_list_arg, clone_pairs)
	elif command == "lasttengames":
		output.printLast10games();
	elif command == "bestteammates" and arg_len == 2:
		output.printHighlightsForAllPlayers()
	elif command == "mostleastplayed":
		numberOfGames = 0
		if arg_len >= 3:
			try:
				numberOfGames = int(args[2])
			except ValueError:
				print("Error: numberOfGames must be an integer")
				return
		output.printMostLeastPlayedWith(numberOfGames)
	elif command == "mostgames":
		numberOfGames = 0
		if arg_len >= 3:
			try:
				numberOfGames = int(args[2])
			except ValueError:
				print("Error: numberOfGames must be an integer")
				return
		output.printMostLeastGamesPlayedWith(numberOfGames)
	elif command == "numberofgames":
		output.printNumberOfGames()
	elif command == "add-player":
		if arg_len == 3:
			addPlayer(args[2])
		elif arg_len == 4:
			addPlayer(args[2], args[3])
		else:
			print("Usage: add-player <player_name> [template_player]")
	else:
		print("Commands:")
		print(" save-game <date> <blue_players> <red_players> [Red|Blue|Balanced|Not Tracked]")
		print(" add-player <player_name> [template_player]")
		print(" generate-teams <players> [--clone <new_player1> <template1> <new_player2> <template2> ...]")
		print(" leaderboard [numberOfGames]")
		print(" games")
		print(" teammates")
		print(" bestteammates")
		print(" mostleastplayed [numberOfGames]")
		print(" mostgames [numberOfGames]")

processArguments(sys.argv)