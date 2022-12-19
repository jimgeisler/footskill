//
//  ResultBadge.swift
//  FootskillApp
//
//  Created by Chris Shoff on 12/13/22.
//

import SwiftUI

struct ResultBadge: View {
    let result: Result
    
    var body: some View {
        if (result == .blue || result == .red) {
            if (result == .blue) {
                Spacer()
            }
            Text("Winner")
                .frame(width: 80, height: 30)
                .foregroundColor(.white)
                .background(result == .blue ? .blue : .red)
                .padding(result == .blue ? .trailing : .leading, 20)
                .padding(.top, 20)
            if (result == .red) {
                Spacer()
            }
        } else {
            Text("Balanced")
                .frame(width: 90, height: 30)
                .foregroundColor(.white)
                .background(.gray)
                .padding(.top, 20)
        }
    }
}

struct ResultBadge_Previews: PreviewProvider {
    static var previews: some View {
        ResultBadge(result: .red)
    }
}
