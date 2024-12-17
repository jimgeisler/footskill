# FootSkill
### A simple soccer ranking system for producing fair teams powered by TrueSkill

https://trueskill.org/#trueskill.Rating

## Requirements

> pip install trueskill
> pip install tinydb
> pip install scipy

## Additional Server Requirements

> pip install flask

## How to use FootSkill

Run
> python3 footskill.py

>Commands:
> save-game <date> <blue_players> <red_players> [Red|Blue|Balanced]<br />
> generate-teams <players><br />
> leaderboard<br />
> games<br />
> teammates <name>

Notes:
saving a game adds it to the historical record
player history is generated from the game history

## How to use FootSkill REST server

> python3 server.py

## Database

Data is saved into team-rankings-db/db.json

