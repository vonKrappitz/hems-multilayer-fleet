"""
Figure 1 (Part II / Air Medical Journal): fleet dislocation map.
Journal-style, colourblind-safe (Okabe-Ito), distinct marker SHAPES (not colour alone),
minimal in-figure text (symbol key only; descriptive caption supplied separately),
Liberation Sans (Arial-equivalent) embedded, vector PDF + 600 dpi PNG.
"""
import numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent
import geopandas as gpd
from shapely.ops import unary_union
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import RegularPolygon
import pyproj

# --- AMJ artwork: allowed/look-alike font, embed as TrueType ---
plt.rcParams["font.family"] = "Liberation Sans"   # Arial-metric-compatible
plt.rcParams["pdf.fonttype"] = 42                  # embed TrueType (editable)
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["svg.fonttype"] = "none"

# Okabe-Ito colourblind-safe palette
C_H145 = "#0072B2"  # blue   - rescue
C_AW   = "#D55E00"  # vermilion - heavy MEDEVAC
C_CAR  = "#E69F00"  # orange - fixed-wing
C_H135 = "#009E73"  # green  - light transport

# bases: name, lat, lon, h145_count (0 = no rescue helicopter)
RESCUE = [
    ("Warsaw", 52.2297, 21.0122, 2), ("Kraków", 50.0647, 19.9450, 2),
    ("Wrocław", 51.1079, 17.0385, 2), ("Gdańsk", 54.3520, 18.6466, 1),
    ("Lublin", 51.2465, 22.5684, 1), ("Poznań", 52.4064, 16.9252, 1),
    ("Olsztyn", 53.7784, 20.4801, 1), ("Mirosławiec", 53.3963, 16.0833, 1),
    ("Białystok", 53.0942, 23.1700, 1), ("Sanok", 49.5917, 22.2106, 1),
    ("Łask", 51.5519, 19.1789, 2), ("Zielona Góra", 52.1356, 15.7986, 1),
    ("Toruń", 53.0451, 18.5556, 2), ("Ełk", 53.8636, 22.1681, 1),
    ("Gliwice", 50.2378, 18.6722, 3), ("Stargard", 53.308, 14.973, 1),
    ("Lubomierz", 51.296, 15.367, 1), ("Zamość", 50.7142, 23.1986, 1),
    ("Bytów", 54.1719, 17.4978, 1), ("Kielce", 50.8979, 20.7167, 1),
    ("Biała Podlaska", 52.0344, 23.1469, 1),
]
AW101  = {"Kraków", "Lublin", "Poznań", "Olsztyn"}               # 4 (p-centre optimum; matches related study)
CARAVAN = {"Warsaw", "Kraków", "Poznań"}                          # 3 (pop-weighted p-median over CRL hubs; caravan_basing.py)
H135   = {"Warsaw", "Kraków", "Wrocław", "Gdańsk", "Lublin",       # 9 (7 CRL + Kielce + Rzeszów)
          "Poznań", "Olsztyn", "Kielce"}
RZESZOW = ("Rzeszów", 50.1100, 22.0190)  # transport-only (H135), no rescue helicopter

# label offsets (points): keep clear of glyph clusters
LBL = {
    "Warsaw": (20, 0), "Kraków": (21, -2), "Wrocław": (20, 2),
    "Gdańsk": (20, -7), "Lublin": (12, -2), "Poznań": (14, -2),
    "Olsztyn": (12, 6), "Mirosławiec": (10, 7), "Białystok": (-12, 2, "right"),
    "Sanok": (-10, 2, "right"), "Łask": (14, -6),
    "Toruń": (18, 0), "Ełk": (-10, 5, "right"), "Gliwice": (-11, 8, "right"),
    "Zielona Góra": (2, -15, "center"),
    "Stargard": (0, -13, "center"), "Lubomierz": (10, 7),
    "Zamość": (-10, 2, "right"), "Bytów": (-10, -9, "right"), "Kielce": (12, -8),
    "Biała Podlaska": (-6, 0, "right"), "Rzeszów": (10, 2),
}

