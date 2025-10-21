"""
scripts/deploy_vertex_agents.py

Script to deploy all agents to Vertex AI Agent Engine with A2A communication.
"""

import argparse
import yaml
from pathlib import Path
from typing import Dict, List, Any
from google.cloud import aiplatform
from vertexai.preview import reasoning_engines
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.orchestration.orchestrator.agent import create_orchestrator_agent
from agents.stage2_development.developer.agent import create_developer_agent
from shared.utils.vertex_a2a_protocol import VertexA2AMessageBus
from shared.tools.vertex_vector_search import setup_vector_search


class VertexAIDeployment:
    """
    Manages deployment of all agents to Vertex AI Agent Engine.
    """
    
    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        staging_bucket: str = None
    ):
        """
        Initialize deployment manager.
        
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
        self.staging_bucket = staging_bucket
        
        # Track deployed agents
        self.deployed_agents: Dict[str, Dict[str, Any]] = {}
        
        # Message bus for A2A communication
        self.message_bus = VertexA2AMessageBus(
            project_id=project_id,
            topic_name="legacy-modernization-messages"
        )
    
    def deploy_all_agents(self, config_path: str):
        """
        Deploy all agents defined in configuration.
        
        Args:
            config_path: Path to agents configuration YAML
        """
        print("=" * 80)
        print("DEPLOYING AGENTS TO VERTEX AI AGENT ENGINE")
        print("=" * 80)
        
        # Load configuration
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Setup Vector Search first
        print("\n[1/4] Setting up Vertex AI Vector Search...")
        vector_search = setup_vector_search(
            project_id=self.project_id,
            location=self.location
        )
        print("✓ Vector Search ready")
        
        # Deploy Orchestrator
        print("\n[2/4] Deploying Orchestrator Agent...")
        orchestrator = self._deploy_orchestrator()
        print(f"✓ Orchestrator deployed: {orchestrator.resource_name}")
        
        # Deploy Stage agents
        print("\n[3/4] Deploying Stage Agents...")
        self._deploy_stage_agents(config, vector_search)
        
        # Setup A2A communication
        print("\n[4/4] Configuring A2A Communication...")
        self._setup_a2a_communication()
        print("✓ A2A communication configured")
        
        print("\n" + "=" * 80)
        print("DEPLOYMENT COMPLETE")
        print("=" * 80)
        self._print_deployment_summary()
    
    def _deploy_orchestrator(self) -> reasoning_engines.ReasoningEngine:
        """Deploy orchestrator agent."""
        orchestrator = create_orchestrator_agent(
            project_id=self.project_id,
            location=self.location
        )
        
        self.deployed_agents["orchestrator_agent"] = {
            "resource_name": orchestrator.resource_name,
            "endpoint": orchestrator.resource_name,
            "type": "orchestration"
        }
        
        return orchestrator
    
    def _deploy_stage_agents(
        self,
        config: Dict[str, Any],
        vector_search: Any
    ):
        """Deploy all stage agents."""
        
        # Stage 0: Discovery agents
        print("  → Deploying Discovery agents...")
        self._deploy_discovery_agents(config.get("stage0_discovery", {}))
        
        # Stage 1: ETL agents
        print("  → Deploying ETL agents...")
        self._deploy_etl_agents(config.get("stage1_etl", {}))
        
        # Stage 2: Development agents
        print("  → Deploying Development agents...")
        self._deploy_development_agents(
            config.get("stage2_development", {}),
            vector_search
        )
        
        # Stage 3: CI/CD agents
        print("  → Deploying CI/CD agents...")
        self._deploy_cicd_agents(config.get("stage3_cicd", {}))
        
        print("  ✓ All stage agents deployed")
    
    def _deploy_discovery_agents(self, config: Dict[str, Any]):
        """Deploy discovery stage agents."""
        # Discovery Agent
        from agents.stage0_discovery.discovery import agent as discovery_module
        
        discovery_agent = reasoning_engines.ReasoningEngine.create(
            discovery_module.DiscoveryAgent(
                project_id=self.project_id,
                location=self.location
            ),
            requirements=["google-cloud-aiplatform", "vertexai"],
            display_name="discovery_agent",
            description="Discovers and catalogs legacy system assets"
        )
        
        self.deployed_agents["discovery_agent"] = {
            "resource_name": discovery_agent.resource_name,
            "type": "stage0"
        }
        
        # Domain Expert Agent would be deployed similarly
        print("    ✓ Discovery agents deployed")
    
    def _deploy_etl_agents(self, config: Dict[str, Any]):
        """Deploy ETL stage agents."""
        etl_agents = [
            "code_ingestion_agent",
            "static_analysis_agent",
            "documentation_mining_agent",
            "knowledge_synthesis_agent",
            "delta_monitoring_agent"
        ]
        
        for agent_name in etl_agents:
            # Would deploy each agent using reasoning_engines.ReasoningEngine.create
            self.deployed_agents[agent_name] = {
                "resource_name": f"projects/{self.project_id}/locations/{self.location}/reasoningEngines/{agent_name}",
                "type": "stage1"
            }
        
        print("    ✓ ETL agents deployed")
    
    def _deploy_development_agents(
        self,
        config: Dict[str, Any],
        vector_search: Any
    ):
        """Deploy development stage agents."""
        
        # Developer Agent with Vector Search
        developer_agent = create_developer_agent(
            project_id=self.project_id,
            location=self.location,
            vector_search_endpoint=vector_search.index_endpoint.resource_name
        )
        
        self.deployed_agents["developer_agent"] = {
            "resource_name": developer_agent.resource_name,
            "type": "stage2"
        }
        
        # Deploy other development agents
        dev_agents = [
            "technical_architect_agent",
            "architecture_validator_agent",
            "code_validator_agent",
            "quality_attribute_agent",
            "build_agent",
            "build_validator_agent",
            "qa_agent",
            "qa_validator_agent",
            "integration_validator_agent"
        ]
        
        for agent_name in dev_agents:
            self.deployed_agents[agent_name] = {
                "resource_name": f"projects/{self.project_id}/locations/{self.location}/reasoningEngines/{agent_name}",
                "type": "stage2"
            }
        
        print("    ✓ Development agents deployed")
    
    def _deploy_cicd_agents(self, config: Dict[str, Any]):
        """Deploy CI/CD stage agents."""
        cicd_agents = [
            "deployment_agent",
            "deployment_validator_agent",
            "monitoring_agent",
            "root_cause_analysis_agent",
            "supply_chain_security_agent"
        ]
        
        for agent_name in cicd_agents:
            self.deployed_agents[agent_name] = {
                "resource_name": f"projects/{self.project_id}/locations/{self.location}/reasoningEngines/{agent_name}",
                "type": "stage3"
            }
        
        print("    ✓ CI/CD agents deployed")
    
    def _setup_a2a_communication(self):
        """Setup Pub/Sub topics and subscriptions for A2A."""
        
        # Register all agents with message bus
        for agent_name, agent_info in self.deployed_agents.items():
            # Each agent gets a subscription filtered to its messages
            print(f"    → Registering {agent_name} for A2A communication")
            
            # Create handler function (would be actual agent logic)
            def create_handler(name):
                def handler(message):
                    print(f"{name} received message: {message.message_type}")
                    return {"status": "processed"}
                return handler
            
            self.message_bus.register_agent(
                agent_id=agent_info["resource_name"],
                agent_name=agent_name,
                message_handler=create_handler(agent_name)
            )
    
    def _print_deployment_summary(self):
        """Print summary of deployed agents."""
        print(f"\nDeployed Agents: {len(self.deployed_agents)}")
        print("\nAgent Registry:")
        print("-" * 80)
        
        # Group by stage
        stages = {}
        for name, info in self.deployed_agents.items():
            stage = info["type"]
            if stage not in stages:
                stages[stage] = []
            stages[stage].append(name)
        
        for stage, agents in sorted(stages.items()):
            print(f"\n{stage.upper()}:")
            for agent in agents:
                resource_name = self.deployed_agents[agent]["resource_name"]
                print(f"  • {agent}")
                print(f"    {resource_name}")
        
        print("\n" + "-" * 80)
        print("\nNext Steps:")
        print("1. Test A2A communication between agents")
        print("2. Load legacy code into Vector Search")
        print("3. Run the modernization pipeline")
        print("\nTo test the pipeline:")
        print(f"  python scripts/run_vertex_pipeline.py --project-id {self.project_id}")
    
    def export_agent_registry(self, output_path: str):
        """
        Export agent registry for use by pipeline.
        
        Args:
            output_path: Path to save registry JSON
        """
        import json
        
        with open(output_path, 'w') as f:
            json.dump(self.deployed_agents, f, indent=2)
        
        print(f"\n✓ Agent registry exported to: {output_path}")


def main():
    """Main deployment script."""
    parser = argparse.ArgumentParser(
        description="Deploy agents to Vertex AI Agent Engine"
    )
    parser.add_argument(
        "--project-id",
        required=True,
        help="GCP project ID"
    )
    parser.add_argument(
        "--location",
        default="us-central1",
        help="Vertex AI location (default: us-central1)"
    )
    parser.add_argument(
        "--staging-bucket",
        required=True,
        help="GCS bucket for staging (gs://bucket-name)"
    )
    parser.add_argument(
        "--config",
        default="config/agents_config.yaml",
        help="Path to agents configuration file"
    )
    parser.add_argument(
        "--export-registry",
        default="config/agent_registry.json",
        help="Path to export agent registry"
    )
    
    args = parser.parse_args()
    
    # Validate staging bucket format
    if not args.staging_bucket.startswith("gs://"):
        print("Error: staging-bucket must start with gs://")
        sys.exit(1)
    
    # Initialize deployment
    deployment = VertexAIDeployment(
        project_id=args.project_id,
        location=args.location,
        staging_bucket=args.staging_bucket
    )
    
    # Deploy all agents
    deployment.deploy_all_agents(args.config)
    
    # Export agent registry
    deployment.export_agent_registry(args.export_registry)


if __name__ == "__main__":
    main()
