"""
shared/utils/agent_base.py

Base classes and utilities for creating A2A-enabled agents.
Provides standard patterns for agent communication and message handling.
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json

from .vertex_a2a_protocol import (
    A2AMessage,
    A2AMessageType,
    VertexA2AMessageBus,
    A2AProtocolHelper,
    A2AAgentWrapper
)


@dataclass
class AgentContext:
    """Context information for an agent."""
    agent_id: str
    agent_name: str
    project_id: str
    location: str = "us-central1"
    model: str = "gemini-2.0-flash"
    vector_search_endpoint: Optional[str] = None


class A2AEnabledAgent(ABC):
    """
    Base class for agents with A2A communication capabilities.

    All agents should inherit from this class to ensure consistent
    message handling and communication patterns.
    """

    def __init__(
        self,
        context: AgentContext,
        message_bus: Optional[VertexA2AMessageBus] = None
    ):
        """
        Initialize A2A-enabled agent.

        Args:
            context: Agent context information
            message_bus: Shared message bus for A2A communication
        """
        self.context = context
        self.agent_id = context.agent_id
        self.agent_name = context.agent_name
        self.project_id = context.project_id

        # A2A communication
        self.message_bus = message_bus
        self.a2a_wrapper: Optional[A2AAgentWrapper] = None

        # Message handlers registry
        self._message_handlers: Dict[A2AMessageType, Callable] = {}
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default message handlers."""
        self._message_handlers[A2AMessageType.TASK_ASSIGNMENT] = self.handle_task_assignment
        self._message_handlers[A2AMessageType.VALIDATION_REQUEST] = self.handle_validation_request
        self._message_handlers[A2AMessageType.QUERY_REQUEST] = self.handle_query_request
        self._message_handlers[A2AMessageType.STATE_UPDATE] = self.handle_state_update
        self._message_handlers[A2AMessageType.ERROR_REPORT] = self.handle_error_report

    def initialize_a2a(self, message_bus: VertexA2AMessageBus):
        """
        Initialize A2A communication wrapper.

        Args:
            message_bus: Message bus instance
        """
        self.message_bus = message_bus
        self.a2a_wrapper = A2AAgentWrapper(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            project_id=self.project_id,
            message_bus=message_bus
        )

        # Register handlers
        for msg_type, handler in self._message_handlers.items():
            self.a2a_wrapper.register_handler(msg_type, handler)

    def start_listening(self):
        """Start listening for A2A messages."""
        if self.a2a_wrapper:
            self.a2a_wrapper.start_listening()
        else:
            raise RuntimeError("A2A not initialized. Call initialize_a2a() first.")

    def stop_listening(self):
        """Stop listening for A2A messages."""
        if self.a2a_wrapper:
            self.a2a_wrapper.stop_listening()

    def send_message(
        self,
        recipient_id: str,
        recipient_name: str,
        message_type: A2AMessageType,
        payload: Dict[str, Any],
        requires_response: bool = False,
        priority: int = 5
    ) -> str:
        """
        Send A2A message to another agent.

        Args:
            recipient_id: Recipient agent's resource ID
            recipient_name: Recipient agent's name
            message_type: Type of message
            payload: Message payload
            requires_response: Whether response is required
            priority: Message priority (1=highest, 10=lowest)

        Returns:
            Message ID
        """
        if not self.a2a_wrapper:
            raise RuntimeError("A2A not initialized. Call initialize_a2a() first.")

        message = A2AMessage(
            message_type=message_type,
            sender_agent_id=self.agent_id,
            sender_agent_name=self.agent_name,
            recipient_agent_id=recipient_id,
            recipient_agent_name=recipient_name,
            payload=payload,
            requires_response=requires_response,
            priority=priority
        )

        return self.a2a_wrapper.send_message(message)

    def send_and_wait(
        self,
        recipient_id: str,
        recipient_name: str,
        message_type: A2AMessageType,
        payload: Dict[str, Any],
        timeout: int = 60
    ) -> Optional[Dict[str, Any]]:
        """
        Send message and wait for response.

        Args:
            recipient_id: Recipient agent's resource ID
            recipient_name: Recipient agent's name
            message_type: Type of message
            payload: Message payload
            timeout: Timeout in seconds

        Returns:
            Response payload
        """
        if not self.a2a_wrapper:
            raise RuntimeError("A2A not initialized. Call initialize_a2a() first.")

        message = A2AMessage(
            message_type=message_type,
            sender_agent_id=self.agent_id,
            sender_agent_name=self.agent_name,
            recipient_agent_id=recipient_id,
            recipient_agent_name=recipient_name,
            payload=payload,
            requires_response=True
        )

        return self.a2a_wrapper.send_and_wait(message, timeout)

    # Abstract methods to be implemented by subclasses

    @abstractmethod
    def handle_task_assignment(self, message: A2AMessage) -> Dict[str, Any]:
        """
        Handle task assignment messages.

        Args:
            message: Incoming A2A message

        Returns:
            Response dict
        """
        pass

    def handle_validation_request(self, message: A2AMessage) -> Dict[str, Any]:
        """
        Handle validation request messages.

        Args:
            message: Incoming A2A message

        Returns:
            Validation result
        """
        return {
            "status": "not_implemented",
            "message": f"{self.agent_name} does not handle validation requests"
        }

    def handle_query_request(self, message: A2AMessage) -> Dict[str, Any]:
        """
        Handle query request messages.

        Args:
            message: Incoming A2A message

        Returns:
            Query response
        """
        return {
            "status": "not_implemented",
            "message": f"{self.agent_name} does not handle query requests"
        }

    def handle_state_update(self, message: A2AMessage) -> Dict[str, Any]:
        """
        Handle state update messages.

        Args:
            message: Incoming A2A message

        Returns:
            Acknowledgment
        """
        return {
            "status": "acknowledged",
            "message": "State update received"
        }

    def handle_error_report(self, message: A2AMessage) -> Dict[str, Any]:
        """
        Handle error report messages.

        Args:
            message: Incoming A2A message

        Returns:
            Acknowledgment
        """
        error_info = message.payload
        print(f"[{self.agent_name}] Error reported: {error_info}")
        return {
            "status": "acknowledged",
            "message": "Error report received"
        }

    # Utility methods

    def report_error(
        self,
        orchestrator_id: str,
        task_id: str,
        error_message: str,
        error_details: Dict[str, Any]
    ):
        """
        Report an error to the orchestrator.

        Args:
            orchestrator_id: Orchestrator agent's resource ID
            task_id: Task identifier
            error_message: Error message
            error_details: Additional error details
        """
        self.send_message(
            recipient_id=orchestrator_id,
            recipient_name="orchestrator_agent",
            message_type=A2AMessageType.ERROR_REPORT,
            payload={
                "task_id": task_id,
                "error_message": error_message,
                "error_details": error_details,
                "agent_name": self.agent_name
            },
            priority=1  # High priority
        )

    def update_task_state(
        self,
        orchestrator_id: str,
        task_id: str,
        old_status: str,
        new_status: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Send task state update to orchestrator.

        Args:
            orchestrator_id: Orchestrator agent's resource ID
            task_id: Task identifier
            old_status: Previous status
            new_status: New status
            metadata: Additional metadata
        """
        message = A2AProtocolHelper.create_state_update(
            sender_id=self.agent_id,
            sender_name=self.agent_name,
            orchestrator_id=orchestrator_id,
            task_id=task_id,
            old_status=old_status,
            new_status=new_status,
            metadata=metadata or {}
        )

        if self.a2a_wrapper:
            self.a2a_wrapper.send_message(message)


class ValidatorAgent(A2AEnabledAgent):
    """
    Base class for validator agents.

    Validators receive artifacts, check them against criteria,
    and return pass/fail results with feedback.
    """

    def handle_task_assignment(self, message: A2AMessage) -> Dict[str, Any]:
        """
        Validators don't typically receive task assignments.
        They receive validation requests instead.
        """
        return {
            "status": "error",
            "message": "Validators should receive VALIDATION_REQUEST, not TASK_ASSIGNMENT"
        }

    def handle_validation_request(self, message: A2AMessage) -> Dict[str, Any]:
        """
        Handle validation request.

        Args:
            message: Validation request message

        Returns:
            Validation result
        """
        payload = message.payload
        task_id = payload.get("task_id")
        artifact = payload.get("artifact")
        criteria = payload.get("validation_criteria", [])

        # Perform validation (implemented by subclass)
        validation_result = self.validate(artifact, criteria)

        # Send validation result back
        result_message = A2AProtocolHelper.create_validation_result(
            validator_id=self.agent_id,
            validator_name=self.agent_name,
            recipient_id=message.sender_agent_id,
            recipient_name=message.sender_agent_name,
            task_id=task_id,
            passed=validation_result["passed"],
            issues=validation_result.get("issues", []),
            feedback=validation_result.get("feedback"),
            correlation_id=message.correlation_id
        )

        if self.a2a_wrapper:
            self.a2a_wrapper.send_message(result_message)

        return validation_result

    @abstractmethod
    def validate(
        self,
        artifact: Any,
        criteria: List[str]
    ) -> Dict[str, Any]:
        """
        Validate an artifact against criteria.

        Args:
            artifact: Artifact to validate
            criteria: Validation criteria

        Returns:
            Validation result with passed, issues, feedback
        """
        pass


def create_agent_context(
    agent_name: str,
    project_id: str,
    agent_id: Optional[str] = None,
    location: str = "us-central1",
    model: str = "gemini-2.0-flash",
    vector_search_endpoint: Optional[str] = None
) -> AgentContext:
    """
    Create agent context for initialization.

    Args:
        agent_name: Agent name
        project_id: GCP project ID
        agent_id: Agent resource ID (if already deployed)
        location: Vertex AI location
        model: Model to use
        vector_search_endpoint: Vector Search endpoint

    Returns:
        AgentContext instance
    """
    if not agent_id:
        agent_id = f"projects/{project_id}/locations/{location}/agents/{agent_name}"

    return AgentContext(
        agent_id=agent_id,
        agent_name=agent_name,
        project_id=project_id,
        location=location,
        model=model,
        vector_search_endpoint=vector_search_endpoint
    )
