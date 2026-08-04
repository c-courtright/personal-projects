library(tidyverse)
library(shiny)

# need to do something with the input...
# either switch to auto pitch type or something idk
pitches <- read.csv("../brady_data_jul25.csv") # placeholder csv

# find league-wide strikeout rate
pas <- pitches |>
  group_by(Pitcher, PitcherId, Batter, BatterId, Date, Inning, PAofInning) |>
  slice_tail(n=1) |>
  ungroup()
num_pas <- nrow(pas)
num_ks <- pas |>
  filter(KorBB == 'Strikeout') |>
  nrow()
league_kr <- num_ks / num_pas

# Name to ID lookup
lookup <- pitches |>
  select(BatterId, Batter, PitcherId, Pitcher) |>
  distinct()

to_name <- function(name) {
  parts <- strsplit(name, ' ')[[1]]
  first <- paste(parts[-length(parts)], collapse=' ')
  last <- parts[length(parts)]
  paste0(last, ', ', first)
}

get_player_id <- function(name, is_pitcher) {
  trackman_name <- to_name(name)
  if(is_pitcher == TRUE) {
    id <- lookup |>
      filter(Pitcher == trackman_name) |>
      pull(PitcherId) |>
      unique()
  }
  else {
    id <- lookup |>
      filter(Batter == trackman_name) |>
      pull(BatterId) |>
      unique()
  }
  
  if(length(id) == 0) { stop(paste("Batter not found:", trackman_name)) }
  if(length(id) > 1) { warning(paste("Multiple IDs found for:", trackman_name, "- using first")) }
  id[1]
}

# pitcher handedness lookup
get_pitcher_hand <- function(pitches, pid) {
  pitches |>
    filter(PitcherId == pid) |>
    pull(PitcherThrows) |>
    unique() |>
    first()
}

# pitcher function
get_pitcher_stats <- function(pitches, pid) {
  pitcher_hand<-get_pitcher_hand(pitches, pid)
  target_pitcher <- pitches |> filter(PitcherId == pid)
  
  twok_pitches <- target_pitcher |>
    filter(Strikes == 2) |>
    group_by(TaggedPitchType) |>
    summarize(num_thrown = n(), .groups='drop') |>
    mutate(
      utx = num_thrown / sum(num_thrown),
      PitchTypeKey = paste0(TaggedPitchType, '_', pitcher_hand)
    )
  
  gen_pitches <- target_pitcher |>
    group_by(TaggedPitchType) |>
    summarize(num_thrown = n(), .groups='drop') |>
    mutate(
      ugx = num_thrown / sum(num_thrown),
      PitchTypeKey = paste0(TaggedPitchType, '_', pitcher_hand)
    )
  
  left_join(twok_pitches, gen_pitches, by=c('TaggedPitchType', 'PitchTypeKey')) |>
    select(TaggedPitchType, PitchTypeKey, utx, ugx)
}

