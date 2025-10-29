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
        "Comprehensive video processing agent for extracting requirements from video demonstrations. "
        "Analyzes UI flows, extracts key frames, generates transcriptions, and maps user journeys."
    ),

    capabilities={
        "video_processing",
        "frame_extraction",
        "key_moment_identification",
        "ui_flow_analysis",
        "user_journey_mapping",
        "video_transcription",
        "audio_extraction",
        "screen_recording_analysis",
        "product_demo_analysis",
        "feature_demonstration_analysis"
    },

    supported_languages=[],

    supported_frameworks=[],

    supported_platforms=["web", "mobile", "desktop"],

    input_modalities={
        InputModality.VIDEO
    },

    output_types={
        "requirements",
        "frames",
        "transcript",
        "ui_flows",
        "user_journey",
        "key_moments",
        "technical_specs"
    },

    kb_integration=KBIntegrationConfig(
        has_vector_db_access=True,
        kb_query_strategy=KBQueryStrategy.ADAPTIVE,
        kb_query_frequency=8,
        kb_query_triggers=["start", "error", "pattern_needed"],
        max_kb_queries_per_task=25,
        enable_kb_caching=True,
        kb_cache_ttl_seconds=300
    ),

    performance_metrics=PerformanceMetrics(
        total_tasks_completed=0,
        total_tasks_failed=0,
        avg_task_duration_minutes=12.0,
        p95_task_duration_minutes=25.0,
        success_rate=0.90,
        avg_validation_failures=0.4,
        retry_rate=0.12
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.10,
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=4,
    estimated_task_duration_minutes=12.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=["multimodal", "video", "processing", "ui_analysis", "transcription"]
)


def get_video_processor_capability() -> AgentCapability:
    return VIDEO_PROCESSOR_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    VIDEO_PROCESSOR_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
