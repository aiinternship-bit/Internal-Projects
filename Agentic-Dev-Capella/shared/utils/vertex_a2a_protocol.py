"""
shared/utils/vertex_a2a_protocol.py

Agent-to-Agent communication protocol for Vertex AI Agent Engine.
Uses Pub/Sub for async messaging between agents.
"""

from google.cloud import pubsub_v1
from google.cloud import aiplatform
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import uuid
import threading


class A2AMessageType(Enum):
    """Types of A2A messages."""
    TASK_ASSIGNMENT = "task_assignment"
    TASK_COMPLETION = "task_completion"
    VALIDATION_REQUEST = "validation_request"
    VALIDATION_RESULT = "validation_result"
    ESCALATION_REQUEST = "escalation_request"
    QUERY_REQUEST = "query_request"
    QUERY_RESPONSE = "query_response"
    STATE_UPDATE = "state_update"
    ERROR_REPORT = "error_report"
    HUMAN_APPROVAL_REQUEST = "human_approval_request"


@dataclass
class A2AMessage:
    """
    Standard A2A message format for Vertex AI Agent Engine.
    Compatible with Vertex AI's agent-to-agent protocol.
    """
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message_type: A2AMessageType = A2AMessageType.TASK_ASSIGNMENT
    
    # Agent routing
    sender_agent_id: str = ""  # Vertex AI agent resource ID
    recipient_agent_id: str = ""  # Vertex AI agent resource ID
    sender_agent_name: str = ""  # Human-readable name
    recipient_agent_name: str = ""  # Human-readable name
    
    # Message content
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    correlation_id: Optional[str] = None  # For request-response pairs
    requires_response: bool = False
    priority: int = 5  # 1=highest, 10=lowest
    
    # Retry and TTL
    retry_count: int = 0
    max_retries: int = 3
    ttl_seconds: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "sender_agent_id": self.sender_agent_id,
            "recipient_agent_id": self.recipient_agent_id,
            "sender_agent_name": self.sender_agent_name,
            "recipient_agent_name": self.recipient_agent_name,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "requires_response": self.requires_response,
            "priority": self.priority,
            "retry_count": self.retry_count
        }
    
    def to_json(self) -> str:
        """Convert message to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2AMessage':
        """Create message from dictionary."""
        return cls(
            message_id=data.get("message_id", str(uuid.uuid4())),
            message_type=A2AMessageType(data["message_type"]),
            sender_agent_id=data.get("sender_agent_id", ""),
            recipient_agent_id=data.get("recipient_agent_id", ""),
            sender_agent_name=data.get("sender_agent_name", ""),
            recipient_agent_name=data.get("recipient_agent_name", ""),
            payload=data.get("payload", {}),
            correlation_id=data.get("correlation_id"),
            requires_response=data.get("requires_response", False),
            priority=data.get("priority", 5)
        )


class VertexA2AMessageBus:
    """
    Message bus using Google Cloud Pub/Sub for A2A communication.
    Enables asynchronous agent-to-agent messaging.
    """
    
    def __init__(
        self,
        project_id: str,
        topic_name: str = "agent-messages",
        create_if_missing: bool = True
    ):
        """
        Initialize Pub/Sub message bus.
        
        Args:
            project_id: GCP project ID
            topic_name: Pub/Sub topic name
            create_if_missing: Create topic/subscriptions if they don't exist
        """
        self.project_id = project_id
        self.topic_name = topic_name
        
        # Initialize Pub/Sub clients
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
        
        # Topic and subscription paths
        self.topic_path = self.publisher.topic_path(project_id, topic_name)
        
        # Agent subscriptions
        self.agent_subscriptions: Dict[str, str] = {}  # agent_id -> subscription_path
        self.message_handlers: Dict[str, Callable] = {}  # agent_id -> handler function
        
        # Active subscription futures
        self.subscription_futures: Dict[str, Any] = {}
        
        if create_if_missing:
            self._ensure_topic_exists()
    
    def _ensure_topic_exists(self):
        """Create topic if it doesn't exist."""
        try:
            self.publisher.create_topic(request={"name": self.topic_path})
            print(f"Created topic: {self.topic_path}")
        except Exception as e:
            # Topic might already exist
            print(f"Topic exists or error: {e}")
    
    def register_agent(
        self,
        agent_id: str,
        agent_name: str,
        message_handler: Callable[[A2AMessage], Dict[str, Any]]
    ):
        """
        Register an agent to receive A2A messages.
        
        Args:
            agent_id: Vertex AI agent resource ID
            agent_name: Human-readable agent name
            message_handler: Function to handle incoming messages
        """
        subscription_name = f"{agent_name}-subscription"
        subscription_path = self.subscriber.subscription_path(
            self.project_id,
            subscription_name
        )
        
        # Create subscription if it doesn't exist
        try:
            self.subscriber.create_subscription(
                request={
                    "name": subscription_path,
                    "topic": self.topic_path,
                    "filter": f'attributes.recipient_agent_id="{agent_id}"'
                }
            )
            print(f"Created subscription for {agent_name}")
        except Exception as e:
            print(f"Subscription exists or error: {e}")
        
        self.agent_subscriptions[agent_id] = subscription_path
        self.message_handlers[agent_id] = message_handler
    
    def publish_message(self, message: A2AMessage) -> str:
        """
        Publish A2A message to Pub/Sub.
        
        Args:
            message: A2AMessage to publish
            
        Returns:
            str: Published message ID
        """
        # Convert message to bytes
        message_data = message.to_json().encode("utf-8")
        
        # Add attributes for filtering
        attributes = {
            "message_type": message.message_type.value,
            "sender_agent_id": message.sender_agent_id,
            "recipient_agent_id": message.recipient_agent_id,
            "priority": str(message.priority)
        }
        
        # Publish to Pub/Sub
        future = self.publisher.publish(
            self.topic_path,
            data=message_data,
            **attributes
        )
        
        # Wait for publish to complete
        message_id = future.result()
        
        return message_id
    
    def start_listening(self, agent_id: str):
        """
        Start listening for messages for a specific agent.
        
        Args:
            agent_id: Agent's Vertex AI resource ID
        """
        if agent_id not in self.agent_subscriptions:
            raise ValueError(f"Agent {agent_id} not registered")
        
        subscription_path = self.agent_subscriptions[agent_id]
        handler = self.message_handlers[agent_id]
        
        def callback(message: pubsub_v1.subscriber.message.Message):
            """Process incoming Pub/Sub message."""
            try:
                # Parse A2A message
                a2a_message = A2AMessage.from_dict(
                    json.loads(message.data.decode("utf-8"))
                )
                
                # Call agent's message handler
                response = handler(a2a_message)
                
                # If response required, send it
                if a2a_message.requires_response and response:
                    response_message = A2AMessage(
                        message_type=A2AMessageType.QUERY_RESPONSE,
                        sender_agent_id=a2a_message.recipient_agent_id,
                        recipient_agent_id=a2a_message.sender_agent_id,
                        correlation_id=a2a_message.correlation_id,
                        payload=response
                    )
                    self.publish_message(response_message)
                
                # Acknowledge message
                message.ack()
                
            except Exception as e:
                print(f"Error processing message: {e}")
                message.nack()  # Negative acknowledge for retry
        
        # Start streaming pull
        future = self.subscriber.subscribe(subscription_path, callback=callback)
        self.subscription_futures[agent_id] = future
        
        print(f"Agent {agent_id} listening for messages...")
    
    def stop_listening(self, agent_id: str):
        """
        Stop listening for messages for a specific agent.
        
        Args:
            agent_id: Agent's Vertex AI resource ID
        """
        if agent_id in self.subscription_futures:
            future = self.subscription_futures[agent_id]
            future.cancel()
            del self.subscription_futures[agent_id]
            print(f"Agent {agent_id} stopped listening")
    
    def send_and_wait(
        self,
        message: A2AMessage,
        timeout: int = 60
    ) -> Optional[Dict[str, Any]]:
        """
        Send message and wait for response (synchronous A2A).
        
        Args:
            message: A2AMessage to send
            timeout: Timeout in seconds
            
        Returns:
            Response payload or None
        """
        # Set up temporary subscription for response
        correlation_id = str(uuid.uuid4())
        message.correlation_id = correlation_id
        message.requires_response = True
        
        # Store response placeholder
        response_container = {"response": None, "received": False}
        
        def response_callback(response_msg: A2AMessage):
            if response_msg.correlation_id == correlation_id:
                response_container["response"] = response_msg.payload
                response_container["received"] = True
        
        # Publish message
        self.publish_message(message)
        
        # Wait for response (simplified - use proper async in production)
        import time
        elapsed = 0
        while elapsed < timeout and not response_container["received"]:
            time.sleep(0.1)
            elapsed += 0.1
        
        return response_container.get("response")


