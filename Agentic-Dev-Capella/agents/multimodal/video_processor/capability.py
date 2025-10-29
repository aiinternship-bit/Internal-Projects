"""
agents/multimodal/video_processor/capability.py

Capability declaration for Video Processor Agent.
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


VIDEO_PROCESSOR_AGENT_CAPABILITY = AgentCapability(
    agent_id="video_processor_agent",
    agent_name="Video Processor Agent",
    agent_type=AgentType.MULTIMODAL_PROCESSOR,

    description=(
        "Processes video inputs for task analysis. Extracts frames, audio, and user flows from demos."
    ),

    capabilities={
        "video_processing",
        "frame_extraction",
        "audio_transcription",
        "flow_analysis"
    },

    supported_languages=[],

    supported_frameworks=[],

    supported_platforms=[],

    input_modalities={
        InputModality.VIDEO
    },

    output_types={
        "requirements",
        "frames",
        "transcript",
        "flows"
    },

    kb_integration=KBIntegrationConfig(
        has_vector_db_access=False,
        kb_query_strategy=KBQueryStrategy.MINIMAL,
        kb_query_frequency=3,
        kb_query_triggers=[],
        max_kb_queries_per_task=10,
        enable_kb_caching=False,
        kb_cache_ttl_seconds=60
    ),

    performance_metrics=PerformanceMetrics(
        total_tasks_completed=0,
        total_tasks_failed=0,
        avg_task_duration_minutes=8.0,
        p95_task_duration_minutes=16.0,
        success_rate=0.88,
        avg_validation_failures=0.6,
        retry_rate=0.15
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.06,
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=3,
    estimated_task_duration_minutes=8.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=
        "multimodal",
        "video",
        "processing"
    
)


def get_video_processor_capability() -> AgentCapability:
    return VIDEO_PROCESSOR_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    VIDEO_PROCESSOR_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
