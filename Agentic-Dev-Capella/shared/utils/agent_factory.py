"""
shared/utils/agent_factory.py

Factory for creating A2A-enabled agents with consistent configuration.
"""

from typing import Dict, List, Any, Optional, Callable
from google.adk.agents import Agent
from vertexai.preview import reasoning_engines
import yaml

from .agent_base import AgentContext, create_agent_context
from .vertex_a2a_protocol import VertexA2AMessageBus


class AgentFactory:
    """
    Factory for creating agents with A2A communication enabled.
    Handles configuration loading and consistent agent setup.
    """

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        config_path: Optional[str] = None,
        message_bus: Optional[VertexA2AMessageBus] = None
    ):
        """
        Initialize agent factory.

        Args:
            project_id: GCP project ID
            location: Vertex AI location
            config_path: Path to agents_config.yaml
            message_bus: Shared message bus for A2A communication
        """
        self.project_id = project_id
        self.location = location
        self.message_bus = message_bus or VertexA2AMessageBus(
            project_id=project_id,
            topic_name="legacy-modernization-messages"
        )

        # Load configuration
        self.config = {}
        if config_path:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)

        self.global_config = self.config.get('global', {})

    def create_agent(
        self,
        name: str,
        description: str,
        instruction: str,
        tools: List[Callable],
        model: Optional[str] = None,
        agent_config: Optional[Dict[str, Any]] = None
    ) -> Agent:
        """
        Create a Google ADK agent with standard configuration.

        Args:
            name: Agent name
            description: Agent description
            instruction: System instruction for the agent
            tools: List of tool functions
            model: Model to use (defaults to global config)
            agent_config: Additional agent-specific configuration

        Returns:
            Agent instance
        """
        agent_config = agent_config or {}

        # Get model from config hierarchy
        if not model:
            model = agent_config.get('model') or self.global_config.get('model', 'gemini-2.0-flash')

        agent = Agent(
            name=name,
            model=model,
            description=description,
            instruction=instruction,
            tools=tools
        )

        return agent

    def deploy_agent(
        self,
        agent: Agent,
        display_name: str,
        description: str,
        requirements: Optional[List[str]] = None
    ) -> reasoning_engines.ReasoningEngine:
        """
        Deploy agent to Vertex AI Agent Engine.

        Args:
            agent: Agent instance to deploy
            display_name: Display name for the reasoning engine
            description: Description of the agent
            requirements: Python package requirements

        Returns:
            Deployed ReasoningEngine instance
        """
        requirements = requirements or [
            "google-cloud-aiplatform>=1.38.0",
            "vertexai>=1.0.0",
            "google-cloud-pubsub>=2.18.0"
        ]

        reasoning_engine = reasoning_engines.ReasoningEngine.create(
            agent,
            requirements=requirements,
            display_name=display_name,
            description=description
        )

        return reasoning_engine

    def create_agent_context(
        self,
        agent_name: str,
        agent_id: Optional[str] = None,
        vector_search_endpoint: Optional[str] = None
    ) -> AgentContext:
        """
        Create agent context for A2A-enabled agents.

        Args:
            agent_name: Agent name
            agent_id: Agent resource ID (if already deployed)
            vector_search_endpoint: Vector Search endpoint

        Returns:
            AgentContext instance
        """
        return create_agent_context(
            agent_name=agent_name,
            project_id=self.project_id,
            agent_id=agent_id,
            location=self.location,
            vector_search_endpoint=vector_search_endpoint
        )

    def register_agent_for_a2a(
        self,
        agent_id: str,
        agent_name: str,
        message_handler: Callable
    ):
        """
        Register an agent for A2A communication.

        Args:
            agent_id: Agent's Vertex AI resource ID
            agent_name: Agent name
            message_handler: Function to handle incoming messages
        """
        self.message_bus.register_agent(
            agent_id=agent_id,
            agent_name=agent_name,
            message_handler=message_handler
        )

    def get_agent_config(self, stage: str, agent_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific agent.

        Args:
            stage: Stage name (e.g., 'stage0_discovery', 'orchestration')
            agent_name: Agent name within the stage

        Returns:
            Agent configuration dict
        """
        stage_config = self.config.get(stage, {})
        return stage_config.get(agent_name, {})


def create_standard_agent_instruction(
    role: str,
    responsibilities: List[str],
    input_format: str,
    output_format: str,
    quality_standards: Optional[List[str]] = None,
    special_instructions: Optional[str] = None
) -> str:
    """
    Create a standardized agent instruction following best practices.

    Args:
        role: Agent's role description
        responsibilities: List of key responsibilities
        input_format: Description of expected input format
        output_format: Description of expected output format
        quality_standards: List of quality standards to follow
        special_instructions: Additional special instructions

    Returns:
        Formatted instruction string
    """
    instruction_parts = [
        f"You are a {role}.",
        "",
        "Your key responsibilities:",
    ]

    for i, resp in enumerate(responsibilities, 1):
        instruction_parts.append(f"{i}. {resp}")

    instruction_parts.extend([
        "",
        "Input Format:",
        input_format,
        "",
        "Output Format:",
        output_format,
    ])

    if quality_standards:
        instruction_parts.extend([
            "",
            "Quality Standards:",
        ])
        for std in quality_standards:
            instruction_parts.append(f"- {std}")

    if special_instructions:
        instruction_parts.extend([
            "",
            "Special Instructions:",
            special_instructions
        ])

    instruction_parts.extend([
        "",
        "IMPORTANT: Always communicate with other agents using the A2A protocol.",
        "- Send state updates to the orchestrator",
        "- Report errors immediately",
        "- Respond to validation requests promptly",
        "- Provide detailed feedback on failures"
    ])

    return "\n".join(instruction_parts)


# Convenience function for quick agent creation
def quick_create_agent(
    name: str,
    role: str,
    responsibilities: List[str],
    tools: List[Callable],
    project_id: str,
    model: str = "gemini-2.0-flash"
) -> Agent:
    """
    Quickly create an agent with minimal configuration.

    Args:
        name: Agent name
        role: Agent role description
        responsibilities: List of responsibilities
        tools: List of tool functions
        project_id: GCP project ID
        model: Model to use

    Returns:
        Agent instance
    """
    factory = AgentFactory(project_id=project_id)

    instruction = create_standard_agent_instruction(
        role=role,
        responsibilities=responsibilities,
        input_format="Task assignment via A2A protocol with task_id, context, and specifications",
        output_format="Completion message via A2A protocol with results and status"
    )

    return factory.create_agent(
        name=name,
        description=f"{role} agent for legacy modernization",
        instruction=instruction,
        tools=tools,
        model=model
    )
