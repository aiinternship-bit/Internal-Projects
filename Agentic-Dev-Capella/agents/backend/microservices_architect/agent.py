"""
agents/backend/microservices_architect/agent.py

Microservices Architect Agent - Decomposes monoliths, designs microservices architecture.

Uses advanced reasoning to design service boundaries, API gateways, event-driven
architectures, and microservices patterns (CQRS, Event Sourcing, Saga, etc.).
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


class MicroservicesArchitectAgent(A2AEnabledAgent, DynamicKnowledgeBaseIntegration):
    """
    Microservices Architect Agent for distributed system design.

    Capabilities:
    - Service decomposition from monoliths
    - API gateway design
    - Event-driven architecture
    - CQRS pattern implementation
    - Event sourcing design
    - Saga pattern for distributed transactions
    - Service mesh configuration
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        vector_db_client=None,
        model_name: str = "gemini-2.0-flash-thinking-exp-1219"  # Reasoning model
    ):
        """Initialize Microservices Architect Agent."""
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

        # Initialize Vertex AI with reasoning model
        aiplatform.init(
            project=context.get("project_id"),
            location=context.get("location", "us-central1")
        )

        self.model = GenerativeModel(model_name)
        self.architecture_history: List[Dict[str, Any]] = []

    def handle_task_assignment(self, message: Dict[str, Any]) -> None:
        """Handle TASK_ASSIGNMENT message from orchestrator."""
        payload = message.get("payload", {})
        task_id = payload.get("task_id")
        task_type = payload.get("task_type")
        parameters = payload.get("parameters", {})

        try:
            if task_type == "decompose_monolith":
                result = self.decompose_monolith(task_id=task_id, **parameters)
            elif task_type == "design_api_gateway":
                result = self.design_api_gateway(task_id=task_id, **parameters)
            elif task_type == "design_event_driven_architecture":
                result = self.design_event_driven_architecture(task_id=task_id, **parameters)
            elif task_type == "apply_cqrs_pattern":
                result = self.apply_cqrs_pattern(task_id=task_id, **parameters)
            elif task_type == "design_service_mesh":
                result = self.design_service_mesh(task_id=task_id, **parameters)
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
                error_type="ARCHITECTURE_DESIGN_FAILED",
                error_message=str(e),
                stack_trace=""
            )

    @A2AIntegration.with_task_tracking
    def decompose_monolith(
        self,
        codebase_analysis: Dict[str, Any],
        business_domains: List[str],
        decomposition_strategy: str = "domain_driven",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Decompose a monolithic application into microservices.

        Args:
            codebase_analysis: Analysis of current monolith (modules, dependencies, etc.)
            business_domains: List of identified business domains
            decomposition_strategy: Strategy (domain_driven, subdomain, strangler_fig)
            task_id: Optional task ID

        Returns:
            {
                "services": List[Dict],
                "service_boundaries": Dict,
                "migration_strategy": str,
                "architecture_diagram": str,
                "documentation": str
            }
        """
        start_time = datetime.utcnow()
        print(f"[Microservices Architect] Decomposing monolith using {decomposition_strategy} strategy")

        # Query KB for decomposition patterns
        kb_context = ""
        if hasattr(self, 'should_query_kb') and self.should_query_kb(codebase_analysis):
            kb_results = self.execute_dynamic_query(
                query_type="decomposition_patterns",
                context={
                    "strategy": decomposition_strategy,
                    "domains": business_domains
                },
                task_id=task_id
            )
            if kb_results:
                kb_context = self._format_kb_results(kb_results)

        # Build prompt for reasoning model
        prompt = self._build_decomposition_prompt(
            codebase_analysis=codebase_analysis,
            business_domains=business_domains,
            decomposition_strategy=decomposition_strategy,
            kb_context=kb_context
        )

        # Generate with reasoning model (will include thinking process)
        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        # Parse result
        result = self._parse_architecture_design(response.text)

        # Add metadata
        duration = (datetime.utcnow() - start_time).total_seconds() / 60
        result.update({
            "decomposition_strategy": decomposition_strategy,
            "service_count": len(result.get("services", [])),
            "duration_minutes": duration,
            "timestamp": datetime.utcnow().isoformat()
        })

        self.architecture_history.append({
            "task_id": task_id,
            "operation": "decompose_monolith",
            "service_count": result["service_count"],
            "timestamp": result["timestamp"]
        })

        return result

    @A2AIntegration.with_task_tracking
    def design_api_gateway(
        self,
        services: List[Dict[str, Any]],
        routing_requirements: Dict[str, Any],
        auth_strategy: str = "jwt",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Design API Gateway for microservices.

        Args:
            services: List of microservices with their endpoints
            routing_requirements: Routing rules, load balancing, etc.
            auth_strategy: Authentication strategy
            task_id: Optional task ID

        Returns:
            {
                "gateway_config": str,
                "routing_rules": List[Dict],
                "middleware": List[str],
                "security_config": Dict,
                "documentation": str
            }
        """
        print(f"[Microservices Architect] Designing API Gateway")

        # Query KB for API gateway patterns
        kb_context = ""
        if hasattr(self, 'should_query_kb') and self.should_query_kb({"services": len(services)}):
            kb_results = self.execute_dynamic_query(
                query_type="api_gateway_patterns",
                context={"auth": auth_strategy, "service_count": len(services)},
                task_id=task_id
            )
            if kb_results:
                kb_context = self._format_kb_results(kb_results)

        prompt = self._build_api_gateway_prompt(
            services=services,
            routing_requirements=routing_requirements,
            auth_strategy=auth_strategy,
            kb_context=kb_context
        )

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = self._parse_gateway_design(response.text)
        result.update({
            "auth_strategy": auth_strategy,
            "service_count": len(services),
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    @A2AIntegration.with_task_tracking
    def design_event_driven_architecture(
        self,
        services: List[Dict[str, Any]],
        events: List[Dict[str, Any]],
        consistency_requirements: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Design event-driven architecture for microservices.

        Args:
            services: List of microservices
            events: List of domain events
            consistency_requirements: Consistency and ordering requirements
            task_id: Optional task ID

        Returns:
            {
                "event_flows": List[Dict],
                "event_schemas": List[Dict],
                "message_broker_config": Dict,
                "saga_definitions": List[Dict],
                "architecture_diagram": str,
                "documentation": str
            }
        """
        print(f"[Microservices Architect] Designing event-driven architecture")

        kb_context = ""
        if hasattr(self, 'should_query_kb') and self.should_query_kb({"events": len(events)}):
            kb_results = self.execute_dynamic_query(
                query_type="event_driven_patterns",
                context={"event_count": len(events)},
                task_id=task_id
            )
            if kb_results:
                kb_context = self._format_kb_results(kb_results)

        prompt = self._build_event_driven_prompt(
            services=services,
            events=events,
            consistency_requirements=consistency_requirements,
            kb_context=kb_context
        )

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = self._parse_event_architecture(response.text)
        result.update({
            "event_count": len(events),
            "service_count": len(services),
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    @A2AIntegration.with_task_tracking
    def apply_cqrs_pattern(
        self,
        domain_model: Dict[str, Any],
        read_write_ratio: float = 0.8,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Apply CQRS (Command Query Responsibility Segregation) pattern.

        Args:
            domain_model: Domain model specification
            read_write_ratio: Expected read/write ratio (0-1, higher = more reads)
            task_id: Optional task ID

        Returns:
            {
                "command_model": Dict,
                "query_model": Dict,
                "event_handlers": List[Dict],
                "projections": List[Dict],
                "implementation_guide": str
            }
        """
        print(f"[Microservices Architect] Applying CQRS pattern")

        prompt = self._build_cqrs_prompt(domain_model, read_write_ratio)
        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = self._parse_cqrs_design(response.text)
        result.update({
            "read_write_ratio": read_write_ratio,
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    @A2AIntegration.with_task_tracking
    def design_service_mesh(
        self,
        services: List[Dict[str, Any]],
        communication_patterns: Dict[str, Any],
        mesh_technology: str = "istio",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Design service mesh configuration.

        Args:
            services: List of microservices
            communication_patterns: Inter-service communication patterns
            mesh_technology: Service mesh tech (istio, linkerd)
            task_id: Optional task ID

        Returns:
            {
                "mesh_config": str,
                "traffic_policies": List[Dict],
                "security_policies": List[Dict],
                "observability_config": Dict,
                "documentation": str
            }
        """
        print(f"[Microservices Architect] Designing service mesh ({mesh_technology})")

        prompt = self._build_service_mesh_prompt(
            services=services,
            communication_patterns=communication_patterns,
            mesh_technology=mesh_technology
        )

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = self._parse_service_mesh_design(response.text)
        result.update({
            "mesh_technology": mesh_technology,
            "service_count": len(services),
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    def _build_decomposition_prompt(
        self,
        codebase_analysis: Dict[str, Any],
        business_domains: List[str],
        decomposition_strategy: str,
        kb_context: str
    ) -> str:
        """Build monolith decomposition prompt."""

        modules = codebase_analysis.get("modules", [])
        dependencies = codebase_analysis.get("dependencies", {})
        complexity_metrics = codebase_analysis.get("complexity_metrics", {})

        return f"""
You are an expert microservices architect. Analyze this monolithic application and design a microservices decomposition.

**Monolith Analysis:**
- Modules: {json.dumps(modules, indent=2)}
- Dependencies: {json.dumps(dependencies, indent=2)}
- Complexity Metrics: {json.dumps(complexity_metrics, indent=2)}

**Business Domains Identified:**
{json.dumps(business_domains, indent=2)}

**Decomposition Strategy:** {decomposition_strategy}

Requirements:
1. Apply Domain-Driven Design (DDD) principles
2. Identify bounded contexts for each service
3. Define clear service boundaries
4. Minimize inter-service coupling
5. Ensure each service has single responsibility
6. Consider data ownership and consistency
7. Plan for backward compatibility during migration
8. Identify shared libraries and cross-cutting concerns

For each microservice, provide:
- Service name and responsibility
- Bounded context definition
- API endpoints (REST/gRPC)
- Data models and ownership
- Dependencies on other services
- Technology stack recommendations

Also provide:
- Service boundary diagram (Mermaid format)
- Migration strategy (strangler fig, feature flags, etc.)
- Data migration approach
- Risk assessment
- Estimated effort

{kb_context}

Think through this systematically, considering:
1. Business domain alignment
2. Technical dependencies
3. Data consistency requirements
4. Team structure (Conway's Law)
5. Deployment independence
"""

    def _build_api_gateway_prompt(
        self,
        services: List[Dict[str, Any]],
        routing_requirements: Dict[str, Any],
        auth_strategy: str,
        kb_context: str
    ) -> str:
        """Build API gateway design prompt."""

        return f"""
Design a production-ready API Gateway for the following microservices architecture.

**Microservices:**
{json.dumps(services, indent=2)}

**Routing Requirements:**
{json.dumps(routing_requirements, indent=2)}

**Authentication Strategy:** {auth_strategy}

Requirements:
1. Design routing rules for all services
2. Implement {auth_strategy} authentication
3. Add rate limiting per client/endpoint
4. Include request/response transformation
5. Add circuit breaker pattern
6. Implement health checks and service discovery
7. Add comprehensive logging and tracing
8. Include CORS configuration
9. Design caching strategy
10. Plan for versioning (URL path or header)

Provide:
1. Gateway configuration (Kong, Nginx, AWS API Gateway, or similar)
2. Routing rules with priority
3. Middleware chain (auth, rate limit, logging, etc.)
4. Security configuration
5. Monitoring and alerting setup
6. Documentation

{kb_context}

Consider:
- Performance and latency
- Scalability and load balancing
- Security (OWASP API Security Top 10)
- Observability
- Developer experience
"""

    def _build_event_driven_prompt(
        self,
        services: List[Dict[str, Any]],
        events: List[Dict[str, Any]],
        consistency_requirements: Dict[str, Any],
        kb_context: str
    ) -> str:
        """Build event-driven architecture prompt."""

        return f"""
Design an event-driven architecture for the following microservices system.

**Microservices:**
{json.dumps(services, indent=2)}

**Domain Events:**
{json.dumps(events, indent=2)}

**Consistency Requirements:**
{json.dumps(consistency_requirements, indent=2)}

Requirements:
1. Design event flow between services
2. Define event schemas with versioning
3. Choose message broker (Kafka, RabbitMQ, Google Pub/Sub)
4. Implement Saga pattern for distributed transactions
5. Handle eventual consistency
6. Design event sourcing if applicable
7. Include dead letter queues
8. Plan for event replay and recovery
9. Design idempotency handling
10. Include event versioning strategy

For each event:
- Event name and schema
- Producer service(s)
- Consumer service(s)
- Ordering guarantees
- Retry and error handling

Provide:
1. Event flow diagrams (Mermaid format)
2. Event schema definitions (JSON Schema or Avro)
3. Message broker configuration
4. Saga orchestration/choreography design
5. Event handler implementations (pseudocode)
6. Consistency and failure scenarios
7. Monitoring and debugging strategy

{kb_context}

Consider:
- At-least-once vs exactly-once delivery
- Event ordering guarantees
- Partition strategy (for Kafka)
- Schema evolution
- Performance and throughput
"""

    def _build_cqrs_prompt(self, domain_model: Dict[str, Any], read_write_ratio: float) -> str:
        """Build CQRS pattern prompt."""

        return f"""
Apply the CQRS (Command Query Responsibility Segregation) pattern to the following domain model.

**Domain Model:**
{json.dumps(domain_model, indent=2)}

**Read/Write Ratio:** {read_write_ratio} (higher = more reads)

Requirements:
1. Separate command model (writes) from query model (reads)
2. Design command handlers for all write operations
3. Design query handlers for all read operations
4. Define events emitted by commands
5. Design projections for query model
6. Handle eventual consistency between models
7. Include event store if using event sourcing
8. Design snapshot strategy for performance
9. Include validation in command handlers
10. Optimize query model for read performance

Provide:
1. Command model structure (aggregates, entities)
2. Query model structure (read models, projections)
3. Command handlers with validation
4. Event definitions
5. Event handlers and projections
6. Synchronization strategy
7. Implementation guide with code examples
8. Performance considerations

Consider:
- Aggregate boundaries
- Event granularity
- Query optimization
- Cache strategy for reads
- Stale read handling
"""

    def _build_service_mesh_prompt(
        self,
        services: List[Dict[str, Any]],
        communication_patterns: Dict[str, Any],
        mesh_technology: str
    ) -> str:
        """Build service mesh design prompt."""

        return f"""
Design a service mesh configuration using {mesh_technology.upper()} for the following microservices.

**Services:**
{json.dumps(services, indent=2)}

**Communication Patterns:**
{json.dumps(communication_patterns, indent=2)}

Requirements:
1. Configure traffic management (routing, load balancing)
2. Implement mutual TLS (mTLS) for service-to-service communication
3. Add circuit breakers and retries
4. Configure rate limiting
5. Implement request tracing
6. Add service-level metrics
7. Configure access control policies
8. Implement fault injection for testing
9. Add traffic splitting for canary deployments
10. Configure observability (metrics, logs, traces)

Provide:
1. Service mesh configuration files
2. Traffic policies (VirtualService, DestinationRule for Istio)
3. Security policies (PeerAuthentication, AuthorizationPolicy)
4. Telemetry configuration
5. Gateway configuration
6. Deployment strategy
7. Monitoring dashboard setup

Consider:
- Performance overhead of sidecar proxies
- Resource requirements
- Complexity vs benefits
- Migration strategy
- Troubleshooting approach
"""

    def _parse_architecture_design(self, text: str) -> Dict[str, Any]:
        """Parse monolith decomposition result."""

        result = {
            "services": [],
            "service_boundaries": {},
            "migration_strategy": "",
            "architecture_diagram": "",
            "documentation": text
        }

        # Extract services from JSON or structured text
        json_matches = re.findall(r'```json\n(.*?)```', text, re.DOTALL)
        for json_str in json_matches:
            try:
                data = json.loads(json_str)
                if isinstance(data, list):
                    result["services"] = data
                elif isinstance(data, dict) and "services" in data:
                    result["services"] = data["services"]
            except:
                pass

        # Extract Mermaid diagram
        mermaid_match = re.search(r'```mermaid\n(.*?)```', text, re.DOTALL)
        if mermaid_match:
            result["architecture_diagram"] = mermaid_match.group(1).strip()

        return result

    def _parse_gateway_design(self, text: str) -> Dict[str, Any]:
        """Parse API gateway design result."""

        result = {
            "gateway_config": "",
            "routing_rules": [],
            "middleware": [],
            "security_config": {},
            "documentation": text
        }

        # Extract code blocks
        code_blocks = re.findall(r'```(\w+)?\n(.*?)```', text, re.DOTALL)
        for lang, code in code_blocks:
            lang = lang.lower() if lang else ""
            if lang in ["yaml", "yml", "nginx", "kong"]:
                result["gateway_config"] += code.strip() + "\n\n"
            elif lang == "json":
                try:
                    data = json.loads(code)
                    if "routing" in str(data).lower():
                        result["routing_rules"].append(data)
                except:
                    pass

        return result

    def _parse_event_architecture(self, text: str) -> Dict[str, Any]:
        """Parse event-driven architecture result."""

        result = {
            "event_flows": [],
            "event_schemas": [],
            "message_broker_config": {},
            "saga_definitions": [],
            "architecture_diagram": "",
            "documentation": text
        }

        # Extract diagrams
        mermaid_match = re.search(r'```mermaid\n(.*?)```', text, re.DOTALL)
        if mermaid_match:
            result["architecture_diagram"] = mermaid_match.group(1).strip()

        # Extract JSON schemas
        json_matches = re.findall(r'```json\n(.*?)```', text, re.DOTALL)
        for json_str in json_matches:
            try:
                data = json.loads(json_str)
                if "event" in str(data).lower() or "schema" in str(data).lower():
                    result["event_schemas"].append(data)
            except:
                pass

        return result

    def _parse_cqrs_design(self, text: str) -> Dict[str, Any]:
        """Parse CQRS design result."""

        result = {
            "command_model": {},
            "query_model": {},
            "event_handlers": [],
            "projections": [],
            "implementation_guide": text
        }

        # Extract structured data
        json_matches = re.findall(r'```json\n(.*?)```', text, re.DOTALL)
        for json_str in json_matches:
            try:
                data = json.loads(json_str)
                if "command" in str(data).lower():
                    result["command_model"] = data
                elif "query" in str(data).lower() or "projection" in str(data).lower():
                    result["query_model"] = data
            except:
                pass

        return result

    def _parse_service_mesh_design(self, text: str) -> Dict[str, Any]:
        """Parse service mesh design result."""

        result = {
            "mesh_config": "",
            "traffic_policies": [],
            "security_policies": [],
            "observability_config": {},
            "documentation": text
        }

        # Extract YAML configuration
        yaml_blocks = re.findall(r'```yaml\n(.*?)```', text, re.DOTALL)
        for yaml_code in yaml_blocks:
            result["mesh_config"] += yaml_code.strip() + "\n---\n"

        return result

    def _get_generation_config(self) -> Dict[str, Any]:
        """Get generation config for reasoning model."""
        return {
            "temperature": 0.3,  # Slightly higher for creative architecture solutions
            "max_output_tokens": 8192,
            "top_p": 0.95,
            "top_k": 40
        }

    def _format_kb_results(self, results: List[Dict]) -> str:
        """Format KB query results."""
        if not results:
            return ""
        formatted = "\n\nRelevant architecture patterns from knowledge base:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result.get('content', '')}\n\n"
        return formatted


# Standalone tool functions

def decompose_monolith(
    codebase_analysis: Dict[str, Any],
    business_domains: List[str],
    decomposition_strategy: str = "domain_driven"
) -> Dict[str, Any]:
    """Standalone function for monolith decomposition."""
    agent = MicroservicesArchitectAgent(context={}, message_bus=None, orchestrator_id="")
    return agent.decompose_monolith(codebase_analysis, business_domains, decomposition_strategy)


def design_api_gateway(
    services: List[Dict[str, Any]],
    routing_requirements: Dict[str, Any],
    auth_strategy: str = "jwt"
) -> Dict[str, Any]:
    """Standalone function for API gateway design."""
    agent = MicroservicesArchitectAgent(context={}, message_bus=None, orchestrator_id="")
    return agent.design_api_gateway(services, routing_requirements, auth_strategy)


def design_event_driven_architecture(
    services: List[Dict[str, Any]],
    events: List[Dict[str, Any]],
    consistency_requirements: Dict[str, Any]
) -> Dict[str, Any]:
    """Standalone function for event-driven architecture design."""
    agent = MicroservicesArchitectAgent(context={}, message_bus=None, orchestrator_id="")
    return agent.design_event_driven_architecture(services, events, consistency_requirements)
