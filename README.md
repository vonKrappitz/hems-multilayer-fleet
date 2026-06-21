# Reproducibility package — Part II (Air Medical Journal)
"Matching aircraft to mission: a multilayer fleet ... with a forecast for air ECMO transport"
Author: Maciej Marcin Kasperek (ORCID 0009-0008-7419-0851).

This package reproduces the decision-relevant results of the paper from public,
operator-independent inputs: the per-base helicopter allocation, the total of 28 rescue
helicopters, the full sensitivity grid, and Figure 1.

## Contents
- `loc28.json` — base coordinates (type, name, sector, airfield, ICAO, lat/lon airfield,
  status, lat/lon model; decimal comma). The 21 primary bases are the 7 CRL + 14 CT
  (Rzeszow is the 22nd standby base and is excluded from the catchment partition).
- `voronoi_fleet.py` — assigns every populated 1 km cell of the WorldPop raster to its
  nearest primary base (Voronoi partition) in PUWG 1992 (EPSG:2180), sums catchment
  population, converts to daily missions at the DRF rate (43.2 per 100,000/yr), divides by
  a single-aircraft capacity of 2.74 missions/day (rounded up), and prints the per-base
  table and the sensitivity grid. Reproduces e-Table 1 and Table 2.
- `generate_fleetmap_EN.py` — renders Figure 1 (fleet dislocation map) as vector PDF + PNG.
- `caravan_basing.py` — places the 3 fixed-wing (Cessna Grand Caravan EX) bases by a population-weighted p-median on the same WorldPop raster, with candidates restricted to the 7 CRL hub airports. Reproduces the fixed-wing base selection (Warsaw, Krakow, Poznan).
- `fetch_gadm.py` — downloads the GADM v4.1 boundary into `geo/`. The file is not shipped, the GADM licence forbids redistribution. Run this once before the map.
- `geo/gadm41_POL_2.json` — administrative boundary, GADM v4.1. Not shipped, produced by `fetch_gadm.py`.
- `geo/pl_pop_1km.tif` — WorldPop 2020 population raster, 1 km, clipped to Poland. CC-BY 4.0, shipped here.
- `requirements.txt` — Python dependencies.

## Data provenance (external, public)

- GADM v4.1 — https://gadm.org/. The GADM licence allows academic use and the making of maps for research articles, but does not allow redistribution of the data. The boundary file is therefore not shipped here. Run `python3 fetch_gadm.py` to download it into `geo/`.
- WorldPop 2020, Poland, 1 km — https://www.worldpop.org/. Released under CC-BY 4.0, the clipped raster is shipped here in `geo/`.
Cite both original sources in any derived work.

## How to run
```
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 fetch_gadm.py           # -> geo/gadm41_POL_2.json (GADM boundary, not shipped)
python3 voronoi_fleet.py        # per-base allocation + sensitivity grid
python3 generate_fleetmap_EN.py # Figure 1 (PDF + PNG)
python3 caravan_basing.py       # fixed-wing (Caravan) base selection
```
The scripts resolve every path relative to their own location, so they run from any working directory. The raster and boundary live under `geo/`, fetch the boundary first with `python3 fetch_gadm.py`.

## Expected output (verified)
- Per-base allocation: Gliwice-Trynek 3; Warsaw, Krakow, Wroclaw, Lask, Torun 2 each;
  the remaining 15 bases 1 each. Operational rescue total: 28.
- Sensitivity (total helicopters): LPR 26/25/24, DRF 30/28/26, ADAC 35/34/32
  across capacities 2.5 / 2.74 / 3.0 — identical to Table 2.
- Raster population total ~39.22 million.
- Fixed-wing bases (population-weighted p-median over the 7 CRL hubs): Warsaw, Krakow, Poznan, with a clear margin over the next-best triple (Warsaw, Krakow, Wroclaw).

## Note on catchment values
The per-base catchment populations reproduce e-Table 1 to within about one per cent; a few
bases differ by tens of thousands of inhabitants because of nearest-base tie handling at
sector edges. These differences do not change any per-base helicopter count or the total.

## Licence
Code under Apache 2.0. The WorldPop raster (`geo/pl_pop_1km.tif`) is CC-BY 4.0 and is shipped here. The GADM boundary is not shipped, it is fetched by `fetch_gadm.py`, and the GADM licence allows academic map-making but not redistribution. Coordinates (`loc28.json`) are CC BY 4.0.
The version of record will be archived with a citable DOI (e.g. Zenodo) on publication.

## How to cite
Software: Kasperek, M.M. Multilayer HEMS fleet — reproducibility package (Python software), Apache-2.0 licence.
GitHub: https://github.com/vonKrappitz/hems-multilayer-fleet
Zenodo DOI: 10.5281/zenodo.20788752
The citation for the associated study will be added once it is published.
