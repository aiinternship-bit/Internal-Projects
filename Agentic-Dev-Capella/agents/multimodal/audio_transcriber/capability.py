"""
agents/multimodal/audio_transcriber/capability.py

Capability declaration for Audio Transcriber Agent.
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


AUDIO_TRANSCRIBER_AGENT_CAPABILITY = AgentCapability(
    agent_id="audio_transcriber_agent",
    agent_name="Audio Transcriber Agent",
    agent_type=AgentType.MULTIMODAL_PROCESSOR,

    description=(
        "Enterprise-grade audio transcription and analysis agent for meetings, interviews, and discussions. "
        "Provides speaker diarization, sentiment analysis, technical specs extraction, and action item tracking."
    ),

    capabilities={
        "audio_transcription",
        "meeting_analysis",
        "speaker_diarization",
        "speaker_identification",
        "sentiment_analysis",
        "tone_analysis",
        "technical_specs_extraction",
        "action_item_extraction",
        "decision_tracking",
        "requirements_extraction",
        "turn_taking_analysis",
        "emotional_pattern_analysis"
    },

    supported_languages=[],

    supported_frameworks=[],

    supported_platforms=["meetings", "interviews", "discussions", "voice_notes"],

    input_modalities={
        InputModality.AUDIO
    },

    output_types={
        "transcript",
        "meeting_summary",
        "action_items",
        "decisions",
        "requirements",
        "technical_specs",
        "speaker_analysis",
        "sentiment_analysis"
    },

    kb_integration=KBIntegrationConfig(
        has_vector_db_access=True,
        kb_query_strategy=KBQueryStrategy.ADAPTIVE,
        kb_query_frequency=10,
        kb_query_triggers=["start", "error", "pattern_needed"],
        max_kb_queries_per_task=30,
        enable_kb_caching=True,
        kb_cache_ttl_seconds=300
    ),

    performance_metrics=PerformanceMetrics(
        total_tasks_completed=0,
        total_tasks_failed=0,
        avg_task_duration_minutes=14.0,
        p95_task_duration_minutes=28.0,
        success_rate=0.91,
        avg_validation_failures=0.3,
        retry_rate=0.10
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.12,
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=4,
    estimated_task_duration_minutes=14.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=["multimodal", "audio", "transcription", "meeting_analysis", "sentiment", "speaker_diarization"]
)


def get_audio_transcriber_capability() -> AgentCapability:
    return AUDIO_TRANSCRIBER_AGENT_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    AUDIO_TRANSCRIBER_AGENT_CAPABILITY.agent_id = vertex_ai_resource_id
