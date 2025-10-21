"""
agents/__init__.py

Central package initialization for all agents.
Provides easy imports and agent registry.
"""

from typing import Dict, Any
import importlib
import os

# Import orchestration agents
# Note: orchestrator_agent is created via create_orchestrator_agent function
from .orchestration.escalation.agent import escalation_agent
from .orchestration.telemetry.agent import telemetry_agent

# Import stage 0 agents
from .stage0_discovery.discovery.agent import discovery_agent
from .stage0_discovery.domain_expert.agent import domain_expert_agent

# Import stage 1 agents
from .stage1_etl.code_ingestion.agent import code_ingestion_agent
from .stage1_etl.static_analysis.agent import static_analysis_agent
from .stage1_etl.documentation_mining.agent import documentation_mining_agent
from .stage1_etl.knowledge_synthesis.agent import knowledge_synthesis_agent
from .stage1_etl.delta_monitoring.agent import delta_monitoring_agent

# Import stage 2 agents
from .stage2_development.architecture.architect.agent import architect_agent
from .stage2_development.architecture.validator.agent import architecture_validator_agent
from .stage2_development.developer.agent import developer_agent
from .stage2_development.validation.code_validator.agent import code_validator_agent
from .stage2_development.validation.quality_attribute.agent import quality_attribute_validator_agent
from .stage2_development.build.builder.agent import builder_agent
from .stage2_development.build.validator.agent import build_validator_agent
from .stage2_development.qa.tester.agent import qa_tester_agent
from .stage2_development.qa.validator.agent import qa_validator_agent
from .stage2_development.integration.validator.agent import integration_validator_agent
from .stage2_development.integration.coordinator.agent import integration_coordinator_agent

# Import stage 3 agents
from .stage3_cicd.deployment.deployer.agent import deployer_agent
from .stage3_cicd.deployment.validator.agent import deployment_validator_agent
from .stage3_cicd.monitoring.monitor.agent import monitor_agent
from .stage3_cicd.monitoring.root_cause.agent import root_cause_agent
from .stage3_cicd.security.supply_chain.agent import supply_chain_security_agent


class AgentRegistry:
    """
    Central registry for all agents in the system.
    Provides lookup, lifecycle management, and configuration.
    """
    
    def __init__(self):
        """Initialize the agent registry."""
        self._agents: Dict[str, Any] = {}
        self._register_all_agents()
    
    def _register_all_agents(self):
        """Register all agents in the system."""
        # Orchestration
        # Note: orchestrator_agent created via factory function
        self.register("escalation_agent", escalation_agent)
        self.register("telemetry_agent", telemetry_agent)
        
        # Stage 0: Discovery
        self.register("discovery_agent", discovery_agent)
        self.register("domain_expert_agent", domain_expert_agent)
        
        # Stage 1: ETL
        self.register("code_ingestion_agent", code_ingestion_agent)
        self.register("static_analysis_agent", static_analysis_agent)
        self.register("documentation_mining_agent", documentation_mining_agent)
        self.register("knowledge_synthesis_agent", knowledge_synthesis_agent)
        self.register("delta_monitoring_agent", delta_monitoring_agent)
        
        # Stage 2: Development
        self.register("architect_agent", architect_agent)
        self.register("architecture_validator_agent", architecture_validator_agent)
        self.register("developer_agent", developer_agent)
        self.register("code_validator_agent", code_validator_agent)
        self.register("quality_attribute_validator_agent", quality_attribute_validator_agent)
        self.register("builder_agent", builder_agent)
        self.register("build_validator_agent", build_validator_agent)
        self.register("qa_tester_agent", qa_tester_agent)
        self.register("qa_validator_agent", qa_validator_agent)
        self.register("integration_validator_agent", integration_validator_agent)
        self.register("integration_coordinator_agent", integration_coordinator_agent)
        
        # Stage 3: CI/CD
        self.register("deployer_agent", deployer_agent)
        self.register("deployment_validator_agent", deployment_validator_agent)
        self.register("monitor_agent", monitor_agent)
        self.register("root_cause_agent", root_cause_agent)
        self.register("supply_chain_security_agent", supply_chain_security_agent)
    
    def register(self, name: str, agent: Any):
        """
        Register an agent.
        
        Args:
            name: Agent name/identifier
            agent: Agent instance
        """
        self._agents[name] = agent
    
    def get(self, name: str) -> Any:
        """
        Get an agent by name.
        
        Args:
            name: Agent name
            
        Returns:
            Agent instance or None if not found
        """
        return self._agents.get(name)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all registered agents."""
        return self._agents.copy()
    
    def get_by_stage(self, stage: str) -> Dict[str, Any]:
        """
        Get all agents for a specific stage.
        
        Args:
            stage: Stage name (stage0, stage1, stage2, stage3, orchestration)
            
        Returns:
            Dictionary of agents in that stage
        """
        stage_agents = {}
        for name, agent in self._agents.items():
            if stage in name.lower():
                stage_agents[name] = agent
        return stage_agents
    
    def list_agents(self) -> list:
        """Get list of all registered agent names."""
        return list(self._agents.keys())


# Create global registry instance
registry = AgentRegistry()


# Convenience functions
def get_agent(name: str):
    """Get an agent by name from the global registry."""
    return registry.get(name)


def get_all_agents():
    """Get all agents from the global registry."""
    return registry.get_all()


def get_stage_agents(stage: str):
    """Get all agents for a specific stage."""
    return registry.get_by_stage(stage)


__all__ = [
    # Registry
    'AgentRegistry',
    'registry',
    'get_agent',
    'get_all_agents',
    'get_stage_agents',

    # Orchestration
    'escalation_agent',
    'telemetry_agent',
    
    # Stage 0
    'discovery_agent',
    'domain_expert_agent',
    
    # Stage 1
    'code_ingestion_agent',
    'static_analysis_agent',
    'documentation_mining_agent',
    'knowledge_synthesis_agent',
    'delta_monitoring_agent',
    
    # Stage 2
    'architect_agent',
    'architecture_validator_agent',
    'developer_agent',
    'code_validator_agent',
    'quality_attribute_validator_agent',
    'builder_agent',
    'build_validator_agent',
    'qa_tester_agent',
    'qa_validator_agent',
    'integration_validator_agent',
    'integration_coordinator_agent',
    
    # Stage 3
    'deployer_agent',
    'deployment_validator_agent',
    'monitor_agent',
    'root_cause_agent',
    'supply_chain_security_agent',
]
