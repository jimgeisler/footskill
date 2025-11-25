from tinydb import TinyDB, Query

from datetime import date

from trueskill import Rating, quality

import constants
import itertools

database = 'team-rankings-db/db.json'
db = TinyDB(database)

player_ratings_database = 'team-rankings-db/player-starting-ratings.json'
player_ratings_db = TinyDB(player_ratings_database)

############################################################
### Games
############################################################

def createNewGame(date, blue_team, red_team, result):
	existingGames = getGame(date)
	if existingGames != None:
		return existingGames
	gameTable = db.table('games')
	game = __newGame(date, blue_team, red_team, result)
	gameTable.insert(game)
	return game

# Get game from the database
# date - string that represents the game's date
# returns a game if it exists or None
def getGame(date):
	gameTable = db.table('games')
	games = gameTable.search(Query().date == date)
	if len(games) > 1:
		print("Found too many results")
		return None
	elif games == []:
		return None
	else:
		return games[0]
	return game

def updateGame(game):
	db.table('games').update(game, Query().date == game['date'])
	return game

def __newGame(date, blue_team, red_team, result):
	return {'date': date, 'blue_team': blue_team, 'red_team': red_team, 'result': result}	

# returns a list of all games in the database
# reverse - boolean that will return the results in descending order if true
def getAllGames(reverse=False):
	games = db.table('games').all()
	games.sort(key=__sortFunc)
	if reverse:
		games.reverse()
	return games

def __dateFromString(stringDate):
	monthdayyear = stringDate.split('/')
	return date(int(monthdayyear[2]), int(monthdayyear[0]), int(monthdayyear[1]))

def __sortFunc(e):
	return __dateFromString(e['date'])

############################################################
### Player Starting Ratings
############################################################

def addPlayerWithStartingRating(player_name, starting_mu, starting_sigma):
	"""
	Add a player to the database with a custom starting rating.
	This is used for new players who should start with a rating based on a template player.
	"""
	# Check if player already exists
	existing = player_ratings_db.search(Query().name == player_name)
	if existing:
		print(f"Player '{player_name}' already exists with a starting rating")
		return existing[0]

	player = {
		'name': player_name,
		'starting_mu': starting_mu,
		'starting_sigma': starting_sigma
	}
	player_ratings_db.insert(player)
	print(f"Added player '{player_name}' with starting rating from template")
	return player

def getPlayerStartingRating(player_name):
	"""
	Get a player's starting rating from the database.
	Returns None if the player doesn't have a custom starting rating.
	"""
	players = player_ratings_db.search(Query().name == player_name)
	if players:
		return {
			'mu': players[0]['starting_mu'],
			'sigma': players[0]['starting_sigma']
		}
	return None

def getAllPlayersWithStartingRatings():
	"""
	Get all players who have custom starting ratings.
	"""
	return player_ratings_db.all()


