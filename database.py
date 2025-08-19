\
import sqlite3
from datetime import datetime

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS observations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT,
  x INTEGER, y INTEGER,
  lat REAL, lon REAL,
  ndvi REAL, moisture REAL, nutrient REAL, parasite REAL, canopy_h REAL,
  harvestable INTEGER,
  yield_sqft REAL,
  water_req_pct REAL, nutrient_req_pct REAL, fertilizer_req_pct REAL, parasite_pct REAL,
  temp_c REAL, humidity_pct REAL
);
CREATE TABLE IF NOT EXISTS actions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT,
  type TEXT,
  x INTEGER, y INTEGER,
  kg REAL,
  notes TEXT
);
CREATE TABLE IF NOT EXISTS metrics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT,
  total_harvest_potential REAL,
  efficiency_vs_prev_pct REAL,
  avg_yield_per_sqft REAL
);
"""

class DB:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self._init()

    def _init(self):
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def log_observation(self, x,y,lat,lon, feats, preds):
        ts = datetime.utcnow().isoformat()
        self.conn.execute("""INSERT INTO observations
            (ts,x,y,lat,lon,ndvi,moisture,nutrient,parasite,canopy_h,harvestable,yield_sqft,water_req_pct,nutrient_req_pct,fertilizer_req_pct,parasite_pct,temp_c,humidity_pct)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (ts,x,y,lat,lon,
             feats[0],feats[1],feats[2],feats[3],feats[4],
             preds["harvestable"],preds["yield_sqft"],
             preds["water_req_pct"],preds["nutrient_req_pct"],preds["fertilizer_req_pct"],preds["parasite_pct"],
             feats[5],feats[6]))
        self.conn.commit()

    def log_action(self, type_, x,y,kg=None, notes=""):
        ts = datetime.utcnow().isoformat()
        self.conn.execute("""INSERT INTO actions (ts,type,x,y,kg,notes) VALUES (?,?,?,?,?,?)""",
                          (ts,type_,x,y,kg,notes))
        self.conn.commit()

    def write_metrics(self, total_harvest_potential, efficiency_vs_prev_pct, avg_yield_per_sqft):
        ts = datetime.utcnow().isoformat()
        self.conn.execute("""INSERT INTO metrics (ts,total_harvest_potential,efficiency_vs_prev_pct,avg_yield_per_sqft)
                             VALUES (?,?,?,?)""",
                          (ts,total_harvest_potential,efficiency_vs_prev_pct,avg_yield_per_sqft))
        self.conn.commit()
