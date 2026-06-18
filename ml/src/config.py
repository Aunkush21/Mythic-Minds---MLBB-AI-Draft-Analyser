import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
ML_DIR = ROOT_DIR / "ml"
DATA_RAW_DIR = ML_DIR / "data" / "raw"
DATA_PROCESSED_DIR = ML_DIR / "data" / "processed"
MODELS_DIR = ML_DIR / "models"

load_dotenv(ROOT_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

LANES = ["exp", "gold", "mid", "jungle", "roam"]
ROLES = ["Tank", "Fighter", "Assassin", "Mage", "Marksman", "Support"]
RANK_ORDER = [
    "Warrior", "Elite", "Master", "Grandmaster",
    "Epic", "Legend", "Mythic", "Mythical Glory",
]

RANDOM_SEED = 42
