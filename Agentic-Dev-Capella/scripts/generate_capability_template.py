#!/usr/bin/env python3
"""
scripts/generate_capability_template.py

Generates capability.py template files for agents that don't have one yet.
This script helps maintain consistency across all agent capability declarations.
"""

import os
import sys
from pathlib import Path
from typing import List, Set, Optional

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from shared.models.agent_capability import AgentType, InputModality, KBQueryStrategy


CAPABILITY_TEMPLATE = '''"""
{agent_path}/capability.py

Capability declaration for {agent_display_name}.
"""

from shared.models.agent_capability import (
    AgentCapability,
    AgentType,
    InputModality,
    KBQueryStrategy,
    KBIntegrationConfig,
    PerformanceMetrics,
    CostMetrics
)


{capability_constant_name} = AgentCapability(
    agent_id="{agent_id}",
    agent_name="{agent_display_name}",
    agent_type=AgentType.{agent_type},

    description=(
        "{description}"
    ),

    capabilities={{{capabilities}}},

    supported_languages=[{supported_languages}],

    supported_frameworks=[{supported_frameworks}],

    supported_platforms=[{supported_platforms}],

    input_modalities={{{input_modalities}}},

    output_types={{{output_types}}},

    kb_integration=KBIntegrationConfig(
        has_vector_db_access={has_kb},
        kb_query_strategy=KBQueryStrategy.{kb_strategy},
        kb_query_frequency={kb_frequency},
        kb_query_triggers={kb_triggers},
        max_kb_queries_per_task={max_kb_queries},
        enable_kb_caching={enable_kb_caching},
        kb_cache_ttl_seconds={kb_cache_ttl}
    ),

    performance_metrics=PerformanceMetrics(
        total_tasks_completed=0,
        total_tasks_failed=0,
        avg_task_duration_minutes={avg_duration},
        p95_task_duration_minutes={p95_duration},
        success_rate={success_rate},
        avg_validation_failures={avg_validation_failures},
        retry_rate={retry_rate}
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd={avg_cost},
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks={max_concurrent},
    estimated_task_duration_minutes={avg_duration},

    version="1.0.0",
    deployment_region="us-central1",
    tags={tags}
)


def get_{function_name}_capability() -> AgentCapability:
    return {capability_constant_name}


def update_agent_id(vertex_ai_resource_id: str) -> None:
    {capability_constant_name}.agent_id = vertex_ai_resource_id
'''


