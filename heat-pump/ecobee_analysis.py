#!/usr/bin/env python3
"""Empirical Manual J from ecobee runtime data (the gold-standard method).

Reads the ecobee HomeIQ CSV exports in data/ecobee/ (5-minute interval records of
indoor temp, setpoints, outdoor temp, and furnace runtime) and backs out the
house's real heat-loss rate. Because the furnace here is single-stage (only
"Heat Stage 1" runs), delivered heat over any period is simply:

    delivered_heat = furnace_output_Btu_per_hr * (runtime_seconds / 3600)

and in steady state that equals the house load, UA * (T_indoor - T_outdoor). So a
regression of runtime FRACTION against indoor-minus-outdoor temperature gives the
ratio UA / furnace_output directly; multiplying by the furnace's nameplate output
resolves it to an absolute UA, design load, and balance point.

The setpoint schedule and the heating-onset temperature need NO furnace nameplate.
The absolute Btu numbers need the furnace's rated output -- set FURNACE_INPUT_BTU.

Run:  python3 ecobee_analysis.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).parent
ECOBEE_DIR = HERE / "data" / "ecobee"
FIGDIR = HERE / "figures"

INTERVAL_SECONDS = 300  # ecobee reports at 5-minute resolution
DESIGN_T_F = 6.0        # Grand Rapids 99% heating design temp (matches analyze.py)
# Size to a comfortable setpoint, not the thrifty ~64.5 F this household currently
# holds. UA is a physical property of the house (independent of setpoint); design
# LOAD scales with the indoor temp you actually want to maintain on a design day.
DESIGN_INDOOR_F = 70.0

# --- furnace nameplate (from the label) ---
FURNACE_AFUE = 0.95            # user confirmed 95.0 AFUE
# Nameplate not found, but SOLVED from gas energy + runtime hours (see GAS CROSS-CHECK
# at the bottom of the run): ~66k input / ~63k output Btu/hr. Rounded to 66,000.
FURNACE_INPUT_BTU = 66000      # rated INPUT Btu/hr (solved, not from label)
# Sweep of plausible furnace INPUT sizes, shown until the exact number is entered:
INPUT_SWEEP = [60000, 80000, 100000]

# --- gas cross-check (Consumers Energy usage chart, AVERAGE CCF PER DAY) ---
# The utility 13-month chart reads in CCF/day: a whole-month total of ~5 CCF is
# impossible for a furnace running ~40% of winter, so these are daily averages
# (summer ~0.5 CCF/day = water heat + stove; winter ~5 CCF/day = heating).
# Combined with the ecobee runtime hours, gas energy pins the furnace's real output.
GAS_CCF_PER_DAY = {                     # (avg CCF/day, days in month)
    "Nov 2025": (2.4, 30), "Dec 2025": (4.8, 31), "Jan 2026": (5.0, 31),
    "Feb 2026": (5.7, 28), "Mar 2026": (3.8, 31),
}
GAS_BASELOAD_CCF_PER_DAY = 0.55         # summer floor: water heating + cooking + dryer
CCF_TO_THERM = 1.037                    # Consumers heating value ~1.03-1.04 therm/CCF

HOME_SQFT = 1800                        # user-provided
# A gas fireplace (living room, evenings, always off before bed) burns gas that IS in
# the utility bill but is NOT in furnace runtime -- so it slightly inflates the solved
# furnace output, making the load estimate marginally conservative. It's off overnight
# when the design-cold hours occur, so it doesn't affect the sizing tail.

# representative heat pumps (mirror analyze.py) for the balance-point check
HP = {
    "1x 3.5-ton (PVA-A42)": dict(units=1, tmin=-13.0,
                                 cap={47: 48000, 17: 48000, 5: 48000, -13: 38400}),
    "2x 2.5-ton (PVA-A30, per floor)": dict(units=2, tmin=-13.0,
                                            cap={47: 34000, 17: 32000, 5: 32000, -13: 25600}),
}

COLS = {
    "date": "Date", "time": "Time",
    "heat_set": "Heat Set Temp (F)",
    "indoor": "Current Temp (F)",
    "outdoor": "Outdoor Temp (F)",
    "heat_run": "Heat Stage 1 (sec)",
}


def load_ecobee() -> pd.DataFrame:
    frames = []
    for path in sorted(ECOBEE_DIR.glob("*.csv")):
        with open(path) as f:
            lines = f.readlines()
        hdr = next(i for i, l in enumerate(lines) if l.startswith("Date,Time"))
        # data rows carry a trailing comma (one more field than the header), so
        # index_col=False stops pandas from shifting columns into the index.
        df = pd.read_csv(path, skiprows=hdr, index_col=False, low_memory=False)
        frames.append(df)
    raw = pd.concat(frames, ignore_index=True)
    out = pd.DataFrame({
        "time": pd.to_datetime(raw[COLS["date"]] + " " + raw[COLS["time"]],
                               format="%Y-%m-%d %H:%M:%S"),
        "heat_set": pd.to_numeric(raw[COLS["heat_set"]], errors="coerce"),
        "indoor": pd.to_numeric(raw[COLS["indoor"]], errors="coerce"),
        "outdoor": pd.to_numeric(raw[COLS["outdoor"]], errors="coerce"),
        "heat_run_s": pd.to_numeric(raw[COLS["heat_run"]], errors="coerce").fillna(0),
    }).dropna(subset=["indoor", "outdoor"])
    out["runtime_frac"] = (out["heat_run_s"] / INTERVAL_SECONDS).clip(0, 1)
    out["date"] = out["time"].dt.date
    return out.sort_values("time").reset_index(drop=True)


def daily(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("date").agg(
        outdoor=("outdoor", "mean"),
        indoor=("indoor", "mean"),
        heat_set=("heat_set", "mean"),
        runtime_frac=("runtime_frac", "mean"),
        n=("runtime_frac", "size"),
    ).reset_index()
    return g[g["n"] >= 200]  # only near-complete days (>=200 of 288 intervals)


def fit_ua_ratio(d: pd.DataFrame):
    """Fit runtime_frac = k*(indoor - outdoor) + b over heating days.
    Returns k (= UA/furnace_output), b, and the heating-onset outdoor temp."""
    heating = d[d["runtime_frac"] > 0.02].copy()
    dt = heating["indoor"] - heating["outdoor"]
    k, b = np.polyfit(dt, heating["runtime_frac"], 1)
    # onset: runtime_frac -> 0  =>  dt0 = -b/k ; onset_outdoor = indoor - dt0
    dt0 = -b / k
    onset_outdoor = float(heating["indoor"].mean() - dt0)
    return float(k), float(b), onset_outdoor, heating["indoor"].mean()


def hp_capacity(hp: dict, t_f: float) -> float:
    xs = np.array(sorted(hp["cap"]))
    ys = np.array([hp["cap"][t] for t in xs]) * hp["units"]
    cap = float(np.interp(t_f, xs, ys))
    return 0.0 if t_f < hp["tmin"] else cap


def balance_point(hp: dict, ua: float, indoor: float) -> float:
    grid = np.linspace(-20, indoor, 8801)
    caps = np.array([hp_capacity(hp, t) for t in grid])
    load = ua * (indoor - grid)
    diff = caps - load
    cross = np.where(np.diff(np.sign(diff)) != 0)[0]
    for idx in cross[::-1]:
        if diff[idx] <= 0 <= diff[idx + 1]:
            return round(float(grid[idx + 1]), 1)
    return float("nan")


def fig_runtime(d: pd.DataFrame, k: float, b: float, indoor_mean: float):
    FIGDIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(d["outdoor"], d["runtime_frac"] * 100, s=28, color="#4C72B0",
               alpha=0.8, label="daily observations")
    xs = np.linspace(d["outdoor"].min(), 60, 100)
    yfit = np.clip(k * (indoor_mean - xs) + b, 0, 1) * 100
    ax.plot(xs, yfit, color="black", lw=2, label="fit (UA/furnace-output)")
    ax.axvline(DESIGN_T_F, color="#C44E52", ls="--", label=f"design temp ({DESIGN_T_F:.0f} F)")
    ax.set_xlabel("Daily mean outdoor temperature (F)")
    ax.set_ylabel("Furnace runtime (% of the day)")
    ax.set_title("Measured furnace runtime vs outdoor temperature\n"
                 "(ecobee 5-min data, Nov 2025 - Mar 2026)")
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_ylim(0, 100)
    fig.tight_layout()
    fig.savefig(FIGDIR / "ecobee-runtime.png", dpi=130)
    plt.close(fig)


def main():
    df = load_ecobee()
    d = daily(df)
    print(f"Loaded {len(df):,} 5-min records across {df['date'].nunique()} days "
          f"({df['time'].min():%Y-%m-%d} to {df['time'].max():%Y-%m-%d}); "
          f"{len(d)} near-complete days used.")

    # --- setpoint schedule (no furnace nameplate needed) ---
    sp = df.dropna(subset=["heat_set"])
    by_hour = sp.groupby(sp["time"].dt.hour)["heat_set"].mean()
    print("\nHeat setpoint schedule (deg F by hour of day):")
    print("  day (9-21h) avg: %.1f | night/sleep min: %.1f | overall mean: %.1f"
          % (by_hour.loc[9:21].mean(), by_hour.min(), sp["heat_set"].mean()))

    # --- runtime vs temp regression ---
    k, b, onset, indoor_mean = fit_ua_ratio(d)
    frac_design = float(np.clip(k * (indoor_mean - DESIGN_T_F) + b, 0, 1))
    coldest_day = d.loc[d["outdoor"].idxmin()]
    print(f"\nMeasured indoor mean: {indoor_mean:.1f} F")
    print(f"Heating-onset outdoor temp (furnace starts): {onset:.1f} F "
          "(= your effective balance point of internal gains)")
    print(f"Furnace runtime slope k = {k*100:.3f} %/degF  (this is UA / furnace_output)")
    print(f"Extrapolated furnace runtime at the {DESIGN_T_F:.0f} F design temp: "
          f"{frac_design*100:.0f}% of the time")
    print(f"Coldest day observed: {coldest_day['outdoor']:.1f} F avg, "
          f"furnace ran {coldest_day['runtime_frac']*100:.0f}% that day")

    fig_runtime(d, k, b, indoor_mean)
    print(f"Wrote {FIGDIR / 'ecobee-runtime.png'}")

    # --- resolve to absolute Btu, parameterized by furnace size ---
    def report_for_input(inp):
        out_btu = inp * FURNACE_AFUE
        ua = k * out_btu                       # Btu/hr per degF (physical, setpoint-free)
        design_load = ua * (DESIGN_INDOOR_F - DESIGN_T_F)   # sized to a comfy 70 F
        line = (f"  input {inp:>6} -> output {out_btu:>6.0f} Btu/hr | "
                f"UA {ua:5.0f} | design load {design_load:6.0f} Btu/hr @ {DESIGN_T_F:.0f} F")
        for name, hp in HP.items():
            bp = balance_point(hp, ua, DESIGN_INDOOR_F)
            line += f" | {name.split(' ')[0]} bal {bp:5.1f} F"
        return line

    print(f"\nAbsolute load parameterized by furnace INPUT size "
          f"(AFUE {FURNACE_AFUE:.0%}, sized to hold {DESIGN_INDOOR_F:.0f} F @ "
          f"{DESIGN_T_F:.0f} F design):")
    sizes = [FURNACE_INPUT_BTU] if FURNACE_INPUT_BTU else INPUT_SWEEP
    for inp in sizes:
        print(report_for_input(inp))
    if not FURNACE_INPUT_BTU:
        print("  (set FURNACE_INPUT_BTU from the nameplate to collapse this to one row)")

    # --- gas cross-check: solve furnace output from gas energy + runtime hours ---
    runtime_hours = df["heat_run_s"].sum() / 3600.0
    heating_ccf = sum((v - GAS_BASELOAD_CCF_PER_DAY) * days
                      for v, days in GAS_CCF_PER_DAY.values())
    therms = heating_ccf * CCF_TO_THERM
    delivered = therms * 100_000 * FURNACE_AFUE          # Btu delivered to the house
    furnace_output = delivered / runtime_hours           # Btu/hr -- the nameplate answer
    print("\nGAS CROSS-CHECK (Consumers CCF/day x days, over the ecobee period):")
    print(f"  furnace runtime this period: {runtime_hours:,.0f} hours")
    print(f"  heating gas: {heating_ccf:,.0f} CCF = {therms:,.0f} therms "
          f"= {delivered/1e6:,.1f} MMBtu delivered @ AFUE {FURNACE_AFUE:.0%}")
    print(f"  => SOLVED furnace output ~ {furnace_output:,.0f} Btu/hr "
          f"(input ~ {furnace_output/FURNACE_AFUE:,.0f} Btu/hr)")
    ua_gas = k * furnace_output
    design_load = ua_gas * (DESIGN_INDOOR_F - DESIGN_T_F)
    print(f"  => UA ~ {ua_gas:,.0f} Btu/hr-F, design load ~ {design_load:,.0f} Btu/hr "
          f"@ {DESIGN_T_F:.0f} F (to hold {DESIGN_INDOOR_F:.0f} F)")
    for name, hp in HP.items():
        bp = balance_point(hp, ua_gas, DESIGN_INDOOR_F)
        cov = "covers design temp" if bp <= DESIGN_T_F else "SHORT of design"
        print(f"     {name}: balance point {bp:.1f} F ({cov})")

    # --- sniff test: load intensity + stress test against a higher true load ---
    print(f"\nSNIFF TEST (home {HOME_SQFT} sqft):")
    print(f"  design-load intensity: {design_load / HOME_SQFT:.1f} Btu/hr-sqft "
          "(uninsulated rule-of-thumb 30-45; air-sealed old house 15-25)")
    clim = pd.read_csv(HERE / "data" / "grr-hourly-temps.csv")
    nyr = clim["year"].nunique()
    single = HP["1x 3.5-ton (PVA-A42)"]
    print("  load stress test -- balance point if the TRUE load is higher than measured:")
    for m in (1.0, 1.2, 1.3, 1.5):
        ua_s = ua_gas * m
        bp = balance_point(single, ua_s, DESIGN_INDOOR_F)
        below = (clim["temp_f"] < bp).sum() / nyr if not np.isnan(bp) else float("nan")
        tag = "covers design temp" if (not np.isnan(bp) and bp <= DESIGN_T_F) else "below design temp"
        print(f"    x{m:.2f} (design load {ua_s*(DESIGN_INDOOR_F-DESIGN_T_F):6.0f} Btu/hr): "
              f"1x bal {bp:5.1f} F, {below:5.1f} hr/yr below balance ({tag})")


if __name__ == "__main__":
    main()
