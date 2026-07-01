# Should we replace the gas furnace with a heat pump?

**Grand Rapids, MI · ~100-year-old craftsman · air-sealed, attic + rim insulated, uninsulated walls
· wants all-electric + eventual upstairs/downstairs zoning**

*All quantitative claims come from `analyze.py` (5 full years of KGRR hourly data, 2020–2024) and the
sourced tables in [equipment-reference.md](equipment-reference.md). See
[climate-analysis.md](climate-analysis.md) for the bin analysis and figures.*

---

## Bottom line

**Yes — a cold-climate heat pump is a technically sound all-electric replacement for your furnace in
Grand Rapids, and your own data now proves it with margin to spare.** Two independent methods — five
months of ecobee runtime data and your Consumers Energy gas usage — converge on the same measured
numbers: your house loses about **493 BTU/hr per °F**, a design-day load near **31,500 BTU/hr**, from
a furnace that turns out to be **~66,000 BTU/hr** (solved from the data, no nameplate needed) and that
ran only ~50% even on the coldest day of the winter. Against that, **a single 3.5-ton cold-climate
heat pump holds its balance point to −10.5 °F — colder than the coldest hour in five years of Grand
Rapids weather (−9.9 °F).** So a single unit covers essentially every hour, all-electric, no backup.
The only remaining open question is mechanical: whether your old ductwork can move a heat pump's
higher airflow — answerable with a duct evaluation before you buy.

