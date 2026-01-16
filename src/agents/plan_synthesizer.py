"""
Iterative Plan Synthesizer Agent.

This agent generates implementation plans through a two-iteration process:
1. First iteration: Analyze available solutions and identify gaps
2. Second iteration: Fill gaps using KB queries and refine the plan

Owner: [ASSIGN TEAMMATE]
"""

import json
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.agents.base import BaseAgent
from src.agents.retriever import RetrieverAgent, RetrieverAgentInput
from src.models.hypothesis import Hypothesis
from src.models.requirement import RequirementGraph, Requirement
from src.models.solution import Solution
from src.models.research_plan import (
    PreliminaryPlan,
    PreliminaryPlanStep,
    InformationGap,
    FinalPlan,
    FinalPlanStep,
    VerificationCategory,
)


FIRST_ITERATION_PROMPT = """## SYSTEM INSTRUCTION FOR PlanSynthesizerAgent - ITERATION 1: GAP ANALYSIS

You are **PlanSynthesizerAgent**, a research planning specialist analyzing solutions to create an implementation plan.

### Your Task

Analyze the provided problem and solutions to create a PRELIMINARY PLAN that clearly identifies:
1. **What information/solutions we HAVE** - concrete knowledge available
2. **What information we LACK** - gaps that need to be filled

---

### Input Format

You will receive:
1. **Problem**: The main problem to be solved
2. **Problem Breakdown**: A hierarchical breakdown of the problem into requirements
3. **Solutions**: Solutions generated for various requirements, with confidence scores and sources

---

### Analysis Guidelines

**For each step in your plan, evaluate:**

1. **What We Have**:
   - Which solutions directly address this step?
   - What is the confidence level of those solutions?
   - Is the information from existing literature (EXISTING) or generated (NOVEL)?

2. **What We Lack** (identify gaps such as):
   - Missing technical specifications
   - Unknown material properties or behaviors
   - Unresolved trade-offs between approaches
   - Missing integration details between subsystems
   - Unknown performance characteristics
   - Safety margins and failure modes

3. **Gap Query Formulation**:
   - For each gap, formulate a specific query that could be used to search a knowledge base
   - Be specific and technical in your queries

---

### Output Format (JSON)

```json
{
  "problem_summary": "Brief summary of the core problem being solved",
  "available_knowledge_summary": "Summary of what knowledge/solutions are available",
  "steps": [
    {
      "step_number": 1,
      "name": "Step name",
      "description": "What this step accomplishes",
      "what_we_have": "Specific information available for this step",
      "what_we_lack": ["Gap 1 description", "Gap 2 description"],
      "preliminary_approach": "How to approach this step given current knowledge",
      "dependencies": [],
      "confidence": 0.0 to 1.0
    }
  ],
  "gaps": [
    {
      "description": "Detailed description of the information gap",
      "query_for_kb": "Technical query to search knowledge base",
      "related_step_ids": [1, 2]
    }
  ],
  "overall_confidence": 0.0 to 1.0
}
```

---

### Important Rules

1. **Be specific about gaps**: Don't say "need more information" - say exactly WHAT information is missing
2. **Be honest about uncertainty**: If solutions have low confidence, reflect this in the plan
3. **Formulate searchable queries**: Gap queries should be specific enough to find relevant documents
4. **Consider dependencies**: Steps that depend on gaps should have lower confidence
5. **Think about implementation**: Focus on practical steps to SOLVE the problem
6. **Distinguish types of knowledge needs**:
   - Information that might exist in literature (searchable)
   - Information that requires physical experiments (not searchable - note it needs empirical work)

Output ONLY valid JSON, no additional text.
"""


