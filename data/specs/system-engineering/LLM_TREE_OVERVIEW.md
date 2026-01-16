# LLM Knowledge-Gathering Tree Overview

This overview maps the modular prompt trees that support automated or guided research into Mars mission radiation shielding. Use it as the entry point when orchestrating large-model explorations or fine-grained fact gathering.

## Modules
- **0. Mission Context & Exposure Limits**: [`LLM_TREE_0_MISSION.md`](LLM_TREE_0_MISSION.md) · Analysis README: [`LLM_TREE_0_MISSION_README.md`](LLM_TREE_0_MISSION_README.md) · Insights: [`LLM_TREE_INSIGHTS.md#0-mission-context--exposure-limits`](LLM_TREE_INSIGHTS.md#0-mission-context--exposure-limits)
- **1. Radiation Environment Characterization**: [`LLM_TREE_1_ENVIRONMENT.md`](LLM_TREE_1_ENVIRONMENT.md) · Analysis README: [`LLM_TREE_1_ENVIRONMENT_README.md`](LLM_TREE_1_ENVIRONMENT_README.md) · Insights: [`LLM_TREE_INSIGHTS.md#1-radiation-environment-characterization`](LLM_TREE_INSIGHTS.md#1-radiation-environment-characterization)
- **2. Shielding Materials & Structures**: [`LLM_TREE_2_MATERIALS.md`](LLM_TREE_2_MATERIALS.md) · Analysis README: [`LLM_TREE_2_MATERIALS_README.md`](LLM_TREE_2_MATERIALS_README.md) · Insights: [`LLM_TREE_INSIGHTS.md#2-shielding-materials--structures`](LLM_TREE_INSIGHTS.md#2-shielding-materials--structures)
- **3. Storm Shelter & Habitat Design**: [`LLM_TREE_3_SHELTER.md`](LLM_TREE_3_SHELTER.md) · Analysis README: [`LLM_TREE_3_SHELTER_README.md`](LLM_TREE_3_SHELTER_README.md) · Insights: [`LLM_TREE_INSIGHTS.md#3-storm-shelter--habitat-design`](LLM_TREE_INSIGHTS.md#3-storm-shelter--habitat-design)
- **4. Dosimetry, Monitoring & Forecasting**: [`LLM_TREE_4_DOSIMETRY.md`](LLM_TREE_4_DOSIMETRY.md) · Analysis README: [`LLM_TREE_4_DOSIMETRY_README.md`](LLM_TREE_4_DOSIMETRY_README.md) · Insights: [`LLM_TREE_INSIGHTS.md#4-dosimetry-monitoring--forecasting`](LLM_TREE_INSIGHTS.md#4-dosimetry-monitoring--forecasting)
- **5. Verification, Validation & Risk**: [`LLM_TREE_5_VERIFICATION.md`](LLM_TREE_5_VERIFICATION.md) · Analysis README: [`LLM_TREE_5_VERIFICATION_README.md`](LLM_TREE_5_VERIFICATION_README.md) · Insights: [`LLM_TREE_INSIGHTS.md#5-verification-validation--risk`](LLM_TREE_INSIGHTS.md#5-verification-validation--risk)
- **6. Suppliers, Software & Policy**: [`LLM_TREE_6_SUPPLIERS.md`](LLM_TREE_6_SUPPLIERS.md) · Insights: [`LLM_TREE_INSIGHTS.md#6-suppliers-software--policy`](LLM_TREE_INSIGHTS.md#6-suppliers-software--policy)

## Tagging Scheme
- **Priority (Px)**: P0 = foundational; P1 = high value; P2 = medium; P3 = supplementary.
- **Model Size (Mx)**: ML = large model (≥30B parameters) recommended; MM = mid-size (10–30B); MS = small (≤10B) viable.
- Unless otherwise noted, leaf nodes use `[P1|MS]`—designed for small/edge models to retrieve specific facts.
- Roots of sections 0–4 are `[P0|ML]` due to mission-critical reasoning; sections 5–6 default to `[P1|MM]` and `[P2|MS]` respectively.

## Usage Notes
1. **Start at the overview** to choose the relevant module(s) for your investigation.
2. **Run large models** on top-level prompts (Tag `[P0|ML]` or `[P1|MM]`) to gather context.
3. **Assign leaf prompts** to compact models or scripted agents for detail harvesting.
4. **Feed outputs** back into repository specs (e.g., `system-spec/*`, `SUPPLIERS.md`) as knowledge updates.
