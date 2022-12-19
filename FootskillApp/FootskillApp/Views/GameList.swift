//
//  GameList.swift
//  FootskillApp
//
//  Created by Chris Shoff on 12/13/22.
//

import SwiftUI

struct GameList: View {
    @State var games: [Game] = []
    let dataManager: DataManager
    
    func backgroundColor(result: Result) -> Color {
        switch result {
        case .blue:
            return Color.blue
        case .red:
            return Color.red
        case .balanced:
            return Color.gray
        case .noResult, .new:
            return Color.white
        case .pending:
            return Color.yellow
        }
    }
    
    var body: some View {
        VStack {
            NavigationView {
                List {
                    Section {
                        ForEach(games) { game in
                            NavigationLink(destination: GameView(dataManager: dataManager, game: game)) {
                                HStack {
                                    Text("\(game.date)")
                                    Spacer()
                                    Text("\(game.redTeam.count) vs. \(game.blueTeam.count)")
                                }
                            }
                            .listRowBackground(backgroundColor(result: game.result).opacity(0.3))
                        }
                    } header: {
                        HStack {
                            Text("Date")
                            Spacer()
                            Text("Teams")
                        }
                    }
                }
            }
        }
        .onAppear {
            refreshData()
        }
        .refreshable {
            refreshData()
        }
    }
    
    func refreshData() {
        self.games = []
        dataManager.getAllGames { games in
            self.games = games
        }
    }
}

struct GameList_Previews: PreviewProvider {
    static var previews: some View {
        GameList(dataManager: DataManager())
    }
}
