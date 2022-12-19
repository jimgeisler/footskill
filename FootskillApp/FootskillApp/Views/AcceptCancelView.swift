//
//  AcceptCancelView.swift
//  FootskillApp
//
//  Created by Chris Shoff on 12/14/22.
//

import SwiftUI

struct AcceptCancelView: View {
    let commitAction: () -> Void
    let cancelAction: () -> Void
    var body: some View {
        HStack {
            Button {
                commitAction()
            } label: {
                Text("Accept")
            }
            .buttonStyle(.borderedProminent)
            .padding()
            Button {
                cancelAction()
            } label: {
                Text("Cancel")
            }
            .buttonStyle(.bordered)
            .padding()
        }
    }
}

struct AcceptCancelView_Previews: PreviewProvider {
    static var previews: some View {
        AcceptCancelView {
        } cancelAction: {
        }
    }
}
