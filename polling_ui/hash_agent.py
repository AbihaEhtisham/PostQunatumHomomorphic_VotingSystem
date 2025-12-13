import bcrypt
import json

agents = {
    "101": "SuperSecurePass1!",
    "202": "UltraSecureKey2#",
    "303": "MegaSafePassword3$"
}

hashed_agents = {}
for agent_id, password in agents.items():
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    hashed_agents[agent_id] = hashed

with open("static/agents.json", "w") as f:
    json.dump(hashed_agents, f, indent=4)

print("Hashed agent credentials saved in static/agents.json")