class A2AProtocolHelper:
    """Helper functions for common A2A communication patterns."""
    
    @staticmethod
    def create_task_assignment(
        sender_id: str,
        sender_name: str,
        recipient_id: str,
        recipient_name: str,
        task_data: Dict[str, Any]
    ) -> A2AMessage:
        """Create a task assignment message."""
        return A2AMessage(
            message_type=A2AMessageType.TASK_ASSIGNMENT,
            sender_agent_id=sender_id,
            sender_agent_name=sender_name,
            recipient_agent_id=recipient_id,
            recipient_agent_name=recipient_name,
            payload={
                "task_id": task_data.get("task_id"),
                "task_type": task_data.get("task_type"),
                "component_id": task_data.get("component_id"),
                "architecture_spec": task_data.get("architecture_spec", {}),
                "priority": task_data.get("priority", "medium"),
                "context": task_data.get("context", {})
            },
            priority=2,  # High priority
            requires_response=True
        )
    
    @staticmethod
    def create_validation_request(
        sender_id: str,
        sender_name: str,
        validator_id: str,
        validator_name: str,
        artifact: Dict[str, Any]
    ) -> A2AMessage:
        """Create a validation request message."""
        return A2AMessage(
            message_type=A2AMessageType.VALIDATION_REQUEST,
            sender_agent_id=sender_id,
            sender_agent_name=sender_name,
            recipient_agent_id=validator_id,
            recipient_agent_name=validator_name,
            payload={
                "task_id": artifact.get("task_id"),
                "artifact_type": artifact.get("type"),
                "artifact": artifact.get("content"),
                "validation_criteria": artifact.get("criteria", [])
            },
            priority=2,
            requires_response=True
        )
    
    @staticmethod
    def create_validation_result(
        validator_id: str,
        validator_name: str,
        recipient_id: str,
        recipient_name: str,
        task_id: str,
        passed: bool,
        issues: List[str] = None,
        feedback: str = None,
        correlation_id: str = None
    ) -> A2AMessage:
        """Create a validation result message."""
        return A2AMessage(
            message_type=A2AMessageType.VALIDATION_RESULT,
            sender_agent_id=validator_id,
            sender_agent_name=validator_name,
            recipient_agent_id=recipient_id,
            recipient_agent_name=recipient_name,
            payload={
                "task_id": task_id,
                "passed": passed,
                "issues": issues or [],
                "feedback": feedback,
                "validator_name": validator_name
            },
            correlation_id=correlation_id,
            priority=2
        )
    
    @staticmethod
    def create_escalation_request(
        sender_id: str,
        sender_name: str,
        task_id: str,
        reason: str,
        rejection_count: int,
        context: Dict[str, Any]
    ) -> A2AMessage:
        """Create an escalation request message."""
        return A2AMessage(
            message_type=A2AMessageType.ESCALATION_REQUEST,
            sender_agent_id=sender_id,
            sender_agent_name=sender_name,
            recipient_agent_id="escalation_agent_id",  # Set actual ID
            recipient_agent_name="escalation_agent",
            payload={
                "task_id": task_id,
                "reason": reason,
                "rejection_count": rejection_count,
                "context": context,
                "requires_human_review": rejection_count > 3
            },
            priority=1,  # Critical
            requires_response=True
        )
    
    @staticmethod
    def create_state_update(
        sender_id: str,
        sender_name: str,
        orchestrator_id: str,
        task_id: str,
        old_status: str,
        new_status: str,
        metadata: Dict[str, Any] = None
    ) -> A2AMessage:
        """Create a state update message."""
        return A2AMessage(
            message_type=A2AMessageType.STATE_UPDATE,
            sender_agent_id=sender_id,
            sender_agent_name=sender_name,
            recipient_agent_id=orchestrator_id,
            recipient_agent_name="orchestrator_agent",
            payload={
                "task_id": task_id,
                "old_status": old_status,
                "new_status": new_status,
                "metadata": metadata or {},
                "timestamp": datetime.utcnow().isoformat()
            },
            priority=5  # Normal priority
        )


