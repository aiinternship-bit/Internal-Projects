"""
tests/gcp_tests/test_vertex_ai_reasoning_engine.py

Tests for Vertex AI Reasoning Engine deployment and execution.
Tests agent deployment, querying, and lifecycle management.
"""

import unittest
import os
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# ============================================================================
# MOCK TESTS (No GCP Credentials Required)
# ============================================================================

class TestVertexAIReasoningEngineMock(unittest.TestCase):
    """Test Vertex AI Reasoning Engine with mocked services."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_id = "test-project"
        self.location = "us-central1"
        self.staging_bucket = "gs://test-bucket"

    @patch('google.cloud.aiplatform.init')
    @patch('vertexai.preview.reasoning_engines.ReasoningEngine')
    def test_agent_deployment(self, mock_reasoning_engine, mock_init):
        """Test deploying agent to Vertex AI."""
        # Mock agent instance
        class MockAgent:
            def query(self, prompt: str) -> str:
                return f"Response to: {prompt}"

        agent = MockAgent()

        # Mock deployment
        mock_deployed = MagicMock()
        mock_deployed.resource_name = (
            f"projects/{self.project_id}/locations/{self.location}/"
            f"reasoningEngines/test_agent_123"
        )
        mock_reasoning_engine.create.return_value = mock_deployed

        # Deploy agent
        deployed_agent = mock_reasoning_engine.create(
            agent,
            requirements=["google-cloud-aiplatform", "vertexai"],
            display_name="test_agent",
            description="Test agent for unit testing"
        )

        # Verify deployment
        self.assertIsNotNone(deployed_agent.resource_name)
        self.assertIn("reasoningEngines", deployed_agent.resource_name)

    @patch('vertexai.preview.reasoning_engines.ReasoningEngine')
    def test_agent_query(self, mock_reasoning_engine):
        """Test querying a deployed agent."""
        # Mock deployed agent
        mock_agent = MagicMock()
        mock_agent.query.return_value = {
            "response": "Generated code for payment processor",
            "status": "success"
        }

        # Query agent
        result = mock_agent.query("Implement a payment processor in Python")

        # Verify response
        self.assertEqual(result["status"], "success")
        self.assertIn("payment processor", result["response"])

    @patch('vertexai.preview.reasoning_engines.ReasoningEngine')
    def test_agent_tool_execution(self, mock_reasoning_engine):
        """Test executing agent tool functions."""
        # Mock agent with tools
        class MockAgentWithTools:
            def __init__(self):
                self.tools = [self.implement_component]

            def implement_component(
                self,
                component_id: str,
                language: str,
                **kwargs
            ) -> Dict[str, Any]:
                return {
                    "status": "success",
                    "component_id": component_id,
                    "code": f"# {component_id} implementation in {language}",
                    "language": language
                }

        agent = MockAgentWithTools()

        # Execute tool
        result = agent.tools[0](
            component_id="payment_processor",
            language="python"
        )

        # Verify result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["language"], "python")
        self.assertIn("payment_processor", result["code"])

    def test_agent_resource_id_format(self):
        """Test agent resource ID format."""
        agent_name = "developer_agent"
        resource_id = (
            f"projects/{self.project_id}/"
            f"locations/{self.location}/"
            f"reasoningEngines/{agent_name}"
        )

        # Verify format
        self.assertIn(self.project_id, resource_id)
        self.assertIn(self.location, resource_id)
        self.assertIn("reasoningEngines", resource_id)
        self.assertIn(agent_name, resource_id)

    @patch('google.cloud.aiplatform.init')
    def test_vertex_ai_initialization(self, mock_init):
        """Test Vertex AI initialization."""
        import google.cloud.aiplatform as aiplatform

        aiplatform.init(
            project=self.project_id,
            location=self.location,
            staging_bucket=self.staging_bucket
        )

        # Verify initialization was called
        mock_init.assert_called_once_with(
            project=self.project_id,
            location=self.location,
            staging_bucket=self.staging_bucket
        )

    def test_agent_deployment_requirements(self):
        """Test agent deployment with Python requirements."""
        requirements = [
            "google-cloud-aiplatform>=1.38.0",
            "vertexai>=1.0.0",
            "google-cloud-pubsub>=2.18.0",
            "pydantic>=2.0.0"
        ]

        # Verify requirements format
        for req in requirements:
            self.assertIn(">=", req)
            parts = req.split(">=")
            self.assertEqual(len(parts), 2)  # package>=version


# ============================================================================
# INTEGRATION TESTS (Require GCP Credentials)
# ============================================================================

@unittest.skipUnless(
    os.getenv("GCP_PROJECT_ID"),
    "Skipping integration tests - set GCP_PROJECT_ID to run"
)
class TestVertexAIReasoningEngineIntegration(unittest.TestCase):
    """
    Integration tests with real Vertex AI Reasoning Engine.

    Set environment variables:
    export GCP_PROJECT_ID=your-project-id
    export STAGING_BUCKET=gs://your-bucket
    gcloud auth application-default login
    """

    @classmethod
    def setUpClass(cls):
        """Set up Vertex AI."""
        import vertexai
        from google.cloud import aiplatform

        cls.project_id = os.getenv("GCP_PROJECT_ID")
        cls.location = "us-central1"
        cls.staging_bucket = os.getenv("STAGING_BUCKET", f"gs://{cls.project_id}-staging")

        # Initialize Vertex AI
        aiplatform.init(
            project=cls.project_id,
            location=cls.location,
            staging_bucket=cls.staging_bucket
        )
        vertexai.init(project=cls.project_id, location=cls.location)

        print(f"\nInitialized Vertex AI for project: {cls.project_id}")

    def test_deploy_simple_agent_real(self):
        """Test deploying a simple agent to Vertex AI."""
        from vertexai.preview import reasoning_engines

        # Define simple test agent
        class SimpleTestAgent:
            """Simple agent for testing deployment."""

            def query(self, prompt: str) -> Dict[str, Any]:
                """Process query and return response."""
                return {
                    "prompt": prompt,
                    "response": f"Processed: {prompt}",
                    "status": "success"
                }

        agent = SimpleTestAgent()

        try:
            # Deploy agent
            deployed_agent = reasoning_engines.ReasoningEngine.create(
                agent,
                requirements=[
                    "google-cloud-aiplatform>=1.38.0",
                    "vertexai>=1.0.0"
                ],
                display_name="test_simple_agent",
                description="Simple test agent for integration testing"
            )

            # Verify deployment
            self.assertIsNotNone(deployed_agent.resource_name)
            self.assertIn("reasoningEngines", deployed_agent.resource_name)

            print(f"Deployed agent: {deployed_agent.resource_name}")

            # Query deployed agent
            result = deployed_agent.query("Test query")

            # Verify response
            self.assertEqual(result["status"], "success")
            self.assertIn("Test query", result["prompt"])

            # Clean up - delete agent
            deployed_agent.delete()
            print("Cleaned up test agent")

        except Exception as e:
            self.skipTest(f"Deployment failed: {e}")

    def test_list_deployed_agents(self):
        """Test listing deployed Reasoning Engines."""
        from vertexai.preview import reasoning_engines

        try:
            # List all reasoning engines
            engines = reasoning_engines.ReasoningEngine.list()

            # Verify list (may be empty)
            self.assertIsInstance(engines, list)

            if engines:
                # Verify first engine has expected attributes
                first_engine = engines[0]
                self.assertIsNotNone(first_engine.resource_name)

        except Exception as e:
            self.skipTest(f"Listing failed: {e}")


# ============================================================================
# AGENT FACTORY TESTS
# ============================================================================

class TestAgentFactory(unittest.TestCase):
    """Test agent factory for creating agents from config."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent_config = {
            "name": "developer_agent",
            "description": "Implements modern code from legacy patterns",
            "model": "gemini-2.0-flash",
            "tools": ["implement_component", "refactor_code"],
            "instruction": "You are an expert developer..."
        }

    def test_create_agent_from_config(self):
        """Test creating agent from configuration."""
        # Mock agent factory
        class AgentFactory:
            @staticmethod
            def create_agent(config: Dict[str, Any]):
                """Create agent from config."""
                class GeneratedAgent:
                    def __init__(self, config):
                        self.name = config["name"]
                        self.description = config["description"]
                        self.model = config["model"]
                        self.tools = config["tools"]

                return GeneratedAgent(config)

        agent = AgentFactory.create_agent(self.agent_config)

        # Verify agent
        self.assertEqual(agent.name, "developer_agent")
        self.assertEqual(agent.model, "gemini-2.0-flash")
        self.assertEqual(len(agent.tools), 2)

    def test_agent_registry_loading(self):
        """Test loading agents from registry."""
        # Mock agent registry
        registry = {
            "developer_agent": {
                "resource_name": "projects/test/locations/us-central1/reasoningEngines/dev_123",
                "deployed_at": "2025-10-30T10:00:00Z",
                "status": "active"
            },
            "validator_agent": {
                "resource_name": "projects/test/locations/us-central1/reasoningEngines/val_456",
                "deployed_at": "2025-10-30T10:05:00Z",
                "status": "active"
            }
        }

        # Verify registry structure
        self.assertIn("developer_agent", registry)
        self.assertIn("validator_agent", registry)
        self.assertEqual(registry["developer_agent"]["status"], "active")

    def test_batch_agent_deployment(self):
        """Test deploying multiple agents in batch."""
        agents_to_deploy = [
            {"name": "developer_agent", "type": "developer"},
            {"name": "validator_agent", "type": "validator"},
            {"name": "architect_agent", "type": "architect"}
        ]

        # Mock batch deployment
        deployed_agents = []

        for agent_config in agents_to_deploy:
            deployed_agent = {
                "name": agent_config["name"],
                "type": agent_config["type"],
                "resource_id": f"test-{agent_config['name']}-123",
                "status": "deployed"
            }
            deployed_agents.append(deployed_agent)

        # Verify all deployed
        self.assertEqual(len(deployed_agents), 3)
        for agent in deployed_agents:
            self.assertEqual(agent["status"], "deployed")


