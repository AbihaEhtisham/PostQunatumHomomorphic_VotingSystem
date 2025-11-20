import json
import os
from datetime import datetime

# Get the directory where THIS utils.py file exists
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Full absolute paths
CONFIG_FILE = os.path.join(BASE_DIR, "election_config.json")
AGENT_KEYS_FILE = os.path.join(BASE_DIR, "agent_keys.json")


def is_voting_open():
    with open(CONFIG_FILE, 'r') as f:
        cfg = json.load(f)

    start = datetime.fromisoformat(cfg['start_time'])
    end = datetime.fromisoformat(cfg['end_time'])
    now = datetime.now()

    return start <= now <= end


def verify_agent_key(station_id, key_input):
    with open(AGENT_KEYS_FILE, 'r') as f:
        keys = json.load(f)

    correct_key = keys.get(station_id)
    return correct_key == key_input
