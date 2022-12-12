//
//  DataManager.swift
//  FootskillApp
//
//  Created by Chris Shoff on 12/10/22.
//

import Foundation

class DataManager {
    let rootURL = "http://127.0.0.1:5000"
    
    func getPlayers(callback: @escaping (([Player]) -> Void)) {
        guard let url = URL(string: rootURL) else {
            return
        }
        
        let decoder = JSONDecoder()
        
        let task = URLSession.shared.dataTask(with: url) { data, response, error in
            if let data = data {
                do {
                    let players = try decoder.decode([Player].self, from: data)
                    callback(players)
                } catch {
                    print(error)
                }
            }
        }
        
        task.resume()
    }
    
    func generateTeams(players: [Player], callback: @escaping (([Player], [Player], Double) -> Void)) {
        guard let url = URL(string: "\(rootURL)/generate") else {
            return
        }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Application/json", forHTTPHeaderField: "Content-Type")
        
        let encoder = JSONEncoder()
        let decoder = JSONDecoder()
        
        var encodedPlayers: Data
        do {
            encodedPlayers = try encoder.encode(players)
        } catch {
            print(error)
            return
        }
        
        request.httpBody = encodedPlayers
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let data = data {
                do {
                    let response = try decoder.decode(GeneratedTeams.self, from: data)
                    callback(response.redTeam, response.blueTeam, response.quality)
                } catch {
                    print(error)
                }
            }
        }
        
        task.resume()
    }
}
