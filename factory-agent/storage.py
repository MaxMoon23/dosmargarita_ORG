"""
storage.py — the "filing cabinet" for the factory agent.

Nothing in here talks to Claude or the internet. This file only knows how
to read and write our two data files:

  data/activity_log.json  -> every interaction and order we've logged
  data/tasks.json          -> every to-do / reminder

Why JSON files instead of a real database? Because a database is another
moving part that can break or need a password. A JSON file is just a text
file your computer already knows how to open — you can even open it in a
text editor and read it yourself. That matches the "keep it simple and
durable" rule the whole dosmargarita_ORG repo follows.

Why keep this in its own file at all, instead of writing this code inside
tools.py? So that "how do we save data" and "what can the AI ask us to do"
stay separate. If you ever swap JSON files for a real database later, you'd
only need to rewrite THIS file — tools.py wouldn't have to change.
"""

import json
import os
import csv

# This is the folder this very file lives in (factory-agent/), so the paths
# below work no matter what folder you happen to run "python agent.py" from.
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

ACTIVITY_LOG_PATH = os.path.join(DATA_DIR, "activity_log.json")
TASKS_PATH = os.path.join(DATA_DIR, "tasks.json")
STORES_CSV_PATH = os.path.join(DATA_DIR, "stores.csv")


def _load_json_list(path):
    """Read a JSON file that holds a list of records. If it doesn't exist
    yet (first run), just return an empty list instead of crashing."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json_list(path, records):
    """Write a list of records back to a JSON file.

    indent=2 makes the file human-readable (nicely spaced out) if you ever
    open it yourself to peek at what's been logged.
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


def _next_id(records):
    """Every record gets a simple, ever-increasing whole number ID, like a
    receipt number. This just finds the highest ID used so far and adds 1,
    so IDs never repeat even as old entries pile up."""
    if not records:
        return 1
    return max(record["id"] for record in records) + 1


def load_activity_log():
    return _load_json_list(ACTIVITY_LOG_PATH)


def save_activity_log(records):
    _save_json_list(ACTIVITY_LOG_PATH, records)


def load_tasks():
    return _load_json_list(TASKS_PATH)


def save_tasks(records):
    _save_json_list(TASKS_PATH, records)


def load_stores():
    """Read data/stores.csv into a list of dictionaries (one dict per row,
    keyed by whatever column headers the CSV has).

    This file isn't something the agent writes — YOU put it here, by
    exporting the real Master Store List from Google Sheets:
    File -> Download -> Comma Separated Values (.csv), then saving it as
    factory-agent/data/stores.csv. Re-export it whenever the master list
    changes meaningfully; the agent just reads whatever's there.

    Returns an empty list (not an error) if the file hasn't been added yet
    — the tools that use this will explain what to do in that case.
    """
    if not os.path.exists(STORES_CSV_PATH):
        return []
    with open(STORES_CSV_PATH, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def find_column(fieldnames, *candidates):
    """Store spreadsheets get renamed over time ("Status" vs "Store Status"
    vs "State"), so instead of hardcoding one exact column name, we take a
    list of names we'd accept and match case-insensitively, ignoring extra
    spaces. Returns the real column name as it appears in the CSV, or None
    if nothing matched.
    """
    normalized = {name.strip().lower(): name for name in fieldnames}
    for candidate in candidates:
        match = normalized.get(candidate.strip().lower())
        if match:
            return match
    return None
