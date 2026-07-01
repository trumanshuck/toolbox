# Heat-pump feasibility — Grand Rapids craftsman

Should we replace the gas furnace with an all-electric cold-climate heat pump? This project
answers that with a temperature-bin / balance-point analysis against 5 years of local climate data.

## Read this first
- **[report.md](report.md)** — the recommendation and the reasoning. Start here.
- **[climate-analysis.md](climate-analysis.md)** — the bin analysis: how cold it actually gets,
  balance points, cold snaps, and what the figures show.
- **[equipment-reference.md](equipment-reference.md)** — design temperatures, the real NEEP
  heat-pump capacity/COP tables, zoning/duct options, rebates, rates, and all sources.

## Reproduce the numbers
```
python3 analyze.py            # climate + scenarios + carbon/cost (uses cached data/)
python3 analyze.py --refetch  # re-download raw NOAA ISD data
python3 ecobee_analysis.py    # empirical Manual J from your ecobee runtime data
```
Requires Python 3 with `pandas`, `numpy`, `matplotlib`.

`ecobee_analysis.py` reads the ecobee HomeIQ CSV exports in `data/ecobee/` (gitignored — they contain
your thermostat id and occupancy patterns) and backs out your measured heat-loss rate. Set
`FURNACE_INPUT_BTU` at the top of that file (from the furnace nameplate) to resolve absolute Btu.

`analyze.py` writes:
- `data/grr-hourly-temps.csv` — cleaned hourly temps, KGRR, 2020-2024 (committed).
- `data/temp-bins.csv` — hours per 5 F bin.
- `figures/temp-histogram.png`, `figures/load-vs-capacity.png`.

Every quantitative claim in the markdown is printed by `analyze.py`'s summary block. If you change
an assumption (envelope, equipment, rates, grid factor), edit the CONFIG constants at the top of
`analyze.py` and re-run — don't edit numbers into the prose by hand.

## Data source
NOAA NCEI Integrated Surface Database (global-hourly), station 72635094860 —
Grand Rapids / Gerald R. Ford International Airport (KGRR).
