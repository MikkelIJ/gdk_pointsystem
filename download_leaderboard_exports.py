import requests
import os

urls = [
        "https://udisc.com/events/kampen-on-den-gyldne-midrange-1-8-eg4lmf/leaderboard",
        "https://udisc.com/events/kampen-on-den-gyldne-midrange-2-8-HQ2TOo/leaderboard",
        "https://udisc.com/events/kampen-on-den-gyldne-midrange-3-8-RlWFKF/leaderboard",
        "https://udisc.com/events/kampen-on-den-gyldne-midrange-4-8-JXwQbn/leaderboard",
        "https://udisc.com/events/kampen-on-den-gyldne-midrange-5-8-YCJzg4/leaderboard",
        "https://udisc.com/events/kampen-on-den-gyldne-midrange-6-8-kpRQ7X/leaderboard",
        "https://udisc.com/events/kampen-on-den-gyldne-midrange-7-8-0hdute/leaderboard",
        "https://udisc.com/events/kampen-on-den-gyldne-midrange-8-8-AlorJX/leaderboard"
    ]

def download_leaderboard_exports(urls=urls, output_dir="exports"):
    os.makedirs(output_dir, exist_ok=True)
    for url in urls:
        export_url = url.rstrip('/') + '/export'
        # Extract event identifier
        parts = url.split('/')
        event_id = parts[4] if len(parts) > 4 else "unknown-event"
        # Map event identifier to date
        event_dates = {
            "kampen-on-den-gyldne-midrange-1-8-eg4lmf": "2025-07-06",
            "kampen-on-den-gyldne-midrange-2-8-HQ2TOo": "2025-07-13",
            "kampen-on-den-gyldne-midrange-3-8-RlWFKF": "2025-07-20",
            "kampen-on-den-gyldne-midrange-4-8-JXwQbn": "2025-07-27",
            "kampen-on-den-gyldne-midrange-5-8-YCJzg4": "2025-08-03",
            "kampen-on-den-gyldne-midrange-6-8-kpRQ7X": "2025-08-10",
            "kampen-on-den-gyldne-midrange-7-8-0hdute": "2025-08-17",
            "kampen-on-den-gyldne-midrange-8-8-AlorJX": "2025-08-24",
        }
        event_date = event_dates.get(event_id, "unknown-date")
        file_name = f"{event_id}-{event_date}.xlsx"
        file_path = os.path.join(output_dir, file_name)
        response = requests.get(export_url)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"Downloaded: {file_path}")
        else:
            print(f"Failed to download: {export_url} (Status: {response.status_code})")
