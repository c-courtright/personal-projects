//
//  Pitcher.cpp
//  baseball_simulation
//
//  Created by Connor Courtright on 11/14/24.
//

#include "Pitcher.hpp"

Pitcher::Pitcher(string n){
    name = n;
}

Pitcher::Pitcher(vector<string> v){
    // name,war,hit,homer,walk,strikeouts,hbp,bf,team
    //int hitsA, homerunsA, walksA, strikeouts, hbp, battersFaced;
    //double war;
    string ts = v[0];
    if(ts.find("*") != -1 || ts.find("#") != -1) ts = ts.substr(0, ts.size() - 1);
    name = ts;
    war = stod(v[1]);
    hitsA = stoi(v[2]);
    homerunsA = stoi(v[3]);
    walksA = stoi(v[4]);
    strikeouts = stoi(v[5]);
    hbp = stoi(v[6]);
    battersFaced = stoi(v[7]);
    team = v[8];
}

string Pitcher::getTeam(){
    return Player::getTeam();
}

string Pitcher::getPosition(){
    return "P";
}

int Pitcher::getBattersFaced(){
    return this->battersFaced;
}

int Pitcher::getHits(){
    return this->hitsA;
}

int Pitcher::getHomeruns(){
    return this->homerunsA;
}

int Pitcher::getWalks(){
    return this->walksA;
}

int Pitcher::getStrikeouts(){
    return this->strikeouts;
}

int Pitcher::getHBP(){
    return this->hbp;
}

string Pitcher::toString(){
    stringstream ss;
    ss << name << " (P)" << endl;
    ss << "\tWAR: " << war << endl;
    ss << "\tHits Allowed: " << hitsA << endl;
    ss << "\tHomeruns Allowed: " << homerunsA << endl;
    ss << "\tWalks Allowed: " << walksA << endl;
    ss << "\tStrikeouts: " << strikeouts << endl;
    ss << "\tHit by Pitch: " << hbp << endl;
    ss << "\tBatters Faced: " << battersFaced << endl;
    return ss.str();
}

void Pitcher::PrintPlayer(){
    cout << name << " (P)" << endl;
    cout << "\tWAR: " << war << endl;
    cout << "\tHits Allowed: " << hitsA << endl;
    cout << "\tHomeruns Allowed: " << homerunsA << endl;
    cout << "\tWalks Allowed: " << walksA << endl;
    cout << "\tStrikeouts: " << strikeouts << endl;
    cout << "\tHit by Pitch: " << hbp << endl;
    cout << "\tBatters Faced: " << battersFaced << endl;
}

bool Pitcher::operator<(Pitcher* rhs){
    if(this->war < rhs->war) return true;
    else if(this->war > rhs->war) return false;
    else {
        // strikeout rate used as tiebreaker
        if((this->strikeouts/this->battersFaced) < (rhs->strikeouts/rhs->battersFaced)) return true;
        else return false;
    }
}

bool Pitcher::operator>(Pitcher*  rhs){
    if(this->war > rhs->war) return true;
    else if(this->war < rhs->war) return false;
    else {
        // strikeout rate used as tiebreaker
        if((this->strikeouts/this->battersFaced) > (rhs->strikeouts/rhs->battersFaced)) return true;
        else return false;
    }
}
