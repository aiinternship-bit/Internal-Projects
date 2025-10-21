#!/usr/bin/env python3
"""
scripts/verify_agents.py

Quick verification that all agents are properly configured and loadable.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def verify_agents():
    """Verify all agents can be loaded."""
    print("\n" + "="*80)
    print("AGENT VERIFICATION")
    print("="*80)

    agents_to_verify = [
        # Orchestration
        ("agents.orchestration.escalation.agent", "escalation_agent"),
        ("agents.orchestration.telemetry.agent", "telemetry_agent"),

        # Stage 0
        ("agents.stage0_discovery.discovery.agent", "discovery_agent"),
        ("agents.stage0_discovery.domain_expert.agent", "domain_expert_agent"),

        # Stage 1
        ("agents.stage1_etl.code_ingestion.agent", "code_ingestion_agent"),
        ("agents.stage1_etl.static_analysis.agent", "static_analysis_agent"),
        ("agents.stage1_etl.documentation_mining.agent", "documentation_mining_agent"),
        ("agents.stage1_etl.knowledge_synthesis.agent", "knowledge_synthesis_agent"),
        ("agents.stage1_etl.delta_monitoring.agent", "delta_monitoring_agent"),

        # Stage 2
        ("agents.stage2_development.developer.agent", "developer_agent"),
        ("agents.stage2_development.architecture.architect.agent", "architect_agent"),
        ("agents.stage2_development.architecture.validator.agent", "architecture_validator_agent"),
        ("agents.stage2_development.validation.code_validator.agent", "code_validator_agent"),
        ("agents.stage2_development.validation.quality_attribute.agent", "quality_attribute_validator_agent"),
        ("agents.stage2_development.build.builder.agent", "builder_agent"),
        ("agents.stage2_development.build.validator.agent", "build_validator_agent"),
        ("agents.stage2_development.qa.tester.agent", "qa_tester_agent"),
        ("agents.stage2_development.qa.validator.agent", "qa_validator_agent"),
        ("agents.stage2_development.integration.validator.agent", "integration_validator_agent"),
        ("agents.stage2_development.integration.coordinator.agent", "integration_coordinator_agent"),

        # Stage 3
        ("agents.stage3_cicd.deployment.deployer.agent", "deployer_agent"),
        ("agents.stage3_cicd.deployment.validator.agent", "deployment_validator_agent"),
        ("agents.stage3_cicd.monitoring.monitor.agent", "monitor_agent"),
        ("agents.stage3_cicd.monitoring.root_cause.agent", "root_cause_agent"),
        ("agents.stage3_cicd.security.supply_chain.agent", "supply_chain_security_agent"),
    ]

    success_count = 0
    failed_agents = []

    for module_path, agent_name in agents_to_verify:
        try:
            # Import the module
            module = __import__(module_path, fromlist=[agent_name])

            # Get the agent
            agent = getattr(module, agent_name)

            # Verify it has tools
            num_tools = len(agent.tools) if hasattr(agent, 'tools') else 0

            print(f"✓ {agent_name:<40} ({num_tools} tools)")
            success_count += 1

        except Exception as e:
            print(f"✗ {agent_name:<40} ERROR: {str(e)}")
            failed_agents.append((agent_name, str(e)))

    print("\n" + "="*80)
    print(f"VERIFICATION COMPLETE")
    print("="*80)
    print(f"Total Agents: {len(agents_to_verify)}")
    print(f"✓ Success: {success_count}")
    print(f"✗ Failed: {len(failed_agents)}")

    if failed_agents:
        print("\nFailed Agents:")
        for agent_name, error in failed_agents:
            print(f"  - {agent_name}: {error}")
    else:
        print("\n🎉 All agents loaded successfully!")

    return len(failed_agents) == 0


if __name__ == "__main__":
    success = verify_agents()
    sys.exit(0 if success else 1)
