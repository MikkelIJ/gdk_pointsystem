import pandas as pd
import glob
import re
import os
from calculate_points import calculate_points


class Player:
    def __init__(self, name, username=None, pdga_number=None):
        self.name = name
        self.username = username
        self.pdga_number = pdga_number
        self.day_points = {}  # date -> points or 'DUP' or 'DNP'

    def add_points(self, date, points, username=None, pdga_number=None):
        self.day_points[date] = points
        if username:
            self.username = username
        if pdga_number:
            self.pdga_number = pdga_number

    def get_best_points(self, top_n=5):
        valid_points = [p for p in self.day_points.values() if isinstance(p, int)]
        best = sorted(valid_points, reverse=True)[:top_n]
        return sum(best)

    def get_row(self, round_dates):
        row = [self.name, self.username if self.username else "", self.pdga_number if self.pdga_number else ""]
        for d in round_dates:
            val = self.day_points.get(d, "DNP")
            row.append(val)
        row.append(self.get_best_points())
        return row

def process_leaderboard(exports_folder="exports", output_csv="leaderboard.csv", sheet_name=0):
    files = glob.glob(f"{exports_folder}/*.xlsx")
    players = {}
    round_dates = []  # dates expected is in format DD/MM/YYYY
    date_format = "%d/%m/%Y"
    for file in files:
        if file.endswith("leaderboard.xlsx"):
            continue
        # Extract full YYYY-MM-DD from filename reliably
        base = os.path.basename(file)
        m = re.search(r'(\d{4}-\d{2}-\d{2})', base)
        if not m:
            print(f"Could not find date in filename: {base}. Skipping.")
            continue
        raw_date = m.group(1)  # e.g., 2024-09-01

        # Convert to DD/MM/YYYY and record for header
        dt = pd.to_datetime(raw_date, format="%Y-%m-%d", errors="coerce")
        if pd.isna(dt):
            print(f"Unparseable date {raw_date} in {base}. Skipping.")
            continue
        formatted_date = dt.strftime(date_format)
        round_dates.append(formatted_date)
        try:
            df = pd.read_excel(file, sheet_name="Pool White - Round 1")
        except ValueError:
            print(f"Sheet 'Pool White - Round 1' not found in {file}. Skipping.")
            continue
        # Identify columns
        name_col = None
        pos_col = None
        pos_raw_col = None
        score_col = None
        username_col = None
        pdga_col = None
        for col in df.columns:
            if col.lower() == "name":
                name_col = col
            if col.lower() == "position":
                pos_col = col
            if col.lower() == "position_raw":
                pos_raw_col = col
            if col.lower() == "event_total_score":
                score_col = col
            if col.lower() == "username":
                username_col = col
            if col.lower() == "pdga_number":
                pdga_col = col
        if name_col is None or pos_raw_col is None or score_col is None:
            print(f"Could not find required columns in {file}")
            continue
        # Only keep rows where position is not DUP
        df = df[df[pos_col] != "DUP"]
        # For each player, keep only the best round (lowest event_total_score)
        best_rounds = df.sort_values(by=score_col).groupby(name_col, as_index=False).first()
        for _, row in best_rounds.iterrows():
            name = row[name_col]
            position_raw = row[pos_raw_col]
            username = row[username_col] if username_col else None
            pdga_number = row[pdga_col] if pdga_col else None
            points = calculate_points(int(position_raw))
            if name not in players:
                players[name] = Player(name, username, pdga_number)
            players[name].add_points(formatted_date, points, username, pdga_number)

    # Remove duplicate dates and sort
    round_dates = sorted(list(set(round_dates)), key=lambda x: pd.to_datetime(x, format=date_format, errors='coerce'))

    # For each player, mark rounds as DUP if not in their top 5
    for player in players.values():
        # Get all points as (date, value)
        points_list = [(d, p) for d, p in player.day_points.items() if isinstance(p, int)]
        # Sort by points descending
        points_list.sort(key=lambda x: x[1], reverse=True)
        best_dates = set([d for d, _ in points_list[:5]])
        for d in player.day_points:
            if isinstance(player.day_points[d], int) and d not in best_dates:
                player.day_points[d] = "DUP"

    # Build leaderboard rows
    leaderboard_rows = [player.get_row(round_dates) for player in players.values()]
    leaderboard_rows.sort(key=lambda x: x[-1], reverse=True)

    # Write to CSV
    header = ["name", "username", "pdga_number"] + round_dates + ["total_score"]
    import csv
    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(leaderboard_rows)
    print(f"Leaderboard saved to {output_csv}")
