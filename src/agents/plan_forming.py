"""
Plan Forming Agent.

This agent synthesizes all subproblems and solutions into an action-oriented
PLAN.md file, categorizing items as:
- Implemented (ready to use)
- Needs Verification (requires experiments, lab work, human review)
- Needs Research (knowledge gaps, low confidence)

Owner: [ASSIGN TEAMMATE]
"""

import json
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field

from src.agents.base import BaseAgent
from src.agents.retriever import RetrieverAgent, RetrieverAgentInput
from src.models.hypothesis import Hypothesis
from src.models.requirement import Requirement, RequirementGraph
from src.models.solution import Solution, SolutionSource


class PlanCategory(str, Enum):
    """Category for plan items."""

    IMPLEMENTED = "implemented"
    NEEDS_VERIFICATION = "needs_verification"
    NEEDS_RESEARCH = "needs_research"


class VerificationType(str, Enum):
    """Type of verification needed."""

    EXPERIMENT = "experiment"
    LAB_WORK = "lab_work"
    FIELD_TEST = "field_test"
    HUMAN_REVIEW = "human_review"
    PROTOTYPE = "prototype"
    SIMULATION = "simulation"


class PlanItem(BaseModel):
    """A single item in the plan."""

    requirement_id: UUID
    requirement_content: str
    solution_summary: str
    category: PlanCategory
    confidence: float
    source: SolutionSource
    reasoning: str
    verification_type: VerificationType | None = None
    verification_details: str | None = None
    research_questions: list[str] = Field(default_factory=list)


class PlanFormingInput(BaseModel):
    """Input for the plan forming agent."""

    hypothesis: Hypothesis
    graph: RequirementGraph
    solutions: dict[UUID, Solution]


class PlanFormingOutput(BaseModel):
    """Output from the plan forming agent."""

    implemented: list[PlanItem] = Field(default_factory=list)
    needs_verification: list[PlanItem] = Field(default_factory=list)
    needs_research: list[PlanItem] = Field(default_factory=list)
    overall_gaps: list[str] = Field(default_factory=list)
    plan_markdown: str = ""


SYSTEM_PROMPT = """## SYSTEM INSTRUCTION FOR PlanFormingAgent

You are **PlanFormingAgent**, a specialized agent that transforms research solutions into actionable plans.

Your role is to analyze solutions to research problems and categorize them into action-oriented buckets based on what actions are required next.

---

### Your Categories

1. **IMPLEMENTED** - Solutions that are well-established and can be directly applied:
   - Solutions based on existing, validated knowledge
   - Theoretical foundations that don't require physical experiments
   - Known physics, chemistry, or established methodologies
   - Information that can be directly used without further validation

2. **NEEDS_VERIFICATION** - Solutions requiring human intervention or physical work:
   - Physical experiments that must be conducted (e.g., "test radiation shielding effectiveness")
   - Lab work with biological materials (e.g., "culture bacteria", "grow plants", "prepare samples")
   - Field testing in real environments (e.g., "test in Mars-like conditions", "vacuum chamber tests")
   - Prototype construction (e.g., "build habitat module", "fabricate shield")
   - Computational simulations that need to be run and validated
   - Safety-critical decisions requiring expert human review

3. **NEEDS_RESEARCH** - Areas requiring further investigation:
   - Solutions with very low confidence or high uncertainty
   - Areas where knowledge gaps were identified
   - Contradictory or incomplete information
   - Topics where the knowledge base had insufficient sources

---

### Verification Type Detection

When categorizing as NEEDS_VERIFICATION, identify the specific type:

- **EXPERIMENT**: Physical measurements, empirical validation, testing hypotheses
- **LAB_WORK**: Biological cultures, chemical synthesis, sample preparation, material testing
- **FIELD_TEST**: Deployment in target environment, real-world conditions, environmental chambers
- **HUMAN_REVIEW**: Expert opinion required, safety review, ethical considerations, novel approaches
- **PROTOTYPE**: Physical construction, fabrication, assembly of hardware
- **SIMULATION**: Computational modeling, numerical analysis, Monte Carlo simulations

---

### Decision Guidelines

**Key principle**: You must distinguish between what AGENTS CAN DO vs what HUMANS MUST DO.

Things agents CAN do (often → IMPLEMENTED):
- Retrieve and synthesize information
- Apply known formulas and calculations
- Combine existing knowledge
- Reason about documented principles

Things agents CANNOT do (often → NEEDS_VERIFICATION):
- Conduct physical experiments
- Grow biological samples
- Build physical prototypes
- Test in real environments
- Make safety-critical final decisions
- Validate through measurement

---

### Input Format

You will receive:
1. **Requirement**: The problem being addressed
2. **Solution**: The proposed solution content
3. **Confidence**: Numerical confidence score (0-1)
4. **Source**: Whether solution is from EXISTING literature or NOVEL generation
5. **Additional Context**: Retrieved knowledge if available

---

### Output Format (JSON)

For each solution, output valid JSON:
```json
{
  "category": "implemented" | "needs_verification" | "needs_research",
  "reasoning": "Brief explanation of categorization",
  "verification_type": "experiment" | "lab_work" | "field_test" | "human_review" | "prototype" | "simulation" | null,
  "verification_details": "Specific steps required if needs verification",
  "research_questions": ["Question 1", "Question 2"]
}
```

---

### Domain-Specific Considerations (Space/Mars Mission)

- Radiation shielding effectiveness → NEEDS_VERIFICATION (requires testing)
- Life support biological systems → NEEDS_VERIFICATION (requires lab work)
- Known orbital mechanics → IMPLEMENTED
- Material properties under Mars conditions → NEEDS_VERIFICATION (field test)
- Novel habitat designs → NEEDS_VERIFICATION (prototype + simulation)
- Established NASA protocols → IMPLEMENTED

---

### Important Rules

1. Be CONSERVATIVE: When uncertain, prefer NEEDS_VERIFICATION or NEEDS_RESEARCH
2. Focus on ACTIONABILITY: What must be DONE next?
3. Never mark something as IMPLEMENTED if it requires physical validation
4. Consider the Mars mission context for all decisions
5. Output only valid JSON, no extra text
"""


