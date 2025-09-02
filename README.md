# Autonomous Farming Drone System (AFDS) — Simulation

This is a runnable **simulation + reference implementation** for an agricultural project named **Autonomous Farming Drone System** (AFDS).
It focuses on a **square-foot Matrix** representation of the field (0 = no crop, 1 = harvestable crop), UHD camera "object recognition" (simulated),
precise **geo-positioning** for any square-foot `x × y`, **autonomous seed dropping** decisions, **soil sampling**, and a **3D analysis image** renderer.

It is designed to run locally on your laptop and be extendable to real drone hardware (MAVLink/ROS) later.

## ✨ Features

- **UHD Camera Object Recognition (Simulated)**  
  Identifies harvestable crops, nutrient deficiencies, and parasites in field zones.

- **Matrix-Based Field System**  
  Each square foot of the field is mapped into a **matrix grid**:  
  - `0` → empty (ready for seed drop)  
  - `1` → full harvestable crop  

- **3D Visualization**  
  Generates realistic 3D plots of field conditions for analysis.

- **Autonomous Seed & Fertilizer Dropping (Simulated)**  
  Based on matrix zones requiring attention.

- **Soil Sample Analysis (Simulated)**  
  Mimics real-time soil data collection and analysis.

- **Geopositioning System**  
  Pinpoints exact locations (`x, y`) in the matrix and maps them to GPS coordinates.

- **Database System (SQLite)**  
  Stores:  
  - Crop health metrics  
  - Fertilization & nutrient needs  
  - Parasite detection  
  - Soil status  
  - Historical yield comparisons  
  - Environmental factors (temp, humidity, etc.)

- **Command-based Interface**  
  Example commands you can run:
  ```
  situation zone 33x33
  collect soil zone 79x79
  drop 2 kg wheat seeds at 5900x15000
  render 3d 999x999
  metrics
  ```

---

## 🛠️ Installation & Setup

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/Autonomous-Farming-Drone-System.git
cd Autonomous-Farming-Drone-System
```

### 2. Create a virtual environment
#### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

#### macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the system
```bash
python main.py
```

---

## 📊 Example Outputs

- **3D Field Visualization** → stored in `outputs/`  
  Example:  
  ![3D Field Example](docs/sample_3d.png)

- **Database File** → `afds.sqlite3` (auto-generated on first run)  

- **Console Commands**:
  ```
  > situation zone 33x33
  Zone 33x33: Healthy crop detected. No parasite risk. Nutrient level optimal.
  ```

---

## ⚡ Tech Stack

- **Python 3.10+**
- **NumPy, Pandas** (matrix + data handling)  
- **Matplotlib** (3D visualization)  
- **SQLite3** (database system)  
- **Scikit-learn (Dummy AI models)** for classification & prediction  

---

## 📌 Future Enhancements

- Real integration with agricultural drones (via **MAVLink/DroneKit**).  
- Object detection with **YOLOv8 / Detectron2** on UHD images.  
- IoT soil sensor data ingestion.  
- Reinforcement learning for optimal seed/fertilizer dropping.  
- Mobile dashboard for farmers.  

---

## 📖 License
This project is released under the **MIT License**.

---

## 🤝 Contribution
PRs and ideas are welcome! Fork the repo, create a feature branch, and open a pull request.  

---

## 🌍 Author
Developed by **Imam** — exploring AI + Agriculture 🚀
