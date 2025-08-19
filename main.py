\
import os, json
import numpy as np

from field import FieldConfig, FieldGrid
from ai_models import AFDSAI
from vision import synthesize_uhd_field, simple_object_recognition
from drone import DroneAPI, DroneSimulator
from database import DB
from utils import load_config, parse_command, deterministic_features_for_cell, CARE_LABELS, neighborhood_window, plot_3d_surface, env_snapshot

def ensure_dirs():
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("data", exist_ok=True)

def setup(cfg):
    ensure_dirs()
    img_path = os.path.join("data", "uhd_field.png")
    if not os.path.exists(img_path):
        print("[INIT] Generating synthetic UHD field image...")
        synthesize_uhd_field(save_path=img_path, seed=cfg["simulation"]["seed"])
    print("[INIT] Running simple object recognition on UHD image...")
    parasite_points = simple_object_recognition(img_path)
    print(f"[INFO] Found approx {len(parasite_points)} parasite patches (simulated).")
    print("[INIT] Training fast ML models (synthetic)...")
    ai = AFDSAI(random_state=cfg["simulation"]["seed"])
    fcfg = FieldConfig(**cfg["field"])
    field = FieldGrid(fcfg)
    drone = DroneSimulator(fcfg.max_x, fcfg.max_y, cfg["simulation"].get("obstacles", []))
    api = DroneAPI()
    db = DB(cfg["database"]["path"])
    return field, ai, drone, api, db

def matrix_value(ai: AFDSAI, x:int, y:int):
    feats = deterministic_features_for_cell(x,y)
    pred = ai.predict_all(feats)
    return pred["harvestable"], feats, pred

def cmd_situation(field, ai, db, x:int, y:int):
    if not field.in_bounds(x,y):
        print(f"[ERROR] Spot {x}x{y} is outside the field (max {field.cfg.max_x}x{field.cfg.max_y}).")
        return
    lat, lon = field.cell_center_geo(x,y)
    h, feats, preds = matrix_value(ai, x,y)
    db.log_observation(x,y,lat,lon,feats,preds)
    print(f"\n[ZONE {x}x{y}] GPS=({lat:.6f}, {lon:.6f})")
    print(f"  Matrix value (0/1 harvestable): {h}")
    print(f"  Care needed: {CARE_LABELS[preds['care_label']]}")
    print(f"  Yield estimate: {preds['yield_sqft']:.3f} kg/sqft")
    print("  Requirements (%): "
          f"water {preds['water_req_pct']:.0f}%, nutrients {preds['nutrient_req_pct']:.0f}%, "
          f"fertilizer {preds['fertilizer_req_pct']:.0f}%, parasite {preds['parasite_pct']:.0f}%")
    print(f"  Env snapshot: {env_snapshot()}")

def cmd_collect_soil(field, ai, drone, api, db, x:int, y:int):
    if not field.in_bounds(x,y):
        print(f"[ERROR] Spot {x}x{y} is outside the field.")
        return
    lat, lon = field.cell_center_geo(x,y)
    start = (drone.state.x, drone.state.y); goal = (x,y)
    path = drone.plan_path(start, goal)
    if path is None:
        print("[WARN] No collision-free path found (simulation).")
    else:
        print(f"[ROUTE] Steps: {len(path)}")
    api.go_to(x,y,lat,lon)
    api.collect_soil_sample()
    db.log_action("SOIL_SAMPLE", x,y, notes="Live soil sample requested")
    print("[OK] Soil sample collected (simulated).")

