# FootSkill
### A simple soccer ranking system for producing fair teams powered by TrueSkill

https://trueskill.org/#trueskill.Rating

## Requirements

> pip install trueskill
> pip install tinydb
> pip install scipy

## How to use FootSkill

Run
> python3 footskill.py

>Commands:
> leaderboard<br />
> leaderboard-table<br />
> games<br />
> save-game <date> <blue_players> <red_players> [Red|Blue|Balanced]<br />
> generate-teams <players><br />
> player-distribution-table <player_name><br />
> process-game <date>
> new-player <name>

Note: saving and processing a game are two separate steps at the moment

## Database

Data is saved into team-rankings-db/db.json