from shapely.geometry import Polygon, MultiPolygon
def drop_holes(g):
    if g.geom_type == "Polygon": return Polygon(g.exterior)
    if g.geom_type == "MultiPolygon": return MultiPolygon([Polygon(p.exterior) for p in g.geoms])
    return g
poland = gpd.read_file(str(HERE / "geo" / "gadm41_POL_2.json")).to_crs("EPSG:2180")
voiv = (poland.dissolve(by="NAME_1") if "NAME_1" in poland.columns else poland).reset_index(drop=True)
country = drop_holes(unary_union(voiv.geometry).buffer(0))
minx, miny, maxx, maxy = country.bounds
tr = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:2180", always_xy=True)
def xy(lat, lon): return tr.transform(lon, lat)

fig, ax = plt.subplots(figsize=(8.2, 7.4))
ax.set_facecolor("white")
# voivodeship outlines (light grey), country border (black)
try:
    vb = voiv.geometry.apply(drop_holes).simplify(250)
    vb.boundary.plot(ax=ax, color="#C8C8C8", linewidth=0.5, zorder=2)
except Exception:
    pass
gpd.GeoSeries([country.boundary]).plot(ax=ax, color="black", linewidth=1.1, zorder=3)

SIZE = {1: 360, 2: 540, 3: 720}
FS = {1: 10, 2: 12, 3: 13}

def square_ring(bx, by, color):
    # hollow square ring around a city = heavy MEDEVAC (AW101)
    ax.scatter(bx, by, s=1200, marker="s", facecolors="none",
               edgecolors=color, linewidths=2.0, zorder=6)

def small_glyph(bx, by, dx, dy, marker, color):
    ax.scatter(bx + dx, by + dy, s=150, marker=marker, c=color,
               edgecolors="white", linewidths=0.8, zorder=8)

OFF = 22000  # metres offset for secondary glyphs
for name, lat, lon, n in RESCUE:
    bx, by = xy(lat, lon)
    if name in AW101:
        square_ring(bx, by, C_AW)
    # rescue circle + count digit
    ax.scatter(bx, by, s=SIZE[n], marker="o", c=C_H145,
               edgecolors="white", linewidths=1.3, zorder=10)
    ax.text(bx, by, str(n), ha="center", va="center", color="white",
            fontsize=FS[n], fontweight="bold", zorder=11)
    if name in CARAVAN:
        small_glyph(bx, by, OFF, -OFF, "D", C_CAR)     # diamond SE
    if name in H135:
        small_glyph(bx, by, -OFF, OFF, "^", C_H135)    # triangle NW
    o = LBL.get(name, (10, 8))
    ha = o[2] if len(o) > 2 else "left"
    ax.annotate(name, (bx, by), xytext=(o[0], o[1]), textcoords="offset points",
                fontsize=8.5, ha=ha, va="center", color="black", zorder=12)

# transport-only base: Rzeszów (H135 only)
rbx, rby = xy(RZESZOW[1], RZESZOW[2])
ax.scatter(rbx, rby, s=150, marker="^", c=C_H135, edgecolors="white", linewidths=0.8, zorder=8)
o = LBL["Rzeszów"]
ax.annotate("Rzeszów", (rbx, rby), xytext=(o[0], o[1]), textcoords="offset points",
            fontsize=8.5, ha="left", va="center", color="black", zorder=12)

# --- symbol key (minimal text; no descriptive title on figure) ---
handles = [
    Line2D([0], [0], marker="o", color="w", markerfacecolor=C_H145, markeredgecolor="white",
           markersize=13, lw=0, label="HEMS rescue base, H145 (digit = no. of helicopters)"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="none", markeredgecolor=C_AW,
           markersize=15, lw=0, markeredgewidth=2, label="Heavy-MEDEVAC base, AW101 (ECMO-capable)"),
    Line2D([0], [0], marker="D", color="w", markerfacecolor=C_CAR, markeredgecolor="white",
           markersize=10, lw=0, label="Fixed-wing base, Cessna Grand Caravan EX"),
    Line2D([0], [0], marker="^", color="w", markerfacecolor=C_H135, markeredgecolor="white",
           markersize=11, lw=0, label="Light-transport base, H135"),
]
leg = ax.legend(handles=handles, loc="lower left", fontsize=8.2, framealpha=1.0,
                facecolor="white", edgecolor="#666666", borderpad=0.7, handletextpad=0.6)
