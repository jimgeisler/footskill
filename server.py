import datamanager
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Return all players in descending order by rating
@app.route('/', methods=['GET'])
def allPlayers():
    return datamanager.getLeaderboard()

# Generate two teams and a match quality estimate, given a list of names
@app.route('/generate', methods=['POST'])
def generateTeams():
    players = request.get_json()
    player_names = [player["name"] for player in players]
    return datamanager.generateTeamsWithPlayers(player_names)

@app.route('/games', methods=['GET'])
def allGames():
    return datamanager.getAllGames(True)

@app.route('/games', methods=['POST'])
def createGame():
    game = request.get_json()
    return datamanager.createNewGame(game["date"], game["blueTeam"], game["redTeam"], game["result"])

@app.route('/updategame', methods=['POST'])
def updateGame():
    game = request.get_json()
    return datamanager.updateGame(game)

app.run()