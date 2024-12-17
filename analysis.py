
import datamanager
import importutils
import constants
import output

from datetime import date

local_players = {}

def clearPlayers():
	all_players = datamanager.getAllPlayers()
	for player in all_players:
		datamanager.removePlayer(player['name'])

def __dateFromString(stringDate):
	monthdayyear = stringDate.split('/')
	return date(int(monthdayyear[2]), int(monthdayyear[0]), int(monthdayyear[1]))

def __sortFunc(e):
	return __dateFromString(e['date'])	


# generatePlayerHistory()
clearPlayers()
# clearRecords()
# output.printPlayers()