import datamanager
import constants

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

class PlayersManager:
	def __init__(self):
		self.tempAllPlayers = []
		self.populatePlayersFromGameHistory()

	def clearPlayers(self):
		self.tempAllPlayers = []

	def __sortFunc(self, e):
		return self.__dateFromString(e['date'])

	def __dateFromString(self, stringDate):
		monthdayyear = stringDate.split('/')
		return date(int(monthdayyear[2]), int(monthdayyear[0]), int(monthdayyear[1]))			

	def populatePlayersFromGameHistory(self):
		games = datamanager.getAllGames()
		for game in games:
			if game['result'] in ['Red', 'Blue', 'Balanced']:
				self.generatePlayerHistoryForGame(game)	

	def getPlayers(self, player_names):
		today_players = []
		for name in player_names:
			players = list(filter(lambda p: p['name'] == name, self.tempAllPlayers))
			if len(players) == 0:
				new_p = self.findOrCreateNewPlayer(name)
				today_players.append(new_p)
				self.tempAllPlayers.append(new_p)
			else:
				today_players.append(players[0])
		return today_players

	def findOrCreateNewPlayer(self, player_name):
		players = list(filter(lambda p: p['name'] == player_name, self.tempAllPlayers))
		player = self.newPlayerStructure(player_name)
		if len(players) > 0:
			player = players[0]
		else:
			self.tempAllPlayers.append(player)
		return player

	def newPlayerStructure(self, name):
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

	def generatePlayerHistoryForGame(self, game):
		result = game['result']
		game_date = game['date']

		blue_players = list(map(lambda player_name: self.findOrCreateNewPlayer(player_name), game['blue_team']))
		red_players = list(map(lambda player_name: self.findOrCreateNewPlayer(player_name), game['red_team']))

		if len(blue_players) > len(red_players):
			red_players.append(self.findOrCreateNewPlayer("goalie"))
		elif len(red_players) > len(blue_players):
			blue_players.append(self.findOrCreateNewPlayer("goalie"))

		if len(blue_players) > len(red_players):
			print("ISSUES")
		elif len(red_players) > len(blue_players):
			print("ISSUES")

		for player in blue_players:
			self.updatePlayerRecords(player, constants.blue, result, game_date)
		for player in red_players:
			self.updatePlayerRecords(player, constants.red, result, game_date)

		self.recordGame(blue_players, red_players, result, game_date)

	def updatePlayerRecord(self, name, record_history):
		players = list(filter(lambda p: p['name'] == name, self.tempAllPlayers))
		player = players[0]
		player['records'] = record_history

	def updatePlayerRecords(self, player, team_name, result, game_date):
		record_history = []
		if 'records' in player:
			record_history = player['records']
		latest_record = {'wins': 0, 'losses': 0, 'draws': 0, 'games_played': 0}
		if record_history != []:
			record_history.sort(key=self.__sortFunc)
			latest_record = record_history[-1]
			
		new_record = self.updateRecordStructure(latest_record, team_name, result)
		new_record['date'] = game_date

		record_history.append(new_record)
		
		self.updatePlayerRecord(player['name'], record_history)

	def updateRecordStructure(self, record, team_name, result):
		record_updates = record
		record_updates['games_played'] = int(record['games_played']) + 1
		if team_name == constants.blue:
			if result == constants.blue:
				record_updates['wins'] = int(record['wins']) + 1
			elif result == constants.red:
				record_updates['losses'] = int(record['losses']) + 1
			elif result == constants.balanced:
				record_updates['draws'] = int(record['draws']) + 1
		elif team_name == constants.red:
			if result == constants.red:
				record_updates['wins'] = int(record['wins']) + 1
			elif result == constants.blue:
				record_updates['losses'] = int(record['losses']) + 1
			elif result == constants.balanced:
				record_updates['draws'] = int(record['draws']) + 1	
		return record_updates		

	def recordGame(self, blue_team, red_team, result, game_date):
		blue_team_ratings = {}
		red_team_ratings = {}
		for p in blue_team:
			blue_team_ratings[p['name']] = Rating(mu=p['mu'], sigma=p['sigma'])
		for p in red_team:
			red_team_ratings[p['name']] = Rating(mu=p['mu'], sigma=p['sigma'])
		if result == constants.balanced:
			updated_ratings = constants.env.rate([blue_team_ratings, red_team_ratings], ranks=[0,0])
		elif result == constants.blue:
			updated_ratings = constants.env.rate([blue_team_ratings, red_team_ratings], ranks=[0,1])
		elif result == constants.red:
			updated_ratings = constants.env.rate([blue_team_ratings, red_team_ratings], ranks=[1,0])
		else:
			return

		blue_team_updated_ratings = updated_ratings[0]
		red_team_updated_ratings = updated_ratings[1]
		for player_name in blue_team_updated_ratings:
			new_rating = blue_team_updated_ratings[player_name]
			self.updatePlayerRating(player_name, new_rating)
		for player_name in red_team_updated_ratings:
			new_rating = red_team_updated_ratings[player_name]
			self.updatePlayerRating(player_name, new_rating)

	def updatePlayerRating(self, name, rating):
		players = list(filter(lambda p: p['name'] == name, self.tempAllPlayers))
		player = players[0]
		player['mu'] = rating.mu
		player['sigma'] = rating.sigma
