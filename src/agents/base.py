"""
Base agent class for all agents in the system.

Uses Microsoft Agent Framework for LLM interactions and workflow integration.

Owner: [ASSIGN TEAMMATE]

References:
- https://github.com/microsoft/agent-framework
- https://learn.microsoft.com/en-us/agent-framework/
"""

from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic

from agent_framework import Executor, WorkflowContext, handler
from agent_framework.openai import OpenAIChatClient

from src.config import settings

# Type variables for input/output typing
TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


def create_chat_client() -> OpenAIChatClient:
    """
    Create a configured OpenAI chat client.

    Returns:
        Configured OpenAIChatClient instance
    """
    return OpenAIChatClient(
        model_id="gpt-5-mini"
    )


class BaseAgent(ABC, Generic[TInput, TOutput]):
    """
    Abstract base class for all agents.

    This class provides two modes of operation:
    1. Standalone execution via execute() - for direct agent calls
    2. Workflow execution via as_executor() - for workflow integration

    Attributes:
        name: Unique name for this agent instance
        instructions: The system prompt that defines agent behavior
        chat_client: The underlying Microsoft Agent Framework client
    """

    def __init__(self, name: str, instructions: str):
        """
        Initialize the base agent.

        Args:
            name: Unique identifier for this agent
            instructions: System instructions defining agent behavior
        """
        self.name = name
        self.instructions = instructions
        self.chat_client = create_chat_client()

        # Create the agent using Microsoft Agent Framework
        self._agent = self.chat_client.create_agent(
            name=name,
            instructions=instructions,
        )

    async def run(self, message: str) -> str:
        """
        Run the agent with a simple string message.

        Args:
            message: The user message to process

        Returns:
            The agent's response text
        """
        result = await self._agent.run(message)
        return result.text

    async def run_with_history(self, messages: list[dict]) -> str:
        """
        Run the agent with conversation history.

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            The agent's response text
        """
        # TODO: Implement conversation history handling
        # Use ChatMessage objects from agent_framework
        raise NotImplementedError("Implement conversation history")

    @abstractmethod
    async def execute(self, input_data: TInput) -> TOutput:
        """
        Execute the agent's main task with typed input/output.

        This is the primary method subclasses must implement.

        Args:
            input_data: Input data specific to the agent type

        Returns:
            Output data specific to the agent type
        """
        raise NotImplementedError

    def get_instructions(self) -> str:
        """Return the agent's system instructions."""
        return self.instructions


class AgentExecutor(Executor, Generic[TInput, TOutput]):
    """
    Wrapper to use a BaseAgent as a workflow Executor.

    This allows agents to be integrated into Microsoft Agent Framework workflows
    using WorkflowBuilder with edges, fan-out, fan-in, etc.

    Usage:
        agent = MyAgent()
        executor = AgentExecutor(agent)
        workflow = WorkflowBuilder().set_start_executor(executor).build()
    """

    def __init__(self, agent: BaseAgent[TInput, TOutput], executor_id: str | None = None):
        """
        Initialize the executor wrapper.

        Args:
            agent: The BaseAgent to wrap
            executor_id: Optional ID for the executor (defaults to agent name)
        """
        super().__init__(id=executor_id or agent.name)
        self.agent = agent

    @handler
    async def handle(self, input_data: TInput, ctx: WorkflowContext[Any]) -> None:
        """
        Handle workflow execution by delegating to the wrapped agent.

        Args:
            input_data: Input from the workflow
            ctx: Workflow context for sending messages/outputs
        """
        result = await self.agent.execute(input_data)
        await ctx.send_message(result)


