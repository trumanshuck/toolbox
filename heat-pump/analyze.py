#!/usr/bin/env python3
"""Heat-pump feasibility analysis for a ~100-year-old craftsman in Grand Rapids, MI.

Design principle: EVERY number in the written reports comes from this script, not
from hand/LLM arithmetic. This script:

  1. Downloads ~6 full years of NOAA ISD hourly temperatures for KGRR
     (Gerald R. Ford Intl Airport) and writes a cleaned hourly CSV.
  2. Bins the temperatures, computes hours-per-year per bin, hours below key
     thresholds, and the coldest sustained cold snaps.
  3. Builds a house heat-loss "load line" (a range of envelope scenarios).
  4. Overlays a representative NEEP cold-climate heat-pump capacity curve,
     solves the balance point, and counts annual hours spent below it.
  5. Emits data/temp-bins.csv and two figures.

Run:  python3 analyze.py            (downloads on first run, then caches)
      python3 analyze.py --refetch  (force re-download of raw ISD data)
"""

import sys
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).parent
DATA = HERE / "data"
RAWDIR = DATA / "raw"
FIGDIR = HERE / "figures"
CLEAN_CSV = DATA / "grr-hourly-temps.csv"
BINS_CSV = DATA / "temp-bins.csv"

# NOAA Integrated Surface Database (global-hourly) station id for KGRR.
STATION = "72635094860"  # Grand Rapids Gerald R. Ford Intl Airport
# Full calendar years only. The 2025 ISD file is partial (ends late August), which
# would undercount cold hours, so the analysis window is the five full years
# 2020-2024. A completeness guard below also drops any year missing > ~10% of hours.
YEARS = list(range(2020, 2025))  # 2020-2024 inclusive = 5 full calendar years
MIN_HOURS_FOR_FULL_YEAR = 7900  # ~90% of 8760; drop partial years from the stats
ISD_URL = "https://www.ncei.noaa.gov/data/global-hourly/access/{year}/{station}.csv"

# ---------------------------------------------------------------------------
# CONFIG: HOUSE ENVELOPE
# ---------------------------------------------------------------------------
INDOOR_F = 68.0
# Grand Rapids (KGRR) 99% winter heating design temperature (deg F).
# Source: ASHRAE Handbook of Fundamentals climatic design conditions / ENERGY STAR
# County-Level Design Temperature Reference Guide (Kent County) -- 99% = ~6 F,
# 99.6% = 1.4 F. See equipment-reference.md.
DESIGN_T_F = 6.0
# 1% summer cooling design: 86.4 F dry-bulb / 71.8 F mean-coincident wet-bulb.
COOLING_DESIGN_DB_F = 86.4
COOLING_DESIGN_WB_F = 71.8

# Design heat-loss intensity (Btu/hr per sqft at the design temperature) for an
# ~1900 home that is air-sealed with attic + basement-rim insulation but has
# UNINSULATED walls, climate zone 5. Anchored on the ~35 Btu/hr/sqft rule of thumb
# for an early-1900s no-wall-insulation home (HeatingHelp; range 30-45), nudged by
# the air sealing this owner has already done. Three scenarios bracket floor-area
# AND envelope uncertainty. These are planning estimates; a contractor Manual J is
# the authoritative version and typically lands lower once air sealing is credited.
SCENARIOS = {
    "optimistic (1,600 sqft, air sealing paid off)": dict(sqft=1600, btu_per_sqft=25),
    "mid (2,000 sqft, rule-of-thumb)":               dict(sqft=2000, btu_per_sqft=32),
    "conservative (2,400 sqft, leakier)":            dict(sqft=2400, btu_per_sqft=40),
}

