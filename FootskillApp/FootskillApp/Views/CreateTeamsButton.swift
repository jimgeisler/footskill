//
//  CreateTeamsButton.swift
//  FootskillApp
//
//  Created by Chris Shoff on 12/7/22.
//

import SwiftUI

struct CreateTeamsButton: View {
    let dataManager: DataManager
    var players: [Player] = []
    
    var body: some View {
        VStack {
            Spacer()
            NavigationLink(destination: GameView(dataManager: dataManager, players: players)) {
                HStack {
                    Spacer()
                    Text("Create teams with \(players.count) players")
                        .padding()
                        .foregroundColor(.white)
                        .padding(.bottom, 3)
                        .background(.blue)
                        .cornerRadius(38.5)
                        .padding()
                        .shadow(color: .black.opacity(0.3), radius: 3, x: 3, y: 3)
                }
            }
        }
    }
}

struct CreateTeamsButton_Previews: PreviewProvider {
    static var previews: some View {
        CreateTeamsButton(dataManager: DataManager(), players: [])
    }
}
