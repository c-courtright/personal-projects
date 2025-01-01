//
//  Player.cpp
//  baseball_simulation
//
//  Created by Connor Courtright on 11/13/24.
//

#include "Player.hpp"

Player::Player(){
    this->name = "Joe Random";
    this->team = "Major League Baseball";
}

Player::Player(string name, string team){
    this->name = name;
    this->team = team;
}

string Player::getTeam(){
    return this->team;
}

string Player::getLastName(){
    return this->name.substr(this->name.find(" ") + 1);
}

string Player::getPosition(){
    return "base class position";
}

int Player::getWalks(){
    return -20;
}

int Player::getHBP(){
    return -20;
}

int Player::getHits(){
    return -20;
}

int Player::getHomeruns(){
    return -20;
}

int Player::getStrikeouts(){
    return -20;
}

double Player::getBattingAverage(){
    return -20;
}

int Player::getAtBats(){
    return -20;
}

int Player::getDoubles(){
    return -20;
}

int Player::getTriples(){
    return -20;
}

int Player::getBattersFaced(){
    return -20;
}

string Player::toString(){
    stringstream ss;
    ss << this->name << endl;
    ss << "\tNo more info" << endl;
    return ss.str();
}

void Player::PrintPlayer(){
    cout << this->name << endl;
    cout << "\tNo more info" << endl;
}
