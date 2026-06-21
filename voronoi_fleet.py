"""
Part II / Air Medical Journal — reproduces the mission-load result and e-Table 1:
Voronoi (nearest-base) catchment population on the WorldPop 2020 raster for the
21 primary bases, converted to daily missions at the DRF rate (43.2 per 100,000/yr)
and divided by a single-aircraft capacity of 2.74 missions/day (rounded up) to give
the number of HEMS helicopters per base. Also prints the sensitivity grid.
"""
import json, math, numpy as np, rasterio, pyproj
from scipy.spatial import cKDTree

RATE_DRF=43.2; CAP=2.74
f=lambda s: float(str(s).replace(',','.'))
d=json.load(open("loc28.json"))
# 21 primary bases = 7 CRL + 14 CT (exclude Rzeszów, the 22nd/standby)
bases=[(r[1],f(r[8]),f(r[9])) for r in d
       if (r[0]=="CRL") or (r[0]=="CT" and "Rzeszów" not in r[1])]
names=[b[0] for b in bases]
tr=pyproj.Transformer.from_crs("EPSG:4326","EPSG:2180",always_xy=True)
bxy=np.array([tr.transform(lo,la) for _,la,lo in bases])
tree=cKDTree(bxy)

with rasterio.open("geo/pl_pop_1km.tif") as src:
    pop=src.read(1).astype(float); T=src.transform; crs=src.crs
    nod=src.nodata
pop[~np.isfinite(pop)]=0
if nod is not None: pop[pop==nod]=0
pop[pop<0]=0
rows,cols=np.where(pop>0)
vals=pop[rows,cols]
xs=T.c+(cols+0.5)*T.a+(rows+0.5)*T.b
ys=T.f+(cols+0.5)*T.d+(rows+0.5)*T.e
# reproject cell centroids to EPSG:2180 if raster not already in it
if crs and crs.to_epsg()!=2180:
    trc=pyproj.Transformer.from_crs(crs,"EPSG:2180",always_xy=True)
    xs,ys=trc.transform(xs,ys)
_,idx=tree.query(np.c_[xs,ys])
catch=np.zeros(len(bases))
for i,v in zip(idx,vals): catch[i]+=v

print(f"raster population total: {vals.sum():,.0f}")
order=np.argsort(-catch)
total=0
print(f"\n{'Base':22s}{'Catchment':>12s}{'Miss/day':>10s}{'Heli':>6s}")
for i in order:
    miss=catch[i]/1e5*RATE_DRF/365.0
    h=math.ceil(miss/CAP); total+=h
    print(f"{names[i]:22s}{catch[i]:>12,.0f}{miss:>10.2f}{h:>6d}")
print(f"{'TOTAL':22s}{catch.sum():>12,.0f}{'':>10s}{total:>6d}")

print("\nSensitivity (total helicopters):")
for rate,lab in [(34.4,'LPR'),(43.2,'DRF'),(59.1,'ADAC')]:
    row=[]
    for cap in (2.5,2.74,3.0):
        row.append(sum(math.ceil((c/1e5*rate/365.0)/cap) for c in catch))
    print(f"  {lab:5s}({rate}): cap2.5={row[0]}  cap2.74={row[1]}  cap3.0={row[2]}")
