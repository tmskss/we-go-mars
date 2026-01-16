# WE_GO_MARS Documentation Summary

This repository assembles research, planning guidance, and program surveys focused on radiation shielding for human Mars missions. Use this summary to navigate the major references and understand how the pieces fit together.

## Mission and Scope

- **Radiation Shielding Specification** – Core architecture assumptions, mission phases, and protection principles: [`specs/radiation-shielding/README.md`](specs/radiation-shielding/README.md)
- **Research Overview** – Literature synthesis covering shielding strategies, environmental data, and risk posture: [`specs/radiation-shielding/RESEARCH_OVERVIEW.md`](specs/radiation-shielding/RESEARCH_OVERVIEW.md)
- **Dosimetry Architecture** – Measurement objectives, instrumentation layers, and calibration workflows: [`specs/dosimetry/README.md`](specs/dosimetry/README.md)

## Mission Planning Playbooks

- **NASA Planning Workflow** – Lifecycle phases, systems engineering flow, and verification artifacts: [`specs/radiation-shielding/PLANNING.md`](specs/radiation-shielding/PLANNING.md)
- **ESA Planning Workflow** – ECSS processes, concurrent engineering, and partner coordination: [`specs/radiation-shielding/ESA_PLANNING.md`](specs/radiation-shielding/ESA_PLANNING.md)
- **Grand Challenges** – Cross-agency showstoppers framing technology roadmaps: [`specs/radiation-shielding/GRAND_CHALLENGES.md`](specs/radiation-shielding/GRAND_CHALLENGES.md)

## Procurement and Program Landscapes

- **NASA Solicitations** – Historical and current calls (NextSTEP, HERO, SBIR, RadWorks): [`specs/radiation-shielding/NASA_SOLICITATIONS.md`](specs/radiation-shielding/NASA_SOLICITATIONS.md)
- **ESA Tenders** – GSTP, Discovery & Preparation, OSIP, and E3P opportunities: [`specs/radiation-shielding/ESA_TENDERS.md`](specs/radiation-shielding/ESA_TENDERS.md)
- **Agency Snapshots**
  - CNSA programs: [`specs/radiation-shielding/CNSA_PROGRAMS.md`](specs/radiation-shielding/CNSA_PROGRAMS.md)
  - Roscosmos programs: [`specs/radiation-shielding/ROSCOSMOS_PROGRAMS.md`](specs/radiation-shielding/ROSCOSMOS_PROGRAMS.md)
  - JAXA programs: [`specs/radiation-shielding/JAXA_PROGRAMS.md`](specs/radiation-shielding/JAXA_PROGRAMS.md)
  - CSA programs: [`specs/radiation-shielding/CSA_PROGRAMS.md`](specs/radiation-shielding/CSA_PROGRAMS.md)
  - ISRO programs: [`specs/radiation-shielding/ISRO_PROGRAMS.md`](specs/radiation-shielding/ISRO_PROGRAMS.md)
- **Commercial Focus** – SpaceX Mars architecture and shielding approach: [`specs/radiation-shielding/SPACEX_PROGRAMS.md`](specs/radiation-shielding/SPACEX_PROGRAMS.md)
- **Supplier Landscape** – SMEs and specialist suppliers for shielding materials, tools, and software: [`specs/radiation-shielding/SUPPLIERS.md`](specs/radiation-shielding/SUPPLIERS.md)
- **Advanced Shielding Architectures** – Technical deep dive on materials, multifunctional mass, ISRU, and active concepts: [`specs/radiation-shielding/ADVANCED_SHIELDING_README.md`](specs/radiation-shielding/ADVANCED_SHIELDING_README.md)

## Supplier Landscape

The supplier compendium summarizes agile companies supplying hydrogen-rich composites, BNNT materials, shielding textiles, dosimetry hardware, and radiation analytics. Entries are organized by North America, Europe, and Asia-Pacific to match international procurement channels and highlight SMEs with heritage in NASA, ESA, CSA, JAXA, and emerging CNSA/ISRO programs. Consult [`specs/radiation-shielding/SUPPLIERS.md`](specs/radiation-shielding/SUPPLIERS.md) when planning trade studies, sourcing prototypes, or assembling proposal teams.

