//
//  PickResultView.swift
//  FootskillApp
//
//  Created by Chris Shoff on 12/14/22.
//

import SwiftUI

struct PickResultView: View {
    let pickResultCallback: (Result) -> Void
    
    var body: some View {
        HStack {
            Button {
                pickResultCallback(.red)
            } label: {
                Text("Winner?")
                    .frame(width: 80, height: 30)
                    .foregroundColor(.white)
                    .background(.red)
                    .padding(.leading, 20)
                    .padding(.top, 20)
            }
            Spacer()
            Button {
                pickResultCallback(.balanced)
            } label: {
                Text("Balanced?")
                    .frame(width: 90, height: 30)
                    .foregroundColor(.white)
                    .background(.gray)
                    .padding(.top, 20)
            }
            Spacer()
            Button {
                pickResultCallback(.blue)
            } label: {
                Text("Winner?")
                    .frame(width: 80, height: 30)
                    .foregroundColor(.white)
                    .background(.blue)
                    .padding(.trailing, 20)
                    .padding(.top, 20)
            }
        }
    }
}

struct PickResultView_Previews: PreviewProvider {
    static var previews: some View {
        PickResultView(pickResultCallback: { _ in })
    }
}
