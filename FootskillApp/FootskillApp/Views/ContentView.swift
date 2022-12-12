//
//  ContentView.swift
//  FootskillApp
//
//  Created by Chris Shoff on 12/6/22.
//

import SwiftUI

struct ContentView: View {
    @State var players: [Player] = []
    @State var selectedPlayers: [Player] = []
    
    let dataManager = DataManager()
    
    var body: some View {
        ZStack {
            VStack {
                List {
                    Section {
                        ForEach(players) { player in
                            PlayerRow(player: player) { isActive, player in
                                if (isActive) {
                                    selectedPlayers.append(player)
                                } else {
                                    if let index = selectedPlayers.firstIndex(of: player) {
                                        selectedPlayers.remove(at: index)
                                    }
                                }
                            }
                        }
                    } header: {
                        HStack {
                            Text("Player")
                            Spacer()
                            Text("W")
                            Spacer().frame(width:35)
                            Text("L")
                            Spacer().frame(width:35)
                            Text("D")
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
            
            if (selectedPlayers.count > 0) {
                CreateTeamsButton(players: selectedPlayers) { players in
                    dataManager.generateTeams(players: players) { redTeam, blueTeam, quality in
                        for player in redTeam {
                            print(player.name)
                        }
                        print("VS")
                        for player in blueTeam {
                            print(player.name)
                        }
                        print("Quality: \(quality)")
                    }
                }
            }
        }
    }
    
    func refreshData() {
        dataManager.getPlayers { players in
            self.players = players
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