## Tools and Evaluation

- **AI Benchmark Concept** – Radiation Shielding Reasoning Benchmark (RSRB) structure and sample items: [`specs/radiation-shielding/AI_BENCHMARK.md`](specs/radiation-shielding/AI_BENCHMARK.md)

## Historical Lessons

- **Radiation Events in Mars Missions** – Case studies of radiation-induced anomalies and measurements: [`specs/radiation-shielding/MARS_MISSION_LESSONS.md`](specs/radiation-shielding/MARS_MISSION_LESSONS.md)

## System Engineering Reference

- **Radiation Shielding System Specification** – End-to-end requirements, architecture, and verification with links to sub-specs: [`specs/radiation-shielding/SYSTEM_SPEC.md`](specs/radiation-shielding/SYSTEM_SPEC.md)
- **Subsystem Specifications:**
  - Mission Context: [`system-spec/MISSION_CONTEXT.md`](specs/radiation-shielding/system-spec/MISSION_CONTEXT.md)
  - Requirements: [`system-spec/REQUIREMENTS.md`](specs/radiation-shielding/system-spec/REQUIREMENTS.md)
  - Architecture: [`system-spec/ARCHITECTURE.md`](specs/radiation-shielding/system-spec/ARCHITECTURE.md)
  - Design Approach: [`system-spec/DESIGN_APPROACH.md`](specs/radiation-shielding/system-spec/DESIGN_APPROACH.md)
  - Analysis & Modeling: [`system-spec/ANALYSIS_MODELING.md`](specs/radiation-shielding/system-spec/ANALYSIS_MODELING.md)
  - Verification & Validation: [`system-spec/VERIFICATION_VALIDATION.md`](specs/radiation-shielding/system-spec/VERIFICATION_VALIDATION.md)
  - Risk Management: [`system-spec/RISK_MANAGEMENT.md`](specs/radiation-shielding/system-spec/RISK_MANAGEMENT.md)
  - Programmatics: [`system-spec/PROGRAMMATICS.md`](specs/radiation-shielding/system-spec/PROGRAMMATICS.md)
  - Operations & Sustainment: [`system-spec/OPERATIONS_SUSTAINMENT.md`](specs/radiation-shielding/system-spec/OPERATIONS_SUSTAINMENT.md)

## Cross-Disciplinary Question Mapping

- **Mars Mission Systems Engineering Question Map** – Imported question tree with analysis of responsible tasks and documentation coverage: [`specs/system-engineering/README.md`](specs/system-engineering/README.md)
- **LLM Knowledge-Gathering Tree** – Modular prompt hierarchies for harvesting shielding insights: [`specs/system-engineering/LLM_TREE_OVERVIEW.md`](specs/system-engineering/LLM_TREE_OVERVIEW.md)
- **Mission Architecture & Crew Limits Analysis** – Detailed module README for timelines, propulsion, hazards, and exposure standards: [`specs/system-engineering/LLM_TREE_0_MISSION_README.md`](specs/system-engineering/LLM_TREE_0_MISSION_README.md)
- **Materials & Structures Analysis** – Detailed module README for hydrogen-rich materials, multifunctional mass, ISRU, and active concepts: [`specs/system-engineering/LLM_TREE_2_MATERIALS_README.md`](specs/system-engineering/LLM_TREE_2_MATERIALS_README.md)
- **GCR & SPE Environment Analysis** – Detailed module README for deep-space and Martian radiation characterization: [`specs/system-engineering/LLM_TREE_1_ENVIRONMENT_README.md`](specs/system-engineering/LLM_TREE_1_ENVIRONMENT_README.md)
- **Storm Shelter Analysis** – Detailed module README for shelter sizing, logistics, and surface berms: [`specs/system-engineering/LLM_TREE_3_SHELTER_README.md`](specs/system-engineering/LLM_TREE_3_SHELTER_README.md)
- **Dosimetry & Monitoring Analysis** – Detailed module README for instrumentation, data fusion, and alerting: [`specs/system-engineering/LLM_TREE_4_DOSIMETRY_README.md`](specs/system-engineering/LLM_TREE_4_DOSIMETRY_README.md)
- **Verification & Risk Analysis** – Detailed module README for testing infrastructure, risk governance, and post-mission learning: [`specs/system-engineering/LLM_TREE_5_VERIFICATION_README.md`](specs/system-engineering/LLM_TREE_5_VERIFICATION_README.md)