def cmd_seed_drop(field, ai, drone, api, db, kg:float, seed_type:str, x:int, y:int):
    if not field.in_bounds(x,y):
        print(f"[ERROR] Spot {x}x{y} is outside the field.")
        return
    h, feats, preds = matrix_value(ai, x,y)
    if h == 1:
        print(f"[ADVISORY] Zone {x}x{y} looks harvestable already (Matrix=1). Seeding skipped by policy.")
        db.log_action("SEED_SKIP", x,y,kg, notes=f"{seed_type} (area looks harvestable)")
        return
    lat, lon = field.cell_center_geo(x,y)
    start = (drone.state.x, drone.state.y); goal = (x,y)
    path = drone.plan_path(start, goal)
    if path is None:
        print("[WARN] No collision-free path found (simulation). Attempting direct flight.")
    else:
        print(f"[ROUTE] Steps: {len(path)}")
    api.go_to(x,y,lat,lon)
    api.seed_drop(kg, seed_type)
    db.log_action("SEED_DROP", x,y,kg, notes=f"{seed_type}")
    print(f"[OK] Dropped {kg:.2f} kg of {seed_type} seeds at {x}x{y}.")

def cmd_render3d(field, ai, db, cfg, x:int, y:int):
    if not field.in_bounds(x,y):
        print(f"[ERROR] Spot {x}x{y} is outside the field.")
        return
    k = cfg["visualization"]["neighborhood"]
    xs, ys = neighborhood_window(x,y,k)
    xs = [xx for xx in xs if 0 <= xx < field.cfg.max_x]
    ys = [yy for yy in ys if 0 <= yy < field.cfg.max_y]
    Z = np.zeros((len(ys), len(xs)), dtype=float)
    for i, yy in enumerate(ys):
        for j, xx in enumerate(xs):
            _, feats, preds = matrix_value(ai, xx, yy)
            Z[i,j] = preds["yield_sqft"]
    out = os.path.join("outputs", f"3d_{x}x{y}.png")
    path = plot_3d_surface(Z, title=f"3D Yield around {x}x{y}", save_path=out)
    print(f"[OK] Rendered 3D analysis to: {path}")

def cmd_metrics(field, ai, db):
    stride = max(1, field.cfg.max_x // 128)
    harvestable_count = 0; yield_sum = 0.0; samples = 0
    for y in range(0, field.cfg.max_y, stride):
        for x in range(0, field.cfg.max_x, stride):
            h, feats, preds = matrix_value(ai, x,y)
            harvestable_count += h; yield_sum += preds["yield_sqft"]; samples += 1
    avg_yield = yield_sum / samples if samples else 0.0
    total_cells = field.cfg.max_x * field.cfg.max_y
    est_harvestable_cells = int(harvestable_count * (total_cells / samples))
    total_harvest_potential = avg_yield * total_cells
    db.write_metrics(total_harvest_potential, None, avg_yield)
    print("[METRICS]")
    print(f"  Estimated harvestable sq-ft: {est_harvestable_cells:,} / {total_cells:,}")
    print(f"  Average yield per sq-ft: {avg_yield:.3f} kg")
    print(f"  Total harvest potential (field): {total_harvest_potential:,.0f} kg")

def print_help():
    print("""
Available commands:
  help
  exit
  situation zone <X>x<Y>
  collect soil zone <X>x<Y>
  drop <KG> kg <SEEDTYPE> seeds at <X>x<Y>
  render 3d <X>x<Y>
  metrics
Examples:
  situation zone 33x33
  collect soil zone 79x79
  drop 2 kg wheat seeds at 5900x15000
  render 3d 999x999
""")

def main():
    cfg = load_config("config.json")
    field, ai, drone, api, db = setup(cfg)
    print_help()
    while True:
        try:
            s = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[EXIT] Bye.")
            break
        cmd, args = parse_command(s)
        if cmd == "exit":
            print("[EXIT] Bye."); break
        elif cmd == "help":
            print_help()
        elif cmd == "situation":
            cmd_situation(field, ai, db, args["x"], args["y"])
        elif cmd == "collect_soil":
            cmd_collect_soil(field, ai, drone, api, db, args["x"], args["y"])
        elif cmd == "seed_drop":
            cmd_seed_drop(field, ai, drone, api, db, args["kg"], args["seed_type"], args["x"], args["y"])
        elif cmd == "render3d":
            cmd_render3d(field, ai, db, cfg, args["x"], args["y"])
        elif cmd == "metrics":
            cmd_metrics(field, ai, db)
        else:
            print("[ERROR] Unknown command. Type `help`.")

if __name__ == "__main__":
    main()
