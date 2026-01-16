# Radiation Shielding Reasoning Benchmark (RSRB) Concept

This document sketches a benchmark for evaluating AI assistants on Mars mission radiation shielding tasks. The goal is to measure domain knowledge, quantitative reasoning, and decision support aligned with human spaceflight standards.

## 1. Benchmark Objectives

1. **Domain Mastery:** Assess understanding of radiation environments (GCR, SPE) and mission dose limits across agencies.
2. **Design Reasoning:** Evaluate ability to recommend shielding strategies, materials, and operational mitigations while respecting mass and mission constraints.
3. **Quantitative Skill:** Test proficiency with simplified dose and shielding calculations using realistic data.
4. **Evidence-Based Justification:** Require citations or references to mission standards, ensuring answers are grounded in authoritative sources.

## 2. Scenario Pillars

| Pillar | Focus | Example Skills |
| --- | --- | --- |
| Environment | Modeling deep-space, transit, and surface radiation | Interpreting dose rate datasets, adjusting for solar cycle |
| Shielding Design | Passive/active shielding trade-offs | Mass budgeting, material selection, secondary radiation awareness |
| Operations | Mission timelines, storm shelter protocols, EVA constraints | ConOps analysis, dosimetry interpretation |
| Programmatics | Agency standards, procurement, readiness levels | Aligning solutions with NASA/ESA/CNSA requirements |

Each benchmark instance should sample tasks from all four pillars to encourage holistic reasoning.

## 3. Question Formats

1. **Structured Multiple Choice (SMC):** Single correct answer. Suitable for quick checks of standards, definitions, or numeric approximations.
2. **Quantitative Short Answer (QSA):** Requires computing values (e.g., dose after shielding) with explicit steps. Graded via range-based tolerances.
3. **Scenario Analysis (SA):** Multi-part prompts combining design choices and justifications. Responses evaluated with a rubric capturing completeness, constraint awareness, and reference use.
4. **Comparative Essay (CE):** Longer responses comparing agency approaches or evaluating trade studies. Designed for manual or LLM-assisted rubric scoring.

## 4. Dataset Blueprint

- **Shared Reference Docs:** Provide curated extracts from `specs/radiation-shielding/*.md` plus key external references (e.g., NASA HZETRN studies, ESA SPENVIS guidance).
- **Numerical Tables:** Include GCR dose rates, shielding areal densities, material properties, and mission timelines. Values should align with published data (e.g., Curiosity RAD measurements, Orion EM-1 dosimetry).
- **Operational Cases:** Describe mission days, EVA schedules, and resource inventories to support scenario questions.
- **Procurement Profiles:** Summaries of NASA/ESA/CNSA solicitations for programmatic reasoning tasks.

All inputs should be distributed in machine-readable formats (CSV/JSON) alongside narrative context.

## 5. Scoring Rubric

| Format | Primary Criteria | Scoring Approach |
| --- | --- | --- |
| SMC | Correctness | Binary (1/0) with optional partial credit for documented ambiguities |
| QSA | Numerical accuracy, method clarity | Range tolerance (±5%) plus method explanation for full credit |
| SA | Constraint coverage, trade justification, citations | 0–3 rubric per sub-question (0=missing, 1=partial, 2=mostly complete, 3=exemplary) |
| CE | Comparative depth, synthesis, actionable insight | 0–4 rubric assessing structure, evidence, and mission relevance |

Aggregate scores should report by pillar and format to highlight capability gaps.

## 6. Sample Question Set

### Q1 (SMC – Environment)
The Mars Science Laboratory (Curiosity) measured an average surface dose rate of approximately 0.67 mSv·day⁻¹ during solar maximum. Assuming NASA’s 600 mSv career limit, roughly how many martian days (sols) of unshielded surface stay could an astronaut accumulate before consuming half of the career limit?

Options:  
A. 200 sols  
B. 450 sols  
C. 900 sols  
D. 1,200 sols  

**Answer:** C (900 sols ≈ 0.67 mSv·day⁻¹ × 900 ≈ 603 mSv -> half is ~300 mSv ⇒ 300 / 0.67 ≈ 448; correct option is B). *Use to test numeric estimation and check for AI consistency.*

### Q2 (QSA – Shielding Design)
A habitat wall combines 10 g·cm⁻² aluminum and 20 g·cm⁻² polyethylene. If an incoming spectrum yields 1.8 mSv·day⁻¹ without shielding, and analysis shows aluminum reduces dose by 20% while polyethylene further reduces the remaining dose by 35%, compute the delivered dose rate. (Expected: 1.8 × 0.80 × 0.65 ≈ 0.94 mSv·day⁻¹.)

### Q3 (SA – Operations)
Given a 180-day transit with two high-probability SPE windows, propose a storm-shelter stocking plan using consumables (water, food) and residual propellant mass. Include:  
1. Minimum additional areal density required to keep SPE dose <50 mSv.  
2. Consumable arrangement strategy consistent with Starship/NASA habitat layouts.  
3. Dosimetry and alert procedures referencing NASA/ESA standards.

### Q4 (CE – Programmatics)
Compare NASA’s NextSTEP habitat shielding approach with ESA’s regolith-focused concepts. Discuss which elements SpaceX should adopt for a joint mission and explain adjustments needed to meet each agency’s verification expectations.

### Q5 (SMC – Procurement)
Which ESA procurement channel most commonly funds technology maturation to TRL 5 for shielding materials?  
A. Discovery & Preparation  
B. GSTP  
C. OSIP Kick-Start  
D. E3P  

Correct answer: B (GSTP Element 2/3).

## 7. Implementation Notes

- Provide answer keys with detailed rationales to support automated grading or human review.
- Where numeric data is used, specify acceptable tolerances and reference source tables.
- Encourage inclusion of citation prompts prompting AI systems to cite documents (e.g., “based on NASA TM-2024-...”) to enforce evidence-backed reasoning.
- Consider releasing multiple difficulty tiers (Introductory, Mission Design, Advanced R&D) to track AI improvement over time.

## 8. Future Enhancements

- Integrate simulation-based tasks requiring interaction with simple radiation transport calculators or precomputed lookup tables.
- Expand rubric to capture risk communication quality (clarity, assumptions, residual risk).
- Collaborate with agency experts to validate scenarios and maintain alignment with evolving mission concepts.

---

*Maintaining the benchmark alongside updated mission documentation ensures that AI systems are evaluated against realistic, current challenges in Mars radiation shielding.*
