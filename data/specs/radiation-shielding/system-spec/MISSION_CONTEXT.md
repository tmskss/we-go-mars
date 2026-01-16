# Mission Context Specification

## 1. Mission Architecture Assumptions

- **Mission Phases:** Earth launch → LEO aggregation and refueling → outbound transit → Mars orbital insertion → surface entry/landing → surface operations (500 sols nominal) → ascent → return transit → Earth re-entry.
- **Vehicles:**
  - *Transit Habitat / Starship-Class Vehicle:* Crew quarters, life support, storm shelter, logistics.
  - *Surface Habitat:* Prefabricated modules augmented by regolith berms and ISRU infrastructure.
  - *Logistics Assets:* Pressurized rovers, unpressurized rovers, power plants (nuclear/solar), cargo landers.
- **Crew Composition:** 4–6 crew, mixed specialties (pilot, ECLSS engineer, geologist, medical officer, systems engineer).
- **Mission Duration:** 900–1,100 Earth days, aligning with Hohmann transfer synod.

## 2. Environmental Boundaries

- **Interplanetary Space:** Dominant GCR background with flux varying inversely with solar activity; include design reference missions for solar maximum/minimum.
- **Solar Particle Events:** Use NASA SEPEM or equivalent spectra for worst-case events; design for August 1972 analog with safety margin.
- **Martian Surface:** Atmospheric attenuation ~16 g·cm⁻² at datum; site selection near mid-latitude to balance ice access and radiation environment.
- **Secondary Radiation:** Consider neutron albedo from regolith shielding and structural materials.

## 3. Applicable Standards

- NASA: NASA-STD-3001 Vol. 1/2 (Crew Health and Performance), NPR 8705.6 (CREW Smart), NPR 7120.5 (Program/Project Management), NPR 7123.1 (Systems Engineering).
- ESA: ECSS-E-ST-10 (Systems engineering), ECSS-Q-ST-60 (Electrical, electronic, and electromechanical components), ECSS-Q-ST-40 (Safety).
- Other: ISO 15390 (Space environment natural radiation), ANSI/HPS N13.41 (Personnel dosimetry performance).

## 4. Operational Constraints

- **Launch Windows:** Synodic windows every 26 months; plan for mission readiness ahead of window.
- **Propellant Production:** ISRU plant must achieve methane/oxygen production rates to enable return flights; integration with shielding design when tanks double as mass.
- **Communications Latency:** 4–22 minutes one-way; crew autonomy requirements drive on-board decision making for radiation alerts.
- **Power Availability:** Surface power mix (fission surface power units + solar arrays) must support shielding excavation and water processing.

## 5. Stakeholders and Interfaces

- **Mission Directorate:** Human Exploration and Operations (NASA) / HRE (ESA).
- **International Partners:** Agreements defining shared standards and data sharing for radiation monitoring.
- **Commercial Partners:** Starship operators, surface logistics providers; ensure adherence to shielding requirements via contract clauses.
- **Science Community:** Radiation instrument teams (RAD, HERA) supplying data for model validation.

## 6. Mission Success Criteria (Radiation Perspective)

1. Crew cumulative dose remains within agency limits for entire mission.
2. No single radiation event jeopardizes crew survival or critical systems.
3. Dosimetry and environmental data returned to improve future mission planning.
4. Surface infrastructure remains habitable with acceptable operational downtime.

## 7. Assumptions and Open Issues

- **Assumptions:** Availability of heavy-lift launch vehicle capability, successful in-orbit refueling, ISRU infrastructure deployment prior to crew arrival.
- **Open Issues:** Final crew risk tolerance (REID threshold), regulatory approvals for nuclear power units, integration with commercial mission timelines.
