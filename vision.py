\
import numpy as np
from PIL import Image, ImageFilter

def synthesize_uhd_field(width=3840, height=2160, seed=42, save_path="uhd_field.png"):
    rng = np.random.default_rng(seed)
    base = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        vigor = int(120 + 80 * np.sin(y / 180.0) + 15 * rng.normal())
        base[y, :, 1] = np.clip(vigor, 20, 220)
    for x in range(100, width, 300):
        base[:, x:x+2, 2] = 180
    for _ in range(50):
        cx = rng.integers(0, width)
        cy = rng.integers(0, height)
        r = rng.integers(8, 60)
        yy, xx = np.ogrid[-cy:height-cy, -cx:width-cx]
        mask = xx*xx + yy*yy <= r*r
        base[mask, 0] = 200
    img = Image.fromarray(base, 'RGB').filter(ImageFilter.GaussianBlur(radius=1.2))
    img.save(save_path)
    return save_path

def simple_object_recognition(image_path):
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img)
    red = arr[:, :, 0].astype(np.int32)
    green = arr[:, :, 1].astype(np.int32)
    blue = arr[:, :, 2].astype(np.int32)
    mask = (red > green + 40) & (red > blue + 40)
    ys, xs = np.where(mask)
    points = []
    if len(xs) > 0:
        step = 50
        for xbin in range(0, arr.shape[1], step):
            for ybin in range(0, arr.shape[0], step):
                sub = (xs >= xbin) & (xs < xbin+step) & (ys >= ybin) & (ys < ybin+step)
                if np.any(sub):
                    cx = float(xs[sub].mean())
                    cy = float(ys[sub].mean())
                    points.append((cx, cy))
    return points
