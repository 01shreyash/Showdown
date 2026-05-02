import json
import os

# Get the absolute path to the data folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'gen9ou-1695.json')

# Load Chaos data into memory when the server starts
try:
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        chaos_data = json.load(f)['data']
    print(f"✅ SUCCESS: Loaded {len(chaos_data)} Pokemon from Smogon dataset.")
except FileNotFoundError:
    print("❌ ERROR: Make sure gen9ou-1695.json is inside the backend/data/ folder.")
    chaos_data = {}

def normalize_name(name: str) -> str:
    """Normalize a Pokemon name for lookup: lowercase, no spaces, no hyphens."""
    return name.lower().replace(" ", "").replace("-", "")

# Build a normalized -> original key lookup map so we can find entries
# regardless of how the species name is cased/spaced in the paste.
# e.g. "greattusk" -> "Great Tusk", "ogerponwellspring" -> "Ogerpon-Wellspring"
chaos_lookup = {normalize_name(k): k for k in chaos_data.keys()}

def get_chaos_entry(species: str):
    """Return the chaos_data entry for a species name, or None if not found."""
    key = chaos_lookup.get(normalize_name(species))
    return chaos_data.get(key) if key else None

def extract_team_features(team_list: list) -> dict:
    """Calculates Average Usage and Team Synergy Score."""
    total_usage = 0.0
    synergy_score = 0.0

    # Calculate Usage
    for mon in team_list:
        entry = get_chaos_entry(mon['species'])
        if entry:
            total_usage += entry.get('usage', 0)

    avg_usage = total_usage / len(team_list) if team_list else 0

    # Calculate Synergy (Teammates correlation matrix sum).
    # The JSON field is "Teammates" (capital T), with original-cased keys.
    for i in range(len(team_list)):
        for j in range(i + 1, len(team_list)):
            entry1 = get_chaos_entry(team_list[i]['species'])
            mon2_norm = normalize_name(team_list[j]['species'])

            if entry1:
                teammates = entry1.get('Teammates', {})
                # Teammates keys use original casing, so normalize them for comparison
                for tm_name, weight in teammates.items():
                    if normalize_name(tm_name) == mon2_norm:
                        synergy_score += weight
                        break

    return {
        "average_meta_usage": round(avg_usage, 4),
        "team_synergy_score": round(synergy_score, 4)
    }