//
//  Game.swift
//  FootskillApp
//
//  Created by Chris Shoff on 12/13/22.
//

import Foundation

enum Result: String, Codable {
    case red = "Red"
    case blue = "Blue"
    case balanced = "Balanced"
    case noResult = "No Result"
    case pending = "Pending"
    case new = "New"
}

struct Game: Codable, Identifiable {
    let date: String
    let redTeam: [String]
    let blueTeam: [String]
    var result: Result
    let id = UUID()
    
    enum CodingKeys : CodingKey {
        case date, redTeam, blueTeam, result
    }
    
    init(date: String, redTeam: [String], blueTeam: [String], result: Result) {
        self.date = date
        self.redTeam = redTeam
        self.blueTeam = blueTeam
        self.result = result
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.date = try container.decode(String.self, forKey: .date)
        self.redTeam = try container.decode([String].self, forKey: .redTeam)
        self.blueTeam = try container.decode([String].self, forKey: .blueTeam)
        
        let resultString = try container.decode(String.self, forKey: .result)
        
        guard let result = Result(rawValue: resultString) else {
            self.result = .noResult
            return
        }
        
        self.result = result
    }
}
