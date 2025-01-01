
#---
#title: "Baseball Simulator Sheet Cleaner"
#author: "Connor Courtright"
#date: "2024-12-29"
#output: html_document
#---


install.packages("tidyverse")

library(httr)
library(jsonlite)
library(dplyr)
library(tidyr)
library(tidyverse)

# goal of this is to end up with cleaner spreadsheets/csvs that can be used in 
# simulator program later

# first step is to read in csv files containing input info
team <- "Los-Angeles Dodgers"
words <- unlist(strsplit(team, " "))
team_prefix <- tolower(words[2])

off_stats <- read.csv(paste0(team_prefix, "_hitter_input.csv"))
pitch_stats <- read.csv(paste0(team_prefix, "_pitcher_input.csv"))

# we will clean pitching first
# add column with team name
tm_col <- rep(team, nrow(pitch_stats))
pitch_stats$Tm <- tm_col

# start by separating relief and starting pitchers
starting_pitchers <- pitch_stats %>%
  filter(Pos == "SP")
relief_pitchers <- pitch_stats %>%
  filter(Pos == "RP" | Pos == "CL")

# then select important statistics for each pitcher
starting_pitchers <- starting_pitchers %>%
  dplyr::select(Player, WAR, H, HR, BB, SO, HBP, BF, Tm)
relief_pitchers <- relief_pitchers %>%
  dplyr::select(Player, WAR, H, HR, BB, SO, HBP, BF, Tm)

# now onto hitters
# add column with team name, referencing tm_col from before
tm_col <- rep(team, nrow(off_stats))
off_stats$Tm <- tm_col

team_hitters <- off_stats %>%
  filter(Pos != "P" & Pos != "IF" & !is.na(Age))

team_hitters <- team_hitters %>%
  dplyr::select(Player, Pos, G, WAR, AB, H, X2B, X3B, HR, BB, SO, BA, OBP, SLG, HBP, Tm)

# at this point we should be good to export them jawns
write.csv(starting_pitchers, paste("~/Downloads/", "_starting_pitchers.csv", sep = team_prefix), row.names = TRUE)
write.csv(relief_pitchers, paste("~/Downloads/", "_relief_pitchers.csv", sep = team_prefix), row.names = TRUE)
write.csv(team_hitters, paste("~/Downloads/", "_team_hitters.csv", sep = team_prefix), row.names = TRUE)
