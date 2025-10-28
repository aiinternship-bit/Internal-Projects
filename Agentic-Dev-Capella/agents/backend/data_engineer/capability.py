"""
agents/backend/data_engineer/capability.py

Capability declaration for Data Engineer Agent.
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


DATA_ENGINEER_CAPABILITY = AgentCapability(
    agent_id="data_engineer_agent",
    agent_name="Data Engineer Agent",
    agent_type=AgentType.DATA_ENGINEER,

    description=(
        "Creates ETL/ELT pipelines, designs data warehouses, and generates batch processing jobs. "
        "Supports Airflow, dbt, BigQuery, Apache Spark, Redshift, and Snowflake."
    ),

    capabilities={
        "etl_pipeline_development",
        "data_warehouse_design",
        "batch_processing",
        "dbt_modeling",
        "spark_jobs",
        "data_quality_checks",
        "incremental_loading",
        "schema_evolution",
        "data_validation"
    },

    supported_languages=[
        "python",
        "sql",
        "scala"
    ],

    supported_frameworks=[
        "airflow",
        "dbt",
        "apache_spark",
        "bigquery",
        "redshift",
        "snowflake"
    ],

    supported_platforms=[
        "cloud",
        "data_warehouse",
        "data_lake"
    ],

    input_modalities={
        InputModality.TEXT,
        InputModality.JSON,
        InputModality.CODE,
        InputModality.DATA_FILE
    },

    output_types={
        "dag_code",
        "dbt_models",
        "spark_jobs",
        "warehouse_schema",
        "quality_checks",
        "documentation"
    },

    kb_integration=KBIntegrationConfig(
        has_vector_db_access=True,
        kb_query_strategy=KBQueryStrategy.ADAPTIVE,
        kb_query_frequency=10,
        kb_query_triggers=["start", "error", "validation_fail", "checkpoint"],
        max_kb_queries_per_task=50,
        enable_kb_caching=True,
        kb_cache_ttl_seconds=300
    ),

    performance_metrics=PerformanceMetrics(
        total_tasks_completed=0,
        total_tasks_failed=0,
        avg_task_duration_minutes=18.0,
        p95_task_duration_minutes=35.0,
        success_rate=0.87,
        avg_validation_failures=0.9,
        retry_rate=0.22
    ),

    cost_metrics=CostMetrics(
        avg_cost_per_task_usd=0.14,
        kb_query_cost_usd=0.002,
        total_cost_usd=0.0
    ),

    max_concurrent_tasks=3,
    estimated_task_duration_minutes=18.0,

    version="1.0.0",
    deployment_region="us-central1",
    tags=["backend", "data-engineering", "etl", "data-warehouse", "big-data"]
)


def get_data_engineer_capability() -> AgentCapability:
    return DATA_ENGINEER_CAPABILITY


def update_agent_id(vertex_ai_resource_id: str) -> None:
    DATA_ENGINEER_CAPABILITY.agent_id = vertex_ai_resource_id
