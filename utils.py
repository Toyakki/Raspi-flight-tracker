from dotenv import load_dotenv
from os import environ, replace, fsync
from os.path import exists
import math
from typing import Any, Optional
from pathlib import Path
from json import dump

def get_env(key: str) -> float:
    if not exists(".env"):
        raise Exception(".env file not found! Please create one.")
    
    if not load_dotenv(dotenv_path=".env"):
        raise Exception("Failed to parse .env file! Please fill it out using .env.example as a reference!")
    
    if key in environ:
        return environ[key]
    return Exception(f"WARNING: failed to parse env var {key}. Please fill it out!")

# Vibe coded cuz i can't be bothered.
def haversine_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))

# Vibe coded!
def norm_str(input_str: Any) -> Optional[str]:
    if not isinstance(input_str, str):
        return None
    input_str = input_str.strip().upper().replace(" ", "")
    return input_str or None

# Vibe coded!
def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        dump(payload, f)
        f.flush()
        fsync(f.fileno())

    replace(tmp, path)
