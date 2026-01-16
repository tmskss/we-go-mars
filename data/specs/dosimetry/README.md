# Dosimetry Architecture for Crewed Mars Missions

This document summarizes the state of practice and research frontiers in measuring radiation absorbed by astronauts during interplanetary missions. It focuses on instrumentation, deployment strategies, calibration, and operational integration for Mars transit and surface phases.

## Measurement Objectives

1. **Crew Safety Compliance:** Demonstrate adherence to mission and career dose limits (e.g., NASA 600 mSv career effective dose) by tracking cumulative equivalent dose per astronaut.
2. **Event Detection:** Provide rapid (<60 s) alerts for Solar Particle Events (SPEs) that exceed predefined dose-rate thresholds to enable storm-shelter procedures.
3. **Environment Characterization:** Capture Linear Energy Transfer (LET) spectra, particle composition, and angular distribution to validate transport models and improve shielding designs.
4. **Biological Dose Correlation:** Supply time-resolved dosimetry synchronized with biomedical monitoring (blood biomarkers, cognitive assessments) for risk modeling.

## Instrumentation Layers

### Passive Dosimetry

- **Thermoluminescent Dosimeters (TLDs):** Fluoride-based crystals (e.g., LiF:Mg,Ti) placed on personal badges and in vehicle zones; integrated dose accuracy <5% after laboratory readout [Berger et al., 2016].
- **Optically Stimulated Luminescence Dosimeters (OSLDs):** Aluminum oxide (Al₂O₃:C) dosimeters offering re-read capability and better fading characteristics; used by NASA's Personal Active Dosimeter (PAD) kits.
- **Nuclear Track Detectors:** CR-39 plastic for high-LET heavy ions; analyzed post-flight to derive microdosimetric spectra and support cancer risk projections [Cucinotta et al., 2013].

### Active Personal Dosimeters

