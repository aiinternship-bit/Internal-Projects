"""
agents/infrastructure/kubernetes/agent.py

Kubernetes Agent - Generates K8s manifests, Helm charts, and service mesh configs.

Supports Kubernetes 1.28+, Helm 3, Istio, and various deployment strategies including
Blue/Green, Canary, and Rolling updates.
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


class KubernetesAgent(A2AEnabledAgent, DynamicKnowledgeBaseIntegration):
    """
    Kubernetes Agent for container orchestration configuration.

    Capabilities:
    - Kubernetes manifest generation (Deployments, Services, ConfigMaps, etc.)
    - Helm chart development
    - Service mesh configuration (Istio, Linkerd)
    - Deployment strategies (Blue/Green, Canary, Rolling)
    - RBAC policy generation
    - Resource optimization
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        vector_db_client=None,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize Kubernetes Agent."""
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
        self.k8s_history: List[Dict[str, Any]] = []

    def handle_task_assignment(self, message: Dict[str, Any]) -> None:
        """Handle TASK_ASSIGNMENT message from orchestrator."""
        payload = message.get("payload", {})
        task_id = payload.get("task_id")
        task_type = payload.get("task_type")
        parameters = payload.get("parameters", {})

        try:
            if task_type == "generate_k8s_manifests":
                result = self.generate_k8s_manifests(task_id=task_id, **parameters)
            elif task_type == "generate_helm_chart":
                result = self.generate_helm_chart(task_id=task_id, **parameters)
            elif task_type == "generate_istio_config":
                result = self.generate_istio_config(task_id=task_id, **parameters)
            elif task_type == "generate_deployment_strategy":
                result = self.generate_deployment_strategy(task_id=task_id, **parameters)
            elif task_type == "generate_rbac_policies":
                result = self.generate_rbac_policies(task_id=task_id, **parameters)
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
                error_type="K8S_GENERATION_FAILED",
                error_message=str(e),
                stack_trace=""
            )

    @A2AIntegration.with_task_tracking
    def generate_k8s_manifests(
        self,
        app_spec: Dict[str, Any],
        resources: Dict[str, Any],
        config_maps: Optional[List[Dict]] = None,
        secrets: Optional[List[Dict]] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate Kubernetes manifests for an application.

        Args:
            app_spec: Application specification (name, image, ports, etc.)
            resources: Resource requirements (CPU, memory limits/requests)
            config_maps: ConfigMap definitions
            secrets: Secret definitions
            task_id: Optional task ID

        Returns:
            {
                "deployment": str,
                "service": str,
                "configmap": str,
                "secret": str,
                "ingress": str,
                "hpa": str,
                "pdb": str
            }
        """
        start_time = datetime.utcnow()
        print(f"[Kubernetes] Generating manifests for {app_spec.get('name')}")

        # Query KB for K8s patterns
        kb_context = ""
        if hasattr(self, 'should_query_kb') and self.should_query_kb(app_spec):
            kb_results = self.execute_dynamic_query(
                query_type="k8s_patterns",
                context={"app_type": app_spec.get("type", "web")},
                task_id=task_id
            )
            if kb_results:
                kb_context = self._format_kb_results(kb_results)

        # Build prompt
        prompt = self._build_k8s_manifests_prompt(
            app_spec=app_spec,
            resources=resources,
            config_maps=config_maps or [],
            secrets=secrets or [],
            kb_context=kb_context
        )

        # Generate with LLM
        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        # Parse result
        result = self._parse_k8s_manifests(response.text)

        # Add metadata
        duration = (datetime.utcnow() - start_time).total_seconds() / 60
        result.update({
            "app_name": app_spec.get("name"),
            "duration_minutes": duration,
            "timestamp": datetime.utcnow().isoformat()
        })

        self.k8s_history.append({
            "task_id": task_id,
            "operation": "generate_manifests",
            "app_name": app_spec.get("name"),
            "timestamp": result["timestamp"]
        })

        return result

    @A2AIntegration.with_task_tracking
    def generate_helm_chart(
        self,
        app_name: str,
        values: Dict[str, Any],
        templates: Optional[List[str]] = None,
        dependencies: Optional[List[Dict]] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate Helm chart for Kubernetes application.

        Args:
            app_name: Application name
            values: Default values for the chart
            templates: Template types to include
            dependencies: Chart dependencies
            task_id: Optional task ID

        Returns:
            {
                "chart_yaml": str,
                "values_yaml": str,
                "templates": Dict[str, str],
                "helpers_tpl": str,
                "readme": str
            }
        """
        print(f"[Kubernetes] Generating Helm chart for {app_name}")

        kb_context = ""
        if hasattr(self, 'should_query_kb') and self.should_query_kb({"app": app_name}):
            kb_results = self.execute_dynamic_query(
                query_type="helm_patterns",
                context={"app_name": app_name},
                task_id=task_id
            )
            if kb_results:
                kb_context = self._format_kb_results(kb_results)

        prompt = self._build_helm_chart_prompt(
            app_name=app_name,
            values=values,
            templates=templates or ["deployment", "service", "ingress"],
            dependencies=dependencies or [],
            kb_context=kb_context
        )

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = self._parse_helm_chart(response.text)
        result.update({
            "app_name": app_name,
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    @A2AIntegration.with_task_tracking
    def generate_istio_config(
        self,
        services: List[Dict[str, Any]],
        routing_rules: Optional[List[Dict]] = None,
        policies: Optional[List[Dict]] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate Istio service mesh configuration.

        Args:
            services: List of services in the mesh
            routing_rules: Traffic routing rules
            policies: Security and traffic policies
            task_id: Optional task ID

        Returns:
            {
                "virtual_services": List[str],
                "destination_rules": List[str],
                "gateways": List[str],
                "peer_authentication": str,
                "authorization_policy": str
            }
        """
        print(f"[Kubernetes] Generating Istio config for {len(services)} services")

        prompt = self._build_istio_config_prompt(
            services=services,
            routing_rules=routing_rules or [],
            policies=policies or []
        )

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = self._parse_istio_config(response.text)
        result.update({
            "service_count": len(services),
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    @A2AIntegration.with_task_tracking
    def generate_deployment_strategy(
        self,
        strategy_type: str,
        rollout_config: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate deployment strategy configuration.

        Args:
            strategy_type: Strategy type (blue_green, canary, rolling_update)
            rollout_config: Rollout configuration (steps, intervals, etc.)
            task_id: Optional task ID

        Returns:
            {
                "strategy_manifests": str,
                "rollout_script": str,
                "validation_tests": str,
                "rollback_procedure": str
            }
        """
        print(f"[Kubernetes] Generating {strategy_type} deployment strategy")

        prompt = self._build_deployment_strategy_prompt(
            strategy_type=strategy_type,
            rollout_config=rollout_config
        )

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = self._parse_deployment_strategy(response.text)
        result.update({
            "strategy_type": strategy_type,
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    @A2AIntegration.with_task_tracking
    def generate_rbac_policies(
        self,
        service_accounts: List[Dict[str, Any]],
        roles: List[Dict[str, Any]],
        bindings: List[Dict[str, Any]],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate Kubernetes RBAC policies.

        Args:
            service_accounts: ServiceAccount definitions
            roles: Role/ClusterRole definitions
            bindings: RoleBinding/ClusterRoleBinding definitions
            task_id: Optional task ID

        Returns:
            {
                "service_accounts": str,
                "roles": str,
                "role_bindings": str,
                "documentation": str
            }
        """
        print(f"[Kubernetes] Generating RBAC policies")

        prompt = self._build_rbac_policies_prompt(
            service_accounts=service_accounts,
            roles=roles,
            bindings=bindings
        )

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = self._parse_rbac_policies(response.text)
        result.update({
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    def _build_k8s_manifests_prompt(
        self,
        app_spec: Dict[str, Any],
        resources: Dict[str, Any],
        config_maps: List[Dict],
        secrets: List[Dict],
        kb_context: str
    ) -> str:
        """Build Kubernetes manifests generation prompt."""

        return f"""
Generate production-ready Kubernetes manifests.

**Application Specification:**
{json.dumps(app_spec, indent=2)}

**Resource Requirements:**
{json.dumps(resources, indent=2)}

**ConfigMaps:**
{json.dumps(config_maps, indent=2)}

**Secrets:**
{json.dumps(secrets, indent=2)}

Requirements:
1. Generate Deployment manifest with best practices
2. Generate Service (ClusterIP, LoadBalancer, or NodePort)
3. Generate ConfigMap for application configuration
4. Generate Secret for sensitive data (base64 encoded)
5. Generate Ingress for external access
6. Generate HorizontalPodAutoscaler (HPA)
7. Generate PodDisruptionBudget (PDB)
8. Add proper labels and selectors
9. Include health checks (liveness, readiness, startup probes)
10. Add resource limits and requests

Deployment Best Practices:
- Use rolling update strategy
- Set replicas appropriately
- Add anti-affinity rules for HA
- Use init containers if needed
- Add volume mounts for ConfigMaps/Secrets
- Set security context (non-root, read-only filesystem)
- Add annotations for monitoring

Provide:
1. deployment.yaml
2. service.yaml
3. configmap.yaml
4. secret.yaml
5. ingress.yaml
6. hpa.yaml
7. pdb.yaml

{kb_context}

Use Kubernetes API version apps/v1 and follow latest best practices.
"""

    def _build_helm_chart_prompt(
        self,
        app_name: str,
        values: Dict[str, Any],
        templates: List[str],
        dependencies: List[Dict],
        kb_context: str
    ) -> str:
        """Build Helm chart generation prompt."""

        return f"""
Generate production-ready Helm chart.

**Application Name:** {app_name}

**Default Values:**
{json.dumps(values, indent=2)}

**Templates to Include:** {", ".join(templates)}

**Dependencies:**
{json.dumps(dependencies, indent=2)}

Requirements:
1. Create Chart.yaml with proper metadata
2. Create values.yaml with all configurable parameters
3. Create template files for each resource type
4. Create _helpers.tpl with reusable template helpers
5. Add NOTES.txt for post-install instructions
6. Include .helmignore file
7. Add proper templating with {{ .Values }} references
8. Include conditional logic with {{ if }}
9. Add range loops for multiple resources
10. Include comprehensive README.md

Chart.yaml should include:
- apiVersion: v2
- name, version, appVersion
- description
- dependencies (if any)

values.yaml should include:
- Sensible defaults
- Comments explaining each value
- Organized into logical sections

Templates should include:
- Proper Go templating
- Validation checks
- Default values with "default" function
- Proper indentation helpers

Provide:
1. Chart.yaml
2. values.yaml
3. All template files (deployment.yaml, service.yaml, etc.)
4. _helpers.tpl
5. NOTES.txt
6. README.md with installation instructions

{kb_context}

Follow Helm 3 best practices and chart conventions.
"""

    def _build_istio_config_prompt(
        self,
        services: List[Dict[str, Any]],
        routing_rules: List[Dict],
        policies: List[Dict]
    ) -> str:
        """Build Istio configuration prompt."""

        return f"""
Generate Istio service mesh configuration.

**Services:**
{json.dumps(services, indent=2)}

**Routing Rules:**
{json.dumps(routing_rules, indent=2)}

**Policies:**
{json.dumps(policies, indent=2)}

Requirements:
1. Create Gateway for ingress traffic
2. Create VirtualService for each service (routing rules)
3. Create DestinationRule for each service (load balancing, circuit breaker)
4. Configure PeerAuthentication for mTLS
5. Create AuthorizationPolicy for access control
6. Add traffic splitting for canary deployments
7. Configure request timeouts and retries
8. Add fault injection for testing
9. Configure circuit breakers
10. Add telemetry configuration

VirtualService should include:
- HTTP/gRPC routing rules
- Header-based routing
- Weight-based traffic splitting
- Request timeout configuration
- Retry policies

DestinationRule should include:
- Traffic policy (load balancing)
- Connection pool settings
- Circuit breaker configuration
- TLS settings
- Subset definitions for canary

Security:
- Enable strict mTLS mode
- Define authorization policies
- Service-to-service authentication

Provide:
1. gateway.yaml
2. virtual-service.yaml for each service
3. destination-rule.yaml for each service
4. peer-authentication.yaml
5. authorization-policy.yaml
6. telemetry.yaml
7. Documentation

Follow Istio 1.20+ best practices.
"""

    def _build_deployment_strategy_prompt(
        self,
        strategy_type: str,
        rollout_config: Dict[str, Any]
    ) -> str:
        """Build deployment strategy prompt."""

        strategy_guides = {
            "blue_green": """
Blue/Green Deployment Strategy:
- Two identical environments (blue=current, green=new)
- Deploy new version to green environment
- Test green environment thoroughly
- Switch traffic from blue to green
- Keep blue as instant rollback option
""",
            "canary": """
Canary Deployment Strategy:
- Deploy new version to small subset of pods
- Gradually increase traffic to new version
- Monitor metrics and errors closely
- Rollback if issues detected
- Full rollout if metrics look good
""",
            "rolling_update": """
Rolling Update Strategy:
- Update pods incrementally
- Maintain availability during update
- Configure maxSurge and maxUnavailable
- Health checks ensure pod readiness
- Automatic rollback on failure
"""
        }

        return f"""
Generate {strategy_type.upper()} deployment strategy configuration.

{strategy_guides.get(strategy_type, "")}

**Rollout Configuration:**
{json.dumps(rollout_config, indent=2)}

Requirements:
1. Create manifests for {strategy_type} deployment
2. Generate deployment automation scripts
3. Add validation and health check tests
4. Include rollback procedures
5. Add monitoring and alerting configuration
6. Include traffic routing configuration
7. Add smoke tests for validation
8. Generate deployment checklist
9. Add metric thresholds for auto-rollback
10. Include incident response procedures

Provide:
1. Kubernetes manifests (Deployment, Service, etc.)
2. Deployment automation script (bash or kubectl)
3. Validation test suite
4. Rollback procedure documentation
5. Monitoring configuration
6. Runbook for deployment
7. Troubleshooting guide

Deployment should include:
- Proper labels for version tracking
- Health check configuration
- Resource limits
- Monitoring annotations
"""

    def _build_rbac_policies_prompt(
        self,
        service_accounts: List[Dict[str, Any]],
        roles: List[Dict[str, Any]],
        bindings: List[Dict[str, Any]]
    ) -> str:
        """Build RBAC policies prompt."""

        return f"""
Generate Kubernetes RBAC (Role-Based Access Control) policies.

**Service Accounts:**
{json.dumps(service_accounts, indent=2)}

**Roles:**
{json.dumps(roles, indent=2)}

**Bindings:**
{json.dumps(bindings, indent=2)}

Requirements:
1. Create ServiceAccount resources
2. Create Role/ClusterRole with minimal permissions
3. Create RoleBinding/ClusterRoleBinding
4. Follow principle of least privilege
5. Add proper labels and annotations
6. Include documentation for each permission
7. Separate roles for different responsibilities
8. Use namespace-scoped Roles when possible
9. Audit permissions regularly
10. Include security best practices

For each Role/ClusterRole:
- Define specific API groups
- Specify exact resources
- Limit verbs to minimum required
- Add comments explaining permissions

For each ServiceAccount:
- Create in appropriate namespace
- Add annotations for tooling
- Document intended use

Provide:
1. service-accounts.yaml
2. roles.yaml (Role and ClusterRole)
3. role-bindings.yaml (RoleBinding and ClusterRoleBinding)
4. Documentation explaining each policy
5. Audit checklist
6. Security recommendations

Follow Kubernetes RBAC best practices and security hardening guidelines.
"""

    def _parse_k8s_manifests(self, text: str) -> Dict[str, Any]:
        """Parse Kubernetes manifests result."""

        result = {
            "deployment": "",
            "service": "",
            "configmap": "",
            "secret": "",
            "ingress": "",
            "hpa": "",
            "pdb": ""
        }

        # Extract YAML blocks
        yaml_blocks = re.findall(r'```yaml\n(.*?)```', text, re.DOTALL)

        # Assign blocks based on content
        for block in yaml_blocks:
            if "kind: Deployment" in block:
                result["deployment"] = block.strip()
            elif "kind: Service" in block:
                result["service"] = block.strip()
            elif "kind: ConfigMap" in block:
                result["configmap"] = block.strip()
            elif "kind: Secret" in block:
                result["secret"] = block.strip()
            elif "kind: Ingress" in block:
                result["ingress"] = block.strip()
            elif "kind: HorizontalPodAutoscaler" in block:
                result["hpa"] = block.strip()
            elif "kind: PodDisruptionBudget" in block:
                result["pdb"] = block.strip()

        return result

    def _parse_helm_chart(self, text: str) -> Dict[str, Any]:
        """Parse Helm chart result."""

        result = {
            "chart_yaml": "",
            "values_yaml": "",
            "templates": {},
            "helpers_tpl": "",
            "readme": ""
        }

        # Extract YAML blocks
        yaml_blocks = re.findall(r'```yaml\n(.*?)```', text, re.DOTALL)
        if len(yaml_blocks) >= 2:
            result["chart_yaml"] = yaml_blocks[0].strip()
            result["values_yaml"] = yaml_blocks[1].strip()

        # Extract template blocks
        template_blocks = re.findall(r'```(?:yaml|tpl)\n(.*?)```', text, re.DOTALL)
        for i, block in enumerate(template_blocks[2:], 1):  # Skip Chart.yaml and values.yaml
            result["templates"][f"template_{i}"] = block.strip()

        # Extract README
        md_blocks = re.findall(r'```markdown\n(.*?)```', text, re.DOTALL)
        if md_blocks:
            result["readme"] = md_blocks[0].strip()

        return result

    def _parse_istio_config(self, text: str) -> Dict[str, Any]:
        """Parse Istio configuration result."""

        result = {
            "virtual_services": [],
            "destination_rules": [],
            "gateways": [],
            "peer_authentication": "",
            "authorization_policy": ""
        }

        # Extract YAML blocks
        yaml_blocks = re.findall(r'```yaml\n(.*?)```', text, re.DOTALL)

        for block in yaml_blocks:
            if "kind: VirtualService" in block:
                result["virtual_services"].append(block.strip())
            elif "kind: DestinationRule" in block:
                result["destination_rules"].append(block.strip())
            elif "kind: Gateway" in block:
                result["gateways"].append(block.strip())
            elif "kind: PeerAuthentication" in block:
                result["peer_authentication"] = block.strip()
            elif "kind: AuthorizationPolicy" in block:
                result["authorization_policy"] = block.strip()

        return result

    def _parse_deployment_strategy(self, text: str) -> Dict[str, Any]:
        """Parse deployment strategy result."""

        result = {
            "strategy_manifests": "",
            "rollout_script": "",
            "validation_tests": "",
            "rollback_procedure": text
        }

        # Extract YAML manifests
        yaml_blocks = re.findall(r'```yaml\n(.*?)```', text, re.DOTALL)
        if yaml_blocks:
            result["strategy_manifests"] = "\n---\n".join(yaml_blocks)

        # Extract bash scripts
        bash_blocks = re.findall(r'```bash\n(.*?)```', text, re.DOTALL)
        if bash_blocks:
            result["rollout_script"] = bash_blocks[0].strip()

        return result

    def _parse_rbac_policies(self, text: str) -> Dict[str, Any]:
        """Parse RBAC policies result."""

        result = {
            "service_accounts": "",
            "roles": "",
            "role_bindings": "",
            "documentation": text
        }

        # Extract YAML blocks
        yaml_blocks = re.findall(r'```yaml\n(.*?)```', text, re.DOTALL)

        service_accounts = []
        roles = []
        bindings = []

        for block in yaml_blocks:
            if "kind: ServiceAccount" in block:
                service_accounts.append(block.strip())
            elif "kind: Role" in block or "kind: ClusterRole" in block:
                roles.append(block.strip())
            elif "kind: RoleBinding" in block or "kind: ClusterRoleBinding" in block:
                bindings.append(block.strip())

        result["service_accounts"] = "\n---\n".join(service_accounts) if service_accounts else ""
        result["roles"] = "\n---\n".join(roles) if roles else ""
        result["role_bindings"] = "\n---\n".join(bindings) if bindings else ""

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
        formatted = "\n\nRelevant Kubernetes patterns from knowledge base:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result.get('content', '')}\n\n"
        return formatted


# Standalone tool functions

def generate_k8s_manifests(
    app_spec: Dict[str, Any],
    resources: Dict[str, Any],
    config_maps: Optional[List[Dict]] = None,
    secrets: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """Standalone function for K8s manifest generation."""
    agent = KubernetesAgent(context={}, message_bus=None, orchestrator_id="")
    return agent.generate_k8s_manifests(app_spec, resources, config_maps, secrets)


def generate_helm_chart(
    app_name: str,
    values: Dict[str, Any],
    templates: Optional[List[str]] = None,
    dependencies: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """Standalone function for Helm chart generation."""
    agent = KubernetesAgent(context={}, message_bus=None, orchestrator_id="")
    return agent.generate_helm_chart(app_name, values, templates, dependencies)


def generate_istio_config(
    services: List[Dict[str, Any]],
    routing_rules: Optional[List[Dict]] = None,
    policies: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """Standalone function for Istio configuration."""
    agent = KubernetesAgent(context={}, message_bus=None, orchestrator_id="")
    return agent.generate_istio_config(services, routing_rules, policies)