Three things to know going in, matched to your priorities:
- **Comfort & zoning (your #1):** the two-system, one-per-floor layout that gives you the best zoning
  is also the one that leaves your existing basement ductwork intact. Your instinct that zoning means
  "major duct reconfiguration" is, happily, backwards.
- **Carbon (your #2):** a heat pump is cleaner than your furnace today and gets cleaner every year as
  Consumers Energy retires coal — the opposite of a gas furnace, whose emissions never improve.
- **Cost (secondary):** be clear-eyed here — at today's Michigan prices (expensive electricity, cheap
  gas), **heating will likely cost somewhat *more* to run than gas.** You're buying comfort, cooling,
  and a decarbonization path, not a lower heating bill.

---

## 1. The climate is easily within range

Over five years, Grand Rapids spent only **~22 hours per year below the 6 °F design temperature** and
**under 5 hours per year below 0 °F**. The coldest hour in five years was **−9.9 °F** — above the
**−13 °F** operating floor of the representative equipment. The worst sustained cold snap was about a
day bottoming near −10 °F. The heating season lives mostly in the 25–45 °F band, exactly where a
cold-climate heat pump runs efficiently (seasonal COP ≈ **3.0** on this data).

The "will it handle a Michigan winter?" fear is aimed at a sliver of the year that modern hyper-heat
equipment is specifically built for. It will.

## 2. Can one heat pump replace the furnace *and* the AC?

Yes on the AC automatically — **a heat pump is an air conditioner that also runs in reverse**, so it
replaces your central AC by default (and a variable-speed one dehumidifies better through our humid
summers; cooling design here is only ~86 °F).

On heating, it comes down to your load — the one number we're missing:

| Your real heat load | What covers it |
|---|---|
| **Low** (~40k Btu/hr — plausible for ~1,600–2,000 sqft you've already air-sealed) | A **single 3.5-ton** hyper-heat covers essentially the whole climate; balance point below 0 °F, ~4 hr/yr of any shortfall. |
| **Typical** (rule-of-thumb ~64k) | A single unit falls short on the coldest ~470 hr/yr — but **two smaller units, one per floor**, bring the balance point down to the 6 °F design temp (~22 hr/yr below). *That's your zoning setup.* |
| **High/leaky** (~96k) | Even two units strain; this is where a Manual J + a little targeted envelope work (or accepting modest backup) earns its keep. |

So "a single heat pump can't replace our furnace" is only true at the *high* end of the load
estimates — and those rules of thumb tend to overstate load once air sealing is credited. **The
single highest-value next step is a contractor Manual J** to turn that wide range into your actual
number. It likely lands lower than you fear.

## 3. Zoning without tearing up the house

You wanted variable-speed + upstairs/downstairs zoning, and worried two units would mean major duct
work. Building-science consensus flips that:

- **Best fit — two independent systems (one per floor).** Keep the existing ducted system for
  downstairs; add a **compact ducted air handler** (e.g. Mitsubishi SVZ/SEZ) for upstairs. The two
  systems are separate, so **the basement trunk is left intact** — you're *adding* a small second
  system, not re-plumbing the original. Each floor modulates to its own load: true zoning, no fighting.
- **Watch your moisture concern.** The tidy version tucks that upstairs air handler in the attic —
  which, in an *unconditioned* attic, invites the exact condensation problems you avoided walls over.
  Keep any added air handler in **conditioned space**, or use ductless heads upstairs instead.
- **Damper-zoning your single old trunk is the riskier path** — it often needs the trunk re-treed to
  split cleanly by floor, and it tempts installers toward a **bypass duct**, which recirculates
  conditioned air and can freeze the coil or crack a heat exchanger. If anyone proposes a bypass, say no.
- **Duct reality check first.** A heat pump needs ~1.5–3× a furnace's airflow, and old-house
  **returns** are the usual bottleneck. Get a **duct-leakage + static-pressure evaluation** alongside
  the Manual J before committing to equipment.

## 4. Carbon — cleaner now, and the trajectory is the point

Per MMBtu of delivered heat, on the current lower-Michigan grid average (a conservative,
coal-influenced number):

| Source | lb CO₂ / MMBtu delivered | vs. heat pump |
|---|---|---|
| **Heat pump** (seasonal COP 2.97) | **120** | — |
| Gas furnace, 80% (older) | 146 | heat pump **18% cleaner** |
| Gas furnace, 95% (condensing) | 123 | heat pump ~3% cleaner |

In absolute terms, at the mid load scenario that's roughly **10.3 vs 12.6 short tons CO₂/year** (heat
pump vs an 80% furnace). Two things make the real picture better than this table:
1. It uses the **grid-average** emission factor. **Consumers Energy's own mix is cleaner** and
   decarbonizing as coal plants retire, so your actual number is lower.
2. **The gas furnace never improves; the heat pump does.** Every year the grid gets cleaner, the same
   heat pump emits less. A furnace bought today locks in its emissions for its whole life.

For your electrification goal, that trajectory is the whole argument.

## 5. Cost — the honest tradeoff (secondary, but real)

At Consumers' current rates (~$0.20/kWh electricity, ~$1.15/therm gas), estimated **annual heating**
operating cost:

| Envelope scenario | Heat pump | Gas 80% | Gas 95% |
|---|---|---|---|
| Optimistic | ~$2,130 | ~$1,550 | ~$1,305 |
| Mid | ~$3,410 | ~$2,480 | ~$2,090 |
| Conservative | ~$5,110 | ~$3,720 | ~$3,130 |

**Heating will cost more to run on a heat pump than on gas** at today's Michigan price ratio —
electricity is expensive here relative to very cheap natural gas. To *break even* on operating cost
against a 95% furnace you'd need a seasonal COP near 4.8, which cold-climate equipment can't hit.
Partial offsets: the heat pump also handles **cooling** (efficiently replacing your AC), and this is
heating-only energy — not standing charges or the value of retiring the gas meter entirely.

Also note the incentive landscape has shifted: the **federal 25C heat-pump tax credit expired for
installs after Dec 31, 2025**, so for a future replacement assume no federal credit. Consumers offers
small rebates ($300 ASHP / $350 ductless), and income-qualified households may access Michigan's
MiHER program (up to $8,000/heat pump). Details and sources in
[equipment-reference.md](equipment-reference.md).

**Upfront (capital) cost** for the representative system — Mitsubishi PVA-A42 + PUZ-HA42, 3.5-ton
hyper-heat, Grand Rapids 2025–2026:

| | Cost |
|---|---|
| Equipment only (the modeled pair) | ~$9,000–$11,000 |
| **Fully installed, single unit** | **~$13,000–$20,000** (typical MI retrofit $14K–$18K) |
| Two-per-floor zoned option | + ~$11,000–$18,000 (roughly a full second system) |
| Ductwork upgrades, if the airflow eval requires them | + $4,000–$12,000 |

The cold-climate (hyper-heat) premium over a standard heat pump is ~$1,000–$3,000 (~20–40% on
equipment) — the right spend for Zone 5, since it's what buys the −13 °F capability. Because a heat
pump replaces both the furnace *and* the AC, the money is best spent **when one of those is due for
replacement anyway** (your "when the time comes" framing). Sources: EnergySage, Michigan HVAC cost
guides, Got Ductless (see the cost note in [equipment-reference.md](equipment-reference.md)).

Given you ranked cost third, this is a "go in with eyes open" point, not a dealbreaker — but between
the higher running cost and the ~$14–18K install with no federal credit, a heat pump here is
**comfort + cooling + electrification spend, not an energy-savings payback.** Expect the heating-bill
line to go up, not down.

## 6. Pinning down your real numbers — bills, your ecobee, and solar

This analysis leans on scenarios because we don't yet have your house's measured numbers. Three
sources can replace the guesswork, in increasing order of quality:

1. **Gas bills → your real heating load.** Annual heating therms (total minus ~12× a summer month)
   ÷ this climate's degree-hours = your true heat-loss coefficient. Already built: see the table in
   [climate-analysis.md §4](climate-analysis.md). Even heavy gas use points to a load a single
   3.5-ton unit covers.
2. **Electric bills → your real cooling load.** Symmetric method: summer kWh minus a shoulder-month
   baseload = your AC electricity. Grand Rapids' cooling season is modest (~8,900 cooling
   degree-hours/yr), and a variable-speed heat pump cools for **~31% less** than a typical old AC —
   a small annual saving that offsets part of the higher heating cost. Both bill methods need your
   **thermostat setpoint** to be accurate (they assume ~68 °F heat / ~72 °F cool).
