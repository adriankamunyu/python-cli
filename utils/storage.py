import json
import os
from models.user import User
from models.project import Project
from models.task import Task

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DATA_FILE = os.path.join(DATA_DIR, "tracker_data.json")


def ensure_data_dir():
    """Create the data directory if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)


def save_data():
    """Persist all users (with their projects and tasks) to JSON."""
    ensure_data_dir()
    payload = [u.to_dict() for u in User.all_users]
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except OSError as e:
        raise RuntimeError(f"Could not write data file: {e}") from e


def load_data():
    """
    Load users (with their projects and tasks) from JSON.
    Resets the in-memory registries before loading so there are no duplicates.
    """
    # Reset everything before loading
    User.clear_registry()
    # Reset ID counters so they start from 1 (from_dict will advance them)
    Project._id_counter = 1
    Task._id_counter = 1

    if not os.path.exists(DATA_FILE):
        return  # nothing to load yet

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise RuntimeError(
            f"Could not read data file ({DATA_FILE}): {e}\n"
            "The file may be corrupted. Delete it to start fresh."
        ) from e

    for user_data in payload:
        user = User.from_dict(user_data)
        User.register(user)