leg.set_zorder(20)

ax.set_xlim(minx - 25000, maxx + 25000)
ax.set_ylim(miny - 25000, maxy + 25000)
ax.set_aspect("equal")
ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values():
    s.set_visible(False)

# --- automated collision check: labels vs base markers and national border ---
from shapely.geometry import Point as _P
import math as _m
fig.canvas.draw(); _r = fig.canvas.get_renderer(); _inv = ax.transData.inverted()
_dpi = fig.dpi
def _rpx(s): return (_m.sqrt(s)/2.0)*(_dpi/72.0)
_pts = []   # (name, px, py, radius_px)
for name, lat, lon, n in RESCUE:
    bx, by = xy(lat, lon); px, py = ax.transData.transform((bx, by))
    _pts.append((name, px, py, _rpx(1200) if name in AW101 else _rpx(SIZE[n])))
    if name in CARAVAN:
        gx2, gy2 = ax.transData.transform((bx+OFF, by-OFF)); _pts.append((name, gx2, gy2, _rpx(150)))
    if name in H135:
        gx2, gy2 = ax.transData.transform((bx-OFF, by+OFF)); _pts.append((name, gx2, gy2, _rpx(150)))
px, py = ax.transData.transform(xy(RZESZOW[1], RZESZOW[2])); _pts.append(("Rzeszów", px, py, _rpx(150)))
_iss = []
for t in ax.texts:
    lbl = t.get_text();  bb = t.get_window_extent(renderer=_r)
    if lbl.strip().isdigit() or len(lbl) > 60: continue   # skip count digits / legend text
    for nm, mx, my, r in _pts:
        if nm == lbl: continue
        ddx = max(bb.x0-mx, 0, mx-bb.x1); ddy = max(bb.y0-my, 0, my-bb.y1)
        if _m.hypot(ddx, ddy) <= r+1.5:
            _iss.append(f"napis '{lbl}' nachodzi na baze '{nm}'")
    for cx, cy in [(bb.x0,bb.y0),(bb.x1,bb.y0),(bb.x0,bb.y1),(bb.x1,bb.y1),((bb.x0+bb.x1)/2,(bb.y0+bb.y1)/2)]:
        gx_, gy_ = _inv.transform((cx, cy))
        if not country.buffer(500).contains(_P(gx_, gy_)):
            _iss.append(f"napis '{lbl}' wychodzi poza granice panstwa"); break
# label vs label
_tx=[(t.get_text(),t.get_window_extent(renderer=_r)) for t in ax.texts if not t.get_text().strip().isdigit() and len(t.get_text())<=60]
for _i in range(len(_tx)):
    for _j in range(_i+1,len(_tx)):
        a=_tx[_i][1]; b=_tx[_j][1]
        if a.x0<b.x1 and b.x0<a.x1 and a.y0<b.y1 and b.y0<a.y1:
            _iss.append(f"napisy '{_tx[_i][0]}' i '{_tx[_j][0]}' nachodza na siebie")
print("KOLIZJE:", "brak" if not _iss else "WYKRYTE")
for i in sorted(set(_iss)): print("  -", i)

pdf = str(HERE / "Figure1_fleet_dislocation_EN.pdf")
png = str(HERE / "Figure1_fleet_dislocation_EN.png")
plt.savefig(pdf, bbox_inches="tight", facecolor="white")           # vector, fonts embedded
plt.savefig(png, dpi=600, bbox_inches="tight", facecolor="white")  # high-res preview
plt.close()
import os
print("PDF:", round(os.path.getsize(pdf)/1024, 1), "kB | PNG:", round(os.path.getsize(png)/1024/1024, 2), "MB")
print("H145 total:", sum(n for *_, n in RESCUE))
