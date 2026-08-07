import os
import pathlib
import warnings
from datetime import date

warnings.filterwarnings("ignore", message=".*warn_singular.*")
warnings.filterwarnings("ignore", category=FutureWarning, message="The behavior of DataFrame concatenation")

import pandas as pd
pd.options.mode.chained_assignment = None

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, Circle
from matplotlib.path import Path
from matplotlib.colors import to_hex

import seaborn as sns
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import RobustScaler

os.makedirs("output/html_output", exist_ok=True)
os.makedirs("output/pdf_output", exist_ok=True)
os.makedirs("static/images", exist_ok=True)

GAMES_DIR = "../input/gamedata"
PITCH_TYPE_REF = "../input/pitch_type_reference.csv"

teams = {
    "NOR_COR" : "Normal CornBelters",
    "CLI_LUM1" : "Clinton LumberKings",
    "BUR_BEE1" : "Burlington Bees",
    "KOK_CRE" : "Kokomo Creek Chubs",
    "CHA_CIT" : "Champion City Half Trax",
    "JOH_MIL" : "Johnstown Mill Rats",
    "CHI_PAT" : "Chillicothe Paints",
    "QUI_DOG" : "Quincy Doggy Paddlers",
    "ALT_RIV" : "Alton River Dragons",
    "DEC_BEA" : "Decatur Bean Ballers",
    "LAF_AVI" : "Lafayette Aviators",
    "ILL_VAL3" : "Illinois Valley Pistol Shrimp",
    "O'F_HOO" : "O'Fallon Hoots",
    "CAP_CAT" : "Cape Catfish",
    "THR_THR1" : "Thrillville Thrillbillies",
    "TER_HAU" : "Terre Haute Rex",
    "DAN_DAN" : "Danville Dans",
    "SPR_LUC" : "Springfield Lucky Horses",
    "JAC_ROC" : "Jackson Rockabillys",
    "DUB_COU" : "Dubois County Bombers"
}

cmap = plt.cm.Pastel1
PITCH_COLOR_MAP = {}

EVEN_COUNTS = [(0, 0), (1, 1), (2, 2), (3, 2)]
HITTER_COUNTS = [(2, 0), (2, 1), (3, 0), (3, 1)]
PITCHER_COUNTS = [(0, 1), (0, 2)]
ALL_COUNTS = EVEN_COUNTS + HITTER_COUNTS + PITCHER_COUNTS

REPORT_TYPES = {
    "coach": {
        "template": "coaches_report_template.html",
        "label": "coaches_report",
        "needs_splits": True,
        "needs_catchers": True,
        "is_pitcher_view": False,
        "allows_date_filter": False,
    },
    "player": {
        "template": "players_report_template.html",
        "label": "players_report",
        "needs_splits": False,
        "needs_catchers": False,
        "is_pitcher_view": False,
        "allows_date_filter": False,
    },
    "pitcher": {
        "template": "pitchers_report_template.html",
        "label": "pitchers_report",
        "needs_splits": True,
        "needs_catchers": False,
        "is_pitcher_view": True,
        "allows_date_filter": True,
    }
}



def load_trackman_data(dir=GAMES_DIR):
    """
    Loads and concatenates every TrackMan CSV export.

    Input: dir (str)
    Output: df of all pitches
    """
    files = sorted(pathlib.Path(dir).rglob("*.csv"))
    if not files: raise FileNotFoundError(f"No input found under: {dir}")

    return pd.concat([pd.read_csv(f) for f in files], ignore_index=True)

