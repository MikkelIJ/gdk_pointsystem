import pandas as pd
import glob
import re
import os
import argparse
import csv
import yaml
from calculate_points import calculate_points


class Player:
    def __init__(self, name, username=None, pdga_number=None):
        self.name = name
        self.username = username
        self.pdga_number = pdga_number
        self.day_points = {}  # date -> points or 'DUP' or 'DNP'

    def add_points(self, date, points, username=None, pdga_number=None):
        # record points and update identifiers if provided
        self.day_points[date] = points
        if username:
            self.username = username
        if pdga_number:
            self.pdga_number = pdga_number

    def get_row(self, round_dates):
        # build row: name, username, pdga_number, points per date, total of counted points
        per_day = []
        total = 0
        for d in round_dates:
            val = self.day_points.get(d, "DNP")
            per_day.append(val)
            if isinstance(val, int):
                total += val
        return [self.name, self.username, self.pdga_number] + per_day + [total]


def load_event_dates(yaml_path):
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
    # supports both dict and list structures for events and normalizes to "MM-DD-YYYY"
    events = data.get("events", {})
    dates = []
    if isinstance(events, dict):
        for v in events.values():
            if isinstance(v, dict) and "date" in v and v["date"]:
                dates.append(str(v["date"]).replace("/", "-"))
    elif isinstance(events, list):
        for v in events:
            if isinstance(v, dict) and "date" in v and v["date"]:
                dates.append(str(v["date"]).replace("/", "-"))
    return dates


def process_leaderboard(
    exports_folder="exports",
    output_csv="leaderboard.csv",
    sheet_name="Pool White - Round 1",
    season_yaml="seasons/summer_league.yml",
):
    # Load round dates from season YAML
    round_dates = load_event_dates(season_yaml)

    # Collect all Excel files recursively from exports folder
    files = glob.glob(os.path.join(exports_folder, "**", "*.xlsx"), recursive=True)

    players = {}

    for file in files:
        # Skip previously generated leaderboard files
        if file.endswith("leaderboard.xlsx"):
            continue

        base = os.path.basename(file)
        m = re.search(r'event_(\d{2}-\d{2}-\d{4})', base)
        if not m:
            print(f"Could not find date in filename: {base}. Skipping.")
            continue
        # keep date format consistent with YAML: "MM-DD-YYYY"
        file_date = m.group(1)

        # Load the sheet
        try:
            df = pd.read_excel(file, sheet_name=sheet_name)
        except Exception as e:
            print(f"Failed to read '{sheet_name}' from {base}: {e}. Skipping.")
            continue

        if df.empty:
            print(f"Sheet '{sheet_name}' in {base} is empty. Skipping.")
            continue

        # Normalize column names: lower, non-alphanumerics -> underscore
        def norm(s):
            return re.sub(r'[^a-z0-9]+', '_', str(s).lower()).strip('_')

        col_map = {norm(c): c for c in df.columns}

        name_col = col_map.get("name")
        pos_col = col_map.get("position")
        pos_raw_col = col_map.get("position_raw")
        score_col = col_map.get("event_total_score")
        username_col = col_map.get("username")
        pdga_col = col_map.get("pdga_number")

        # Fallback: try to detect with simple lower() matching if normalization failed
        if not all([name_col, pos_raw_col, score_col]):
            for col in df.columns:
                low = str(col).lower()
                if not name_col and low == "name":
                    name_col = col
                if not pos_col and low == "position":
                    pos_col = col
                if not pos_raw_col and low == "position_raw":
                    pos_raw_col = col
                if not score_col and low == "event_total_score":
                    score_col = col
                if not username_col and low == "username":
                    username_col = col
                if not pdga_col and low == "pdga_number":
                    pdga_col = col

        if name_col is None or pos_raw_col is None or score_col is None:
            print(f"Could not find required columns in {base}. Skipping.")
            continue

        # Filter out duplicates only if 'position' exists
        if pos_col is not None:
            df = df[df[pos_col] != "DUP"]

        # Ensure numeric for sorting best round (lowest score)
        df[score_col] = pd.to_numeric(df[score_col], errors="coerce")
        df = df.dropna(subset=[score_col])

        # Pick best round per player (lowest total score)
        best_rounds = df.sort_values(by=score_col, ascending=True).groupby(name_col, as_index=False).first()

        for _, row in best_rounds.iterrows():
            name = row[name_col]
            position_raw = row[pos_raw_col]
            username = row[username_col] if username_col in row else None
            pdga_number = row[pdga_col] if pdga_col in row else None

            try:
                pos_int = int(position_raw)
                points = calculate_points(pos_int)
            except Exception:
                print(f"Invalid position_raw '{position_raw}' for {name} in {base}. Skipping row.")
                continue

            if name not in players:
                players[name] = Player(name, username, pdga_number)
            players[name].add_points(file_date, points, username, pdga_number)

    # Mark only top 5 scoring days as counted; others become 'DUP'
    for player in players.values():
        points_list = [(d, p) for d, p in player.day_points.items() if isinstance(p, int)]
        points_list.sort(key=lambda x: x[1], reverse=True)
        best_dates = set([d for d, _ in points_list[:5]])
        for d in list(player.day_points.keys()):
            if isinstance(player.day_points[d], int) and d not in best_dates:
                player.day_points[d] = "DUP"

    # Build leaderboard rows and write CSV
    leaderboard_rows = [player.get_row(round_dates) for player in players.values()]
    leaderboard_rows.sort(key=lambda x: x[-1], reverse=True)

    header = ["name", "username", "pdga_number"] + round_dates + ["total_score"]
    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(leaderboard_rows)
    print(f"Leaderboard saved to {output_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--sheet', type=str, default="Pool White - Round 1", help="Sheet name to process")
    parser.add_argument('--output', type=str, default="leaderboard.csv", help="Output CSV filename")
    parser.add_argument('--exports', type=str, default="exports", help="Folder containing exported xlsx files")
    parser.add_argument('--season', type=str, default="seasons/summer_league.yml", help="YAML file with season events")
    args = parser.parse_args()
    process_leaderboard(
        exports_folder=args.exports,
        output_csv=args.output,
        sheet_name=args.sheet,
        season_yaml=args.season,
    )