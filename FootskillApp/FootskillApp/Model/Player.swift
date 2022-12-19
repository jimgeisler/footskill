//
//  Player.swift
//  FootskillApp
//
//  Created by Chris Shoff on 12/7/22.
//

import Foundation

struct Player: Identifiable, Codable, Equatable {
    let name: String
    let wins: Int
    let losses: Int
    let draws: Int
    let gamesPlayed: Int
    let mu: Double
    let sigma: Double
    let id = UUID()
    
    init() {
        self.name = "John Doe"
        self.wins = 10
        self.losses = 3
        self.draws = 5
        self.gamesPlayed = 18
        self.mu = 23.232423434
        self.sigma = 6.2342328732
    }
    
    static func ==(lhs: Player, rhs: Player) -> Bool {
        return lhs.name == rhs.name
    }
    
    enum CodingKeys: String, CodingKey {
        case name, wins, losses, draws, gamesPlayed, mu, sigma
    }
    
    func listViewLabel() -> String {
        return "\(self.name) - W: \(self.wins)  L: \(self.losses)  D: \(self.draws)"
    }
}
