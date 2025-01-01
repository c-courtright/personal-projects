//
//  PositionPlayer.cpp
//  baseball_simulation
//
//  Created by Connor Courtright on 11/14/24.
//

#include "PositionPlayer.hpp"

PositionPlayer::PositionPlayer(string n){
    name = n;
}

PositionPlayer::PositionPlayer(vector<string> v){
    // name,pos,games,war,atbats,hits,doubles,triples,homers,walks,strikeouts,average,obp,slug,hbp,team
    //string name, position;
    //int games, atbats, hits, doubles, triples, homeruns, walks, strikeouts, hbp;
    //double war, average, obp, slug;
    
    string ts = v[0];
    if(ts.find("*") != -1 || ts.find("#") != -1) ts = ts.substr(0, ts.size() - 1);
    name = ts;
    position = v[1];
    games = stoi(v[2]);
    war = stod(v[3]);
    atbats = stoi(v[4]);
    hits = stoi(v[5]);
    doubles = stoi(v[6]);
    triples = stoi(v[7]);
    homeruns = stoi(v[8]);
    walks = stoi(v[9]);
    strikeouts = stoi(v[10]);
    average = stod(v[11]);
    obp = stod(v[12]);
    slug = stod(v[13]);
    hbp = stoi(v[14]);
    team = v[15];
}

string PositionPlayer::getTeam(){
    return Player::getTeam();
}

string PositionPlayer::getLastName(){
    return Player::getLastName();
}

string PositionPlayer::getPosition(){
    return this->position;
}

int PositionPlayer::getHits(){
    return this->hits;
}

int PositionPlayer::getDoubles(){
    return this->doubles;
}

int PositionPlayer::getTriples(){
    return this->triples;
}

int PositionPlayer::getHomeruns(){
    return this->homeruns;
}

double PositionPlayer::getBattingAverage(){
    return this->average;
}

int PositionPlayer::getWalks(){
    return this->walks;
}

int PositionPlayer::getHBP(){
    return this->hbp;
}

int PositionPlayer::getAtBats(){
    return this->atbats;
}

string PositionPlayer::toString(){
    stringstream ss;
    ss << name << " (" << position << ")" << endl;
    ss << "\tGames Played: " << games << endl;
    ss << "\tWAR: " << war << endl;
    ss << "\tAt-Bats: " << atbats << endl;
    ss << "\tHits: " << hits << endl;
    ss << "\tDoubles: " << doubles << endl;
    ss << "\tTriples: " << triples << endl;
    ss << "\tHome Runs: " << homeruns << endl;
    ss << "\tWalks: " << walks << endl;
    ss << "\tStrikeouts: " << strikeouts << endl;
    ss << "\tBatting Average: " << average << endl;
    ss << "\tOn-Base Percentage: " << obp << endl;
    ss << "\tSlugging Percentage: " << slug << endl;
    ss << "\tHit by Pitch: " << hbp << endl;
    return ss.str();
}

void PositionPlayer::PrintPlayer(){
    cout << name << " (" << position << ")" << endl;
    cout << "\tGames Played: " << games << endl;
    cout << "\tWAR: " << war << endl;
    cout << "\tAt-Bats: " << atbats << endl;
    cout << "\tHits: " << hits << endl;
    cout << "\tDoubles: " << doubles << endl;
    cout << "\tTriples: " << triples << endl;
    cout << "\tHome Runs: " << homeruns << endl;
    cout << "\tWalks: " << walks << endl;
    cout << "\tStrikeouts: " << strikeouts << endl;
    cout << "\tBatting Average: " << average << endl;
    cout << "\tOn-Base Percentage: " << obp << endl;
    cout << "\tSlugging Percentage: " << slug << endl;
    cout << "\tHit by Pitch: " << hbp << endl;
}

bool PositionPlayer::operator<(PositionPlayer* rhs){
    if(this->war < rhs->war) return true;
    else if(this->war > rhs->war) return false;
    else {
        // ops used as tiebreaker
        if((this->obp + this->slug) < (rhs->obp + rhs->slug)) return true;
        else return false;
    }
}

bool PositionPlayer::operator>(PositionPlayer* rhs){
    if(this->war > rhs->war) return true;
    else if(this->war < rhs->war) return false;
    else {
        // ops used as tiebreaker
        if((this->obp + this->slug) > (rhs->obp + rhs->slug)) return true;
        else return false;
    }
}