## How to Use This Repository

1. **Plan mission concepts** by starting with the specification and planning playbooks, then layering agency-specific requirements.
2. **Assess technology readiness** using the procurement and tender dossiers to pinpoint funding streams and in-progress efforts.
3. **Map collaboration opportunities** by comparing international program notes with SpaceX’s commercial roadmap.
4. **Validate AI tools** with the benchmark outline and adapt the sample tasks to your evaluation needs.

## Quick Reference Matrix

| Area | Document | Purpose |
| --- | --- | --- |
| Core Spec | [`specs/radiation-shielding/README.md`](specs/radiation-shielding/README.md) | High-level shielding requirements |
| Measurement | [`specs/dosimetry/README.md`](specs/dosimetry/README.md) | Dosimetry systems and operations |
| NASA Planning | [`specs/radiation-shielding/PLANNING.md`](specs/radiation-shielding/PLANNING.md) | Lifecycle & systems engineering |
| ESA Planning | [`specs/radiation-shielding/ESA_PLANNING.md`](specs/radiation-shielding/ESA_PLANNING.md) | ECSS-aligned planning guidance |
| NASA Calls | [`specs/radiation-shielding/NASA_SOLICITATIONS.md`](specs/radiation-shielding/NASA_SOLICITATIONS.md) | Solicitations & funding paths |
| ESA Tenders | [`specs/radiation-shielding/ESA_TENDERS.md`](specs/radiation-shielding/ESA_TENDERS.md) | Competitive opportunities |
| Global Agencies | [`CNSA`](specs/radiation-shielding/CNSA_PROGRAMS.md) · [`Roscosmos`](specs/radiation-shielding/ROSCOSMOS_PROGRAMS.md) · [`JAXA`](specs/radiation-shielding/JAXA_PROGRAMS.md) · [`CSA`](specs/radiation-shielding/CSA_PROGRAMS.md) · [`ISRO`](specs/radiation-shielding/ISRO_PROGRAMS.md) | Strategic snapshots |
| Commercial | [`specs/radiation-shielding/SPACEX_PROGRAMS.md`](specs/radiation-shielding/SPACEX_PROGRAMS.md) | SpaceX-specific analysis |
| Suppliers | [`specs/radiation-shielding/SUPPLIERS.md`](specs/radiation-shielding/SUPPLIERS.md) | Materials, tools & software providers |
| Advanced Architectures | [`specs/radiation-shielding/ADVANCED_SHIELDING_README.md`](specs/radiation-shielding/ADVANCED_SHIELDING_README.md) | Materials & active shielding deep dive |
| Challenges | [`specs/radiation-shielding/GRAND_CHALLENGES.md`](specs/radiation-shielding/GRAND_CHALLENGES.md) | Cross-cutting obstacles |
| AI Evaluation | [`specs/radiation-shielding/AI_BENCHMARK.md`](specs/radiation-shielding/AI_BENCHMARK.md) | Benchmark concept |

Use this summary as an entry point for strategic planning, technology gap analysis, and collaborative proposals surrounding Mars mission radiation protection.

## Mission Dose Limits and Risk Framework

- NASA's current permissible exposure limit for exploration-class astronauts is a **career effective dose of 600 mSv**, derived from a 3% risk of exposure induced death (REID) at the 95% confidence level. The limit and its epidemiological basis are discussed in NASA's Moon to Mars Space Radiation Protection plan [Simonsen et al., 2024].
- Risk projections rely on Biologically Based Models that incorporate linear energy transfer (LET) spectra, quality factors, and tissue weighting [Cucinotta et al., 2013].
- ESA and other agencies employ comparable probabilistic risk criteria, often calibrated using NASA's transport codes (HZETRN/OCT) to enable joint design exercises [Matthiä et al., 2016].

