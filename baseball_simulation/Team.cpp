//
//  Team.cpp
//  baseball_simulation
//
//  Created by Connor Courtright on 11/13/24.
//

#include "Team.hpp"

Team::Team(string n){
    this->teamName = n;
}

Team::Team(string teamName, vector<Player*> hitters, vector<Player*> spitchers, vector<Player*> rpitchers){
    for(auto p : hitters){
        this->hitters.push_back(p);
    }
    
    for(auto p : spitchers){
        this->startingPitchers.push_back(p);
    }
    
    for(auto p : rpitchers){
        this->reliefPitchers.push_back(p);
    }
        
    this->teamName = teamName;
}

string Team::getTeamName(){
    return this->teamName;
}

// logic is weird; it is returning a lineup of nobodies lmao
/*vector<Player*> Team::setLineup(){
    vector<Player*> lineup;
    
    // starting pitcher is gonna be the one with the highest war/strikeout percentage
    Player* startingPitcher = startingPitchers.at(0);
    for(int i = 1; i < startingPitchers.size(); i++){
        Player* curr = startingPitchers.at(i);
        if(curr > startingPitcher) startingPitcher = curr;
    }
    // starting pitcher always found at index == 0
    lineup.push_back(startingPitcher);
    
    // now we need to find 9 players, sorted by WAR, to put into lineup, all different positions
    vector<bool> visited(hitters.size());
    while(lineup.size() < 10){
        try{
            Player* curr = nullptr;
            int index = -1;
            for(int i = 0; i < hitters.size(); i++){
                if(visited.at(i)) continue;
                if(curr == nullptr){
                    curr = hitters.at(i);
                    continue;
                }
                if(hitters.at(i) > curr) curr = hitters.at(i);
                
                index = i;
            }
            
            visited.at(index) = true;
            
            bool posmatchfound = false;
            for(auto p : lineup){
                if(curr->getPosition() == p->getPosition()){
                    posmatchfound = true;
                    break;
                }
            }
            if(posmatchfound) continue;
            
            lineup.push_back(curr);
        }
        catch(const out_of_range& e){
            cout << "error: " << e.what() << endl;
            return {nullptr};
        }
    }
    
    return lineup;
}*/

vector<Player*> Team::setLineup(){
    vector<Player*> lineup;
    lineup.push_back(startingPitchers.at(0));
    for(int i = 0; i < lineup.size(); i++){
        if(lineup.size() > 10) break;
        lineup.push_back(hitters.at(i));
    }
    return lineup;
}

string Team::toString(){
    stringstream ss;
    ss << this->teamName << endl;
    
    ss << "Position Players: " << endl;
    for(auto p : hitters){
        ss << p->toString();
    }
    
    ss << "\nStarting Pitchers:" << endl;
    for(auto p : startingPitchers){
        ss << p->toString();
    }
    
    ss << "\nRelief Pitchers:" << endl;
    for(auto p : reliefPitchers){
        ss << p->toString();
    }
    
    return ss.str();
}