- **Timepix/Medipix Arrays:** Hybrid pixel detectors providing per-particle energy deposition and track topology, worn on body or placed in phantom mannequins (e.g., ESA's AREB, AstroRad) [Narici et al., 2017].
- **Electronic Personal Dosimeters (EPDs):** Compact silicon diode stacks (e.g., Teledyne Microdosimeter) giving real-time dose equivalent with programmable alarms; targeted response 0.1 µSv·h⁻¹ to >10 mSv·h⁻¹.

### Fixed Vehicle Sensors

- **Tissue-Equivalent Proportional Counters (TEPCs):** Gas-filled detectors simulating a 1–10 µm tissue site for microdosimetric spectra and quality factor estimation; central to ISS DOSIS 3D and NASA's Orion suites [Semones et al., 2017].
- **Hybrid Electronic Radiation Assessor (HERA):** Orion exploration module payload combining silicon detectors, plastic scintillators, and fast electronics to deliver dose rates, LET, and automated storm shelter cues with <15 s latency [Semones et al., 2017].
- **Neutron Spectrometers:** Bonner sphere systems and scintillating fiber detectors monitor secondary neutron flux generated in shielding; essential for habitats with regolith or water shielding where neutron albedo dominates [Zeitlin et al., 2022].

### Distributed and Surface Networks

- **Embedded Fiber Dosimeters:** Radiation-sensitive optical fibers woven into habitat structures for spatial dose mapping with minimal mass penalty.
- **Surface Reference Stations:** Mars habitat concepts deploy tripod-mounted or rover-integrated dosimetry clusters (TEPC + neutron + silicon) to compare indoor/outdoor differentials and adjust EVA constraints [De Angelis et al., 2020].

## Platform-Specific Deployment

- **Transit Habitat:** Layer sensors near crew quarters, storm shelter, propulsion tanks, and docking adapters to capture mass-distribution effects. Personal dosimeters are worn continuously; fixed monitors feed telemetry to flight data systems for predictive analytics (HZETRN/OCT).
- **Storm Shelter:** HERA or equivalent monitors provide localized readings; additional passive tiles verify accumulated dose for post-event analysis.
- **Surface Habitat:** A 3D grid of passive chips and active sensors monitors wall penetration depth and regolith shielding performance. Underground or bermed structures incorporate borehole detectors to capture neutron backscatter.
- **EVA Suit/Rover:** Suits include lightweight active dosimeters with haptic/visual alarms coupled to rover-based detectors providing safe-haven dose-rate readouts. Rover cabins integrate 10–15 g·cm⁻² hydrogenous shielding and active monitors for near-real-time exposure logging [Townsend et al., 2018].

## Calibration and Cross-Validation

1. **Beamline Campaigns:** Detectors are exposed at accelerator facilities (NASA NSRL, JAXA HIMAC, GSI SIS-18) across proton and heavy-ion beams to generate response matrices for LET up to ~1,500 keV·µm⁻¹ [Norbury et al., 2019].
2. **Phantom Experiments:** Anthropomorphic phantoms (e.g., Matroshka, Phantom Torso) house dosimeters at organ-equivalent locations to calibrate conversion from skin to organ dose.
3. **Model Coupling:** Flight telemetry is assimilated into transport codes (HZETRN, OLTARIS, PHITS, GEANT4) to adjust boundary conditions, verify shielding performance, and update mission dose projections.
4. **Uncertainty Management:** Bayesian frameworks incorporate detector calibration errors, statistical counting uncertainty, and biological weighting factor variance to produce operational confidence intervals.

## Operations and Data Handling

- **Telemetry Integration:** Active dosimeter data are streamed via vehicle avionics to mission control, where automated pipelines compute absorbed dose, dose equivalent, and dose rate for each crew member.
- **Alert Protocols:** Thresholds (e.g., 10 mSv cumulative within SPE, >0.5 mSv·h⁻¹ rate) trigger automatic notifications. HERA can directly command Orion's caution and warning system for rapid shelter-in-place.
- **Mission Analytics:** Daily summary reports merge dosimetry with heliophysics data (NOAA, ESA space-weather feeds) to adjust EVA schedules and shielding configuration.
- **Post-Mission Analysis:** Retrieved passive dosimeters undergo high-precision readout; combined datasets improve epidemiological models and update permissible exposure limits.

## Research Frontiers

1. **Mixed-Field Spectrometers:** Development of compact instruments capable of simultaneous charged particle and neutron LET spectroscopy (e.g., silicon carbide diodes, microcalorimeters) to replace multi-instrument stacks.
2. **Machine-Learning Fusion:** Real-time assimilation of multi-detector data with heliospheric forecasts to predict dose evolution hours ahead, enabling proactive operations.
3. **Radiation Digital Twins:** Coupled simulation environments linking structural CAD, shielding mass, and dosimetry telemetry for visualization and risk management during missions.
4. **Biologically Weighted Sensors:** Advanced materials and microfluidic bioassays that directly measure biological effectiveness rather than relying on physical dose proxies.
5. **Miniaturized EVA Dosimetry:** Ultra-low-mass wearable arrays with directionality to identify anisotropic fluxes during surface traverses.

## Key Missions and Demonstrations

- **ISS DOSIS & DOSIS 3D:** Long-term passive/active dosimetry delivering 10+ years of spatial dose maps and LET spectra inside the ISS [Berger et al., 2016].
- **Matroshka/Phantom Torso:** Human phantom with embedded dosimeters flown on Shuttle, ISS, and Artemis I to quantify organ doses [Zeitlin et al., 2022].
- **Orion EM-1 / Artemis I:** Verified HERA performance in deep space, recorded ~1.8 mSv during 25.5-day mission, demonstrating operational storm-shelter warnings [Zeitlin et al., 2022].
- **MSL RAD:** Provided cruise and Mars surface dose baseline (~1.84 mSv·day⁻¹ cruise, 0.67 mSv·day⁻¹ surface) used to calibrate future mission dosimetry expectations [Zeitlin et al., 2013].

## References

- Berger, T. et al. (2016). "DOSIS & DOSIS 3D: Long-Term Radiation Measurements On Board the ISS." *Radiation Protection Dosimetry*, 167(1-3), 296–302. https://doi.org/10.1093/rpd/ncv470
- Cucinotta, F. A. et al. (2013). "Space Radiation Cancer Risk Projections and Uncertainties—2012." NASA TP-2013-217375.
- De Angelis, G. et al. (2020). "Mars Surface Radiation Shielding Strategies." *Life Sciences in Space Research*, 27, 18–29. https://doi.org/10.1016/j.lssr.2020.07.002
- Narici, L. et al. (2017). "Silicon Detector Active Dosimetry in Space." *Journal of Instrumentation*, 12(08), C08007. https://doi.org/10.1088/1748-0221/12/08/C08007
- Norbury, J. W. et al. (2019). "Improving Galactic Cosmic Ray Transport Models Using Accelerator Data." *Frontiers in Physics*, 7, 132. https://doi.org/10.3389/fphy.2019.00132
- Semones, E. J. et al. (2017). "The Hybrid Electronic Radiation Assessor for Orion Exploration Missions." NASA/TP-2017-219439.
- Townsend, L. W. et al. (2018). "Solar Particle Event Storm Shelter Requirements for Space Habitats." *Life Sciences in Space Research*, 18, 29–37. https://doi.org/10.1016/j.lssr.2018.04.001
- Zeitlin, C. et al. (2013). "Measurements of Energetic Particle Radiation in Transit to Mars by MSL." *Science*, 340(6136), 1080–1084. https://doi.org/10.1126/science.1235989
- Zeitlin, C. et al. (2022). "Radiation Measurements on Orion EM-1." *Space Weather*, 20, e2022SW003180. https://doi.org/10.1029/2022SW003180
