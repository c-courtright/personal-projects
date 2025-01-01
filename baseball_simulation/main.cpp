//
//  main.cpp
//  baseball_simulation
//
//  Created by Connor Courtright on 11/13/24.
//

#include <iostream>
#include <fstream>
#include <cstdlib>
#include <ctime>

#include "Team.hpp"
#include "Player.hpp"
#include "PositionPlayer.hpp"
#include "Pitcher.hpp"

using namespace std;

const string linebreak = "--------------------------------";

// HOMERUN PROBLEM!!!!!
// as of 12/31/24 @ 11:08pm

enum Runner
{
    first = 1,
    second = 2,
    third = 3,
    scored = 4
};

Runner operator+(Runner lhs, int rhs){
    if(rhs == 1){
        if(lhs == first) return second;
        else if(lhs == second) return third;
        else return scored;
    } else if(rhs == 2){
        if(lhs == first) return third;
        else return scored;
    } else return scored;
}

Runner operator+=(Runner lhs, int rhs){
    if(rhs == 1){
        if(lhs == first) return second;
        else if(lhs == second) return third;
        else return scored;
    } else if(rhs == 2){
        if(lhs == first) return third;
        else return scored;
    } else return scored;
}

// read in csv file with lots of players, data will be formatted as:
// playerName, teamName, jerseyNumber, position
// and then after that it deviates depending on type of player

// then will have unique stats depending on their whole thing:
// pitchers will have era, strikeout percentage, etc
// batters will have batting average, slugging, obp, etc
Team* createTeam(string hitterfile, string spitcherfile, string rpitcherfile){
    
    string teamName;
    vector<Player*> hitters, spitchers, rpitchers;
    
    // hitter data comes in csv in form of:
    // name,pos,games,war,atbats,hits,doubles,triples,homers,walks,strikeouts,average,obp,slug,hbp,team
    fstream fin;
    fin.open(hitterfile);
    if(!fin.is_open()){
        cout << "error opening hitter file" << endl;
        return nullptr;
    }
    string s;
    // extra write to get around column names
    getline(fin, s);
    getline(fin, s);
    while(!fin.eof()){
        s += ",";
        vector<string> tv;
        while(s.size() > 0){
            string tempstr = s.substr(0, s.find(","));
            if(tempstr.find("\"") != -1){
                tempstr = tempstr.substr(1, tempstr.size() - 2);
            }
            tv.push_back(tempstr);
            s = s.substr(s.find(",") + 1);
        }
        
        tv.erase(tv.begin());
        Player* newPlayer = new PositionPlayer(tv);
        if(teamName == "") teamName = newPlayer->getTeam();
        hitters.push_back(newPlayer);
        
        getline(fin, s);
    }
    fin.close();
    
    
    
    // starting pitcher data comes in csv in form of:
    // name,war,hit,homer,walk,strikeouts,hbp,bf,team
    fin.open(spitcherfile);
    if(!fin.is_open()){
        cout << "error opening starting pitcher file";
        return nullptr;
    }
    // extra write to get around column names
    getline(fin, s);
    getline(fin, s);
    while(!fin.eof()){
        s += ",";
        vector<string> tv;
        while(s.size() > 0){
            string tempstr = s.substr(0, s.find(","));
            if(tempstr.find("\"") != -1){
                tempstr = tempstr.substr(1, tempstr.size() - 2);
            }
            tv.push_back(tempstr);
            s = s.substr(s.find(",") + 1);
        }
        
        tv.erase(tv.begin());
        Player* newPlayer = new Pitcher(tv);
        spitchers.push_back(newPlayer);
        
        getline(fin, s);
    }
    fin.close();
    


    //relief pitchers come in same format as starting pitchers
    fin.open(rpitcherfile);
    if(!fin.is_open()){
        cout << "error opening starting pitcher file";
        return nullptr;
    }
    // extra write to get around column names
    getline(fin, s);
    getline(fin, s);
    while(!fin.eof()){
        s += ",";
        vector<string> tv;
        while(s.size() > 0){
            string tempstr = s.substr(0, s.find(","));
            if(tempstr.find("\"") != -1){
                tempstr = tempstr.substr(1, tempstr.size() - 2);
            }
            tv.push_back(tempstr);
            s = s.substr(s.find(",") + 1);
        }
        
        tv.erase(tv.begin());
        Player* newPlayer = new Pitcher(tv);
        rpitchers.push_back(newPlayer);
        
        getline(fin, s);
    }
    fin.close();

    
    Team* newTeam = new Team(teamName, hitters, spitchers, rpitchers);
    return newTeam;
}

