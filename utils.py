\
import re
import json
import math
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple

CARE_LABELS = {0: "none", 1:"water", 2:"nutrients", 3:"fertilizer", 4:"parasite"}

def load_config(path="config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def deterministic_features_for_cell(x:int, y:int) -> np.ndarray:
    import hashlib, numpy as np
    seed_bytes = hashlib.sha256(f"{x}:{y}".encode("utf-8")).digest()
    seed = int.from_bytes(seed_bytes[:8], "little", signed=False)
    rng = np.random.default_rng(seed)
    ndvi = np.clip(0.5 + 0.3*math.sin(x/2000) + 0.2*math.cos(y/1800) + 0.1*rng.normal(), 0, 1)
    moisture = np.clip(0.55 + 0.25*math.sin(y/700) - 0.2*math.cos(x/900) + 0.1*rng.normal(), 0, 1)
    nutrient = np.clip(0.6 + 0.2*math.cos(x/1200+y/1500) + 0.1*rng.normal(), 0, 1)
    parasite = np.clip(0.15 + 0.25*abs(math.sin(x/4000)+math.cos(y/3500)) + 0.1*abs(rng.normal()), 0, 1)
    canopy_h = np.clip(0.4 + 0.8*ndvi + 0.1*rng.normal(), 0.1, 1.8)
    temp = 26 + 6*math.sin((x+y)/5000) + rng.normal(0, 1.2)
    humidity = np.clip(55 + 25*math.cos(x/4500) + rng.normal(0, 4.0), 30, 95)
    return np.array([ndvi, moisture, nutrient, parasite, canopy_h, temp, humidity], dtype=float)

def parse_command(s: str):
    s = s.strip().lower()
    if s in ("exit", "quit", "q"): return ("exit", {})
    if s in ("help", "?"): return ("help", {})
    m = re.search(r"(situation|status).*(?:zone|spot)\s+(\d+)x(\d+)", s)
    if m:
        return ("situation", {"x":int(m.group(2)), "y":int(m.group(3))})
    m = re.search(r"(collect).*(?:soil|soil sample).*(?:zone|spot)\s+(\d+)x(\d+)", s)
    if m:
        return ("collect_soil", {"x":int(m.group(2)), "y":int(m.group(3))})
    m = re.search(r"drop\s+(\d+(?:\.\d+)?)\s*(?:kg|kilogram|kilograms)\s+(?:worth\s+of\s+)?([a-zA-Z0-9_-]+)\s+seeds.*(?:at|in|on)\s+(\d+)x(\d+)", s)
    if m:
        return ("seed_drop", {"kg":float(m.group(1)), "seed_type":m.group(2), "x":int(m.group(3)), "y":int(m.group(4))})
    m = re.search(r"(render|generate).*(3d).*(?:zone|spot)?\s*(\d+)x(\d+)", s)
    if m:
        return ("render3d", {"x":int(m.group(3)), "y":int(m.group(4))})
    if s.strip().startswith("metrics"):
        return ("metrics", {})
    return ("unknown", {"raw": s})

def neighborhood_window(center_x:int, center_y:int, k:int):
    assert k % 2 == 1, "Neighborhood size must be odd"
    half = k // 2
    xs = list(range(center_x - half, center_x + half + 1))
    ys = list(range(center_y - half, center_y + half + 1))
    return xs, ys

def plot_3d_surface(Z, title="3D Analysis", save_path="outputs/3d.png"):
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    import os
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111, projection='3d')
    X = np.arange(Z.shape[1]); Y = np.arange(Z.shape[0])
    X, Y = np.meshgrid(X, Y)
    ax.plot_surface(X, Y, Z, cmap="viridis", linewidth=0, antialiased=True)
    ax.set_title(title); ax.set_xlabel("Δx"); ax.set_ylabel("Δy"); ax.set_zlabel("Yield (kg/sqft)")
    fig.tight_layout(); fig.savefig(save_path, dpi=200)
    try: plt.show()
    except Exception: pass
    return save_path

def env_snapshot():
    import time, random
    return {
        "ts": time.time(),
        "temperature_c": round(26 + random.uniform(-2.5, 2.5), 2),
        "humidity_pct": round(60 + random.uniform(-10, 10), 1),
        "wind_mps": round(max(0, random.gauss(2.0, 0.7)), 2)
    }
