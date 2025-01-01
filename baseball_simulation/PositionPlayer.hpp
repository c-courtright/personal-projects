//
//  PositionPlayer.hpp
//  baseball_simulation
//
//  Created by Connor Courtright on 11/14/24.
//

#ifndef PositionPlayer_hpp
#define PositionPlayer_hpp

#include "Player.hpp"

#include <stdio.h>
#include <iostream>
#include <vector>

class PositionPlayer : public Player {
protected:
    string position;
    int games, atbats, hits, doubles, triples, homeruns, walks, strikeouts, hbp;
    double war, average, obp, slug;
    
public:
    PositionPlayer(string n);
    PositionPlayer(vector<string> v);
    
    string getTeam();
    string getLastName();
    string getPosition() override;
    double getBattingAverage() override;
    int getWalks() override;
    int getHBP() override;
    int getAtBats() override;
    int getHits() override;
    int getDoubles() override;
    int getTriples() override;
    int getHomeruns() override;
    
    string toString() override;
    void PrintPlayer() override;
    
    bool operator<(PositionPlayer* rhs);
    bool operator>(PositionPlayer* rhs);
};

#endif /* PositionPlayer_hpp */