# ---------------------------------------------------------------------------
# CONFIG: REPRESENTATIVE COLD-CLIMATE HEAT PUMPS (real NEEP/AHRI submittal data)
# ---------------------------------------------------------------------------
# Maximum heating capacity (Btu/hr) and COP at each outdoor temp (deg F), from
# Mitsubishi AHRI-certified submittal sheets (same test conditions NEEP lists).
# -5 F is not published by these units (they publish 47/17/5/-13); the curve
# interpolates linearly between 5 F and -13 F. Sources in equipment-reference.md.
#
# We model two ways to serve this house, because the second doubles as the
# owner's upstairs/downstairs ZONING plan:
#   * one 3.5-ton ducted system, or
#   * two 2.5-ton ducted systems (one per floor) -> ~2x capacity + native zoning.
EQUIPMENT = {
    "1x 3.5-ton ducted hyper-heat (PVA-A42 + PUZ-HA42)": dict(
        units=1, tmin=-13.0,
        cap={47: 48000, 17: 48000, 5: 48000, -13: 38400},
        cop={47: 3.65, 17: 2.12, 5: 1.91, -13: 1.55},
    ),
    "2x 2.5-ton ducted hyper-heat (PVA-A30 + PUZ-HA30), one per floor": dict(
        units=2, tmin=-13.0,
        cap={47: 34000, 17: 32000, 5: 32000, -13: 25600},
        cop={47: 3.8, 17: 2.2, 5: 2.0, -13: 1.7},
    ),
}
# The single unit is the primary capacity curve drawn on the load/capacity figure.
PRIMARY_EQUIP = "1x 3.5-ton ducted hyper-heat (PVA-A42 + PUZ-HA42)"

# ---------------------------------------------------------------------------
# CONFIG: CARBON
# ---------------------------------------------------------------------------
# Grid CO2 intensity: eGRID2023 RFCM (RFC-Michigan, lower-peninsula) output
# emission rate = 1,214.1 lb CO2/MWh. This is the SUBREGION AVERAGE (still
# coal-influenced); Consumers Energy's own mix is cleaner and decarbonizing as
# coal retires, so this is a conservative (HP-unfavorable) input.
GRID_CO2_LB_PER_KWH = 1.2141
# Natural gas combustion: EPA ~11.7 lb CO2 per therm (~117 lb CO2/MMBtu).
GAS_CO2_LB_PER_THERM = 11.7
FURNACE_AFUE = {"80% non-condensing": 0.80, "95% condensing": 0.95}
KWH_PER_MMBTU = 293.07  # unit conversion
THERM_MMBTU = 0.1       # 1 therm = 0.1 MMBtu

# ---------------------------------------------------------------------------
# CONFIG: ENERGY RATES (Consumers Energy residential, Grand Rapids, 2026)
# All-in midpoint estimates -- flag as estimates. Sources in equipment-reference.md.
# Electricity ~$0.19-0.21/kWh; gas ~$1.09-1.25/therm ($11.3-12.5/Mcf).
# ---------------------------------------------------------------------------
ELEC_USD_PER_KWH = 0.20
GAS_USD_PER_THERM = 1.15

# ---------------------------------------------------------------------------
# CONFIG: EMPIRICAL "BILL METHOD" MANUAL J
# ---------------------------------------------------------------------------
# Back out the house's real heat-loss coefficient (UA) from actual heating-season
# gas use + this climate data (degree-hour / PRISM regression). Base 65 F is the
# convention: it implicitly credits ~3 F of internal gains below a 68 F setpoint.
# Enter your ANNUAL HEATING gas therms (total annual therms MINUS ~12x an average
# summer month, to strip water-heating/cooking/dryer baseload). Set to None to skip.
DEGREE_HOUR_BASE_F = 65.0
YOUR_HEATING_THERMS = None      # e.g. 900 -- your measured annual heating gas use
YOUR_FURNACE_AFUE = 0.80        # your current furnace's efficiency
# Sensitivity sweep printed so you can locate yourself before finding exact bills:
THERMS_SWEEP = [500, 700, 900, 1100, 1300]

