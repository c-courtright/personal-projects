//
//  Team.hpp
//  baseball_simulation
//
//  Created by Connor Courtright on 11/13/24.
//

#ifndef Team_hpp
#define Team_hpp

#include "Player.hpp"
#include "PositionPlayer.hpp"
#include "Pitcher.hpp"

#include <stdio.h>
#include <iostream>
#include <vector>
#include <sstream>

using namespace std;

class Team{
protected:
    string teamName;
    
    vector<Player*> hitters;
    vector<Player*> reliefPitchers;
    vector<Player*> startingPitchers;
public:
    Team(string teamName);
    Team(string teamName, vector<Player*> hitters, vector<Player*> spitchers, vector<Player*> rpitchers);
    
    vector<Player*> setLineup();
    
    string getTeamName();
    string toString();
    
    Player* operator[](int i);
};

#endif /* Team_hpp */
