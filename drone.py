\
from __future__ import annotations
import heapq
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class DroneState:
    x: int = 0
    y: int = 0
    battery_pct: float = 100.0

class DroneAPI:
    def go_to(self, x: int, y: int, lat: float, lon: float):
        print(f"[DRONE] Navigating to cell ({x},{y}) @ lat={lat:.6f}, lon={lon:.6f}")

    def seed_drop(self, kg: float, seed_type: str):
        print(f"[DRONE] Dropping {kg:.2f} kg of {seed_type} seeds")

    def collect_soil_sample(self):
        print("[DRONE] Collecting soil sample...")

class DroneSimulator:
    def __init__(self, max_x: int, max_y: int, obstacles: List[Tuple[int,int,int,int]] | None = None):
        self.state = DroneState()
        self.max_x = max_x
        self.max_y = max_y
        self.obstacles = obstacles or []

    def is_blocked(self, x:int, y:int) -> bool:
        for x1,y1,x2,y2 in self.obstacles:
            if x1 <= x <= x2 and y1 <= y <= y2:
                return True
        return False

    def neighbors(self, x:int, y:int):
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < self.max_x and 0 <= ny < self.max_y and not self.is_blocked(nx, ny):
                yield nx, ny

    def plan_path(self, start:Tuple[int,int], goal:Tuple[int,int]) -> Optional[List[Tuple[int,int]]]:
        sx, sy = start
        gx, gy = goal
        open_set = [(0, sx, sy)]
        came = {}
        gscore = {(sx, sy): 0}
        def h(a,b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
        closed = set()
        while open_set:
            _, x, y = heapq.heappop(open_set)
            if (x,y) == (gx,gy):
                path = [(x,y)]
                while (x,y) in came:
                    x,y = came[(x,y)]
                    path.append((x,y))
                return path[::-1]
            if (x,y) in closed: 
                continue
            closed.add((x,y))
            for nx, ny in self.neighbors(x,y):
                tentative = gscore[(x,y)] + 1
                if (nx,ny) not in gscore or tentative < gscore[(nx,ny)]:
                    came[(nx,ny)] = (x,y)
                    gscore[(nx,ny)] = tentative
                    f = tentative + h((nx,ny),(gx,gy))
                    heapq.heappush(open_set, (f, nx, ny))
        return None