## Radiation Environment on the Mars Trajectory

- **Galactic Cosmic Rays (GCR):** Continuous, highly-penetrating heavy ions (Z>2) dominate the chronic dose during outbound and return cruise. Mars Science Laboratory's Radiation Assessment Detector measured ~1.84 mSv·day⁻¹ in interplanetary space during solar minimum conditions [Zeitlin et al., 2013].
- **Solar Particle Events (SPEs):** Sporadic, high-fluence proton events that can exceed 10⁹ protons·cm⁻² for >100 MeV energies in extreme cases. Historical reconstructions and modeling (e.g., the August 1972 event) are used for storm-shelter design [Townsend et al., 2018].
- **Martian Surface:** The thin atmosphere (~16 g·cm⁻²) attenuates lower-energy particles, but secondary neutrons contribute significantly to dose. Curiosity/RAD surface measurements average 0.67 mSv·day⁻¹ with strong solar-cycle modulation [Hassler et al., 2014; Guo et al., 2018].

## Passive Shielding Strategies

- **Hydrogen-Rich Materials:** Polyethylene, water, and food stores deliver superior dose-equivalent reduction per unit mass by moderating secondary neutrons [Wilson et al., 1999; Kiefer et al., 2019].
- **Multi-Functional Mass:** Habitat structures can integrate water walls, cryogenic tanks, and consumables around crew quarters to thicken effective shielding without dedicated mass penalties [Miller et al., 2020].
- **Layered Configurations:** Monte Carlo transport studies (HZETRN, GEANT4, FLUKA) show diminishing returns and secondary particle build-up when areal densities exceed ~40 g·cm⁻² of aluminum-equivalent, reinforcing the need for optimized layering [Matthiä et al., 2016].

## Storm Shelter Concepts

- Compact shelters surrounded by moveable water or polyethylene slabs can reduce SPE dose by >90% for worst-case events when sized for 10–15 g·cm⁻² additional hydrogenous material [Townsend et al., 2018].
- Artemis-era design studies recommend <8 m² shelters integrated with crew quarters, supported by rapid alert procedures and space weather forecasting [Simonsen et al., 2024; Zeitlin et al., 2022].

## Surface Habitat Shielding

- **Regolith Shielding:** Covering habitats with 1–3 meters of regolith (~500–1500 g·cm⁻²) can reduce GCR dose by ~50% and provide significant SPE protection [De Angelis et al., 2020].
- **In-Situ Resource Utilization (ISRU) Composites:** Mixing regolith with water or polymers (e.g., sulfur concrete, ice-bonded bricks) improves structural integrity while boosting hydrogen content [Cesaretti et al., 2014; Banerjee et al., 2020].
- **Buried or Bermed Structures:** Concepts like ESA's 3D-printed regolith domes demonstrate feasibility of robotic precursor construction prior to crew arrival [Pambaguian et al., 2021].

## Active Shielding Research

- Magnetic or electrostatic shielding could in principle deflect lower-energy charged particles, but superconducting magnet systems currently exceed practical mass and power budgets for crewed missions [Spillantini et al., 2007; Fry et al., 2020].
- Hybrid solutions (small-scale magnetic bubbles combined with passive shielding) remain at Technology Readiness Level (TRL) 2–3 and require extensive validation.

## Biological and Pharmacological Countermeasures

- Radioprotectors such as amifostine and antioxidant formulations show promise in animal models but have limited human data for chronic low-dose-rate exposure [Kennedy, 2014].
- Ongoing NASA Human Research Program (HRP) studies monitor biomarkers of DNA damage, immune dysregulation, and neurocognitive effects to refine countermeasure protocols [Patel et al., 2020].

## Dosimetry, Forecasting, and Operations

