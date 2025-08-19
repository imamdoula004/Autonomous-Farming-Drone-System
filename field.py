\
import math
from dataclasses import dataclass

@dataclass
class FieldConfig:
    max_x: int = 4096
    max_y: int = 4096
    feet_per_cell: float = 1.0
    origin_lat: float = 23.8103
    origin_lon: float = 90.4125
    orientation_deg: float = 0.0

class FieldGrid:
    FEET_PER_DEG_LAT = 364000.0  # approximate conversion

    def __init__(self, cfg: FieldConfig):
        self.cfg = cfg

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.cfg.max_x and 0 <= y < self.cfg.max_y

    def cell_center_geo(self, x: int, y: int) -> tuple[float, float]:
        dx_feet = (x + 0.5) * self.cfg.feet_per_cell
        dy_feet = (y + 0.5) * self.cfg.feet_per_cell
        theta = math.radians(self.cfg.orientation_deg)
        east_feet = dx_feet*math.cos(theta) - dy_feet*math.sin(theta)
        north_feet = dx_feet*math.sin(theta) + dy_feet*math.cos(theta)
        lat = self.cfg.origin_lat + (north_feet / self.FEET_PER_DEG_LAT)
        feet_per_deg_lon = math.cos(math.radians(lat)) * self.FEET_PER_DEG_LAT
        lon = self.cfg.origin_lon + (east_feet / feet_per_deg_lon) if feet_per_deg_lon != 0 else self.cfg.origin_lon
        return lat, lon
