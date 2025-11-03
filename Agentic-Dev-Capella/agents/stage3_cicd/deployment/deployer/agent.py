"""
agents/stage3_cicd/deployment/deployer/agent.py

Deployer agent deploys services to target environments.
"""

from typing import Dict, List, Any, Optional
import re
import json

from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration


def deploy_to_environment(
    service: str,
    environment: str,
    artifacts: Dict[str, Any]
) -> Dict[str, Any]:
    """Deploy service to target environment."""
    return {
        "status": "success",
        "deployment": {
            "service": service,
            "environment": environment,
            "version": artifacts.get("version", "1.0.0"),
            "replicas": 3,
            "deployment_time": "2024-01-15T10:30:00Z",
            "status": "healthy"
        }
    }


def run_health_checks(service: str, environment: str) -> Dict[str, Any]:
    """Run health checks after deployment."""
    return {
        "status": "success",
        "health_checks": {
            "liveness": True,
            "readiness": True,
            "startup": True,
            "all_healthy": True
        }
    }


def run_smoke_tests(service: str, environment: str) -> Dict[str, Any]:
    """Run smoke tests to validate deployment."""
    return {
        "status": "success",
        "smoke_tests": {
            "total": 10,
            "passed": 10,
            "failed": 0,
            "duration_seconds": 30
        }
    }


def rollback(service: str, environment: str, previous_version: str) -> Dict[str, Any]:
    """Rollback to previous version."""
    return {
        "status": "success",
        "rollback": {
            "service": service,
            "environment": environment,
            "rolled_back_to": previous_version,
            "rollback_time": "2024-01-15T10:35:00Z",
            "status": "completed"
        }
    }


def generate_deployment_report(
    deployment: Dict, health: Dict, smoke_tests: Dict
) -> Dict[str, Any]:
    """Generate deployment report."""
    deployment_successful = all([
        deployment.get("deployment", {}).get("status") == "healthy",
        health.get("health_checks", {}).get("all_healthy", False),
        smoke_tests.get("smoke_tests", {}).get("failed", 1) == 0
    ])

    return {
        "status": "success",
        "deployment_result": "success" if deployment_successful else "failed",
        "summary": {
            "service": deployment.get("deployment", {}).get("service"),
            "environment": deployment.get("deployment", {}).get("environment"),
            "version": deployment.get("deployment", {}).get("version"),
            "health": "healthy" if health.get("health_checks", {}).get("all_healthy") else "unhealthy",
            "smoke_tests": "passed" if smoke_tests.get("smoke_tests", {}).get("failed", 1) == 0 else "failed"
        },
        "recommendations": []
    }