class PlanFormingAgent(BaseAgent[PlanFormingInput, PlanFormingOutput]):
    """
    Synthesizes all subproblems and solutions into an action-oriented plan.

    Process:
    1. Extract all (requirement, solution) pairs from the graph
    2. For unclear items, query KB per-item for additional context
    3. Use LLM to categorize based on context (what needs physical work vs info synthesis)
    4. Render PLAN.md with sections: Implemented, Needs Verification, Needs Research
    """

    def __init__(self):
        super().__init__(
            name="plan_former",
            instructions=SYSTEM_PROMPT,
        )
        self.retriever = RetrieverAgent()

    def _extract_pairs(
        self, graph: RequirementGraph, solutions: dict[UUID, Solution]
    ) -> list[tuple[Requirement, Solution]]:
        """Extract all (requirement, solution) pairs from the graph."""
        pairs = []
        seen_ids: set[UUID] = set()

        for node_id, solution in solutions.items():
            if node_id in seen_ids:
                continue
            seen_ids.add(node_id)

            node = graph.get_node(node_id)
            if node:
                pairs.append((node, solution))

        return pairs

    def _is_unclear(self, solution: Solution) -> bool:
        """Determine if a solution needs additional KB context."""
        # Medium confidence range - could go either way
        if 0.4 <= solution.confidence <= 0.7:
            return True
        # Novel solutions might benefit from KB lookup
        if solution.source == SolutionSource.NOVEL and solution.confidence < 0.8:
            return True
        return False

    async def _query_kb_for_item(
        self, requirement: Requirement, solution: Solution, hypothesis: Hypothesis
    ) -> str:
        """Query KB for additional context on an unclear item."""
        query = f"{hypothesis.original_text} - {requirement.content}: {solution.content[:300]}"

        result = await self.retriever.execute(
            RetrieverAgentInput(query=query, top_k=3)
        )

        return result.chunks if result.success else ""

    async def _categorize_item(
        self,
        requirement: Requirement,
        solution: Solution,
        additional_context: str,
    ) -> dict:
        """Use LLM to categorize a single item."""
        prompt = f"""Categorize this solution:

Requirement: {requirement.content}

Solution: {solution.content}

Confidence: {solution.confidence}
Source: {solution.source.value}

Additional Context: {additional_context if additional_context else "None available"}

Respond with JSON only."""

        response = await self._agent.run(prompt)

        # Parse JSON from response
        try:
            # Try to extract JSON from response
            text = response.text.strip()
            # Handle markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            return json.loads(text)
        except (json.JSONDecodeError, IndexError):
            # Default categorization if parsing fails
            return {
                "category": "needs_research",
                "reasoning": "Could not parse LLM response, defaulting to needs_research",
                "verification_type": None,
                "verification_details": None,
                "research_questions": ["Further investigation required"],
            }

    def _render_markdown(
        self, output: PlanFormingOutput, hypothesis: Hypothesis
    ) -> str:
        """Render the plan as markdown."""
        lines = []

        # Header
        lines.append(f"# Action Plan: {hypothesis.original_text[:100]}")
        lines.append("")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Implemented**: {len(output.implemented)} items ready to use")
        lines.append(f"- **Needs Verification**: {len(output.needs_verification)} items requiring experiments/human work")
        lines.append(f"- **Needs Research**: {len(output.needs_research)} items requiring further investigation")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Implemented section
        if output.implemented:
            lines.append("## Implemented (Ready to Use)")
            lines.append("")
            lines.append("These solutions are well-established and can be directly applied.")
            lines.append("")

            for item in output.implemented:
                lines.append(f"### {item.requirement_content[:80]}")
                lines.append("")
                lines.append(f"**Solution**: {item.solution_summary}")
                lines.append("")
                lines.append(f"- **Confidence**: {item.confidence:.0%}")
                lines.append(f"- **Source**: {item.source.value.upper()}")
                lines.append(f"- **Reasoning**: {item.reasoning}")
                lines.append("")

            lines.append("---")
            lines.append("")

        # Needs Verification section
        if output.needs_verification:
            lines.append("## Needs Verification")
            lines.append("")
            lines.append("These items require human intervention, physical experiments, or real-world testing.")
            lines.append("")

            for item in output.needs_verification:
                lines.append(f"### {item.requirement_content[:80]}")
                lines.append("")
                lines.append(f"**Solution**: {item.solution_summary}")
                lines.append("")
                if item.verification_type:
                    lines.append(f"- **Verification Type**: {item.verification_type.value.replace('_', ' ').title()}")
                lines.append(f"- **Confidence**: {item.confidence:.0%}")
                lines.append(f"- **Why Verification Needed**: {item.reasoning}")
                lines.append("")
                if item.verification_details:
                    lines.append("**Verification Steps**:")
                    lines.append("")
                    lines.append(item.verification_details)
                    lines.append("")

            lines.append("---")
            lines.append("")

        # Needs Research section
        if output.needs_research:
            lines.append("## Needs More Research")
            lines.append("")
            lines.append("These areas have knowledge gaps or low confidence and require further investigation.")
            lines.append("")

            for item in output.needs_research:
                lines.append(f"### {item.requirement_content[:80]}")
                lines.append("")
                lines.append(f"**Current Understanding**: {item.solution_summary}")
                lines.append("")
                lines.append(f"- **Confidence**: {item.confidence:.0%}")
                lines.append(f"- **Why More Research**: {item.reasoning}")
                lines.append("")
                if item.research_questions:
                    lines.append("**Research Questions**:")
                    lines.append("")
                    for i, q in enumerate(item.research_questions, 1):
                        lines.append(f"{i}. {q}")
                    lines.append("")

            lines.append("---")
            lines.append("")

        # Overall Gaps section
        if output.overall_gaps:
            lines.append("## Overall Gaps")
            lines.append("")
            lines.append("The following gaps were identified across all solutions:")
            lines.append("")
            for i, gap in enumerate(output.overall_gaps, 1):
                lines.append(f"{i}. {gap}")
            lines.append("")
            lines.append("---")
            lines.append("")

        # Footer
        lines.append("*Generated by PlanFormingAgent | We Go Mars*")

        return "\n".join(lines)

    async def execute(self, input_data: PlanFormingInput) -> PlanFormingOutput:
        """
        Synthesize all subproblems and solutions into an action-oriented plan.

        Args:
            input_data: PlanFormingInput with hypothesis, graph, and solutions

        Returns:
            PlanFormingOutput with categorized items and PLAN.md content
        """
        output = PlanFormingOutput()

        # Extract all (requirement, solution) pairs
        pairs = self._extract_pairs(input_data.graph, input_data.solutions)

        # Process each pair
        for requirement, solution in pairs:
            # Query KB for unclear items
            additional_context = ""
            if self._is_unclear(solution):
                additional_context = await self._query_kb_for_item(
                    requirement, solution, input_data.hypothesis
                )

            # Categorize using LLM
            categorization = await self._categorize_item(
                requirement, solution, additional_context
            )

            # Build PlanItem
            category_str = categorization.get("category", "needs_research")
            try:
                category = PlanCategory(category_str)
            except ValueError:
                category = PlanCategory.NEEDS_RESEARCH

            verification_type = None
            if categorization.get("verification_type"):
                try:
                    verification_type = VerificationType(categorization["verification_type"])
                except ValueError:
                    pass

            plan_item = PlanItem(
                requirement_id=requirement.id,
                requirement_content=requirement.content,
                solution_summary=solution.content[:500] + ("..." if len(solution.content) > 500 else ""),
                category=category,
                confidence=solution.confidence,
                source=solution.source,
                reasoning=categorization.get("reasoning", ""),
                verification_type=verification_type,
                verification_details=categorization.get("verification_details"),
                research_questions=categorization.get("research_questions", []),
            )

            # Add to appropriate list
            if category == PlanCategory.IMPLEMENTED:
                output.implemented.append(plan_item)
            elif category == PlanCategory.NEEDS_VERIFICATION:
                output.needs_verification.append(plan_item)
            else:
                output.needs_research.append(plan_item)

        # Collect overall gaps from research items
        for item in output.needs_research:
            if item.research_questions:
                output.overall_gaps.extend(item.research_questions[:2])

        # Render markdown
        output.plan_markdown = self._render_markdown(output, input_data.hypothesis)

        return output
