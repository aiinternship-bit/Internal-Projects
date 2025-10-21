"""
shared/utils/a2a_integration.py

Integration utilities to seamlessly embed A2A communication into agents.
Provides decorators and wrappers to make agents A2A-aware.
"""

from typing import Dict, List, Any, Optional, Callable
from functools import wraps
import json
import time

from .vertex_a2a_protocol import (
    A2AMessage,
    A2AMessageType,
    VertexA2AMessageBus,
    A2AProtocolHelper
)
from .agent_base import AgentContext


class A2AIntegration:
    """
    Integration layer that adds A2A communication to existing agents.

    This class wraps agent tool functions to automatically:
    - Send state updates to orchestrator
    - Report errors
    - Track task progress
    - Handle A2A message routing
    """

    def __init__(
        self,
        agent_context: AgentContext,
        message_bus: VertexA2AMessageBus,
        orchestrator_id: str
    ):
        """
        Initialize A2A integration.

        Args:
            agent_context: Agent context information
            message_bus: Message bus for A2A communication
            orchestrator_id: Orchestrator agent's resource ID
        """
        self.context = agent_context
        self.message_bus = message_bus
        self.orchestrator_id = orchestrator_id

        # Track current task
        self.current_task_id: Optional[str] = None
        self.task_start_time: Optional[float] = None

    def send_task_update(
        self,
        task_id: str,
        old_status: str,
        new_status: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Send task state update to orchestrator."""
        message = A2AProtocolHelper.create_state_update(
            sender_id=self.context.agent_id,
            sender_name=self.context.agent_name,
            orchestrator_id=self.orchestrator_id,
            task_id=task_id,
            old_status=old_status,
            new_status=new_status,
            metadata=metadata or {}
        )

        self.message_bus.publish_message(message)

    def send_error_report(
        self,
        task_id: str,
        error_message: str,
        error_details: Dict[str, Any]
    ):
        """Report error to orchestrator."""
        message = A2AMessage(
            message_type=A2AMessageType.ERROR_REPORT,
            sender_agent_id=self.context.agent_id,
            sender_agent_name=self.context.agent_name,
            recipient_agent_id=self.orchestrator_id,
            recipient_agent_name="orchestrator_agent",
            payload={
                "task_id": task_id,
                "error_message": error_message,
                "error_details": error_details,
                "agent_name": self.context.agent_name
            },
            priority=1  # High priority
        )

        self.message_bus.publish_message(message)

    def send_validation_request(
        self,
        validator_id: str,
        validator_name: str,
        task_id: str,
        artifact: Dict[str, Any],
        criteria: List[str]
    ) -> Dict[str, Any]:
        """
        Send validation request and wait for response.

        Args:
            validator_id: Validator agent's resource ID
            validator_name: Validator agent's name
            task_id: Task identifier
            artifact: Artifact to validate
            criteria: Validation criteria

        Returns:
            Validation result
        """
        message = A2AProtocolHelper.create_validation_request(
            sender_id=self.context.agent_id,
            sender_name=self.context.agent_name,
            validator_id=validator_id,
            validator_name=validator_name,
            artifact={
                "task_id": task_id,
                "type": artifact.get("type"),
                "content": artifact.get("content"),
                "criteria": criteria
            }
        )

        # Send and wait for response
        response = self.message_bus.send_and_wait(message, timeout=120)
        return response or {"status": "timeout", "passed": False}

    def send_task_assignment(
        self,
        recipient_id: str,
        recipient_name: str,
        task_data: Dict[str, Any]
    ) -> str:
        """
        Send task assignment to another agent.

        Args:
            recipient_id: Recipient agent's resource ID
            recipient_name: Recipient agent's name
            task_data: Task data

        Returns:
            Message ID
        """
        message = A2AProtocolHelper.create_task_assignment(
            sender_id=self.context.agent_id,
            sender_name=self.context.agent_name,
            recipient_id=recipient_id,
            recipient_name=recipient_name,
            task_data=task_data
        )

        return self.message_bus.publish_message(message)

    def with_task_tracking(self, tool_func: Callable) -> Callable:
        """
        Decorator to automatically track task execution.

        Automatically:
        - Sends task start update
        - Tracks execution time
        - Sends task completion update
        - Reports errors

        Usage:
            @a2a_integration.with_task_tracking
            def my_tool_function(task_id: str, **kwargs):
                # Tool implementation
                return result
        """
        @wraps(tool_func)
        def wrapper(*args, **kwargs):
            # Extract task_id from kwargs
            task_id = kwargs.get('task_id') or (args[0] if args else None)

            if not task_id:
                # No task tracking if no task_id
                return tool_func(*args, **kwargs)

            # Track task start
            self.current_task_id = task_id
            self.task_start_time = time.time()

            self.send_task_update(
                task_id=task_id,
                old_status="pending",
                new_status="in_progress",
                metadata={
                    "agent": self.context.agent_name,
                    "tool": tool_func.__name__
                }
            )

            try:
                # Execute tool
                result = tool_func(*args, **kwargs)

                # Track completion
                execution_time = time.time() - self.task_start_time

                self.send_task_update(
                    task_id=task_id,
                    old_status="in_progress",
                    new_status="completed",
                    metadata={
                        "agent": self.context.agent_name,
                        "tool": tool_func.__name__,
                        "execution_time_seconds": execution_time,
                        "result_status": result.get("status") if isinstance(result, dict) else "success"
                    }
                )

                return result

            except Exception as e:
                # Report error
                execution_time = time.time() - self.task_start_time

                self.send_error_report(
                    task_id=task_id,
                    error_message=str(e),
                    error_details={
                        "agent": self.context.agent_name,
                        "tool": tool_func.__name__,
                        "execution_time_seconds": execution_time,
                        "error_type": type(e).__name__
                    }
                )

                self.send_task_update(
                    task_id=task_id,
                    old_status="in_progress",
                    new_status="failed",
                    metadata={
                        "agent": self.context.agent_name,
                        "error": str(e)
                    }
                )

                raise

        return wrapper


def create_a2a_enabled_tool(
    tool_func: Callable,
    agent_context: AgentContext,
    message_bus: VertexA2AMessageBus,
    orchestrator_id: str,
    auto_track: bool = True
) -> Callable:
    """
    Convert a regular tool function to an A2A-enabled tool.

    Args:
        tool_func: Original tool function
        agent_context: Agent context
        message_bus: Message bus
        orchestrator_id: Orchestrator ID
        auto_track: Automatically track task execution

    Returns:
        A2A-enabled tool function
    """
    integration = A2AIntegration(agent_context, message_bus, orchestrator_id)

    if auto_track:
        return integration.with_task_tracking(tool_func)
    else:
        return tool_func


class ValidationLoopHandler:
    """
    Handles validation loops with automatic retry and escalation.

    Implements the validation pattern:
    1. Submit artifact for validation
    2. If rejected, incorporate feedback and retry
    3. After N rejections, escalate to escalation agent
    """

    def __init__(
        self,
        a2a_integration: A2AIntegration,
        max_retries: int = 3,
        escalation_agent_id: str = None
    ):
        """
        Initialize validation loop handler.

        Args:
            a2a_integration: A2A integration instance
            max_retries: Maximum retry attempts before escalation
            escalation_agent_id: Escalation agent's resource ID
        """
        self.a2a = a2a_integration
        self.max_retries = max_retries
        self.escalation_agent_id = escalation_agent_id

    def validate_with_retry(
        self,
        task_id: str,
        validator_id: str,
        validator_name: str,
        artifact_generator: Callable[[Optional[str]], Dict[str, Any]],
        validation_criteria: List[str]
    ) -> Dict[str, Any]:
        """
        Validate artifact with automatic retry on failure.

        Args:
            task_id: Task identifier
            validator_id: Validator agent's resource ID
            validator_name: Validator agent's name
            artifact_generator: Function that generates artifact (accepts feedback)
            validation_criteria: Validation criteria

        Returns:
            Final validation result with artifact
        """
        retry_count = 0
        feedback = None
        rejection_history = []

        while retry_count <= self.max_retries:
            # Generate artifact (incorporating feedback if available)
            artifact = artifact_generator(feedback)

            # Send for validation
            validation_result = self.a2a.send_validation_request(
                validator_id=validator_id,
                validator_name=validator_name,
                task_id=task_id,
                artifact=artifact,
                criteria=validation_criteria
            )

            # Check result
            if validation_result.get("passed"):
                return {
                    "status": "validated",
                    "artifact": artifact,
                    "retry_count": retry_count,
                    "validation_result": validation_result
                }

            # Validation failed
            retry_count += 1
            feedback = validation_result.get("feedback")
            issues = validation_result.get("issues", [])

            rejection_history.append({
                "retry": retry_count,
                "issues": issues,
                "feedback": feedback
            })

            print(f"[{self.a2a.context.agent_name}] Validation failed (attempt {retry_count}/{self.max_retries})")
            print(f"  Issues: {issues}")
            print(f"  Feedback: {feedback}")

            if retry_count >= self.max_retries:
                # Max retries reached - escalate
                if self.escalation_agent_id:
                    self._escalate_to_human(
                        task_id=task_id,
                        rejection_history=rejection_history,
                        last_artifact=artifact
                    )

                return {
                    "status": "escalated",
                    "retry_count": retry_count,
                    "rejection_history": rejection_history,
                    "last_artifact": artifact
                }

        return {
            "status": "failed",
            "message": "Validation loop exhausted",
            "rejection_history": rejection_history
        }

    def _escalate_to_human(
        self,
        task_id: str,
        rejection_history: List[Dict[str, Any]],
        last_artifact: Dict[str, Any]
    ):
        """Escalate to escalation agent for human review."""
        escalation_message = A2AProtocolHelper.create_escalation_request(
            sender_id=self.a2a.context.agent_id,
            sender_name=self.a2a.context.agent_name,
            task_id=task_id,
            reason="validation_deadlock",
            rejection_count=len(rejection_history),
            context={
                "rejection_history": rejection_history,
                "last_artifact": last_artifact
            }
        )

        self.a2a.message_bus.publish_message(escalation_message)

        print(f"[{self.a2a.context.agent_name}] Escalated task {task_id} after {len(rejection_history)} rejections")


# Convenience functions

def create_a2a_integration(
    agent_name: str,
    project_id: str,
    message_bus: VertexA2AMessageBus,
    orchestrator_id: str,
    agent_id: Optional[str] = None,
    location: str = "us-central1"
) -> A2AIntegration:
    """
    Quickly create A2A integration for an agent.

    Args:
        agent_name: Agent name
        project_id: GCP project ID
        message_bus: Message bus
        orchestrator_id: Orchestrator agent's resource ID
        agent_id: Agent's resource ID (auto-generated if not provided)
        location: Vertex AI location

    Returns:
        A2AIntegration instance
    """
    if not agent_id:
        agent_id = f"projects/{project_id}/locations/{location}/agents/{agent_name}"

    context = AgentContext(
        agent_id=agent_id,
        agent_name=agent_name,
        project_id=project_id,
        location=location
    )

    return A2AIntegration(context, message_bus, orchestrator_id)
