//
//  Pitcher.hpp
//  baseball_simulation
//
//  Created by Connor Courtright on 11/14/24.
//

#ifndef Pitcher_hpp
#define Pitcher_hpp

#include "Player.hpp"

#include <iostream>
#include <stdio.h>
#include <vector>

class Pitcher : public Player {
protected:
    int hitsA, homerunsA, walksA, strikeouts, hbp, battersFaced;
    double war;
    
public:
    Pitcher(string n);
    Pitcher(vector<string> v);
    
    string getTeam();
    string getPosition() override;
    int getBattersFaced() override;
    int getHits() override;
    int getHomeruns() override;
    int getWalks() override;
    int getStrikeouts() override;
    int getHBP() override;
    
    string toString() override;
    void PrintPlayer() override;
    
    bool operator<(Pitcher* rhs);
    bool operator>(Pitcher* rhs);
};

#endif /* Pitcher_hpp */
