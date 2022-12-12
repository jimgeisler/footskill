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

app.run()