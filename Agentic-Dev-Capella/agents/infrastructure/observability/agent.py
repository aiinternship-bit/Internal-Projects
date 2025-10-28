"""
agents/infrastructure/observability/agent.py

Observability Agent - Sets up monitoring, alerting, and distributed tracing.

Supports Prometheus, Grafana, Jaeger, Google Cloud Monitoring, and OpenTelemetry
for comprehensive observability solutions.
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


class ObservabilityAgent(A2AEnabledAgent, DynamicKnowledgeBaseIntegration):
    """
    Observability Agent for monitoring and tracing infrastructure.

    Capabilities:
    - Prometheus configuration and alert rules
    - Grafana dashboard generation
    - Distributed tracing setup (Jaeger, Cloud Trace)
    - Cloud Monitoring alert policies
    - SLO/SLI definitions
    - Log aggregation setup
    - OpenTelemetry instrumentation
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        vector_db_client=None,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize Observability Agent."""
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
        self.observability_history: List[Dict[str, Any]] = []

    def handle_task_assignment(self, message: Dict[str, Any]) -> None:
        """Handle TASK_ASSIGNMENT message from orchestrator."""
        payload = message.get("payload", {})
        task_id = payload.get("task_id")
        task_type = payload.get("task_type")
        parameters = payload.get("parameters", {})

        try:
            if task_type == "generate_prometheus_config":
                result = self.generate_prometheus_config(task_id=task_id, **parameters)
            elif task_type == "generate_grafana_dashboard":
                result = self.generate_grafana_dashboard(task_id=task_id, **parameters)
            elif task_type == "generate_tracing_config":
                result = self.generate_tracing_config(task_id=task_id, **parameters)
            elif task_type == "generate_cloud_monitoring_alerts":
                result = self.generate_cloud_monitoring_alerts(task_id=task_id, **parameters)
            elif task_type == "define_slo_sli":
                result = self.define_slo_sli(task_id=task_id, **parameters)
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
                error_type="OBSERVABILITY_SETUP_FAILED",
                error_message=str(e),
                stack_trace=""
            )

    @A2AIntegration.with_task_tracking
    def generate_prometheus_config(
        self,
        scrape_targets: List[Dict[str, Any]],
        alert_rules: List[Dict[str, Any]],
        recording_rules: Optional[List[Dict]] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate Prometheus configuration.

        Args:
            scrape_targets: Scrape target configurations
            alert_rules: Alert rule definitions
            recording_rules: Recording rule definitions
            task_id: Optional task ID

        Returns:
            {
                "prometheus_yml": str,
                "alert_rules_yml": str,
                "recording_rules_yml": str,
                "service_discovery": str,
                "documentation": str
            }
        """
        start_time = datetime.utcnow()
        print(f"[Observability] Generating Prometheus config with {len(scrape_targets)} targets")

        # Query KB for Prometheus patterns
        kb_context = ""
        if hasattr(self, 'should_query_kb') and self.should_query_kb({"targets": len(scrape_targets)}):
            kb_results = self.execute_dynamic_query(
                query_type="prometheus_patterns",
                context={"target_count": len(scrape_targets)},
                task_id=task_id
            )
            if kb_results:
                kb_context = self._format_kb_results(kb_results)

        # Build prompt
        prompt = self._build_prometheus_config_prompt(
            scrape_targets=scrape_targets,
            alert_rules=alert_rules,
            recording_rules=recording_rules or [],
            kb_context=kb_context
        )

        # Generate with LLM
        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        # Parse result
        result = self._parse_prometheus_config(response.text)

        # Add metadata
        duration = (datetime.utcnow() - start_time).total_seconds() / 60
        result.update({
            "target_count": len(scrape_targets),
            "alert_count": len(alert_rules),
            "duration_minutes": duration,
            "timestamp": datetime.utcnow().isoformat()
        })

        self.observability_history.append({
            "task_id": task_id,
            "operation": "prometheus_config",
            "target_count": len(scrape_targets),
            "timestamp": result["timestamp"]
        })

        return result

    @A2AIntegration.with_task_tracking
    def generate_grafana_dashboard(
        self,
        metrics: List[str],
        panels: List[Dict[str, Any]],
        layout: Optional[Dict[str, Any]] = None,
        variables: Optional[List[Dict]] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate Grafana dashboard JSON.

        Args:
            metrics: List of metrics to visualize
            panels: Panel configurations
            layout: Dashboard layout configuration
            variables: Dashboard variables for filtering
            task_id: Optional task ID

        Returns:
            {
                "dashboard_json": str,
                "provisioning_yaml": str,
                "documentation": str
            }
        """
        print(f"[Observability] Generating Grafana dashboard with {len(panels)} panels")

        kb_context = ""
        if hasattr(self, 'should_query_kb') and self.should_query_kb({"panels": len(panels)}):
            kb_results = self.execute_dynamic_query(
                query_type="grafana_patterns",
                context={"panel_count": len(panels)},
                task_id=task_id
            )
            if kb_results:
                kb_context = self._format_kb_results(kb_results)

        prompt = self._build_grafana_dashboard_prompt(
            metrics=metrics,
            panels=panels,
            layout=layout or {},
            variables=variables or [],
            kb_context=kb_context
        )

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = self._parse_grafana_dashboard(response.text)
        result.update({
            "panel_count": len(panels),
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    @A2AIntegration.with_task_tracking
    def generate_tracing_config(
        self,
        tracing_backend: str,
        sampling_rate: float = 0.1,
        exporters: Optional[List[str]] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate distributed tracing configuration.

        Args:
            tracing_backend: Backend (jaeger, cloud_trace, zipkin)
            sampling_rate: Sampling rate (0.0-1.0)
            exporters: List of exporters to configure
            task_id: Optional task ID

        Returns:
            {
                "collector_config": str,
                "instrumentation_code": str,
                "deployment_manifests": str,
                "documentation": str
            }
        """
        print(f"[Observability] Generating {tracing_backend} tracing config")

        prompt = self._build_tracing_config_prompt(
            tracing_backend=tracing_backend,
            sampling_rate=sampling_rate,
            exporters=exporters or ["otlp"]
        )

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = self._parse_tracing_config(response.text)
        result.update({
            "backend": tracing_backend,
            "sampling_rate": sampling_rate,
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    @A2AIntegration.with_task_tracking
    def generate_cloud_monitoring_alerts(
        self,
        metrics: List[Dict[str, Any]],
        conditions: List[Dict[str, Any]],
        notification_channels: List[str],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate Google Cloud Monitoring alert policies.

        Args:
            metrics: Metrics to monitor
            conditions: Alert conditions
            notification_channels: Notification channel IDs
            task_id: Optional task ID

        Returns:
            {
                "alert_policies": List[Dict],
                "terraform_config": str,
                "notification_setup": str,
                "documentation": str
            }
        """
        print(f"[Observability] Generating Cloud Monitoring alerts")

        prompt = self._build_cloud_monitoring_prompt(
            metrics=metrics,
            conditions=conditions,
            notification_channels=notification_channels
        )

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = self._parse_cloud_monitoring(response.text)
        result.update({
            "metric_count": len(metrics),
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    @A2AIntegration.with_task_tracking
    def define_slo_sli(
        self,
        service_name: str,
        availability_target: float,
        latency_target: Dict[str, float],
        error_budget: Optional[float] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Define SLO (Service Level Objectives) and SLI (Service Level Indicators).

        Args:
            service_name: Name of service
            availability_target: Availability target (e.g., 0.999 for 99.9%)
            latency_target: Latency targets (e.g., {"p95": 200, "p99": 500})
            error_budget: Error budget (optional)
            task_id: Optional task ID

        Returns:
            {
                "slo_config": Dict,
                "sli_definitions": List[Dict],
                "monitoring_queries": List[str],
                "error_budget_policy": Dict,
                "documentation": str
            }
        """
        print(f"[Observability] Defining SLO/SLI for {service_name}")

        prompt = self._build_slo_sli_prompt(
            service_name=service_name,
            availability_target=availability_target,
            latency_target=latency_target,
            error_budget=error_budget or (1.0 - availability_target)
        )

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = self._parse_slo_sli(response.text)
        result.update({
            "service_name": service_name,
            "availability_target": availability_target,
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    def _build_prometheus_config_prompt(
        self,
        scrape_targets: List[Dict[str, Any]],
        alert_rules: List[Dict[str, Any]],
        recording_rules: List[Dict],
        kb_context: str
    ) -> str:
        """Build Prometheus configuration prompt."""

        return f"""
Generate production-ready Prometheus configuration.

**Scrape Targets:**
{json.dumps(scrape_targets, indent=2)}

**Alert Rules:**
{json.dumps(alert_rules, indent=2)}

**Recording Rules:**
{json.dumps(recording_rules, indent=2)}

Requirements:
1. Create prometheus.yml with global config and scrape configs
2. Generate alert rules (alerts.yml) with proper expressions
3. Generate recording rules for pre-computed metrics
4. Configure service discovery (Kubernetes, Consul, etc.)
5. Add relabeling rules for metric management
6. Configure remote write for long-term storage
7. Add security (TLS, authentication)
8. Configure retention and storage
9. Add proper labels for multi-tenancy
10. Include documentation

prometheus.yml should include:
- Global configuration (scrape_interval, evaluation_interval)
- Alertmanager configuration
- Scrape configs for each target type
- Remote write configuration
- Storage configuration

Alert rules should include:
- Proper PromQL expressions
- Alert severity labels
- Meaningful descriptions
- Runbook URLs
- Proper grouping

Provide:
1. prometheus.yml
2. alerts.yml with all alert rules
3. recording-rules.yml
4. Service discovery configuration
5. Alertmanager configuration
6. Deployment manifests (Docker Compose or K8s)
7. Documentation

{kb_context}

Follow Prometheus best practices:
- Use recording rules for expensive queries
- Add proper labels for routing
- Set appropriate evaluation intervals
- Configure retention policies
"""

    def _build_grafana_dashboard_prompt(
        self,
        metrics: List[str],
        panels: List[Dict[str, Any]],
        layout: Dict[str, Any],
        variables: List[Dict],
        kb_context: str
    ) -> str:
        """Build Grafana dashboard prompt."""

        return f"""
Generate Grafana dashboard JSON.

**Metrics to Visualize:**
{json.dumps(metrics, indent=2)}

**Panel Configurations:**
{json.dumps(panels, indent=2)}

**Dashboard Variables:**
{json.dumps(variables, indent=2)}

**Layout:**
{json.dumps(layout, indent=2)}

Requirements:
1. Create complete Grafana dashboard JSON
2. Include all panels with proper queries
3. Add dashboard variables for filtering
4. Configure time ranges and refresh intervals
5. Add annotations for events
6. Include template variables
7. Configure alerting on panels
8. Add links to related dashboards
9. Use proper panel types (graph, stat, table, heatmap)
10. Add documentation panel

Dashboard structure:
- Title and description
- Tags for organization
- Time range selector
- Template variables
- Rows and panels
- Panel configurations (queries, thresholds, legends)

Panel types to include:
- Time series graphs
- Stat panels for key metrics
- Table panels for detailed data
- Heatmaps for latency distribution
- Gauge panels for percentage metrics

Provide:
1. Complete dashboard JSON
2. Provisioning YAML for auto-import
3. Variable configuration guide
4. Query examples for each panel
5. Alert configuration
6. Documentation

{kb_context}

Follow Grafana best practices:
- Use consistent naming
- Add proper legends
- Set meaningful thresholds
- Use template variables
- Add drill-down links
"""

    def _build_tracing_config_prompt(
        self,
        tracing_backend: str,
        sampling_rate: float,
        exporters: List[str]
    ) -> str:
        """Build tracing configuration prompt."""

        backend_configs = {
            "jaeger": "Jaeger - distributed tracing system",
            "cloud_trace": "Google Cloud Trace",
            "zipkin": "Zipkin - distributed tracing",
            "tempo": "Grafana Tempo"
        }

        return f"""
Generate distributed tracing configuration using OpenTelemetry.

**Tracing Backend:** {backend_configs.get(tracing_backend, tracing_backend)}
**Sampling Rate:** {sampling_rate} ({sampling_rate * 100}%)
**Exporters:** {", ".join(exporters)}

Requirements:
1. Generate OpenTelemetry Collector configuration
2. Create instrumentation code for applications (Python, Node.js, Go)
3. Configure sampling strategy
4. Setup exporters to {tracing_backend}
5. Configure trace context propagation
6. Add resource attributes for service identification
7. Configure batch processing
8. Setup deployment manifests
9. Add monitoring for the collector itself
10. Include documentation

Collector Configuration should include:
- Receivers (OTLP, Jaeger, Zipkin)
- Processors (batch, resource, sampling)
- Exporters ({tracing_backend})
- Service pipelines

Instrumentation should include:
- Auto-instrumentation setup
- Manual span creation examples
- Context propagation
- Attribute configuration
- Error handling

Provide:
1. OpenTelemetry Collector config (YAML)
2. Instrumentation code examples (Python, Node.js, Go)
3. Kubernetes deployment manifests
4. Sampling configuration
5. Backend-specific setup ({tracing_backend})
6. Query examples for traces
7. Troubleshooting guide
8. Documentation

Best practices:
- Use tail-based sampling for important traces
- Add semantic conventions
- Configure proper resource attributes
- Monitor collector performance
- Setup proper retention
"""

    def _build_cloud_monitoring_prompt(
        self,
        metrics: List[Dict[str, Any]],
        conditions: List[Dict[str, Any]],
        notification_channels: List[str]
    ) -> str:
        """Build Cloud Monitoring alert prompt."""

        return f"""
Generate Google Cloud Monitoring alert policies.

**Metrics:**
{json.dumps(metrics, indent=2)}

**Alert Conditions:**
{json.dumps(conditions, indent=2)}

**Notification Channels:** {", ".join(notification_channels)}

Requirements:
1. Create alert policies for all metrics
2. Configure alert conditions (threshold, absence, rate)
3. Setup notification channels
4. Add proper documentation strings
5. Configure alert aggregation
6. Setup incident auto-close
7. Add labels for organization
8. Configure severity levels
9. Include Terraform configuration
10. Add monitoring dashboards

Alert Policy should include:
- Display name and description
- Conditions (metric, threshold, duration)
- Notification channels
- Documentation (markdown)
- Alignment period
- Aggregation function

Provide:
1. Alert policy definitions (JSON/YAML)
2. Terraform configuration for policies
3. Notification channel setup
4. Uptime check configurations
5. Log-based metrics
6. Custom metrics if needed
7. Dashboard configuration
8. Runbook links
9. Documentation

Best practices:
- Use appropriate alignment periods
- Add proper alert documentation
- Configure alert grouping
- Setup escalation policies
- Monitor alert fatigue
"""

    def _build_slo_sli_prompt(
        self,
        service_name: str,
        availability_target: float,
        latency_target: Dict[str, float],
        error_budget: float
    ) -> str:
        """Build SLO/SLI definition prompt."""

        return f"""
Define Service Level Objectives (SLO) and Service Level Indicators (SLI).

**Service:** {service_name}
**Availability Target:** {availability_target} ({availability_target * 100}%)
**Latency Targets:** {json.dumps(latency_target, indent=2)}
**Error Budget:** {error_budget} ({error_budget * 100}%)

Requirements:
1. Define clear SLIs (measurable indicators)
2. Define SLOs (target values for SLIs)
3. Calculate error budget
4. Create monitoring queries for SLIs
5. Setup error budget alerts
6. Define error budget policy
7. Create SLO dashboard
8. Add documentation
9. Include incident response procedures
10. Setup reporting

SLIs to define:
- Availability SLI (successful requests / total requests)
- Latency SLI (requests below latency threshold / total requests)
- Error rate SLI
- Custom SLIs as needed

SLOs to define:
- Availability: {availability_target * 100}%
- Latency: {latency_target}
- Error budget: {error_budget * 100}%

Provide:
1. SLI definitions with PromQL/Cloud Monitoring queries
2. SLO targets and time windows (rolling 30 days)
3. Error budget calculation methodology
4. Error budget alerts (at 50%, 75%, 90%, 100% consumption)
5. SLO dashboard (Grafana JSON)
6. Error budget policy document
7. Incident response runbook
8. Monthly SLO report template
9. Documentation

Best practices:
- Use request-based SLIs for user-facing services
- Define SLOs based on user experience
- Monitor error budget consumption
- Review SLOs quarterly
- Document SLO violations
"""

    def _parse_prometheus_config(self, text: str) -> Dict[str, Any]:
        """Parse Prometheus configuration result."""

        result = {
            "prometheus_yml": "",
            "alert_rules_yml": "",
            "recording_rules_yml": "",
            "service_discovery": "",
            "documentation": text
        }

        # Extract YAML blocks
        yaml_blocks = re.findall(r'```yaml\n(.*?)```', text, re.DOTALL)
        if len(yaml_blocks) >= 3:
            result["prometheus_yml"] = yaml_blocks[0].strip()
            result["alert_rules_yml"] = yaml_blocks[1].strip()
            result["recording_rules_yml"] = yaml_blocks[2].strip()
        elif len(yaml_blocks) >= 2:
            result["prometheus_yml"] = yaml_blocks[0].strip()
            result["alert_rules_yml"] = yaml_blocks[1].strip()
        elif yaml_blocks:
            result["prometheus_yml"] = yaml_blocks[0].strip()

        return result

    def _parse_grafana_dashboard(self, text: str) -> Dict[str, Any]:
        """Parse Grafana dashboard result."""

        result = {
            "dashboard_json": "",
            "provisioning_yaml": "",
            "documentation": text
        }

        # Extract JSON dashboard
        json_blocks = re.findall(r'```json\n(.*?)```', text, re.DOTALL)
        if json_blocks:
            result["dashboard_json"] = json_blocks[0].strip()

        # Extract provisioning YAML
        yaml_blocks = re.findall(r'```yaml\n(.*?)```', text, re.DOTALL)
        if yaml_blocks:
            result["provisioning_yaml"] = yaml_blocks[0].strip()

        return result

    def _parse_tracing_config(self, text: str) -> Dict[str, Any]:
        """Parse tracing configuration result."""

        result = {
            "collector_config": "",
            "instrumentation_code": "",
            "deployment_manifests": "",
            "documentation": text
        }

        # Extract YAML blocks
        yaml_blocks = re.findall(r'```yaml\n(.*?)```', text, re.DOTALL)
        if len(yaml_blocks) >= 2:
            result["collector_config"] = yaml_blocks[0].strip()
            result["deployment_manifests"] = yaml_blocks[1].strip()
        elif yaml_blocks:
            result["collector_config"] = yaml_blocks[0].strip()

        # Extract Python code
        python_blocks = re.findall(r'```python\n(.*?)```', text, re.DOTALL)
        if python_blocks:
            result["instrumentation_code"] = python_blocks[0].strip()

        return result

    def _parse_cloud_monitoring(self, text: str) -> Dict[str, Any]:
        """Parse Cloud Monitoring result."""

        result = {
            "alert_policies": [],
            "terraform_config": "",
            "notification_setup": "",
            "documentation": text
        }

        # Extract JSON alert policies
        json_blocks = re.findall(r'```json\n(.*?)```', text, re.DOTALL)
        for json_str in json_blocks:
            try:
                result["alert_policies"].append(json.loads(json_str))
            except:
                pass

        # Extract Terraform
        tf_blocks = re.findall(r'```(?:terraform|hcl)\n(.*?)```', text, re.DOTALL)
        if tf_blocks:
            result["terraform_config"] = tf_blocks[0].strip()

        return result

    def _parse_slo_sli(self, text: str) -> Dict[str, Any]:
        """Parse SLO/SLI result."""

        result = {
            "slo_config": {},
            "sli_definitions": [],
            "monitoring_queries": [],
            "error_budget_policy": {},
            "documentation": text
        }

        # Extract JSON configurations
        json_blocks = re.findall(r'```json\n(.*?)```', text, re.DOTALL)
        for json_str in json_blocks:
            try:
                data = json.loads(json_str)
                if "slo" in str(data).lower():
                    result["slo_config"] = data
                elif "sli" in str(data).lower():
                    result["sli_definitions"].append(data)
            except:
                pass

        # Extract PromQL queries
        promql_blocks = re.findall(r'```promql\n(.*?)```', text, re.DOTALL)
        result["monitoring_queries"] = [q.strip() for q in promql_blocks]

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
        formatted = "\n\nRelevant observability patterns from knowledge base:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result.get('content', '')}\n\n"
        return formatted


# Standalone tool functions

def generate_prometheus_config(
    scrape_targets: List[Dict[str, Any]],
    alert_rules: List[Dict[str, Any]],
    recording_rules: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """Standalone function for Prometheus configuration."""
    agent = ObservabilityAgent(context={}, message_bus=None, orchestrator_id="")
    return agent.generate_prometheus_config(scrape_targets, alert_rules, recording_rules)


def generate_grafana_dashboard(
    metrics: List[str],
    panels: List[Dict[str, Any]],
    layout: Optional[Dict[str, Any]] = None,
    variables: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """Standalone function for Grafana dashboard generation."""
    agent = ObservabilityAgent(context={}, message_bus=None, orchestrator_id="")
    return agent.generate_grafana_dashboard(metrics, panels, layout, variables)


def define_slo_sli(
    service_name: str,
    availability_target: float,
    latency_target: Dict[str, float],
    error_budget: Optional[float] = None
) -> Dict[str, Any]:
    """Standalone function for SLO/SLI definition."""
    agent = ObservabilityAgent(context={}, message_bus=None, orchestrator_id="")
    return agent.define_slo_sli(service_name, availability_target, latency_target, error_budget)
