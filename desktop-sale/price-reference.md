# Price Reference — Build Components

**Pulled:** 2026-04-26
**Sources:** eBay sold/completed listings (last ~90 days, filtered to working units) + r/hardwareswap recent-month posts (via `search-hardwareswap.py`)

## How to read this

- **eBay used median** = real sell-through prices with buyer protection. Treat as the *ceiling* for your hardwareswap ask.
- **Hardwareswap median** = real asks (and a few closed sales) on r/hws. Typically runs 10–15% under eBay because friction is lower and there's no marketplace fee.
- **Suggested ask** = hardwareswap median, give or take, depending on volume and trend.
- Outliers excluded: "FOR PARTS / NOT WORKING / READ" listings on eBay (genuinely broken units), and bundle/multi-item posts on hardwareswap that contaminated the price extraction.

## Snapshot

| Part | eBay used median | r/hws median | Suggested ask | vs. partout-prices.md |
|---|---:|---:|---:|---|
| RTX 4090 Founders Edition | ~$2,500 | ~$2,200 | **$2,150** | +$100 (raise from $2,050) |
| Ryzen 9 7950X3D | ~$385 | ~$375 | **$375** | unchanged |
| Corsair Vengeance 64GB DDR5-6000 | ~$600 | sparse | **$600** | **−$150 (drop from $750)** |
| Crucial T700 1TB Gen5 | ~$140 | sparse | **$150** | −$25 (drop from $175) |
| ASUS ROG Strix B650E-I | ~$185 | ~$175 | **$175** | +$5 |
| Corsair SF850L | ~$122 | ~$115 | **$115** | unchanged |
| Fractal Design Terra (Jade) | ~$140 | sparse | **$140** | +$5 |
| ID-COOLING IS-55 Black | ~$30 | n/a | **$30** | +$5 |
| **Total revised partout** | | | **$3,735** | vs. $3,795 prior |

**Headline change:** the DDR5 64GB number drops sharply. The April 21 research had it at $750 anchored to retail; real eBay sell-through over the last 30 days clusters at $500–$609. Retail price did not move, but used-market buyers aren't paying the retail premium. The total partout estimate only falls ~$60 (the DDR5 drop is partly offset by the 4090 rebound), so the bundle ask of $3,400/$3,500 still saves the buyer $235–$335 vs. parting out — a real spread, just thinner than the $395 it looked like before.

---

## 1. NVIDIA GeForce RTX 4090 Founders Edition

**eBay used median:** ~$2,500 · **range $2,426–$2,899** for clean working FE
**Sealed/NIB on eBay:** $2,924, $2,949
**r/hardwareswap:** range $2,030–$2,375 · median $2,200 · 9 clean comps

### Recent eBay sold (working FE only)

| Price | Date | Title |
|---:|---|---|
| $2,899 | Apr 16, 2026 | RTX 4090 FE Founders Edition 24GB GDDR6X – Excellent |
| $2,699 | Apr 23, 2026 | RTX 4090 24GB Founders Edition |
| $2,599 | Apr 20, 2026 | RTX 4090 Founders Edition 24GB GDDR6X |
| $2,500 | Apr 19, 22, 25 | RTX 4090 Founders Edition 24GB (3 separate sales) |
| $2,500 | Apr 22, 2026 | RTX 4090 FE 24GB & BOX |
| $2,426 | Apr 17, 2026 | RTX 4090 Founders Edition 24GB GDDR6X |

### Recent r/hardwareswap

- $2,100 [USA-NY] — `[CLOSED]`
- $2,030 / $2,100 / $2,200 [USA-MN] — `[CLOSED]` (buyer thread, those were offer prices)
- $2,100 / $2,300 [USA-IN] — `[CLOSED]`
- $2,200 / $2,300 [USA-MD] — bundle context, 4090FE included
- $2,325 / $2,340 / $2,375 [USA-AR] — multi-GPU partout
- Trade context: [USA-IN] looking to trade 4090FE for 5080FE + cash

**Read:** eBay clears comfortably above $2,400 for clean used FE; hardwareswap lives in the $2,100–$2,300 band. Suggested ask $2,150 is conservative-aggressive — leaves room to negotiate to $2,050 floor. If listing patient on eBay, $2,400 is realistic.

