//
//  Player.hpp
//  baseball_simulation
//
//  Created by Connor Courtright on 11/13/24.
//

#ifndef Player_hpp
#define Player_hpp

#include <stdio.h>
#include <iostream>
#include <sstream>

// abstract class
using namespace std;

class Player{
protected:
    string name, team;
    
public:
    Player();
    Player(string name, string team);
    
    string getTeam();
    string getLastName();
    virtual string getPosition();
    
    // universal getters
    virtual int getWalks();
    virtual int getHBP();
    virtual int getHits();
    virtual int getHomeruns();
    virtual int getStrikeouts();

    // pos player getters
    virtual double getBattingAverage();
    virtual int getAtBats();
    virtual int getDoubles();
    virtual int getTriples();
    
    // pitcher getters
    virtual int getBattersFaced();

    
    virtual void PrintPlayer();
    virtual string toString();
    
    //virtual bool operator<(const Player* rhs);
    //virtual bool operator>(const Player* rhs);
    bool operator==(const Player* rhs){
        return this->name == rhs->name;
    }
};

#endif /* Player_hpp */
