"""
tests/a2a_tests/test_multi_agent_workflows.py

End-to-end tests for multi-agent communication workflows.
Tests complete workflows like orchestrator→developer→validator→orchestrator.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any, List
import time

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.utils.vertex_a2a_protocol import (
    A2AMessageType,
    A2AMessage,
    A2AProtocolHelper
)
from shared.utils.a2a_integration import A2AIntegration
from shared.utils.agent_base import AgentContext, A2AEnabledAgent


class MockDeveloperAgent(A2AEnabledAgent):
    """Mock developer agent for testing."""

    def __init__(self, context, message_bus):
        super().__init__(context, message_bus)
        self.tasks_received = []
        self.a2a = A2AIntegration(context, message_bus, "orchestrator_id")

    def handle_task_assignment(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle incoming task assignment."""
        self.tasks_received.append(message)
        task_id = message.payload.get("task_id")

        # Simulate code generation
        code = """
def process_payment(amount: float, currency: str) -> dict:
    if amount <= 0:
        raise ValueError("Amount must be positive")
    return {"status": "success", "amount": amount, "currency": currency}
"""

        # Send for validation
        validation_result = self.a2a.send_validation_request(
            validator_id="validator_id",
            validator_name="code_validator",
            task_id=task_id,
            artifact={"code": code},
            validation_criteria=["correctness", "security"]
        )

        # Send completion to orchestrator
        return {
            "status": "success",
            "code": code,
            "validation_result": validation_result
        }


