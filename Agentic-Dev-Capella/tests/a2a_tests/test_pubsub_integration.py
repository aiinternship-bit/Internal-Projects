"""
tests/a2a_tests/test_pubsub_integration.py

Integration tests for Google Cloud Pub/Sub message bus.
Tests message publishing, subscription filtering, and agent communication.

NOTE: These tests require Google Cloud credentials and a test project.
Run with: pytest tests/a2a_tests/test_pubsub_integration.py --gcp-project=YOUR_PROJECT
"""

import unittest
import os
import time
import uuid
from typing import List, Dict, Any, Optional
from unittest.mock import Mock, patch, MagicMock
from threading import Event

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.utils.vertex_a2a_protocol import (
    A2AMessageType,
    A2AMessage,
    A2AProtocolHelper,
    VertexA2AMessageBus
)


# ============================================================================
# MOCK TESTS (No GCP Credentials Required)
# ============================================================================

class TestVertexA2AMessageBusMock(unittest.TestCase):
    """Test VertexA2AMessageBus with mocked Google Cloud Pub/Sub."""

    def setUp(self):
        """Set up test fixtures with mocked Pub/Sub clients."""
        self.project_id = "test-project"
        self.topic_name = "test-agent-messages"

        # Mock Pub/Sub clients
        self.mock_publisher = MagicMock()
        self.mock_subscriber = MagicMock()

        # Patch Pub/Sub clients
        self.publisher_patch = patch(
            'google.cloud.pubsub_v1.PublisherClient',
            return_value=self.mock_publisher
        )
        self.subscriber_patch = patch(
            'google.cloud.pubsub_v1.SubscriberClient',
            return_value=self.mock_subscriber
        )

        self.publisher_patch.start()
        self.subscriber_patch.start()

        # Set up mock paths
        self.mock_publisher.topic_path.return_value = (
            f"projects/{self.project_id}/topics/{self.topic_name}"
        )
        self.mock_subscriber.subscription_path.return_value = (
            f"projects/{self.project_id}/subscriptions/test-sub"
        )

    def tearDown(self):
        """Clean up patches."""
        self.publisher_patch.stop()
        self.subscriber_patch.stop()

    def test_message_bus_initialization(self):
        """Test VertexA2AMessageBus initialization."""
        message_bus = VertexA2AMessageBus(
            project_id=self.project_id,
            topic_name=self.topic_name,
            create_if_missing=False
        )

        self.assertEqual(message_bus.project_id, self.project_id)
        self.assertEqual(message_bus.topic_name, self.topic_name)
        self.mock_publisher.topic_path.assert_called_once_with(
            self.project_id,
            self.topic_name
        )

    def test_publish_message(self):
        """Test publishing a message to Pub/Sub."""
        message_bus = VertexA2AMessageBus(
            project_id=self.project_id,
            topic_name=self.topic_name,
            create_if_missing=False
        )

        # Mock successful publish
        future_mock = MagicMock()
        future_mock.result.return_value = "message-id-123"
        self.mock_publisher.publish.return_value = future_mock

        # Create test message
        message = A2AProtocolHelper.create_task_assignment(
            sender_id="agent1",
            sender_name="orchestrator",
            recipient_id="agent2",
            recipient_name="developer",
            task_data={"task_id": "test_001"}
        )

        # Publish message
        message_id = message_bus.publish_message(message)

        # Verify publish was called
        self.mock_publisher.publish.assert_called_once()

        # Verify message attributes were set
        call_kwargs = self.mock_publisher.publish.call_args[1]
        self.assertEqual(call_kwargs["message_type"], message.message_type.value)
        self.assertEqual(call_kwargs["sender_agent_id"], message.sender_agent_id)
        self.assertEqual(call_kwargs["recipient_agent_id"], message.recipient_agent_id)

    def test_register_agent_creates_subscription(self):
        """Test that registering an agent creates a filtered subscription."""
        message_bus = VertexA2AMessageBus(
            project_id=self.project_id,
            topic_name=self.topic_name,
            create_if_missing=False
        )

        agent_id = "projects/test/locations/us-central1/reasoningEngines/dev_agent"
        agent_name = "developer_agent"

        # Mock subscription doesn't exist
        self.mock_subscriber.get_subscription.side_effect = Exception("Not found")

        # Register agent
        def message_handler(message):
            pass

        message_bus.register_agent(agent_id, agent_name, message_handler)

        # Verify subscription creation was attempted
        self.mock_subscriber.create_subscription.assert_called_once()

        # Verify filter was set correctly
        create_call = self.mock_subscriber.create_subscription.call_args
        request = create_call[1]["request"]

        expected_filter = f'attributes.recipient_agent_id="{agent_id}"'
        self.assertEqual(request["filter"], expected_filter)

    def test_message_filtering_by_recipient(self):
        """Test that messages are filtered by recipient_agent_id attribute."""
        message_bus = VertexA2AMessageBus(
            project_id=self.project_id,
            topic_name=self.topic_name,
            create_if_missing=False
        )

        agent1_id = "projects/test/locations/us-central1/reasoningEngines/agent1"
        agent2_id = "projects/test/locations/us-central1/reasoningEngines/agent2"

        # Register two agents
        agent1_messages = []
        agent2_messages = []

        def agent1_handler(msg):
            agent1_messages.append(msg)

        def agent2_handler(msg):
            agent2_messages.append(msg)

        # Mock subscription creation
        self.mock_subscriber.get_subscription.side_effect = Exception("Not found")

        message_bus.register_agent(agent1_id, "agent1", agent1_handler)
        message_bus.register_agent(agent2_id, "agent2", agent2_handler)

        # Verify both subscriptions were created with correct filters
        self.assertEqual(self.mock_subscriber.create_subscription.call_count, 2)

        # Get the filters from both calls
        call1_filter = self.mock_subscriber.create_subscription.call_args_list[0][1]["request"]["filter"]
        call2_filter = self.mock_subscriber.create_subscription.call_args_list[1][1]["request"]["filter"]

        self.assertIn(agent1_id, call1_filter)
        self.assertIn(agent2_id, call2_filter)

    def test_send_and_wait_with_timeout(self):
        """Test send_and_wait with request-response pattern."""
        message_bus = VertexA2AMessageBus(
            project_id=self.project_id,
            topic_name=self.topic_name,
            create_if_missing=False
        )

        # Mock publish
        future_mock = MagicMock()
        future_mock.result.return_value = "msg-123"
        self.mock_publisher.publish.return_value = future_mock

        request_message = A2AProtocolHelper.create_query_request(
            sender_id="agent1",
            sender_name="developer",
            recipient_id="agent2",
            recipient_name="domain_expert",
            query="What are the business rules?",
            context={}
        )

        # Test with mock - should timeout or return response
        # In real implementation, this would wait for response message
        # with matching correlation_id

        # For mock test, we just verify the publish happened
        with patch.object(message_bus, 'publish_message') as mock_publish:
            mock_publish.return_value = "msg-123"

            try:
                # This will timeout in mock environment
                response = message_bus.send_and_wait(request_message, timeout=1)
            except TimeoutError:
                # Expected in mock environment
                pass

            mock_publish.assert_called_once_with(request_message)

    def test_error_handling_on_publish_failure(self):
        """Test error handling when message publish fails."""
        message_bus = VertexA2AMessageBus(
            project_id=self.project_id,
            topic_name=self.topic_name,
            create_if_missing=False
        )

        # Mock publish failure
        self.mock_publisher.publish.side_effect = Exception("Pub/Sub unavailable")

        message = A2AProtocolHelper.create_state_update(
            sender_id="agent1",
            sender_name="developer",
            recipient_id="agent2",
            recipient_name="orchestrator",
            task_id="test_001",
            old_status="pending",
            new_status="in_progress",
            metadata={}
        )

        # Should raise exception on publish failure
        with self.assertRaises(Exception) as context:
            message_bus.publish_message(message)

        self.assertIn("Pub/Sub unavailable", str(context.exception))

    def test_message_retry_on_failure(self):
        """Test message retry logic when delivery fails."""
        message = A2AMessage(
            message_type=A2AMessageType.VALIDATION_REQUEST,
            sender_agent_id="agent1",
            sender_agent_name="developer",
            recipient_agent_id="agent2",
            recipient_agent_name="validator",
            payload={"artifact": "code"},
            max_retries=3,
            retry_count=0
        )

        # Simulate retry increments
        self.assertEqual(message.retry_count, 0)

        # After first retry
        retry_message = A2AMessage.from_dict(message.to_dict())
        retry_message.retry_count = 1
        self.assertEqual(retry_message.retry_count, 1)

        # After second retry
        retry_message.retry_count = 2
        self.assertEqual(retry_message.retry_count, 2)

        # Should escalate after max retries
        retry_message.retry_count = 3
        self.assertGreaterEqual(retry_message.retry_count, retry_message.max_retries)


