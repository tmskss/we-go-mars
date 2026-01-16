"""
Retriever Agent for RAG-based context retrieval.

This agent retrieves relevant context from the literature store
using query reforming and relevance checking.

Owner: [ASSIGN TEAMMATE]
"""

from pydantic import BaseModel

from src.agents.base import BaseAgent
from src.rag import LiteratureStore


QUERY_REFORM_PROMPT = """You are a query optimization agent.

Your task is to reformulate the user's query to be more effective for vector search.

Guidelines:
- Expand abbreviations and acronyms
- Add relevant synonyms or related terms
- Make the query more specific if too vague
- Keep the core intent intact

Return ONLY the optimized query, nothing else."""

RELEVANCE_CHECK_PROMPT = """Your task is to determine if the retrieved chunks contain information that helps answer the user query.

Instructions:
- Read the query and the provided chunks.
- If the chunks contain information useful or related to answering the query, respond with exactly:
  "RELEVANT"
- If the chunks do not provide useful information for the query, respond with exactly:
  "NOT_RELEVANT"
- Do not output anything else."""


class RetrieverAgentInput(BaseModel):
    """Input for the retriever agent."""

    query: str
    top_k: int = 5


class RetrieverAgentOutput(BaseModel):
    """Output from the retriever agent."""

    success: bool
    chunks: str  # Concatenated relevant chunks
    sources: list[str]  # Document titles for attribution


class RetrieverAgent(BaseAgent[RetrieverAgentInput, RetrieverAgentOutput]):
    """
    Agent that retrieves relevant context from the literature store.

    Process:
    1. Reform query for optimal vector search
    2. Execute hybrid search via LiteratureStore
    3. Check relevance of retrieved chunks
    4. Return concatenated context if relevant
    """

    def __init__(self):
        super().__init__(
            name="retriever",
            instructions=QUERY_REFORM_PROMPT,
        )
        self.store = LiteratureStore()
        self._relevance_agent = self.chat_client.create_agent(
            name="relevance_checker",
            instructions=RELEVANCE_CHECK_PROMPT,
        )

    async def _reform_query(self, query: str) -> str:
        """Reform the query for better vector search results."""
        result = await self._agent.run(query)
        return result.text.strip()

    async def _check_relevance(self, query: str, chunks: str) -> bool:
        """Check if retrieved chunks are relevant to the query."""
        input_text = f"Query: {query}\n\nChunks:\n{chunks}"
        result = await self._relevance_agent.run(input_text)
        return "RELEVANT" in result.text.upper()

    async def execute(
        self, input_data: RetrieverAgentInput
    ) -> RetrieverAgentOutput:
        """
        Retrieve relevant context from the literature store.

        Args:
            input_data: RetrieverAgentInput containing query and top_k

        Returns:
            RetrieverAgentOutput with success status, chunks, and sources
        """
        # Step 1: Reform the query for better search
        reformed_query = await self._reform_query(input_data.query)

        # Step 2: Execute hybrid search
        results = self.store.search(reformed_query, top_k=input_data.top_k)

        if not results:
            return RetrieverAgentOutput(
                success=False,
                chunks="",
                sources=[],
            )

        # Step 3: Concatenate chunks and collect sources
        chunks_text = "\n\n".join([r.chunk.content for r in results])
        sources = list(set([r.document_title for r in results]))

        # Step 4: Check relevance
        is_relevant = await self._check_relevance(input_data.query, chunks_text)

        return RetrieverAgentOutput(
            success=is_relevant,
            chunks=chunks_text if is_relevant else "",
            sources=sources if is_relevant else [],
        )