def assign_pitch_types(td, ref_path=PITCH_TYPE_REF):
    """
    
    """
    td = td.copy()
    td['PitchType'] = td['AutoPitchType']

    try:
        ref = pd.read_csv(ref_path)
    except FileNotFoundError:
        print(f"Pitch type reference not found at '{ref_path}'. Using AutoPitchType for every pitcher.")
        return td
    
    pitch_cols = [c for c in ref.columns if c.lower() != 'pitcher']
    feature_cols = [c for c in ['RelSpeed', 'InducedVertBreak', 'HorzBreak', 'SpinRate', 'Extension', 'RelHeight', 'RelSide'] if c in td.columns]

    for _, row in ref.iterrows():
        pitcher_name = row['pitcher']
        labels = [row[c] for c in pitch_cols if pd.notna(row[c]) and str(row[c]).strip()]
        if not labels: continue

        mask = td['Pitcher'] == pitcher_name
        if len(labels) == 1: 
            td.loc[mask, 'PitchType'] = labels[0]
            continue

        subset = td.loc[mask, feature_cols]
        filled = subset.fillna(subset.mean(numeric_only=True)).dropna()
        if len(filled) < len(labels):
            print(f"Not enough usable pitches to cluster for {pitcher_name}. Using AutoPitchType.")
            continue

        scaler = RobustScaler().fit(filled)
        scaled = scaler.transform(filled)

        gmm = GaussianMixture(n_components=len(labels), random_state=42, n_init=10, reg_covar=1e-3)
        cluster_ids = pd.Series(gmm.fit_predict(scaled), index=filled.index)

        cluster_velo = filled['RelSpeed'].groupby(cluster_ids).median().sort_values(ascending=False)
        cluster_to_label = {cluster : labels[i] for i, cluster in enumerate(cluster_velo.index)}

        td.loc[filled.index, 'PitchType'] = cluster_ids.map(cluster_to_label)
    
    return td

trackman_data = assign_pitch_types(load_trackman_data())

def find_pitcher(first, last, td=trackman_data):
    """
    
    """
    pitches = td.query(f"Pitcher == '{last}, {first}'")
    if pitches.empty:
        print("Pitcher not found or has not thrown a pitch.")
        return None
    
    pid = pitches.iloc[0]['PitcherId']
    print(f"{first} {last}: pid={pid}; {len(pitches)} pitches found")
    return pid

def player_info(pitches):
    """
    
    """
    fullname = pitches.iloc[0]['Pitcher']
    last, first = fullname.split(', ', 1)
    team = teams.get(pitches.iloc[0]['PitcherTeam'], "Team not found")
    handedness = pitches.iloc[0]['PitcherThrows'][0] + "HP"
    pitch_types = list(pitches['PitchType'].dropna().unique())

    return (f"{first} {last}", team, handedness, pitch_types)

def get_stats(pitches):
    """
    Computes pitching stats displayed in banner at the top of the report
    (IP, WHIP, SO9, BB9, HR9). All rate stats with 0 IP display 0.0.

    Input: pitches (df)
    Output: list of (label, stat value) tuples
    """
    k = int((pitches.get('KorBB') == 'Strikeout').sum())
    bb = int((pitches.get('KorBB') == 'Walk').sum())
    hits = int(pitches.get('PlayResult').isin(['Single', 'Double', 'Triple', 'HomeRun']).sum())
    hr = int((pitches.get('PlayResult') == 'HomeRun').sum())
    outs_play = pd.to_numeric(pitches.get('OutsOnPlay'), errors='coerce').fillna(0).sum()
    outs = k + outs_play
    ip = outs / 3.0

    whole, rem = divmod(int(round(outs)), 3)
    ip_str = f"{whole}.{rem}"

    nine = (9.0 / ip) if ip else 0.0
    whip = round((bb + hits) / ip, 2) if ip else 0.0
    so9 = round(k*nine, 1) if ip else 0.0
    bb9 = round(bb*nine, 1) if ip else 0.0
    hr9 = round(hr*nine, 1) if ip else 0.0

    return [
        ('IP', ip_str),
        ('WHIP', f"{whip}"),
        ('SO9', f"{so9}"),
        ('BB9', f"{bb9}"),
        ('HR9', f"{hr9}")
    ]

def get_ops(pitches, split=True, handedness='Right'):
    """
    Calculates OPS allowed. OBP is approximated as (H + BB + HBP) / PA.

    Input: pitches (df), split (bool), handedness (str)
    Output: float
    """
    if split: pitches = pitches.query(f"BatterSide == '{handedness}'")
    if pitches.empty: return 0.0

    hit_bases = {'Single':1, 'Double':2, 'Triple':3, 'HomeRun':4}
    play_result = pitches.get('PlayResult')
    hits = int(play_result.isin(hit_bases).sum())
    tb = int(play_result.map(hit_bases).fillna(0).sum())

    bb = int((pitches.get('KorBB') == 'Walk').sum())
    hbp = int((pitches.get('PitchCall') == 'HitByPitch').sum())

    pa = pitches.groupby(['GameUID', 'Inning', 'Outs', 'BatterId']).ngroups
    if pa == 0.0: return 0.0

    ab = pa - bb - hbp
    obp = (hits + bb + hbp) / pa
    slg = (tb / ab) if ab > 0 else 0.0

    return round(obp + slg, 3)

