//
//  TeamView.swift
//  FootskillApp
//
//  Created by Chris Shoff on 12/13/22.
//

import SwiftUI

struct TeamView: View {
    let team: [String]
    let edge: Edge.Set
    
    var body: some View {
        VStack {
            ForEach(team, id: \.self, content: { name in
                Text("\(name)")
                    .frame(maxWidth: .infinity, alignment: edge == .leading ? .leading : .trailing)
                    .padding(edge, 20)
                    .padding(.top, 3)
                    .foregroundColor(edge == .leading ? .red : .blue)
            })
        }
    }
}

struct TeamView_Previews: PreviewProvider {
    static var previews: some View {
        TeamView(team: ["Chris", "Jim", "Ed"], edge: .leading)
    }
}
