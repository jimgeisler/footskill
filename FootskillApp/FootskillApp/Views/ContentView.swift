//
//  ContentView.swift
//  FootskillApp
//
//  Created by Chris Shoff on 12/6/22.
//

import SwiftUI

struct ContentView: View {
    let dataManager = DataManager()
    
    var body: some View {
        TabView {
            PlayerList(dataManager: dataManager)
            .tabItem {
               Image(systemName: "person.fill")
               Text("Players")
             }
            GameList(dataManager: dataManager)
            .tabItem {
               Image(systemName: "soccerball")
               Text("Games")
             }
        }
    }
    
    
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