# ---------------------------------------------------------------------------
# CONFIG: COOLING-SIDE BILL METHOD (electricity)
# ---------------------------------------------------------------------------
# Symmetric to the gas method: your AC electricity ~= summer bills minus the
# non-HVAC baseload (a shoulder-season month). Enter your measured annual COOLING
# kWh (summer kWh above baseload) to get current AC cost and what a more efficient
# heat pump would use for the same cooling. Set to None to skip.
COOLING_BASE_F = 72.0           # approx AC setpoint for cooling degree-hours
YOUR_ANNUAL_COOLING_KWH = None  # e.g. 1500 -- summer kWh above your baseload
OLD_AC_SEER = 11.0              # a typical older central AC
NEW_HP_SEER2 = 16.0             # a variable-speed cold-climate heat pump in cooling
COOLING_KWH_SWEEP = [800, 1500, 2500]

BIN_WIDTH = 5  # deg F


# ---------------------------------------------------------------------------
# 1. DATA ACQUISITION
# ---------------------------------------------------------------------------
def parse_tmp(field: str):
    """Parse an ISD TMP field like '+0072,1' -> 7.2 C, honoring quality flags."""
    try:
        value_str, quality = field.split(",")
    except (ValueError, AttributeError):
        return np.nan
    value = int(value_str)
    if value == 9999:  # missing
        return np.nan
    if quality in {"2", "3", "6", "7"}:  # suspect / erroneous
        return np.nan
    return value / 10.0  # tenths of deg C -> deg C


def fetch_clean(refetch: bool = False) -> pd.DataFrame:
    """Return a cleaned hourly temperature DataFrame, downloading if needed."""
    if CLEAN_CSV.exists() and not refetch:
        df = pd.read_csv(CLEAN_CSV, parse_dates=["time"])
        return df

    RAWDIR.mkdir(parents=True, exist_ok=True)
    frames = []
    for year in YEARS:
        raw_path = RAWDIR / f"{STATION}_{year}.csv"
        if not raw_path.exists() or refetch:
            url = ISD_URL.format(year=year, station=STATION)
            print(f"  downloading {year} ...", flush=True)
            urllib.request.urlretrieve(url, raw_path)
        raw = pd.read_csv(raw_path, usecols=["DATE", "TMP"], low_memory=False)
        raw["time"] = pd.to_datetime(raw["DATE"])
        raw["temp_c"] = raw["TMP"].map(parse_tmp)
        frames.append(raw[["time", "temp_c"]])

    allrows = pd.concat(frames, ignore_index=True).dropna(subset=["temp_c"])
    # ISD carries several reports per hour (METAR/SPECI). Collapse to one value
    # per clock hour so each row counts as exactly one hour of weather.
    allrows["hour"] = allrows["time"].dt.floor("h")
    hourly = (
        allrows.groupby("hour", as_index=False)["temp_c"].mean()
        .rename(columns={"hour": "time"})
    )
    hourly["temp_f"] = hourly["temp_c"] * 9 / 5 + 32
    hourly["year"] = hourly["time"].dt.year
    # completeness guard: drop any year that is missing too many hours (partial year)
    per_year = hourly.groupby("year").size()
    full_years = per_year[per_year >= MIN_HOURS_FOR_FULL_YEAR].index
    dropped = sorted(set(per_year.index) - set(full_years))
    if dropped:
        print(f"  dropping partial year(s) {dropped} "
              f"({', '.join(f'{y}:{per_year[y]}h' for y in dropped)})")
    hourly = hourly[hourly["year"].isin(full_years)].copy()
    hourly = hourly.sort_values("time").reset_index(drop=True)
    DATA.mkdir(parents=True, exist_ok=True)
    hourly.to_csv(CLEAN_CSV, index=False)
    return hourly


