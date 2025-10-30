"""
tests/a2a_tests/test_validation_loop.py

Tests for the validation loop workflow with retry and escalation logic.
Tests ValidationLoopHandler and the critical validate_with_retry pattern.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
from typing import Dict, Any, List

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.utils.vertex_a2a_protocol import (
    A2AMessageType,
    A2AMessage,
    A2AProtocolHelper
)
from shared.utils.a2a_integration import (
    A2AIntegration,
    ValidationLoopHandler
)
from shared.utils.agent_base import AgentContext


class TestValidationLoopHandler(unittest.TestCase):
    """Test ValidationLoopHandler for validation-retry-escalation pattern."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock context and message bus
        self.context = AgentContext(
            agent_id="projects/test/locations/us-central1/reasoningEngines/dev_agent",
            agent_name="developer_agent",
            project_id="test-project",
            location="us-central1"
        )

        self.message_bus = MagicMock()
        self.orchestrator_id = "projects/test/locations/us-central1/reasoningEngines/orchestrator"
        self.validator_id = "projects/test/locations/us-central1/reasoningEngines/validator"
        self.escalation_id = "projects/test/locations/us-central1/reasoningEngines/escalation"

        # Create A2A integration
        self.a2a = A2AIntegration(
            agent_context=self.context,
            message_bus=self.message_bus,
            orchestrator_id=self.orchestrator_id
        )

        # Create validation loop handler
        self.validation_handler = ValidationLoopHandler(
            a2a_integration=self.a2a,
            max_retries=3,
            escalation_agent_id=self.escalation_id
        )

    def test_validation_handler_initialization(self):
        """Test ValidationLoopHandler initialization."""
        self.assertEqual(self.validation_handler.max_retries, 3)
        self.assertEqual(self.validation_handler.escalation_agent_id, self.escalation_id)
        self.assertIsNotNone(self.validation_handler.a2a)

    def test_validation_success_first_attempt(self):
        """Test successful validation on first attempt."""
        task_id = "test_001"

        # Mock artifact generator (generates code)
        def artifact_generator(feedback: str = None) -> Dict[str, Any]:
            return {
                "code": "def process_payment(): return True",
                "tests": "def test_payment(): assert process_payment()"
            }

        # Mock validation response (passes immediately)
        validation_response = A2AProtocolHelper.create_validation_result(
            sender_id=self.validator_id,
            sender_name="code_validator",
            recipient_id=self.context.agent_id,
            recipient_name=self.context.agent_name,
            task_id=task_id,
            passed=True,
            issues=[],
            feedback="Code looks good",
            correlation_id="test-corr-123"
        )

        # Mock send_and_wait to return passing validation
        self.message_bus.send_and_wait = MagicMock(return_value=validation_response)

        # Execute validation loop
        result = self.validation_handler.validate_with_retry(
            task_id=task_id,
            validator_id=self.validator_id,
            validator_name="code_validator",
            artifact_generator=artifact_generator,
            validation_criteria=["correctness", "security"]
        )

        # Verify success
        self.assertEqual(result["status"], "validated")
        self.assertEqual(result["attempts"], 1)
        self.assertTrue(result["validation_passed"])
        self.assertEqual(len(result["issues"]), 0)

        # Verify send_and_wait was called once
        self.message_bus.send_and_wait.assert_called_once()

    def test_validation_retry_with_feedback_incorporation(self):
        """Test validation retry with feedback incorporation."""
        task_id = "test_002"

        # Track artifact generation attempts with feedback
        generation_attempts = []

        def artifact_generator(feedback: str = None) -> Dict[str, Any]:
            generation_attempts.append(feedback)

            if feedback is None:
                # First attempt - no error handling
                return {
                    "code": "def process_payment(amount): return amount"
                }
            elif "error handling" in feedback:
                # Second attempt - added error handling
                return {
                    "code": """
def process_payment(amount):
    try:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        return amount
    except Exception as e:
        logging.error(f"Payment failed: {e}")
        raise
"""
                }
            else:
                return {"code": "def process_payment(amount): return amount"}

        # Mock validation responses
        # First attempt: fails (missing error handling)
        fail_response_1 = A2AProtocolHelper.create_validation_result(
            sender_id=self.validator_id,
            sender_name="code_validator",
            recipient_id=self.context.agent_id,
            recipient_name=self.context.agent_name,
            task_id=task_id,
            passed=False,
            issues=["Missing error handling"],
            feedback="Add try-catch blocks and input validation",
            correlation_id="corr-1"
        )

        # Second attempt: passes
        pass_response = A2AProtocolHelper.create_validation_result(
            sender_id=self.validator_id,
            sender_name="code_validator",
            recipient_id=self.context.agent_id,
            recipient_name=self.context.agent_name,
            task_id=task_id,
            passed=True,
            issues=[],
            feedback="Code looks good now",
            correlation_id="corr-2"
        )

        # Mock send_and_wait to return different responses
        self.message_bus.send_and_wait = MagicMock(
            side_effect=[fail_response_1, pass_response]
        )

        # Execute validation loop
        result = self.validation_handler.validate_with_retry(
            task_id=task_id,
            validator_id=self.validator_id,
            validator_name="code_validator",
            artifact_generator=artifact_generator,
            validation_criteria=["correctness", "error_handling"]
        )

        # Verify success after retry
        self.assertEqual(result["status"], "validated")
        self.assertEqual(result["attempts"], 2)
        self.assertTrue(result["validation_passed"])

        # Verify feedback was incorporated
        self.assertEqual(len(generation_attempts), 2)
        self.assertIsNone(generation_attempts[0])  # First attempt: no feedback
        self.assertIn("error handling", generation_attempts[1])  # Second attempt: with feedback

        # Verify send_and_wait was called twice
        self.assertEqual(self.message_bus.send_and_wait.call_count, 2)

    def test_validation_max_retries_then_escalation(self):
        """Test escalation after max retries exceeded."""
        task_id = "test_003"

        def artifact_generator(feedback: str = None) -> Dict[str, Any]:
            # Always generates same code (doesn't improve)
            return {"code": "def process_payment(): pass"}

        # Mock validation responses - always fail
        fail_response = A2AProtocolHelper.create_validation_result(
            sender_id=self.validator_id,
            sender_name="code_validator",
            recipient_id=self.context.agent_id,
            recipient_name=self.context.agent_name,
            task_id=task_id,
            passed=False,
            issues=["Missing implementation", "No error handling", "No tests"],
            feedback="Please implement the payment logic properly",
            correlation_id="corr"
        )

        # All attempts fail
        self.message_bus.send_and_wait = MagicMock(
            return_value=fail_response
        )

        # Mock publish_message for escalation
        self.message_bus.publish_message = MagicMock()

        # Execute validation loop (should escalate after 3 failures)
        result = self.validation_handler.validate_with_retry(
            task_id=task_id,
            validator_id=self.validator_id,
            validator_name="code_validator",
            artifact_generator=artifact_generator,
            validation_criteria=["correctness"]
        )

        # Verify escalation
        self.assertEqual(result["status"], "escalated")
        self.assertEqual(result["attempts"], 3)  # Max retries
        self.assertFalse(result["validation_passed"])
        self.assertEqual(len(result["issues"]), 3)

        # Verify send_and_wait was called 3 times
        self.assertEqual(self.message_bus.send_and_wait.call_count, 3)

        # Verify escalation message was sent
        self.message_bus.publish_message.assert_called()
        escalation_call = self.message_bus.publish_message.call_args[0][0]
        self.assertEqual(escalation_call.message_type, A2AMessageType.ESCALATION_REQUEST)
        self.assertEqual(escalation_call.recipient_agent_id, self.escalation_id)

    def test_validation_timeout_handling(self):
        """Test handling of validation timeout."""
        task_id = "test_004"

        def artifact_generator(feedback: str = None) -> Dict[str, Any]:
            return {"code": "def process_payment(): pass"}

        # Mock send_and_wait to raise TimeoutError
        self.message_bus.send_and_wait = MagicMock(
            side_effect=TimeoutError("Validation request timed out")
        )

        # Mock publish_message for error report
        self.message_bus.publish_message = MagicMock()

        # Execute validation loop (should handle timeout)
        with self.assertRaises(TimeoutError):
            self.validation_handler.validate_with_retry(
                task_id=task_id,
                validator_id=self.validator_id,
                validator_name="code_validator",
                artifact_generator=artifact_generator,
                validation_criteria=["correctness"]
            )

    def test_validation_criteria_passed_to_validator(self):
        """Test that validation criteria are correctly passed to validator."""
        task_id = "test_005"

        def artifact_generator(feedback: str = None) -> Dict[str, Any]:
            return {"code": "test code"}

        validation_criteria = [
            "correctness",
            "security",
            "performance",
            "maintainability"
        ]

        # Mock passing validation
        pass_response = A2AProtocolHelper.create_validation_result(
            sender_id=self.validator_id,
            sender_name="code_validator",
            recipient_id=self.context.agent_id,
            recipient_name=self.context.agent_name,
            task_id=task_id,
            passed=True,
            issues=[],
            feedback="All criteria met",
            correlation_id="corr"
        )

        self.message_bus.send_and_wait = MagicMock(return_value=pass_response)

        # Execute validation
        result = self.validation_handler.validate_with_retry(
            task_id=task_id,
            validator_id=self.validator_id,
            validator_name="code_validator",
            artifact_generator=artifact_generator,
            validation_criteria=validation_criteria
        )

        # Verify validation request included all criteria
        validation_request = self.message_bus.send_and_wait.call_args[0][0]
        self.assertEqual(
            validation_request.payload["validation_criteria"],
            validation_criteria
        )

    def test_rejection_history_tracking(self):
        """Test that rejection history is tracked correctly."""
        task_id = "test_006"

        def artifact_generator(feedback: str = None) -> Dict[str, Any]:
            return {"code": "test"}

        # Create 3 different failure responses
        fail_responses = []
        for i in range(3):
            fail_responses.append(
                A2AProtocolHelper.create_validation_result(
                    sender_id=self.validator_id,
                    sender_name="code_validator",
                    recipient_id=self.context.agent_id,
                    recipient_name=self.context.agent_name,
                    task_id=task_id,
                    passed=False,
                    issues=[f"Issue {i+1}"],
                    feedback=f"Feedback {i+1}",
                    correlation_id=f"corr-{i}"
                )
            )

        self.message_bus.send_and_wait = MagicMock(side_effect=fail_responses)
        self.message_bus.publish_message = MagicMock()

        # Execute validation (will escalate)
        result = self.validation_handler.validate_with_retry(
            task_id=task_id,
            validator_id=self.validator_id,
            validator_name="code_validator",
            artifact_generator=artifact_generator,
            validation_criteria=["correctness"]
        )

        # Verify escalation was called with rejection history
        escalation_call = self.message_bus.publish_message.call_args[0][0]
        rejection_history = escalation_call.payload["rejection_history"]

        self.assertEqual(len(rejection_history), 3)
        for i, rejection in enumerate(rejection_history):
            self.assertEqual(rejection["attempt"], i + 1)
            self.assertIn(f"Issue {i+1}", str(rejection["issues"]))

    def test_validation_with_custom_max_retries(self):
        """Test validation with custom max_retries setting."""
        # Create handler with max_retries=5
        custom_handler = ValidationLoopHandler(
            a2a_integration=self.a2a,
            max_retries=5,
            escalation_agent_id=self.escalation_id
        )

        task_id = "test_007"

        def artifact_generator(feedback: str = None) -> Dict[str, Any]:
            return {"code": "test"}

        # Mock all attempts fail
        fail_response = A2AProtocolHelper.create_validation_result(
            sender_id=self.validator_id,
            sender_name="code_validator",
            recipient_id=self.context.agent_id,
            recipient_name=self.context.agent_name,
            task_id=task_id,
            passed=False,
            issues=["Still failing"],
            feedback="Fix it",
            correlation_id="corr"
        )

        self.message_bus.send_and_wait = MagicMock(return_value=fail_response)
        self.message_bus.publish_message = MagicMock()

        # Execute
        result = custom_handler.validate_with_retry(
            task_id=task_id,
            validator_id=self.validator_id,
            validator_name="code_validator",
            artifact_generator=artifact_generator,
            validation_criteria=["correctness"]
        )

        # Verify it tried 5 times before escalating
        self.assertEqual(result["attempts"], 5)
        self.assertEqual(self.message_bus.send_and_wait.call_count, 5)