def usage_velo(pitches, split=False, handedness='Right'):
    """
    Calculates pitch usage rate and avg/min/max velocity per pitch type.

    Input: pitches (df), split (bool), handedness (str)
    Output: tuple (usage dict, velo dict)
    """
    if split: pitches = pitches.query(f"BatterSide == '{handedness}'")

    grouped = (
        pitches.groupby(['PitcherId', 'Pitcher', 'PitchType'])
        .agg(
            NumThrown = ('PitchType', 'count'),
            AvgVelo = ('RelSpeed', 'mean'),
            MinVelo = ('RelSpeed', 'min'),
            MaxVelo = ('RelSpeed', 'max')
        )
        .reset_index()
    )

    total = grouped['NumThrown'].sum()
    if not total: return {}, {}

    usages, velocities = {}, {}
    for _, row in grouped.iterrows():
        pitch = row['PitchType']
        usages[pitch] = round(row['NumThrown'] / total * 100, 1)
        velocities[pitch] = {
            'avg' : round(row['AvgVelo'], 1),
            'min' : round(row['MinVelo'], 1),
            'max' : round(row['MaxVelo'], 1)
        }
    
    return usages, velocities

def get_strike_perc(pitches):
    """
    Helper for get_tendencies - calculates strike percentage by count.

    Input: pitches (df)
    Output: tuple (df, float)
    """
    pitches = pitches.query("PitchCall != 'BallIntentional'")
    pitches = pitches.replace({'PitchCall' : {
        'StrikeCalled' : 'Strike',
        'StrikeSwinging' : 'Strike',
        'Foul' : 'Strike',
        'InPlay' : 'Strike',
        'BallCalled' : 'Ball',
        'BallinDirt' : 'Ball',
        'HitByPitch' : 'Ball'
    }})

    grouped = (
        pitches.groupby(['PitcherId', 'Pitcher', 'Balls', 'Strikes', 'PitchCall'])
        .agg(
            NumThrown = ('PitchCall', 'count')
        )
        .reset_index()
    )

    total_thrown, total_strikes = 0, 0
    rows = []
    for (b, s) in ALL_COUNTS:
        temp = grouped.query(f"Balls == {b} & Strikes == {s}")
        num = temp['NumThrown'].sum()
        if num == 0: continue

        ks = temp.query("PitchCall == 'Strike'")['NumThrown'].sum()
        total_thrown += num
        total_strikes += ks

        row = temp.iloc[[0]].copy()
        row['StrikePerc'] = round((ks / num) * 100, 2)
        rows.append(row.drop(columns=['NumThrown', 'PitchCall']))

    if not rows: return pd.DataFrame(columns=['PitcherId', 'Pitcher', 'Balls', 'Strikes', 'StrikePerc']), 0.0

    overall_strike_perc = (total_strikes / total_thrown * 100) if total_thrown else 0.0
    return pd.concat(rows, ignore_index=True), overall_strike_perc

def pitches_by_count(b, s, pitches):
    """
    Helper for get_tendencies - calculates pitch usage tendencies for a single count.

    Input: b (int), s (int), pitches (df)
    Output: list of dicts
    """
    global PITCH_COLOR_MAP

    target = pitches.query(f"Balls == {b} & Strikes == {s}")
    if target.empty: return []

    grouped = (
        target.groupby('PitchType')
        .agg(
            NumThrown = ('PitchType', 'count')
        )
        .sort_values(by='NumThrown', ascending=False)
        .reset_index()
    )
    total = grouped['NumThrown'].sum()

    res = []
    for _, row in grouped.iterrows():
        pitch = row['PitchType']
        if pitch not in PITCH_COLOR_MAP: PITCH_COLOR_MAP[pitch] = to_hex(cmap(len(PITCH_COLOR_MAP)))

        res.append({
            'name' : pitch,
            'usage' : f"{round(row['NumThrown'] / total * 100, 1)}%",
            'color' : PITCH_COLOR_MAP[pitch]
        })

    return res

