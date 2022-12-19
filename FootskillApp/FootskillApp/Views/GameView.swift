//
//  GameView.swift
//  FootskillApp
//
//  Created by Chris Shoff on 12/13/22.
//

import SwiftUI

struct GameView: View {
    let dataManager: DataManager
    @State var game: Game?
    var players: [Player]?
    @Environment(\.presentationMode) var presentationMode
    
    var body: some View {
        if var game = game {
            VStack {
                Text(game.date)
                    .font(.title2)
                HStack {
                    TeamView(team: game.redTeam, edge: .leading)
                    TeamView(team: game.blueTeam, edge: .trailing)
                }
                HStack {
                    if game.result == .red ||
                        game.result == .blue ||
                        game.result == .balanced {
                        ResultBadge(result: game.result)
                    } else if game.result == .pending {
                        PickResultView() { result in
                            game.result = result
                            dataManager.updateGame(game: game) { game in
                                self.game = game
                            }
                        }
                    } else {
                        AcceptCancelView {
                            game.result = .pending
                            dataManager.createNewGame(game: game) { game in
                                self.game = game
                            }
                        } cancelAction: {
                            self.presentationMode.wrappedValue.dismiss()
                        }

                    }
                }
                Spacer()
            }
        } else {
            Text("Generating teams...")
                .onAppear {
                    if let players = players {
                        dataManager.generateTeams(players: players) { redTeam, blueTeam, quality in
                            
                            let redTeamNames = redTeam.map { $0.name }
                            let blueTeamNames = blueTeam.map { $0.name }
                            
                            let date = Date()
                            let dateFormatter = DateFormatter()
                            dateFormatter.dateFormat = "MM/dd/YYYY"
                            
                            game = Game(date: dateFormatter.string(from: date), redTeam: redTeamNames, blueTeam: blueTeamNames, result: .new)
                        }
                    }
                }
        }
    }
}

struct GameView_Previews: PreviewProvider {
    static var previews: some View {
        GameView(dataManager: DataManager(), game: Game(date: "12/13/2022", redTeam: ["Chris S.", "Chris C.", "Ed", "Greg", "Kunal", "Matt"], blueTeam: ["Dave", "Dominik", "Jeff", "Jim", "Nate", "Steven"], result: .red))
    }
}
