# calculates DISC+ for single hitter

import pandas as pd
import numpy as np

BANDWIDTH = 4.0
GRID_POINTS_PER_AXIS = 15
X_RANGE = (-15, 33)
Y_RANGE = (-15, 41)
MIN_EFFECTIVE_N = 3.0

league_cache = {}

def make_grid():
    xs = np.linspace(X_RANGE[0], X_RANGE[1], GRID_POINTS_PER_AXIS)
    ys = np.linspace(Y_RANGE[0], Y_RANGE[1], GRID_POINTS_PER_AXIS)
    gx, gy = np.meshgrid(xs, ys)
    return gx.ravel(), gy.ravel()

def kernel_weights(px, py, gx, gy):
    dx = px[:, None] - gx[None, :]
    dy = py[:, None] - gy[None, :]
    dist_sq = dx**2 + dy**2
    return np.exp(-dist_sq / (2 * BANDWIDTH**2))

def get_league_rates(pitches:pd.DataFrame):
    cache_key = id(pitches)
    if(cache_key in league_cache): return league_cache[cache_key]

    gx, gy = make_grid()

    px = pitches['PlateLocSide'].to_numpy(dtype=float)
    py = pitches['PlateLocHeight'].to_numpy(dtype=float)
    is_swing = (pitches['Group'] == 'Swing').to_numpy()
    is_strike_call = (pitches['Group'] == 'Strike').to_numpy()
    is_whiff = (pitches['SwingResult'] == 'Whiff').to_numpy()

    weights = kernel_weights(px, py, gx, gy)

    w_sum_all = weights.sum(axis=0)
    s_lg = (weights * is_swing[:, None]).sum(axis=0) / np.where(w_sum_all == 0, np.nan, w_sum_all)

    taken_mask = ~is_swing
    w_taken = weights * taken_mask[:, None]
    w_sum_taken = w_taken.sum(axis=0)
    p_k = (w_taken * is_strike_call[:, None]).sum(axis=0) / np.where(w_sum_taken == 0, np.nan, w_sum_taken)

    w_swung = weights * is_swing[:, None]
    w_sum_swung = w_swung.sum(axis=0)
    p_w = (w_swung * is_whiff[:, None]).sum(axis=0) / np.where(w_sum_swung == 0, np.nan, w_sum_swung)

    p_k = np.nan_to_num(p_k, nan=0.0)
    p_w = np.nan_to_num(p_w, nan=0.0)
    s_lg = np.nan_to_num(s_lg, nan=0.0)

    target = np.clip(p_k * (1 - p_w), 0.0, 1.0)
    w = p_k * (1 - p_k)

    res = (gx, gy, target, s_lg, w)
    league_cache[cache_key] = res
    return res

def calc_discp(btr:str, pitches:pd.DataFrame, min_pitches:int = 200) -> float:
    gx, gy, target_rate, s_lg, w = get_league_rates(pitches)

    w_sum = w.sum()
    if(w_sum == 0): raise ValueError("league rates summed to 0; check input data")

    d_lg = np.sum(w * np.abs(s_lg - target_rate)) / w_sum

    target = pitches[pitches['Batter'] == btr]
    if(len(target) < min_pitches): raise ValueError(f"not enough pitches for batter: {btr}")

    px = target['PlateLocSide'].to_numpy(dtype=float)
    py = target['PlateLocHeight'].to_numpy(dtype=float)
    is_swing = (target['Group'] == 'Swing').to_numpy()

    weights = kernel_weights(px, py, gx, gy)
    w_sum_h = weights.sum(axis=0)

    valid = w_sum_h >= MIN_EFFECTIVE_N
    if not np.any(valid): raise ValueError(f"not enough usable location coverage for batter: {btr}")

    si_h = (weights[:, valid] * is_swing[:, None]).sum(axis=0) / w_sum_h[valid]

    w_valid = w[valid]
    w_valid_sum = w_valid.sum()
    if w_valid_sum == 0: raise ValueError(f"no informative grid coverage for batter: {btr}")

    d_h = np.sum(w_valid * np.abs(si_h - target_rate[valid])) / w_valid_sum
    if d_h == 0: return float("inf")

    return d_lg / d_h * 100