# Agent specifications database
AGENT_SPECS = {
    # Stage 0 - Discovery
    "discovery_agent": {
        "path": "agents/stage0_discovery/discovery",
        "type": "LEGACY_MODERNIZATION",
        "description": "Scans legacy codebase, identifies languages, frameworks, and creates file inventory. Entry point for modernization pipeline.",
        "capabilities": ['"legacy_code_scanning"', '"language_detection"', '"framework_identification"', '"file_inventory"'],
        "languages": ['"cobol"', '"fortran"', '"c"', '"java"', '"python"'],
        "frameworks": [],
        "platforms": ['"mainframe"', '"on-premise"'],
        "input_modalities": ["InputModality.CODE", "InputModality.TEXT"],
        "output_types": ['"inventory"', '"metadata"', '"scan_report"'],
        "kb_strategy": "MINIMAL",
        "kb_frequency": 5,
        "avg_duration": 10.0,
        "tags": ['"stage0"', '"discovery"', '"legacy"'],
    },
    "domain_expert_agent": {
        "path": "agents/stage0_discovery/domain_expert",
        "type": "LEGACY_MODERNIZATION",
        "description": "Infers business domain from legacy code analysis. Identifies domain patterns and business logic.",
        "capabilities": ['"domain_inference"', '"business_logic_identification"', '"pattern_recognition"'],
        "languages": [],
        "frameworks": [],
        "platforms": [],
        "input_modalities": ["InputModality.TEXT", "InputModality.CODE"],
        "output_types": ['"domain_model"', '"business_rules"', '"glossary"'],
        "kb_strategy": "ADAPTIVE",
        "kb_frequency": 10,
        "avg_duration": 12.0,
        "tags": ['"stage0"', '"discovery"', '"domain"'],
    },

    # Stage 1 - ETL
    "code_ingestion_agent": {
        "path": "agents/stage1_etl/code_ingestion",
        "type": "LEGACY_MODERNIZATION",
        "description": "Parses and catalogs legacy code. Creates structured representation of codebase for analysis.",
        "capabilities": ['"code_parsing"', '"ast_generation"', '"code_cataloging"', '"metadata_extraction"'],
        "languages": ['"cobol"', '"fortran"', '"c"', '"java"'],
        "frameworks": [],
        "platforms": [],
        "input_modalities": ["InputModality.CODE"],
        "output_types": ['"ast"', '"catalog"', '"metadata"'],
        "kb_strategy": "MINIMAL",
        "kb_frequency": 3,
        "avg_duration": 15.0,
        "tags": ['"stage1"', '"etl"', '"parsing"'],
    },
    "static_analysis_agent": {
        "path": "agents/stage1_etl/static_analysis",
        "type": "LEGACY_MODERNIZATION",
        "description": "Performs static code analysis on legacy codebase. Identifies code quality, complexity, and technical debt.",
        "capabilities": ['"static_analysis"', '"complexity_calculation"', '"dependency_analysis"', '"quality_metrics"'],
        "languages": ['"cobol"', '"fortran"', '"c"', '"java"'],
        "frameworks": [],
        "platforms": [],
        "input_modalities": ["InputModality.CODE"],
        "output_types": ['"analysis_report"', '"metrics"', '"dependencies"'],
        "kb_strategy": "ADAPTIVE",
        "kb_frequency": 8,
        "avg_duration": 20.0,
        "tags": ['"stage1"', '"etl"', '"analysis"'],
    },
    "documentation_mining_agent": {
        "path": "agents/stage1_etl/documentation_mining",
        "type": "LEGACY_MODERNIZATION",
        "description": "Extracts and analyzes documentation from legacy codebase. Mines comments, READMEs, and external docs.",
        "capabilities": ['"documentation_extraction"', '"comment_analysis"', '"knowledge_extraction"'],
        "languages": [],
        "frameworks": [],
        "platforms": [],
        "input_modalities": ["InputModality.TEXT", "InputModality.CODE", "InputModality.PDF"],
        "output_types": ['"documentation"', '"knowledge_base"', '"glossary"'],
        "kb_strategy": "ADAPTIVE",
        "kb_frequency": 10,
        "avg_duration": 18.0,
        "tags": ['"stage1"', '"etl"', '"documentation"'],
    },
    "knowledge_synthesis_agent": {
        "path": "agents/stage1_etl/knowledge_synthesis",
        "type": "LEGACY_MODERNIZATION",
        "description": "Synthesizes knowledge from all ETL sources. Creates Vector Search index for semantic code search.",
        "capabilities": ['"knowledge_synthesis"', '"vector_embeddings"', '"semantic_indexing"'],
        "languages": [],
        "frameworks": [],
        "platforms": [],
        "input_modalities": ["InputModality.TEXT", "InputModality.CODE", "InputModality.JSON"],
        "output_types": ['"vector_index"', '"knowledge_graph"', '"embeddings"'],
        "kb_strategy": "ALWAYS_QUERY",
        "kb_frequency": 20,
        "avg_duration": 25.0,
        "tags": ['"stage1"', '"etl"', '"synthesis"'],
    },
    "delta_monitoring_agent": {
        "path": "agents/stage1_etl/delta_monitoring",
        "type": "LEGACY_MODERNIZATION",
        "description": "Monitors changes in legacy codebase during modernization. Tracks deltas and updates knowledge base.",
        "capabilities": ['"change_detection"', '"diff_analysis"', '"incremental_updates"'],
        "languages": [],
        "frameworks": [],
        "platforms": [],
        "input_modalities": ["InputModality.CODE"],
        "output_types": ['"change_report"', '"diff"', '"updates"'],
        "kb_strategy": "ADAPTIVE",
        "kb_frequency": 5,
        "avg_duration": 8.0,
        "tags": ['"stage1"', '"etl"', '"monitoring"'],
    },

    # Stage 2 - Development
    "architecture_validator_agent": {
        "path": "agents/stage2_development/architect_validator",
        "type": "VALIDATOR",
        "description": "Validates architecture designs for correctness, completeness, and best practices.",
        "capabilities": ['"architecture_validation"', '"design_review"', '"best_practices_checking"'],
        "languages": [],
        "frameworks": [],
        "platforms": [],
        "input_modalities": ["InputModality.JSON", "InputModality.YAML", "InputModality.TEXT"],
        "output_types": ['"validation_report"', '"feedback"', '"recommendations"'],
        "kb_strategy": "ADAPTIVE",
        "kb_frequency": 12,
        "avg_duration": 12.0,
        "tags": ['"stage2"', '"validation"', '"architecture"'],
    },
    "code_validator_agent": {
        "path": "agents/stage2_development/code_validator",
        "type": "VALIDATOR",
        "description": "Validates generated code for correctness, syntax, and functional requirements.",
        "capabilities": ['"code_validation"', '"syntax_checking"', '"functional_verification"'],
        "languages": ['"python"', '"typescript"', '"java"', '"go"'],
        "frameworks": [],
        "platforms": [],
        "input_modalities": ["InputModality.CODE"],
        "output_types": ['"validation_report"', '"feedback"', '"errors"'],
        "kb_strategy": "ADAPTIVE",
        "kb_frequency": 10,
        "avg_duration": 10.0,
        "tags": ['"stage2"', '"validation"', '"code"'],
    },
    "quality_attribute_validator_agent": {
        "path": "agents/stage2_development/quality_attribute_validator",
        "type": "VALIDATOR",
        "description": "Validates non-functional requirements: performance, security, maintainability, scalability.",
        "capabilities": ['"nfr_validation"', '"quality_checking"', '"performance_analysis"', '"security_review"'],
        "languages": [],
        "frameworks": [],
        "platforms": [],
        "input_modalities": ["InputModality.CODE", "InputModality.JSON"],
        "output_types": ['"validation_report"', '"nfr_scores"', '"recommendations"'],
        "kb_strategy": "ADAPTIVE",
        "kb_frequency": 15,
        "avg_duration": 15.0,
        "tags": ['"stage2"', '"validation"', '"quality"'],
    },
    "build_validator_agent": {
        "path": "agents/stage2_development/build_validator",
        "type": "VALIDATOR",
        "description": "Validates build artifacts for completeness, dependencies, and packaging.",
        "capabilities": ['"build_validation"', '"artifact_verification"', '"dependency_checking"'],
        "languages": [],
        "frameworks": [],
        "platforms": [],
        "input_modalities": ["InputModality.CODE", "InputModality.JSON"],
        "output_types": ['"validation_report"', '"build_status"', '"errors"'],
        "kb_strategy": "MINIMAL",
        "kb_frequency": 5,
        "avg_duration": 8.0,
        "tags": ['"stage2"', '"validation"', '"build"'],
    },
    "qa_validator_agent": {
        "path": "agents/stage2_development/qa_validator",
        "type": "VALIDATOR",
        "description": "Validates test quality, coverage, and effectiveness.",
        "capabilities": ['"test_validation"', '"coverage_analysis"', '"test_quality_checking"'],
        "languages": [],
        "frameworks": [],
        "platforms": [],
        "input_modalities": ["InputModality.CODE"],
        "output_types": ['"validation_report"', '"coverage_metrics"', '"recommendations"'],
        "kb_strategy": "ADAPTIVE",
        "kb_frequency": 8,
        "avg_duration": 10.0,
        "tags": ['"stage2"', '"validation"', '"testing"'],
    },
    "integration_validator_agent": {
        "path": "agents/stage2_development/integration_validator",
        "type": "VALIDATOR",
        "description": "Validates integration points, API contracts, and service communication.",
        "capabilities": ['"integration_validation"', '"api_contract_checking"', '"service_compatibility"'],
        "languages": [],
        "frameworks": [],
        "platforms": [],
        "input_modalities": ["InputModality.CODE", "InputModality.JSON", "InputModality.YAML"],
        "output_types": ['"validation_report"', '"contract_violations"', '"recommendations"'],
        "kb_strategy": "ADAPTIVE",
        "kb_frequency": 10,
        "avg_duration": 12.0,
        "tags": ['"stage2"', '"validation"', '"integration"'],
    },
    "multi_service_coordinator_agent": {
        "path": "agents/stage2_development/multi_service_coordinator",
        "type": "BACKEND_ENGINEER",
        "description": "Coordinates deployment of multiple services. Manages dependencies and orchestrates rollout.",
        "capabilities": ['"service_orchestration"', '"dependency_management"', '"rollout_coordination"'],
        "languages": [],
        "frameworks": [],
        "platforms": ['"kubernetes"', '"cloud"'],
        "input_modalities": ["InputModality.JSON", "InputModality.YAML"],
        "output_types": ['"deployment_plan"', '"orchestration_config"', '"status"'],
        "kb_strategy": "ADAPTIVE",
        "kb_frequency": 8,
        "avg_duration": 15.0,
        "tags": ['"stage2"', '"coordination"', '"deployment"'],
    },
    "technical_architect_agent": {
        "path": "agents/stage2_development/technical_architect",
        "type": "BACKEND_ENGINEER",
        "description": "Designs modern architecture from legacy code analysis. Creates microservices, APIs, and data models.",
        "capabilities": ['"architecture_design"', '"microservices_decomposition"', '"api_design"', '"data_modeling"'],
        "languages": [],
        "frameworks": [],
        "platforms": [],
        "input_modalities": ["InputModality.TEXT", "InputModality.JSON", "InputModality.CODE"],
        "output_types": ['"architecture_spec"', '"component_design"', '"api_spec"'],
        "kb_strategy": "ADAPTIVE",
        "kb_frequency": 15,
        "avg_duration": 30.0,
        "tags": ['"stage2"', '"architecture"', '"design"'],
    },
    "builder_agent": {
        "path": "agents/stage2_development/builder",
        "type": "DEVOPS_ENGINEER",
        "description": "Builds and packages modern code. Generates build scripts, Dockerfiles, and CI/CD configs.",
        "capabilities": ['"build_automation"', '"docker_generation"', '"ci_cd_config"', '"artifact_packaging"'],
        "languages": [],
        "frameworks": ['"docker"', '"gradle"', '"maven"', '"npm"'],
        "platforms": ['"kubernetes"', '"cloud"'],
        "input_modalities": ["InputModality.CODE"],
        "output_types": ['"dockerfile"', '"build_script"', '"ci_config"', '"artifacts"'],
        "kb_strategy": "ADAPTIVE",
        "kb_frequency": 8,
        "avg_duration": 10.0,
        "tags": ['"stage2"', '"build"', '"ci_cd"'],
    },
    "qa_tester_agent": {
        "path": "agents/stage2_development/qa_tester",
        "type": "QA_ENGINEER",
        "description": "Generates and runs comprehensive tests. Creates unit, integration, and E2E tests.",
        "capabilities": ['"test_generation"', '"test_execution"', '"test_reporting"', '"coverage_analysis"'],
        "languages": ['"python"', '"typescript"', '"java"'],
        "frameworks": ['"pytest"', '"jest"', '"junit"'],
        "platforms": [],
        "input_modalities": ["InputModality.CODE"],
        "output_types": ['"test_suite"', '"test_report"', '"coverage_report"'],
        "kb_strategy": "ADAPTIVE",
        "kb_frequency": 10,
        "avg_duration": 15.0,
        "tags": ['"stage2"', '"testing"', '"qa"'],
    },

    # Stage 3 - CI/CD
    "deployment_validator_agent": {
        "path": "agents/stage3_cicd/deployment_validator",
        "type": "VALIDATOR",
        "description": "Validates deployments for correctness, health, and readiness.",
        "capabilities": ['"deployment_validation"', '"health_checking"', '"readiness_verification"'],
        "languages": [],
        "frameworks": [],
        "platforms": ['"kubernetes"', '"cloud"'],
        "input_modalities": ["InputModality.JSON", "InputModality.YAML"],
        "output_types": ['"validation_report"', '"health_status"', '"errors"'],
        "kb_strategy": "MINIMAL",
        "kb_frequency": 5,
        "avg_duration": 8.0,
        "tags": ['"stage3"', '"validation"', '"deployment"'],
    },
    "deployment_agent": {
        "path": "agents/stage3_cicd/deployment",
        "type": "DEVOPS_ENGINEER",
        "description": "Deploys services to cloud platforms. Manages Kubernetes deployments and cloud resources.",
        "capabilities": ['"deployment_automation"', '"kubernetes_deployment"', '"cloud_provisioning"'],
        "languages": [],
        "frameworks": ['"kubernetes"', '"terraform"', '"helm"'],
        "platforms": ['"gcp"', '"aws"', '"azure"', '"kubernetes"'],
        "input_modalities": ["InputModality.YAML", "InputModality.JSON"],
        "output_types": ['"deployment_manifest"', '"deployment_status"', '"logs"'],
        "kb_strategy": "ADAPTIVE",
        "kb_frequency": 8,
        "avg_duration": 12.0,
        "tags": ['"stage3"', '"deployment"', '"devops"'],
    },
    "monitoring_agent": {
        "path": "agents/stage3_cicd/monitoring",
        "type": "DEVOPS_ENGINEER",
        "description": "Sets up monitoring, alerting, and observability. Configures Prometheus, Grafana, and Cloud Monitoring.",
        "capabilities": ['"monitoring_setup"', '"alerting_config"', '"dashboard_creation"', '"slo_definition"'],
        "languages": [],
        "frameworks": ['"prometheus"', '"grafana"', '"cloud-monitoring"'],
        "platforms": ['"kubernetes"', '"cloud"'],
        "input_modalities": ["InputModality.YAML", "InputModality.JSON"],
        "output_types": ['"monitoring_config"', '"dashboards"', '"alert_rules"'],
        "kb_strategy": "ADAPTIVE",
        "kb_frequency": 10,
        "avg_duration": 15.0,
        "tags": ['"stage3"', '"monitoring"', '"observability"'],
    },
    "root_cause_analysis_agent": {
        "path": "agents/stage3_cicd/root_cause_analysis",
        "type": "DEVOPS_ENGINEER",
        "description": "Performs root cause analysis on incidents and failures. Analyzes logs, metrics, and traces.",
        "capabilities": ['"rca_analysis"', '"log_analysis"', '"metric_correlation"', '"incident_investigation"'],
        "languages": [],
        "frameworks": [],
        "platforms": [],
        "input_modalities": ["InputModality.TEXT", "InputModality.JSON"],
        "output_types": ['"rca_report"', '"findings"', '"recommendations"'],
        "kb_strategy": "ADAPTIVE",
        "kb_frequency": 12,
        "avg_duration": 20.0,
        "tags": ['"stage3"', '"rca"', '"incident"'],
    },
    "supply_chain_security_agent": {
        "path": "agents/stage3_cicd/security/supply_chain",
        "type": "SECURITY_ENGINEER",
        "description": "Scans dependencies for vulnerabilities. Ensures supply chain security compliance.",
        "capabilities": ['"dependency_scanning"', '"vulnerability_detection"', '"sbom_generation"', '"license_checking"'],
        "languages": [],
        "frameworks": [],
        "platforms": [],
        "input_modalities": ["InputModality.CODE", "InputModality.JSON"],
        "output_types": ['"security_report"', '"vulnerabilities"', '"sbom"'],
        "kb_strategy": "ADAPTIVE",
        "kb_frequency": 10,
        "avg_duration": 12.0,
        "tags": ['"stage3"', '"security"', '"supply_chain"'],
    },

    # Orchestration
    "orchestrator_agent": {
        "path": "agents/orchestration/orchestrator",
        "type": "ORCHESTRATOR",
        "description": "Main orchestrator supporting both static (stage-based) and dynamic (capability-based) modes. Central coordinator for all agents.",
        "capabilities": ['"task_routing"', '"agent_coordination"', '"progress_tracking"', '"error_handling"'],
        "languages": [],
        "frameworks": [],
        "platforms": [],
        "input_modalities": ["InputModality.TEXT", "InputModality.JSON"],
        "output_types": ['"orchestration_plan"', '"status_updates"', '"execution_report"'],
        "kb_strategy": "ADAPTIVE",
        "kb_frequency": 5,
        "avg_duration": 5.0,
        "tags": ['"orchestration"', '"coordinator"'],
    },
    "escalation_agent": {
        "path": "agents/orchestration/escalation",
        "type": "ORCHESTRATOR",
        "description": "Handles escalations after validation failures. Routes to human review when automated resolution fails.",
        "capabilities": ['"escalation_handling"', '"human_routing"', '"deadlock_resolution"'],
        "languages": [],
        "frameworks": [],
        "platforms": [],
        "input_modalities": ["InputModality.TEXT", "InputModality.JSON"],
        "output_types": ['"escalation_report"', '"resolution_plan"'],
        "kb_strategy": "MINIMAL",
        "kb_frequency": 3,
        "avg_duration": 5.0,
        "tags": ['"orchestration"', '"escalation"'],
    },
    "telemetry_audit_agent": {
        "path": "agents/orchestration/telemetry",
        "type": "ORCHESTRATOR",
        "description": "Tracks all system activities for audit and compliance. Creates comprehensive audit trails.",
        "capabilities": ['"activity_tracking"', '"audit_logging"', '"compliance_reporting"'],
        "languages": [],
        "frameworks": [],
        "platforms": [],
        "input_modalities": ["InputModality.JSON"],
        "output_types": ['"audit_log"', '"activity_report"', '"compliance_data"'],
        "kb_strategy": "MINIMAL",
        "kb_frequency": 1,
        "avg_duration": 2.0,
        "tags": ['"orchestration"', '"audit"', '"telemetry"'],
    },

    # Multimodal
    "video_processor_agent": {
        "path": "agents/multimodal/video_processor",
        "type": "MULTIMODAL_PROCESSOR",
        "description": "Processes video inputs for task analysis. Extracts frames, audio, and user flows from demos.",
        "capabilities": ['"video_processing"', '"frame_extraction"', '"audio_transcription"', '"flow_analysis"'],
        "languages": [],
        "frameworks": [],
        "platforms": [],
        "input_modalities": ["InputModality.VIDEO"],
        "output_types": ['"requirements"', '"frames"', '"transcript"', '"flows"'],
        "kb_strategy": "MINIMAL",
        "kb_frequency": 3,
        "avg_duration": 8.0,
        "tags": ['"multimodal"', '"video"', '"processing"'],
    },
    "audio_transcriber_agent": {
        "path": "agents/multimodal/audio_transcriber",
        "type": "MULTIMODAL_PROCESSOR",
        "description": "Transcribes audio inputs and extracts requirements. Processes stakeholder interviews and voice notes.",
        "capabilities": ['"audio_transcription"', '"requirements_extraction"', '"speaker_diarization"'],
        "languages": [],
        "frameworks": [],
        "platforms": [],
        "input_modalities": ["InputModality.AUDIO"],
        "output_types": ['"transcript"', '"requirements"', '"speakers"'],
        "kb_strategy": "MINIMAL",
        "kb_frequency": 3,
        "avg_duration": 5.0,
        "tags": ['"multimodal"', '"audio"', '"transcription"'],
    },

    # Frontend
    "ui_developer_agent": {
        "path": "agents/frontend/ui_developer",
        "type": "FRONTEND_ENGINEER",
        "description": "Generates UI components from design specifications. Creates accessible, responsive interfaces.",
        "capabilities": ['"ui_component_generation"', '"responsive_design"', '"accessibility_implementation"'],
        "languages": ['"typescript"', '"javascript"', '"html"', '"css"'],
        "frameworks": ['"react"', '"vue"', '"angular"'],
        "platforms": ['"web"'],
        "input_modalities": ["InputModality.IMAGE", "InputModality.JSON", "InputModality.DESIGN_FILE"],
        "output_types": ['"ui_components"', '"styles"', '"markup"'],
        "kb_strategy": "ADAPTIVE",
        "kb_frequency": 10,
        "avg_duration": 15.0,
        "tags": ['"frontend"', '"ui"', '"components"'],
    },
    "css_specialist_agent": {
        "path": "agents/frontend/css_specialist",
        "type": "FRONTEND_ENGINEER",
        "description": "Specialized in CSS and styling. Implements design systems, animations, and responsive layouts.",
        "capabilities": ['"css_generation"', '"responsive_design"', '"animation"', '"design_system_implementation"'],
        "languages": ['"css"', '"scss"', '"sass"'],
        "frameworks": ['"tailwind"', '"styled-components"', '"css-modules"'],
        "platforms": ['"web"'],
        "input_modalities": ["InputModality.IMAGE", "InputModality.JSON", "InputModality.DESIGN_FILE"],
        "output_types": ['"stylesheets"', '"design_tokens"', '"animations"'],
        "kb_strategy": "ADAPTIVE",
        "kb_frequency": 8,
        "avg_duration": 12.0,
        "tags": ['"frontend"', '"css"', '"styling"'],
    },
    "accessibility_specialist_agent": {
        "path": "agents/frontend/accessibility_specialist",
        "type": "FRONTEND_ENGINEER",
        "description": "Ensures WCAG compliance and accessibility best practices. Implements ARIA, keyboard navigation, and screen reader support.",
        "capabilities": ['"accessibility_audit"', '"wcag_compliance"', '"aria_implementation"', '"keyboard_navigation"'],
        "languages": ['"typescript"', '"javascript"'],
        "frameworks": ['"react"', '"vue"'],
        "platforms": ['"web"'],
        "input_modalities": ["InputModality.CODE", "InputModality.TEXT"],
        "output_types": ['"accessible_code"', '"audit_report"', '"recommendations"'],
        "kb_strategy": "ADAPTIVE",
        "kb_frequency": 12,
        "avg_duration": 15.0,
        "tags": ['"frontend"', '"accessibility"', '"wcag"'],
    },
}


