"""
agents/multimodal/vision/capability.py

Capability declaration for Vision Agent.
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


VISION_AGENT_CAPABILITY = AgentCapability(
    # Identity
    agent_id="vision_agent",
    agent_name="Vision Agent",
    agent_type=AgentType.MULTIMODAL_PROCESSOR,

    # Description
    description=(
        "Analyzes images, screenshots, UI mockups, architecture diagrams, and design systems. "
        "Extracts UI components, design patterns, color schemes, typography, and technical requirements. "
        "Uses Gemini 2.0 Flash Exp for multimodal vision analysis."
    ),

    # Capabilities
    capabilities={
        "image_analysis",
        "ui_mockup_extraction",
        "screenshot_analysis",
        "diagram_interpretation",
        "wireframe_analysis",
        "design_system_extraction",
        "color_extraction",
        "typography_detection",
        "layout_analysis",
        "component_identification",
        "design_comparison"
    },

    # Supported languages (for code generation from mockups)
    supported_languages=[
        "html",
        "css",
        "javascript",
        "typescript"
    ],

    # Supported frameworks
    supported_frameworks=[
        "react",
        "vue",
        "angular",
        "tailwind",
        "material-ui",
        "bootstrap"
    ],

    # Input modalities
    input_modalities={
        InputModality.IMAGE,
        InputModality.DIAGRAM,
        InputModality.DESIGN_FILE
    },

    # Output types
    output_types={
        "ui_components",
        "design_spec",
        "color_palette",
        "component_hierarchy",
        "technical_requirements"
    },

    # Knowledge Base Integration
    kb_integration=KBIntegrationConfig(
        has_vector_db_access=True,
        kb_query_strategy=KBQueryStrategy.MINIMAL,  # Minimal KB usage for vision
        kb_query_frequency=50,  # Rarely query KB
        kb_query_triggers=["start"],  # Only at start for similar designs
        max_kb_queries_per_task=5,
        enable_kb_caching=True,
        kb_cache_ttl_seconds=300
    ),

    # Performance Metrics
    performance_metrics=PerformanceMetrics(
        total_tasks_completed=0,
        total_tasks_failed=0,
        avg_task_duration_minutes=2.0,  # ~2 minutes per image
        p95_task_duration_minutes=5.0,
        success_rate=0.95,  # 95% success rate
        avg_validation_failures=0.1,
        retry_rate=0.05
    ),

    # Cost Metrics
    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.05,  # ~$0.05 per image analysis
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    # Resource limits
    max_concurrent_tasks=5,
    estimated_task_duration_minutes=2.0,

    # Additional metadata
    version="1.0.0",
    deployment_region="us-central1",
    tags=["multimodal", "vision", "image-analysis", "ui-extraction"]
)


def get_vision_capability() -> AgentCapability:
    """Get the Vision Agent capability declaration."""
    return VISION_AGENT_CAPABILITY