def create_color_map(pitches):
    """
    Ensures colors are assigned uniformly for each pitch type.

    Input: pitches (df)
    Output: void
    """
    global PITCH_COLOR_MAP
    for p in pitches['PitchType'].dropna().unique():
        if p not in PITCH_COLOR_MAP:
            PITCH_COLOR_MAP[p] = to_hex(cmap(len(PITCH_COLOR_MAP)))

def get_tendencies(pitches, is_pitcher=False):
    """
    Builds by-count tendencies (strike rate and pitch mix) for every count.
    Note: is_pitcher only affects view orientation for charts

    Input: pitches (df), is_pitcher (bool)
    Output: tuple (dict, float)
    """
    strike_percs, overall_strike_perc = get_strike_perc(pitches)
    create_color_map(pitches)
    spraycharts = get_spraycharts_by_count(pitches, is_pitcher)

    def build_entry(b, s):
        matches = strike_percs.query(f"Balls == {b} & Strikes == {s}")
        strike_rate = matches['StrikePerc'].item() if not matches.empty else 0

        return {
            'count_label' : f"{b}-{s}",
            'strike_rate' : f"{strike_rate}%",
            'pitches' : pitches_by_count(b, s, pitches),
            'spray_chart' : spraycharts.get(f"{b}-{s}")
        }
    
    tendencies = {
        'even' : [build_entry(b, s) for (b, s) in EVEN_COUNTS],
        'hitter' : [build_entry(b, s) for (b, s) in HITTER_COUNTS],
        'pitcher' : [build_entry(b, s) for (b, s) in PITCHER_COUNTS]
    }

    return tendencies, overall_strike_perc

def draw_strike_zone(axs):
    """
    Draws strike zone grid on the given figure.

    Input: axs (matplotlib axes)
    Output: void
    """
    rect = Rectangle((0, 0), 17, 19.2, linewidth=2, edgecolor='black', facecolor='none')
    axs.add_patch(rect)
    verts = [(5.67, 0), (5.67, 19.2), (11.33, 19.2), (11.33, 0), (0, 6.4), (17, 6.4), (17, 12.8), (0, 12.8)]
    codes = [Path.MOVETO, Path.LINETO, Path.MOVETO, Path.LINETO, Path.MOVETO, Path.LINETO, Path.MOVETO, Path.LINETO]
    grid_lines = patches.PathPatch(Path(verts, codes), edgecolor='black', facecolor='none', lw=2)
    axs.add_patch(grid_lines)

def to_plate_coords(pitches, is_pitcher):
    """
    Converts PlateLocSide/PlateLocHeight from feet to inches and
    makes sure the orientation of the chart matches intended use.

    Input: pitches (df), is_pitcher (bool)
    Output: df
    """
    pitches = pitches.copy()
    pitches['PlateLocHeight'] = pitches['PlateLocHeight']*12 - 18
    if not is_pitcher: pitches['PlateLocSide'] *= -1
    pitches['PlateLocSide'] = pitches['PlateLocSide']*12 + 8.5

    return pitches