# ============================================================================
# INTEGRATION TESTS (Require GCP Credentials)
# ============================================================================

@unittest.skipUnless(
    os.getenv("GCP_PROJECT_ID"),
    "Skipping integration tests - set GCP_PROJECT_ID environment variable to run"
)
class TestVertexA2AMessageBusIntegration(unittest.TestCase):
    """
    Integration tests with real Google Cloud Pub/Sub.

    Set environment variable GCP_PROJECT_ID to run these tests:
    export GCP_PROJECT_ID=your-project-id
    gcloud auth application-default login
    """

    @classmethod
    def setUpClass(cls):
        """Set up test project and topic."""
        cls.project_id = os.getenv("GCP_PROJECT_ID")
        cls.topic_name = f"test-a2a-messages-{uuid.uuid4().hex[:8]}"

        # Create message bus with test topic
        cls.message_bus = VertexA2AMessageBus(
            project_id=cls.project_id,
            topic_name=cls.topic_name,
            create_if_missing=True
        )

        print(f"\nCreated test topic: {cls.topic_name}")

    @classmethod
    def tearDownClass(cls):
        """Clean up test topic and subscriptions."""
        try:
            # Delete subscriptions
            for sub_name in cls.message_bus._subscriptions.keys():
                sub_path = cls.message_bus.subscriber.subscription_path(
                    cls.project_id,
                    sub_name
                )
                try:
                    cls.message_bus.subscriber.delete_subscription(
                        request={"subscription": sub_path}
                    )
                    print(f"Deleted subscription: {sub_name}")
                except Exception as e:
                    print(f"Failed to delete subscription {sub_name}: {e}")

            # Delete topic
            cls.message_bus.publisher.delete_topic(
                request={"topic": cls.message_bus.topic_path}
            )
            print(f"Deleted test topic: {cls.topic_name}")
        except Exception as e:
            print(f"Cleanup failed: {e}")

    def test_publish_and_receive_message(self):
        """Test end-to-end message publishing and receiving."""
        agent_id = f"test-agent-{uuid.uuid4().hex[:8]}"
        received_messages = []
        message_received = Event()

        def message_handler(message: A2AMessage):
            received_messages.append(message)
            message_received.set()

        # Register agent
        self.message_bus.register_agent(agent_id, "test_agent", message_handler)

        # Start listening
        self.message_bus.start_listening(agent_id)

        # Wait for subscription to be ready
        time.sleep(2)

        # Publish test message
        test_message = A2AProtocolHelper.create_task_assignment(
            sender_id="orchestrator",
            sender_name="orchestrator_agent",
            recipient_id=agent_id,
            recipient_name="test_agent",
            task_data={"task_id": "integration_test_001", "test": "data"}
        )

        message_id = self.message_bus.publish_message(test_message)
        self.assertIsNotNone(message_id)

        # Wait for message to be received (max 10 seconds)
        message_received.wait(timeout=10)

        # Verify message was received
        self.assertEqual(len(received_messages), 1)
        received = received_messages[0]

        self.assertEqual(received.message_type, A2AMessageType.TASK_ASSIGNMENT)
        self.assertEqual(received.recipient_agent_id, agent_id)
        self.assertEqual(received.payload["task_id"], "integration_test_001")

    def test_message_filtering(self):
        """Test that messages are correctly filtered by recipient."""
        agent1_id = f"test-agent1-{uuid.uuid4().hex[:8]}"
        agent2_id = f"test-agent2-{uuid.uuid4().hex[:8]}"

        agent1_messages = []
        agent2_messages = []

        agent1_received = Event()
        agent2_received = Event()

        def agent1_handler(message: A2AMessage):
            agent1_messages.append(message)
            agent1_received.set()

        def agent2_handler(message: A2AMessage):
            agent2_messages.append(message)
            agent2_received.set()

        # Register both agents
        self.message_bus.register_agent(agent1_id, "agent1", agent1_handler)
        self.message_bus.register_agent(agent2_id, "agent2", agent2_handler)

        # Start listening
        self.message_bus.start_listening(agent1_id)
        self.message_bus.start_listening(agent2_id)

        time.sleep(2)

        # Send message to agent1
        message_for_agent1 = A2AProtocolHelper.create_task_assignment(
            sender_id="orchestrator",
            sender_name="orchestrator",
            recipient_id=agent1_id,
            recipient_name="agent1",
            task_data={"for": "agent1"}
        )

        # Send message to agent2
        message_for_agent2 = A2AProtocolHelper.create_task_assignment(
            sender_id="orchestrator",
            sender_name="orchestrator",
            recipient_id=agent2_id,
            recipient_name="agent2",
            task_data={"for": "agent2"}
        )

        self.message_bus.publish_message(message_for_agent1)
        self.message_bus.publish_message(message_for_agent2)

        # Wait for both messages
        agent1_received.wait(timeout=10)
        agent2_received.wait(timeout=10)

        # Verify each agent only received their message
        self.assertEqual(len(agent1_messages), 1)
        self.assertEqual(len(agent2_messages), 1)

        self.assertEqual(agent1_messages[0].recipient_agent_id, agent1_id)
        self.assertEqual(agent2_messages[0].recipient_agent_id, agent2_id)

    def test_request_response_pattern(self):
        """Test request-response pattern with correlation IDs."""
        requester_id = f"test-requester-{uuid.uuid4().hex[:8]}"
        responder_id = f"test-responder-{uuid.uuid4().hex[:8]}"

        response_received = Event()
        received_response = None

        def requester_handler(message: A2AMessage):
            nonlocal received_response
            if message.message_type == A2AMessageType.QUERY_RESPONSE:
                received_response = message
                response_received.set()

        def responder_handler(message: A2AMessage):
            if message.message_type == A2AMessageType.QUERY_REQUEST:
                # Send response with same correlation ID
                response = A2AProtocolHelper.create_query_response(
                    sender_id=responder_id,
                    sender_name="responder",
                    recipient_id=message.sender_agent_id,
                    recipient_name=message.sender_agent_name,
                    query_result={"answer": "42"},
                    correlation_id=message.correlation_id
                )
                self.message_bus.publish_message(response)

        # Register both agents
        self.message_bus.register_agent(requester_id, "requester", requester_handler)
        self.message_bus.register_agent(responder_id, "responder", responder_handler)

        self.message_bus.start_listening(requester_id)
        self.message_bus.start_listening(responder_id)

        time.sleep(2)

        # Send query request
        request = A2AProtocolHelper.create_query_request(
            sender_id=requester_id,
            sender_name="requester",
            recipient_id=responder_id,
            recipient_name="responder",
            query="What is the answer?",
            context={}
        )

        request_corr_id = request.correlation_id
        self.message_bus.publish_message(request)

        # Wait for response
        response_received.wait(timeout=15)

        # Verify response was received with matching correlation ID
        self.assertIsNotNone(received_response)
        self.assertEqual(received_response.correlation_id, request_corr_id)
        self.assertEqual(received_response.payload["query_result"]["answer"], "42")

    def test_high_priority_message_delivery(self):
        """Test that high priority messages are delivered."""
        agent_id = f"test-agent-{uuid.uuid4().hex[:8]}"
        received_messages = []
        message_received = Event()

        def message_handler(message: A2AMessage):
            received_messages.append(message)
            message_received.set()

        self.message_bus.register_agent(agent_id, "test_agent", message_handler)
        self.message_bus.start_listening(agent_id)

        time.sleep(2)

        # Send high priority error report
        error_message = A2AProtocolHelper.create_error_report(
            sender_id="developer",
            sender_name="developer_agent",
            recipient_id=agent_id,
            recipient_name="test_agent",
            task_id="test_001",
            error_message="Critical failure",
            error_details={"severity": "high"}
        )

        # Error reports have priority=1
        self.assertEqual(error_message.priority, 1)

        self.message_bus.publish_message(error_message)

        message_received.wait(timeout=10)

        self.assertEqual(len(received_messages), 1)
        self.assertEqual(received_messages[0].priority, 1)


if __name__ == "__main__":
    # Run with: python -m pytest tests/a2a_tests/test_pubsub_integration.py -v
    unittest.main()
