# LLM Prompt Tree – Research Insights

This document summarizes the current knowledge captured across the modular LLM prompt trees. Each section highlights the most actionable findings, open issues, and recommended data sources to guide follow-on investigations or automation runs.

## 0. Mission Context & Exposure Limits
- **Mission Phases:** Reference DRMs (NASA DRA 5.0, Moon-to-Mars 2024) target ~6–9 month transits, ~500 sol surface stays, and similar-duration return legs. Cumulative dose for an unshielded mission would exceed 1 Sv, underscoring the need for sheltering strategies (`specs/radiation-shielding/RESEARCH_OVERVIEW.md`).
- **Propulsion Trade:** Faster trajectories (nuclear thermal/electric) can cut exposure by ~25–40% but demand higher Δv and complex refueling infrastructure (`specs/radiation-shielding/SYSTEM_SPEC.md` §1).
- **Logistics Synchronization:** Pre-deployed assets must include shielding mass (water, regolith movers) to ensure shelters are in place before crew landing (`system-spec/PROGRAMMATICS.md`).
- **Exposure Limits:** NASA’s current 600 mSv career limit (3% REID at 95% CL); ESA, CNSA, and Roscosmos adopt comparable probabilistic thresholds. Rolling limits are under review to personalize risk acceptance (`specs/radiation-shielding/MARS_MISSION_LESSONS.md`).
- **Contingencies:** Free-return aborts extend transit exposure by ~2–3 months; shelter consumables must cover at least 72 h of occupancy with margins for delayed ingress (`specs/system-engineering/LLM_TREE_3_SHELTER.md`).

## 1. Radiation Environment Characterization
- **GCR Baseline:** Cruise measurements from MSL RAD averaged 1.84 mSv/day during solar minimum; surface dose at Gale crater ~0.67 mSv/day (`specs/radiation-shielding/RESEARCH_OVERVIEW.md`).
- **Solar Modulation:** Dose varies ±30–40% between solar minimum and maximum; mission planning should bias toward solar maximum launch windows while managing elevated SPE risk (`LLM_TREE_1_ENVIRONMENT.md`).
- **SPE Design Events:** August 1972 remains the reference extreme, demanding ~15 g·cm⁻² hydrogen-equivalent shielding to maintain <50 mSv event dose.
- **Forecasting:** NOAA SWPC/ESA SSA provide alerts with tens-of-minutes lead time; onboard dosimetry (HERA, Timepix) must validate alerts to prevent false positives (`specs/dosimetry/README.md`).
- **Surface Environment:** Atmospheric depth (~16 g·cm⁻²) halves dose relative to deep space; regolith composition and hydration drive secondary neutron production (`specs/radiation-shielding/SYSTEM_SPEC.md` §5).

## 2. Shielding Materials & Structures
- **Hydrogen-Rich Materials:** Polyethylene (HDPE/UHMWPE) and water deliver best mass efficiency; BNNT/CNT composites show promise but remain TRL 3–4 (`specs/radiation-shielding/SUPPLIERS.md`).
- **Multifunctional Mass:** Water walls integrated with life support store 25–30% of outbound water inventory while providing ~5–8 g·cm⁻² along crew quarters; propellant depletion requires dynamic mass tracking (`system-spec/DESIGN_APPROACH.md`).
- **Regolith ISRU:** 1–2 m berms (≥1000 t regolith) cut surface dose by ~50%; robotic excavation must achieve ≥5 m³/day ahead of crew arrival (`system-spec/OPERATIONS_SUSTAINMENT.md`).
- **Active Concepts:** Superconducting magnetic shields remain mass/power prohibitive (>30 t, >20 kW), with cryogenic safety still open; electrostatics challenged by dusty plasma; continue technology watch (`LLM_TREE_2_MATERIALS.md`).

## 3. Storm Shelter & Habitat Design
- **Shelter Requirements:** 15–20 g·cm⁻² hydrogen-equivalent walls, <8 m² shelter footprint, and 72 h autonomous life support are recommended (`specs/radiation-shielding/SYSTEM_SPEC.md` §5).
- **Layout:** Logistics (water, food) should encircle sleep quarters to deliver everyday shielding; panels must be modular for repairs (`LLM_TREE_3_SHELTER.md`).
- **Surface Infrastructure:** Regolith berms, partial burial, and shielded rover garages provide safe havens; inspection via ground-penetrating radar or lidar should be scheduled per quarter (`system-spec/OPERATIONS_SUSTAINMENT.md`).
- **Maintenance:** Berm reinforcement and water-wall inspections form part of routine EVA planning; carry patch kits and spare bladder liners.

## 4. Dosimetry, Monitoring & Forecasting
- **Instrumentation:** Mixed suite—personal dosimeters (Timepix, bubble detectors), distributed neutron detectors, and TEPCs—provides coverage (`specs/dosimetry/README.md`).
- **Data Fusion:** Transport tools (HZETRN/OCT, OLTARIS, PHITS) should ingest real-time spectra for predictive updates; uncertainty reporting crucial for mission decisions.
- **Alerting:** Multi-tier thresholds (caution, warning, emergency) triggered by dose rate and heliophysics telemetry; automate summarization for crew tablets via small LLMs (`LLM_TREE_4_DOSIMETRY.md`).
- **Edge Processing:** Local buffering ensures monitoring during comm blackouts; onboard AI should flag deviations for manual verification.

## 5. Verification, Validation & Risk
- **Testing Campaigns:** Coordinate NSRL/HIMAC beam tests for shielding coupons and electronics; analog mockups (HI-SEAS, SIRIUS) rehearse shelter ops (`LLM_TREE_5_VERIFICATION.md`).
- **Risk Register:** Key risks—extreme SPE exceedance, dosimetry outage, regolith system failure—require mitigation owners and contingency plans (`system-spec/RISK_MANAGEMENT.md`).
- **Post-Mission Learning:** Archive dosimetry with medical data for long-term studies; update shielding requirements via configuration control.
- **Reporting Automation:** Small models can generate after-action reports, but human review remains mandatory to avoid drift.

## 6. Suppliers, Software & Policy
- **Materials SMEs:** Nanocomp Technologies, BNNT LLC, Teijin, Mitsui, BIAM—cover CNT/BNNT composites, hydrogen-rich polymers (`specs/radiation-shielding/SUPPLIERS.md`).
- **Instrumentation Providers:** Bubble Technology Industries, cosine measurement systems, Arktis—offer neutron and LET detectors; require calibration partnerships.
- **Analytics Vendors:** ASTRA LLC (space weather), Redwire (habitat integration) provide modeling services; track new entrants via NASA SBIR and ESA GSTP announcements.
- **Procurement Watch:** Monitor SAM.gov, ESA-Star, and JAXA RA channels; ensure suppliers meet ECSS/NASA quality standards and export control compliance (`LLM_TREE_6_SUPPLIERS.md`).