# ---------------------------------------------------------------------------
# 2. TEMPERATURE BINS & COLD SNAPS
# ---------------------------------------------------------------------------
def temperature_bins(df: pd.DataFrame) -> pd.DataFrame:
    n_years = df["year"].nunique()
    lo = int(np.floor(df["temp_f"].min() / BIN_WIDTH) * BIN_WIDTH)
    hi = int(np.ceil(df["temp_f"].max() / BIN_WIDTH) * BIN_WIDTH)
    edges = np.arange(lo, hi + BIN_WIDTH, BIN_WIDTH)
    cats = pd.cut(df["temp_f"], bins=edges, right=False)
    counts = cats.value_counts().sort_index()
    out = pd.DataFrame({
        "bin_low_f": [int(iv.left) for iv in counts.index],
        "bin_high_f": [int(iv.right) for iv in counts.index],
        "total_hours": counts.values,
    })
    out["hours_per_year"] = (out["total_hours"] / n_years).round(1)
    return out


def hours_below(df: pd.DataFrame, threshold_f: float) -> float:
    n_years = df["year"].nunique()
    return round((df["temp_f"] < threshold_f).sum() / n_years, 1)


def coldest_snaps(df: pd.DataFrame, threshold_f: float, top_n: int = 5):
    """Longest runs of consecutive hours at or below threshold_f."""
    s = df.set_index("time")["temp_f"].sort_index()
    below = s <= threshold_f
    grp = (below != below.shift()).cumsum()
    snaps = []
    for _, run in s.groupby(grp):
        mask = run <= threshold_f
        if mask.all() and len(run) > 0:
            snaps.append({
                "start": run.index[0],
                "end": run.index[-1],
                "hours": len(run),
                "min_temp_f": round(run.min(), 1),
            })
    snaps.sort(key=lambda r: r["hours"], reverse=True)
    return snaps[:top_n]


# ---------------------------------------------------------------------------
# 3+4. LOAD LINE, CAPACITY CURVE, BALANCE POINT
# ---------------------------------------------------------------------------
def ua_of(scenario: dict) -> float:
    """Overall heat-loss coefficient UA (Btu/hr per deg F)."""
    design_load = scenario["sqft"] * scenario["btu_per_sqft"]
    return design_load / (INDOOR_F - DESIGN_T_F)


def load_at(scenario: dict, outdoor_f):
    ua = ua_of(scenario)
    return np.maximum(ua * (INDOOR_F - np.asarray(outdoor_f, dtype=float)), 0.0)


def capacity_at(equip: dict, outdoor_f):
    """Total max heating capacity (Btu/hr) of an equipment option vs outdoor temp."""
    xs = np.array(sorted(equip["cap"]))
    ys = np.array([equip["cap"][t] for t in xs]) * equip["units"]
    of = np.asarray(outdoor_f, dtype=float)
    cap = np.interp(of, xs, ys)  # flat extrapolation beyond endpoints
    cap = np.where(of < equip["tmin"], 0.0, cap)
    return cap


def seasonal_cop(df: pd.DataFrame, equip: dict) -> float:
    """Heating-demand-weighted average COP over all heating hours (temp < 65 F).

    Each heating hour's COP is interpolated from the unit's published max-capacity
    COP points and weighted by that hour's heat demand (proportional to indoor-minus
    -outdoor delta-T). Uses max-capacity COP, so this UNDERSTATES real seasonal COP
    (inverters run more efficiently at part load) -- a conservative choice.
    """
    xs = np.array(sorted(equip["cop"]))
    ys = np.array([equip["cop"][t] for t in xs])
    heating = df[df["temp_f"] < 65]
    cop_i = np.interp(heating["temp_f"], xs, ys)
    weight = np.maximum(INDOOR_F - heating["temp_f"].to_numpy(), 0.0)
    return float(np.sum(cop_i * weight) / np.sum(weight))


def heating_degree_hours(df: pd.DataFrame, base_f: float) -> float:
    """Annual heating degree-hours (deg F * hr) at a given base temperature."""
    n_years = df["year"].nunique()
    hdh = np.maximum(base_f - df["temp_f"].to_numpy(), 0.0).sum()
    return hdh / n_years