def get_spraychart(pitches_inp, split=False, handedness='Right', is_pitcher=False):
    """
    Creates main spray chart shown on page 1.

    Input: pitches_inp (df), split (bool), handedness (str), is_pitcher (bool)
    Output: str
    """
    pitches = to_plate_coords(pitches_inp, is_pitcher)
    pitches = pitches.query(
        "(PlateLocSide > -1 & PlateLocSide < 18) & "
        "(PlateLocHeight > -1 & PlateLocHeight < 20.2)"
    )

    if split: pitches = pitches.query(f"BatterSide == '{handedness}'")

    pitch_types = list(pitches['PitchType'].unique())

    fig, axs = plt.subplots(figsize=(6, 6))
    draw_strike_zone(axs)

    for pitch in pitch_types:
        color = PITCH_COLOR_MAP.get(pitch, '#cccccc')
        for _, row in pitches.query(f"PitchType == '{pitch}'").iterrows():
            c = Circle((row['PlateLocSide'], row['PlateLocHeight']), radius = 1.43, facecolor=color, edgecolor='black', linewidth=1, alpha=0.7)
            axs.add_patch(c)
    
    if not split:
        x, y = -12.5, 15
        for p in pitch_types:
            color = PITCH_COLOR_MAP.get(p, '#cccccc')
            axs.text(x, y, p, fontsize=12, va='bottom')
            axs.add_patch(Circle((x-2.5, y+0.9), radius=1, facecolor=color, edgecolor='black', linewidth=1, alpha=0.7))
            y -= 3.6
        axs.set_xlim(-20, 22)
        axs.set_ylim(-5, 24.2)
    else:
        axs.set_xlim(-5, 22)
        axs.set_ylim(-3, 23)

    axs.set_aspect('equal')
    plt.axis('off')
    
    pid = int(pitches_inp.iloc[0]['PitcherId'])
    suffix = f"_{handedness[0]}" if split else ""
    filepath = f"static/images/pitcher{pid}_sc{suffix}_{date.today()}.png"
    plt.savefig(filepath)
    plt.close(fig)
    return filepath

def get_spraycharts_by_count(pitches_inp, is_pitcher=True):
    """
    Creates spray chart for each count. Boundaries are extended to allow for
    a larger sample.

    Input: pitches_inp (df), is_pitcher (bool)
    Output: dict
    """
    pitches = to_plate_coords(pitches_inp, is_pitcher)
    pitches = pitches.query(
        "(PlateLocSide > -4 & PlateLocSide < 21) & "
        "(PlateLocHeight > -4 & PlateLocHeight < 24)"
    )

    pid = int(pitches_inp.iloc[0]['PitcherId'])
    today = date.today()
    res = {}
    for (b, s) in ALL_COUNTS:
        temp = pitches.query(f"Balls == {b} & Strikes == {s}")

        fig, axs = plt.subplots(figsize=(3, 3))
        draw_strike_zone(axs)

        for _, row in temp.iterrows():
            color = PITCH_COLOR_MAP.get(row['PitchType'], '#cccccc')
            c = Circle((row['PlateLocSide'], row['PlateLocHeight']), radius=1.43, facecolor=color, edgecolor='black', linewidth=0.8, alpha=0.7)
            axs.add_patch(c)
        
        axs.set_xlim(-5, 22)
        axs.set_ylim(-3, 23)
        axs.set_aspect('equal')
        plt.axis('off')
        
        filepath = f"static/images/pitcher{pid}_sc_{b}{s}_{today}.png"
        plt.savefig(filepath, bbox_inches='tight', dpi=120)
        plt.close(fig)
        res[f"{b}-{s}"] = filepath
    
    return res

def get_heatmaps(pitches_inp, is_pitcher=False):
    """
    Creates location-density heatmap for each pitch type.

    Input: pitches_input (df), is_pitcher (bool)
    Output: dict
    """
    pitches = to_plate_coords(pitches_inp, is_pitcher)

    pid = int(pitches_inp.iloc[0]['PitcherId'])
    today = date.today()
    heatmaps = {}
    for pitch in pitches['PitchType'].dropna().unique():
        target = pitches.query(f"PitchType == '{pitch}'")

        fig, axs = plt.subplots()
        sns.kdeplot(target, x='PlateLocSide', y='PlateLocHeight', fill=True, cmap='coolwarm')
        axs.scatter(target['PlateLocSide'], target['PlateLocHeight'], color='green', marker='o')
        draw_strike_zone(axs)

        axs.set_xlim(-7, 24)
        axs.set_ylim(-7, 26.2)
        axs.set_aspect('equal')
        plt.axis('off')

        filepath = f"static/images/pitcher{pid}_{pitch}_heatmap_{today}.png"
        plt.savefig(filepath)
        plt.close(fig)
        heatmaps[pitch] = filepath
    
    return heatmaps

