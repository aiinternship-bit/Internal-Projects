"""
agents/backend/message_queue/agent.py

Message Queue Agent - Sets up message brokers and designs event schemas.

Supports Kafka, RabbitMQ, Google Pub/Sub, Amazon SQS/SNS with event schema
design using Avro, Protobuf, and JSON Schema.
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


class MessageQueueAgent(A2AEnabledAgent, DynamicKnowledgeBaseIntegration):
    """
    Message Queue Agent for messaging infrastructure and event schema design.

    Capabilities:
    - Kafka cluster setup and configuration
    - RabbitMQ setup with exchanges and queues
    - Google Cloud Pub/Sub configuration
    - Event schema design (Avro, Protobuf, JSON Schema)
    - Producer/Consumer implementation
    - Schema registry setup
    - Message versioning and compatibility
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        vector_db_client=None,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize Message Queue Agent."""
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
        self.config_history: List[Dict[str, Any]] = []

    def handle_task_assignment(self, message: Dict[str, Any]) -> None:
        """Handle TASK_ASSIGNMENT message from orchestrator."""
        payload = message.get("payload", {})
        task_id = payload.get("task_id")
        task_type = payload.get("task_type")
        parameters = payload.get("parameters", {})

        try:
            if task_type == "setup_kafka_cluster":
                result = self.setup_kafka_cluster(task_id=task_id, **parameters)
            elif task_type == "setup_rabbitmq":
                result = self.setup_rabbitmq(task_id=task_id, **parameters)
            elif task_type == "setup_pubsub":
                result = self.setup_pubsub(task_id=task_id, **parameters)
            elif task_type == "design_event_schema":
                result = self.design_event_schema(task_id=task_id, **parameters)
            elif task_type == "implement_producer_consumer":
                result = self.implement_producer_consumer(task_id=task_id, **parameters)
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
                error_type="MESSAGE_QUEUE_SETUP_FAILED",
                error_message=str(e),
                stack_trace=""
            )

    @A2AIntegration.with_task_tracking
    def setup_kafka_cluster(
        self,
        broker_count: int,
        topics: List[Dict[str, Any]],
        partitions: int = 3,
        replication_factor: int = 2,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Setup Apache Kafka cluster configuration.

        Args:
            broker_count: Number of broker nodes
            topics: List of topic specifications
            partitions: Default partition count
            replication_factor: Replication factor
            task_id: Optional task ID

        Returns:
            {
                "broker_config": str,
                "topic_configs": List[Dict],
                "producer_config": Dict,
                "consumer_config": Dict,
                "monitoring_setup": str,
                "documentation": str
            }
        """
        start_time = datetime.utcnow()
        print(f"[Message Queue] Setting up Kafka cluster with {broker_count} brokers, {len(topics)} topics")

        # Query KB for Kafka patterns
        kb_context = ""
        if hasattr(self, 'should_query_kb') and self.should_query_kb({"topics": len(topics)}):
            kb_results = self.execute_dynamic_query(
                query_type="kafka_patterns",
                context={"topic_count": len(topics), "brokers": broker_count},
                task_id=task_id
            )
            if kb_results:
                kb_context = self._format_kb_results(kb_results)

        # Build prompt
        prompt = self._build_kafka_setup_prompt(
            broker_count=broker_count,
            topics=topics,
            partitions=partitions,
            replication_factor=replication_factor,
            kb_context=kb_context
        )

        # Generate with LLM
        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        # Parse result
        result = self._parse_kafka_setup(response.text)

        # Add metadata
        duration = (datetime.utcnow() - start_time).total_seconds() / 60
        result.update({
            "broker_count": broker_count,
            "topic_count": len(topics),
            "partitions": partitions,
            "replication_factor": replication_factor,
            "duration_minutes": duration,
            "timestamp": datetime.utcnow().isoformat()
        })

        self.config_history.append({
            "task_id": task_id,
            "broker_type": "kafka",
            "topic_count": len(topics),
            "timestamp": result["timestamp"]
        })

        return result

    @A2AIntegration.with_task_tracking
    def setup_rabbitmq(
        self,
        exchanges: List[Dict[str, Any]],
        queues: List[Dict[str, Any]],
        bindings: List[Dict[str, Any]],
        policies: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Setup RabbitMQ configuration.

        Args:
            exchanges: Exchange definitions
            queues: Queue definitions
            bindings: Exchange-queue bindings
            policies: RabbitMQ policies (HA, TTL, etc.)
            task_id: Optional task ID

        Returns:
            {
                "definitions": str,
                "producer_code": str,
                "consumer_code": str,
                "configuration": Dict,
                "documentation": str
            }
        """
        print(f"[Message Queue] Setting up RabbitMQ: {len(exchanges)} exchanges, {len(queues)} queues")

        kb_context = ""
        if hasattr(self, 'should_query_kb') and self.should_query_kb({"queues": len(queues)}):
            kb_results = self.execute_dynamic_query(
                query_type="rabbitmq_patterns",
                context={"queue_count": len(queues)},
                task_id=task_id
            )
            if kb_results:
                kb_context = self._format_kb_results(kb_results)

        prompt = self._build_rabbitmq_setup_prompt(
            exchanges=exchanges,
            queues=queues,
            bindings=bindings,
            policies=policies or {},
            kb_context=kb_context
        )

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = self._parse_rabbitmq_setup(response.text)
        result.update({
            "exchange_count": len(exchanges),
            "queue_count": len(queues),
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    @A2AIntegration.with_task_tracking
    def setup_pubsub(
        self,
        topics: List[Dict[str, Any]],
        subscriptions: List[Dict[str, Any]],
        filters: Optional[List[Dict[str, Any]]] = None,
        dead_letter_config: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Setup Google Cloud Pub/Sub configuration.

        Args:
            topics: Topic definitions
            subscriptions: Subscription definitions
            filters: Message filters
            dead_letter_config: Dead letter queue configuration
            task_id: Optional task ID

        Returns:
            {
                "terraform_config": str,
                "publisher_code": str,
                "subscriber_code": str,
                "iam_policies": Dict,
                "documentation": str
            }
        """
        print(f"[Message Queue] Setting up Pub/Sub: {len(topics)} topics, {len(subscriptions)} subscriptions")

        prompt = self._build_pubsub_setup_prompt(
            topics=topics,
            subscriptions=subscriptions,
            filters=filters or [],
            dead_letter_config=dead_letter_config or {}
        )

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = self._parse_pubsub_setup(response.text)
        result.update({
            "topic_count": len(topics),
            "subscription_count": len(subscriptions),
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    @A2AIntegration.with_task_tracking
    def design_event_schema(
        self,
        event_type: str,
        payload_fields: List[Dict[str, Any]],
        schema_format: str = "avro",
        versioning_strategy: str = "backward_compatible",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Design event schema with versioning.

        Args:
            event_type: Type of event
            payload_fields: Field definitions
            schema_format: Schema format (avro, protobuf, json_schema)
            versioning_strategy: Versioning strategy
            task_id: Optional task ID

        Returns:
            {
                "schema": str,
                "schema_registry_config": Dict,
                "compatibility_rules": Dict,
                "examples": List[Dict],
                "documentation": str
            }
        """
        print(f"[Message Queue] Designing {schema_format} schema for {event_type}")

        prompt = self._build_schema_design_prompt(
            event_type=event_type,
            payload_fields=payload_fields,
            schema_format=schema_format,
            versioning_strategy=versioning_strategy
        )

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = self._parse_schema_design(response.text, schema_format)
        result.update({
            "event_type": event_type,
            "schema_format": schema_format,
            "versioning_strategy": versioning_strategy,
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    @A2AIntegration.with_task_tracking
    def implement_producer_consumer(
        self,
        language: str,
        broker_type: str,
        events: List[str],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Implement producer and consumer code.

        Args:
            language: Programming language (python, typescript, go, java)
            broker_type: Message broker (kafka, rabbitmq, pubsub)
            events: List of event types to handle
            task_id: Optional task ID

        Returns:
            {
                "producer_code": str,
                "consumer_code": str,
                "configuration": Dict,
                "error_handling": str,
                "tests": str,
                "documentation": str
            }
        """
        print(f"[Message Queue] Implementing {broker_type} producer/consumer in {language}")

        prompt = self._build_producer_consumer_prompt(
            language=language,
            broker_type=broker_type,
            events=events
        )

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = self._parse_producer_consumer(response.text, language)
        result.update({
            "language": language,
            "broker_type": broker_type,
            "event_count": len(events),
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    def _build_kafka_setup_prompt(
        self,
        broker_count: int,
        topics: List[Dict[str, Any]],
        partitions: int,
        replication_factor: int,
        kb_context: str
    ) -> str:
        """Build Kafka setup prompt."""

        return f"""
Generate production-ready Apache Kafka cluster configuration.

**Cluster Specifications:**
- Broker Count: {broker_count}
- Default Partitions: {partitions}
- Replication Factor: {replication_factor}

**Topics:**
{json.dumps(topics, indent=2)}

Requirements:
1. Generate broker configuration (server.properties)
2. Create topic configurations with appropriate settings
3. Configure producer settings (idempotence, compression, batching)
4. Configure consumer settings (group management, offset management)
5. Setup Zookeeper configuration (or KRaft if Kafka 3.0+)
6. Add monitoring with JMX metrics
7. Configure security (SSL/TLS, SASL)
8. Setup log retention and cleanup policies
9. Configure rack awareness for HA
10. Add health checks and monitoring

Provide:
1. Complete broker configuration files
2. Topic creation scripts
3. Producer configuration (Java properties / Python dict)
4. Consumer configuration
5. Monitoring setup (Prometheus exporters)
6. Security configuration
7. Deployment guide (Docker Compose or Kubernetes)
8. Documentation

{kb_context}

Best practices:
- Enable idempotent producers
- Use appropriate compression (lz4, snappy)
- Configure appropriate retention
- Enable rack awareness
- Setup monitoring and alerting
"""

    def _build_rabbitmq_setup_prompt(
        self,
        exchanges: List[Dict[str, Any]],
        queues: List[Dict[str, Any]],
        bindings: List[Dict[str, Any]],
        policies: Dict[str, Any],
        kb_context: str
    ) -> str:
        """Build RabbitMQ setup prompt."""

        return f"""
Generate production-ready RabbitMQ configuration.

**Exchanges:**
{json.dumps(exchanges, indent=2)}

**Queues:**
{json.dumps(queues, indent=2)}

**Bindings:**
{json.dumps(bindings, indent=2)}

**Policies:**
{json.dumps(policies, indent=2)}

Requirements:
1. Generate RabbitMQ definitions file (JSON)
2. Create exchange configurations (direct, topic, fanout, headers)
3. Create queue configurations (durable, TTL, max-length)
4. Define bindings with routing keys
5. Setup HA policies (mirroring, quorum queues)
6. Configure dead letter exchanges
7. Setup monitoring (management plugin)
8. Configure security (users, permissions, vhosts)
9. Add message TTL and queue length limits
10. Setup federation/shovel if needed

Provide:
1. RabbitMQ definitions.json
2. Producer implementation (Python/Node.js)
3. Consumer implementation with error handling
4. Configuration files
5. Monitoring setup
6. Security configuration
7. Deployment guide
8. Documentation

{kb_context}

Best practices:
- Use quorum queues for HA
- Enable publisher confirms
- Use appropriate acknowledgment modes
- Configure proper prefetch counts
- Setup monitoring and alerting
"""

    def _build_pubsub_setup_prompt(
        self,
        topics: List[Dict[str, Any]],
        subscriptions: List[Dict[str, Any]],
        filters: List[Dict[str, Any]],
        dead_letter_config: Dict[str, Any]
    ) -> str:
        """Build Pub/Sub setup prompt."""

        return f"""
Generate Google Cloud Pub/Sub configuration.

**Topics:**
{json.dumps(topics, indent=2)}

**Subscriptions:**
{json.dumps(subscriptions, indent=2)}

**Filters:**
{json.dumps(filters, indent=2)}

**Dead Letter Configuration:**
{json.dumps(dead_letter_config, indent=2)}

Requirements:
1. Generate Terraform configuration for all resources
2. Create topic configurations with message retention
3. Create subscription configurations (push/pull, ack deadline)
4. Setup message filters for subscriptions
5. Configure dead letter topics
6. Setup IAM policies for publishers/subscribers
7. Configure monitoring and alerting
8. Add retry policies
9. Setup message ordering if needed
10. Configure encryption

Provide:
1. Terraform configuration files
2. Publisher code (Python)
3. Subscriber code (pull and push)
4. IAM policy definitions
5. Monitoring dashboard setup
6. Error handling implementation
7. Deployment guide
8. Documentation

Best practices:
- Enable message ordering when needed
- Use appropriate ack deadlines
- Configure exponential backoff
- Setup dead letter topics
- Monitor subscription backlog
"""

    def _build_schema_design_prompt(
        self,
        event_type: str,
        payload_fields: List[Dict[str, Any]],
        schema_format: str,
        versioning_strategy: str
    ) -> str:
        """Build schema design prompt."""

        format_examples = {
            "avro": """
Example Avro schema:
{
  "type": "record",
  "name": "EventName",
  "namespace": "com.example.events",
  "fields": [...]
}
""",
            "protobuf": """
Example Protobuf schema:
syntax = "proto3";
message EventName {
  string field1 = 1;
  int32 field2 = 2;
}
""",
            "json_schema": """
Example JSON Schema:
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {...}
}
"""
        }

        return f"""
Design an event schema using {schema_format.upper()}.

**Event Type:** {event_type}

**Payload Fields:**
{json.dumps(payload_fields, indent=2)}

**Versioning Strategy:** {versioning_strategy}

{format_examples.get(schema_format, "")}

Requirements:
1. Design complete schema in {schema_format} format
2. Include proper versioning (version field)
3. Add documentation/descriptions for all fields
4. Define required vs optional fields
5. Add appropriate data type constraints
6. Include enums for fixed value sets
7. Add default values where appropriate
8. Design for {versioning_strategy} compatibility
9. Include metadata fields (timestamp, trace_id, etc.)
10. Provide schema evolution guidelines

Provide:
1. Complete schema definition
2. Schema registry configuration
3. Compatibility rules
4. Example messages
5. Validation code
6. Evolution guide
7. Documentation

Schema evolution rules:
- {versioning_strategy}: Explain constraints
- Version numbering: Semantic versioning
- Deprecated fields: How to handle
"""

    def _build_producer_consumer_prompt(
        self,
        language: str,
        broker_type: str,
        events: List[str]
    ) -> str:
        """Build producer/consumer implementation prompt."""

        return f"""
Implement producer and consumer for {broker_type.upper()} in {language.upper()}.

**Events to Handle:**
{json.dumps(events, indent=2)}

**Message Broker:** {broker_type}
**Language:** {language}

Requirements:
1. Implement producer with proper error handling
2. Implement consumer with message processing
3. Add idempotency handling (deduplication)
4. Implement retry logic with exponential backoff
5. Add circuit breaker for fault tolerance
6. Include structured logging
7. Add metrics and monitoring
8. Implement graceful shutdown
9. Handle schema evolution
10. Add comprehensive tests

For Producer:
- Connection management
- Message serialization
- Batching and compression
- Error handling and retries
- Monitoring and metrics

For Consumer:
- Connection management
- Message deserialization
- Processing and acknowledgment
- Error handling (retry, DLQ)
- Offset/acknowledgment management
- Graceful shutdown

Provide:
1. Producer implementation
2. Consumer implementation
3. Configuration management
4. Error handling utilities
5. Unit tests
6. Integration tests
7. Documentation

Best practices for {broker_type}:
- Include broker-specific optimizations
- Handle connection failures
- Implement proper backpressure
- Use connection pooling
"""

    def _parse_kafka_setup(self, text: str) -> Dict[str, Any]:
        """Parse Kafka setup result."""

        result = {
            "broker_config": "",
            "topic_configs": [],
            "producer_config": {},
            "consumer_config": {},
            "monitoring_setup": "",
            "documentation": text
        }

        # Extract configuration blocks
        code_blocks = re.findall(r'```(?:properties|conf|yaml)\n(.*?)```', text, re.DOTALL)
        if code_blocks:
            result["broker_config"] = code_blocks[0].strip()

        # Extract JSON configs
        json_blocks = re.findall(r'```json\n(.*?)```', text, re.DOTALL)
        for json_str in json_blocks:
            try:
                data = json.loads(json_str)
                if "producer" in str(data).lower():
                    result["producer_config"] = data
                elif "consumer" in str(data).lower():
                    result["consumer_config"] = data
            except:
                pass

        return result

    def _parse_rabbitmq_setup(self, text: str) -> Dict[str, Any]:
        """Parse RabbitMQ setup result."""

        result = {
            "definitions": "",
            "producer_code": "",
            "consumer_code": "",
            "configuration": {},
            "documentation": text
        }

        # Extract JSON definitions
        json_blocks = re.findall(r'```json\n(.*?)```', text, re.DOTALL)
        if json_blocks:
            result["definitions"] = json_blocks[0].strip()

        # Extract Python code
        python_blocks = re.findall(r'```python\n(.*?)```', text, re.DOTALL)
        if len(python_blocks) >= 2:
            result["producer_code"] = python_blocks[0].strip()
            result["consumer_code"] = python_blocks[1].strip()

        return result

    def _parse_pubsub_setup(self, text: str) -> Dict[str, Any]:
        """Parse Pub/Sub setup result."""

        result = {
            "terraform_config": "",
            "publisher_code": "",
            "subscriber_code": "",
            "iam_policies": {},
            "documentation": text
        }

        # Extract Terraform
        tf_blocks = re.findall(r'```(?:terraform|hcl)\n(.*?)```', text, re.DOTALL)
        if tf_blocks:
            result["terraform_config"] = "\n\n".join(tf_blocks)

        # Extract Python code
        python_blocks = re.findall(r'```python\n(.*?)```', text, re.DOTALL)
        if len(python_blocks) >= 2:
            result["publisher_code"] = python_blocks[0].strip()
            result["subscriber_code"] = python_blocks[1].strip()

        return result

    def _parse_schema_design(self, text: str, schema_format: str) -> Dict[str, Any]:
        """Parse schema design result."""

        result = {
            "schema": "",
            "schema_registry_config": {},
            "compatibility_rules": {},
            "examples": [],
            "documentation": text
        }

        if schema_format == "avro":
            json_blocks = re.findall(r'```json\n(.*?)```', text, re.DOTALL)
            if json_blocks:
                result["schema"] = json_blocks[0].strip()
        elif schema_format == "protobuf":
            proto_blocks = re.findall(r'```proto(?:buf)?\n(.*?)```', text, re.DOTALL)
            if proto_blocks:
                result["schema"] = proto_blocks[0].strip()
        elif schema_format == "json_schema":
            json_blocks = re.findall(r'```json\n(.*?)```', text, re.DOTALL)
            if json_blocks:
                result["schema"] = json_blocks[0].strip()

        return result

    def _parse_producer_consumer(self, text: str, language: str) -> Dict[str, Any]:
        """Parse producer/consumer implementation."""

        result = {
            "producer_code": "",
            "consumer_code": "",
            "configuration": {},
            "error_handling": "",
            "tests": "",
            "documentation": text
        }

        # Extract code blocks
        lang_pattern = language if language != "typescript" else "(?:typescript|ts|javascript|js)"
        code_blocks = re.findall(rf'```{lang_pattern}\n(.*?)```', text, re.DOTALL | re.IGNORECASE)

        if len(code_blocks) >= 2:
            result["producer_code"] = code_blocks[0].strip()
            result["consumer_code"] = code_blocks[1].strip()
        elif len(code_blocks) == 1:
            result["producer_code"] = code_blocks[0].strip()

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
        formatted = "\n\nRelevant messaging patterns from knowledge base:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result.get('content', '')}\n\n"
        return formatted


# Standalone tool functions

def setup_kafka_cluster(
    broker_count: int,
    topics: List[Dict[str, Any]],
    partitions: int = 3,
    replication_factor: int = 2
) -> Dict[str, Any]:
    """Standalone function for Kafka setup."""
    agent = MessageQueueAgent(context={}, message_bus=None, orchestrator_id="")
    return agent.setup_kafka_cluster(broker_count, topics, partitions, replication_factor)


def setup_rabbitmq(
    exchanges: List[Dict[str, Any]],
    queues: List[Dict[str, Any]],
    bindings: List[Dict[str, Any]],
    policies: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Standalone function for RabbitMQ setup."""
    agent = MessageQueueAgent(context={}, message_bus=None, orchestrator_id="")
    return agent.setup_rabbitmq(exchanges, queues, bindings, policies)


def design_event_schema(
    event_type: str,
    payload_fields: List[Dict[str, Any]],
    schema_format: str = "avro",
    versioning_strategy: str = "backward_compatible"
) -> Dict[str, Any]:
    """Standalone function for event schema design."""
    agent = MessageQueueAgent(context={}, message_bus=None, orchestrator_id="")
    return agent.design_event_schema(event_type, payload_fields, schema_format, versioning_strategy)