class TestA2AIntegrationTaskTracking(unittest.TestCase):
    """Test A2AIntegration task tracking decorator."""

    def setUp(self):
        """Set up test fixtures."""
        self.context = AgentContext(
            agent_id="projects/test/locations/us-central1/reasoningEngines/dev_agent",
            agent_name="developer_agent",
            project_id="test-project",
            location="us-central1"
        )

        self.message_bus = MagicMock()
        self.orchestrator_id = "projects/test/locations/us-central1/reasoningEngines/orchestrator"

        self.a2a = A2AIntegration(
            agent_context=self.context,
            message_bus=self.message_bus,
            orchestrator_id=self.orchestrator_id
        )

    def test_with_task_tracking_success(self):
        """Test @with_task_tracking decorator on successful execution."""
        @self.a2a.with_task_tracking
        def example_tool(task_id: str, component_id: str, **kwargs) -> Dict[str, Any]:
            return {
                "status": "success",
                "component_id": component_id,
                "result": "Implementation complete"
            }

        # Execute tool
        result = example_tool(task_id="test_001", component_id="payment_processor")

        # Verify result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["component_id"], "payment_processor")

        # Verify state updates were sent
        # Should have sent: pending→in_progress, in_progress→completed
        self.assertEqual(self.message_bus.publish_message.call_count, 2)

        # Check first state update (pending → in_progress)
        first_update = self.message_bus.publish_message.call_args_list[0][0][0]
        self.assertEqual(first_update.message_type, A2AMessageType.STATE_UPDATE)
        self.assertEqual(first_update.payload["old_status"], "pending")
        self.assertEqual(first_update.payload["new_status"], "in_progress")

        # Check second state update (in_progress → completed)
        second_update = self.message_bus.publish_message.call_args_list[1][0][0]
        self.assertEqual(second_update.payload["old_status"], "in_progress")
        self.assertEqual(second_update.payload["new_status"], "completed")
        self.assertIn("execution_time_seconds", second_update.payload["metadata"])

    def test_with_task_tracking_failure(self):
        """Test @with_task_tracking decorator on exception."""
        @self.a2a.with_task_tracking
        def failing_tool(task_id: str, **kwargs) -> Dict[str, Any]:
            raise ValueError("Something went wrong")

        # Execute tool (should raise)
        with self.assertRaises(ValueError):
            failing_tool(task_id="test_002")

        # Verify error report and state update were sent
        # Should have sent: pending→in_progress, ERROR_REPORT, in_progress→failed
        self.assertGreaterEqual(self.message_bus.publish_message.call_count, 2)

        # Find error report
        error_reports = [
            call[0][0] for call in self.message_bus.publish_message.call_args_list
            if call[0][0].message_type == A2AMessageType.ERROR_REPORT
        ]

        self.assertEqual(len(error_reports), 1)
        error_report = error_reports[0]
        self.assertIn("Something went wrong", error_report.payload["error_message"])
        self.assertEqual(error_report.priority, 1)  # High priority

    def test_send_task_update(self):
        """Test manual task status update."""
        self.a2a.send_task_update(
            task_id="test_003",
            old_status="pending",
            new_status="in_progress",
            metadata={"started_at": "2025-10-30T10:00:00Z"}
        )

        # Verify state update was sent
        self.message_bus.publish_message.assert_called_once()

        update_message = self.message_bus.publish_message.call_args[0][0]
        self.assertEqual(update_message.message_type, A2AMessageType.STATE_UPDATE)
        self.assertEqual(update_message.payload["task_id"], "test_003")
        self.assertEqual(update_message.payload["old_status"], "pending")
        self.assertEqual(update_message.payload["new_status"], "in_progress")

    def test_send_error_report(self):
        """Test manual error reporting."""
        self.a2a.send_error_report(
            task_id="test_004",
            error_message="Failed to connect to database",
            error_details={
                "exception": "ConnectionError",
                "host": "db.example.com",
                "port": 5432
            }
        )

        # Verify error report was sent
        self.message_bus.publish_message.assert_called_once()

        error_message = self.message_bus.publish_message.call_args[0][0]
        self.assertEqual(error_message.message_type, A2AMessageType.ERROR_REPORT)
        self.assertEqual(error_message.payload["task_id"], "test_004")
        self.assertIn("database", error_message.payload["error_message"])
        self.assertEqual(error_message.priority, 1)

    def test_send_validation_request(self):
        """Test sending validation request."""
        # Mock send_and_wait
        validation_result = A2AProtocolHelper.create_validation_result(
            sender_id="validator_id",
            sender_name="code_validator",
            recipient_id=self.context.agent_id,
            recipient_name=self.context.agent_name,
            task_id="test_005",
            passed=True,
            issues=[],
            feedback="Good",
            correlation_id="corr"
        )
        self.message_bus.send_and_wait = MagicMock(return_value=validation_result)

        # Send validation request
        result = self.a2a.send_validation_request(
            validator_id="validator_id",
            validator_name="code_validator",
            task_id="test_005",
            artifact={"code": "def foo(): pass"},
            validation_criteria=["correctness"]
        )

        # Verify request was sent
        self.message_bus.send_and_wait.assert_called_once()

        request = self.message_bus.send_and_wait.call_args[0][0]
        self.assertEqual(request.message_type, A2AMessageType.VALIDATION_REQUEST)
        self.assertEqual(request.payload["task_id"], "test_005")
        self.assertEqual(request.payload["validation_criteria"], ["correctness"])


if __name__ == "__main__":
    unittest.main()
