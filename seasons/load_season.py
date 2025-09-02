import yaml

def load_events(yaml_path):
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
    return [{"url": event["url"], "date": event["date"]} for event in data["events"].values()]
