"""
agents/orchestration/orchestrator/agent.py

Vertex AI Agent Engine orchestrator with A2A communication.
Uses Vertex AI's native agent-to-agent protocol.
"""

from vertexai.preview import reasoning_engines
from vertexai.preview.reasoning_engines import LangchainAgent
from google.cloud import aiplatform
from typing import Dict, List, Any, Optional
import json


class OrchestratorAgent:
    """
    Central orchestrator using Vertex AI Agent Engine.
    Manages A2A communication between specialized agents.
    """
    
    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        staging_bucket: str = None
    ):
        """
        Initialize Vertex AI orchestrator.
        
        Args:
            project_id: GCP project ID
            location: Vertex AI location
            staging_bucket: GCS bucket for staging
        """
        aiplatform.init(
            project=project_id,
            location=location,
            staging_bucket=staging_bucket
        )
        
        self.project_id = project_id
        self.location = location
        self.agent_registry: Dict[str, str] = {}  # agent_name -> agent_id
        self.task_state: Dict[str, Dict] = {}
        
    def route_task(
        self,
        task_id: str,
        task_type: str,
        component_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Routes tasks to appropriate agents using A2A protocol.
        
        Args:
            task_id: Unique identifier for the task
            task_type: Type of task (architecture, development, qa, etc.)
            component_context: Context about the component being modernized
            
        Returns:
            dict: Routing decision with target agent
        """
        routing_map = {
            "discovery": "discovery_agent",
            "architecture": "technical_architect_agent",
            "development": "developer_agent",
            "validation": "code_validator_agent",
            "qa": "qa_agent",
            "integration": "integration_validator_agent",
            "deployment": "deployment_agent"
        }
        
        target_agent = routing_map.get(task_type, "unknown")
        
        if target_agent not in self.agent_registry:
            return {
                "status": "error",
                "message": f"Agent {target_agent} not registered"
            }
        
        # Send A2A message to target agent
        result = self._send_a2a_message(
            target_agent_id=self.agent_registry[target_agent],
            message_type="task_assignment",
            payload={
                "task_id": task_id,
                "task_type": task_type,
                "component_context": component_context,
                "priority": component_context.get("priority", "medium")
            }
        )
        
        return result
    
    def check_deadlock(
        self,
        task_id: str,
        rejection_count: int
    ) -> Dict[str, Any]:
        """
        Detects validation deadlocks and triggers escalation.
        
        Args:
            task_id: Task identifier
            rejection_count: Number of consecutive rejections
            
        Returns:
            dict: Deadlock status and escalation decision
        """
        ESCALATION_THRESHOLD = 3
        
        if rejection_count >= ESCALATION_THRESHOLD:
            # Send A2A message to escalation agent
            escalation_result = self._send_a2a_message(
                target_agent_id=self.agent_registry.get("escalation_agent"),
                message_type="escalation_request",
                payload={
                    "task_id": task_id,
                    "rejection_count": rejection_count,
                    "reason": "validation_deadlock",
                    "requires_human_intervention": True
                }
            )
            
            return {
                "status": "deadlock_detected",
                "task_id": task_id,
                "action": "escalated",
                "escalation_result": escalation_result
            }
        
        return {
            "status": "normal",
            "task_id": task_id,
            "rejection_count": rejection_count,
            "action": "retry"
        }
    
    def update_task_state(
        self,
        task_id: str,
        new_status: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Updates task state in Vertex AI state store.
        
        Args:
            task_id: Task identifier
            new_status: New status value
            metadata: Additional metadata to store
            
        Returns:
            dict: Confirmation of state update
        """
        self.task_state[task_id] = {
            "status": new_status,
            "metadata": metadata,
            "updated_at": metadata.get("timestamp")
        }
        
        # Persist to Vertex AI Feature Store or Cloud Firestore
        # For production use
        
        return {
            "status": "success",
            "task_id": task_id,
            "updated_status": new_status
        }
    
    def get_task_dependencies(
        self,
        task_id: str,
        component_graph: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Retrieves dependencies for hierarchical task assignment.
        
        Args:
            task_id: Task identifier
            component_graph: Graph of component dependencies
            
        Returns:
            dict: List of dependency tasks
        """
        hierarchy_levels = {
            "infrastructure": 0,
            "backend": 1,
            "integration": 2,
            "ui": 3
        }
        
        component_type = component_graph.get(task_id, {}).get("type", "backend")
        current_level = hierarchy_levels.get(component_type, 1)
        
        dependencies = []
        for dep_id, dep_info in component_graph.items():
            dep_level = hierarchy_levels.get(dep_info.get("type", "backend"), 1)
            if dep_level < current_level and dep_id in component_graph.get(task_id, {}).get("depends_on", []):
                dependencies.append(dep_id)
        
        return {
            "status": "success",
            "task_id": task_id,
            "dependencies": dependencies,
            "hierarchy_level": current_level
        }
    
    def _send_a2a_message(
        self,
        target_agent_id: str,
        message_type: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send agent-to-agent message using Vertex AI A2A protocol.
        
        Args:
            target_agent_id: Target agent's Vertex AI resource ID
            message_type: Type of message
            payload: Message payload
            
        Returns:
            dict: Response from target agent
        """
        # Use Vertex AI Agent Engine A2A communication
        try:
            # Create reasoning engine query
            query = {
                "message_type": message_type,
                "payload": payload,
                "sender": "orchestrator_agent"
            }
            
            # This would use actual Vertex AI A2A API
            # For now, simulate the response
            response = {
                "status": "success",
                "agent_id": target_agent_id,
                "response": "Message received and processing"
            }
            
            return response
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def register_agent(self, agent_name: str, agent_id: str):
        """
        Register an agent in the orchestrator's registry.
        
        Args:
            agent_name: Human-readable agent name
            agent_id: Vertex AI agent resource ID
        """
        self.agent_registry[agent_name] = agent_id


def create_orchestrator_agent(
    project_id: str,
    location: str = "us-central1"
) -> reasoning_engines.ReasoningEngine:
    """
    Create and deploy orchestrator agent to Vertex AI Agent Engine.
    
    Args:
        project_id: GCP project ID
        location: Vertex AI location
        
    Returns:
        ReasoningEngine instance
    """
    orchestrator = OrchestratorAgent(
        project_id=project_id,
        location=location
    )
    
    # Define agent tools
    tools = [
        {
            "function_declarations": [
                {
                    "name": "route_task",
                    "description": "Routes tasks to appropriate agents based on task type and dependencies",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string"},
                            "task_type": {"type": "string"},
                            "component_context": {"type": "object"}
                        },
                        "required": ["task_id", "task_type"]
                    }
                },
                {
                    "name": "check_deadlock",
                    "description": "Detects validation deadlocks and triggers escalation",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string"},
                            "rejection_count": {"type": "integer"}
                        },
                        "required": ["task_id", "rejection_count"]
                    }
                },
                {
                    "name": "update_task_state",
                    "description": "Updates task state in the central state store",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string"},
                            "new_status": {"type": "string"},
                            "metadata": {"type": "object"}
                        },
                        "required": ["task_id", "new_status"]
                    }
                }
            ]
        }
    ]
    
    # Create reasoning engine with orchestrator logic
    reasoning_engine = reasoning_engines.ReasoningEngine.create(
        orchestrator,
        requirements=[
            "google-cloud-aiplatform",
            "vertexai"
        ],
        display_name="orchestrator_agent",
        description="Central orchestrator for legacy modernization pipeline"
    )
    
    return reasoning_engine
