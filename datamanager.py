from tinydb import TinyDB, Query

from datetime import date

from trueskill import Rating

database = 'team-rankings-db/db.json'
db = TinyDB(database)

############################################################
### Players
############################################################


# Give a string name, create a new player in the database or find an existing one.
# name - string that represents player name
# returns a player that exists in the database
def findOrCreateNewPlayer(name):
	existingPlayer = getPlayer(name)
	if existingPlayer != None:
		return existingPlayer

	playerTable = db.table('players')
	player = __newPlayerStructure(name)
	playerTable.insert(player)
	return player

# name - string that represents a player name
def __newPlayerStructure(name):
	new_player = {}
	new_player['name'] = name
	new_player['games_played'] = 0
	new_player['wins'] = 0
	new_player['losses'] = 0
	new_player['draws'] = 0

	# Rating is represented by mu and sigma
	rating = Rating()
	new_player['mu'] = rating.mu
	new_player['sigma'] = rating.sigma

	# Historical data - starting record and rating
	new_player['records'] = []
	new_player['ratings'] = []	
	return new_player

# Get player from the database
# name - string that represents a player name
# returns player if found or None
def getPlayer(name):
	User = Query()
	playerTable = db.table('players')
	players = playerTable.search(User.name == name)

	if len(players) > 1:
		print("Found too many results")
		return None
	elif players == []:
		return None
	else:
		return players[0]

# Gets a list of players from a string of player names
# names - string of player names
# returns a list of players from the database
def getPlayers(names):
	User = Query()
	playerTable = db.table('players')
	return playerTable.search(User.name.one_of(names))

# returns a list of all players in the database
def getAllPlayers():
	return db.table('players').all()

def updatePlayerRating(name, rating):
	db.table('players').update({'mu': rating.mu, 'sigma': rating.sigma}, Query().name == name)

def updatePlayerRecord(name, record):
	db.table('players').update(record, Query().name == name)

def updatePlayerHistoricalRecordAndRating(name, struct):
	db.table('players').update(struct, Query().name == name)

def removePlayer(name):
	db.table('players').remove(Query().name == name)



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

def __newGame(date, blue_team, red_team, result):
	return {'date': date, 'blue_team': blue_team, 'red_team': red_team, 'result': result}	

# returns a list of all games in the database
def getAllGames():
	games = db.table('games').all()
	games.sort(key=__sortFunc)
	return games

def __dateFromString(stringDate):
	monthdayyear = stringDate.split('/')
	return date(int(monthdayyear[2]), int(monthdayyear[0]), int(monthdayyear[1]))

def __sortFunc(e):
	return __dateFromString(e['date'])	


