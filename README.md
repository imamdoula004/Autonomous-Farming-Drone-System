# Autonomous Farming Drone System (AFDS) — Simulation

This is a runnable **simulation + reference implementation** for an agricultural project named **Autonomous Farming Drone System** (AFDS).
It focuses on a **square-foot Matrix** representation of the field (0 = no crop, 1 = harvestable crop), UHD camera "object recognition" (simulated),
precise **geo-positioning** for any square-foot `x × y`, **autonomous seed dropping** decisions, **soil sampling**, and a **3D analysis image** renderer.

It is designed to run locally on your laptop and be extendable to real drone hardware (MAVLink/ROS) later.

## Quick Start (VSCode)

1. Install Python 3.10+
2. Create & activate a venv
3. `pip install -r requirements.txt`
4. `python main.py`

### Example commands
- `situation zone 33x33`
- `collect soil zone 79x79`
- `drop 2 kg wheat seeds at 5900x15000`
- `render 3d 999x999`
- `metrics`
