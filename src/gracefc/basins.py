"""Aggregate a gridded mascon product to monthly basin-mean TWSA and build the basin table.

Reads a CSR or JPL mascon NetCDF file and the 0.25-degree basin mask file. Returns one row
per basin and month (TWSA in cm of equivalent water height) and a metadata table with each
basin's centroid, area, continent and sample flags. Excluded basins (ice sheets, water
bodies and, on JPL, masks with no valid scaled cells) stay in the metadata table with their
reason in the exclude_reason column.

Solutions are assigned to calendar months from the product's months_missing attribute
(see assign_solution_months).
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

from gracefc.comparison import fully_contained_group_counts

# Approximate continent boxes on basin centroids, checked in order; the first match wins.
# The Arabia box and Europe precede Africa so that Gulf basins and Sicily are not assigned
# to Africa. Maritime Southeast Asia precedes the "australia" box so that the
# southern-hemisphere Indonesian islands stay in Asia; its eastern edge at 132 E keeps all
# of New Guinea with Oceania.
# The "australia" group includes Oceania (Melanesia, New Zealand).
CONTINENT_BOXES = [
    ("antarctica", -90, -60, -180, 180),
    ("greenland", 59, 84, -75, -10),
    ("asia", 12, 40, 35, 60),
    ("europe", 36, 72, -25, 60),
    ("africa", -35, 38, -18, 52),
    ("asia", 0, 82, 60, 180),
    ("asia", 36, 82, 25, 60),
    ("asia", -11, 0, 95, 132),
    ("australia", -50, 0, 110, 180),
    ("south_america", -56, 13, -82, -33),
    ("north_america", 7, 84, -170, -50),
]


# Basins are labelled B001 to B284 in the sorted order of the mask's basin names, which are
# not published. Sorting by label gives the same order as sorting by mask name.

# The Antarctic and Greenland ice-sheet drainage systems, which are excluded from the sample
ICE_SHEETS = {
    "antarctica": """B004 B005 B006 B007 B029 B030 B031 B032 B033 B034 B035 B036 B037 B038
        B039 B040 B041 B042 B043 B044 B186 B187 B188 B189 B190 B191 B192""".split(),
    "greenland": """B088 B089 B090 B091 B092 B093 B094 B095 B096 B097 B098 B099 B100 B101
        B102 B103 B104 B105 B106""".split(),
}
# Basins the centroid boxes misplace: Red Sea, Gulf of Aden and Mediterranean coasts,
# Sicily, and northern islands and peninsulas
CONTINENT_OVERRIDES = {
    "asia": ["B022", "B054", "B058"],
    "europe": ["B073", "B148", "B173"],
    "north_america": ["B116", "B156"],
    "africa": ["B162", "B165", "B169", "B201"],
}
LABEL_CONTINENT = {label: cont for groups in (ICE_SHEETS, CONTINENT_OVERRIDES)
                   for cont, labels in groups.items() for label in labels}
ICE_SHEET_LABELS = {label for labels in ICE_SHEETS.values() for label in labels}
# Largely glaciated basins inside the kept sample (Arctic islands, Iceland, southern Alaska,
# Patagonia)
GLACIATED_LABELS = {"B001", "B009", "B073", "B110", "B132", "B137", "B145", "B173"}


def _assign_continent(lat: float, lon: float, label: str) -> str:
    # Listed basins take precedence over the centroid boxes
    if label in LABEL_CONTINENT:
        return LABEL_CONTINENT[label]
    for cont, la0, la1, lo0, lo1 in CONTINENT_BOXES:
        if la0 <= lat <= la1 and lo0 <= lon <= lo1:
            return cont
    return "other"


def load_basin_masks(mask_path: Path) -> dict:
    """Return per-basin flat cell indices and cos-lat weights, the metadata table and mask axes."""
    dm = xr.open_dataset(mask_path, decode_times=False)
    masks = dm["mask"].values  # (basin, lat, lon), binary
    mask_names = [str(n) for n in dm["Name"].values]
    rank = {n: i + 1 for i, n in enumerate(sorted(mask_names))}
    names = [f"B{rank[n]:03d}" for n in mask_names]
    ids = dm["ID"].values
    lat = dm["lat"].values
    lon = dm["lon"].values
    # Wrap 0-360 longitudes to -180..180 so centroids and distances behave near the meridian
    lon_wrapped = np.where(lon > 180, lon - 360, lon)
    coslat = np.cos(np.deg2rad(lat))
    w2d = np.broadcast_to(coslat[:, None], masks.shape[1:])

    cell_indices, cell_weights, meta_rows = [], [], []
    # Quarter-degree cell area at the equator, scaled by cos(lat) per cell
    cell_km2_eq = (111.32 * 0.25) * (111.32 * 0.25)
    for b in range(masks.shape[0]):
        sel = masks[b] > 0
        flat = np.flatnonzero(sel)
        w = w2d[sel]
        cell_indices.append(flat)
        cell_weights.append(w)
        lat_cells = np.broadcast_to(lat[:, None], masks.shape[1:])[sel]
        lon_cells = np.broadcast_to(lon_wrapped[None, :], masks.shape[1:])[sel]
        c_lat = float(np.average(lat_cells, weights=w))
        # Weighted circular mean of longitude, so dateline-crossing basins get a correct centroid
        rad = np.deg2rad(lon_cells)
        c_lon = float(np.rad2deg(np.arctan2(
            np.average(np.sin(rad), weights=w), np.average(np.cos(rad), weights=w)
        )))
        area = float(np.sum(w) * cell_km2_eq)
        meta_rows.append({
            "basin_idx": b,
            "id": str(ids[b]),
            "name": names[b],
            # The first letter of the mask name is its basin class; W marks a water body
            "prefix": mask_names[b].split("_")[0],
            "centroid_lat": c_lat,
            "centroid_lon": c_lon,
            "area_km2": area,
            "n_cells": int(flat.size),
        })
    meta = pd.DataFrame(meta_rows)
    meta["continent"] = [
        _assign_continent(r.centroid_lat, r.centroid_lon, r.name) for r in meta.itertuples()
    ]
    reasons = []
    for r in meta.itertuples():
        if r.name in ICE_SHEET_LABELS:
            reasons.append("ice_sheet")
        elif r.prefix == "W":
            reasons.append("water_body")
        else:
            # An explicit value, because an empty string is read back from CSV as NaN
            reasons.append("keep")
    meta["exclude_reason"] = reasons
    # A GRACE resolution element of about 300 km covers about 90 000 km2; smaller kept basins
    # are flagged as below the resolution of the observations
    meta["below_resolution"] = (meta["area_km2"] < 90_000) & (meta["exclude_reason"] == "keep")
    # Largely glaciated basins inside the kept sample, flagged so they can be reported separately
    meta["glaciated"] = meta["name"].isin(GLACIATED_LABELS)
    return {"indices": cell_indices, "weights": cell_weights, "meta": meta,
            "lat": lat, "lon": lon}


def assign_solution_months(ds: xr.Dataset, product: str = "csr") -> pd.DatetimeIndex:
    """Return the official calendar month of each solution in the file, one solution per month.

    The month sequence is the file's coverage span minus the months listed in its
    months_missing attribute. Binning by the midpoint of the data span would mislabel
    irregular-span solutions: the arcs centered on 2011-10-31 and 2015-04-27 are the CSR
    November 2011 and May 2015 solutions. When the file has time bounds, each assigned
    month is checked against its solution's data span.
    """
    units = ds["time"].attrs.get(
        "units", ds["time"].attrs.get("Units", "days since 2002-01-01T00:00:00Z")
    )
    origin = pd.Timestamp(str(units).split("since", 1)[1].strip().replace("Z", ""))
    missing = {
        pd.Period(m, freq="M")
        for m in re.findall(r"\d{4}-\d{2}", str(ds.attrs["months_missing"]))
    }
    start = pd.Period(pd.Timestamp(str(ds.attrs["time_coverage_start"]).replace("Z", "")), freq="M")
    end = pd.Period(pd.Timestamp(str(ds.attrs["time_coverage_end"]).replace("Z", "")), freq="M")
    months = [m for m in pd.period_range(start, end, freq="M") if m not in missing]
    n_sol = ds["time"].shape[0]
    if len(months) != n_sol:
        raise ValueError(
            f"{product.upper()} metadata inconsistent: {len(months)} expected months vs "
            f"{n_sol} solutions; "
            "verify months_missing/time_coverage attributes before rebuilding"
        )
    bounds_name = ds["time"].attrs.get("bounds", "time_bounds")
    if bounds_name not in ds:
        # Some JPL releases omit time bounds; the official month sequence is still
        # unambiguous without them.
        return pd.DatetimeIndex([m.to_timestamp() for m in months])
    bounds = ds[bounds_name].values.astype("float64")
    t0 = origin + pd.to_timedelta(bounds[:, 0], unit="D")
    t1 = origin + pd.to_timedelta(bounds[:, 1], unit="D")
    for i, m in enumerate(months):
        if t1[i] < m.start_time or t0[i] > m.end_time:
            raise ValueError(
                f"solution {i} span {t0[i]:%Y-%m-%d}..{t1[i]:%Y-%m-%d} does not overlap "
                f"its assigned month {m}"
            )
    return pd.DatetimeIndex([m.to_timestamp() for m in months])


def _coord_name(obj: xr.DataArray, candidates: tuple[str, ...]) -> str:
    for name in candidates:
        if name in obj.dims and name in obj.coords:
            return name
    raise ValueError(f"none of coordinates {candidates} occur in lwe_thickness dimensions {obj.dims}")


def _nearest_grid_indices(source: np.ndarray, target: np.ndarray, circular: bool = False) -> np.ndarray:
    """Index of the closest source-grid centre for every target-grid centre."""
    source = np.asarray(source, dtype=float)
    target = np.asarray(target, dtype=float)
    delta = np.abs(target[:, None] - source[None, :])
    if circular:
        delta = np.mod(delta, 360.0)
        delta = np.minimum(delta, 360.0 - delta)
    return np.argmin(delta, axis=1)


def build_basin_series(
    mascon_path: Path,
    mask_path: Path,
    product: str = "csr",
    apply_scale_factors: bool | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Aggregate a CSR or JPL mascon grid into per-basin monthly means.

    The HydroSHEDS mask is on a 0.25-degree grid. CSR is already sampled on that
    grid, while JPL is sampled at 0.5 degrees. Mask-cell centres are mapped to the
    nearest mascon grid centre before area-weighted aggregation; a source cell hit by
    several mask cells carries their summed weight. Returns (long_df, meta): basin
    means in cm, one row per basin and month, and the basin metadata table.
    """
    product = product.lower()
    if product not in {"csr", "jpl"}:
        raise ValueError(f"unsupported mascon product: {product!r}")
    bm = load_basin_masks(mask_path)
    ds = xr.open_dataset(mascon_path, decode_times=False)
    dates = assign_solution_months(ds, product=product)
    if "lwe_thickness" not in ds:
        raise ValueError(f"{mascon_path} has no lwe_thickness variable")
    lwe = ds["lwe_thickness"]
    lat_name = _coord_name(lwe, ("lat", "latitude"))
    lon_name = _coord_name(lwe, ("lon", "longitude"))
    lwe = lwe.transpose("time", lat_name, lon_name)

    # JPL's CRI product distributes optional scale factors for sub-mascon hydrology;
    # the expert non-CRI product does not. CSR is used as distributed.
    if apply_scale_factors is None:
        apply_scale_factors = product == "jpl" and "scale_factor" in ds
    if apply_scale_factors:
        if "scale_factor" not in ds:
            raise ValueError("JPL scale factors requested but scale_factor is absent")
        scale = ds["scale_factor"].transpose(lat_name, lon_name)
        lwe = lwe * scale

    mask_lat = np.asarray(bm["lat"])
    mask_lon = np.asarray(bm["lon"])
    src_lat_for_mask = _nearest_grid_indices(ds[lat_name].values, mask_lat)
    src_lon_for_mask = _nearest_grid_indices(ds[lon_name].values, mask_lon, circular=True)
    mask_nlon = len(mask_lon)
    src_nlon = len(ds[lon_name])
    source_indices = []
    for mask_flat in bm["indices"]:
        mask_rows, mask_cols = np.divmod(mask_flat, mask_nlon)
        source_indices.append(
            src_lat_for_mask[mask_rows] * src_nlon + src_lon_for_mask[mask_cols]
        )
    n_time = lwe.shape[0]

    n_basins = len(bm["indices"])
    out = np.full((n_time, n_basins), np.nan)
    # Chunk over time to keep memory bounded: one chunk is ~170 MB
    chunk = 40
    for t0 in range(0, n_time, chunk):
        t1 = min(t0 + chunk, n_time)
        block = lwe.isel(time=slice(t0, t1)).values.reshape(t1 - t0, -1)
        for b in range(n_basins):
            idx, w = source_indices[b], bm["weights"][b]
            vals = block[:, idx]
            # NaN-aware weighted mean: renormalize weights over valid cells per timestep
            valid = np.isfinite(vals)
            wsum = (valid * w).sum(axis=1)
            num = np.nansum(vals * w, axis=1)
            np.divide(num, wsum, out=out[t0:t1, b], where=wsum > 0)

    df = pd.DataFrame(out, index=dates, columns=bm["meta"]["name"].values)
    # One solution per official month by construction; duplicates mean the mapping broke
    if not df.index.is_unique:
        raise ValueError("duplicate solution months after official assignment")
    long_df = df.reset_index(names="date").melt(id_vars="date", var_name="name", value_name="twsa_cm")
    long_df = long_df.merge(bm["meta"][["name", "basin_idx"]], on="name")
    meta = bm["meta"].copy()
    meta["mascon_product"] = product
    meta["scale_factors_applied"] = bool(apply_scale_factors)
    if product == "jpl":
        if "mascon_ID" not in ds:
            raise ValueError("JPL product has no mascon_ID field")
        native_id = ds["mascon_ID"].transpose(lat_name, lon_name).values
        id_on_mask_grid = native_id[np.ix_(src_lat_for_mask, src_lon_for_mask)]
        meta["n_full_jpl_mascons"] = fully_contained_group_counts(
            id_on_mask_grid, bm["indices"]
        )
    valid_months = np.isfinite(out).sum(axis=0)
    meta["product_valid_months"] = valid_months
    if product == "jpl":
        # Small island masks can map entirely to JPL cells without a CRI land
        # scale factor. Their metadata rows are kept, but they are excluded so
        # that no all-NaN target series enters the forecasting experiments.
        unavailable = (meta["exclude_reason"] == "keep") & (valid_months == 0)
        meta.loc[unavailable, "exclude_reason"] = "jpl_unavailable"
    ds.close()
    return long_df.sort_values(["basin_idx", "date"]).reset_index(drop=True), meta
