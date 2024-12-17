from tinydb import TinyDB, Query

from datetime import date

from trueskill import Rating, quality

import constants
import itertools

database = 'team-rankings-db/db.json'
db = TinyDB(database)

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