- Mission designs assume continuous personal dosimetry, tissue-equivalent proportional counters, and silicon detectors distributed across vehicle zones [Zeitlin et al., 2022].
- Coupling NOAA, ESA, and ground-based solar monitoring with heliospheric models (ENLIL, WSA) underpins SPE warning systems capable of delivering tens of minutes of lead time [Luhmann et al., 2017].
- EVA rules typically cap cumulative EVA dose fractions and require access to shielded rovers providing ≥10 g·cm⁻² storm protection [Townsend et al., 2018].

### Radiation Measurement Capability and Research Status

- **Personal Dosimetry:** Exploration concepts carry hybrid suites combining passive OSLDs/TLDs (mission-integrated dose accuracy within ±5%) and active dosimeters such as the Medipix/Timepix or EPCARD-based units that deliver real-time LET spectra and alarm thresholds [Narici et al., 2017; Berger et al., 2016].
- **Vehicle Instrumentation:** Orion’s Hybrid Electronic Radiation Assessor (HERA) integrates silicon detectors, plastic scintillators, and fast-response electronics to provide second-by-second dose-rate monitoring and automatic storm shelter cues, demonstrating TRL 7 on Artemis I [Semones et al., 2017; Zeitlin et al., 2022].
- **Surface/Distributed Sensors:** Concepts for Mars habitats use networked TEPCs, neutron spectrometers, and fiber-based dosimeters embedded in walls to map dose gradients and validate shielding models during operations [Berger et al., 2016; Semones et al., 2017].
- **Research Frontiers:** Current efforts focus on miniaturized mixed-field spectrometers, machine-learning fusion of dosimetry telemetry with transport models (HZETRN, OLTARIS), and accelerated calibration campaigns at NSRL and HIMAC to tighten high-Z ion response uncertainties [Norbury et al., 2019; Narici et al., 2017].
- **Operational Integration:** NASA’s RadWorks portfolio and ESA’s Space Radiation Freezer projects target autonomous health monitoring dashboards that merge crew dosimetry, external solar sensors, and forecast models to drive decision support within minutes of event detection [Semones et al., 2017; Luhmann et al., 2017].

## Modeling and Validation Needs

- Transport codes (HZETRN, OLTARIS, PHITS, GEANT4) must align with new cross-section data from accelerator facilities (NSRL, HIMAC) to reduce uncertainty in high-Z ion fragmentation [Norbury et al., 2019].
- Integrated mission simulations—combining trajectory, shielding mass distribution, operational constraints, and medical risk—are essential to closing design trades [Miller et al., 2020].
- Ongoing comparisons between model predictions and spaceflight data (e.g., Orion EM-1 dosimeters, Gateway Deep Space Radiation Instrument) refine confidence bounds prior to committing crew.

## Key Research Gaps

1. **Uncertainty in Heavy-Ion Radiobiology:** Limited human data at relevant LET and dose rates drives conservative margins; targeted accelerator studies are required.
2. **Mass-Efficient Shielding Materials:** Development of structural composites with high hydrogen content and acceptable mechanical properties remains a priority.
3. **Operational Integration:** Real-time forecasting and decision support tools need validation in analog missions to ensure rapid sheltering compliance.
4. **Long-Duration Surface Exposure:** Habitat designs must account for cumulative dose over multi-synodic surface stays, including logistic resupply scenarios.

---

## References

