"""
agents/backend/data_engineer/agent.py

Data Engineer Agent - Creates ETL pipelines, designs data warehouses, batch processing.

Supports Airflow, dbt, BigQuery, Apache Spark, Redshift, Snowflake for comprehensive
data engineering solutions.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re

from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration
from shared.utils.kb_integration_mixin import DynamicKnowledgeBaseIntegration


class DataEngineerAgent(A2AEnabledAgent, DynamicKnowledgeBaseIntegration):
    """
    Data Engineer Agent for data pipeline and warehouse design.

    Capabilities:
    - ETL/ELT pipeline development (Airflow)
    - Data warehouse design (BigQuery, Redshift, Snowflake)
    - dbt model generation
    - Apache Spark job development
    - Data quality and validation
    - Batch processing orchestration
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        vector_db_client=None,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize Data Engineer Agent."""
        A2AEnabledAgent.__init__(self, context, message_bus)

        self.context = context
        self.orchestrator_id = orchestrator_id
        self.model_name = model_name

        # Initialize A2A integration
        self.a2a = A2AIntegration(
            context=context,
            message_bus=message_bus,
            orchestrator_id=orchestrator_id
        )

        # Initialize KB integration
        if vector_db_client:
            self.initialize_kb_integration(
                vector_db_client=vector_db_client,
                kb_query_strategy="adaptive"
            )

        # Initialize Vertex AI
        aiplatform.init(
            project=context.get("project_id"),
            location=context.get("location", "us-central1")
        )

        self.model = GenerativeModel(model_name)
        self.pipeline_history: List[Dict[str, Any]] = []

    def handle_task_assignment(self, message: Dict[str, Any]) -> None:
        """Handle TASK_ASSIGNMENT message from orchestrator."""
        payload = message.get("payload", {})
        task_id = payload.get("task_id")
        task_type = payload.get("task_type")
        parameters = payload.get("parameters", {})

        try:
            if task_type == "generate_etl_pipeline":
                result = self.generate_etl_pipeline(task_id=task_id, **parameters)
            elif task_type == "generate_dbt_models":
                result = self.generate_dbt_models(task_id=task_id, **parameters)
            elif task_type == "design_data_warehouse":
                result = self.design_data_warehouse(task_id=task_id, **parameters)
            elif task_type == "generate_spark_job":
                result = self.generate_spark_job(task_id=task_id, **parameters)
            elif task_type == "generate_data_quality_checks":
                result = self.generate_data_quality_checks(task_id=task_id, **parameters)
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            self.a2a.send_completion(
                task_id=task_id,
                artifacts=result,
                metrics={"kb_queries_used": getattr(self, "_kb_query_count", 0)}
            )

        except Exception as e:
            self.a2a.send_error_report(
                task_id=task_id,
                error_type="DATA_PIPELINE_FAILED",
                error_message=str(e),
                stack_trace=""
            )

    @A2AIntegration.with_task_tracking
    def generate_etl_pipeline(
        self,
        source: Dict[str, Any],
        destination: Dict[str, Any],
        transformations: List[Dict[str, Any]],
        schedule: str = "0 0 * * *",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate ETL pipeline using Apache Airflow.

        Args:
            source: Source configuration (type, connection, format)
            destination: Destination configuration
            transformations: List of transformation steps
            schedule: Cron schedule for pipeline
            task_id: Optional task ID

        Returns:
            {
                "dag_code": str,
                "operators": List[str],
                "dependencies": List[str],
                "configuration": Dict,
                "documentation": str
            }
        """
        start_time = datetime.utcnow()
        print(f"[Data Engineer] Generating ETL pipeline from {source.get('type')} to {destination.get('type')}")

        # Query KB for ETL patterns
        kb_context = ""
        if hasattr(self, 'should_query_kb') and self.should_query_kb(source):
            kb_results = self.execute_dynamic_query(
                query_type="etl_patterns",
                context={"source": source.get("type"), "destination": destination.get("type")},
                task_id=task_id
            )
            if kb_results:
                kb_context = self._format_kb_results(kb_results)

        # Build prompt
        prompt = self._build_etl_pipeline_prompt(
            source=source,
            destination=destination,
            transformations=transformations,
            schedule=schedule,
            kb_context=kb_context
        )

        # Generate with LLM
        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        # Parse result
        result = self._parse_etl_pipeline(response.text)

        # Add metadata
        duration = (datetime.utcnow() - start_time).total_seconds() / 60
        result.update({
            "source_type": source.get("type"),
            "destination_type": destination.get("type"),
            "schedule": schedule,
            "transformation_count": len(transformations),
            "duration_minutes": duration,
            "timestamp": datetime.utcnow().isoformat()
        })

        self.pipeline_history.append({
            "task_id": task_id,
            "pipeline_type": "etl",
            "source": source.get("type"),
            "timestamp": result["timestamp"]
        })

        return result

    @A2AIntegration.with_task_tracking
    def generate_dbt_models(
        self,
        source_tables: List[Dict[str, Any]],
        transformations: List[Dict[str, Any]],
        tests: Optional[List[str]] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate dbt (data build tool) models.

        Args:
            source_tables: Source table specifications
            transformations: Transformation logic
            tests: Data quality tests to include
            task_id: Optional task ID

        Returns:
            {
                "models": List[Dict],
                "tests": List[str],
                "documentation": str,
                "project_config": str
            }
        """
        print(f"[Data Engineer] Generating dbt models for {len(source_tables)} source tables")

        kb_context = ""
        if hasattr(self, 'should_query_kb') and self.should_query_kb({"tables": len(source_tables)}):
            kb_results = self.execute_dynamic_query(
                query_type="dbt_patterns",
                context={"table_count": len(source_tables)},
                task_id=task_id
            )
            if kb_results:
                kb_context = self._format_kb_results(kb_results)

        prompt = self._build_dbt_models_prompt(
            source_tables=source_tables,
            transformations=transformations,
            tests=tests or [],
            kb_context=kb_context
        )

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = self._parse_dbt_models(response.text)
        result.update({
            "source_table_count": len(source_tables),
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    @A2AIntegration.with_task_tracking
    def design_data_warehouse(
        self,
        business_requirements: Dict[str, Any],
        schema_type: str = "star",
        warehouse_platform: str = "bigquery",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Design data warehouse schema.

        Args:
            business_requirements: Business metrics and dimensions
            schema_type: Schema type (star, snowflake, data_vault)
            warehouse_platform: Platform (bigquery, redshift, snowflake)
            task_id: Optional task ID

        Returns:
            {
                "fact_tables": List[Dict],
                "dimension_tables": List[Dict],
                "ddl": str,
                "er_diagram": str,
                "documentation": str
            }
        """
        print(f"[Data Engineer] Designing {schema_type} schema for {warehouse_platform}")

        prompt = self._build_data_warehouse_prompt(
            business_requirements=business_requirements,
            schema_type=schema_type,
            warehouse_platform=warehouse_platform
        )

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = self._parse_warehouse_design(response.text)
        result.update({
            "schema_type": schema_type,
            "platform": warehouse_platform,
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    @A2AIntegration.with_task_tracking
    def generate_spark_job(
        self,
        data_source: Dict[str, Any],
        transformations: List[Dict[str, Any]],
        output_format: str = "parquet",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate Apache Spark job for batch processing.

        Args:
            data_source: Data source configuration
            transformations: Transformation operations
            output_format: Output format (parquet, avro, delta)
            task_id: Optional task ID

        Returns:
            {
                "spark_code": str,
                "configuration": Dict,
                "deployment_script": str,
                "documentation": str
            }
        """
        print(f"[Data Engineer] Generating Spark job for {data_source.get('type')} source")

        prompt = self._build_spark_job_prompt(
            data_source=data_source,
            transformations=transformations,
            output_format=output_format
        )

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = self._parse_spark_job(response.text)
        result.update({
            "source_type": data_source.get("type"),
            "output_format": output_format,
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    @A2AIntegration.with_task_tracking
    def generate_data_quality_checks(
        self,
        data_schema: Dict[str, Any],
        quality_rules: List[Dict[str, Any]],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate data quality checks and validation.

        Args:
            data_schema: Data schema specification
            quality_rules: Quality rules (completeness, accuracy, etc.)
            task_id: Optional task ID

        Returns:
            {
                "quality_checks": List[Dict],
                "test_code": str,
                "monitoring_config": Dict
            }
        """
        print(f"[Data Engineer] Generating data quality checks")

        prompt = self._build_quality_checks_prompt(
            data_schema=data_schema,
            quality_rules=quality_rules
        )

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = self._parse_quality_checks(response.text)
        result.update({
            "rule_count": len(quality_rules),
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    def _build_etl_pipeline_prompt(
        self,
        source: Dict[str, Any],
        destination: Dict[str, Any],
        transformations: List[Dict[str, Any]],
        schedule: str,
        kb_context: str
    ) -> str:
        """Build ETL pipeline generation prompt."""

        return f"""
Generate a production-ready Apache Airflow DAG for ETL pipeline.

**Source:**
{json.dumps(source, indent=2)}

**Destination:**
{json.dumps(destination, indent=2)}

**Transformations:**
{json.dumps(transformations, indent=2)}

**Schedule:** {schedule} (cron format)

Requirements:
1. Use Airflow 2.x with TaskFlow API
2. Implement proper error handling and retries
3. Add data validation before and after transformations
4. Include idempotency checks
5. Add monitoring and alerting
6. Use XComs for passing data between tasks
7. Implement incremental loading if applicable
8. Add data quality checks
9. Include proper logging
10. Handle schema evolution

Provide:
1. Complete DAG Python code
2. Custom operators if needed
3. Connection configurations
4. Variable definitions
5. Data validation functions
6. Error handling and alerting
7. Documentation and usage guide

{kb_context}

Best practices:
- Use sensors for dependency management
- Implement backfill strategy
- Add SLA monitoring
- Use connection pools
- Optimize for parallelism
"""

    def _build_dbt_models_prompt(
        self,
        source_tables: List[Dict[str, Any]],
        transformations: List[Dict[str, Any]],
        tests: List[str],
        kb_context: str
    ) -> str:
        """Build dbt models generation prompt."""

        return f"""
Generate dbt models for data transformation.

**Source Tables:**
{json.dumps(source_tables, indent=2)}

**Transformations:**
{json.dumps(transformations, indent=2)}

**Tests Required:**
{json.dumps(tests, indent=2)}

Requirements:
1. Create staging models (stg_*.sql)
2. Create intermediate models (int_*.sql)
3. Create final mart models (mart_*.sql)
4. Use Jinja templating and macros
5. Implement data tests (unique, not_null, relationships)
6. Add schema tests
7. Include documentation (schema.yml)
8. Use sources and refs properly
9. Implement incremental models where appropriate
10. Add data freshness checks

Provide:
1. All model SQL files
2. schema.yml with tests and documentation
3. dbt_project.yml configuration
4. Custom macros if needed
5. Model dependencies (DAG)
6. Documentation

{kb_context}

Follow dbt best practices:
- Use CTEs for readability
- Avoid nested subqueries
- Use incremental models for large tables
- Add proper materialization strategy
"""

    def _build_data_warehouse_prompt(
        self,
        business_requirements: Dict[str, Any],
        schema_type: str,
        warehouse_platform: str
    ) -> str:
        """Build data warehouse design prompt."""

        return f"""
Design a {schema_type} schema data warehouse for {warehouse_platform.upper()}.

**Business Requirements:**
{json.dumps(business_requirements, indent=2)}

**Schema Type:** {schema_type}
**Platform:** {warehouse_platform}

Requirements:
1. Design fact table(s) with measures
2. Design dimension tables with hierarchies
3. Implement slowly changing dimensions (SCD Type 2 where needed)
4. Add surrogate keys for dimensions
5. Include date/time dimensions
6. Optimize for query performance
7. Add partitioning and clustering
8. Include aggregation tables if needed
9. Design for incremental loads
10. Add data lineage documentation

Provide:
1. Fact table definitions (DDL)
2. Dimension table definitions (DDL)
3. ER diagram (Mermaid format)
4. Indexing and partitioning strategy
5. ETL/ELT design for loading
6. Sample queries
7. Performance optimization guide
8. Documentation

Platform-specific optimizations for {warehouse_platform}:
- Use native features (partitioning, clustering, etc.)
- Optimize for cost and performance
- Consider data retention policies
"""

    def _build_spark_job_prompt(
        self,
        data_source: Dict[str, Any],
        transformations: List[Dict[str, Any]],
        output_format: str
    ) -> str:
        """Build Spark job generation prompt."""

        return f"""
Generate an Apache Spark job (PySpark) for batch data processing.

**Data Source:**
{json.dumps(data_source, indent=2)}

**Transformations:**
{json.dumps(transformations, indent=2)}

**Output Format:** {output_format}

Requirements:
1. Use PySpark DataFrame API
2. Implement all transformations efficiently
3. Add data validation and quality checks
4. Handle schema evolution
5. Optimize for performance (partitioning, caching)
6. Add error handling and logging
7. Implement checkpointing for fault tolerance
8. Use broadcast joins where appropriate
9. Add metrics and monitoring
10. Support incremental processing

Provide:
1. Complete PySpark code
2. Spark configuration (spark-submit parameters)
3. Deployment script
4. Unit tests
5. Performance tuning guide
6. Monitoring setup
7. Documentation

Optimizations:
- Use appropriate partitioning
- Cache intermediate results
- Avoid shuffles where possible
- Use column pruning and filter pushdown
"""

    def _build_quality_checks_prompt(
        self,
        data_schema: Dict[str, Any],
        quality_rules: List[Dict[str, Any]]
    ) -> str:
        """Build data quality checks prompt."""

        return f"""
Generate data quality checks and validation.

**Data Schema:**
{json.dumps(data_schema, indent=2)}

**Quality Rules:**
{json.dumps(quality_rules, indent=2)}

Requirements:
1. Implement completeness checks (null values, required fields)
2. Implement accuracy checks (data type, format, range)
3. Implement consistency checks (referential integrity, business rules)
4. Implement uniqueness checks (primary keys, duplicates)
5. Implement timeliness checks (data freshness, SLA)
6. Add anomaly detection
7. Include data profiling
8. Generate quality reports
9. Add alerting for failures
10. Track quality metrics over time

Provide:
1. Quality check implementations (Great Expectations or SQL)
2. Test configurations
3. Monitoring dashboard setup
4. Alerting rules
5. Quality metrics definitions
6. Documentation
"""

    def _parse_etl_pipeline(self, text: str) -> Dict[str, Any]:
        """Parse ETL pipeline result."""

        result = {
            "dag_code": "",
            "operators": [],
            "dependencies": [],
            "configuration": {},
            "documentation": text
        }

        # Extract Python code
        python_blocks = re.findall(r'```python\n(.*?)```', text, re.DOTALL)
        if python_blocks:
            result["dag_code"] = "\n\n".join(python_blocks)

        # Extract configuration
        json_blocks = re.findall(r'```json\n(.*?)```', text, re.DOTALL)
        for json_str in json_blocks:
            try:
                result["configuration"] = json.loads(json_str)
            except:
                pass

        return result

    def _parse_dbt_models(self, text: str) -> Dict[str, Any]:
        """Parse dbt models result."""

        result = {
            "models": [],
            "tests": [],
            "documentation": text,
            "project_config": ""
        }

        # Extract SQL models
        sql_blocks = re.findall(r'```sql\n(.*?)```', text, re.DOTALL)
        result["models"] = [{"sql": block.strip()} for block in sql_blocks]

        # Extract YAML configuration
        yaml_blocks = re.findall(r'```yaml\n(.*?)```', text, re.DOTALL)
        if yaml_blocks:
            result["project_config"] = yaml_blocks[0].strip()

        return result

    def _parse_warehouse_design(self, text: str) -> Dict[str, Any]:
        """Parse warehouse design result."""

        result = {
            "fact_tables": [],
            "dimension_tables": [],
            "ddl": "",
            "er_diagram": "",
            "documentation": text
        }

        # Extract DDL
        sql_blocks = re.findall(r'```sql\n(.*?)```', text, re.DOTALL)
        result["ddl"] = "\n\n".join(sql_blocks)

        # Extract diagram
        mermaid_match = re.search(r'```mermaid\n(.*?)```', text, re.DOTALL)
        if mermaid_match:
            result["er_diagram"] = mermaid_match.group(1).strip()

        return result

    def _parse_spark_job(self, text: str) -> Dict[str, Any]:
        """Parse Spark job result."""

        result = {
            "spark_code": "",
            "configuration": {},
            "deployment_script": "",
            "documentation": text
        }

        # Extract Python code
        python_blocks = re.findall(r'```python\n(.*?)```', text, re.DOTALL)
        if python_blocks:
            result["spark_code"] = python_blocks[0].strip()

        # Extract bash deployment script
        bash_blocks = re.findall(r'```bash\n(.*?)```', text, re.DOTALL)
        if bash_blocks:
            result["deployment_script"] = bash_blocks[0].strip()

        return result

    def _parse_quality_checks(self, text: str) -> Dict[str, Any]:
        """Parse quality checks result."""

        result = {
            "quality_checks": [],
            "test_code": "",
            "monitoring_config": {},
            "documentation": text
        }

        # Extract code blocks
        code_blocks = re.findall(r'```(?:python|sql)\n(.*?)```', text, re.DOTALL)
        if code_blocks:
            result["test_code"] = "\n\n".join(code_blocks)

        return result

    def _get_generation_config(self) -> Dict[str, Any]:
        """Get generation config for LLM."""
        return {
            "temperature": 0.2,
            "max_output_tokens": 8192,
            "top_p": 0.95,
            "top_k": 40
        }

    def _format_kb_results(self, results: List[Dict]) -> str:
        """Format KB query results."""
        if not results:
            return ""
        formatted = "\n\nRelevant data engineering patterns from knowledge base:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result.get('content', '')}\n\n"
        return formatted


# Standalone tool functions

def generate_etl_pipeline(
    source: Dict[str, Any],
    destination: Dict[str, Any],
    transformations: List[Dict[str, Any]],
    schedule: str = "0 0 * * *"
) -> Dict[str, Any]:
    """Standalone function for ETL pipeline generation."""
    agent = DataEngineerAgent(context={}, message_bus=None, orchestrator_id="")
    return agent.generate_etl_pipeline(source, destination, transformations, schedule)


def generate_dbt_models(
    source_tables: List[Dict[str, Any]],
    transformations: List[Dict[str, Any]],
    tests: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Standalone function for dbt model generation."""
    agent = DataEngineerAgent(context={}, message_bus=None, orchestrator_id="")
    return agent.generate_dbt_models(source_tables, transformations, tests)


def design_data_warehouse(
    business_requirements: Dict[str, Any],
    schema_type: str = "star",
    warehouse_platform: str = "bigquery"
) -> Dict[str, Any]:
    """Standalone function for data warehouse design."""
    agent = DataEngineerAgent(context={}, message_bus=None, orchestrator_id="")
    return agent.design_data_warehouse(business_requirements, schema_type, warehouse_platform)