def cooling_degree_hours(df: pd.DataFrame, base_f: float) -> float:
    """Annual cooling degree-hours (deg F * hr) at a given base temperature."""
    n_years = df["year"].nunique()
    cdh = np.maximum(df["temp_f"].to_numpy() - base_f, 0.0).sum()
    return cdh / n_years


def infer_load_from_gas(df: pd.DataFrame, heating_therms: float, afue: float):
    """Empirical 'bill method' Manual J: back out UA and design load from measured
    annual heating gas use + this climate's degree-hours. Returns a dict."""
    hdh = heating_degree_hours(df, DEGREE_HOUR_BASE_F)          # deg F * hr / yr
    delivered_btu = heating_therms * 100_000 * afue             # Btu/yr to the house
    ua = delivered_btu / hdh                                    # Btu/hr per deg F
    design_load = ua * (INDOOR_F - DESIGN_T_F)                  # Btu/hr @ design temp
    return dict(ua=ua, design_load=design_load, hdh=hdh)


def annual_heating_mmbtu(df: pd.DataFrame, scenario: dict) -> float:
    """Annual delivered heating energy (MMBtu/yr) by integrating hourly load."""
    n_years = df["year"].nunique()
    hourly_btu = load_at(scenario, df["temp_f"].to_numpy())  # Btu/hr * 1 hr
    return float(hourly_btu.sum() / 1e6 / n_years)


def carbon_lb_per_mmbtu(scop: float):
    """CO2 (lb) per MMBtu of DELIVERED heat: heat pump vs gas furnace(s)."""
    hp = (KWH_PER_MMBTU / scop) * GRID_CO2_LB_PER_KWH
    gas = {name: GAS_CO2_LB_PER_THERM / (THERM_MMBTU * afue)
           for name, afue in FURNACE_AFUE.items()}
    return hp, gas


def balance_point(equip: dict, scenario: dict) -> float:
    """Outdoor temp (deg F) where capacity == load. Below it, capacity < load."""
    grid = np.linspace(-20, INDOOR_F, 8801)  # 0.01 F resolution
    diff = capacity_at(equip, grid) - load_at(scenario, grid)
    sign = np.sign(diff)
    crossings = np.where(np.diff(sign) != 0)[0]
    if len(crossings) == 0:
        # never cross: either always covered, or never covered in this range
        return float("nan")
    # warmest crossing from deficit(-) to surplus(+)
    for idx in crossings[::-1]:
        if diff[idx] <= 0 <= diff[idx + 1]:
            return round(float(grid[idx + 1]), 1)
    return round(float(grid[crossings[-1] + 1]), 1)


# ---------------------------------------------------------------------------
# 5. FIGURES
# ---------------------------------------------------------------------------
def fig_histogram(bins: pd.DataFrame):
    FIGDIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    centers = (bins["bin_low_f"] + bins["bin_high_f"]) / 2
    ax.bar(centers, bins["hours_per_year"], width=BIN_WIDTH * 0.9,
           color="#4C72B0", edgecolor="white")
    ax.axvline(DESIGN_T_F, color="#C44E52", linestyle="--", linewidth=2,
               label=f"99% design temp ({DESIGN_T_F:.0f} F)")
    ax.axvline(5, color="#55A868", linestyle=":", linewidth=2,
               label="5 F (ccHP full-capacity threshold)")
    ax.set_xlabel("Outdoor temperature (deg F)")
    ax.set_ylabel("Hours per year")
    ax.set_title("Grand Rapids (KGRR) hours per year by temperature bin\n"
                 f"{YEARS[0]}-{YEARS[-1]}, {len(YEARS)} full years")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIGDIR / "temp-histogram.png", dpi=130)
    plt.close(fig)


