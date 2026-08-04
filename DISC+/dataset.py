# sets up data for analysis

import numpy as np
import pandas as pd

import discp

MIN_PITCHES_SEEN = 200

def get_disc_stats(pitches:pd.DataFrame) -> pd.DataFrame:
    p = pitches.copy()
    p['InZone'] = p['PlateLocSide'].between(0, 18) & p['PlateLocHeight'].between(0, 20.2)
    p['IsSwing'] = p['Group'] == 'Swing'

    swing = p.groupby('Batter')['IsSwing'].mean()
    zswing = p[p['InZone']].groupby('Batter')['IsSwing'].mean()
    oswing = p[~p['InZone']].groupby('Batter')['IsSwing'].mean()

    swings = p[p['IsSwing']]
    whiff = swings.groupby('Batter')['SwingResult'].apply(lambda s: (s == 'Whiff').mean())
    contact = swings.groupby('Batter')['SwingResult'].apply(lambda s: (s == 'Contact').mean())

    res = pd.DataFrame({
        'Swing%' : swing,
        'ZSwing%' : zswing,
        'OSwing%' : oswing,
        'Whiff%' : whiff,
        "Contact%" : contact
    })

    return res.fillna(0.0)

def get_cqual_stats(pitches:pd.DataFrame) -> pd.DataFrame:
    p = pitches.dropna(subset=['ExitSpeed']).copy()

    high_cut = p['ExitSpeed'].quantile(0.70)
    p['HardHit'] = p['ExitSpeed'] > high_cut

    la_min = 26 - (p['ExitSpeed'] - 98)
    la_max = 30 + (p['ExitSpeed'] - 98)*(20/18)
    p['Barrel'] = (p['ExitSpeed'] >= 98) & p['Angle'].between(la_min, la_max)

    num_contact = pitches[pitches['SwingResult'] == 'Contact'].groupby('Batter').size()

    res = pd.DataFrame({
        'Hard%' : p.groupby('Batter')['HardHit'].sum() / num_contact,
        'BRL%' : p.groupby('Batter')['Barrel'].sum() / num_contact
    })

    return res.fillna(0.0)

def resolve_pas(pitches:pd.DataFrame):
    pa_group_cols = ['Batter', 'GameID', 'Inning', 'Top/Bottom', 'PAofInning']
    p = pitches.sort_values(pa_group_cols + ['PitchofPA'])
    last_pitches = p.groupby(pa_group_cols, as_index=False).last()

    korbb = last_pitches.get('KorBB', pd.Series(np.nan, index=last_pitches.index))
    play_result = last_pitches.get('PlayResult', pd.Series(np.nan, index=last_pitches.index))
    pitch_call = last_pitches.get('PitchCall', pd.Series(np.nan, index=last_pitches.index))
    tb_map = {'Single':1, 'Double':2, 'Triple':3, 'HomeRun':4}

    is_bb = (korbb == 'Walk')
    is_hbp = (~is_bb & ((pitch_call == 'HitByPitch') | (korbb == 'HitByPitch')))
    not_bb_hbp = ~is_bb & ~is_hbp

    is_k = not_bb_hbp & (korbb == 'Strikeout')
    is_hit = not_bb_hbp & ~is_k & play_result.isin(tb_map)
    is_sac = not_bb_hbp & ~is_k & ~is_hit & (play_result == 'Sacrifice')
    is_ab = not_bb_hbp & ~is_sac

    last_pitches['_AB'] = is_ab.astype(int)
    last_pitches['_BB'] = is_bb.astype(int)
    last_pitches['_HBP'] = is_hbp.astype(int)
    last_pitches['_K'] = is_k.astype(int)
    last_pitches['_H'] = is_hit.astype(int)
    last_pitches['_SF'] = is_sac.astype(int)
    last_pitches['_TB'] = play_result.map(tb_map).where(is_hit, 0).fillna(0)

    return last_pitches

def get_kbb(pitches:pd.DataFrame) -> pd.DataFrame:
    last_pitches = resolve_pas(pitches)

    grouped = (
        last_pitches.groupby('Batter')
        .agg(
            AB = ('_AB', 'sum'),
            BB = ('_BB', 'sum'),
            K = ('_K', 'sum')
        )
    )

    ab_safe = grouped['AB'].replace(0, np.nan)
    res = pd.DataFrame({
        'K%' : (grouped['K'] / ab_safe).fillna(0.0),
        'BB%' : (grouped['BB'] / ab_safe).fillna(0.0)
    })

    return res

def get_ops(pitches:pd.DataFrame) -> pd.DataFrame:
    last_pitches = resolve_pas(pitches)
    grouped = (
        last_pitches.groupby('Batter').agg(
            PA = ('Batter', 'size'),
            AB = ('_AB', 'sum'),
            BB = ('_BB', 'sum'),
            HBP = ('_HBP', 'sum'),
            H = ('_H', 'sum'),
            TB = ('_TB', 'sum'),
            SF = ('_SF', 'sum')
        )
    )

    ab_safe = grouped['AB'].replace(0, np.nan)
    pa_safe = grouped['PA'].replace(0, np.nan)

    obp = ((grouped['H'] + grouped['BB'] + grouped['HBP']) / pa_safe).fillna(0.0)
    slg = (grouped['TB'] / ab_safe).fillna(0.0)

    res = pd.DataFrame({
        'PA' : grouped['PA'],
        'AB' : grouped['AB'],
        'BB' : grouped['BB'],
        'HBP' : grouped['HBP'],
        'OBP' : grouped['OBP'],
        'SLG' : grouped['SLG'],
        'OPS' : (obp + slg).round(3)
    })

    return res

def build_dataset(pitches:pd.DataFrame, min_pitches=MIN_PITCHES_SEEN) -> pd.DataFrame:
    pitch_counts = pitches.groupby('Batter').size()
    qualified = pitch_counts[pitch_counts >= min_pitches].index

    discipline = get_disc_stats(pitches)
    cqual = get_cqual_stats(pitches)
    kbb = get_kbb(pitches)

    discp_vals = {
        batter : discp.calc_discp(batter, pitches, min_pitches) for batter in qualified
    }

    res = (
        pd.DataFrame({"DISC+" : discp_vals})
        .join(discipline)
        .join(cqual)
        .join(kbb)
        .dropna()
        .reset_index()
        .rename(columns={'index' : 'Batter'})
    )

    return res