def setup_movement_prof(axs, is_pitcher=False):
    """
    Draws the movement profile chart template.

    Input: axs (matplotlib axes), is_pitcher (bool)
    Output: axs
    """
    r = 24
    while r > 0:
        axs.add_patch(Circle((0, 0), radius=r, facecolor='white', edgecolor='black'))
        r -= 8
    
    verts = [(0, 24), (0, -24), (-24, 0), (24, 0)]
    codes = [Path.MOVETO, Path.LINETO, Path.MOVETO, Path.LINETO]
    axs.add_patch(patches.PathPatch(Path(verts, codes), edgecolor='black', facecolor='none', lw=2))

    top_label = "1B < MOVES TOWARD > 3B" if is_pitcher else "3B < MOVES TOWARD > 1B"
    plt.text(0, 25, top_label, ha='center', va='bottom')
    plt.text(-7.5, 0, "8\"", ha='left', va='bottom')
    plt.text(-15.5, 0, "16\"", ha='left', va='bottom')
    plt.text(-23.5, 0, "24\"", ha='left', va='bottom')

    return axs

def get_movement_prof(pitches_inp, is_pitcher=False):
    """
    Generates movement profile chart per pitch along with table of specific datapoints.

    Input: pitches_inp (df), is_pitcher (bool)
    Output: tuple
    """
    pitches = pitches_inp[['PitchType', 'HorzBreak', 'InducedVertBreak', 'SpinRate']].copy()
    if not is_pitcher: pitches['HorzBreak'] *= -1
    pitch_types = list(pitches['PitchType'].dropna().unique())

    fig, axs = plt.subplots()
    setup_movement_prof(axs, is_pitcher)

    def max_abs(s): 
        s = s.dropna()
        if s.empty: return float('nan')
        return s.loc[s.abs().idxmax()]

    mvmt = (
        pitches.groupby('PitchType')
        .agg(
            AvgHorzBreak = ('HorzBreak', 'mean'),
            MaxHorzBreak = ('HorzBreak', max_abs),
            AvgVertBreak = ('InducedVertBreak', 'mean'),
            MaxVertBreak = ('InducedVertBreak', max_abs),
            AvgSpinRate = ('SpinRate', 'mean'),
            MaxSpinRate = ('SpinRate', 'max')
        )
        .reset_index()
        .set_index('PitchType')
    )

    pitch_info = []
    x, y = 30, 15
    for i, pitch in enumerate(pitch_types):
        if pitch not in PITCH_COLOR_MAP: PITCH_COLOR_MAP[pitch] = to_hex(cmap(len(PITCH_COLOR_MAP)))
        color = PITCH_COLOR_MAP[pitch]

        for _, row in pitches.query(f"PitchType == '{pitch}'").iterrows():
            axs.add_patch(Circle((row['HorzBreak'], row['InducedVertBreak']), radius=1, facecolor=color, edgecolor='none', alpha=0.5))
        
        avg = mvmt.loc[pitch]
        axs.add_patch(Circle((avg['AvgHorzBreak'], avg['AvgVertBreak']), radius=3, facecolor=color, edgecolor='black', alpha=0.8))

        pitch_info.append({
            'pitch' : pitch,
            'avg_spin' : f"{avg['AvgSpinRate']:0.2f}",
            'max_spin' : f"{avg['MaxSpinRate']:0.2f}",
            'avg_hb' : f"{avg['AvgHorzBreak']:0.2f}",
            'max_hb' : f"{avg['MaxHorzBreak']:0.2f}",
            'avg_vb' : f"{avg['AvgVertBreak']:0.2f}",
            'max_vb' : f"{avg['MaxVertBreak']:0.2f}"
        })

        axs.text(x, y, pitch, fontsize=12, va='bottom')
        axs.add_patch(Circle((x-2.5, y+1.35), radius=1, facecolor=color, edgecolor='black', linewidth=1))
        y -= 3.6

    axs.set_xlim(-28, 45.5)
    axs.set_ylim(-28, 28)
    axs.set_aspect('equal')
    plt.axis('off')

    pid = int(pitches_inp.iloc[0]['PitcherId'])
    filepath = f"static/images/pitcher{pid}_mvmtprof_{date.today()}.png"
    plt.savefig(filepath)
    plt.close(fig)
    return filepath, pitch_info