def fig_load_vs_capacity(balances: dict):
    FIGDIR.mkdir(parents=True, exist_ok=True)
    temps = np.linspace(-15, 50, 400)
    fig, ax = plt.subplots(figsize=(10, 6))
    # both capacity curves
    ax.plot(temps, capacity_at(EQUIPMENT[PRIMARY_EQUIP], temps) / 1000,
            color="black", linewidth=2.5, label=f"Capacity: {PRIMARY_EQUIP}")
    two = [k for k in EQUIPMENT if k != PRIMARY_EQUIP][0]
    ax.plot(temps, capacity_at(EQUIPMENT[two], temps) / 1000,
            color="black", linewidth=2.0, linestyle=(0, (4, 2)),
            label=f"Capacity: {two}")
    colors = ["#55A868", "#DD8452", "#C44E52"]
    for (name, sc), c in zip(SCENARIOS.items(), colors):
        ax.plot(temps, load_at(sc, temps) / 1000, color=c, linewidth=1.8,
                label=f"Load: {name}")
        bp = balances[PRIMARY_EQUIP][name]
        if not np.isnan(bp):
            ax.plot(bp, load_at(sc, bp) / 1000, "o", color=c, markersize=8)
            ax.annotate(f"{bp:.0f} F", (bp, load_at(sc, bp) / 1000),
                        textcoords="offset points", xytext=(6, 6), color=c,
                        fontweight="bold")
    ax.axvline(DESIGN_T_F, color="gray", linestyle="--", alpha=0.7,
               label=f"Design temp ({DESIGN_T_F:.0f} F)")
    ax.set_xlabel("Outdoor temperature (deg F)")
    ax.set_ylabel("Heating output / demand (kBtu/hr)")
    ax.set_title("Heat-pump capacity vs house heat loss\n"
                 "Balance point = where the lines cross")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    ax.set_ylim(bottom=0)
    fig.tight_layout()
    fig.savefig(FIGDIR / "load-vs-capacity.png", dpi=130)
    plt.close(fig)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    refetch = "--refetch" in sys.argv
    print("Fetching / loading climate data ...")
    df = fetch_clean(refetch=refetch)
    n_years = df["year"].nunique()
    total_hours = len(df)
    print(f"  {total_hours:,} hourly records across {n_years} years "
          f"({df['year'].min()}-{df['year'].max()})")

    bins = temperature_bins(df)
    bins.to_csv(BINS_CSV, index=False)

    thresholds = [DESIGN_T_F, 0, 5, 17, 32]
    hb = {t: hours_below(df, t) for t in thresholds}

    # balances[equip_name][scenario_name] = balance point (deg F)
    balances = {
        eqname: {scname: balance_point(eq, sc) for scname, sc in SCENARIOS.items()}
        for eqname, eq in EQUIPMENT.items()
    }

    fig_histogram(bins)
    fig_load_vs_capacity(balances)

    # ---- console summary (this is what the reports cite) ----
    print("\n=== SUMMARY (cite these in the markdown) ===")
    print(f"Station: KGRR ({STATION}), years {df['year'].min()}-{df['year'].max()} "
          f"({n_years} full years)")
    print(f"Coldest hourly temp observed: {df['temp_f'].min():.1f} F")
    print(f"Warmest hourly temp observed: {df['temp_f'].max():.1f} F")
    print(f"Mean annual temp: {df['temp_f'].mean():.1f} F")
    print("\nHours per year below threshold:")
    for t in thresholds:
        pct = 100 * hb[t] / (total_hours / n_years)
        print(f"  < {t:>4.0f} F : {hb[t]:>7.1f} hr/yr  ({pct:4.1f}% of the year)")

    print("\nEnvelope scenarios (design load @ %.0f F):" % DESIGN_T_F)
    for name, sc in SCENARIOS.items():
        ua = ua_of(sc)
        design_load = sc["sqft"] * sc["btu_per_sqft"]
        print(f"  {name}: UA={ua:6.0f} Btu/hr-F, design load={design_load:6.0f} Btu/hr")

    print("\nBalance point (F) and hours/yr the house spends below it:")
    for eqname, eq in EQUIPMENT.items():
        print(f"  [{eqname}]  full-capacity to ~5 F = "
              f"{eq['cap'][5] * eq['units']:,} Btu/hr")
        for scname in SCENARIOS:
            bp = balances[eqname][scname]
            below = hours_below(df, bp) if not np.isnan(bp) else float("nan")
            covers = "covers design temp" if (not np.isnan(bp) and bp <= DESIGN_T_F) \
                else "SHORT of design temp"
            print(f"      {scname:<45} bp={bp:5.1f} F  "
                  f"({below:6.1f} hr/yr below, {covers})")

    print("\nCapacity of each unit at key temps (per-unit Btu/hr | COP):")
    for eqname, eq in EQUIPMENT.items():
        print(f"  [{eqname}]")
        for t in sorted(eq["cap"], reverse=True):
            print(f"      {t:>4} F : {eq['cap'][t]:>6} Btu/hr | COP {eq['cop'].get(t)}")

    # ---- carbon ----
    scop = seasonal_cop(df, EQUIPMENT[PRIMARY_EQUIP])
    hp_lb, gas_lb = carbon_lb_per_mmbtu(scop)
    print("\nCarbon (CO2 per MMBtu of delivered heat):")
    print(f"  Grid intensity (eGRID2023 RFCM): {GRID_CO2_LB_PER_KWH:.3f} lb/kWh")
    print(f"  Demand-weighted seasonal COP ({PRIMARY_EQUIP.split(' (')[0]}): {scop:.2f}")
    print(f"  Heat pump @ COP {scop:.2f}: {hp_lb:6.1f} lb CO2/MMBtu")
    for name, val in gas_lb.items():
        delta = 100 * (hp_lb - val) / val
        print(f"  Gas furnace {name}: {val:6.1f} lb CO2/MMBtu "
              f"(heat pump is {delta:+.0f}% vs this)")
    print("  Annual heating demand by envelope scenario (drives absolute tons):")
    for name, sc in SCENARIOS.items():
        mmbtu = annual_heating_mmbtu(df, sc)
        hp_tons = mmbtu * hp_lb / 2000
        gas80_tons = mmbtu * gas_lb["80% non-condensing"] / 2000
        print(f"    {name:<45} {mmbtu:6.1f} MMBtu/yr  "
              f"-> HP {hp_tons:4.1f} vs gas(80%) {gas80_tons:4.1f} short-tons CO2/yr")

    # ---- operating cost (heating season only; estimates) ----
    print("\nEstimated annual HEATING operating cost "
          f"(elec ${ELEC_USD_PER_KWH}/kWh, gas ${GAS_USD_PER_THERM}/therm):")
    for name, sc in SCENARIOS.items():
        mmbtu = annual_heating_mmbtu(df, sc)
        hp_cost = mmbtu * KWH_PER_MMBTU / scop * ELEC_USD_PER_KWH
        gas80 = mmbtu / (THERM_MMBTU * 0.80) * GAS_USD_PER_THERM
        gas95 = mmbtu / (THERM_MMBTU * 0.95) * GAS_USD_PER_THERM
        print(f"    {name:<45} HP ${hp_cost:5.0f}  |  "
              f"gas80% ${gas80:5.0f}  |  gas95% ${gas95:5.0f}")

    # ---- empirical 'bill method' Manual J ----
    hdh65 = heating_degree_hours(df, DEGREE_HOUR_BASE_F)
    print(f"\nEmpirical Manual J from gas bills "
          f"(HDH base {DEGREE_HOUR_BASE_F:.0f} F = {hdh65:,.0f} deg F*hr/yr):")
    print(f"  {'heating therms/yr':>17} | {'UA':>6} | {'design load':>11} | "
          f"{'bal (1x3.5t)':>12} | {'bal (2x2.5t)':>12}")
    single = EQUIPMENT[PRIMARY_EQUIP]
    two = EQUIPMENT[[k for k in EQUIPMENT if k != PRIMARY_EQUIP][0]]
    for th in THERMS_SWEEP:
        r = infer_load_from_gas(df, th, YOUR_FURNACE_AFUE)
        pseudo = {"sqft": 1, "btu_per_sqft": r["design_load"]}
        bp1 = balance_point(single, pseudo)
        bp2 = balance_point(two, pseudo)
        print(f"  {th:>17} | {r['ua']:6.0f} | {r['design_load']:8.0f} Btu | "
              f"{bp1:9.1f} F | {bp2:9.1f} F")
    print(f"  (assumes AFUE {YOUR_FURNACE_AFUE:.0%}; 'heating therms' = annual total "
          f"minus ~12x an avg summer month)")
    if YOUR_HEATING_THERMS is not None:
        r = infer_load_from_gas(df, YOUR_HEATING_THERMS, YOUR_FURNACE_AFUE)
        print(f"  >>> YOUR house ({YOUR_HEATING_THERMS} therms): "
              f"UA={r['ua']:.0f} Btu/hr-F, design load={r['design_load']:.0f} Btu/hr @ "
              f"{DESIGN_T_F:.0f} F")

    # ---- cooling-side bill method (electricity) ----
    cdh72 = cooling_degree_hours(df, COOLING_BASE_F)
    print(f"\nCooling side (CDH base {COOLING_BASE_F:.0f} F = {cdh72:,.0f} deg F*hr/yr "
          f"-- modest; Grand Rapids summers are short):")
    print(f"  {'AC kWh/yr (summer above baseload)':>34} | {'current AC cost':>15} | "
          f"{'heat-pump cost @ SEER2 %g':>24}" % NEW_HP_SEER2)
    for kwh in COOLING_KWH_SWEEP:
        cur = kwh * ELEC_USD_PER_KWH
        hp_kwh = kwh * OLD_AC_SEER / NEW_HP_SEER2   # same cooling, better efficiency
        hp_cost = hp_kwh * ELEC_USD_PER_KWH
        print(f"  {kwh:>34} | ${cur:14.0f} | ${hp_cost:9.0f} "
              f"({hp_kwh:.0f} kWh, ~{100*(1-OLD_AC_SEER/NEW_HP_SEER2):.0f}% less)")
    print(f"  (old AC SEER {OLD_AC_SEER:g} -> heat pump SEER2 {NEW_HP_SEER2:g}; "
          f"AC kWh = summer bills minus a shoulder-month baseload)")
    if YOUR_ANNUAL_COOLING_KWH is not None:
        cur = YOUR_ANNUAL_COOLING_KWH * ELEC_USD_PER_KWH
        hp_cost = YOUR_ANNUAL_COOLING_KWH * OLD_AC_SEER / NEW_HP_SEER2 * ELEC_USD_PER_KWH
        print(f"  >>> YOUR cooling ({YOUR_ANNUAL_COOLING_KWH} kWh): "
              f"now ~${cur:.0f}/yr, heat pump ~${hp_cost:.0f}/yr")

    print("\nLongest cold snaps at/below 5 F (top 5):")
    for snap in coldest_snaps(df, 5):
        print(f"  {snap['start']:%Y-%m-%d %Hh} -> {snap['end']:%Y-%m-%d %Hh}: "
              f"{snap['hours']} hr, min {snap['min_temp_f']} F")
    print("\nLongest cold snaps at/below 0 F (top 5):")
    for snap in coldest_snaps(df, 0):
        print(f"  {snap['start']:%Y-%m-%d %Hh} -> {snap['end']:%Y-%m-%d %Hh}: "
              f"{snap['hours']} hr, min {snap['min_temp_f']} F")

    print(f"\nWrote: {CLEAN_CSV}")
    print(f"Wrote: {BINS_CSV}")
    print(f"Wrote: {FIGDIR / 'temp-histogram.png'}")
    print(f"Wrote: {FIGDIR / 'load-vs-capacity.png'}")


if __name__ == "__main__":
    main()
