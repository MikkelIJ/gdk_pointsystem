import requests
import os
import argparse
from seasons.load_season import load_events

def download_leaderboard_exports(events, output_dir="exports"):
    os.makedirs(output_dir, exist_ok=True)
    for event in events:
        url = event["url"]
        date = event["date"]
        export_url = url.rstrip('/') + '/export'
        file_name = f"event_{date.replace('/', '-')}.xlsx"
        file_path = os.path.join(output_dir, file_name)
        response = requests.get(export_url)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"Downloaded: {file_path}")
        else:
            print(f"Failed to download: {export_url} (Status: {response.status_code})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--season', type=str, default="seasons/summer_league.yml", help="Path to season YAML file")
    args = parser.parse_args()
    events = load_events(args.season)
    download_leaderboard_exports(events, output_dir="exports")