class MockValidatorAgent(A2AEnabledAgent):
    """Mock validator agent for testing."""

    def __init__(self, context, message_bus):
        super().__init__(context, message_bus)
        self.validation_requests = []

    def handle_validation_request(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle validation request."""
        self.validation_requests.append(message)

        artifact = message.payload.get("artifact", {})
        code = artifact.get("code", "")

        # Simple validation logic
        passed = "raise ValueError" in code  # Check error handling
        issues = [] if passed else ["Missing error handling"]
        feedback = "Good code" if passed else "Add error handling"

        # Send validation result back
        result = A2AProtocolHelper.create_validation_result(
            sender_id=self.context.agent_id,
            sender_name=self.context.agent_name,
            recipient_id=message.sender_agent_id,
            recipient_name=message.sender_agent_name,
            task_id=message.payload.get("task_id"),
            passed=passed,
            issues=issues,
            feedback=feedback,
            correlation_id=message.correlation_id
        )

        self.send_message(
            recipient_id=message.sender_agent_id,
            recipient_name=message.sender_agent_name,
            message_type=A2AMessageType.VALIDATION_RESULT,
            payload=result.payload
        )

        return {"passed": passed, "issues": issues}


class MockOrchestratorAgent(A2AEnabledAgent):
    """Mock orchestrator agent for testing."""

    def __init__(self, context, message_bus):
        super().__init__(context, message_bus)
        self.task_completions = []
        self.state_updates = []

    def handle_task_assignment(self, message: A2AMessage) -> Dict[str, Any]:
        """Orchestrator doesn't handle task assignments."""
        pass

    def handle_task_completion(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle task completion from agents."""
        self.task_completions.append(message)
        return {"acknowledged": True}

    def handle_state_update(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle state updates from agents."""
        self.state_updates.append(message)
        return {"acknowledged": True}

    def assign_task(self, developer_id: str, task_data: Dict[str, Any]):
        """Assign task to developer."""
        message = A2AProtocolHelper.create_task_assignment(
            sender_id=self.context.agent_id,
            sender_name=self.context.agent_name,
            recipient_id=developer_id,
            recipient_name="developer_agent",
            task_data=task_data
        )

        self.send_message(
            recipient_id=developer_id,
            recipient_name="developer_agent",
            message_type=A2AMessageType.TASK_ASSIGNMENT,
            payload=message.payload
        )


class TestMultiAgentWorkflows(unittest.TestCase):
    """Test multi-agent communication workflows."""

    def setUp(self):
        """Set up mock agents and message bus."""
        # Create mock message bus
        self.message_bus = MagicMock()
        self.message_queue = []  # Simulate message queue

        # Mock publish_message to add to queue
        def mock_publish(message):
            self.message_queue.append(message)
            return f"msg-{len(self.message_queue)}"

        self.message_bus.publish_message = mock_publish

        # Create agent contexts
        self.orchestrator_context = AgentContext(
            agent_id="orchestrator_id",
            agent_name="orchestrator_agent",
            project_id="test-project",
            location="us-central1"
        )

        self.developer_context = AgentContext(
            agent_id="developer_id",
            agent_name="developer_agent",
            project_id="test-project",
            location="us-central1"
        )

        self.validator_context = AgentContext(
            agent_id="validator_id",
            agent_name="code_validator",
            project_id="test-project",
            location="us-central1"
        )

        # Create mock agents
        self.orchestrator = MockOrchestratorAgent(
            self.orchestrator_context,
            self.message_bus
        )

        self.developer = MockDeveloperAgent(
            self.developer_context,
            self.message_bus
        )

        self.validator = MockValidatorAgent(
            self.validator_context,
            self.message_bus
        )

    def test_orchestrator_to_developer_task_assignment(self):
        """Test task assignment from orchestrator to developer."""
        task_data = {
            "task_id": "dev_001",
            "component_id": "payment_processor",
            "architecture_spec": {
                "language": "python",
                "framework": "fastapi"
            }
        }

        # Orchestrator assigns task
        self.orchestrator.assign_task(
            developer_id=self.developer_context.agent_id,
            task_data=task_data
        )

        # Verify message was published
        self.assertEqual(len(self.message_queue), 1)

        # Verify message content
        message = self.message_queue[0]
        self.assertEqual(message.message_type, A2AMessageType.TASK_ASSIGNMENT)
        self.assertEqual(message.recipient_agent_id, self.developer_context.agent_id)
        self.assertEqual(message.payload["task_id"], "dev_001")

        # Developer handles the task
        self.developer.handle_task_assignment(message)

        # Verify developer received the task
        self.assertEqual(len(self.developer.tasks_received), 1)
        self.assertEqual(
            self.developer.tasks_received[0].payload["task_id"],
            "dev_001"
        )

    def test_developer_to_validator_validation_request(self):
        """Test validation request from developer to validator."""
        # Mock send_and_wait to return validation result
        def mock_send_and_wait(message, timeout=120):
            # Validator processes the request
            validation_result = self.validator.handle_validation_request(message)

            # Return validation result message
            return A2AProtocolHelper.create_validation_result(
                sender_id=self.validator_context.agent_id,
                sender_name=self.validator_context.agent_name,
                recipient_id=self.developer_context.agent_id,
                recipient_name=self.developer_context.agent_name,
                task_id=message.payload.get("task_id"),
                passed=validation_result["passed"],
                issues=validation_result["issues"],
                feedback="Validation complete",
                correlation_id=message.correlation_id
            )

        self.message_bus.send_and_wait = mock_send_and_wait

        # Task assignment to developer
        task_message = A2AProtocolHelper.create_task_assignment(
            sender_id=self.orchestrator_context.agent_id,
            sender_name=self.orchestrator_context.agent_name,
            recipient_id=self.developer_context.agent_id,
            recipient_name=self.developer_context.agent_name,
            task_data={
                "task_id": "dev_002",
                "component_id": "payment_processor"
            }
        )

        # Developer handles task (will request validation)
        result = self.developer.handle_task_assignment(task_message)

        # Verify validation was requested
        self.assertEqual(len(self.validator.validation_requests), 1)

        validation_request = self.validator.validation_requests[0]
        self.assertEqual(validation_request.message_type, A2AMessageType.VALIDATION_REQUEST)
        self.assertIn("code", validation_request.payload["artifact"])

        # Verify validation passed
        self.assertTrue(result["validation_result"]["passed"])

    def test_full_workflow_orchestrator_to_developer_to_validator(self):
        """Test complete workflow: Orchestrator → Developer → Validator → Developer → Orchestrator."""
        # Mock send_and_wait for validation
        def mock_send_and_wait(message, timeout=120):
            if message.message_type == A2AMessageType.VALIDATION_REQUEST:
                validation_result = self.validator.handle_validation_request(message)
                return A2AProtocolHelper.create_validation_result(
                    sender_id=self.validator_context.agent_id,
                    sender_name=self.validator_context.agent_name,
                    recipient_id=message.sender_agent_id,
                    recipient_name=message.sender_agent_name,
                    task_id=message.payload.get("task_id"),
                    passed=validation_result["passed"],
                    issues=validation_result["issues"],
                    feedback="Validation complete",
                    correlation_id=message.correlation_id
                )
            return None

        self.message_bus.send_and_wait = mock_send_and_wait

        # Step 1: Orchestrator assigns task to developer
        task_data = {
            "task_id": "dev_003",
            "component_id": "payment_processor",
            "architecture_spec": {"language": "python"}
        }

        self.orchestrator.assign_task(
            developer_id=self.developer_context.agent_id,
            task_data=task_data
        )

        # Step 2: Developer receives and processes task
        task_message = self.message_queue[-1]
        result = self.developer.handle_task_assignment(task_message)

        # Step 3: Developer sends validation request to validator
        # (handled internally in developer.handle_task_assignment)

        # Step 4: Validator validates and returns result
        # (mocked in send_and_wait)

        # Step 5: Developer completes task and notifies orchestrator
        completion_message = A2AProtocolHelper.create_task_completion(
            sender_id=self.developer_context.agent_id,
            sender_name=self.developer_context.agent_name,
            recipient_id=self.orchestrator_context.agent_id,
            recipient_name=self.orchestrator_context.agent_name,
            task_id="dev_003",
            result=result,
            execution_time_seconds=10.5
        )

        self.orchestrator.handle_task_completion(completion_message)

        # Verify complete workflow
        self.assertEqual(len(self.developer.tasks_received), 1)  # Developer received task
        self.assertEqual(len(self.validator.validation_requests), 1)  # Validator received request
        self.assertEqual(len(self.orchestrator.task_completions), 1)  # Orchestrator received completion

        # Verify final result
        self.assertEqual(result["status"], "success")
        self.assertIn("code", result)

    def test_state_update_tracking(self):
        """Test state updates are sent during task execution."""
        state_updates = []

        def mock_publish(message):
            if message.message_type == A2AMessageType.STATE_UPDATE:
                state_updates.append(message)
            return f"msg-{len(self.message_queue)}"

        self.message_bus.publish_message = mock_publish

        # Create A2A integration with task tracking
        a2a = A2AIntegration(
            agent_context=self.developer_context,
            message_bus=self.message_bus,
            orchestrator_id=self.orchestrator_context.agent_id
        )

        # Define tool with task tracking
        @a2a.with_task_tracking
        def implement_component(task_id: str, component_id: str) -> Dict[str, Any]:
            return {"status": "success", "component_id": component_id}

        # Execute tool
        implement_component(task_id="dev_004", component_id="payment_processor")

        # Verify state updates were sent
        self.assertGreaterEqual(len(state_updates), 2)

        # Check first update (pending → in_progress)
        first_update = state_updates[0]
        self.assertEqual(first_update.payload["old_status"], "pending")
        self.assertEqual(first_update.payload["new_status"], "in_progress")

        # Check last update (in_progress → completed)
        last_update = state_updates[-1]
        self.assertEqual(last_update.payload["old_status"], "in_progress")
        self.assertEqual(last_update.payload["new_status"], "completed")

    def test_error_reporting_workflow(self):
        """Test error reporting from agent to orchestrator."""
        error_reports = []

        def mock_publish(message):
            if message.message_type == A2AMessageType.ERROR_REPORT:
                error_reports.append(message)
            self.message_queue.append(message)
            return f"msg-{len(self.message_queue)}"

        self.message_bus.publish_message = mock_publish

        # Create A2A integration
        a2a = A2AIntegration(
            agent_context=self.developer_context,
            message_bus=self.message_bus,
            orchestrator_id=self.orchestrator_context.agent_id
        )

        # Define failing tool
        @a2a.with_task_tracking
        def failing_tool(task_id: str) -> Dict[str, Any]:
            raise RuntimeError("Database connection failed")

        # Execute failing tool
        with self.assertRaises(RuntimeError):
            failing_tool(task_id="dev_005")

        # Verify error report was sent
        self.assertEqual(len(error_reports), 1)

        error_report = error_reports[0]
        self.assertEqual(error_report.message_type, A2AMessageType.ERROR_REPORT)
        self.assertEqual(error_report.recipient_agent_id, self.orchestrator_context.agent_id)
        self.assertIn("Database connection failed", error_report.payload["error_message"])
        self.assertEqual(error_report.priority, 1)  # High priority

    def test_query_request_response_workflow(self):
        """Test query request-response between agents."""
        # Mock Domain Expert Agent
        class MockDomainExpertAgent(A2AEnabledAgent):
            def handle_query_request(self, message: A2AMessage) -> Dict[str, Any]:
                query = message.payload.get("query")

                # Send response
                response = A2AProtocolHelper.create_query_response(
                    sender_id=self.context.agent_id,
                    sender_name=self.context.agent_name,
                    recipient_id=message.sender_agent_id,
                    recipient_name=message.sender_agent_name,
                    query_result={
                        "business_rules": ["Validate amount > 0", "Check card expiry"],
                        "constraints": ["PCI-DSS compliance required"]
                    },
                    correlation_id=message.correlation_id
                )

                self.send_message(
                    recipient_id=message.sender_agent_id,
                    recipient_name=message.sender_agent_name,
                    message_type=A2AMessageType.QUERY_RESPONSE,
                    payload=response.payload
                )

                return response.payload["query_result"]

        domain_expert_context = AgentContext(
            agent_id="domain_expert_id",
            agent_name="domain_expert",
            project_id="test-project",
            location="us-central1"
        )

        domain_expert = MockDomainExpertAgent(domain_expert_context, self.message_bus)

        # Mock send_and_wait to simulate query response
        def mock_send_and_wait(message, timeout=60):
            if message.message_type == A2AMessageType.QUERY_REQUEST:
                return domain_expert.handle_query_request(message)
            return None

        self.message_bus.send_and_wait = mock_send_and_wait

        # Developer sends query to domain expert
        a2a = A2AIntegration(
            agent_context=self.developer_context,
            message_bus=self.message_bus,
            orchestrator_id=self.orchestrator_context.agent_id
        )

        query_message = A2AProtocolHelper.create_query_request(
            sender_id=self.developer_context.agent_id,
            sender_name=self.developer_context.agent_name,
            recipient_id=domain_expert_context.agent_id,
            recipient_name=domain_expert_context.agent_name,
            query="What are the business rules for payment processing?",
            context={"component_id": "payment_processor"}
        )

        response = self.message_bus.send_and_wait(query_message, timeout=60)

        # Verify response
        self.assertIn("business_rules", response.payload["query_result"])
        self.assertEqual(len(response.payload["query_result"]["business_rules"]), 2)
        self.assertEqual(response.correlation_id, query_message.correlation_id)

    def test_escalation_workflow(self):
        """Test escalation workflow after max retries."""
        escalation_messages = []

        def mock_publish(message):
            if message.message_type == A2AMessageType.ESCALATION_REQUEST:
                escalation_messages.append(message)
            self.message_queue.append(message)
            return f"msg-{len(self.message_queue)}"

        self.message_bus.publish_message = mock_publish

        # Mock validator that always fails
        def mock_send_and_wait(message, timeout=120):
            if message.message_type == A2AMessageType.VALIDATION_REQUEST:
                return A2AProtocolHelper.create_validation_result(
                    sender_id=self.validator_context.agent_id,
                    sender_name=self.validator_context.agent_name,
                    recipient_id=message.sender_agent_id,
                    recipient_name=message.sender_agent_name,
                    task_id=message.payload.get("task_id"),
                    passed=False,
                    issues=["Persistent issue"],
                    feedback="Still not fixed",
                    correlation_id=message.correlation_id
                )
            return None

        self.message_bus.send_and_wait = mock_send_and_wait

        # Create validation handler
        from shared.utils.a2a_integration import ValidationLoopHandler

        a2a = A2AIntegration(
            agent_context=self.developer_context,
            message_bus=self.message_bus,
            orchestrator_id=self.orchestrator_context.agent_id
        )

        validation_handler = ValidationLoopHandler(
            a2a_integration=a2a,
            max_retries=3,
            escalation_agent_id="escalation_id"
        )

        # Try validation (will fail and escalate)
        def artifact_generator(feedback=None):
            return {"code": "def process(): pass"}  # Never improves

        result = validation_handler.validate_with_retry(
            task_id="dev_006",
            validator_id=self.validator_context.agent_id,
            validator_name=self.validator_context.agent_name,
            artifact_generator=artifact_generator,
            validation_criteria=["correctness"]
        )

        # Verify escalation
        self.assertEqual(result["status"], "escalated")
        self.assertEqual(len(escalation_messages), 1)

        escalation_msg = escalation_messages[0]
        self.assertEqual(escalation_msg.message_type, A2AMessageType.ESCALATION_REQUEST)
        self.assertEqual(escalation_msg.recipient_agent_id, "escalation_id")
        self.assertEqual(len(escalation_msg.payload["rejection_history"]), 3)


if __name__ == "__main__":
    unittest.main()
