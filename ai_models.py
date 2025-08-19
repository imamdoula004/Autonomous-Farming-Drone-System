\
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

class AFDSAI:
    def __init__(self, random_state: int = 42):
        self.rng = np.random.default_rng(random_state)
        self.harvestable_classifier = RandomForestClassifier(n_estimators=80, random_state=random_state)
        self.care_classifier = RandomForestClassifier(n_estimators=80, random_state=random_state+1)
        self.yield_regressor = RandomForestRegressor(n_estimators=120, random_state=random_state+2)
        self._train()

    def _synth_row(self, n=12000):
        ndvi = self.rng.uniform(0, 1, n)
        moisture = self.rng.uniform(0, 1, n)
        nutrient = self.rng.uniform(0, 1, n)
        parasite = np.clip(self.rng.normal(0.1, 0.15, n), 0, 1)
        canopy_h = self.rng.uniform(0.1, 1.5, n)
        temp = self.rng.normal(28, 5, n)
        humidity = self.rng.uniform(40, 90, n)
        X = np.vstack([ndvi, moisture, nutrient, parasite, canopy_h, temp, humidity]).T
        harvestable = ((ndvi > 0.55) & (parasite < 0.35) & (canopy_h > 0.6)).astype(int)
        care = np.zeros(n, dtype=int)
        care[(moisture < 0.35) & (harvestable == 0)] = 1
        care[(nutrient < 0.45) & (harvestable == 0)] = 2
        care[(nutrient < 0.45) & (ndvi < 0.5) & (harvestable == 0)] = 3
        care[parasite > 0.45] = 4
        y = np.clip((ndvi * 0.8 + canopy_h * 0.3 - parasite * 0.5), 0, None) * 0.8
        return X, harvestable, care, y

    def _train(self):
        X, y_h, y_c, y_r = self._synth_row(n=12000)
        self.harvestable_classifier.fit(X, y_h)
        self.care_classifier.fit(X, y_c)
        self.yield_regressor.fit(X, y_r)

    def predict_all(self, features: np.ndarray) -> dict:
        X = features.reshape(1, -1)
        h = int(self.harvestable_classifier.predict(X)[0])
        c = int(self.care_classifier.predict(X)[0])
        y = float(self.yield_regressor.predict(X)[0])
        ndvi, moisture, nutrient, parasite, canopy_h, temp, humidity = features.tolist()
        water_pct = float(np.clip((0.6 - moisture) * 100, 0, 100))
        nutrient_pct = float(np.clip((0.7 - nutrient) * 100, 0, 100))
        fertilizer_pct = float(np.clip((0.65 - (ndvi * 0.8 + nutrient * 0.2)) * 150, 0, 100))
        parasite_pct = float(np.clip(parasite * 100, 0, 100))
        return {
            "harvestable": h,
            "care_label": c,
            "yield_sqft": max(0.0, y),
            "water_req_pct": water_pct,
            "nutrient_req_pct": nutrient_pct,
            "fertilizer_req_pct": fertilizer_pct,
            "parasite_pct": parasite_pct
        }