def format_list(items: List[str], indent: int = 8) -> str:
    """Format list items with proper indentation."""
    if not items:
        return ""

    indent_str = " " * indent
    formatted_items = [f'\n{indent_str}{item}' for item in items]
    return ",".join(formatted_items) + "\n" + (" " * (indent - 4))


def generate_capability_file(agent_id: str, output_dir: Optional[str] = None) -> str:
    """
    Generate capability.py file for the given agent.

    Args:
        agent_id: Agent identifier (e.g., "discovery_agent")
        output_dir: Optional output directory (defaults to agent's directory)

    Returns:
        Path to generated file
    """
    if agent_id not in AGENT_SPECS:
        raise ValueError(f"Unknown agent: {agent_id}. Available agents: {', '.join(AGENT_SPECS.keys())}")

    spec = AGENT_SPECS[agent_id]
    agent_path = spec["path"]

    # Determine output path
    if output_dir:
        capability_path = os.path.join(output_dir, "capability.py")
    else:
        # Use agent's directory
        project_root = Path(__file__).parent.parent
        capability_path = project_root / agent_path / "capability.py"

    # Prepare template variables
    capability_constant_name = f"{agent_id.upper().replace('_', '_')}_CAPABILITY"
    function_name = agent_id.replace("_agent", "")

    # Format collections
    capabilities_str = format_list(spec["capabilities"])
    languages_str = format_list([f'"{lang}"' for lang in spec.get("languages", [])])
    frameworks_str = format_list([f'"{fw}"' for fw in spec.get("frameworks", [])])
    platforms_str = format_list([f'"{platform}"' for platform in spec.get("platforms", [])])
    input_modalities_str = format_list(spec["input_modalities"])
    output_types_str = format_list(spec["output_types"])
    tags_str = format_list(spec["tags"])

    # KB config
    has_kb = spec.get("kb_strategy") != "MINIMAL"
    kb_strategy = spec.get("kb_strategy", "ADAPTIVE")
    kb_frequency = spec.get("kb_frequency", 10)
    kb_triggers = '["start", "error", "checkpoint"]' if has_kb else '[]'
    max_kb_queries = 50 if has_kb else 10
    enable_kb_caching = str(has_kb)
    kb_cache_ttl = 300 if has_kb else 60

    # Performance metrics
    avg_duration = spec.get("avg_duration", 15.0)
    p95_duration = avg_duration * 2
    success_rate = 0.88
    avg_validation_failures = 0.6
    retry_rate = 0.15
    max_concurrent = 3
    avg_cost = round(avg_duration * 0.008, 2)  # ~$0.008 per minute

    # Generate content
    content = CAPABILITY_TEMPLATE.format(
        agent_path=agent_path,
        agent_display_name=agent_id.replace("_", " ").title(),
        capability_constant_name=capability_constant_name,
        agent_id=agent_id,
        agent_type=spec["type"],
        description=spec["description"],
        capabilities=capabilities_str,
        supported_languages=languages_str,
        supported_frameworks=frameworks_str,
        supported_platforms=platforms_str,
        input_modalities=input_modalities_str,
        output_types=output_types_str,
        has_kb=has_kb,
        kb_strategy=kb_strategy,
        kb_frequency=kb_frequency,
        kb_triggers=kb_triggers,
        max_kb_queries=max_kb_queries,
        enable_kb_caching=enable_kb_caching,
        kb_cache_ttl=kb_cache_ttl,
        avg_duration=avg_duration,
        p95_duration=p95_duration,
        success_rate=success_rate,
        avg_validation_failures=avg_validation_failures,
        retry_rate=retry_rate,
        avg_cost=avg_cost,
        max_concurrent=max_concurrent,
        tags=tags_str,
        function_name=function_name
    )

    # Write file
    os.makedirs(os.path.dirname(capability_path), exist_ok=True)
    with open(capability_path, 'w') as f:
        f.write(content)

    print(f"✓ Generated: {capability_path}")
    return str(capability_path)


