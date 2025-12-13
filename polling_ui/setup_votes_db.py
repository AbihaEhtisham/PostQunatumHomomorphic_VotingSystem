from vote_manager import init_votes_db
import os

DB = os.path.join("votes.db")

print("Initializing:", DB)
init_votes_db(DB)
print("Done.")
