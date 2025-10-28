"""
agents/multimodal/pdf_parser/capability.py

Capability declaration for PDF Parser Agent.
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


PDF_PARSER_AGENT_CAPABILITY = AgentCapability(
    # Identity
    agent_id="pdf_parser_agent",
    agent_name="PDF Parser Agent",
    agent_type=AgentType.MULTIMODAL_PROCESSOR,

    # Description
    description=(
        "Extracts requirements, specifications, and documentation from PDF documents. "
        "Identifies functional/non-functional requirements, API specs, technical constraints, "
        "dependencies, and success criteria. Uses Gemini 2.0 Flash Exp for PDF processing."
    ),

    # Capabilities
    capabilities={
        "pdf_parsing",
        "requirement_extraction",
        "specification_extraction",
        "documentation_parsing",
        "api_extraction",
        "nfr_identification",
        "constraint_extraction",
        "dependency_identification",
        "text_extraction",
        "structure_analysis"
    },

    # Supported languages
    supported_languages=[],  # Language-agnostic

    # Supported frameworks
    supported_frameworks=[],  # Framework-agnostic

    # Input modalities
    input_modalities={
        InputModality.PDF,
        InputModality.TEXT
    },

    # Output types
    output_types={
        "requirements",
        "specifications",
        "api_docs",
        "nfrs",
        "constraints"
    },

    # Knowledge Base Integration
    kb_integration=KBIntegrationConfig(
        has_vector_db_access=True,
        kb_query_strategy=KBQueryStrategy.ONCE,  # Query once for similar docs
        kb_query_frequency=100,
        kb_query_triggers=["start"],
        max_kb_queries_per_task=3,
        enable_kb_caching=True,
        kb_cache_ttl_seconds=300
    ),

    # Performance Metrics
    performance_metrics=PerformanceMetrics(
        total_tasks_completed=0,
        total_tasks_failed=0,
        avg_task_duration_minutes=3.0,  # ~3 minutes per PDF
        p95_task_duration_minutes=8.0,
        success_rate=0.92,
        avg_validation_failures=0.2,
        retry_rate=0.08
    ),

    # Cost Metrics
    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.08,  # ~$0.08 per PDF
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    # Resource limits
    max_concurrent_tasks=3,
    estimated_task_duration_minutes=3.0,

    # Additional metadata
    version="1.0.0",
    deployment_region="us-central1",
    tags=["multimodal", "pdf", "document-parsing", "requirement-extraction"]
)


def get_pdf_parser_capability() -> AgentCapability:
    """Get the PDF Parser Agent capability declaration."""
    return PDF_PARSER_AGENT_CAPABILITY