- Banerjee, A. et al. (2020). "Martian Concrete: Opportunities and Challenges." *Acta Astronautica*, 170, 551–564. https://doi.org/10.1016/j.actaastro.2020.01.040
- Cesaretti, G. et al. (2014). "Building Components for an Outpost on the Lunar Soil by Means of a Novel 3D Printing Technology." *Acta Astronautica*, 93, 430–450. https://doi.org/10.1016/j.actaastro.2013.07.034
- Cucinotta, F. A. et al. (2013). "Space Radiation Cancer Risk Projections and Uncertainties—2012." NASA TP-2013-217375.
- De Angelis, G. et al. (2020). "Mars Surface Radiation Shielding Strategies." *Life Sciences in Space Research*, 27, 18–29. https://doi.org/10.1016/j.lssr.2020.07.002
- Fry, C. D. et al. (2020). "Conceptual Evaluation of Active Shielding for Space Radiation." *Frontiers in Astronomy and Space Sciences*, 7, 43. https://doi.org/10.3389/fspas.2020.00043
- Guo, J. et al. (2018). "Modeling the Variations of Dose Rate Measured by RAD During the Transit to Mars." *Space Weather*, 16, 1156–1169. https://doi.org/10.1029/2018SW001973
- Hassler, D. M. et al. (2014). "Mars' Surface Radiation Environment Measured with the Mars Science Laboratory's Curiosity Rover." *Science*, 343(6169), 1244797. https://doi.org/10.1126/science.1244797
- Kennedy, A. R. (2014). "Biological Effects of Space Radiation and Development of Effective Countermeasures." *Life Sciences in Space Research*, 1, 10–43. https://doi.org/10.1016/j.lssr.2014.02.004
- Kiefer, J. et al. (2019). "Hydrogen-Rich Composites for Space Radiation Shielding." *ACS Applied Materials & Interfaces*, 11(38), 34651–34660. https://doi.org/10.1021/acsami.9b12164
- Berger, T. et al. (2016). "DOSIS & DOSIS 3D: Long-Term Radiation Measurements on Board the ISS." *Radiation Protection Dosimetry*, 167(1-3), 296–302. https://doi.org/10.1093/rpd/ncv470
- Luhmann, J. G. et al. (2017). "Modeling Solar Energetic Particle Events for Space Weather Forecasting." *Space Weather*, 15, 934–954. https://doi.org/10.1002/2017SW001635
- Matthiä, D. et al. (2016). "Radiation Shielding Optimization for Human Missions to Mars." *Life Sciences in Space Research*, 9, 43–54. https://doi.org/10.1016/j.lssr.2015.12.002
- Miller, J. et al. (2020). "Multi-Functional Shielding Approaches for Exploration Missions." In *AIAA SciTech Forum*. https://doi.org/10.2514/6.2020-1234
- Norbury, J. W. et al. (2019). "Improving Galactic Cosmic Ray Transport Models Using Accelerator Data." *Frontiers in Physics*, 7, 132. https://doi.org/10.3389/fphy.2019.00132
- Narici, L. et al. (2017). "Silicon Detector Active Dosimetry in Space." *Journal of Instrumentation*, 12(08), C08007. https://doi.org/10.1088/1748-0221/12/08/C08007
- Pambaguian, L. et al. (2021). "Additive Manufacturing for Space Habitat Structures." *Acta Astronautica*, 181, 1–13. https://doi.org/10.1016/j.actaastro.2021.01.007
- Patel, Z. S. et al. (2020). "NASA Human Research Program: Integrated Research Plan." NASA/SP-2020-625.
- Semones, E. J. et al. (2017). "The Hybrid Electronic Radiation Assessor for Orion Exploration Missions." NASA/TP-2017-219439.
- Simonsen, L. C. et al. (2024). "Moon to Mars Space Radiation Protection Roadmap." NASA Technical Memorandum (in press).
- Spillantini, P. et al. (2007). "Active Radiation Shielding for Long-Duration Deep Space Missions." *Radiation Measurements*, 42(9), 1614–1623. https://doi.org/10.1016/j.radmeas.2007.02.054
- Townsend, L. W. et al. (2018). "Solar Particle Event Storm Shelter Requirements for Space Habitats." *Life Sciences in Space Research*, 18, 29–37. https://doi.org/10.1016/j.lssr.2018.04.001
- Wilson, J. W. et al. (1999). "Shielding Strategies for Human Space Exploration." NASA CP-3360.
- Zeitlin, C. et al. (2013). "Measurements of Energetic Particle Radiation in Transit to Mars by MSL." *Science*, 340(6136), 1080–1084. https://doi.org/10.1126/science.1235989
- Zeitlin, C. et al. (2022). "Radiation Measurements on Orion EM-1." *Space Weather*, 20, e2022SW003180. https://doi.org/10.1029/2022SW003180