SECOND_ITERATION_PROMPT = """## SYSTEM INSTRUCTION FOR PlanSynthesizerAgent - ITERATION 2: REFINEMENT

You are **PlanSynthesizerAgent**, refining a preliminary plan by incorporating newly retrieved information.

### Your Task

Take the preliminary plan and:
1. **Integrate retrieved information** to fill gaps where possible
2. **Refine step descriptions** with more specific details
3. **Mark each step with verification requirements**

---

### Input Format

You will receive:
1. **Preliminary Plan**: The plan from iteration 1 with identified gaps
2. **Retrieved Information**: For each gap, any information found in the knowledge base

---

### Verification Categories

Mark each step with ONE of these categories:

1. **information_complete**: Step can be executed with available information
   - Example: "Use polyethylene as primary shielding material (well-documented properties)"

2. **requires_experiment**: Needs physical lab experiments
   - Example: "Test radiation attenuation of hybrid shield under simulated GCR conditions"

3. **requires_field_test**: Needs testing in target environment
   - Example: "Validate thermal performance in Mars-analog vacuum chamber"

4. **requires_prototype**: Needs physical construction
   - Example: "Fabricate modular habitat section for structural testing"

5. **requires_simulation**: Needs computational modeling
   - Example: "Run Monte Carlo radiation transport simulation"

6. **requires_measurement**: Needs physical measurements
   - Example: "Measure actual crew doses during ISS EVA for baseline"

7. **requires_expert_review**: Needs human expert review
   - Example: "Safety review of life support redundancy design"

---

### Decision Guidelines for Verification

**Mark as information_complete when:**
- Solution comes from established literature with high confidence
- Well-known physics/chemistry principles that don't need validation
- Existing NASA protocols or standards that can be directly applied

**Mark as requires_* when:**
- Solution involves novel combinations not previously tested
- Performance claims need empirical validation
- Safety-critical decisions
- Physical construction or fabrication is needed
- Environmental conditions affect performance unpredictably

---

### Output Format (JSON)

```json
{
  "problem_statement": "Clear statement of the problem being solved",
  "hypothesis_refined": "Refined hypothesis based on analysis",
  "executive_summary": "2-3 sentence summary of the plan",
  "steps": [
    {
      "step_number": 1,
      "name": "Step name",
      "description": "Detailed description",
      "detailed_approach": "Specific technical approach",
      "expected_output": "What this step produces",
      "dependencies": [],
      "verification_category": "information_complete|requires_experiment|requires_field_test|requires_prototype|requires_simulation|requires_measurement|requires_expert_review",
      "verification_details": "What exactly needs to be verified and how",
      "estimated_effort": "Time/resource estimate if verification needed",
      "knowledge_sources": ["Source 1", "Source 2"],
      "confidence": 0.0 to 1.0
    }
  ],
  "total_steps": N,
  "steps_information_complete": N,
  "steps_requiring_verification": N,
  "remaining_gaps": ["Gap that could not be filled"],
  "overall_feasibility": "Assessment of plan feasibility",
  "key_risks": ["Risk 1", "Risk 2"],
  "recommended_next_actions": ["Action 1", "Action 2"]
}
```

---

### Important Rules

1. **Use retrieved information**: Integrate KB results into step details
2. **Be conservative with information_complete**: When in doubt, require verification
3. **Be specific about verification**: Don't just say "needs testing" - say WHAT and HOW
4. **Estimate effort realistically**: Lab work takes weeks, field tests take months
5. **Track remaining gaps**: If KB didn't help, note it as a remaining gap
6. **Focus on actionability**: The plan should tell someone exactly what to do

Output ONLY valid JSON, no additional text.
"""


class PlanSynthesizerInput(BaseModel):
    """Input for the plan synthesizer agent."""

    hypothesis: Hypothesis
    graph: RequirementGraph
    solutions: dict[UUID, Solution]


class PlanSynthesizerOutput(BaseModel):
    """Output from the plan synthesizer agent."""

    preliminary_plan: PreliminaryPlan
    final_plan: FinalPlan
    plan_markdown: str