---

## 2. AMD Ryzen 9 7950X3D

**eBay used median:** ~$385 · **range $345–$399** for clean working chips
**Sealed/new on eBay:** $490–$500
**r/hardwareswap:** range $350–$400 · median $375 · 8 clean comps

### Recent eBay sold (used)

| Price | Date | Title |
|---:|---|---|
| $399 | Apr 22, 2026 | AMD Ryzen 9 7950x3D 5.70GHz CPU AM5 |
| $389 | Apr 26, 2026 | AMD Ryzen 9 7950X3D cpu |
| $388 | Apr 23, 2026 | Ryzen 9 7950X3D AM5 16C/32T |
| $385 | Apr 22, 24 | Ryzen 9 7950X3D 5.70GHz (2 sales) |
| $350 | Apr 21, 21, 25 | Ryzen 9 7950X3D 16-Core (3 sales) |
| $345 | Apr 24, 2026 | AMD Ryzen 9 7950X3D 16-Core |

### Recent r/hardwareswap

- $375 [USA-FL] — selling alongside 9800X3D, 7800X3D
- $375 [USA-FL] — bundle with 4090 Gigabyte
- $375 [USA-PA] — `[CLOSED]`
- $390 [USA-CA] — High End Computer Parts post
- $390 [USA-AR] — multi-CPU partout
- $400 [USA-AZ] — bundle
- $360 [USA-CA]
- $350 [USA-OR]

**Read:** Tightest price band of any component. $375 is dead-on the going rate.

---

## 3. Corsair Vengeance 64GB DDR5-6000 (CMK64GX5M2B6000C30)

**eBay used median:** ~$600 · **range $500–$609** for clean Apr 2026 sales
**One outlier high:** $1,050 (Apr 17)
**r/hardwareswap:** sparse — most matches were false positives (32GB kits)
**New retail (Z30 variant, Best Buy):** $1,071.99

### Recent eBay sold

| Price | Date | Title |
|---:|---|---|
| $609 | Apr 24, 2026 | Corsair Vengeance 64GB 2x32GB DDR5 6000 CL30 EXPO/XMP Grey |
| $600 | Apr 16, 17, 17, 26 | CORSAIR VENGEANCE 64GB (2x32GB) DDR5 6000 CL30 (4 sales) |
| $599 | Apr 10, 14 | Corsair Vengeance 64GB 2x32GB DDR5 6000 CL30 (2 sales) |
| $569 | Apr 13, 2026 | Corsair Vengeance 64GB DDR5 6000 CL30 (Black) |
| $549 | Apr 11, 2026 | Corsair Vengeance DDR5 64GB CMK64GX5M2B6000Z30 |
| $510 | Apr 19, 2026 | Corsair Vengeance 64GB DDR5 6000 CL30 (Black) |
| $500 | Apr 11 ×2 | Corsair Vengeance 64GB CMK64GX5M2B6000Z30 |

### Recent r/hardwareswap

Data was mostly noise — script extracted prices from posts where 64GB DDR5 was a small line item in larger bundles, and most actual matches were 32GB kits. No clean single-kit r/hws comp surfaced this month.

**Read:** Single biggest revision from prior research. Retail floor stayed at $1,070+ but eBay buyers aren't paying that for used — they're paying $500–$610. The $750 number in `partout-prices.md` was anchored to retail and didn't reflect actual sell-through. **List at $600**, expect some "would you take $500" lowballs.

---

## 4. Crucial T700 1TB Gen5 NVMe (CT1000T700SSD3)