# batter function
get_batter_stats <- function(pitches, bid, pitcher_hand, pitch_key_list) {
  target_batter <- pitches |> filter(BatterId == bid)
  
  total_pas_all <- target_batter |>
    group_by(GameID, Inning, PAofInning, PitcherId, BatterId) |>
    slice(1) |>
    ungroup()
  
  strikeout_pas <- target_batter |>
    group_by(GameID, Inning, PAofInning, PitcherId, BatterId) |>
    slice_tail(n=1) |>
    ungroup() |>
    filter(KorBB == 'Strikeout')
  
  total_pa <- nrow(total_pas_all)
  total_k <- nrow(strikeout_pas)
  k_rate <- total_k / total_pa
  
  total_pitches_seen <- nrow(target_batter)
  total_whiffs <- target_batter |>
    filter(PitchCall == 'StrikeSwinging') |>
    nrow()
  overall_whiff_rate <- total_whiffs / total_pitches_seen
  
  total_pas_split <- target_batter |>
    filter(PitcherThrows == pitcher_hand) |>
    group_by(GameID, Inning, PAofInning, PitcherId, BatterId) |>
    slice(1) |>
    ungroup()
  
  two_strike_pas_split <- target_batter |>
    filter(PitcherThrows == pitcher_hand, Strikes == 2) |>
    group_by(GameID, Inning, PAofInning, PitcherId, BatterId) |>
    slice(1) |>
    ungroup()
  
  if(nrow(total_pas_split) >= 20) {
    rate2k <- nrow(two_strike_pas_split) / nrow(total_pas_split)
  } else {
    two_strike_pas_all <- target_batter |>
      filter(Strikes == 2) |>
      group_by(GameID, Inning, PAofInning, PitcherId, BatterId) |>
      slice(1) |>
      ungroup()
    rate2k <- nrow(two_strike_pas_all) / nrow(total_pas_all)
  }
  
  twok_pitches_b <- target_batter |>
    filter(Strikes == 2) |>
    mutate(
      PitchTypeKey = paste0(TaggedPitchType, '_', PitcherThrows)
    ) |>
    group_by(PitchTypeKey, TaggedPitchType) |>
    summarize(num_thrown = n(), .groups='drop')
  
  twok_whiffs <- target_batter |>
    filter(Strikes == 2, PitchCall %in% c('StrikeSwinging', 'StrikeCalled')) |>
    mutate(
      PitchTypeKey = paste0(TaggedPitchType, '_', PitcherThrows)
    ) |>
    group_by(PitchTypeKey) |>
    summarize(num_whiffs = n(), .groups='drop')
  
  twok_stats <- left_join(twok_pitches_b, twok_whiffs, by='PitchTypeKey') |>
    mutate(
      num_whiffs = replace_na(num_whiffs, 0),
      wtx_split = num_whiffs / num_thrown
    )
  
  twok_pitches_gen <- target_batter |>
    filter(Strikes == 2) |>
    group_by(TaggedPitchType) |>
    summarize(num_thrown_gen = n(), .groups='drop')
  
  twok_whiffs_gen <- target_batter |>
    filter(Strikes == 2, PitchCall %in% c('StrikeSwinging', 'StrikeCalled')) |>
    group_by(TaggedPitchType) |>
    summarize(num_whiffs_gen = n(), .groups='drop')
  
  twok_gen <- left_join(twok_pitches_gen, twok_whiffs_gen, by='TaggedPitchType') |>
    mutate(
      num_whiffs_gen = replace_na(num_whiffs_gen, 0),
      wtx_gen = num_whiffs_gen / num_thrown_gen
    )
  
  twok_stats <- twok_stats |>
    left_join(twok_gen, by='TaggedPitchType') |>
    mutate(
      wtx = case_when(
        num_thrown >= 20 ~ wtx_split,
        TRUE ~ 0.7*wtx_split + 0.3*wtx_gen
      )
    )
  
  gen_pitches_b <- target_batter |>
    mutate(
      PitchTypeKey = paste0(TaggedPitchType, '_', PitcherThrows)
    ) |>
    group_by(PitchTypeKey, TaggedPitchType) |>
    summarize(num_thrown = n(), .groups='drop')
  
  gen_whiffs <- target_batter |>
    filter(PitchCall == 'StrikeSwinging') |>
    mutate(
      PitchTypeKey = paste0(TaggedPitchType, '_', PitcherThrows)
    ) |>
    group_by(PitchTypeKey) |>
    summarize(num_whiffs = n(), .groups='drop')
  
  gen_stats <- left_join(gen_pitches_b, gen_whiffs, by='PitchTypeKey') |>
    mutate(
      num_whiffs = replace_na(num_whiffs, 0),
      wgx = num_whiffs / num_thrown
    )
  
  stats_b <- left_join(twok_stats, gen_stats, by=c('PitchTypeKey', 'TaggedPitchType')) |>
    select(PitchTypeKey, wtx, wgx) |>
    filter(PitchTypeKey %in% pitch_key_list)
  
  list(
    stats = stats_b,
    rate2k = rate2k,
    total_pa = total_pa,
    total_k = total_k,
    k_rate = k_rate,
    overall_whiff_rate = overall_whiff_rate
  )
}