class PlanSynthesizerAgent(BaseAgent[PlanSynthesizerInput, PlanSynthesizerOutput]):
    """
    Iterative plan synthesizer using two-pass approach.

    Process:
    1. First iteration: Analyze graph + solutions, identify gaps
    2. Gap filling: Query KB for each identified gap
    3. Second iteration: Refine plan with filled gaps, add verification markers
    4. Render PLAN.md with verification markers
    """

    def __init__(self):
        super().__init__(
            name="plan_synthesizer",
            instructions=FIRST_ITERATION_PROMPT,
        )
        self.retriever = RetrieverAgent()
        self._refinement_agent = self.chat_client.create_agent(
            name="plan_refiner",
            instructions=SECOND_ITERATION_PROMPT,
        )

    async def execute(self, input_data: PlanSynthesizerInput) -> PlanSynthesizerOutput:
        """
        Execute two-iteration plan synthesis.

        Args:
            input_data: Hypothesis, requirement graph, and solutions

        Returns:
            PlanSynthesizerOutput with preliminary plan, final plan, and markdown
        """
        # === ITERATION 1: Gap Analysis ===
        preliminary_plan = await self._iteration_one(
            input_data.hypothesis,
            input_data.graph,
            input_data.solutions,
        )

        # === GAP FILLING: Query KB for each gap ===
        filled_gaps = await self._fill_gaps(preliminary_plan.gaps)

        # === ITERATION 2: Refinement ===
        final_plan = await self._iteration_two(preliminary_plan, filled_gaps)

        # === RENDER MARKDOWN ===
        plan_markdown = self._render_plan_markdown(
            input_data.hypothesis,
            final_plan,
        )

        return PlanSynthesizerOutput(
            preliminary_plan=preliminary_plan,
            final_plan=final_plan,
            plan_markdown=plan_markdown,
        )

    async def _iteration_one(
        self,
        hypothesis: Hypothesis,
        graph: RequirementGraph,
        solutions: dict[UUID, Solution],
    ) -> PreliminaryPlan:
        """
        First iteration: Analyze what we have vs what we lack.

        Args:
            hypothesis: The research hypothesis
            graph: Requirement graph
            solutions: Map of requirement ID to solution

        Returns:
            PreliminaryPlan with gaps identified
        """
        prompt = self._format_iteration_one_input(hypothesis, graph, solutions)
        result = await self._agent.run(prompt)
        plan_dict = self._parse_json_response(result.text)
        return self._build_preliminary_plan(plan_dict)

    async def _fill_gaps(
        self,
        gaps: list[InformationGap],
    ) -> dict[UUID, str]:
        """
        Query KB for each identified gap.

        Args:
            gaps: List of information gaps from preliminary plan

        Returns:
            Dict mapping gap ID to retrieved content
        """
        filled = {}

        for gap in gaps:
            result = await self.retriever.execute(
                RetrieverAgentInput(query=gap.query_for_kb, top_k=5)
            )

            if result.success and result.chunks:
                filled[gap.id] = result.chunks
                gap.filled = True
                gap.filled_content = result.chunks
                gap.sources = result.sources

        return filled

    async def _iteration_two(
        self,
        preliminary_plan: PreliminaryPlan,
        filled_gaps: dict[UUID, str],
    ) -> FinalPlan:
        """
        Second iteration: Refine plan with filled gaps.

        IMPORTANT: Input is ONLY the preliminary plan, not original graph.

        Args:
            preliminary_plan: Plan from iteration 1
            filled_gaps: Retrieved information for gaps

        Returns:
            FinalPlan with verification markers
        """
        prompt = self._format_iteration_two_input(preliminary_plan, filled_gaps)
        result = await self._refinement_agent.run(prompt)
        plan_dict = self._parse_json_response(result.text)
        return self._build_final_plan(plan_dict)

    def _format_iteration_one_input(
        self,
        hypothesis: Hypothesis,
        graph: RequirementGraph,
        solutions: dict[UUID, Solution],
    ) -> str:
        """Format the input for iteration one LLM call."""
        graph_text = self._format_graph(graph)
        solutions_text = self._format_solutions(graph, solutions)

        return f"""## Problem
{hypothesis.original_text}

{f"Refined: {hypothesis.refined_text}" if hypothesis.refined_text else ""}

## Problem Breakdown (Requirement Graph)
{graph_text}

## Available Solutions
{solutions_text}

Analyze this information and create a preliminary implementation plan with identified gaps.
Output JSON only."""

    def _format_iteration_two_input(
        self,
        preliminary_plan: PreliminaryPlan,
        filled_gaps: dict[UUID, str],
    ) -> str:
        """Format input for iteration two - ONLY the preliminary plan."""
        steps_text = ""
        for step in preliminary_plan.steps:
            steps_text += f"""
### Step {step.step_number}: {step.name}
- Description: {step.description}
- What we have: {step.what_we_have}
- What we lack: {', '.join(step.what_we_lack) if step.what_we_lack else 'None'}
- Preliminary approach: {step.preliminary_approach}
- Confidence: {step.confidence}
"""

        gaps_text = ""
        for gap in preliminary_plan.gaps:
            filled_content = filled_gaps.get(gap.id, "No information found")
            content_preview = filled_content[:1000] + "..." if len(str(filled_content)) > 1000 else filled_content
            gaps_text += f"""
### Gap: {gap.description}
- Query: {gap.query_for_kb}
- Retrieved Information: {content_preview}
- Sources: {', '.join(gap.sources) if gap.sources else 'None'}
"""

        return f"""## Preliminary Plan

Problem Summary: {preliminary_plan.problem_summary}

Available Knowledge: {preliminary_plan.available_knowledge_summary}

{steps_text}

## Retrieved Information for Gaps
{gaps_text}

Refine this plan by:
1. Integrating retrieved information
2. Adding specific verification requirements for each step
3. Marking remaining gaps that could not be filled

Output JSON only."""

    def _format_graph(self, graph: RequirementGraph) -> str:
        """Format requirement graph as readable text."""
        lines = []

        def format_node(node: Requirement, indent: int = 0):
            prefix = "  " * indent
            lines.append(f"{prefix}- [{node.status.value}] {node.content}")
            for child in graph.get_children(node.id):
                format_node(child, indent + 1)

        root = graph.get_root()
        format_node(root)
        return "\n".join(lines)

    def _format_solutions(
        self,
        graph: RequirementGraph,
        solutions: dict[UUID, Solution],
    ) -> str:
        """Format solutions as readable text."""
        lines = []
        for req_id, solution in solutions.items():
            req = graph.get_node(req_id)
            if req:
                content_preview = solution.content[:500] + "..." if len(solution.content) > 500 else solution.content
                lines.append(f"""
Requirement: {req.content}
Solution ({solution.source.value}, confidence={solution.confidence:.2f}):
{content_preview}
---""")
        return "\n".join(lines)

    def _parse_json_response(self, text: str) -> dict:
        """Parse JSON from LLM response, handling markdown code blocks."""
        text = text.strip()

        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {
                "problem_summary": "Failed to parse LLM response",
                "steps": [],
                "gaps": [],
            }

    def _build_preliminary_plan(self, data: dict) -> PreliminaryPlan:
        """Build PreliminaryPlan from parsed JSON dict."""
        steps = []
        for step_data in data.get("steps", []):
            steps.append(PreliminaryPlanStep(
                step_number=step_data.get("step_number", len(steps) + 1),
                name=step_data.get("name", ""),
                description=step_data.get("description", ""),
                what_we_have=step_data.get("what_we_have", ""),
                what_we_lack=step_data.get("what_we_lack", []),
                preliminary_approach=step_data.get("preliminary_approach", ""),
                dependencies=step_data.get("dependencies", []),
                confidence=step_data.get("confidence", 0.5),
            ))

        gaps = []
        for gap_data in data.get("gaps", []):
            gap = InformationGap(
                description=gap_data.get("description", ""),
                query_for_kb=gap_data.get("query_for_kb", ""),
                related_step_ids=gap_data.get("related_step_ids", []),
            )
            gaps.append(gap)

        return PreliminaryPlan(
            problem_summary=data.get("problem_summary", ""),
            available_knowledge_summary=data.get("available_knowledge_summary", ""),
            steps=steps,
            gaps=gaps,
            overall_confidence=data.get("overall_confidence", 0.5),
        )

    def _build_final_plan(self, data: dict) -> FinalPlan:
        """Build FinalPlan from parsed JSON dict."""
        steps = []
        for step_data in data.get("steps", []):
            category_str = step_data.get("verification_category", "information_complete")
            try:
                category = VerificationCategory(category_str)
            except ValueError:
                category = VerificationCategory.REQUIRES_EXPERT_REVIEW

            steps.append(FinalPlanStep(
                step_number=step_data.get("step_number", len(steps) + 1),
                name=step_data.get("name", ""),
                description=step_data.get("description", ""),
                detailed_approach=step_data.get("detailed_approach", ""),
                expected_output=step_data.get("expected_output", ""),
                dependencies=step_data.get("dependencies", []),
                verification_category=category,
                verification_details=step_data.get("verification_details", ""),
                estimated_effort=step_data.get("estimated_effort", ""),
                knowledge_sources=step_data.get("knowledge_sources", []),
                confidence=step_data.get("confidence", 0.7),
            ))

        return FinalPlan(
            problem_statement=data.get("problem_statement", ""),
            hypothesis_refined=data.get("hypothesis_refined", ""),
            executive_summary=data.get("executive_summary", ""),
            steps=steps,
            total_steps=data.get("total_steps", len(steps)),
            steps_information_complete=data.get("steps_information_complete", 0),
            steps_requiring_verification=data.get("steps_requiring_verification", 0),
            remaining_gaps=data.get("remaining_gaps", []),
            overall_feasibility=data.get("overall_feasibility", ""),
            key_risks=data.get("key_risks", []),
            recommended_next_actions=data.get("recommended_next_actions", []),
        )

    def _render_plan_markdown(
        self,
        hypothesis: Hypothesis,
        plan: FinalPlan,
    ) -> str:
        """Render the final plan as PLAN.md markdown."""
        lines = []

        # Header
        lines.append("# Implementation Plan")
        lines.append("")
        lines.append(f"**Problem**: {plan.problem_statement}")
        lines.append("")
        lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(plan.executive_summary)
        lines.append("")

        # Statistics
        lines.append("## Plan Overview")
        lines.append("")
        lines.append(f"- **Total Steps**: {plan.total_steps}")
        lines.append(f"- **Information Complete**: {plan.steps_information_complete} steps")
        lines.append(f"- **Requires Verification**: {plan.steps_requiring_verification} steps")
        lines.append(f"- **Feasibility Assessment**: {plan.overall_feasibility}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Steps grouped by verification category
        complete_steps = [s for s in plan.steps if s.verification_category == VerificationCategory.INFORMATION_COMPLETE]
        verification_steps = [s for s in plan.steps if s.verification_category != VerificationCategory.INFORMATION_COMPLETE]

        if complete_steps:
            lines.append("## Steps Ready for Implementation")
            lines.append("")
            lines.append("*These steps have sufficient information and can proceed directly.*")
            lines.append("")
            for step in complete_steps:
                lines.extend(self._render_step(step))
            lines.append("---")
            lines.append("")

        if verification_steps:
            lines.append("## Steps Requiring Empirical Verification")
            lines.append("")
            lines.append("*These steps require physical experiments, tests, or expert review before full implementation.*")
            lines.append("")
            for step in verification_steps:
                lines.extend(self._render_step(step, show_verification=True))
            lines.append("---")
            lines.append("")

        # Remaining Gaps
        if plan.remaining_gaps:
            lines.append("## Remaining Knowledge Gaps")
            lines.append("")
            lines.append("*These gaps could not be filled from the knowledge base and require further research.*")
            lines.append("")
            for i, gap in enumerate(plan.remaining_gaps, 1):
                lines.append(f"{i}. {gap}")
            lines.append("")
            lines.append("---")
            lines.append("")

        # Risks
        if plan.key_risks:
            lines.append("## Key Risks")
            lines.append("")
            for i, risk in enumerate(plan.key_risks, 1):
                lines.append(f"{i}. {risk}")
            lines.append("")
            lines.append("---")
            lines.append("")

        # Next Actions
        if plan.recommended_next_actions:
            lines.append("## Recommended Next Actions")
            lines.append("")
            for i, action in enumerate(plan.recommended_next_actions, 1):
                lines.append(f"{i}. {action}")
            lines.append("")
            lines.append("---")
            lines.append("")

        # Footer
        lines.append("*Generated by PlanSynthesizerAgent | We Go Mars*")

        return "\n".join(lines)

    def _render_step(self, step: FinalPlanStep, show_verification: bool = False) -> list[str]:
        """Render a single step as markdown lines."""
        lines = []

        lines.append(f"### Step {step.step_number}: {step.name}")
        lines.append("")
        lines.append(f"**Description**: {step.description}")
        lines.append("")
        lines.append(f"**Approach**: {step.detailed_approach}")
        lines.append("")
        lines.append(f"**Expected Output**: {step.expected_output}")
        lines.append("")

        if step.dependencies:
            lines.append(f"**Dependencies**: Steps {', '.join(map(str, step.dependencies))}")
            lines.append("")

        if show_verification:
            category_display = step.verification_category.value.replace("_", " ").title()
            lines.append(f"> **EMPIRICAL VERIFICATION REQUIRED**: {category_display}")
            lines.append(f">")
            lines.append(f"> {step.verification_details}")
            if step.estimated_effort:
                lines.append(f">")
                lines.append(f"> *Estimated Effort*: {step.estimated_effort}")
            lines.append("")

        if step.knowledge_sources:
            lines.append(f"**Sources**: {', '.join(step.knowledge_sources)}")
            lines.append("")

        lines.append(f"**Confidence**: {step.confidence:.0%}")
        lines.append("")

        return lines
