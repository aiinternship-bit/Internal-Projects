"""
tests/a2a_tests/test_a2a_protocol.py

Unit tests for A2A (Agent-to-Agent) protocol implementation.
Tests message creation, serialization, and protocol helper methods.
"""

import unittest
import json
from datetime import datetime
from typing import Dict, Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.utils.vertex_a2a_protocol import (
    A2AMessageType,
    A2AMessage,
    A2AProtocolHelper
)


class TestA2AMessageType(unittest.TestCase):
    """Test A2AMessageType enum."""

    def test_all_message_types_exist(self):
        """Test that all 10 message types are defined."""
        expected_types = [
            "TASK_ASSIGNMENT",
            "TASK_COMPLETION",
            "VALIDATION_REQUEST",
            "VALIDATION_RESULT",
            "ESCALATION_REQUEST",
            "QUERY_REQUEST",
            "QUERY_RESPONSE",
            "STATE_UPDATE",
            "ERROR_REPORT",
            "HUMAN_APPROVAL_REQUEST"
        ]

        actual_types = [msg_type.name for msg_type in A2AMessageType]

        for expected in expected_types:
            self.assertIn(expected, actual_types,
                         f"Message type {expected} not found")

        self.assertEqual(len(actual_types), 10,
                        "Should have exactly 10 message types")

    def test_message_type_values(self):
        """Test message type string values."""
        self.assertEqual(A2AMessageType.TASK_ASSIGNMENT.value, "task_assignment")
        self.assertEqual(A2AMessageType.VALIDATION_REQUEST.value, "validation_request")
        self.assertEqual(A2AMessageType.ERROR_REPORT.value, "error_report")


class TestA2AMessage(unittest.TestCase):
    """Test A2AMessage dataclass."""

    def setUp(self):
        """Set up test fixtures."""
        self.sender_id = "projects/test-proj/locations/us-central1/reasoningEngines/agent1"
        self.recipient_id = "projects/test-proj/locations/us-central1/reasoningEngines/agent2"
        self.test_payload = {
            "task_id": "test_001",
            "component_id": "payment_processor",
            "data": "test data"
        }

    def test_message_creation(self):
        """Test creating a basic A2A message."""
        message = A2AMessage(
            message_type=A2AMessageType.TASK_ASSIGNMENT,
            sender_agent_id=self.sender_id,
            sender_agent_name="orchestrator",
            recipient_agent_id=self.recipient_id,
            recipient_agent_name="developer",
            payload=self.test_payload
        )

        self.assertEqual(message.message_type, A2AMessageType.TASK_ASSIGNMENT)
        self.assertEqual(message.sender_agent_id, self.sender_id)
        self.assertEqual(message.recipient_agent_id, self.recipient_id)
        self.assertEqual(message.payload, self.test_payload)
        self.assertIsNotNone(message.correlation_id)
        self.assertIsNotNone(message.timestamp)

    def test_message_with_priority(self):
        """Test message with custom priority."""
        message = A2AMessage(
            message_type=A2AMessageType.ERROR_REPORT,
            sender_agent_id=self.sender_id,
            sender_agent_name="developer",
            recipient_agent_id=self.recipient_id,
            recipient_agent_name="orchestrator",
            payload={"error": "Critical failure"},
            priority=1  # Highest priority
        )

        self.assertEqual(message.priority, 1)

    def test_message_with_retry_settings(self):
        """Test message with retry configuration."""
        message = A2AMessage(
            message_type=A2AMessageType.VALIDATION_REQUEST,
            sender_agent_id=self.sender_id,
            sender_agent_name="developer",
            recipient_agent_id=self.recipient_id,
            recipient_agent_name="validator",
            payload={"artifact": "code"},
            max_retries=5,
            retry_count=2,
            ttl_seconds=300
        )

        self.assertEqual(message.max_retries, 5)
        self.assertEqual(message.retry_count, 2)
        self.assertEqual(message.ttl_seconds, 300)

    def test_message_serialization_to_dict(self):
        """Test message serialization to dictionary."""
        message = A2AMessage(
            message_type=A2AMessageType.TASK_ASSIGNMENT,
            sender_agent_id=self.sender_id,
            sender_agent_name="orchestrator",
            recipient_agent_id=self.recipient_id,
            recipient_agent_name="developer",
            payload=self.test_payload,
            correlation_id="test-corr-123"
        )

        message_dict = message.to_dict()

        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict["message_type"], "task_assignment")
        self.assertEqual(message_dict["sender_agent_id"], self.sender_id)
        self.assertEqual(message_dict["recipient_agent_id"], self.recipient_id)
        self.assertEqual(message_dict["payload"], self.test_payload)
        self.assertEqual(message_dict["correlation_id"], "test-corr-123")

    def test_message_serialization_to_json(self):
        """Test message serialization to JSON string."""
        message = A2AMessage(
            message_type=A2AMessageType.STATE_UPDATE,
            sender_agent_id=self.sender_id,
            sender_agent_name="developer",
            recipient_agent_id=self.recipient_id,
            recipient_agent_name="orchestrator",
            payload={"task_id": "test_001", "status": "completed"}
        )

        message_json = message.to_json()

        self.assertIsInstance(message_json, str)

        # Verify it's valid JSON
        parsed = json.loads(message_json)
        self.assertEqual(parsed["message_type"], "state_update")
        self.assertEqual(parsed["payload"]["status"], "completed")

    def test_message_deserialization_from_dict(self):
        """Test message deserialization from dictionary."""
        message_dict = {
            "message_type": "validation_result",
            "sender_agent_id": self.sender_id,
            "sender_agent_name": "validator",
            "recipient_agent_id": self.recipient_id,
            "recipient_agent_name": "developer",
            "payload": {"passed": True, "issues": []},
            "correlation_id": "test-456",
            "timestamp": "2025-10-30T10:30:00Z",
            "requires_response": False,
            "priority": 5,
            "retry_count": 0,
            "max_retries": 3,
            "ttl_seconds": 3600
        }

        message = A2AMessage.from_dict(message_dict)

        self.assertEqual(message.message_type, A2AMessageType.VALIDATION_RESULT)
        self.assertEqual(message.sender_agent_id, self.sender_id)
        self.assertEqual(message.payload["passed"], True)
        self.assertEqual(message.correlation_id, "test-456")
        self.assertEqual(message.priority, 5)

    def test_message_round_trip_serialization(self):
        """Test message serialization round trip (dict → message → dict)."""
        original = A2AMessage(
            message_type=A2AMessageType.TASK_COMPLETION,
            sender_agent_id=self.sender_id,
            sender_agent_name="developer",
            recipient_agent_id=self.recipient_id,
            recipient_agent_name="orchestrator",
            payload={"task_id": "test_001", "result": "success"},
            priority=3
        )

        # Serialize to dict
        message_dict = original.to_dict()

        # Deserialize back to message
        reconstructed = A2AMessage.from_dict(message_dict)

        # Verify all fields match
        self.assertEqual(reconstructed.message_type, original.message_type)
        self.assertEqual(reconstructed.sender_agent_id, original.sender_agent_id)
        self.assertEqual(reconstructed.recipient_agent_id, original.recipient_agent_id)
        self.assertEqual(reconstructed.payload, original.payload)
        self.assertEqual(reconstructed.priority, original.priority)