**eBay used median:** ~$140 · **range $129–$153** for Q1 2026 sales
**One outlier:** $299 (likely bundle)
**r/hardwareswap:** essentially no clean comps this month
**New retail:** ~$295 (Tom's Hardware tracker)

### Recent eBay sold

| Price | Date | Title |
|---:|---|---|
| $153 | Aug 9, 2025  | Crucial 1TB SSD T700 GEN5 PCIe 5.0 |
| $152 | Feb 22, 2026 | Crucial T700 1TB M.2 NVMe Internal SSD |
| $139 | Apr 20, 2026 | Crucial T700 Gen5 1TB CT1000T700SSD3 |
| $139 | Mar 29, 2026 | Crucial T700 Gen5 1TB CT1000T700SSD3 |
| $137 | Feb 26, 2026 | Crucial T700 Pro PCIe Gen5 NVMe 1TB |
| $135 | Mar 28, 2026 | Crucial T700 Gen5 1TB CT1000T700SSD3 |
| $135 | Mar 15, 2026 | Crucial T700 1TB PCIe 5.0 11,700 MB/s |
| $129 | Mar 7, 2026  | Crucial T700 CT1000T700SSD3 1TB |

### Recent r/hardwareswap

No isolated T700 1TB sales this month. Drives are usually bundled with builds or paired with 2TB/4TB SSDs in multi-item listings.

**Read:** eBay tells the truer story here — used T700 1TB clears at $130–$150, well below the $175 in `partout-prices.md`. The previous research note about "Gen5 caught up with DRAM crisis" may have been overstated. Suggested ask $150 leaves room to drop to $140 if needed.

---

## 5. ASUS ROG Strix B650E-I Gaming WiFi

**eBay used median:** ~$185 · **range $99–$239** (heavy variance — condition matters)
**Refurbished:** $169
**Broken/parts:** $32–$54
**r/hardwareswap:** range $150–$215 · median $175 · 5 clean comps
**New retail:** $229 Newegg (sometimes $209 with code)

### Recent eBay sold (working)

| Price | Date | Title |
|---:|---|---|
| $239 | Apr 23, 2026 | ASUS ROG Strix B650E-I Gaming WiFi Mini ITX |
| $229 | Apr 24, 2026 | ASUS ROG STRIX B650E-I AM5 DDR5 PCIe 5.0 |
| $209 | Apr 23, 2026 | ASUS ROG STRIX B650E-I GAMING WIFI 6E |
| $190 | Apr 23, 2026 | ASUS ROG STRIX B650E-I |
| $185 | Apr 20, 2026 | ASUS ROG STRIX B650E-I |
| $175 | Apr 22, 2026 | ASUS ROG STRIX B650E-I |
| $169 | Apr 23, 2026 | (Factory Refurbished) ASUS ROG B650E-I |
| $152 | Apr 24, 2026 | ASUS ROG Strix B650E-I Gaming WiFi 6E |
| $120 | Apr 25, 2026 | ASUS ROG STRIX B650E-I (low — likely cosmetic) |

### Recent r/hardwareswap

- $160 local / $180 shipped [USA-NY] — light use, OBO, original box
- $185 [USA-MD] — bundle with MacBook Pro M5, RTX 5070 Ti
- $215 [USA-CA] `[CLOSED]` — FormD T1 SFF parts bundle
- $165 [USA-NJ] — multi-CPU/mobo combos
- $150 [USA-FL] — gaming PC parts bundle

**Read:** Pricing depends on condition. With original box and good cosmetic: $175–$200. Pure functional: $150–170. Suggested $175 splits the difference.

---

## 6. Corsair SF850L SFX

**eBay used median:** ~$122 · **range $89–$165** (some confusion with SF850 Platinum vs SF850L Gold)
**r/hardwareswap:** range $110–$120 · median $120 · 2 clean comps
**New retail:** ~$180

### Recent eBay sold (SF850L specifically)

| Price | Date | Title |
|---:|---|---|
| $129 | Apr 10, 2026 | Corsair SF-L Series SF850L Fully Modular |
| $122 | Apr 16, 2026 | Corsair SF-L SF850L 850W Modular |
| $120 | Apr 15, 2026 | Corsair SF-L series SF850L |
| $119 | Jan 26, 2026 | Corsair SF850L SFX-L 850W ATX 3.0 PCIe 5.0 |
| $89  | Feb 7, 2026  | CORSAIR SF850L 850W 80 Plus Gold (low — possibly issue) |
| $150 | Mar 1, 2026  | Corsair SF-L Series SF850L |

Note: several other "$150 SF850" sales are actually the **SF850 Platinum** (different product, no -L). Not directly comparable.

### Recent r/hardwareswap

- $120 [USA-NC] — full system part-out
- $110 [USA-FL] — selling SF850L, SF750, SF600 together

**Read:** $115 ask is right in the band. Easy sell, low value, no urgency.

---

## 7. Fractal Design Terra (Jade) + PCIe 4.0 Riser

**eBay used median:** ~$140 · **range $99–$204** for Jade variants Apr 2026
**Open-box / basically new:** $199–$204
**r/hardwareswap:** sparse — only bundle context
**New retail:** $199 (current Newegg/Microcenter)

### Recent eBay sold (Jade)

| Price | Date | Title |
|---:|---|---|
| $204 | Apr 3, 2026  | Fractal Design Terra FD-C-TER1N-03 Jade No PSU |
| $199 | Apr 6, 11    | Fractal Design Terra Jade Mini-ITX w/ PCIe 4.0 Riser (2 sales — basically retail) |
| $169 | Jan 27, 2026 | Fractal Terra Open Box |
| $155 | Mar 29, 2026 | Fractal Design Terra Mini-ITX |
| $132 | Mar 25, 2026 | Fractal Design Terra Mini-ITX |
| $129 | Mar 25, 2026 | Fractal Design Terra Jade FD-C-TER1N-03 |
| $119 | Apr 25, 2026 | Fractal Design Terra Jade Mini-ITX |
| $99  | Apr 4, 2026  | Fractal Design Terra Jade w/ Walnut + Noctua fan |

(Other-color comp: $175 Apr 23 for Terra Graphite NEW with riser.)

### Recent r/hardwareswap

Mentioned in two SFF builds (USA-PA Ryzen 9700X / 9070XT) but no isolated case sale this month.

**Read:** Jade with riser, used good condition, clears around $130–$155 on eBay. $199 happens for near-mint with all original packaging. Suggested $140.

---

## 8. ID-COOLING IS-55 Black PWM

**eBay used median (IS-55):** ~$30 · **range $16–$57**
**New IS-55 ARGB:** $39–$57 still in stock retail
**r/hardwareswap:** not searched (low-value bundle)
**Noctua NF-A4x10 separately:** $5–$10

### Recent eBay sold (IS-55)

| Price | Date | Title |
|---:|---|---|
| $57 | Mar 10, 25 | ID-COOLING IS-55 ARGB / Black (NEW or near-new) |
| $40 | Apr 20, 2026 | ID-COOLING IS-55 Black Low Profile |
| $39 | Mar 5, 14 | NEW ID-COOLING IS-55 ARGB |
| $30 | Mar 30, 2026 | ID-COOLING IS-55 ARGB White |
| $29 | Apr 22, 2026 | ID-Cooling IS-55 ARGB |
| $28 | Apr 20, 2026 | ID Cooling IS-55 RGB Low Profile |
| $20 | Mar 22, 2026 | ID-COOLING IS-55 Black 5 Heatpipes |
| $16 | Apr 7, 2026  | ID-COOLING IS-55 ARGB White |

**Read:** Bundle the IS-55 + Noctua at $30 to move. Not worth more effort than that.

---

## What changed since the April 21 pull

| Component | Apr 21 estimate | Apr 26 (this pull) | Delta |
|---|---:|---:|---:|
| RTX 4090 FE | $2,100 | $2,150 | +$50 (slight rebound on hws) |
| 7950X3D | $385 | $375 | −$10 |
| 64GB DDR5-6000 | $800 | **$600** | **−$200** (retail-anchor was off) |
| T700 1TB | $185 | $150 | −$35 |
| B650E-I | $180 | $175 | −$5 |
| SF850L | $120 | $115 | −$5 |
| Terra Jade | $150 | $140 | −$10 |
| IS-55 + Noctua | $27 | $30 | +$3 |
| **Total** | **$3,947** | **$3,735** | **−$212** |

The DDR5 correction is the headline (−$200 alone). Everything else moved single-digit dollars or stayed flat, except a small +$50 rebound on the 4090. **`partout-prices.md` should be updated** if you want it to drive the hardwareswap-listing pricing table; otherwise the listing will price the RAM ~$150 high.