def get_pop_times(pitches, td=trackman_data):
    """
    Retrieves pop times for all catchers on the pitcher's team.

    Input: pitches (df), td (df)
    Output: list of dicts
    """
    team = pitches.iloc[0]['PitcherTeam']
    catchers = (
        td.query(f"CatcherTeam == '{team}'")
        .groupby('Catcher')
        .agg(
            NumPitches = ('PopTime', 'count'),
            AvgPopTime = ('PopTime', 'mean'),
            MinPopTime = ('PopTime', 'min')
        )
        .sort_values(by='NumPitches', ascending=False)
        .reset_index()
        .dropna(subset=['AvgPopTime'])
    )

    res = []
    for _, row in catchers.iterrows():
        last, first = row['Catcher'].split(', ', 1)
        res.append({
            'name' : f"{first} {last}",
            'avg_pop' : row['AvgPopTime'],
            'min_pop' : row['MinPopTime']
        })
    
    return res

def build_report(
        name, handedness, team, pitch_types, stats, usages, ops,
        velocities, tendencies, spraycharts, heatmaps, mvmt_prof,
        pitch_details, catchers
):
    """
    Assembles every computed section into a single dict that is rendered into
    a pdf report by the template.

    Input: too many
    Output: dict
    """
    stats_list = [{'stat' : stat, 'value' : value} for (stat, value) in stats]

    heatmap_info = []
    for pitch in pitch_types:
        usage = usages['main'].get(pitch)
        velo = velocities.get(pitch)
        image = heatmaps.get(pitch)
        if usage is None or velo is None or image is None:
            print(f"Skipping {pitch}: missing usage, velocity, or heatmap data.")
            continue
        heatmap_info.append({
            'pitch' : pitch,
            'usage' : usage,
            'image' : image,
            'vavg' : velo['avg'],
            'vmin' : velo['min'],
            'vmax' : velo['max']
        })
    heatmap_info.sort(key=lambda h: h['usage'], reverse=True)

    if pitch_details:
        detail_by_pitch = {d['pitch'] : d for d in pitch_details}
        pitch_details = [detail_by_pitch[h['pitch']] for h in heatmap_info if h['pitch'] in detail_by_pitch]

    return {
        'player' : {'name' : name, 'position' : handedness, 'team' : team},
        'stats' : stats_list,
        'tendencies' : tendencies,
        'spraycharts' : spraycharts,
        'heatmaps' : heatmap_info,
        'split_usages' : {
            'r' : usages['r'],
            'r_avg' : f"{ops['r']:0.3f}",
            'l' : usages['l'],
            'l_avg' : f"{ops['l']:0.3f}"
        },
        'mvmtprof' : mvmt_prof,
        'pitchdetails' : pitch_details,
        'catchers' : catchers,
        'pitch_colors' : dict(PITCH_COLOR_MAP),
        'date' : date.today()
    }

def export_report(report, template_name, label, name):
    """
    Renders pdf report through the template, writing both an HTML copy and PDF version.

    Input: report (dict), template_name (str), label (str), player_name (str)
    Output: void
    """
    env = Environment(loader=FileSystemLoader("templates"))
    html = env.get_template(template_name).render(report=report)

    tempname = name.replace(" ", "")
    today = date.today()
    html_path = f"output/html_output/{tempname}_{label}_{today}.html"
    pdf_path = f"output/pdf_output/{tempname}_{label}_{today}.pdf"

    with open(html_path, 'w') as f: f.write(html)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"file://{os.path.abspath(html_path)}")
        page.wait_for_timeout(1000)
        page.pdf(path=pdf_path, format='Letter', landscape=True, print_background=True)
        browser.close()
    
    print(f"Report exported: {pdf_path}")

