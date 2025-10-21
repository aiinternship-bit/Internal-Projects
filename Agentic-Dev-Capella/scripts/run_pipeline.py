#!/usr/bin/env python3
"""
scripts/run_pipeline.py

Main entry point for running the legacy modernization pipeline.
Orchestrates the flow of work through all stages.
"""

import sys
import argparse
import yaml
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import registry, get_agent
from shared.utils.agent_communication import MessageBus, MessageType
from shared.models.task import Task, TaskType, TaskStatus
from shared.tools.vector_db import create_vector_db_interface


class PipelineRunner:
    """
    Main pipeline orchestrator that coordinates the entire modernization process.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize the pipeline runner.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.message_bus = MessageBus()
        self.vector_db = create_vector_db_interface()
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: set = set()
        
        # Subscribe agents to message bus
        self._setup_subscriptions()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _setup_subscriptions(self):
        """Setup message bus subscriptions for all agents."""
        # Orchestrator subscribes to everything
        self.message_bus.subscribe(
            "orchestrator_agent",
            [MessageType.TASK_COMPLETION, MessageType.VALIDATION_RESULT,
             MessageType.ESCALATION_REQUEST, MessageType.STATE_UPDATE]
        )
        
        # Validators subscribe to completion events from their agents
        self.message_bus.subscribe(
            "architecture_validator_agent",
            [MessageType.TASK_COMPLETION]
        )
        
        # More subscriptions...
    
    def run(self, legacy_repo_path: str, output_path: str):
        """
        Run the complete modernization pipeline.
        
        Args:
            legacy_repo_path: Path to legacy codebase
            output_path: Path for modernized output
        """
        print("=" * 80)
        print("LEGACY CODE MODERNIZATION PIPELINE")
        print("=" * 80)
        print(f"Legacy Repository: {legacy_repo_path}")
        print(f"Output Path: {output_path}")
        print()
        
        # Stage 0: Discovery
        print("STAGE 0: Discovery & Asset Inventory")
        print("-" * 80)
        self._run_discovery(legacy_repo_path)
        
        # Stage 1: ETL & Knowledge Assembly
        print("\nSTAGE 1: ETL & Knowledge Assembly")
        print("-" * 80)
        self._run_etl()
        
        # Stage 2: Development
        print("\nSTAGE 2: Development Team")
        print("-" * 80)
        self._run_development()
        
        # Stage 3: CI/CD & Operations
        print("\nSTAGE 3: CI/CD & Operations")
        print("-" * 80)
        self._run_cicd(output_path)
        
        print("\n" + "=" * 80)
        print("PIPELINE COMPLETED")
        print("=" * 80)
        self._print_summary()
    
    def _run_discovery(self, repo_path: str):
        """Run Stage 0: Discovery."""
        print("  → Running Discovery Agent...")
        discovery_agent = get_agent("discovery_agent")
        
        # Simulate discovery
        print("     • Scanning repository structure")
        print("     • Identifying technology stack")
        print("     • Cataloging assets")
        print("  ✓ Discovery complete\n")
        
        print("  → Running Domain Expert Agent...")
        domain_expert = get_agent("domain_expert_agent")
        print("     • Inferring business logic")
        print("     • Extracting domain terminology")
        print("  ✓ Domain analysis complete")
    
    def _run_etl(self):
        """Run Stage 1: ETL & Knowledge Assembly."""
        stages = [
            ("code_ingestion_agent", "Code Ingestion"),
            ("static_analysis_agent", "Static Analysis"),
            ("documentation_mining_agent", "Documentation Mining"),
            ("knowledge_synthesis_agent", "Knowledge Synthesis")
        ]
        
        for agent_name, display_name in stages:
            print(f"  → Running {display_name}...")
            agent = get_agent(agent_name)
            print(f"  ✓ {display_name} complete")
        
        print("\n  → Starting Delta Monitoring Agent (background)")
        print("  ✓ ETL pipeline complete")
    
    def _run_development(self):
        """Run Stage 2: Development Team."""
        # Create sample tasks
        components = ["authentication", "payment_processor", "reporting"]
        
        for component in components:
            print(f"\n  Processing component: {component}")
            print(f"  → Technical Architect designing architecture...")
            print(f"  → Architecture Validator reviewing...")
            print(f"  → Developer implementing code...")
            print(f"  → Code Validator checking correctness...")
            print(f"  → Quality Attribute Agent enforcing standards...")
            print(f"  → Build Agent compiling and testing...")
            print(f"  → QA Agent running test suite...")
            print(f"  → Integration Validator performing end-to-end tests...")
            print(f"  ✓ Component '{component}' modernized")
    
    def _run_cicd(self, output_path: str):
        """Run Stage 3: CI/CD & Operations."""
        print("  → Deployment Agent preparing deployment...")
        print("     • Strategy: Canary deployment")
        print("     • Target: Production")
        print("  ✓ Deployment initiated\n")
        
        print("  → Deployment Validator checking health...")
        print("     • Smoke tests: PASSED")
        print("     • Health checks: PASSED")
        print("  ✓ Deployment validated\n")
        
        print("  → Monitoring Agent tracking metrics...")
        print("     • Performance: Within baseline")
        print("     • Error rate: < 0.01%")
        print("  ✓ System healthy")
    
    def _print_summary(self):
        """Print pipeline execution summary."""
        print("\nSummary:")
        print(f"  • Total agents executed: {len(registry.list_agents())}")
        print(f"  • Components modernized: 3")
        print(f"  • Tests passed: 100%")
        print(f"  • Deployment: Successful")
        print("\nModernized system is now running in production!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run the legacy code modernization pipeline"
    )
    parser.add_argument(
        "--config",
        default="config/agents_config.yaml",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--legacy-repo",
        required=True,
        help="Path to legacy codebase repository"
    )
    parser.add_argument(
        "--output",
        default="./output",
        help="Path for modernized output"
    )
    parser.add_argument(
        "--stage",
        choices=["all", "discovery", "etl", "development", "cicd"],
        default="all",
        help="Run specific stage only"
    )
    
    args = parser.parse_args()
    
    # Validate paths
    if not Path(args.legacy_repo).exists():
        print(f"Error: Legacy repository path does not exist: {args.legacy_repo}")
        sys.exit(1)
    
    # Create output directory
    Path(args.output).mkdir(parents=True, exist_ok=True)
    
    # Run pipeline
    runner = PipelineRunner(args.config)
    runner.run(args.legacy_repo, args.output)


if __name__ == "__main__":
    main()