void simulategame(Team* homeTeam, Team* awayTeam){
    vector<Player*> home = homeTeam->setLineup();
    int runsHome = 0;
    vector<Player*> away = awayTeam->setLineup();
    int runsAway = 0;
    
    Player* homePitcher = home[0];
    Player* awayPitcher = home[0];
    
    int halfInningsPlayed = 0;
    int currBatterHome = 1;
    int currBatterAway = 1;
    bool top = true;
    while(halfInningsPlayed < 18){
        
        if(halfInningsPlayed == 17 && runsHome > runsAway) break;
        
        vector<Runner> activeRunners;
        
        cout << linebreak << endl;
        cout << "Now onto the";
        if(top) cout << " top of the ";
        else cout << " bottom of the ";
        cout << ((halfInningsPlayed / 2) + 1) << "th inning." << endl;
        
        cout << "On the mound for the ";
        if(top) cout << homeTeam->getTeamName();
        else cout << awayTeam->getTeamName();
        cout << " is ";
        Player* currPitcher;
        if(top) currPitcher = homePitcher;
        else currPitcher = awayPitcher;
        cout << currPitcher->getLastName() << endl;
        
        int currHitterIndex;
        vector<Player*> hittingTeam;
        if(top) {
            hittingTeam = away;
            currHitterIndex = currBatterAway;
        } else {
            hittingTeam = home;
            currHitterIndex = currBatterHome;
        }
        
        int outs = 0;
        int multiplier = 1;
        while(outs < 3){
            Player* currHitter = hittingTeam.at(currHitterIndex);
            cout << "Up to bat: " << currHitter->getLastName() << endl;
            
            
            // first layer: hit, out, or walk
            double hitterHitCont = currHitter->getBattingAverage();
            double pitcherHitCont = currPitcher->getHits() / currPitcher->getBattersFaced();
            //double hitavg = (hitterHitCont + pitcherHitCont) / 2;
            double hitavg = (0.75*hitterHitCont) + (0.25*pitcherHitCont);
            hitavg *= multiplier;
            
            double hitterWalkCont = double(currHitter->getHBP() + currHitter->getWalks()) / double(currHitter->getAtBats());
            double pitcherWalkCont = double(currPitcher->getHBP() + currPitcher->getWalks()) / double(currPitcher->getBattersFaced());
            double walkavg = (hitterWalkCont + pitcherWalkCont) / 2;
            //cout << "hitterWalkCont: " << hitterWalkCont << endl;
            //cout << "pitcherWalkCont: " << pitcherWalkCont << endl;
            //cout << "walkavg: " << walkavg << endl;
            
            double hitterOutCont = 1 - currHitter->getBattingAverage();
            double pitcherOutCont = double(currPitcher->getStrikeouts() + currPitcher->getBattersFaced() - currPitcher->getHits()) / double(currPitcher->getBattersFaced());
            double outavg = (hitterOutCont + pitcherOutCont) / 2;
            
            double sum = hitavg + walkavg + outavg;
            double hit = 100 * (hitavg / sum);
            double walk = 100 * (walkavg / sum);
            double out = 100 * (outavg / sum);
            
            double result = rand() % 100;
            //cout << "chances of hit: " << hit << endl;
            //cout << "chances of walk: " << walk << endl;
            //cout << "chances of out: " << out << endl;
            //cout << "result: " << result << endl;
            int runsScored = 0;
            if(result < hit){
                if(multiplier <= 3) multiplier++;
                // result of at bat was hit
                //cout << "# of hits: " << currHitter->getHits() << endl;
                //cout << "# of doubles: " << currHitter->getDoubles() << endl;
                //cout << "# of triples: " << currHitter->getTriples() << endl;
                //cout << "# of homeruns: " << currHitter->getHomeruns() << endl;
                double singleavg = double(currHitter->getHits() - currHitter->getDoubles() - currHitter->getTriples() - currHitter->getHomeruns()) / double(currHitter->getHits());
                double doubleavg = double(currHitter->getDoubles()) / double(currHitter->getHits());
                double tripleavg = double(currHitter->getTriples()) / double(currHitter->getHits());
                
                double hitterHomerunCont = double(currHitter->getHomeruns()) / double(currHitter->getHits());
                double pitcherHomerunCont = double(currPitcher->getHomeruns()) / double(currPitcher->getBattersFaced());
                double homerunavg = (hitterHomerunCont + pitcherHomerunCont) / 2.0;
                
                double sum = singleavg + doubleavg + tripleavg + homerunavg;
                double single = 100 * (singleavg / sum);
                double doble = 100 * (doubleavg / sum);
                double triple = 100 * (tripleavg / sum);
                
                //cout << "chances of single: " << single << endl;
                //cout << "chances of double: " << doble << endl;
                //cout << "chances of triple: " << triple << endl;
                //cout << "chances of homerun: " << 100*(homerunavg/sum) << endl;
                
                result = rand() % 100;
                //cout << "result: " << endl;
                if(result < single){
                    // single
                    cout << currHitter->getLastName() << " knocks a single." << endl;
                    for(int i = 0; i < activeRunners.size(); i++){
                        activeRunners.at(i) = activeRunners.at(i) + 1;
                        if(activeRunners.at(i) == scored){
                            runsScored++;
                            activeRunners.erase(activeRunners.begin() + i);
                            i--;
                        }
                    }
                    activeRunners.push_back(first);
                } else if(result < (single+doble)){
                    // double
                    cout << currHitter->getLastName() << " hits a double." << endl;
                    for(int i = 0; i < activeRunners.size(); i++){
                        activeRunners.at(i) = activeRunners.at(i) + 2;
                        if(activeRunners.at(i) == scored){
                            runsScored++;
                            activeRunners.erase(activeRunners.begin() + i);
                            i--;
                        }
                    }
                    activeRunners.push_back(second);
                } else if(result < (single+doble+triple)){
                    // triple
                    cout << currHitter->getLastName() << " crushed a triple." << endl;
                    for(int i = 0; i < activeRunners.size(); i++){
                        activeRunners.at(i) = activeRunners.at(i) + 3;
                        if(activeRunners.at(i) == scored){
                            runsScored++;
                            activeRunners.erase(activeRunners.begin() + i);
                            i--;
                        }
                    }
                    activeRunners.push_back(third);
                } else {
                    // homerun
                    cout << "Homerun!!!!!!" << endl;
                    runsScored += activeRunners.size() + 1;
                    activeRunners.clear();
                }
            } else if(result < (hit + walk)){
                // result of at bat was walk
                cout << currHitter->getLastName() << " walks." << endl;
                if(activeRunners.size() != 0){
                    Runner benchmark = first;
                    for(int i = int(activeRunners.size() - 1); i >= 0; i--){
                        if(activeRunners.at(i) == benchmark){
                            activeRunners.at(i) = activeRunners.at(i) + 1;
                            benchmark = benchmark + 1;
                        } else break;
                    }
                    if(benchmark == scored) runsScored++;
                }
                activeRunners.push_back(first);
            } else {
                // result of at bat was out
                double hitterKCont = currHitter->getStrikeouts() / currHitter->getAtBats();
                double pitcherKCont = currPitcher->getStrikeouts() / currPitcher->getBattersFaced();
                double strikeoutavg = (hitterKCont + pitcherKCont) / 2;
                
                double strikeout = 100 * strikeoutavg;
                
                result = rand() % 100;
                if(result < strikeout){
                    //strikeout
                    cout << currPitcher->getLastName() << " strikes out " << currHitter->getLastName() << "." << endl;
                } else {
                    // hit out
                    cout << currHitter->getLastName() << " hits out." << endl;
                }
                
                outs++;
            }
            
            //cout << linebreak << endl;
            /*cout << "active runners: ";
            if(activeRunners.size() == 0) cout << "size of zero";
            else for(Runner r : activeRunners) cout << r << ",";
            cout << endl;*/
            
            if(top){
                cout << awayTeam->getTeamName() << " scores " << runsScored << " run(s) on the play!" << endl;
                runsAway += runsScored;
            } else {
                cout << homeTeam->getTeamName() << " scores " << runsScored << " runs(s) on the play!" << endl;
                runsHome += runsScored;
            }
            
            currHitterIndex++;
            if(currHitterIndex > 9) currHitterIndex = 1;
        }
        
        halfInningsPlayed++;
        top = !top;
    }
    
    cout << "Final Score:" << endl;
    cout << awayTeam->getTeamName() << ": " << runsAway << endl;
    cout << homeTeam->getTeamName() << ": " << runsHome << endl;
    
    if(runsAway > runsHome) cout << "Congratulations to the " << awayTeam->getTeamName() << " on the win!" << endl;
    else if(runsAway < runsHome) cout << "Congratulations to the " << homeTeam->getTeamName() << " on the win!" << endl;
    else cout << "Result is a tie." << endl;
}

