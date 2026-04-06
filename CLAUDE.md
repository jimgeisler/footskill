# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Python Environment

All Python code must be run using the virtual environment located in the `foot/` directory:

```bash
foot/bin/python3 footskill.py
```

Dependencies are installed in `foot/lib/python3.13/site-packages/` and include:
- trueskill (TrueSkill ranking algorithm)
- tinydb (JSON-based database)
- scipy (statistics)
- flask (REST API server)

## Running the Application

### CLI Application
```bash
foot/bin/python3 footskill.py <command> [args]
```

Available commands:
- `save-game <date> <blue_players> <red_players> [Red|Blue|Balanced|Not Tracked]`
- `add-player <player_name> [template_player]` - Add new player, optionally clone rating from template
- `generate-teams <players> [--clone <new_player1> <template1> ...]` - Generate balanced teams
- `leaderboard [numberOfGames]` - Show player rankings (includes Streak and Trend columns)
- `attendance-stats <year>` - Show attendance statistics for a specific year (games played, longest streak, fake goalie games, new player status)
- `games` - Display all game history with win probabilities
- `teammates` - Show teammate statistics
- `bestteammates` - Show best teammate combinations for all players
- `mostleastplayed [numberOfGames]` - Show most/least played with statistics
- `mostgames [numberOfGames]` - Show players who have played most games together
- `lasttengames` - Show player participation counts in the last 10 games
- `uneven-games` - Show games where teams had unequal numbers of players
- `numberofgames` - Show total number of games in the database

### REST API Server
```bash
foot/bin/python3 server.py
```

Endpoints:
- `GET /` - Get leaderboard (all players by rating)
- `POST /generate` - Generate teams from player list
- `GET /games` - Get all games
- `POST /games` - Create new game
- `POST /updategame` - Update existing game

## Architecture

### Data Flow
1. **Game History** (`team-rankings-db/db.json`) - Source of truth for all games
2. **Player Starting Ratings** (`team-rankings-db/player-starting-ratings.json`) - Custom starting ratings for new players
3. **PlayersManager** - Rebuilds all player ratings from game history on initialization
4. **TrueSkill Algorithm** - Updates ratings after each game using mu (skill) and sigma (uncertainty)

### Core Modules

**footskill.py** - CLI entry point that parses commands and calls appropriate functions

**datamanager.py** - Database layer for games and player starting ratings
- `createNewGame()` - Add game to history
- `getAllGames()` - Retrieve game history (sorted by date)
- `addPlayerWithStartingRating()` - Set custom starting rating for new player
- `getPlayerStartingRating()` - Get custom starting rating if exists

**playersmanager.py** - Manages player state and rating calculations
- `populatePlayersFromGameHistory()` - Rebuilds all player ratings from scratch by replaying games
- `generatePlayerHistoryForGame()` - Updates player records and ratings for a single game
- `newPlayerStructure()` - Creates new player with default or custom starting rating
- Auto-adds "goalie" player to balance uneven teams

**output.py** - Output formatting and team generation
- Various `print*()` functions for displaying leaderboards, games, teammates
- `win_probability()` - Calculate win probability between teams using TrueSkill
- `getCurrentStreak()` - Calculate current win/loss/draw streak for a player (e.g., "W3", "L2")
- `getRatingTrend()` - Calculate rating trend over the last 10 games (e.g., "↑15.2", "↓3.5")
- `getAttendanceStatsByYear()` / `printAttendanceStatsByYear()` - Attendance stats per year including games played, longest streak, fake goalie games, and new player detection
- `generateTeamsWithPlayers()` - Core team generation logic returning best and second-best team splits

**server.py** - Flask REST API that wraps datamanager functions

**constants.py** - Shared constants including:
- Team names: `blue`, `red`, `balanced`, `notTracked`
- `env` - Global TrueSkill environment instance

### Key Patterns

**Rating System**: Uses TrueSkill with two components:
- `mu` - Skill estimate (higher = better)
- `sigma` - Uncertainty (starts high, decreases with more games)

**Player Cloning**: The `--clone` feature allows generating teams with hypothetical players who have ratings based on existing players. This is useful for "what if" scenarios.

**Goalie Balancing**: When teams have unequal numbers, a virtual "goalie" player is automatically added to the smaller team to balance the TrueSkill calculation.

**Game Results**: Games can be `Red`, `Blue`, `Balanced` (draw), or `Not Tracked` (not used for rating updates).

## iOS Application

`FootskillApp/` contains a SwiftUI iOS app that communicates with the Flask REST server:
- Model layer: `Player.swift`, `Game.swift`, `GeneratedTeams.swift`
- Controller: `DataManager.swift` handles API calls
- Views: SwiftUI views for player/game lists and team generation

## Database Structure

Both databases use TinyDB (JSON-based):

**team-rankings-db/db.json**:
```json
{
  "games": [
    {
      "date": "MM/DD/YYYY",
      "blue_team": ["player1", "player2"],
      "red_team": ["player3", "player4"],
      "result": "Red|Blue|Balanced|Not Tracked"
    }
  ]
}
```

**team-rankings-db/player-starting-ratings.json**:
```json
[
  {
    "name": "player_name",
    "starting_mu": 25.0,
    "starting_sigma": 8.333
  }
]
```

## Testing

Tests use pytest and are in files like `test_best_teammate.py`. Run with:
```bash
foot/bin/python3 -m pytest test_best_teammate.py
```

## Important Notes

- Player ratings are ALWAYS recalculated from scratch by replaying all games in chronological order
- Adding a game to history automatically triggers rating recalculation for all affected players
- The system assumes games are in chronological order (sorted by date)
- Custom starting ratings allow new players to start at a specific skill level while maintaining high uncertainty