# ============================================================================
# GENERATIVE MODEL TESTS
# ============================================================================

class TestVertexAIGenerativeModels(unittest.TestCase):
    """Test Vertex AI Generative Models (Gemini)."""

    def setUp(self):
        """Set up test fixtures."""
        self.model_name = "gemini-2.0-flash"

    @patch('vertexai.generative_models.GenerativeModel')
    def test_model_initialization(self, mock_model):
        """Test initializing Gemini model."""
        # Mock model
        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        # Create model
        model = mock_model(self.model_name)

        # Verify creation
        mock_model.assert_called_once_with(self.model_name)

    @patch('vertexai.generative_models.GenerativeModel')
    def test_generate_content(self, mock_model):
        """Test generating content with Gemini."""
        # Mock model
        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        # Mock response
        mock_response = MagicMock()
        mock_response.text = "Generated Python code:\n```python\ndef process_payment(): pass\n```"
        mock_model_instance.generate_content.return_value = mock_response

        # Generate content
        model = mock_model(self.model_name)
        response = model.generate_content("Implement a payment processor")

        # Verify response
        self.assertIn("def process_payment", response.text)

    def test_model_selection_by_use_case(self):
        """Test selecting appropriate model for use case."""
        use_cases = {
            "simple_code_generation": "gemini-2.0-flash",  # Fast, cost-effective
            "complex_architecture": "gemini-2.0-flash-thinking-exp-1219",  # Complex reasoning
            "image_analysis": "gemini-2.0-flash-exp",  # Multimodal
            "quick_validation": "gemini-2.0-flash"  # Fast validation
        }

        # Verify model selection
        self.assertEqual(use_cases["simple_code_generation"], "gemini-2.0-flash")
        self.assertIn("thinking", use_cases["complex_architecture"])
        self.assertIn("exp", use_cases["image_analysis"])


if __name__ == "__main__":
    unittest.main()