Team* simulategameNoTextWithReturn(Team* homeTeam, Team* awayTeam){
    vector<Player*> home = homeTeam->setLineup();
    int runsHome = 0;
    vector<Player*> away = awayTeam->setLineup();
    int runsAway = 0;
    
    Player* homePitcher = home[0];
    Player* awayPitcher = home[0];
    
    int halfInningsPlayed = 0;
    int currBatterHome = 1;
    int currBatterAway = 1;
    bool top = true;
    while(halfInningsPlayed < 18){
        
        if(halfInningsPlayed == 17 && runsHome > runsAway) break;
        
        //cout << linebreak << endl;
        //cout << "Now onto the";
        //if(top) cout << " top of the ";
        //else cout << " bottom of the ";
        //cout << ((halfInningsPlayed / 2) + 1) << "th inning." << endl;
        
        //cout << "On the mound for the ";
        //if(top) cout << homeTeam->getTeamName();
        //else cout << awayTeam->getTeamName();
        //cout << " is ";
        Player* currPitcher;
        if(top) currPitcher = homePitcher;
        else currPitcher = awayPitcher;
        //cout << currPitcher->getLastName() << endl;
        
        int currHitterIndex;
        vector<Player*> hittingTeam;
        if(top) {
            hittingTeam = away;
            currHitterIndex = currBatterAway;
        } else {
            hittingTeam = home;
            currHitterIndex = currBatterHome;
        }
        
        int outs = 0;
        int multiplier = 1;
        while(outs < 3){
            Player* currHitter = hittingTeam.at(currHitterIndex);
            //cout << "Up to bat: " << currHitter->getLastName() << endl;
            vector<Runner> activeRunners;
            
            // first layer: hit, out, or walk
            double hitterHitCont = currHitter->getBattingAverage();
            double pitcherHitCont = currPitcher->getHits() / currPitcher->getBattersFaced();
            //double hitavg = (hitterHitCont + pitcherHitCont) / 2;
            double hitavg = (0.75*hitterHitCont) + (0.25*pitcherHitCont);
            hitavg *= multiplier;
            
            double hitterWalkCont = double(currHitter->getHBP() + currHitter->getWalks()) / double(currHitter->getAtBats());
            double pitcherWalkCont = double(currPitcher->getHBP() + currPitcher->getWalks()) / double(currPitcher->getBattersFaced());
            double walkavg = (hitterWalkCont + pitcherWalkCont) / 2;
            //cout << "hitterWalkCont: " << hitterWalkCont << endl;
            //cout << "pitcherWalkCont: " << pitcherWalkCont << endl;
            //cout << "walkavg: " << walkavg << endl;
            
            double hitterOutCont = 1 - currHitter->getBattingAverage();
            double pitcherOutCont = double(currPitcher->getStrikeouts() + currPitcher->getBattersFaced() - currPitcher->getHits()) / double(currPitcher->getBattersFaced());
            double outavg = (hitterOutCont + pitcherOutCont) / 2;
            
            double sum = hitavg + walkavg + outavg;
            double hit = 100 * (hitavg / sum);
            double walk = 100 * (walkavg / sum);
            double out = 100 * (outavg / sum);
            
            double result = rand() % 100;
            //cout << "chances of hit: " << hit << endl;
            //cout << "chances of walk: " << walk << endl;
            //cout << "chances of out: " << out << endl;
            //cout << "result: " << result << endl;
            int runsScored = 0;
            if(result < hit){
                if(multiplier <= 3) multiplier++;
                // result of at bat was hit
                //cout << "# of hits: " << currHitter->getHits() << endl;
                //cout << "# of doubles: " << currHitter->getDoubles() << endl;
                //cout << "# of triples: " << currHitter->getTriples() << endl;
                //cout << "# of homeruns: " << currHitter->getHomeruns() << endl;
                double singleavg = double(currHitter->getHits() - currHitter->getDoubles() - currHitter->getTriples() - currHitter->getHomeruns()) / double(currHitter->getHits());
                double doubleavg = double(currHitter->getDoubles()) / double(currHitter->getHits());
                double tripleavg = double(currHitter->getTriples()) / double(currHitter->getHits());
                
                double hitterHomerunCont = double(currHitter->getHomeruns()) / double(currHitter->getHits());
                double pitcherHomerunCont = double(currPitcher->getHomeruns()) / double(currPitcher->getBattersFaced());
                double homerunavg = (hitterHomerunCont + pitcherHomerunCont) / 2.0;
                
                double sum = singleavg + doubleavg + tripleavg + homerunavg;
                double single = 100 * (singleavg / sum);
                double doble = 100 * (doubleavg / sum);
                double triple = 100 * (tripleavg / sum);
                
                //cout << "chances of single: " << single << endl;
                //cout << "chances of double: " << doble << endl;
                //cout << "chances of triple: " << triple << endl;
                //cout << "chances of homerun: " << 100*(homerunavg/sum) << endl;
                
                result = rand() % 100;
                //cout << "result: " << endl;
                if(result < single){
                    // single
                    //cout << currHitter->getLastName() << " knocks a single." << endl;
                    cout << "active runners: ";
                    for(auto r : activeRunners) cout << ", " << r << endl;
                    for(auto r : activeRunners) r = r + 1;
                    for(int i = 0; i < activeRunners.size(); i++){
                        if(activeRunners.at(i) == scored){
                            runsScored++;
                            activeRunners.erase(activeRunners.begin() + i);
                            i--;
                        } else break;
                    }
                    activeRunners.push_back(first);
                } else if(result < (single+doble)){
                    // double
                    //cout << currHitter->getLastName() << " hits a double." << endl;
                    for(auto r : activeRunners) r = r + 2;
                    for(int i = 0; i < activeRunners.size(); i++){
                        if(activeRunners.at(i) == scored){
                            runsScored++;
                            activeRunners.erase(activeRunners.begin() + i);
                            i--;
                        } else break;
                    }
                    activeRunners.push_back(second);
                } else if(result < (single+doble+triple)){
                    // triple
                    //cout << currHitter->getLastName() << " crushes a triple." << endl;
                    for(auto r : activeRunners) r = r + 3;
                    for(int i = 0; i < activeRunners.size(); i++){
                        if(activeRunners.at(i) == scored){
                            runsScored++;
                            activeRunners.erase(activeRunners.begin() + i);
                            i--;
                        } else break;
                    }
                    activeRunners.push_back(third);
                } else {
                    // homerun
                    //cout << "Homerun!!!!!!" << endl;
                    runsScored += activeRunners.size() + 1;
                    activeRunners.clear();
                }
            } else if(result < (hit + walk)){
                // result of at bat was walk
                //cout << currHitter->getLastName() << " walks." << endl;
                if(activeRunners.size() != 0){
                    Runner benchmark = first;
                    for(int i = int(activeRunners.size()); i >= 0; i--){
                        if(activeRunners.at(i) == benchmark){
                            activeRunners.at(i) = activeRunners.at(i) + 1;
                            benchmark = benchmark + 1;
                        } else break;
                    }
                    if(benchmark == scored) runsScored++;
                    activeRunners.push_back(first);
                }
            } else {
                // result of at bat was out
                double hitterKCont = currHitter->getStrikeouts() / currHitter->getAtBats();
                double pitcherKCont = currPitcher->getStrikeouts() / currPitcher->getBattersFaced();
                double strikeoutavg = (hitterKCont + pitcherKCont) / 2;
                
                double strikeout = 100 * strikeoutavg;
                
                result = rand() % 100;
                if(result < strikeout){
                    //strikeout
                    //cout << currPitcher->getLastName() << " strikes out " << currHitter->getLastName() << "." << endl;
                } else {
                    // hit out
                    //cout << currHitter->getLastName() << " hits out." << endl;
                }
                
                outs++;
            }
            
            if(top){
                //cout << awayTeam->getTeamName() << " scores " << runsScored << " run(s) on the play!" << endl;
                runsAway += runsScored;
            } else {
                //cout << homeTeam->getTeamName() << " scores " << runsScored << " runs(s) on the play!" << endl;
                runsHome += runsScored;
            }
            
            currHitterIndex++;
            if(currHitterIndex > 9) currHitterIndex = 1;
        }
        
        halfInningsPlayed++;
        top = !top;
    }
    
    //cout << "Final Score:" << endl;
    //cout << awayTeam->getTeamName() << ": " << runsAway << endl;
    //cout << homeTeam->getTeamName() << ": " << runsHome << endl;

    if(runsAway > runsHome){
        //cout << "Congratulations to the " << awayTeam->getTeamName() << " on the win!" << endl;
        return awayTeam;
    } else if(runsAway < runsHome) {
        //cout << "Congratulations to the " << homeTeam->getTeamName() << " on the win!" << endl;
        return homeTeam;
    } else {
        //cout << "Result is a tie." << endl;
        return nullptr;
    }
}