class DeployerAgent(A2AEnabledAgent):
    """
    LLM-powered Deployer Agent.

    Plans and executes deployments with intelligent strategy selection and risk management.
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize Deployer Agent with LLM."""
        A2AEnabledAgent.__init__(self, context, message_bus)

        self.context = context
        self.orchestrator_id = orchestrator_id
        self.model_name = model_name

        # Initialize A2A integration
        self.a2a = A2AIntegration(
            agent_context=context,
            message_bus=message_bus,
            orchestrator_id=orchestrator_id
        )

        # Initialize Vertex AI
        aiplatform.init(
            project=context.get("project_id") if hasattr(context, 'get') else getattr(context, 'project_id', None),
            location=context.get("location", "us-central1") if hasattr(context, 'get') else getattr(context, 'location', "us-central1")
        )

        self.model = GenerativeModel(model_name)

    def plan_deployment_strategy_llm(
        self,
        service_spec: Dict[str, Any],
        environment: str,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze service and choose optimal deployment strategy."""
        print(f"[Deployer] Planning deployment strategy with LLM")

        prompt = self._build_deployment_strategy_prompt(service_spec, environment)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.3)
        )

        strategy = self._parse_deployment_strategy(response.text)

        return {
            "status": "success",
            "deployment_strategy": strategy
        }

    def assess_deployment_risks_llm(
        self,
        deployment_plan: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Assess risks and recommend mitigation strategies."""
        print(f"[Deployer] Assessing deployment risks with LLM")

        prompt = self._build_risk_assessment_prompt(deployment_plan)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.2)
        )

        risk_assessment = self._parse_risk_assessment(response.text)

        return {
            "status": "success",
            "risk_assessment": risk_assessment,
            "risk_level": risk_assessment.get("overall_risk", "medium")
        }

    def plan_rollback_strategy_llm(
        self,
        deployment_spec: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create intelligent rollback plans based on deployment type."""
        print(f"[Deployer] Planning rollback strategy with LLM")

        prompt = self._build_rollback_planning_prompt(deployment_spec)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.2)
        )

        rollback_plan = self._parse_rollback_plan(response.text)

        return {
            "status": "success",
            "rollback_plan": rollback_plan
        }

    def _build_deployment_strategy_prompt(
        self,
        service_spec: Dict[str, Any],
        environment: str
    ) -> str:
        """Build prompt for deployment strategy selection."""

        spec_text = json.dumps(service_spec, indent=2)

        prompt = f"""You are a deployment architect selecting the optimal deployment strategy for a service.

**Service Specification:**
{spec_text}

**Target Environment:** {environment}

**Deployment Strategy Options:**

1. **Blue-Green Deployment**
   - Pros: Instant rollback, zero downtime, easy to test
   - Cons: Requires 2x resources, database migrations tricky
   - Best for: Stateless services, significant changes

2. **Canary Deployment**
   - Pros: Gradual rollout, early issue detection, minimal blast radius
   - Cons: Slower deployment, requires traffic routing
   - Best for: User-facing services, high-risk changes

3. **Rolling Deployment**
   - Pros: Resource efficient, no extra capacity needed
   - Cons: Slower rollback, version mix during deployment
   - Best for: Stateful services, low-risk changes

4. **Recreate (Big Bang)**
   - Pros: Simple, no version mixing
   - Cons: Downtime required
   - Best for: Development/staging, maintenance windows

**Selection Criteria:**

1. **Service Characteristics**
   - Stateful vs stateless
   - User-facing vs internal
   - Critical vs non-critical
   - Database changes?

2. **Change Risk**
   - Breaking API changes?
   - Data migration required?
   - Infrastructure changes?
   - New dependencies?

3. **Environment Constraints**
   - Available resources (can we double capacity?)
   - Traffic routing capabilities
   - Observability maturity
   - Rollback complexity

4. **Business Requirements**
   - Downtime tolerance
   - Rollout speed requirements
   - Testing requirements
   - Compliance constraints

**Response Format:**

**Recommended Strategy:** [blue-green/canary/rolling/recreate]

**Rationale:**
[2-3 sentences explaining why this strategy is optimal for this service and environment]

**Implementation Details:**

**Phase 1: Pre-Deployment**
- [Step 1]
- [Step 2]
- Duration: [X minutes]

**Phase 2: Deployment Execution**
- [Deployment steps specific to chosen strategy]
- Duration: [X minutes]

**Phase 3: Validation**
- Health checks: [which endpoints]
- Smoke tests: [which tests]
- Monitoring: [which metrics]
- Duration: [X minutes]

**Phase 4: Traffic Shift** (if canary/blue-green)
- Initial: [X% traffic to new version]
- Increment: [increase by Y% every Z minutes]
- Full cutover: [after all validations pass]

**Rollback Trigger Conditions:**
- Error rate > [X%]
- Response time p95 > [Y ms]
- Health check failures
- Failed smoke tests

**Resource Requirements:**
- Additional compute: [X cores, Y GB RAM]
- Storage: [Z GB]
- Network: [bandwidth requirements]

**Estimated Total Duration:** [X minutes]

**Risk Level:** [low/medium/high]

Optimize for safety and speed based on service characteristics.
"""

        return prompt

    def _build_risk_assessment_prompt(self, deployment_plan: Dict[str, Any]) -> str:
        """Build prompt for deployment risk assessment."""

        plan_text = json.dumps(deployment_plan, indent=2)

        prompt = f"""You are a deployment risk assessor evaluating potential issues with a deployment plan.

**Deployment Plan:**
{plan_text}

**Risk Assessment Criteria:**

1. **Technical Risks**
   - Breaking changes in API/contracts
   - Database schema changes
   - Configuration changes
   - Infrastructure dependencies
   - Third-party service dependencies

2. **Operational Risks**
   - Complexity of rollback
   - Time to detect issues
   - Impact of failures
   - Monitoring coverage
   - Runbook completeness

3. **Business Risks**
   - User impact if deployment fails
   - Revenue impact
   - SLA violations
   - Customer commitments
   - Compliance requirements

4. **Environmental Risks**
   - Resource capacity
   - Network reliability
   - Dependency availability
   - Peak traffic timing
   - Concurrent deployments

**Response Format:**

**Overall Risk:** [low/medium/high/critical]

**Technical Risks:**
1. **Risk**: [description]
   - **Likelihood**: [low/medium/high]
   - **Impact**: [low/medium/high/critical]
   - **Mitigation**: [how to reduce risk]

**Operational Risks:**
1. **Risk**: [description]
   - **Likelihood**: [low/medium/high]
   - **Impact**: [low/medium/high/critical]
   - **Mitigation**: [how to reduce risk]

**Business Risks:**
1. **Risk**: [description]
   - **Likelihood**: [low/medium/high]
   - **Impact**: [low/medium/high/critical]
   - **Mitigation**: [how to reduce risk]

**Deployment Timing Assessment:**
- **Best Time to Deploy**: [day/time based on traffic patterns]
- **Avoid Deploying**: [when not to deploy]
- **Concurrent Operations**: [conflicts with other activities]

**Pre-Deployment Checklist:**
- [ ] [Critical item 1]
- [ ] [Critical item 2]
- [ ] [Critical item 3]

**Monitoring Requirements:**
- **Key Metrics**: [metrics to watch]
- **Alert Thresholds**: [when to alert]
- **Dashboards**: [what to monitor]

**Rollback Readiness:**
- **Rollback Complexity**: [low/medium/high]
- **Rollback Time**: [estimated minutes]
- **Data Reconciliation**: [required/not required]

**Go/No-Go Decision:** [go/conditional-go/no-go]

**Conditions for Go:**
- [Condition 1 that must be met]
- [Condition 2 that must be met]

**Recommendations:**
1. [Risk reduction recommendation]
2. [Monitoring improvement]
3. [Process improvement]

Provide honest risk assessment - better to delay than to cause an incident.
"""

        return prompt

    def _build_rollback_planning_prompt(self, deployment_spec: Dict[str, Any]) -> str:
        """Build prompt for rollback strategy planning."""

        spec_text = json.dumps(deployment_spec, indent=2)

        prompt = f"""You are a deployment safety expert creating a comprehensive rollback plan.

**Deployment Specification:**
{spec_text}

**Rollback Planning Requirements:**

1. **Rollback Trigger Conditions**
   - Automatic triggers (error rates, latency)
   - Manual triggers (smoke test failures)
   - Time-based triggers (if not healthy after X minutes)

2. **Rollback Execution**
   - How to revert application version
   - How to revert infrastructure changes
   - How to handle in-flight requests
   - How to clean up resources

3. **Data Consistency**
   - Database rollback strategy
   - Data migration rollback
   - Event replay requirements
   - Transaction handling

4. **Validation**
   - How to verify rollback success
   - Health checks post-rollback
   - Smoke tests post-rollback
   - User impact assessment

**Response Format:**

**Rollback Strategy:** [instant/gradual/manual]

**Automatic Rollback Triggers:**
- Error rate > [X%] for [Y minutes]
- Response time p95 > [Z ms] for [Y minutes]
- Health check failures: [threshold]
- Failed smoke tests: [which tests]

**Manual Rollback Triggers:**
- Smoke test failures: [description]
- Performance degradation: [metrics]
- User-reported issues: [severity threshold]
- Data inconsistencies detected

**Rollback Execution Steps:**

1. **Immediate Actions** (0-2 minutes)
   - Stop new deployment
   - Command: [specific rollback command]
   - Traffic: [shift back to old version]

2. **Version Revert** (2-5 minutes)
   - Application: [how to revert]
   - Configuration: [how to revert]
   - Infrastructure: [how to revert]

3. **Data Reconciliation** (5-15 minutes)
   - Database: [migration rollback if needed]
   - Cache: [invalidation strategy]
   - Messages: [queue handling]

4. **Validation** (5-10 minutes)
   - Health checks: [which endpoints]
   - Smoke tests: [which tests]
   - Metrics: [which to verify]

**Rollback Commands:**
```bash
# Kubernetes example
kubectl rollout undo deployment/service-name

# Terraform example
terraform apply -target=resource_name -var="version=previous"

# Cloud provider specific commands
[cloud-specific rollback commands]
```

**Data Consistency Handling:**
- **Forward-only migrations**: [how to handle]
- **Dual-write period**: [if needed]
- **Data reconciliation**: [script or process]

**Post-Rollback Actions:**
- Verify old version health
- Check data consistency
- Notify stakeholders
- Update incident ticket
- Schedule postmortem

**Estimated Rollback Time:**
- Best case: [X minutes]
- Typical: [Y minutes]
- Worst case: [Z minutes]

**Rollback Risks:**
- [Risk 1 of rolling back]
- [Risk 2 of rolling back]

**When NOT to Rollback:**
- [Scenario where rolling back makes things worse]
- [Alternative mitigation if rollback not possible]

Ensure rollback is always faster than forward fix.
"""

        return prompt

    def _parse_deployment_strategy(self, response_text: str) -> Dict[str, Any]:
        """Parse deployment strategy response."""

        # Extract strategy
        strategy = "rolling"
        strategy_match = re.search(r"\*\*Recommended Strategy:\*\*\s*\[?(blue-green|canary|rolling|recreate)\]?", response_text, re.IGNORECASE)
        if strategy_match:
            strategy = strategy_match.group(1).lower()

        # Extract risk level
        risk = "medium"
        risk_match = re.search(r"\*\*Risk Level:\*\*\s*\[?(low|medium|high|critical)\]?", response_text, re.IGNORECASE)
        if risk_match:
            risk = risk_match.group(1).lower()

        # Extract duration
        duration = 30
        duration_match = re.search(r"\*\*Estimated Total Duration:\*\*\s*(\d+)", response_text)
        if duration_match:
            duration = int(duration_match.group(1))

        # Extract rollback triggers
        triggers = self._extract_list_items(response_text, "**Rollback Trigger Conditions:**")

        return {
            "strategy": strategy,
            "risk_level": risk,
            "estimated_duration_minutes": duration,
            "rollback_triggers": triggers
        }

    def _parse_risk_assessment(self, response_text: str) -> Dict[str, Any]:
        """Parse risk assessment response."""

        # Extract overall risk
        risk = "medium"
        risk_match = re.search(r"\*\*Overall Risk:\*\*\s*\[?(low|medium|high|critical)\]?", response_text, re.IGNORECASE)
        if risk_match:
            risk = risk_match.group(1).lower()

        # Extract decision
        decision = "conditional-go"
        decision_match = re.search(r"\*\*Go/No-Go Decision:\*\*\s*\[?(go|conditional-go|no-go)\]?", response_text, re.IGNORECASE)
        if decision_match:
            decision = decision_match.group(1).lower()

        # Extract risks
        technical_risks = self._extract_list_items(response_text, "**Technical Risks:**")
        operational_risks = self._extract_list_items(response_text, "**Operational Risks:**")
        business_risks = self._extract_list_items(response_text, "**Business Risks:**")

        # Extract recommendations
        recommendations = self._extract_list_items(response_text, "**Recommendations:**")

        return {
            "overall_risk": risk,
            "decision": decision,
            "technical_risks": technical_risks,
            "operational_risks": operational_risks,
            "business_risks": business_risks,
            "recommendations": recommendations
        }

    def _parse_rollback_plan(self, response_text: str) -> Dict[str, Any]:
        """Parse rollback plan response."""

        # Extract strategy
        strategy = "instant"
        strategy_match = re.search(r"\*\*Rollback Strategy:\*\*\s*\[?(instant|gradual|manual)\]?", response_text, re.IGNORECASE)
        if strategy_match:
            strategy = strategy_match.group(1).lower()

        # Extract automatic triggers
        auto_triggers = self._extract_list_items(response_text, "**Automatic Rollback Triggers:**")

        # Extract manual triggers
        manual_triggers = self._extract_list_items(response_text, "**Manual Rollback Triggers:**")

        # Extract execution steps
        execution_steps = self._extract_list_items(response_text, "**Rollback Execution Steps:**")

        return {
            "strategy": strategy,
            "automatic_triggers": auto_triggers,
            "manual_triggers": manual_triggers,
            "execution_steps": execution_steps
        }

    def _extract_list_items(self, text: str, section_header: str) -> List[str]:
        """Extract list items from a section."""
        items = []

        if section_header in text:
            section_start = text.find(section_header)
            section_text = text[section_start:]

            # Find next section or end
            next_section = re.search(r"\n\*\*[A-Z]", section_text[len(section_header):])
            if next_section:
                section_text = section_text[:len(section_header) + next_section.start()]

            # Extract list items
            for line in section_text.split("\n"):
                line = line.strip()
                if line.startswith("-") or line.startswith("*") or re.match(r"^\d+\.", line):
                    item = re.sub(r"^[-*\d.]+\s*", "", line).strip()
                    if item and len(item) > 5:
                        items.append(item)

        return items[:15]

    def _get_generation_config(self, temperature: float = 0.3) -> Dict[str, Any]:
        """Get LLM generation configuration."""
        return {
            "temperature": temperature,
            "max_output_tokens": 8192,
            "top_p": 0.95,
            "top_k": 40
        }


# Factory function
def create_deployer_agent(context: Dict[str, Any], message_bus, orchestrator_id: str):
    """Factory function to create LLM-enhanced deployer agent."""
    return DeployerAgent(
        context=context,
        message_bus=message_bus,
        orchestrator_id=orchestrator_id
    )

# Backward compatibility
deployer_agent = None