def generate_all_capabilities():
    """Generate capability files for all agents in AGENT_SPECS."""
    print(f"\nGenerating capability files for {len(AGENT_SPECS)} agents...\n")

    generated = []
    failed = []

    for agent_id in sorted(AGENT_SPECS.keys()):
        try:
            path = generate_capability_file(agent_id)
            generated.append((agent_id, path))
        except Exception as e:
            failed.append((agent_id, str(e)))
            print(f"✗ Failed: {agent_id} - {e}")

    # Summary
    print(f"\n{'='*60}")
    print(f"Summary: {len(generated)} generated, {len(failed)} failed")
    print(f"{'='*60}")

    if failed:
        print("\nFailed agents:")
        for agent_id, error in failed:
            print(f"  - {agent_id}: {error}")

    return generated, failed


def list_agents():
    """List all available agents."""
    print("\nAvailable agents:\n")

    by_category = {}
    for agent_id, spec in AGENT_SPECS.items():
        category = spec["path"].split("/")[1]  # e.g., "stage0_discovery"
        if category not in by_category:
            by_category[category] = []
        by_category[category].append((agent_id, spec["description"]))

    for category in sorted(by_category.keys()):
        print(f"\n{category.upper().replace('_', ' ')}:")
        for agent_id, description in sorted(by_category[category]):
            print(f"  • {agent_id}")
            print(f"    {description[:80]}...")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate capability.py files for agents")
    parser.add_argument("--agent", help="Agent ID to generate (e.g., discovery_agent)")
    parser.add_argument("--all", action="store_true", help="Generate for all agents")
    parser.add_argument("--list", action="store_true", help="List available agents")
    parser.add_argument("--output-dir", help="Output directory for generated file")

    args = parser.parse_args()

    if args.list:
        list_agents()
    elif args.all:
        generate_all_capabilities()
    elif args.agent:
        generate_capability_file(args.agent, args.output_dir)
    else:
        parser.print_help()
        print("\nExamples:")
        print("  # Generate for single agent")
        print("  python scripts/generate_capability_template.py --agent discovery_agent")
        print("\n  # Generate for all agents")
        print("  python scripts/generate_capability_template.py --all")
        print("\n  # List available agents")
        print("  python scripts/generate_capability_template.py --list")
