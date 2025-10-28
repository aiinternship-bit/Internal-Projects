"""
agents/backend/api_developer/capability.py

Capability declaration for API Developer Agent.

This file defines the agent's capabilities for generating REST, GraphQL, and gRPC APIs.
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


# API Developer Agent Capability Declaration
API_DEVELOPER_CAPABILITY = AgentCapability(
    # Identity
    agent_id="api_developer_agent",  # Will be updated with Vertex AI resource ID after deployment
    agent_name="API Developer Agent",
    agent_type=AgentType.BACKEND_ENGINEER,

    # Description
    description=(
        "Generates production-ready REST, GraphQL, and gRPC APIs with comprehensive documentation. "
        "Supports multiple languages and frameworks with built-in authentication, validation, and testing."
    ),

    # Capabilities
    capabilities={
        "rest_api_development",
        "graphql_api_development",
        "grpc_service_development",
        "api_documentation",
        "openapi_specification",
        "authentication_implementation",
        "request_validation",
        "error_handling",
        "api_testing"
    },

    # Supported languages
    supported_languages=[
        "typescript",
        "python",
        "go",
        "java"
    ],

    # Supported frameworks
    supported_frameworks=[
        "express",           # Node.js/TypeScript REST
        "fastapi",           # Python REST
        "gin",               # Go REST
        "spring-boot",       # Java REST
        "apollo-server",     # TypeScript GraphQL
        "strawberry",        # Python GraphQL
        "gqlgen",            # Go GraphQL
        "grpc-node",         # TypeScript gRPC
        "grpcio",            # Python gRPC
        "grpc-go"            # Go gRPC
    ],

    # Supported platforms
    supported_platforms=[
        "web",
        "cloud",
        "microservices"
    ],

    # Input modalities
    input_modalities={
        InputModality.TEXT,  # API specifications
        InputModality.JSON,  # Endpoint definitions
        InputModality.YAML,  # OpenAPI specs
        InputModality.CODE   # Existing code for enhancement
    },

    # Output types
    output_types={
        "api_code",
        "tests",
        "documentation",
        "openapi_spec",
        "graphql_schema",
        "proto_definition"
    },

    # Knowledge Base Integration
    kb_integration=KBIntegrationConfig(
        has_vector_db_access=True,
        kb_query_strategy=KBQueryStrategy.ADAPTIVE,
        kb_query_frequency=10,  # Query every 10 operations
        kb_query_triggers=[
            "start",            # Query at task start for API patterns
            "error",            # Query on generation errors
            "validation_fail",  # Query when validation fails
            "checkpoint"        # Query at periodic checkpoints
        ],
        max_kb_queries_per_task=50,
        enable_kb_caching=True,
        kb_cache_ttl_seconds=300
    ),

    # Performance Metrics (initial baselines)
    performance_metrics=PerformanceMetrics(
        total_tasks_completed=0,
        total_tasks_failed=0,
        avg_task_duration_minutes=15.0,  # Baseline: 15 minutes per API
        p95_task_duration_minutes=30.0,   # 95th percentile
        success_rate=0.88,  # 88% success rate baseline
        avg_validation_failures=0.8,  # Average retries before validation passes
        retry_rate=0.20  # 20% of tasks require retry
    ),

    # Cost Metrics (initial estimates)
    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.12,  # ~$0.12 per API generation
        kb_query_cost_usd=0.002,     # ~$0.002 per KB query
        total_cost_usd=0.0
    ),

    # Resource limits
    max_concurrent_tasks=3,
    estimated_task_duration_minutes=15.0,

    # Additional metadata
    version="1.0.0",
    deployment_region="us-central1",
    tags=["backend", "api", "rest", "graphql", "grpc", "microservices"]
)


def get_api_developer_capability() -> AgentCapability:
    """
    Get the API Developer Agent capability declaration.

    Returns:
        AgentCapability object
    """
    return API_DEVELOPER_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    """
    Update the agent_id with the actual Vertex AI resource ID after deployment.

    Args:
        vertex_ai_resource_id: Full Vertex AI resource name
    """
    API_DEVELOPER_CAPABILITY.agent_id = vertex_ai_resource_id