def create_report(pid, report_type, game_date=None, td=trackman_data):
    """
    Generates scouting report for one pitcher.

    Input: pid (int), report_type (str), game_date (str), td (df)
    Output: void
    """
    if report_type not in REPORT_TYPES:
        raise ValueError(f"Unknown report_type: '{report_type}'. Choose from {list(REPORT_TYPES)}.")
    config = REPORT_TYPES[report_type]

    pitches = td.query(f"PitcherId == {pid}")
    if pitches.empty: raise ValueError("No pitches found for given PitcherId.")

    if game_date is not None:
        if not config['allows_date_filter']: raise ValueError(f"Date filtering isn't supported for '{report_type}' reports.")
        mm, dd = (part.zfill(2) for part in game_date.split('-'))
        pitches = pitches.query(f"Date == '{date.today().year}-{mm}-{dd}'")
        if pitches.empty: raise ValueError("No pitches found for given PitcherId on given date.")

    is_pitcher_view = config['is_pitcher_view']
    name, team, handedness, pitch_types = player_info(pitches)
    if game_date is not None: name = f"{name} - {game_date}"

    stats = get_stats(pitches)
    usages_main, velocities = usage_velo(pitches)
    usages = {
        'main' : usages_main,
        'r' : None,
        'l' : None
    }
    ops = {
        'r' : 0.0,
        'l' : 0.0
    }
    
    if config['needs_splits']:
        usages['r'], _ = usage_velo(pitches, split=True, handedness='Right')
        usages['l'], _ = usage_velo(pitches, split=True, handedness='Left')
        ops['r'] = get_ops(pitches, split=True, handedness='Right')
        ops['l'] = get_ops(pitches, split=True, handedness='Left')
    
    tendencies, strike_rate = get_tendencies(pitches, is_pitcher=is_pitcher_view)
    stats.append(('STR%', f"{strike_rate:0.2f}%"))

    spraycharts = {
        'main' : get_spraychart(pitches, is_pitcher=is_pitcher_view),
        'r' : None,
        'l' : None
    }
    if config['needs_splits']:
        spraycharts['r'] = get_spraychart(pitches, split=True, handedness='Right', is_pitcher=is_pitcher_view)
        spraycharts['l'] = get_spraychart(pitches, split=True, handedness='Left', is_pitcher=is_pitcher_view)

    heatmaps = get_heatmaps(pitches, is_pitcher=is_pitcher_view)
    mvmt_prof, pitch_details = get_movement_prof(pitches, is_pitcher=is_pitcher_view)
    catchers = get_pop_times(pitches, td) if config['needs_catchers'] else []

    report = build_report(
        name, handedness, team, pitch_types, stats, usages, ops,
        velocities, tendencies, spraycharts, heatmaps, mvmt_prof,
        pitch_details, catchers
    )

    export_report(report, config['template'], config['label'], name)
    print(f"{report_type.capitalize()} report generated for {name} (pid={pid})")

# CLI
HELP_TEXT = (
    "findpitcher <first> <last>\n"
    "  -> looks up a pitcher, then offers to generate a report:\n"
    "     C = coach, P = pitcher (prompts for a single-outing date), H = hitter-facing, B = coach + hitter-facing\n"
    "quit\n"
    "  -> exits\n"
)

def run_cli():
    """
    Simple CLI for users to interact and use the program.

    Input: none
    Output: void
    """
    print(HELP_TEXT)
    report_choices = {
        'c' : ['coach'],
        'p' : ['pitcher'],
        'h' : ['player'],
        'b' : ['coach', 'player']
    }

    while True:
        raw = input("Enter command (help for command list): ").strip().split()
        if not raw: continue

        cmd, args = raw[0].lower(), raw[1:]
        
        if cmd == 'quit': break
        elif cmd == 'help': print(HELP_TEXT)
        elif cmd == 'findpitcher':
            if len(args) < 2:
                print("Usage: findpitcher <first> <last>")
                continue
            pid = find_pitcher(args[0], args[1])
            if pid is None: continue
        
            choice = input(f"Generate report for {args[0]} {args[1]}? (P/C/H/B/N): ").strip().lower()
            report_types = report_choices.get(choice)
            if not report_types:
                print("No report generated.")
                continue

            try:
                for report_type in report_types:
                    if report_type == 'pitcher':
                        date_inp = input("Input specific date (MM-DD; if full season, put 'none'): ").strip()
                        create_report(pid, 'pitcher', game_date = None if date_inp.lower() == 'none' else date_inp)
                    else:
                        create_report(pid, report_type)
            except ValueError as e:
                print(f"Could not generate report: {e}")
        
        else:
            print("Command not recognized. Try 'help'.")

if __name__ == "__main__":
    run_cli()