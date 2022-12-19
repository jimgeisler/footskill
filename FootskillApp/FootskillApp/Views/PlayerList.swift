//
//  PlayerList.swift
//  FootskillApp
//
//  Created by Chris Shoff on 12/13/22.
//

import SwiftUI

struct PlayerList: View {
    @State var players: [Player] = []
    @State var selectedPlayers: [Player] = []
    let dataManager: DataManager
    
    var body: some View {
        NavigationView {
            ZStack {
                VStack {
                    List {
                        Section {
                            ForEach(players) { player in
                                PlayerRow(player: player, isPlaying: selectedPlayers.contains(player)) { isActive, player in
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
                    CreateTeamsButton(dataManager: dataManager, players: selectedPlayers)
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

struct PlayerList_Previews: PreviewProvider {
    static var previews: some View {
        PlayerList(dataManager: DataManager())
    }
}
