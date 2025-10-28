"""
agents/infrastructure/cloud_infrastructure/agent.py

Cloud Infrastructure Agent - Generates IaC for multi-cloud deployments.

Supports Terraform, CloudFormation, and GCP Deployment Manager for infrastructure
provisioning across GCP, AWS, and Azure.
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


class CloudInfrastructureAgent(A2AEnabledAgent, DynamicKnowledgeBaseIntegration):
    """
    Cloud Infrastructure Agent for IaC generation.

    Capabilities:
    - Terraform module development (GCP, AWS, Azure)
    - CloudFormation template generation
    - GCP Deployment Manager configuration
    - Multi-cloud infrastructure design
    - Cost optimization recommendations
    - Security best practices
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        vector_db_client=None,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize Cloud Infrastructure Agent."""
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
        self.infrastructure_history: List[Dict[str, Any]] = []

    def handle_task_assignment(self, message: Dict[str, Any]) -> None:
        """Handle TASK_ASSIGNMENT message from orchestrator."""
        payload = message.get("payload", {})
        task_id = payload.get("task_id")
        task_type = payload.get("task_type")
        parameters = payload.get("parameters", {})

        try:
            if task_type == "generate_terraform_module":
                result = self.generate_terraform_module(task_id=task_id, **parameters)
            elif task_type == "generate_cloudformation":
                result = self.generate_cloudformation(task_id=task_id, **parameters)
            elif task_type == "generate_gcp_deployment_manager":
                result = self.generate_gcp_deployment_manager(task_id=task_id, **parameters)
            elif task_type == "generate_multi_cloud_setup":
                result = self.generate_multi_cloud_setup(task_id=task_id, **parameters)
            elif task_type == "optimize_infrastructure_cost":
                result = self.optimize_infrastructure_cost(task_id=task_id, **parameters)
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
                error_type="INFRASTRUCTURE_GENERATION_FAILED",
                error_message=str(e),
                stack_trace=""
            )

    @A2AIntegration.with_task_tracking
    def generate_terraform_module(
        self,
        cloud_provider: str,
        resources: List[Dict[str, Any]],
        variables: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate Terraform module for cloud infrastructure.

        Args:
            cloud_provider: Cloud provider (gcp, aws, azure)
            resources: List of resources to provision
            variables: Terraform variables
            task_id: Optional task ID

        Returns:
            {
                "main_tf": str,
                "variables_tf": str,
                "outputs_tf": str,
                "readme": str,
                "examples": str
            }
        """
        start_time = datetime.utcnow()
        print(f"[Cloud Infrastructure] Generating Terraform module for {cloud_provider}")

        # Query KB for Terraform patterns
        kb_context = ""
        if hasattr(self, 'should_query_kb') and self.should_query_kb({"provider": cloud_provider}):
            kb_results = self.execute_dynamic_query(
                query_type="terraform_patterns",
                context={"provider": cloud_provider, "resource_count": len(resources)},
                task_id=task_id
            )
            if kb_results:
                kb_context = self._format_kb_results(kb_results)

        # Build prompt
        prompt = self._build_terraform_prompt(
            cloud_provider=cloud_provider,
            resources=resources,
            variables=variables or {},
            kb_context=kb_context
        )

        # Generate with LLM
        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        # Parse result
        result = self._parse_terraform_module(response.text)

        # Add metadata
        duration = (datetime.utcnow() - start_time).total_seconds() / 60
        result.update({
            "cloud_provider": cloud_provider,
            "resource_count": len(resources),
            "duration_minutes": duration,
            "timestamp": datetime.utcnow().isoformat()
        })

        self.infrastructure_history.append({
            "task_id": task_id,
            "iac_tool": "terraform",
            "provider": cloud_provider,
            "timestamp": result["timestamp"]
        })

        return result

    @A2AIntegration.with_task_tracking
    def generate_cloudformation(
        self,
        resources: List[Dict[str, Any]],
        parameters: Optional[Dict[str, Any]] = None,
        conditions: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AWS CloudFormation template.

        Args:
            resources: AWS resources to provision
            parameters: CloudFormation parameters
            conditions: Conditional resource creation
            task_id: Optional task ID

        Returns:
            {
                "template": str,
                "parameters_file": str,
                "deployment_guide": str,
                "validation_script": str
            }
        """
        print(f"[Cloud Infrastructure] Generating CloudFormation template")

        prompt = self._build_cloudformation_prompt(
            resources=resources,
            parameters=parameters or {},
            conditions=conditions or {}
        )

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = self._parse_cloudformation(response.text)
        result.update({
            "resource_count": len(resources),
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    @A2AIntegration.with_task_tracking
    def generate_gcp_deployment_manager(
        self,
        resources: List[Dict[str, Any]],
        properties: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate GCP Deployment Manager configuration.

        Args:
            resources: GCP resources to provision
            properties: Deployment properties
            task_id: Optional task ID

        Returns:
            {
                "config_yaml": str,
                "schema_yaml": str,
                "deployment_script": str,
                "documentation": str
            }
        """
        print(f"[Cloud Infrastructure] Generating GCP Deployment Manager config")

        prompt = self._build_gcp_dm_prompt(
            resources=resources,
            properties=properties or {}
        )

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = self._parse_gcp_dm(response.text)
        result.update({
            "resource_count": len(resources),
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    @A2AIntegration.with_task_tracking
    def generate_multi_cloud_setup(
        self,
        primary_cloud: str,
        dr_cloud: str,
        resources: List[Dict[str, Any]],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate multi-cloud infrastructure setup.

        Args:
            primary_cloud: Primary cloud provider (gcp, aws, azure)
            dr_cloud: DR/backup cloud provider
            resources: Resources to deploy across clouds
            task_id: Optional task ID

        Returns:
            {
                "primary_config": str,
                "dr_config": str,
                "replication_setup": str,
                "failover_plan": str,
                "architecture_diagram": str
            }
        """
        print(f"[Cloud Infrastructure] Generating multi-cloud setup: {primary_cloud} + {dr_cloud}")

        prompt = self._build_multi_cloud_prompt(
            primary_cloud=primary_cloud,
            dr_cloud=dr_cloud,
            resources=resources
        )

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = self._parse_multi_cloud(response.text)
        result.update({
            "primary_cloud": primary_cloud,
            "dr_cloud": dr_cloud,
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    @A2AIntegration.with_task_tracking
    def optimize_infrastructure_cost(
        self,
        current_infrastructure: Dict[str, Any],
        budget_target: Optional[float] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze and optimize infrastructure costs.

        Args:
            current_infrastructure: Current infrastructure configuration
            budget_target: Target monthly budget (optional)
            task_id: Optional task ID

        Returns:
            {
                "analysis": str,
                "recommendations": List[Dict],
                "estimated_savings": float,
                "optimized_config": str
            }
        """
        print(f"[Cloud Infrastructure] Optimizing infrastructure costs")

        prompt = self._build_cost_optimization_prompt(
            current_infrastructure=current_infrastructure,
            budget_target=budget_target
        )

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = self._parse_cost_optimization(response.text)
        result.update({
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    def _build_terraform_prompt(
        self,
        cloud_provider: str,
        resources: List[Dict[str, Any]],
        variables: Dict[str, Any],
        kb_context: str
    ) -> str:
        """Build Terraform generation prompt."""

        provider_configs = {
            "gcp": """
Provider: Google Cloud Platform
Terraform Provider: google
Common Resources: google_compute_instance, google_storage_bucket, google_sql_database_instance
""",
            "aws": """
Provider: Amazon Web Services
Terraform Provider: aws
Common Resources: aws_instance, aws_s3_bucket, aws_rds_instance, aws_vpc
""",
            "azure": """
Provider: Microsoft Azure
Terraform Provider: azurerm
Common Resources: azurerm_virtual_machine, azurerm_storage_account, azurerm_sql_database
"""
        }

        return f"""
Generate production-ready Terraform module for {cloud_provider.upper()}.

{provider_configs.get(cloud_provider, "")}

**Resources to Provision:**
{json.dumps(resources, indent=2)}

**Variables:**
{json.dumps(variables, indent=2)}

Requirements:
1. Create modular, reusable Terraform code
2. Use Terraform 1.0+ syntax
3. Define all resources with proper configuration
4. Add comprehensive input variables with descriptions and types
5. Define meaningful outputs
6. Include data sources where appropriate
7. Add resource dependencies
8. Use locals for computed values
9. Add proper tags/labels for resource management
10. Include security best practices

File Structure:
- main.tf: Primary resource definitions
- variables.tf: Input variable declarations
- outputs.tf: Output value definitions
- versions.tf: Provider version constraints
- README.md: Module documentation with examples

Provide:
1. Complete main.tf
2. Complete variables.tf with validation
3. Complete outputs.tf
4. Provider version constraints
5. README with usage examples
6. Examples directory with sample usage
7. Security considerations

{kb_context}

Best practices:
- Use remote state backend
- Enable state locking
- Use workspaces for environments
- Implement proper IAM/security groups
- Add lifecycle rules where appropriate
- Use terraform fmt conventions
"""

    def _build_cloudformation_prompt(
        self,
        resources: List[Dict[str, Any]],
        parameters: Dict[str, Any],
        conditions: Dict[str, Any]
    ) -> str:
        """Build CloudFormation generation prompt."""

        return f"""
Generate AWS CloudFormation template (YAML format).

**Resources:**
{json.dumps(resources, indent=2)}

**Parameters:**
{json.dumps(parameters, indent=2)}

**Conditions:**
{json.dumps(conditions, indent=2)}

Requirements:
1. Use YAML format for readability
2. Define all AWS resources with proper types
3. Add Parameters section for configurability
4. Add Conditions for conditional resource creation
5. Define Outputs for important values
6. Use Intrinsic Functions (Ref, GetAtt, Join, etc.)
7. Add proper DependsOn where needed
8. Include Metadata for parameter grouping
9. Add Tags to all taggable resources
10. Follow AWS best practices

Template Structure:
- AWSTemplateFormatVersion
- Description
- Metadata
- Parameters
- Conditions
- Resources
- Outputs

Provide:
1. Complete CloudFormation template (YAML)
2. Parameters file for different environments
3. Deployment command examples
4. Validation script (aws cloudformation validate-template)
5. Stack policy for production
6. Change set creation guide
7. Documentation

Best practices:
- Use stack policies for critical resources
- Implement rollback triggers
- Use nested stacks for large deployments
- Add termination protection
- Use AWS Secrets Manager for sensitive data
"""

    def _build_gcp_dm_prompt(
        self,
        resources: List[Dict[str, Any]],
        properties: Dict[str, Any]
    ) -> str:
        """Build GCP Deployment Manager prompt."""

        return f"""
Generate Google Cloud Deployment Manager configuration.

**Resources:**
{json.dumps(resources, indent=2)}

**Properties:**
{json.dumps(properties, indent=2)}

Requirements:
1. Use YAML configuration format
2. Define all GCP resources with types
3. Add properties for resource configuration
4. Use templates for reusability
5. Define outputs for important values
6. Add resource metadata
7. Use references between resources
8. Include schema file for validation
9. Add proper IAM bindings
10. Follow GCP best practices

Configuration Structure:
- imports (template files)
- resources
- outputs

Provide:
1. Main configuration YAML
2. Python/Jinja2 templates if needed
3. Schema files for custom types
4. Deployment script (gcloud deployment-manager)
5. Update strategy
6. Documentation

Best practices:
- Use templates for reusable components
- Implement proper IAM least privilege
- Add labels for resource organization
- Use service accounts with minimal permissions
- Enable audit logging
"""

    def _build_multi_cloud_prompt(
        self,
        primary_cloud: str,
        dr_cloud: str,
        resources: List[Dict[str, Any]]
    ) -> str:
        """Build multi-cloud setup prompt."""

        return f"""
Design multi-cloud infrastructure with disaster recovery.

**Primary Cloud:** {primary_cloud.upper()}
**DR/Backup Cloud:** {dr_cloud.upper()}

**Resources:**
{json.dumps(resources, indent=2)}

Requirements:
1. Design primary infrastructure on {primary_cloud}
2. Design DR infrastructure on {dr_cloud}
3. Setup cross-cloud networking (VPN/Interconnect)
4. Implement data replication strategy
5. Design failover and failback procedures
6. Setup monitoring and health checks
7. Implement traffic routing (DNS-based or global LB)
8. Add cost optimization for DR environment
9. Design backup and recovery procedures
10. Document RTO and RPO targets

Provide:
1. Primary cloud IaC (Terraform/native)
2. DR cloud IaC
3. Networking setup (VPN/peering)
4. Data replication configuration
5. Failover automation scripts
6. Monitoring and alerting setup
7. Architecture diagram (Mermaid)
8. Runbook for disaster scenarios
9. Cost analysis
10. Documentation

Consider:
- Active-Passive vs Active-Active
- Data consistency across clouds
- Network latency and bandwidth
- Cost optimization (reserved instances in DR)
- Compliance requirements
"""

    def _build_cost_optimization_prompt(
        self,
        current_infrastructure: Dict[str, Any],
        budget_target: Optional[float]
    ) -> str:
        """Build cost optimization prompt."""

        budget_text = f"Target Monthly Budget: ${budget_target}" if budget_target else "No specific budget target"

        return f"""
Analyze and optimize cloud infrastructure costs.

**Current Infrastructure:**
{json.dumps(current_infrastructure, indent=2)}

**{budget_text}**

Requirements:
1. Analyze current resource usage and costs
2. Identify over-provisioned resources
3. Recommend rightsizing opportunities
4. Suggest reserved instances/committed use discounts
5. Identify idle/unused resources
6. Recommend storage optimization
7. Suggest network cost optimization
8. Recommend auto-scaling policies
9. Identify cost anomalies
10. Provide implementation priority

Provide:
1. Cost analysis report
2. Prioritized recommendations with savings estimates
3. Rightsizing recommendations (instance types, storage tiers)
4. Reserved capacity/committed use opportunities
5. Resources to delete (idle, unused)
6. Auto-scaling configurations
7. Storage lifecycle policies
8. Network optimization (NAT, data transfer)
9. Implementation plan with effort estimates
10. Monitoring and alerting for cost spikes

Cost optimization strategies:
- Compute: Rightsizing, spot instances, auto-scaling
- Storage: Lifecycle policies, archival, compression
- Network: CDN, peering, data transfer optimization
- Database: Read replicas, connection pooling
- Monitoring: Log retention, metrics aggregation
"""

    def _parse_terraform_module(self, text: str) -> Dict[str, Any]:
        """Parse Terraform module result."""

        result = {
            "main_tf": "",
            "variables_tf": "",
            "outputs_tf": "",
            "readme": "",
            "examples": ""
        }

        # Extract HCL code blocks
        hcl_blocks = re.findall(r'```(?:terraform|hcl)\n(.*?)```', text, re.DOTALL)
        if len(hcl_blocks) >= 3:
            result["main_tf"] = hcl_blocks[0].strip()
            result["variables_tf"] = hcl_blocks[1].strip()
            result["outputs_tf"] = hcl_blocks[2].strip()
        elif len(hcl_blocks) >= 1:
            result["main_tf"] = hcl_blocks[0].strip()

        # Extract README
        md_blocks = re.findall(r'```markdown\n(.*?)```', text, re.DOTALL)
        if md_blocks:
            result["readme"] = md_blocks[0].strip()

        return result

    def _parse_cloudformation(self, text: str) -> Dict[str, Any]:
        """Parse CloudFormation result."""

        result = {
            "template": "",
            "parameters_file": "",
            "deployment_guide": text,
            "validation_script": ""
        }

        # Extract YAML template
        yaml_blocks = re.findall(r'```yaml\n(.*?)```', text, re.DOTALL)
        if yaml_blocks:
            result["template"] = yaml_blocks[0].strip()

        # Extract bash scripts
        bash_blocks = re.findall(r'```bash\n(.*?)```', text, re.DOTALL)
        if bash_blocks:
            result["validation_script"] = bash_blocks[0].strip()

        return result

    def _parse_gcp_dm(self, text: str) -> Dict[str, Any]:
        """Parse GCP Deployment Manager result."""

        result = {
            "config_yaml": "",
            "schema_yaml": "",
            "deployment_script": "",
            "documentation": text
        }

        # Extract YAML blocks
        yaml_blocks = re.findall(r'```yaml\n(.*?)```', text, re.DOTALL)
        if len(yaml_blocks) >= 2:
            result["config_yaml"] = yaml_blocks[0].strip()
            result["schema_yaml"] = yaml_blocks[1].strip()
        elif yaml_blocks:
            result["config_yaml"] = yaml_blocks[0].strip()

        # Extract bash scripts
        bash_blocks = re.findall(r'```bash\n(.*?)```', text, re.DOTALL)
        if bash_blocks:
            result["deployment_script"] = bash_blocks[0].strip()

        return result

    def _parse_multi_cloud(self, text: str) -> Dict[str, Any]:
        """Parse multi-cloud setup result."""

        result = {
            "primary_config": "",
            "dr_config": "",
            "replication_setup": "",
            "failover_plan": text,
            "architecture_diagram": ""
        }

        # Extract diagrams
        mermaid_match = re.search(r'```mermaid\n(.*?)```', text, re.DOTALL)
        if mermaid_match:
            result["architecture_diagram"] = mermaid_match.group(1).strip()

        # Extract config blocks
        hcl_blocks = re.findall(r'```(?:terraform|hcl)\n(.*?)```', text, re.DOTALL)
        if len(hcl_blocks) >= 2:
            result["primary_config"] = hcl_blocks[0].strip()
            result["dr_config"] = hcl_blocks[1].strip()

        return result

    def _parse_cost_optimization(self, text: str) -> Dict[str, Any]:
        """Parse cost optimization result."""

        result = {
            "analysis": text,
            "recommendations": [],
            "estimated_savings": 0.0,
            "optimized_config": ""
        }

        # Extract savings estimate
        savings_match = re.search(r'\$?([\d,]+(?:\.\d{2})?)\s*(?:per month|monthly|/mo)', text, re.IGNORECASE)
        if savings_match:
            result["estimated_savings"] = float(savings_match.group(1).replace(',', ''))

        # Extract recommendations (look for numbered lists)
        recommendations = re.findall(r'\d+\.\s+(.+?)(?=\n\d+\.|\n\n|$)', text, re.DOTALL)
        result["recommendations"] = [{"recommendation": rec.strip()} for rec in recommendations]

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
        formatted = "\n\nRelevant infrastructure patterns from knowledge base:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result.get('content', '')}\n\n"
        return formatted


# Standalone tool functions

def generate_terraform_module(
    cloud_provider: str,
    resources: List[Dict[str, Any]],
    variables: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Standalone function for Terraform module generation."""
    agent = CloudInfrastructureAgent(context={}, message_bus=None, orchestrator_id="")
    return agent.generate_terraform_module(cloud_provider, resources, variables)


def generate_cloudformation(
    resources: List[Dict[str, Any]],
    parameters: Optional[Dict[str, Any]] = None,
    conditions: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Standalone function for CloudFormation generation."""
    agent = CloudInfrastructureAgent(context={}, message_bus=None, orchestrator_id="")
    return agent.generate_cloudformation(resources, parameters, conditions)


def generate_multi_cloud_setup(
    primary_cloud: str,
    dr_cloud: str,
    resources: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Standalone function for multi-cloud setup."""
    agent = CloudInfrastructureAgent(context={}, message_bus=None, orchestrator_id="")
    return agent.generate_multi_cloud_setup(primary_cloud, dr_cloud, resources)