# Pk = (freq. of X-2 cts) * (Whiff% on X-2)
# K_adj = coeff. to adjust for hitter's strikeout rate relative to league avg
# \mu_PA = avg. number of PAs per game for hitters in the nth spot
# score = Pk*K_adj*\mu_PA
compute_score <- function(pitches, pid, bid, pa_avg, kr_mean, kr_scale=2) {
  pitcher_hand <- get_pitcher_hand(pitches, pid)
  stats_p <- get_pitcher_stats(pitches, pid)
  pitch_key_list <- stats_p$PitchTypeKey
  
  batter <- get_batter_stats(pitches, bid, pitcher_hand, pitch_key_list)
  
  stats_cum <- left_join(stats_p, batter$stats, by='PitchTypeKey') |>
    mutate(
      across(c(wtx, wgx), ~replace_na(.x, 0)),
      w2kx = (0.7*wtx + 0.3*wgx) * (0.7*utx + 0.3*ugx)
    )
  
  w2k <- sum(stats_cum$w2kx)
  pk <- batter$rate2k * w2k
  k_adj = 1 + kr_scale*(batter$k_rate - kr_mean)
  score <- pk * k_adj * pa_avg
  
  list(
    score = score,
    total_pa = batter$total_pa,
    total_k = batter$total_k,
    k_rate = batter$k_rate,
    overall_whiff_rate = batter$overall_whiff_rate
  )
}

# pulled from online
pa_avg_by_spot <- c("1"=4.65, "2"=4.55, "3"=4.43, "4"=4.33, "5"=4.24, "6"=4.13, "7"=4.01, "8"=3.90, "9"=3.77)

# build interactive shiny app
ui <- fluidPage(
  titlePanel("Strikeout Predictor"),
  sidebarLayout(
    sidebarPanel(
      textInput("pitcher", "Pitcher (First Last)"),
      textInput("b1", "Batter 1"),
      textInput("b2", "Batter 2"),
      textInput("b3", "Batter 3"),
      textInput("b4", "Batter 4"),
      textInput("b5", "Batter 5"),
      textInput("b6", "Batter 6"),
      textInput("b7", "Batter 7"),
      textInput("b8", "Batter 8"),
      textInput("b9", "Batter 9"),
      actionButton("run", "Calculate", class="btn-primary"),
      textOutput("error_msg")
    ),
    mainPanel(
      tableOutput('results')
    )
  )
)

server <- function(input, output) {
  results <- eventReactive(input$run, {
    lineup_names <- c(input$b1, input$b2, input$b3, input$b4, input$b5, input$b6, input$b7, input$b8, input$b9)
    lineup_names <- lineup_names[lineup_names != ""]
    
    validate(
      need(input$pitcher != "", "Enter a pitcher."),
      need(length(lineup_names) > 0, "Enter at least one batter.")
    )
    
    pid <- tryCatch(
      get_player_id(input$pitcher, TRUE),
      error = function(e) { validate(need(FALSE, conditionMessage(e))) }
    )
    
    raw <- tibble(Batter = lineup_names) |>
      mutate(
        lineup_spot = row_number(),
        pa_avg = pa_avg_by_spot[as.character(lineup_spot)],
        BatterId = map_int(Batter, ~tryCatch(
          get_player_id(.x, FALSE),
          error = function(e) NA_integer_
        )),
        result = pmap(
          list(BatterId, pa_avg),
          ~ {
            if (is.na(..1)) {
              list(score = NA_real_, total_pa = NA_integer_, total_k = NA_integer_,
                   k_rate = NA_real_, overall_whiff_rate = NA_real_)
            } else {
              compute_score(pitches, pid, ..1, pa_avg = ..2, kr_mean = league_kr)
            }
          }
        )
      ) |>
      mutate(
        score = map_dbl(result, 'score'),
        total_pa = map_int(result, ~ as.integer(.x$total_pa)),
        total_k = map_int(result, ~ as.integer(.x$total_k)),
        k_rate = map_dbl(result, 'k_rate')*100,
        wr_pct = map_dbl(result, 'overall_whiff_rate')*100
      )
    
    raw |>
      arrange(desc(score), desc(total_k), desc(wr_pct)) |>
      select(
        Batter,
        'Score' = score,
        'PA' = total_pa,
        'K' = total_k,
        'K%' = k_rate,
        'Whiff%' = wr_pct
      )
  })
  
  output$results <- renderTable({ results() }, digits=3)
}

shinyApp(ui, server)