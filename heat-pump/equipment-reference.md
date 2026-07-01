# Equipment, design conditions, zoning, incentives & rates

Reference data behind the analysis. Numbers used by `analyze.py` are marked. Sources linked inline.

---

## 1. Design temperatures — Grand Rapids (KGRR)

| Condition | Value | Used in model |
|---|---|---|
| **Heating, 99%** | **~6 °F** | `DESIGN_T_F = 6.0` |
| Heating, 99.6% | 1.4 °F | — |
| **Cooling, 1% DB / MCWB** | **86.4 °F / 71.8 °F** | cooling discussion |
| Cooling, 0.4% DB / MCWB | 89.3 °F / 73.5 °F | — |

Station: Grand Rapids / Gerald R. Ford Int'l (Kent County), WMO 726350, 42.88 °N, 85.52 °W.
The 99% heating design temperature means only ~1% of hours in an average year fall below it — our
5-year data puts that at **~22 hours/year below 6 °F** (see climate-analysis.md).

Sources: ASHRAE Handbook of Fundamentals climatic design conditions (reproduced in
[CaptiveAire design-temp table](https://www.captiveaire.com/catalogcontent/fans/sup_mpu/doc/winter_summer_design_temps_us.pdf));
[ENERGY STAR County-Level Design Temperature Reference Guide](https://www.energystar.gov/ia/partners/bldrs_lenders_raters/downloads/County%20Level%20Design%20Temperature%20Reference%20Guide%20-%202015-06-24.pdf)
(Kent County: 99% heating 6 °F, 1% cooling 87 °F).

---

## 2. Representative cold-climate heat pumps (NEEP / AHRI submittal data)

Both are **ducted, variable-speed (inverter) hyper-heating** systems — the type that maintains
capacity in the cold and supports zoning. Values are **maximum heating capacity (Btu/hr) and COP**
at each outdoor dry-bulb. `−5 °F` is not published by these units (they publish 47 / 17 / 5 / −13);
the model interpolates linearly between 5 °F and −13 °F.

### Unit B — Mitsubishi 3.5-ton ducted H2i: `PVA-A42AA7` + `PUZ-HA42NKA1`
Nominal 42,000 Btu/hr · **min operating temp −13 °F** · modeled as the single-system option.

| Outdoor °F | Max heating (Btu/hr) | COP |
|---|---|---|
| 47 | 48,000 | 3.65 |
| 17 | 48,000 | 2.12 |
| 5  | 48,000 | 1.91 |
| −13 | 38,400 | 1.55 |

Source: [Mitsubishi submittal SB_PVA-A42AA7_PUZ-HA42NKA1_202403](https://www.mitsubishitechinfo.ca/sites/default/files/SB_PVA-A42AA7_PUZ-HA42NKA1_202403.pdf).

### Unit A — Mitsubishi 2.5-ton ducted H2i: `PVA-A30AA7` + `PUZ-HA30NKA`
Nominal 30,000 Btu/hr · **min operating temp −13 °F** · modeled ×2 as the "one-per-floor" option.

| Outdoor °F | Max heating (Btu/hr) | COP |
|---|---|---|
| 47 | 34,000 | 3.8 |
| 17 | 32,000 | 2.2 |
| 5  | 32,000 | 2.0 |
| −13 | 25,600 | 1.7 |

Source: [Mitsubishi submittal PVA-A30AA7 Form 202103](https://resource.gemaire.com/is/content/Watscocom/Gemaire/mitsubishi_pva-a30aa7_article_1861855288254147_en_ss2.pdf).

> These specific models are illustrative, not a purchase recommendation. Carrier/Bosch IDS,
> Trane/American Standard, and Daikin offer comparable NEEP-listed ducted variable-speed units.
> The 47 °F COP corresponds to the rated (not maximum-capacity) row — treat COP at 47 °F as
> approximate. The key point for a cold climate is that both hold **full nominal capacity down to
> 5 °F** and keep running to **−13 °F**.

---

## 3. Zoning & ductwork — how to get upstairs/downstairs zoning

Ranked for this house (one existing basement duct system, wants ducted + zoning). The counter-
intuitive headline from building-science sources: **two small independent systems (one per floor)
is the *recommended* way to get true per-floor zoning, and it leaves the existing basement trunk
intact** — it does *not* require re-plumbing the original ductwork. Damper-zoning the single old
trunk is often the more troublesome path.

| Rank | Approach | True per-floor zoning | Invasiveness to existing ducts | Fit here |
|---|---|---|---|---|
| 1 | Keep ducted downstairs + **add a compact ducted air handler (Mitsubishi SVZ/SEZ) for upstairs, in *conditioned* space** | Excellent — each floor modulates to its own load | Low to the existing trunk (adds a 2nd small system) | Best match to "ducted + real zoning." |
| 2 | **Hybrid: ducted downstairs + ductless head(s) upstairs** | Very good (per room) | Lowest — no new upstairs ducts, no attic exposure | Strong fallback if upstairs duct routing is hard. |
| 3 | **Damper zoning on one variable-speed air handler** | Good *only if* the trunk already splits cleanly by floor | Potentially high — old single trunk often needs re-treeing | Riskiest in a ~1900 house; **never accept a bypass duct**. |
| 4 | Fully ductless multi-zone | Excellent (room-level) | None | Rejected on the ducted preference. |

Key gotchas for an old house:
- **A heat pump needs ~1.5–3× the airflow (CFM) of a furnace** of the same output (it delivers
  cooler air), so furnace-era ducts are often undersized — especially **returns**, which are the
  usual bottleneck. [Fine Homebuilding — Furnace to Heat Pump Retrofit](https://www.finehomebuilding.com/2024/03/06/furnace-to-heat-pump-retrofit),
  [NuWatt — Can I reuse existing ductwork?](https://nuwattenergy.com/en/heat-pump-guide/reuse-existing-ductwork)
- **Never use a bypass duct** with zone dampers — recirculated conditioned air can freeze the coil
  or crack a heat exchanger. [Energy Vanguard — To Zone or Not to Zone](https://www.energyvanguard.com/blog/to-zone-or-not-to-zone-and-how/),
  [GreenBuildingAdvisor — Achilles' Heel of Zoned Duct Systems](https://www.greenbuildingadvisor.com/article/the-achilles-heel-of-zoned-duct-systems)
- **Moisture note (relevant to you):** the tidy version of the two-system path puts a compact air
  handler + short ducts in an **unconditioned attic**, which building scientists discourage
  (condensation risk, ~130 °F attic temps). Given you avoided wall insulation over moisture
  concerns, keep any added air handler in *conditioned* space or use ductless heads upstairs.
  [GBA — Slim duct in unconditioned attic?](https://www.greenbuildingadvisor.com/question/mitsubishi-slim-duct-sez-in-unconditioned-attic)
- Before buying: get a **duct-leakage + static-pressure evaluation** and a **Manual J**; target
  duct leakage below ~10%. [CEE Duct Retrofit Decision Guide](https://cee1.org/images/pdf/CEE_Duct_Retrofit_Decision_Guide_TRC_01.16.24.pdf)
- Two-story reference designs treat "ducted heat pump(s) for a two-story home" as standard:
  [NYSERDA](https://www.nyserda.ny.gov/-/media/Project/Nyserda/Files/Programs/clean-heating-and-cooling/2-story-duct-air-source.pdf),
  [Mitsubishi SVZ](https://www.mitsubishicomfort.com/products/p-series/svz) /
  [SEZ](https://www.mitsubishicomfort.com/products/p-series/sez).

---

## 4. Carbon factors

| Factor | Value | Used in model |
|---|---|---|
| Lower-Michigan grid intensity (eGRID2023 **RFCM** subregion output rate) | **1,214 lb CO₂/MWh** = 1.214 lb/kWh | `GRID_CO2_LB_PER_KWH` |
| Natural gas combustion | **~11.7 lb CO₂/therm** (~117 lb/MMBtu) | `GAS_CO2_LB_PER_THERM` |
| Gas furnace AFUE range | 80% (non-condensing) – 95%+ (condensing) | `FURNACE_AFUE` |

The RFCM figure is the **subregion average**, still coal-influenced. Consumers Energy's own mix is
cleaner and decarbonizing (coal retirements underway), so using the subregion average is a
**conservative, heat-pump-unfavorable** input — the real carbon picture is better and improving.

Sources: [EPA eGRID subregion emission factors (2023)](https://www.epa.gov/egrid/summary-data)
(RFCM = 1,214.1 lb CO₂/MWh); [EPA GHG Emission Factors Hub](https://www.epa.gov/system/files/documents/2024-02/ghg-emission-factors-hub-2024.pdf)
and [AP-42 §1.4 Natural Gas Combustion](https://www.epa.gov/sites/default/files/2020-09/documents/1.4_natural_gas_combustion.pdf).

---

## 5. Incentives & rates (Consumers Energy territory, 2026)

**⚠️ Federal 25C tax credit has expired for future installs.** The 30%-up-to-$2,000 heat-pump
credit was terminated early by the One Big Beautiful Bill Act (P.L. 119-21): property must have been
**placed in service on or before Dec 31, 2025**. Installs in 2026+ **do not qualify**. Since you're
planning for "when the time comes," assume **no federal 25C**.
Source: [IRS — Energy Efficient Home Improvement Credit](https://www.irs.gov/credits-deductions/energy-efficient-home-improvement-credit),
[Rewiring America — 25C](https://homes.rewiringamerica.org/federal-incentives/25c-heat-pump-tax-credits).

Still available:
- **Consumers Energy residential rebates** (participating-contractor install): air-source heat pump
  **$300**; ductless mini-split **$350**; geothermal $200–$300.
  [Consumers Energy heating & cooling rebates](https://www.consumersenergy.com/residential/save-money-and-energy/rebates/heating-and-cooling)
- **Michigan MiHER (IRA HEAR/HOMES, via EGLE)** — income-qualified: up to **$8,000 per heat pump**
  (≤150% AMI); low-income (≤80% AMI) up to $14,000 total.
  [Michigan EGLE Home Energy Rebate Programs](https://www.michigan.gov/egle/about/organization/materials-management/energy/rfps-loans/home-energy-rebate-programs)

**Energy rates (all-in midpoint estimates used for operating-cost math):**
| | Rate | Used in model |
|---|---|---|
| Electricity | ~$0.19–0.21/kWh (Consumers residential is time-of-use) | `ELEC_USD_PER_KWH = 0.20` |
| Natural gas | ~$1.09–1.25/therm (≈ $11.3–12.5/Mcf) | `GAS_USD_PER_THERM = 1.15` |

Sources: [EIA Michigan residential gas price](https://www.eia.gov/dnav/ng/hist/n3010mi3m.htm)
($11.32–12.51/Mcf, early 2026); [Consumers Energy electric rate book](https://www.consumersenergy.com/-/media/CE/Documents/rates/electric-rate-book.pdf);
EnergySage/EIA-derived Grand Rapids retail electricity ~19–21¢/kWh.

## 6. Equipment & install pricing (representative system, 2025–2026)

For the modeled Mitsubishi **PVA-A42AA7 + PUZ-HA42NKA1** (3.5-ton hyper-heat, 15.4 SEER2):

| Item | Price | Confidence |
|---|---|---|
| Equipment only (matched pair) | **~$9,000–$11,000** (~$9,900 clean online quote) | med-high |
| Fully installed, single unit (MI ducted cold-climate) | **~$13,000–$20,000** (typical $14K–$18K) | med |
| Two-per-floor zoned option | + ~$11,000–$18,000 (≈ a full second system) | low (extrapolated) |
| Ductwork upgrades if airflow eval requires | + $4,000–$12,000 | med |
| Cold-climate premium vs. standard heat pump | ~$1,000–$3,000 (~20–40% on equipment) | med |

Incentives (2026): Consumers Energy ASHP rebate **~$300** (this unit's 15.4 SEER2 qualifies; requires
a participating Trade Ally contractor via ConsumersHVAC.com); **MiHER up to $8,000** if
income-qualified; **federal 25C expired** after Dec 31, 2025 (see §5). Get 2–3 local Trade Ally quotes
to firm up the install figure — the numbers above are national/regional guides plus the exact
equipment pair, not a Grand Rapids quote.

Sources: [EnergySage air-source heat pump costs](https://www.energysage.com/heat-pumps/costs-and-benefits-air-source-heat-pumps/) ·
[Michigan HVAC cost estimates](https://michiganhvacauthority.com/michigan-hvac-cost-estimates/) ·
[Got Ductless — PVA-A42 + PUZ-HA42 system](https://gotductless.com/products/mitsubishi-42-000-btu-15-4-seer-p-series-hyper-heat-multi-position-air-handler-heat-pump-system-pva-a42aa7-puz-ha42nka1) ·
[Today's Homeowner — zoning vs. two systems](https://todayshomeowner.com/hvac/guides/hvac-zoning-vs-two-systems/).
