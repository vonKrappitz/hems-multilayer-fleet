# SPDX-License-Identifier: Apache-2.0
"""
Part II / Air Medical Journal — reproduces the fixed-wing (Cessna Grand Caravan EX)
base placement. The 3 long-range bases are placed by a population-weighted p-median
on the same WorldPop 2020 raster used for the rescue helicopters, with the candidate
set restricted to the network hub airports (the 7 CRL Regional Centers), because a
fixed-wing aircraft needs a hub-grade runway. The objective minimizes the
population-weighted distance from each inhabited cell to its nearest of 3 bases.
Classic p-median (Hakimi 1964; ReVelle and Swain 1970). Distances in EPSG:2180 (m).
"""
import json, numpy as np, rasterio, pyproj
from pathlib import Path
HERE = Path(__file__).resolve().parent
from itertools import combinations

f = lambda s: float(str(s).replace(",", "."))
d = json.load(open(HERE / "loc28.json"))
# candidate fixed-wing bases = 7 CRL hub airports (network HEMS infrastructure)
hubs = [(r[1], f(r[8]), f(r[9])) for r in d if r[0] == "CRL"]
names = [h[0] for h in hubs]

tr = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:2180", always_xy=True)
hxy = np.array([tr.transform(lo, la) for _, la, lo in hubs])

with rasterio.open(str(HERE / "geo" / "pl_pop_1km.tif")) as src:
    pop = src.read(1).astype(float); T = src.transform; crs = src.crs; nod = src.nodata
pop[~np.isfinite(pop)] = 0
if nod is not None: pop[pop == nod] = 0
pop[pop < 0] = 0
rows, cols = np.where(pop > 0)
w = pop[rows, cols]
xs = T.c + (cols + 0.5) * T.a + (rows + 0.5) * T.b
ys = T.f + (cols + 0.5) * T.d + (rows + 0.5) * T.e
if crs and crs.to_epsg() != 2180:
    trc = pyproj.Transformer.from_crs(crs, "EPSG:2180", always_xy=True)
    xs, ys = trc.transform(xs, ys)
cells = np.c_[xs, ys]

# distance (km) from every inhabited cell to every hub
dist = np.sqrt(((cells[:, None, :] - hxy[None, :, :]) ** 2).sum(2)) / 1000.0

def cost(tri):
    return float((w * dist[:, list(tri)].min(1)).sum())

best, bt = 9e18, None
for tri in combinations(range(len(hubs)), 3):
    c = cost(tri)
    if c < best: best, bt = c, tri

print(f"inhabited cells: {len(w):,}   population: {w.sum():,.0f}")
print("candidate CRL hubs:", ", ".join(names))
print("\np-median (population-weighted) fixed-wing bases:")
print("  ", ", ".join(names[b] for b in bt))
print(f"  objective (pop-weighted Mkm): {best/1e6:,.1f}")
# margin: show the best alternative for the southern slot
alt = sorted(((cost(t), t) for t in combinations(range(len(hubs)), 3)))[:3]
print("\ntop-3 base triples by objective:")
for c, t in alt:
    print(f"  {', '.join(names[b] for b in t):32s} {c/1e6:,.1f}")