ostream& operator<<(ostream& os, Team* t){
    os << t->toString();
    return os;
}

ostream& operator<<(ostream& os, Runner r){
    if(r == first) os << "first";
    else if(r == second) os << "second";
    else if(r == third) os << "third";
    else os << "scored";
    return os;
}

int main(int argc, const char * argv[]) {
    
    /*Runner r1 = third;
    Runner r2 = second;
    Runner r3 = first;
    vector<Runner> v = {r1, r2, r3};
    cout << linebreak << endl << "bases before:";
    for(auto r : v) cout << r << ",";
    cout << endl << linebreak;
    int runsScored = 0;
    for(int i = 0; i < v.size(); i++){
        cout << "old runner value: " << v.at(i) << endl;
        v.at(i) = v.at(i) + 2;
        cout << "new runner value: " << v.at(i) << endl;
        if(v.at(i) == scored){
            runsScored++;
            v.erase(v.begin() + i);
            i--;
        }
    }
    cout << "runs scored: " << runsScored << endl;
    cout << "bases after:";
    for(auto r : v) cout << r << ",";
    cout << endl;
    
    return 0;*/
    
    srand(static_cast<unsigned int>(time(0)));
    
    if(argc != 7){
        cout << "Usage: ./a.out f1.csv f2.csv f3.csv f4.csv f5.csv f6.csv" << endl;
        cout << "argc = " << argc << endl;
        return 1;
    }
    
    const string FilePrefix = "/Users/connorcourtright/Desktop/personal/baseball_simulation/baseball_simulation/input files/";
    
    string t1hitters = FilePrefix + argv[1];
    string t1starters = FilePrefix + argv[2];
    string t1bullpen = FilePrefix + argv[3];
    
    string t2hitters = FilePrefix + argv[4];
    string t2starters = FilePrefix + argv[5];
    string t2bullpen = FilePrefix + argv[6];
    
    //return 0;
        
    Team* astros = createTeam(t1hitters, t1starters, t1bullpen);
    Team* dodgers = createTeam(t2hitters, t2starters, t2bullpen);
    
    simulategame(astros, dodgers);
    
    /*int astrosWins = 0;
    int dodgersWins = 0;
    int ties = 0;
    while(ties < 100){
        Team* result = simulategameNoTextWithReturn(astros, dodgers);
        if(result == astros) astrosWins++;
        else if(result == dodgers) dodgersWins++;
        else ties++;
    }
    cout << linebreak << endl;
    cout << "Astros: " << astrosWins << endl;
    cout << "Dodgers: " << dodgersWins << endl;
    cout << "Ties: " << ties << endl;
    cout << linebreak << endl;
    
    astrosWins = 0;
    dodgersWins = 0;
    ties = 0;
    while(ties < 100){
        Team*result = simulategameNoTextWithReturn(dodgers, astros);
        if(result == astros) astrosWins++;
        else if(result == dodgers) dodgersWins++;
        else ties++;
    }
    cout << linebreak << endl;
    cout << "Astros: " << astrosWins << endl;
    cout << "Dodgers: " << dodgersWins << endl;
    cout << "Ties: " << ties << endl;
    cout << linebreak << endl;*/
    
    return 0;
}