3. **Your ecobee runtime + gas bills → the gold standard (done).** Five months of HomeIQ data
   (Nov 2025–Mar 2026, 43k records) regressed cleanly: runtime vs. outdoor temp is nearly a straight
   line (`ecobee_analysis.py`, figure `figures/ecobee-runtime.png`). It measured your setpoint schedule
   (~66 °F day / 62 °F night, **64.5 °F mean** — you run cool) and your heating-onset temperature
   (~62 °F outdoors). Combined with your Consumers gas usage (which also **solved your furnace at
   ~66k BTU/hr** without opening a panel), it pins your measured **UA ≈ 493 BTU/hr·°F, design load
   ≈ 31,500 BTU/hr**, and a **single-unit balance point of −10.5 °F** — colder than any hour in five
   years. Definitive: **a single 3.5-ton cold-climate unit covers you, all-electric, no backup**
   (details in [climate-analysis.md §5](climate-analysis.md)).

**Where solar fits (you mentioned it's on the horizon).** Solar changes the *financial* picture but
not uniformly, because of timing:
- **Cooling and shoulder seasons line up beautifully with solar** — you'd cool the house on your own
  midday sun. That strengthens the "heat pump replaces the AC" economics directly.
- **Deep-winter heating is solar's weakest season** — December/January in Grand Rapids means short
  days, low sun angle, and snow on the panels, exactly when the heat pump draws most. Solar won't
  power the coldest-day heating in real time.
- **Michigan no longer has 1:1 net metering.** Consumers' Distributed Generation tariff credits
  exported energy below retail, so "bank summer overproduction to cover winter heat" is weaker than
  it used to be. Self-consumed solar (offsetting ~$0.20/kWh retail) is worth much more than exported
  solar. This matters a lot for whether solar closes the winter heating-cost gap.
- **Net:** solar makes the whole all-electric plan more coherent (one self-generated fuel) and
  improves lifetime economics — strongest on the cooling/shoulder side, partial on winter heating. To
  quantify it properly needs a monthly PV-production model (PVWatts for Grand Rapids) against monthly
  heat-pump load, plus the Consumers DG credit rate — a worthwhile add when you're ready.

## 7. Risks & how to retire them

| Risk | Mitigation |
|---|---|
| **Undersizing against uninsulated walls** (the biggest one) | Manual J before buying; size to the real load, not a rule of thumb. |
| Coldest-snap shortfall | Small in Grand Rapids (coldest −9.9 °F in 5 yr, within the −13 °F range). Right-sizing or the two-unit layout covers it; a modest strip-heat kit is a cheap insurance policy if you want zero risk. |
| Old ducts can't move heat-pump airflow | Duct-leakage + static-pressure test; upsize returns; target <10% leakage. |
| Attic moisture from added upstairs ducting | Keep the added air handler in conditioned space, or go ductless upstairs. |
| Higher heating bills | Expected; weigh against comfort, cooling, and carbon. Consider ccHP + keeping the furnace as a *dual-fuel backup* if you later want a cost hedge (note: that's not the all-electric path you specified). |

## Recommended next steps

1. **Get a Manual J load calculation** from a contractor who does cold-climate heat pumps — this
   single number decides single-unit vs two-unit and collapses the uncertainty in this whole analysis.
2. **Get a duct-leakage + static-pressure evaluation** of the existing system (returns especially).
3. Decide **single 3.5-ton vs two per-floor units** based on (load) and (your zoning goal) — they
   point the same way if your load is mid-or-higher.
4. Get quotes on **NEEP-listed ducted variable-speed** systems; insist on no bypass dampers and
   conditioned-space air handlers.
5. Treat this as your **furnace-replacement plan for when the time comes** — the climate case is
   settled; you're really deciding on load, ducts, and how much of a heating-bill increase the comfort
   and carbon are worth to you.

---

*Reproduce every number here with `python3 analyze.py`. Change assumptions in the CONFIG block at the
top of that file and re-run — the reports are meant to track the code, not the other way around.*
