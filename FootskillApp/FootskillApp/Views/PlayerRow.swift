//
//  PlayerRow.swift
//  FootskillApp
//
//  Created by Chris Shoff on 12/7/22.
//

import SwiftUI

struct PlayerRow: View {
    let player: Player
    @State var isPlaying: Bool = false
    let toggleActiveCallback: (Bool, Player) -> Void
    
    var body: some View {
        HStack {
            if (isPlaying) {
                Image(systemName: "figure.soccer")
            }
            Text("\(player.name)")
                .bold()
            Spacer()
            Text("\(player.wins)")
            Spacer().frame(width:35)
            Text("\(player.losses)")
            Spacer().frame(width:35)
            Text("\(player.draws)")
        }
        .swipeActions(edge: .leading, allowsFullSwipe: true) {
            Button {
                isPlaying = !isPlaying
                toggleActiveCallback(isPlaying, player)
            } label: {
                if (isPlaying) {
                    Label("Not Playing", systemImage: "person.fill.badge.minus")
                } else {
                    Label("Playing", systemImage: "figure.soccer")
                }
            }
            .tint(isPlaying ? .red : .blue)
        }
    }
}

struct PlayerRow_Previews: PreviewProvider {
    static var previews: some View {
        PlayerRow(player: Player()) { _, _ in }
    }
}