class A2AAgentWrapper:
    """
    Wrapper for Vertex AI agents to enable A2A communication.
    Provides convenient methods for sending/receiving messages.
    """
    
    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        project_id: str,
        message_bus: VertexA2AMessageBus
    ):
        """
        Initialize agent wrapper.
        
        Args:
            agent_id: Vertex AI agent resource ID
            agent_name: Human-readable agent name
            project_id: GCP project ID
            message_bus: Shared message bus instance
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.project_id = project_id
        self.message_bus = message_bus
        
        # Message handling
        self.message_handlers: Dict[A2AMessageType, Callable] = {}
    
    def register_handler(
        self,
        message_type: A2AMessageType,
        handler: Callable[[A2AMessage], Dict[str, Any]]
    ):
        """
        Register a handler for a specific message type.
        
        Args:
            message_type: Type of message to handle
            handler: Function to process the message
        """
        self.message_handlers[message_type] = handler
    
    def handle_message(self, message: A2AMessage) -> Dict[str, Any]:
        """
        Route incoming message to appropriate handler.
        
        Args:
            message: Incoming A2A message
            
        Returns:
            Response dict
        """
        handler = self.message_handlers.get(message.message_type)
        
        if handler:
            return handler(message)
        else:
            return {
                "status": "error",
                "message": f"No handler for message type: {message.message_type}"
            }
    
    def send_message(self, message: A2AMessage) -> str:
        """
        Send A2A message via the message bus.
        
        Args:
            message: A2AMessage to send
            
        Returns:
            Message ID
        """
        message.sender_agent_id = self.agent_id
        message.sender_agent_name = self.agent_name
        return self.message_bus.publish_message(message)
    
    def send_and_wait(
        self,
        message: A2AMessage,
        timeout: int = 60
    ) -> Optional[Dict[str, Any]]:
        """
        Send message and wait for response.
        
        Args:
            message: A2AMessage to send
            timeout: Timeout in seconds
            
        Returns:
            Response payload
        """
        message.sender_agent_id = self.agent_id
        message.sender_agent_name = self.agent_name
        return self.message_bus.send_and_wait(message, timeout)
    
    def start_listening(self):
        """Start listening for incoming messages."""
        self.message_bus.register_agent(
            self.agent_id,
            self.agent_name,
            self.handle_message
        )
        self.message_bus.start_listening(self.agent_id)
    
    def stop_listening(self):
        """Stop listening for messages."""
        self.message_bus.stop_listening(self.agent_id)


# Example usage
def example_a2a_usage():
    """Example of using A2A protocol between agents."""
    
    # Initialize message bus
    message_bus = VertexA2AMessageBus(
        project_id="your-project-id",
        topic_name="legacy-modernization-messages"
    )
    
    # Create agent wrappers
    orchestrator = A2AAgentWrapper(
        agent_id="projects/123/locations/us-central1/agents/orchestrator",
        agent_name="orchestrator_agent",
        project_id="your-project-id",
        message_bus=message_bus
    )
    
    developer = A2AAgentWrapper(
        agent_id="projects/123/locations/us-central1/agents/developer",
        agent_name="developer_agent",
        project_id="your-project-id",
        message_bus=message_bus
    )
    
    # Register message handlers
    def handle_task_assignment(msg: A2AMessage) -> Dict[str, Any]:
        print(f"Developer received task: {msg.payload.get('task_id')}")
        # Process task...
        return {"status": "task_accepted"}
    
    developer.register_handler(
        A2AMessageType.TASK_ASSIGNMENT,
        handle_task_assignment
    )
    
    # Start listening
    developer.start_listening()
    
    # Send task from orchestrator to developer
    task_message = A2AProtocolHelper.create_task_assignment(
        sender_id=orchestrator.agent_id,
        sender_name=orchestrator.agent_name,
        recipient_id=developer.agent_id,
        recipient_name=developer.agent_name,
        task_data={
            "task_id": "task_001",
            "task_type": "development",
            "component_id": "payment_processor"
        }
    )
    
    response = orchestrator.send_and_wait(task_message)
    print(f"Response: {response}")
