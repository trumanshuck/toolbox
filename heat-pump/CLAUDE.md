# heat-pump

Research project evaluating whether an **all-electric cold-climate heat pump** could
replace the gas furnace in a ~100-year-old craftsman in **Grand Rapids, MI** (air-sealed,
attic + basement-rim insulated, uninsulated walls; wants eventual upstairs/downstairs zoning).

The method is a **temperature-bin / balance-point analysis**: `analyze.py` pulls 5 full years
of NOAA hourly temperatures for KGRR, bins them, builds the house's heat-loss line, overlays
real NEEP cold-climate heat-pump capacity curves, and solves the balance point. **All numbers in
the markdown come from `analyze.py`** — do not hand-edit figures into the prose; change the code
and re-run. Start at `report.md`.