class TestA2AProtocolHelper(unittest.TestCase):
    """Test A2AProtocolHelper factory methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.sender_id = "projects/test/locations/us-central1/reasoningEngines/agent1"
        self.recipient_id = "projects/test/locations/us-central1/reasoningEngines/agent2"

    def test_create_task_assignment(self):
        """Test creating TASK_ASSIGNMENT message."""
        message = A2AProtocolHelper.create_task_assignment(
            sender_id=self.sender_id,
            sender_name="orchestrator",
            recipient_id=self.recipient_id,
            recipient_name="developer",
            task_data={
                "task_id": "dev_001",
                "component_id": "payment_processor",
                "architecture_spec": {"language": "python"}
            }
        )

        self.assertEqual(message.message_type, A2AMessageType.TASK_ASSIGNMENT)
        self.assertEqual(message.sender_agent_name, "orchestrator")
        self.assertEqual(message.recipient_agent_name, "developer")
        self.assertEqual(message.payload["task_id"], "dev_001")
        self.assertTrue(message.requires_response)  # Task assignments expect completion

    def test_create_validation_request(self):
        """Test creating VALIDATION_REQUEST message."""
        message = A2AProtocolHelper.create_validation_request(
            sender_id=self.sender_id,
            sender_name="developer",
            recipient_id=self.recipient_id,
            recipient_name="code_validator",
            task_id="dev_001",
            artifact={
                "code": "def process_payment(): pass",
                "tests": "def test_payment(): assert True"
            },
            validation_criteria=["correctness", "security", "error_handling"]
        )

        self.assertEqual(message.message_type, A2AMessageType.VALIDATION_REQUEST)
        self.assertEqual(message.payload["task_id"], "dev_001")
        self.assertIn("code", message.payload["artifact"])
        self.assertEqual(len(message.payload["validation_criteria"]), 3)
        self.assertTrue(message.requires_response)  # Validation requests expect results

    def test_create_validation_result(self):
        """Test creating VALIDATION_RESULT message."""
        message = A2AProtocolHelper.create_validation_result(
            sender_id=self.sender_id,
            sender_name="code_validator",
            recipient_id=self.recipient_id,
            recipient_name="developer",
            task_id="dev_001",
            passed=False,
            issues=["Missing error handling in line 10", "SQL injection vulnerability"],
            feedback="Add try-catch blocks and parameterized queries",
            correlation_id="req-123"
        )

        self.assertEqual(message.message_type, A2AMessageType.VALIDATION_RESULT)
        self.assertEqual(message.payload["passed"], False)
        self.assertEqual(len(message.payload["issues"]), 2)
        self.assertIn("try-catch", message.payload["feedback"])
        self.assertEqual(message.correlation_id, "req-123")
        self.assertFalse(message.requires_response)  # Results don't need response

    def test_create_escalation_request(self):
        """Test creating ESCALATION_REQUEST message."""
        rejection_history = [
            {"attempt": 1, "reason": "missing_error_handling"},
            {"attempt": 2, "reason": "missing_error_handling"},
            {"attempt": 3, "reason": "missing_error_handling"}
        ]

        message = A2AProtocolHelper.create_escalation_request(
            sender_id=self.sender_id,
            sender_name="developer",
            recipient_id=self.recipient_id,
            recipient_name="escalation_agent",
            task_id="dev_001",
            rejection_history=rejection_history,
            task_context={"component_id": "payment_processor", "priority": "high"},
            reason="Validation failed 3 times with same issue"
        )

        self.assertEqual(message.message_type, A2AMessageType.ESCALATION_REQUEST)
        self.assertEqual(message.payload["task_id"], "dev_001")
        self.assertEqual(len(message.payload["rejection_history"]), 3)
        self.assertEqual(message.payload["task_context"]["priority"], "high")
        self.assertEqual(message.priority, 1)  # Escalations are high priority
        self.assertTrue(message.requires_response)

    def test_create_state_update(self):
        """Test creating STATE_UPDATE message."""
        message = A2AProtocolHelper.create_state_update(
            sender_id=self.sender_id,
            sender_name="developer",
            recipient_id=self.recipient_id,
            recipient_name="orchestrator",
            task_id="dev_001",
            old_status="in_progress",
            new_status="completed",
            metadata={"execution_time_seconds": 45.3, "validation_attempts": 2}
        )

        self.assertEqual(message.message_type, A2AMessageType.STATE_UPDATE)
        self.assertEqual(message.payload["task_id"], "dev_001")
        self.assertEqual(message.payload["old_status"], "in_progress")
        self.assertEqual(message.payload["new_status"], "completed")
        self.assertEqual(message.payload["metadata"]["validation_attempts"], 2)
        self.assertFalse(message.requires_response)  # State updates are notifications

    def test_create_error_report(self):
        """Test creating ERROR_REPORT message."""
        message = A2AProtocolHelper.create_error_report(
            sender_id=self.sender_id,
            sender_name="developer",
            recipient_id=self.recipient_id,
            recipient_name="orchestrator",
            task_id="dev_001",
            error_message="Failed to generate code",
            error_details={
                "exception_type": "ValueError",
                "stack_trace": "...",
                "context": {"component_id": "payment_processor"}
            }
        )

        self.assertEqual(message.message_type, A2AMessageType.ERROR_REPORT)
        self.assertEqual(message.payload["error_message"], "Failed to generate code")
        self.assertEqual(message.payload["error_details"]["exception_type"], "ValueError")
        self.assertEqual(message.priority, 1)  # Errors are high priority
        self.assertFalse(message.requires_response)

    def test_create_query_request(self):
        """Test creating QUERY_REQUEST message."""
        message = A2AProtocolHelper.create_query_request(
            sender_id=self.sender_id,
            sender_name="developer",
            recipient_id=self.recipient_id,
            recipient_name="domain_expert",
            query="What are the business rules for payment processing?",
            context={"component_id": "payment_processor", "domain": "fintech"}
        )

        self.assertEqual(message.message_type, A2AMessageType.QUERY_REQUEST)
        self.assertIn("business rules", message.payload["query"])
        self.assertEqual(message.payload["context"]["domain"], "fintech")
        self.assertTrue(message.requires_response)

    def test_create_query_response(self):
        """Test creating QUERY_RESPONSE message."""
        message = A2AProtocolHelper.create_query_response(
            sender_id=self.sender_id,
            sender_name="domain_expert",
            recipient_id=self.recipient_id,
            recipient_name="developer",
            query_result={
                "business_rules": ["Validate amount > 0", "Check card expiry"],
                "constraints": ["PCI-DSS compliance required"]
            },
            correlation_id="query-789"
        )

        self.assertEqual(message.message_type, A2AMessageType.QUERY_RESPONSE)
        self.assertEqual(len(message.payload["query_result"]["business_rules"]), 2)
        self.assertEqual(message.correlation_id, "query-789")
        self.assertFalse(message.requires_response)

    def test_create_task_completion(self):
        """Test creating TASK_COMPLETION message."""
        message = A2AProtocolHelper.create_task_completion(
            sender_id=self.sender_id,
            sender_name="developer",
            recipient_id=self.recipient_id,
            recipient_name="orchestrator",
            task_id="dev_001",
            result={
                "code": "def process_payment(): ...",
                "unit_tests": "def test_payment(): ...",
                "documentation": "Payment processor docs"
            },
            execution_time_seconds=42.5
        )

        self.assertEqual(message.message_type, A2AMessageType.TASK_COMPLETION)
        self.assertEqual(message.payload["task_id"], "dev_001")
        self.assertIn("code", message.payload["result"])
        self.assertEqual(message.payload["execution_time_seconds"], 42.5)
        self.assertFalse(message.requires_response)

    def test_message_type_validation(self):
        """Test that message_type must be A2AMessageType enum."""
        # Valid: using enum
        message1 = A2AMessage(
            message_type=A2AMessageType.TASK_ASSIGNMENT,
            sender_agent_id=self.sender_id,
            sender_agent_name="agent1",
            recipient_agent_id=self.recipient_id,
            recipient_agent_name="agent2",
            payload={}
        )
        self.assertIsInstance(message1.message_type, A2AMessageType)

    def test_correlation_id_propagation(self):
        """Test correlation ID is preserved in response messages."""
        # Create request with correlation ID
        request = A2AProtocolHelper.create_validation_request(
            sender_id=self.sender_id,
            sender_name="developer",
            recipient_id=self.recipient_id,
            recipient_name="validator",
            task_id="dev_001",
            artifact={"code": "test"},
            validation_criteria=["correctness"]
        )

        request_corr_id = request.correlation_id

        # Create response with same correlation ID
        response = A2AProtocolHelper.create_validation_result(
            sender_id=self.recipient_id,
            sender_name="validator",
            recipient_id=self.sender_id,
            recipient_name="developer",
            task_id="dev_001",
            passed=True,
            issues=[],
            feedback="Looks good",
            correlation_id=request_corr_id
        )

        # Verify correlation IDs match
        self.assertEqual(request.correlation_id, response.correlation_id)


class TestA2AMessageValidation(unittest.TestCase):
    """Test A2A message validation logic."""

    def setUp(self):
        """Set up test fixtures."""
        self.sender_id = "projects/test/locations/us-central1/reasoningEngines/agent1"
        self.recipient_id = "projects/test/locations/us-central1/reasoningEngines/agent2"

    def test_priority_range(self):
        """Test that priority is within valid range (1-10)."""
        # Valid priorities
        for priority in range(1, 11):
            message = A2AMessage(
                message_type=A2AMessageType.TASK_ASSIGNMENT,
                sender_agent_id=self.sender_id,
                sender_agent_name="agent1",
                recipient_agent_id=self.recipient_id,
                recipient_agent_name="agent2",
                payload={},
                priority=priority
            )
            self.assertGreaterEqual(message.priority, 1)
            self.assertLessEqual(message.priority, 10)

    def test_retry_count_increments(self):
        """Test retry count can be tracked."""
        message = A2AMessage(
            message_type=A2AMessageType.VALIDATION_REQUEST,
            sender_agent_id=self.sender_id,
            sender_agent_name="developer",
            recipient_agent_id=self.recipient_id,
            recipient_agent_name="validator",
            payload={},
            retry_count=2,
            max_retries=3
        )

        self.assertEqual(message.retry_count, 2)
        self.assertLess(message.retry_count, message.max_retries)

    def test_timestamp_format(self):
        """Test timestamp is in ISO format."""
        message = A2AMessage(
            message_type=A2AMessageType.STATE_UPDATE,
            sender_agent_id=self.sender_id,
            sender_agent_name="agent1",
            recipient_agent_id=self.recipient_id,
            recipient_agent_name="agent2",
            payload={}
        )

        # Should be able to parse timestamp
        try:
            datetime.fromisoformat(message.timestamp.replace('Z', '+00:00'))
            timestamp_valid = True
        except ValueError:
            timestamp_valid = False

        self.assertTrue(timestamp_valid, "Timestamp should be in ISO format")


if __name__ == "__main__":
    unittest.main()
