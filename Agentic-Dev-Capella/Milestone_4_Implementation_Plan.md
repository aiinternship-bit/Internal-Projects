# Milestone 4 Implementation Plan: Backend & Infrastructure Agents

## Executive Summary

**Objective**: Implement 8 production-ready AI agents (5 Backend Engineering + 3 Infrastructure) for the Agentic Dev Team Capella system.

**Timeline**: 1.5-2 weeks (12 working days)

**Approach**: Full parallel implementation with implementation-first, testing-second strategy

**Deliverables**: ~5,300-6,400 lines of production-ready code with full KB integration and comprehensive testing

---

## Table of Contents
1. [Overview](#overview)
2. [Agent Specifications](#agent-specifications)
3. [Implementation Strategy](#implementation-strategy)
4. [Detailed Phase Breakdown](#detailed-phase-breakdown)
5. [Technical Architecture](#technical-architecture)
6. [Testing Strategy](#testing-strategy)
7. [Success Criteria](#success-criteria)
8. [Risk Mitigation](#risk-mitigation)

---

## Overview

### Scope
Milestone 4 adds **8 specialized agents** to enable full backend and infrastructure development capabilities:

**Backend Engineering Team (5 agents)**:
1. API Developer Agent
2. Database Engineer Agent
3. Microservices Architect Agent
4. Data Engineer Agent
5. Message Queue Agent

**Infrastructure Team (3 agents)**:
6. Cloud Infrastructure Agent
7. Kubernetes Agent
8. Observability Agent

### Prerequisites (All Complete ✅)
- ✅ Agent capability system (`shared/models/agent_capability.py`)
- ✅ Agent registry service (`shared/services/agent_registry.py`)
- ✅ A2A communication protocol (`shared/utils/vertex_a2a_protocol.py`)
- ✅ KB integration framework (`shared/utils/kb_integration_mixin.py`)
- ✅ Testing infrastructure (mock + LLM tests)
- ✅ Base agent classes (`shared/utils/agent_base.py`)

### Implementation Approach
**Selected Strategy**: Full Parallel Implementation
- Create all 8 agent skeletons simultaneously
- Implement agents in parallel
- Minimize coordination overhead
- Fastest time to completion (~1.5-2 weeks)

**Key Decisions**:
- ✅ Full KB integration for all agents (adaptive querying)
- ✅ Production-ready code generation (validation, error handling, best practices)
- ✅ Implementation-first testing (get agents working, then add comprehensive tests)

---

## Agent Specifications

### 1. API Developer Agent

**Location**: `agents/backend/api_developer/`

**Capabilities**:
- `rest_api_development` - RESTful API design and implementation
- `graphql_api_development` - GraphQL schema and resolvers
- `grpc_service_development` - gRPC service definitions

**Technical Details**:
- **Model**: `gemini-2.0-flash`
- **Input Modalities**: TEXT, CODE
- **Output Types**: API implementations, OpenAPI/Swagger docs, API tests
- **Supported Languages**: TypeScript, Python, Go, Java
- **Frameworks**:
  - REST: Express.js, FastAPI, Gin, Spring Boot
  - GraphQL: Apollo Server, Strawberry, gqlgen
  - gRPC: grpc-node, grpcio, grpc-go
- **KB Integration**: Adaptive querying for API patterns and best practices
- **Lines of Code**: ~500-600

**Core Functions**:
```python
def generate_rest_api(task_id, language, framework, endpoints, auth_type)
def generate_graphql_api(task_id, language, schema, resolvers)
def generate_grpc_service(task_id, language, proto_definition)
def generate_api_documentation(task_id, api_spec)
def generate_api_tests(task_id, api_type, test_framework)
```

**Validation**:
- Syntax validation with language parsers
- OpenAPI 3.0 schema validation
- Security best practices check (auth, CORS, rate limiting)
- Generated code runs without errors

---

### 2. Database Engineer Agent

**Location**: `agents/backend/database_engineer/`

**Capabilities**:
- `schema_design` - Database schema modeling
- `migration_scripts` - Database migration generation
- `query_optimization` - Query performance tuning

**Technical Details**:
- **Model**: `gemini-2.0-flash`
- **Input Modalities**: TEXT, PDF (ER diagrams), CODE
- **Output Types**: SQL schemas, migrations, ER diagrams, optimization reports
- **Supported Databases**: PostgreSQL, MySQL, MongoDB, Redis
- **KB Integration**: Query patterns, indexing strategies, normalization rules
- **Lines of Code**: ~400-500

**Core Functions**:
```python
def design_database_schema(task_id, requirements, database_type, constraints)
def generate_migration_scripts(task_id, from_schema, to_schema, database_type)
def optimize_queries(task_id, queries, database_type, performance_targets)
def generate_er_diagram(task_id, schema, format="mermaid")
def validate_schema_design(task_id, schema, normalization_level)
```

**Validation**:
- SQL syntax validation
- Foreign key constraint verification
- Index strategy validation
- Migration script rollback support

---

### 3. Microservices Architect Agent

**Location**: `agents/backend/microservices_architect/`

**Capabilities**:
- `service_decomposition` - Breaking monoliths into services
- `api_gateway_design` - Gateway patterns and routing
- `event_driven_architecture` - Event-based communication design

**Technical Details**:
- **Model**: `gemini-2.0-flash-thinking-exp` (requires advanced reasoning)
- **Input Modalities**: TEXT, PDF (architecture diagrams), CODE
- **Output Types**: Service definitions, API gateway configs, event flow diagrams, architecture docs
- **Supported Patterns**: CQRS, Event Sourcing, Saga, Circuit Breaker, Service Mesh
- **KB Integration**: Architecture patterns, bounded contexts, DDD principles
- **Lines of Code**: ~600-700

**Core Functions**:
```python
def decompose_monolith(task_id, codebase_analysis, business_domains)
def design_api_gateway(task_id, services, routing_requirements, auth_strategy)
def design_event_driven_architecture(task_id, services, events, consistency_requirements)
def apply_cqrs_pattern(task_id, domain_model, read_write_separation)
def design_service_mesh(task_id, services, communication_patterns)
```

**Validation**:
- Bounded context validation (no domain leakage)
- Event flow consistency checks
- Gateway routing logic validation
- Pattern compliance verification

---

### 4. Data Engineer Agent

**Location**: `agents/backend/data_engineer/`

**Capabilities**:
- `etl_pipeline_development` - ETL/ELT pipeline creation
- `data_warehouse_design` - Data warehouse schema design
- `batch_processing` - Batch job orchestration

**Technical Details**:
- **Model**: `gemini-2.0-flash`
- **Input Modalities**: TEXT, DATA_FILES (CSV, JSON, XML)
- **Output Types**: Airflow DAGs, dbt models, data warehouse schemas, Spark jobs
- **Supported Tools**: Apache Airflow, dbt, BigQuery, Apache Spark, Redshift, Snowflake
- **KB Integration**: ETL patterns, data quality rules, warehouse schemas
- **Lines of Code**: ~400-500

**Core Functions**:
```python
def generate_etl_pipeline(task_id, source, destination, transformations, schedule)
def generate_dbt_models(task_id, source_tables, transformations, tests)
def design_data_warehouse(task_id, business_requirements, star_snowflake_schema)
def generate_spark_job(task_id, data_source, transformations, output_format)
def generate_data_quality_checks(task_id, data_schema, quality_rules)
```

**Validation**:
- Airflow DAG syntax validation
- dbt model compilation
- SQL transformation logic validation
- Data lineage verification

---

### 5. Message Queue Agent

**Location**: `agents/backend/message_queue/`

**Capabilities**:
- `kafka_setup` - Apache Kafka configuration
- `rabbitmq_setup` - RabbitMQ setup
- `pubsub_setup` - Google Cloud Pub/Sub configuration
- `event_schema_design` - Event schema versioning

**Technical Details**:
- **Model**: `gemini-2.0-flash`
- **Input Modalities**: TEXT, CODE
- **Output Types**: Broker configs, event schemas, producer/consumer code, schema registry
- **Supported Technologies**: Apache Kafka, RabbitMQ, Google Cloud Pub/Sub, Amazon SQS/SNS
- **KB Integration**: Messaging patterns, schema evolution strategies
- **Lines of Code**: ~300-400

**Core Functions**:
```python
def setup_kafka_cluster(task_id, broker_count, topics, partitions, replication_factor)
def setup_rabbitmq(task_id, exchanges, queues, bindings, policies)
def setup_pubsub(task_id, topics, subscriptions, filters, dead_letter_config)
def design_event_schema(task_id, event_type, payload_fields, schema_format)
def implement_producer_consumer(task_id, language, broker_type, events)
```

**Validation**:
- Configuration syntax validation
- Schema format validation (Avro, Protobuf, JSON Schema)
- Producer/consumer code compilation
- Backward compatibility check for schema changes

---

### 6. Cloud Infrastructure Agent

**Location**: `agents/infrastructure/cloud_infrastructure/`

**Capabilities**:
- `terraform_development` - Terraform IaC creation
- `cloudformation_development` - AWS CloudFormation templates
- `gcp_deployment_manager` - GCP Deployment Manager configs

**Technical Details**:
- **Model**: `gemini-2.0-flash`
- **Input Modalities**: TEXT, PDF (architecture diagrams)
- **Output Types**: Terraform modules, CloudFormation templates, GCP DM configs, infrastructure docs
- **Supported Cloud Providers**: GCP, AWS, Azure
- **Supported Services**:
  - Compute: VMs, App Engine, Cloud Run, Lambda, EC2
  - Storage: Cloud Storage, S3, Azure Blob
  - Networking: VPC, Load Balancers, CDN
  - Databases: Cloud SQL, RDS, Cosmos DB
- **KB Integration**: IaC patterns, security best practices, cost optimization
- **Lines of Code**: ~500-600

**Core Functions**:
```python
def generate_terraform_module(task_id, cloud_provider, resources, variables)
def generate_cloudformation_template(task_id, resources, parameters, conditions)
def generate_gcp_deployment_manager(task_id, resources, properties)
def generate_multi_cloud_setup(task_id, primary_cloud, dr_cloud, resources)
def generate_cost_optimization_plan(task_id, current_infrastructure)
```

**Validation**:
- Terraform/CloudFormation syntax validation
- Resource dependency validation
- Security group/firewall rule validation
- Cost estimation

---

### 7. Kubernetes Agent

**Location**: `agents/infrastructure/kubernetes/`

**Capabilities**:
- `manifest_creation` - K8s YAML manifest generation
- `helm_charts` - Helm chart development
- `service_mesh_config` - Istio/Linkerd configuration

**Technical Details**:
- **Model**: `gemini-2.0-flash`
- **Input Modalities**: TEXT, CODE
- **Output Types**: K8s manifests, Helm charts, service mesh configs, deployment strategies
- **Supported Tools**: Kubernetes 1.28+, Helm 3, Istio, Linkerd
- **Deployment Strategies**: Blue/Green, Canary, Rolling Update
- **KB Integration**: K8s patterns, resource sizing, security policies
- **Lines of Code**: ~400-500

**Core Functions**:
```python
def generate_k8s_manifests(task_id, app_spec, resources, config_maps, secrets)
def generate_helm_chart(task_id, app_name, values, templates, dependencies)
def generate_istio_config(task_id, services, routing_rules, policies)
def generate_deployment_strategy(task_id, strategy_type, rollout_config)
def generate_rbac_policies(task_id, service_accounts, roles, bindings)
```

**Validation**:
- YAML syntax validation
- Kubernetes API schema validation
- Resource limit validation
- RBAC policy validation
- Helm chart lint

---

### 8. Observability Agent

**Location**: `agents/infrastructure/observability/`

**Capabilities**:
- `prometheus_setup` - Prometheus configuration
- `grafana_dashboards` - Dashboard creation
- `distributed_tracing` - Tracing setup (Jaeger, Cloud Trace)

**Technical Details**:
- **Model**: `gemini-2.0-flash`
- **Input Modalities**: TEXT, CODE
- **Output Types**: Prometheus configs, Grafana dashboards, tracing configs, alert policies, SLO/SLI definitions
- **Supported Tools**: Prometheus, Grafana, Jaeger, Google Cloud Monitoring, OpenTelemetry
- **KB Integration**: Monitoring patterns, SLO best practices, alert thresholds
- **Lines of Code**: ~400-500

**Core Functions**:
```python
def generate_prometheus_config(task_id, scrape_targets, alert_rules, recording_rules)
def generate_grafana_dashboard(task_id, metrics, panels, layout, variables)
def generate_tracing_config(task_id, tracing_backend, sampling_rate, exporters)
def generate_cloud_monitoring_alerts(task_id, metrics, conditions, notification_channels)
def define_slo_sli(task_id, service_name, availability_target, latency_target)
```

**Validation**:
- Prometheus config syntax validation
- Grafana dashboard JSON validation
- Alert rule logic validation
- SLO/SLI threshold validation

---

## Implementation Strategy

### Phase 1: Foundation Setup (Day 1)

**Objective**: Create the complete directory structure and configuration for all 8 agents

#### Tasks:

**1.1 Create Directory Structure**
```bash
mkdir -p agents/backend/{api_developer,database_engineer,microservices_architect,data_engineer,message_queue}
mkdir -p agents/infrastructure/{cloud_infrastructure,kubernetes,observability}

# Create __init__.py files
touch agents/backend/__init__.py
touch agents/infrastructure/__init__.py
touch agents/backend/{api_developer,database_engineer,microservices_architect,data_engineer,message_queue}/__init__.py
touch agents/infrastructure/{cloud_infrastructure,kubernetes,observability}/__init__.py
```

**1.2 Update Configuration File**

Add to `config/agents_config.yaml` after the `frontend:` section:

```yaml
# Backend Engineering Agents
backend:
  enabled: true
  default_language: "typescript"
  kb_integration_enabled: true

  api_developer:
    name: "api_developer_agent"
    model: "gemini-2.0-flash"
    description: "Generates REST, GraphQL, and gRPC APIs with documentation"
    supported_api_types:
      - "rest"
      - "graphql"
      - "grpc"
    supported_languages:
      - "typescript"
      - "python"
      - "go"
      - "java"
    supported_frameworks:
      rest: ["express", "fastapi", "gin", "spring-boot"]
      graphql: ["apollo-server", "strawberry", "gqlgen"]
      grpc: ["grpc-node", "grpcio", "grpc-go"]
    kb_query_strategy: "adaptive"
    max_concurrent_tasks: 3

  database_engineer:
    name: "database_engineer_agent"
    model: "gemini-2.0-flash"
    description: "Designs database schemas, generates migrations, optimizes queries"
    supported_databases:
      - "postgresql"
      - "mysql"
      - "mongodb"
      - "redis"
    features:
      - "schema_design"
      - "migration_generation"
      - "query_optimization"
      - "er_diagram_generation"
    kb_query_strategy: "adaptive"
    max_concurrent_tasks: 3

  microservices_architect:
    name: "microservices_architect_agent"
    model: "gemini-2.0-flash-thinking-exp"  # Reasoning model
    description: "Decomposes monoliths, designs microservices architecture"
    supported_patterns:
      - "cqrs"
      - "event_sourcing"
      - "saga"
      - "circuit_breaker"
      - "service_mesh"
    capabilities:
      - "service_decomposition"
      - "api_gateway_design"
      - "event_driven_architecture"
    kb_query_strategy: "adaptive"
    max_concurrent_tasks: 2  # Lower due to reasoning model

  data_engineer:
    name: "data_engineer_agent"
    model: "gemini-2.0-flash"
    description: "Creates ETL pipelines, designs data warehouses"
    supported_tools:
      - "airflow"
      - "dbt"
      - "bigquery"
      - "apache_spark"
      - "redshift"
      - "snowflake"
    capabilities:
      - "etl_pipeline_development"
      - "data_warehouse_design"
      - "batch_processing"
    kb_query_strategy: "adaptive"
    max_concurrent_tasks: 3

  message_queue:
    name: "message_queue_agent"
    model: "gemini-2.0-flash"
    description: "Sets up message brokers and event schemas"
    supported_technologies:
      - "kafka"
      - "rabbitmq"
      - "google_pubsub"
      - "amazon_sqs_sns"
    schema_formats:
      - "avro"
      - "protobuf"
      - "json_schema"
    kb_query_strategy: "adaptive"
    max_concurrent_tasks: 3

# Infrastructure Agents
infrastructure:
  enabled: true
  kb_integration_enabled: true

  cloud_infrastructure:
    name: "cloud_infrastructure_agent"
    model: "gemini-2.0-flash"
    description: "Generates IaC for multi-cloud deployments"
    supported_iac_tools:
      - "terraform"
      - "cloudformation"
      - "gcp_deployment_manager"
    supported_cloud_providers:
      - "gcp"
      - "aws"
      - "azure"
    capabilities:
      - "terraform_development"
      - "cloudformation_development"
      - "gcp_deployment_manager"
      - "multi_cloud_setup"
    kb_query_strategy: "adaptive"
    max_concurrent_tasks: 3

  kubernetes:
    name: "kubernetes_agent"
    model: "gemini-2.0-flash"
    description: "Generates Kubernetes manifests and Helm charts"
    k8s_version: "1.28+"
    helm_version: "3"
    supported_service_mesh:
      - "istio"
      - "linkerd"
    deployment_strategies:
      - "blue_green"
      - "canary"
      - "rolling_update"
    capabilities:
      - "manifest_creation"
      - "helm_charts"
      - "service_mesh_config"
    kb_query_strategy: "adaptive"
    max_concurrent_tasks: 3

  observability:
    name: "observability_agent"
    model: "gemini-2.0-flash"
    description: "Sets up monitoring, alerting, and distributed tracing"
    supported_tools:
      - "prometheus"
      - "grafana"
      - "jaeger"
      - "google_cloud_monitoring"
      - "opentelemetry"
    capabilities:
      - "prometheus_setup"
      - "grafana_dashboards"
      - "distributed_tracing"
      - "slo_sli_definition"
    kb_query_strategy: "adaptive"
    max_concurrent_tasks: 3
```

**1.3 Create Agent Skeletons**

For each agent, create:
- `agents/{category}/{agent_name}/agent.py` - Main agent class
- `agents/{category}/{agent_name}/capability.py` - Capability declaration

**Skeleton Template** (same for all 8 agents):

```python
# agents/{category}/{agent_name}/agent.py

from typing import Dict, Any, List, Optional
import json
from vertexai.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration
from shared.utils.kb_integration_mixin import DynamicKnowledgeBaseIntegration


class AgentNameAgent(A2AEnabledAgent, DynamicKnowledgeBaseIntegration):
    """
    [Agent Description]

    Capabilities:
    - capability_1
    - capability_2
    - capability_3
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        vector_db_client=None,
        model_name: str = "gemini-2.0-flash"  # or "gemini-2.0-flash-thinking-exp"
    ):
        """Initialize the agent."""
        # Initialize base classes
        A2AEnabledAgent.__init__(self, context, message_bus)

        # Store context
        self.context = context
        self.orchestrator_id = orchestrator_id

        # Initialize A2A integration
        self.a2a = A2AIntegration(context, message_bus, orchestrator_id)

        # Initialize KB integration (full integration)
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

        # Agent-specific state
        self.history: List[Dict[str, Any]] = []

    def handle_task_assignment(self, message: Dict[str, Any]) -> None:
        """
        Handle TASK_ASSIGNMENT message from orchestrator.

        Args:
            message: A2A message with task details
        """
        payload = message.get("payload", {})
        task_id = payload.get("task_id")
        task_type = payload.get("task_type")
        parameters = payload.get("parameters", {})

        try:
            # Route to appropriate handler
            if task_type == "main_task_type":
                result = self.main_tool_function(task_id=task_id, **parameters)
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            # Send completion
            self.a2a.send_completion(
                task_id=task_id,
                artifacts=result,
                metrics={
                    "kb_queries_used": getattr(self, "_kb_query_count", 0)
                }
            )

        except Exception as e:
            self.a2a.send_error_report(
                task_id=task_id,
                error_type="execution_error",
                error_message=str(e)
            )

    @A2AIntegration.with_task_tracking
    def main_tool_function(
        self,
        task_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Main tool function.

        Args:
            task_id: Task ID for tracking
            **kwargs: Function-specific parameters

        Returns:
            Dict with status and generated artifacts
        """
        # Query KB if enabled
        kb_context = ""
        if hasattr(self, 'should_query_kb') and self.should_query_kb(kwargs):
            kb_results = self.execute_dynamic_query(
                query_text=str(kwargs),
                max_results=5
            )
            kb_context = self._format_kb_results(kb_results)

        # Build prompt
        prompt = self._build_prompt(kb_context=kb_context, **kwargs)

        # Generate with LLM
        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        # Parse and validate result
        result = self._parse_and_validate_result(response.text)

        # Store in history
        self.history.append({
            "task_id": task_id,
            "input": kwargs,
            "output": result,
            "kb_used": bool(kb_context)
        })

        return result

    def _build_prompt(self, kb_context: str = "", **kwargs) -> str:
        """Build prompt for LLM."""
        # TODO: Implement agent-specific prompt
        return f"Generate output based on: {kwargs}"

    def _parse_and_validate_result(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate LLM response."""
        # TODO: Implement agent-specific parsing and validation
        return {
            "status": "success",
            "result": response_text
        }

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

        formatted = "Relevant knowledge from codebase:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result.get('content', '')}\n\n"
        return formatted


# Standalone tool function for testing
def tool_function_name(**kwargs) -> Dict[str, Any]:
    """Standalone tool function."""
    agent = AgentNameAgent(
        context={},
        message_bus=None,
        orchestrator_id=""
    )
    return agent.main_tool_function(**kwargs)
```

**Deliverables (Day 1)**:
- ✅ 16 new directories
- ✅ 18 `__init__.py` files
- ✅ Updated `config/agents_config.yaml` (~200 lines)
- ✅ 8 agent skeleton files (~200 lines each = 1,600 lines)
- ✅ Ready for parallel implementation

---

### Phase 2: Parallel Implementation (Days 2-8)

**Objective**: Implement all 8 agents with production-ready code generation capabilities

#### Implementation Guidelines:

**For Each Agent**:

1. **Implement capability declaration** (`capability.py`)
   - Complete `AgentCapability` with all metadata
   - Define precise capabilities set
   - Configure KB integration settings
   - Set performance and cost baselines

2. **Implement core tool functions** (`agent.py`)
   - Main generation functions (3-5 per agent)
   - Prompt engineering for production-ready output
   - Output parsing and validation
   - Error handling and edge cases

3. **Implement validation layer**
   - Syntax validation (AST parsing, YAML validation, etc.)
   - Semantic validation (logic checks, best practices)
   - Security validation (vulnerabilities, misconfigurations)
   - Generated code testing (where applicable)

4. **KB integration**
   - Query triggers (start, error, checkpoint)
   - Context formatting
   - Fallback strategies

5. **Documentation**
   - Inline docstrings
   - Usage examples in comments
   - Parameter descriptions

#### Agent-Specific Implementation Details:

**Days 2-3: API Developer Agent**
```python
# Key functions to implement:
def generate_rest_api(self, task_id, language, framework, endpoints, auth_type)
def generate_graphql_api(self, task_id, language, schema, resolvers)
def generate_grpc_service(self, task_id, language, proto_definition)
def generate_api_documentation(self, task_id, api_spec)

# Validation:
- AST parsing for syntax
- OpenAPI 3.0 schema validation
- Security checks (auth, CORS, input validation)
```

**Days 2-3: Database Engineer Agent**
```python
# Key functions to implement:
def design_database_schema(self, task_id, requirements, database_type)
def generate_migration_scripts(self, task_id, from_schema, to_schema)
def optimize_queries(self, task_id, queries, database_type)
def generate_er_diagram(self, task_id, schema)

# Validation:
- SQL syntax validation
- FK constraint verification
- Index strategy validation
```

**Days 3-4: Microservices Architect Agent** (Use reasoning model)
```python
# Key functions to implement:
def decompose_monolith(self, task_id, codebase_analysis, domains)
def design_api_gateway(self, task_id, services, routing)
def design_event_architecture(self, task_id, services, events)
def apply_cqrs_pattern(self, task_id, domain_model)

# Validation:
- Bounded context validation
- Event flow consistency
- Pattern compliance
```

**Days 4-5: Data Engineer Agent**
```python
# Key functions to implement:
def generate_etl_pipeline(self, task_id, source, dest, transformations)
def generate_dbt_models(self, task_id, source_tables, transformations)
def design_data_warehouse(self, task_id, requirements, schema_type)
def generate_spark_job(self, task_id, source, transformations)

# Validation:
- Airflow DAG syntax
- dbt model compilation
- SQL transformation validation
```

**Days 5-6: Message Queue Agent**
```python
# Key functions to implement:
def setup_kafka_cluster(self, task_id, topics, partitions)
def setup_rabbitmq(self, task_id, exchanges, queues)
def setup_pubsub(self, task_id, topics, subscriptions)
def design_event_schema(self, task_id, event_type, fields)

# Validation:
- Config syntax validation
- Schema format validation (Avro, Protobuf)
- Backward compatibility check
```

**Days 6-7: Cloud Infrastructure Agent**
```python
# Key functions to implement:
def generate_terraform_module(self, task_id, cloud, resources)
def generate_cloudformation(self, task_id, resources)
def generate_gcp_deployment_manager(self, task_id, resources)
def generate_multi_cloud_setup(self, task_id, primary, dr)

# Validation:
- Terraform/CF syntax
- Resource dependency validation
- Security group validation
```

**Days 7-8: Kubernetes Agent**
```python
# Key functions to implement:
def generate_k8s_manifests(self, task_id, app_spec, resources)
def generate_helm_chart(self, task_id, app_name, values)
def generate_istio_config(self, task_id, services, routing)
def generate_deployment_strategy(self, task_id, strategy_type)

# Validation:
- YAML syntax
- K8s API schema validation
- Resource limit validation
- Helm chart lint
```

**Days 7-8: Observability Agent**
```python
# Key functions to implement:
def generate_prometheus_config(self, task_id, targets, alerts)
def generate_grafana_dashboard(self, task_id, metrics, panels)
def generate_tracing_config(self, task_id, backend, sampling)
def define_slo_sli(self, task_id, service, targets)

# Validation:
- Prometheus config syntax
- Grafana JSON validation
- Alert rule logic validation
```

**Deliverables (Days 2-8)**:
- ✅ 8 fully implemented agents (~3,500-4,400 lines)
- ✅ 8 capability declarations (~1,200 lines)
- ✅ Production-ready code generation with validation
- ✅ Full KB integration

---

### Phase 3: Testing & Validation (Days 9-10)

**Objective**: Comprehensive testing of all 8 agents

#### 3.1 Mock Tests (Day 9)

**Update**: `scripts/test_agents_with_mocks.py`

Add test functions for all 8 agents:

```python
def test_api_developer_agent():
    """Test API Developer Agent with mock inputs."""
    from agents.backend.api_developer.agent import generate_rest_api

    print("\n" + "="*80)
    print("TESTING: API Developer Agent")
    print("="*80)

    # Test 1: REST API generation
    print("\n[Test 1] Generate REST API (Express.js)")
    print("-" * 80)
    result = generate_rest_api(
        language="typescript",
        framework="express",
        endpoints=[
            {"method": "GET", "path": "/users", "description": "List users"},
            {"method": "POST", "path": "/users", "description": "Create user"}
        ],
        auth_type="jwt"
    )
    print(f"✓ Generated API code (length: {len(result.get('code', ''))})")
    assert result["status"] == "success"
    assert "code" in result
    assert "documentation" in result
    print("✓ All assertions passed")

    # Test 2: GraphQL API generation
    print("\n[Test 2] Generate GraphQL API (Apollo Server)")
    print("-" * 80)
    result = generate_graphql_api(
        language="typescript",
        schema="""
        type User {
            id: ID!
            name: String!
            email: String!
        }
        type Query {
            users: [User!]!
        }
        """,
        resolvers=["Query.users"]
    )
    assert result["status"] == "success"
    print("✓ All assertions passed")

# Add similar test functions for all other agents...
```

**Run Mock Tests**:
```bash
python scripts/test_agents_with_mocks.py
```

**Expected Output**: All 8 agents pass mock tests in <5 seconds

#### 3.2 LLM Integration Tests (Day 10)

**Create**: `tests/agent_tests/test_milestone_4_agents.py`

```python
import pytest
from tests.agent_tests.agent_test_framework import AgentTestRunner, AgentTestCase

# API Developer Agent Tests
def test_api_developer_rest_generation():
    """Test REST API generation with real LLM."""
    test_case = AgentTestCase(
        agent_name="api_developer",
        test_name="rest_api_generation",
        task_type="generate_rest_api",
        inputs={
            "language": "python",
            "framework": "fastapi",
            "endpoints": [
                {"method": "GET", "path": "/products", "description": "List products"},
                {"method": "POST", "path": "/products", "description": "Create product"}
            ],
            "auth_type": "bearer"
        },
        expected_outputs={
            "status": "success",
            "code": str,  # Must be string
            "documentation": str
        },
        validation_rules=[
            "code_compiles",
            "has_auth_middleware",
            "openapi_valid"
        ]
    )

    runner = AgentTestRunner()
    result = runner.run_test(test_case)

    assert result.passed
    assert result.execution_time_seconds < 30

# Add tests for all agents and capabilities...
```

**Run LLM Tests**:
```bash
# Test all new agents
python scripts/test_agents_with_llm.py --agent api_developer
python scripts/test_agents_with_llm.py --agent database_engineer
python scripts/test_agents_with_llm.py --agent microservices_architect
python scripts/test_agents_with_llm.py --agent data_engineer
python scripts/test_agents_with_llm.py --agent message_queue
python scripts/test_agents_with_llm.py --agent cloud_infrastructure
python scripts/test_agents_with_llm.py --agent kubernetes
python scripts/test_agents_with_llm.py --agent observability

# Or test all at once
python scripts/test_agents_with_llm.py --agent all
```

#### 3.3 Test Coverage Analysis

**Run**:
```bash
pytest tests/agent_tests/ --cov=agents/backend --cov=agents/infrastructure --cov-report=html
```

**Target**: >80% coverage for all new code

**Deliverables (Days 9-10)**:
- ✅ Mock tests for all 8 agents (~500-700 lines)
- ✅ LLM integration tests (~300-400 lines)
- ✅ All tests passing
- ✅ Test coverage >80%

---

### Phase 4: Documentation & Polish (Days 11-12)

**Objective**: Finalize documentation and ensure production readiness

#### 4.1 Update Documentation (Day 11)

**Update `README.md`**:

Add Milestone 4 agents to the agent list:

```markdown
### Backend Engineering Agents (5)
- **API Developer**: Generates REST, GraphQL, and gRPC APIs with documentation
- **Database Engineer**: Designs schemas, generates migrations, optimizes queries
- **Microservices Architect**: Decomposes monoliths, designs microservices architecture
- **Data Engineer**: Creates ETL pipelines, designs data warehouses
- **Message Queue**: Sets up message brokers and event schemas

### Infrastructure Agents (3)
- **Cloud Infrastructure**: Generates IaC for multi-cloud deployments
- **Kubernetes**: Creates K8s manifests, Helm charts, service mesh configs
- **Observability**: Sets up monitoring, alerting, and distributed tracing
```

**Update `AGENT-TESTING-GUIDE.md`**:

Add testing examples for Milestone 4 agents.

**Create `docs/MILESTONE-4-USAGE.md`**:

```markdown
# Milestone 4 Agents: Usage Guide

## API Developer Agent

### Generate REST API

\`\`\`python
from agents.backend.api_developer.agent import generate_rest_api

result = generate_rest_api(
    language="typescript",
    framework="express",
    endpoints=[
        {
            "method": "GET",
            "path": "/users/:id",
            "description": "Get user by ID"
        }
    ],
    auth_type="jwt"
)

print(result["code"])
print(result["documentation"])
\`\`\`

[Add examples for all agents...]
```

#### 4.2 Code Quality (Day 12)

**Format code**:
```bash
black agents/backend/ agents/infrastructure/
```

**Lint**:
```bash
flake8 agents/backend/ agents/infrastructure/ --max-line-length=100
```

**Type checking**:
```bash
mypy agents/backend/ agents/infrastructure/ --ignore-missing-imports
```

**Fix all issues found**

#### 4.3 Deployment Preparation

**Verify capability declarations**:
- All 8 agents have complete `AGENT_CAPABILITY` in `capability.py`
- All capabilities match config entries

**Test deployment script compatibility**:
```bash
# Dry run
python scripts/deploy_vertex_agents.py \
  --project-id test-project \
  --location us-central1 \
  --staging-bucket gs://test-bucket \
  --config config/agents_config.yaml \
  --dry-run \
  --agents backend.api_developer,backend.database_engineer
```

**Update agent registry schema** (if needed):
- Ensure `config/agent_registry.json` supports new agent types

**Deliverables (Days 11-12)**:
- ✅ Updated documentation
- ✅ Code formatted and linted
- ✅ Type checking passed
- ✅ Deployment tested
- ✅ Ready for production deployment

---

## Technical Architecture

### Agent Class Hierarchy

```
A2AEnabledAgent (Base)
    └── DynamicKnowledgeBaseIntegration (Mixin)
            └── Backend/Infrastructure Agents (Milestone 4)
                    ├── APIDevAgent
                    ├── DatabaseEngineerAgent
                    ├── MicroservicesArchitectAgent
                    ├── DataEngineerAgent
                    ├── MessageQueueAgent
                    ├── CloudInfrastructureAgent
                    ├── KubernetesAgent
                    └── ObservabilityAgent
```

### A2A Communication Flow

```
Orchestrator
    │
    ├─ TASK_ASSIGNMENT ──→ Backend/Infrastructure Agent
    │                            │
    │                            ├─ Query KB (adaptive)
    │                            │
    │                            ├─ Generate with LLM
    │                            │
    │                            ├─ Validate output
    │                            │
    │                            └─ TASK_COMPLETION ──→ Orchestrator
    │
    └─ (or ERROR_REPORT if failed)
```

### KB Integration Architecture

```
Agent
    │
    ├─ should_query_kb(task)
    │       │
    │       └─ Adaptive strategy:
    │           - Always at task start
    │           - On error/validation fail
    │           - At checkpoints
    │           - Based on task complexity
    │
    ├─ execute_dynamic_query(query)
    │       │
    │       └─ Vector Search
    │           - Semantic search
    │           - Top-K results (5-10)
    │           - Cached if repeated
    │
    └─ format_kb_results(results)
            │
            └─ Context string for LLM prompt
```

### Production-Ready Code Generation Pipeline

```
Input Parameters
    │
    ├─ Query KB for patterns/examples
    │
    ├─ Build structured prompt with:
    │   - Task description
    │   - Language/framework requirements
    │   - KB context
    │   - Best practices
    │   - Security requirements
    │
    ├─ Generate with LLM
    │   - Temperature: 0.2 (deterministic)
    │   - Max tokens: 8192
    │
    ├─ Parse response (extract code blocks)
    │
    ├─ Validate:
    │   ├─ Syntax (AST parsing)
    │   ├─ Semantics (logic checks)
    │   ├─ Security (vulnerability scan)
    │   └─ Best practices
    │
    ├─ If validation fails:
    │   └─ Retry with feedback (up to 3 times)
    │
    └─ Return validated output + metadata
```

---

## Testing Strategy

### Three-Tier Testing Approach

#### Tier 1: Mock Tests (Fast, <5 seconds)
- **Purpose**: Validate tool function logic without LLM calls
- **Scope**: All 8 agents
- **Location**: `scripts/test_agents_with_mocks.py`
- **Run frequency**: Every commit
- **Assertions**:
  - Function returns expected structure
  - Required fields present
  - Type checking

#### Tier 2: LLM Integration Tests (Slow, ~5-30 seconds per test)
- **Purpose**: Validate real LLM generation quality
- **Scope**: All 8 agents, 3-5 tests per agent
- **Location**: `tests/agent_tests/test_milestone_4_agents.py`
- **Run frequency**: Before PR merge
- **Assertions**:
  - Generated code compiles/runs
  - Validates against schemas
  - Security checks pass
  - Performance within limits

#### Tier 3: End-to-End Tests (Manual/CI)
- **Purpose**: Validate full A2A workflow
- **Scope**: Selected critical paths
- **Run frequency**: Pre-release
- **Workflow**:
  1. Orchestrator assigns task
  2. Agent processes with KB queries
  3. Validator validates output
  4. Agent iterates with feedback (if needed)
  5. Final completion

### Test Coverage Targets

| Component | Target Coverage |
|-----------|----------------|
| Agent core logic | >85% |
| Tool functions | >90% |
| Validation logic | >80% |
| KB integration | >70% |
| Overall | >80% |

---

## Success Criteria

### Functional Criteria

✅ **All 8 agents implemented and functional**
- Each agent has complete implementation
- All advertised capabilities work
- A2A integration complete

✅ **Production-ready code generation**
- Generated code is syntactically correct
- Passes validation checks
- Includes error handling
- Follows best practices

✅ **Full KB integration**
- All agents use adaptive KB querying
- Query results improve output quality
- Fallback works when KB unavailable

✅ **Comprehensive testing**
- Mock tests for all agents
- LLM tests with >80% coverage
- All tests passing

✅ **Configuration and deployment**
- All agents in `agents_config.yaml`
- Capability declarations complete
- Deployment script compatible

### Quality Criteria

✅ **Code quality**
- Formatted with Black
- Passes Flake8 linting
- Type hints pass MyPy
- No critical issues

✅ **Documentation**
- All functions have docstrings
- Usage examples provided
- Testing guide updated

✅ **Performance**
- Agent response time <30 seconds
- KB queries <3 seconds
- Validation <5 seconds

### Deployment Criteria

✅ **Ready for Vertex AI deployment**
- All agents can be deployed via script
- Agent registry updates correctly
- Pub/Sub topics created

✅ **Integration ready**
- Works with existing orchestrator
- Compatible with Phase 2 dynamic mode
- No breaking changes to existing agents

---

## Risk Mitigation

### Risk 1: Code Generation Quality
**Risk**: Generated code may not be production-ready

**Mitigation**:
- Multi-layer validation (syntax, semantics, security)
- KB integration provides proven patterns
- Retry mechanism with feedback
- Conservative generation parameters (low temperature)
- Comprehensive test suite

### Risk 2: LLM Response Parsing
**Risk**: LLM may return unparseable output

**Mitigation**:
- Structured prompts with explicit format requirements
- Robust parsing with fallbacks
- JSON mode where applicable
- Error handling with retry

### Risk 3: KB Query Performance
**Risk**: KB queries may slow down agents

**Mitigation**:
- Adaptive querying (only when beneficial)
- Result caching
- Configurable query limits
- Async queries where possible
- Fallback to generation without KB

### Risk 4: Testing Coverage
**Risk**: Tests may not catch all issues

**Mitigation**:
- Three-tier testing approach
- Both mock and real LLM tests
- Manual end-to-end testing
- Performance benchmarking
- Security scanning

### Risk 5: Parallel Implementation Coordination
**Risk**: Parallel work may cause conflicts

**Mitigation**:
- Clear agent boundaries (no overlap)
- Standard skeleton structure
- Shared utility functions
- Regular synchronization
- Git workflow with feature branches

### Risk 6: Deployment Complexity
**Risk**: Deploying 8 new agents may have issues

**Mitigation**:
- Deployment dry-run testing
- Incremental deployment (deploy 2-3 at a time)
- Rollback plan
- Monitoring and alerts
- Staged rollout (dev → staging → prod)

---

## Timeline and Milestones

### Week 1: Foundation + Implementation

**Day 1 (Monday)**: Foundation Setup
- ✅ Directory structure created
- ✅ Config updated
- ✅ Agent skeletons created

**Days 2-3 (Tue-Wed)**: Backend Agents (Part 1)
- ✅ API Developer Agent implemented
- ✅ Database Engineer Agent implemented
- ✅ Message Queue Agent implemented

**Days 4-5 (Thu-Fri)**: Backend Agents (Part 2) + Infrastructure (Part 1)
- ✅ Microservices Architect Agent implemented
- ✅ Data Engineer Agent implemented
- ✅ Cloud Infrastructure Agent implemented

### Week 2: Infrastructure + Testing + Documentation

**Days 6-7 (Mon-Tue)**: Infrastructure Agents (Part 2)
- ✅ Kubernetes Agent implemented
- ✅ Observability Agent implemented

**Day 8 (Wednesday)**: Implementation Polish
- ✅ All 8 agents complete and functional
- ✅ Internal review and fixes

**Day 9 (Thursday)**: Testing
- ✅ Mock tests added and passing
- ✅ LLM tests added and passing
- ✅ Test coverage >80%

**Day 10 (Friday)**: Testing + Documentation
- ✅ All tests validated
- ✅ Documentation updated
- ✅ Usage guide created

**Days 11-12 (Mon-Tue)**: Polish + Deployment Prep
- ✅ Code formatted and linted
- ✅ Type checking passed
- ✅ Deployment tested
- ✅ **Milestone 4 Complete** 🎉

---

## Appendix A: File Checklist

### New Files to Create (Total: 34 files)

#### Directory Structure (18 files)
- [ ] `agents/backend/__init__.py`
- [ ] `agents/backend/api_developer/__init__.py`
- [ ] `agents/backend/database_engineer/__init__.py`
- [ ] `agents/backend/microservices_architect/__init__.py`
- [ ] `agents/backend/data_engineer/__init__.py`
- [ ] `agents/backend/message_queue/__init__.py`
- [ ] `agents/infrastructure/__init__.py`
- [ ] `agents/infrastructure/cloud_infrastructure/__init__.py`
- [ ] `agents/infrastructure/kubernetes/__init__.py`
- [ ] `agents/infrastructure/observability/__init__.py`

#### Agent Implementation Files (16 files)
- [ ] `agents/backend/api_developer/agent.py`
- [ ] `agents/backend/api_developer/capability.py`
- [ ] `agents/backend/database_engineer/agent.py`
- [ ] `agents/backend/database_engineer/capability.py`
- [ ] `agents/backend/microservices_architect/agent.py`
- [ ] `agents/backend/microservices_architect/capability.py`
- [ ] `agents/backend/data_engineer/agent.py`
- [ ] `agents/backend/data_engineer/capability.py`
- [ ] `agents/backend/message_queue/agent.py`
- [ ] `agents/backend/message_queue/capability.py`
- [ ] `agents/infrastructure/cloud_infrastructure/agent.py`
- [ ] `agents/infrastructure/cloud_infrastructure/capability.py`
- [ ] `agents/infrastructure/kubernetes/agent.py`
- [ ] `agents/infrastructure/kubernetes/capability.py`
- [ ] `agents/infrastructure/observability/agent.py`
- [ ] `agents/infrastructure/observability/capability.py`

#### Documentation Files
- [ ] `docs/MILESTONE-4-USAGE.md` (new)

### Files to Update

- [ ] `config/agents_config.yaml` (add backend + infrastructure sections)
- [ ] `README.md` (add Milestone 4 agents)
- [ ] `AGENT-TESTING-GUIDE.md` (add testing examples)
- [ ] `scripts/test_agents_with_mocks.py` (add 8 test functions)
- [ ] `tests/agent_tests/test_milestone_4_agents.py` (new file with LLM tests)

---

## Appendix B: Key Dependencies

### Python Packages (Already in requirements.txt)
- `google-cloud-aiplatform` - Vertex AI SDK
- `google-cloud-pubsub` - Pub/Sub for A2A
- `vertexai` - Generative AI models
- `pyyaml` - Config parsing
- `pytest` - Testing framework
- `black` - Code formatting
- `flake8` - Linting
- `mypy` - Type checking

### External Services (Already Configured)
- Google Cloud Vertex AI
- Google Cloud Pub/Sub
- Vector Search (Matching Engine)
- Cloud Storage (staging bucket)

---

## Appendix C: Prompt Engineering Guidelines

### General Principles for Production-Ready Code

1. **Structured Output Requests**
   ```
   Generate [language] code for [purpose].

   Requirements:
   - Use [framework] version [version]
   - Include error handling for [scenarios]
   - Follow [style guide] conventions
   - Add inline documentation

   Return code in a JSON object:
   {
     "code": "...",
     "tests": "...",
     "documentation": "..."
   }
   ```

2. **KB Context Integration**
   ```
   Based on these examples from the codebase:
   [KB results here]

   Generate similar code that follows the established patterns.
   ```

3. **Validation Requirements**
   ```
   The generated code MUST:
   - Compile without errors
   - Pass [linter] checks
   - Include error handling
   - Have no security vulnerabilities
   ```

4. **Iterative Refinement**
   ```
   Previous attempt failed validation:
   [Validation errors here]

   Please fix these issues in the next version.
   ```

---

## Appendix D: Success Metrics

### Quantitative Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Lines of code | 5,300-6,400 | `cloc agents/backend agents/infrastructure` |
| Test coverage | >80% | `pytest --cov` |
| Agent response time | <30s | LLM integration tests |
| KB query time | <3s | Performance benchmarks |
| Mock test runtime | <5s | `time python scripts/test_agents_with_mocks.py` |
| Code generation success rate | >85% | LLM test pass rate |

### Qualitative Metrics

| Metric | Assessment Method |
|--------|------------------|
| Code quality | Manual review, linting |
| Documentation completeness | Peer review |
| Integration compatibility | End-to-end tests |
| Production readiness | Deployment dry-run |
| Developer experience | Usability testing |

---

## Conclusion

This implementation plan provides a comprehensive roadmap for Milestone 4, delivering 8 production-ready AI agents with full KB integration in 1.5-2 weeks. The parallel implementation approach maximizes velocity while the structured testing and validation ensures quality. All prerequisites are in place, and the plan mitigates key risks through multiple validation layers and incremental delivery.

**Next Steps**:
1. ✅ Review and approve this plan
2. ✅ Begin Day 1: Foundation Setup
3. ✅ Execute parallel implementation
4. ✅ Complete testing and documentation
5. ✅ Deploy to production

**Milestone 4 Status**: Ready to begin implementation 🚀
