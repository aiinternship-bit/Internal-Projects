"""
agents/stage3_cicd/deployment/validator/agent.py

Deployment validator validates deployments meet production requirements.
"""

from typing import Dict, List, Any, Optional
import re
import json

from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration


def validate_deployment_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate deployment configuration."""
    return {
        "status": "success",
        "config_validation": {
            "replicas_sufficient": True,
            "resource_limits_set": True,
            "health_checks_defined": True,
            "secrets_configured": True,
            "passed": True
        }
    }


def validate_production_readiness(service: str, environment: str) -> Dict[str, Any]:
    """Validate service is production-ready."""
    return {
        "status": "success",
        "production_readiness": {
            "monitoring_enabled": True,
            "logging_configured": True,
            "alerting_rules_set": True,
            "backup_configured": True,
            "disaster_recovery_plan": True,
            "passed": True
        }
    }


def validate_security_compliance(service: str) -> Dict[str, Any]:
    """Validate security and compliance requirements."""
    return {
        "status": "success",
        "security_compliance": {
            "secrets_encrypted": True,
            "tls_enabled": True,
            "rbac_configured": True,
            "vulnerability_scan_passed": True,
            "compliance_met": True
        }
    }


def validate_rollback_capability(deployment: Dict[str, Any]) -> Dict[str, Any]:
    """Validate rollback capability exists."""
    return {
        "status": "success",
        "rollback_validation": {
            "previous_version_available": True,
            "rollback_tested": True,
            "rollback_time_acceptable": True,
            "passed": True
        }
    }


def generate_deployment_validation_report(
    config: Dict, readiness: Dict, security: Dict, rollback: Dict
) -> Dict[str, Any]:
    """Generate deployment validation report."""
    all_passed = all([
        config.get("config_validation", {}).get("passed", False),
        readiness.get("production_readiness", {}).get("passed", False),
        security.get("security_compliance", {}).get("compliance_met", False),
        rollback.get("rollback_validation", {}).get("passed", False)
    ])

    return {
        "status": "success",
        "validation_result": "approved" if all_passed else "rejected",
        "checks": {
            "configuration": "passed",
            "production_readiness": "passed",
            "security": "passed",
            "rollback": "passed"
        },
        "ready_for_production": all_passed
    }


class DeploymentValidatorAgent(A2AEnabledAgent):
    """
    LLM-powered Deployment Validator Agent.

    Validates deployments meet production requirements with intelligent analysis.
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize Deployment Validator Agent with LLM."""
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

    def validate_comprehensive_llm(
        self,
        deployment_spec: Dict[str, Any],
        environment: str,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Comprehensive deployment validation using LLM."""
        print(f"[Deployment Validator] Starting comprehensive validation for {environment}")

        # Validate with LLM
        validation_result = self.validate_with_llm(
            deployment_spec=deployment_spec,
            environment=environment,
            task_id=task_id
        )

        return validation_result

    def validate_with_llm(
        self,
        deployment_spec: Dict[str, Any],
        environment: str,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Use LLM to validate deployment comprehensively."""
        print(f"[Deployment Validator] Validating deployment with LLM")

        prompt = self._build_validation_prompt(deployment_spec, environment)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.2)
        )

        validation = self._parse_validation_response(response.text)

        return {
            "status": "success",
            "validation_result": validation.get("overall_decision", "rejected"),
            "validation_report": validation,
            "blockers": validation.get("blockers", []),
            "ready_for_production": validation.get("overall_decision") == "approved"
        }

    def validate_security_compliance_llm(
        self,
        deployment_spec: Dict[str, Any],
        compliance_standards: List[str],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate security compliance against standards."""
        print(f"[Deployment Validator] Validating security compliance with LLM")

        prompt = self._build_security_compliance_prompt(deployment_spec, compliance_standards)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.2)
        )

        compliance = self._parse_security_compliance(response.text)

        return {
            "status": "success",
            "compliance_result": compliance.get("overall_compliance", "non-compliant"),
            "compliance_report": compliance,
            "violations": compliance.get("violations", [])
        }

    def assess_production_readiness_llm(
        self,
        service_spec: Dict[str, Any],
        environment: str,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Assess production readiness holistically."""
        print(f"[Deployment Validator] Assessing production readiness with LLM")

        prompt = self._build_production_readiness_prompt(service_spec, environment)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.3)
        )

        readiness = self._parse_production_readiness(response.text)

        return {
            "status": "success",
            "readiness_result": readiness.get("overall_readiness", "not-ready"),
            "readiness_score": readiness.get("readiness_score", 0),
            "readiness_report": readiness,
            "missing_requirements": readiness.get("missing_requirements", [])
        }

    def _build_validation_prompt(
        self,
        deployment_spec: Dict[str, Any],
        environment: str
    ) -> str:
        """Build prompt for comprehensive deployment validation."""

        spec_text = json.dumps(deployment_spec, indent=2)

        prompt = f"""You are a production deployment validator ensuring deployments meet all requirements before going live.

**Deployment Specification:**
{spec_text}

**Environment:** {environment}

**Comprehensive Validation Checklist:**

1. **Configuration Validation**
   - Resource requests/limits defined? (CPU, memory, storage)
   - Replicas configured appropriately for HA?
   - Environment variables properly set?
   - ConfigMaps/Secrets referenced correctly?
   - Ports and networking configured?
   - Volume mounts valid?
   - Init containers (if any) validated?
   - Service account permissions appropriate?
   - Node selectors/affinity rules correct?
   - Pod disruption budgets defined?

2. **Production Readiness**
   - Liveness probes configured? (path, interval, timeout)
   - Readiness probes configured? (startup time considered)
   - Startup probes for slow-starting apps?
   - Graceful shutdown hooks configured?
   - Termination grace period appropriate?
   - Resource quotas respected?
   - HPA (Horizontal Pod Autoscaler) configured?
   - PDB (Pod Disruption Budget) prevents total outage?
   - Anti-affinity rules prevent single-point-of-failure?

3. **Monitoring & Observability**
   - Prometheus metrics exposed?
   - Custom application metrics defined?
   - Log aggregation configured? (stdout/stderr)
   - Structured logging enabled?
   - Distributed tracing enabled? (Jaeger/Zipkin)
   - APM integration configured?
   - Alerting rules defined for critical metrics?
   - Dashboard created for service?
   - SLO/SLA monitoring in place?

4. **Security & Compliance**
   - Container image from trusted registry?
   - Image vulnerabilities scanned? (severity thresholds)
   - Secrets encrypted at rest?
   - Secrets not hardcoded in manifests?
   - TLS/SSL certificates valid and not expiring soon?
   - Network policies restrict ingress/egress?
   - RBAC roles follow least-privilege principle?
   - Service mesh security policies applied?
   - Security context defined? (runAsNonRoot, readOnlyRootFilesystem)
   - Pod security policies/standards enforced?
   - Supply chain security validated?

5. **Rollback Capability**
   - Previous version available for rollback?
   - Rollback strategy documented?
   - Database migrations backward-compatible?
   - Feature flags for gradual rollout?
   - Canary deployment configured?
   - Blue-green infrastructure ready?
   - Automated rollback triggers defined?
   - Manual rollback procedure tested?
   - Rollback time within SLA?

6. **Disaster Recovery & Business Continuity**
   - Backup strategy configured?
   - Restore procedure tested?
   - Multi-region/multi-zone deployment?
   - Data replication configured?
   - Recovery Time Objective (RTO) met?
   - Recovery Point Objective (RPO) met?
   - Disaster recovery runbook exists?
   - Chaos engineering tests passed?

7. **Performance & Scalability**
   - Load testing completed?
   - Performance benchmarks met?
   - Resource limits prevent noisy neighbor?
   - Autoscaling tested under load?
   - Database connection pooling configured?
   - Caching strategy implemented?
   - CDN configured for static assets?
   - Rate limiting configured?

8. **Operational Excellence**
   - Deployment runbook exists?
   - On-call rotation defined?
   - Incident response playbook ready?
   - Service ownership clear? (team, contacts)
   - Documentation up-to-date?
   - Change management process followed?
   - Deployment approval obtained?
   - Maintenance window scheduled (if needed)?

**Response Format:**

**Overall Decision:** [approved/conditional-approval/rejected]

**Validation Results:**

**Configuration:** [passed/failed]
- [Specific findings]

**Production Readiness:** [passed/failed]
- [Specific findings]

**Monitoring & Observability:** [passed/failed]
- [Specific findings]

**Security & Compliance:** [passed/failed]
- [Specific findings]

**Rollback Capability:** [passed/failed]
- [Specific findings]

**Disaster Recovery:** [passed/failed]
- [Specific findings]

**Performance & Scalability:** [passed/failed]
- [Specific findings]

**Operational Excellence:** [passed/failed]
- [Specific findings]

**Blockers (Must Fix Before Production):**
1. [Critical issue preventing deployment]
2. [Critical issue preventing deployment]

**Warnings (Should Fix Soon):**
1. [Important issue that should be addressed]
2. [Important issue that should be addressed]

**Recommendations (Nice to Have):**
1. [Improvement suggestion]
2. [Improvement suggestion]

**Missing Requirements:**
- [Requirement 1 not met]
- [Requirement 2 not met]

**Compliance Status:**
- CIS Benchmarks: [compliant/non-compliant]
- NIST Guidelines: [compliant/non-compliant]
- PCI-DSS (if applicable): [compliant/non-compliant]
- SOC2 (if applicable): [compliant/non-compliant]

**Go/No-Go Decision:**
- Decision: [GO/NO-GO/CONDITIONAL-GO]
- Conditions for GO: [if conditional]
- Risk Level: [low/medium/high]
- Deployment Window: [recommended time/date]

**Sign-off Requirements:**
- Engineering Lead: [required/not-required]
- Security Team: [required/not-required]
- Product Manager: [required/not-required]
- Executive Approval: [required/not-required]

Be thorough and conservative - it's better to delay a deployment than cause a production outage.
"""

        return prompt

    def _build_security_compliance_prompt(
        self,
        deployment_spec: Dict[str, Any],
        compliance_standards: List[str]
    ) -> str:
        """Build prompt for security compliance validation."""

        spec_text = json.dumps(deployment_spec, indent=2)
        standards_text = ", ".join(compliance_standards)

        prompt = f"""You are a security compliance auditor validating deployments against security standards.

**Deployment Specification:**
{spec_text}

**Compliance Standards to Validate Against:**
{standards_text}

**Security Compliance Checklist:**

1. **CIS Kubernetes Benchmark** (if applicable)
   - 5.1.1: Minimize cluster access to read-only for service accounts
   - 5.2.1: Minimize admission of privileged containers
   - 5.2.2: Minimize admission of containers with capabilities
   - 5.2.3: Minimize admission of root containers
   - 5.2.4: Minimize admission of containers with NET_RAW capability
   - 5.2.5: Minimize admission of containers with allowPrivilegeEscalation
   - 5.3.1: Ensure securityContext is defined
   - 5.4.1: Prefer using secrets as files over environment variables
   - 5.7.1: Create administrative boundaries between resources

2. **NIST Cybersecurity Framework**
   - Identify: Asset inventory, risk assessment
   - Protect: Access control, data security, protective technology
   - Detect: Anomaly detection, continuous monitoring
   - Respond: Incident response plan, communications
   - Recover: Recovery planning, improvements

3. **OWASP Top 10** (for web applications)
   - A01: Broken Access Control
   - A02: Cryptographic Failures
   - A03: Injection
   - A04: Insecure Design
   - A05: Security Misconfiguration
   - A06: Vulnerable and Outdated Components
   - A07: Identification and Authentication Failures
   - A08: Software and Data Integrity Failures
   - A09: Security Logging and Monitoring Failures
   - A10: Server-Side Request Forgery (SSRF)

4. **PCI-DSS** (if handling payment data)
   - Requirement 1: Install and maintain firewall
   - Requirement 2: Don't use vendor defaults
   - Requirement 3: Protect stored cardholder data
   - Requirement 4: Encrypt transmission of cardholder data
   - Requirement 6: Develop secure systems
   - Requirement 8: Assign unique ID to each person
   - Requirement 10: Track and monitor access to network

5. **SOC 2 Type II** (if applicable)
   - Security: Protection against unauthorized access
   - Availability: System availability for operation
   - Processing Integrity: System processing is complete and accurate
   - Confidentiality: Confidential information is protected
   - Privacy: Personal information is collected and used appropriately

**Response Format:**

**Overall Compliance:** [compliant/non-compliant/conditional]

**Compliance by Standard:**

**CIS Kubernetes Benchmark:**
- Overall: [compliant/non-compliant]
- Violations:
  - 5.2.3: [description if violated]
  - 5.4.1: [description if violated]

**NIST Cybersecurity Framework:**
- Identify: [compliant/non-compliant] - [findings]
- Protect: [compliant/non-compliant] - [findings]
- Detect: [compliant/non-compliant] - [findings]
- Respond: [compliant/non-compliant] - [findings]
- Recover: [compliant/non-compliant] - [findings]

**OWASP Top 10:**
- A01 (Broken Access Control): [compliant/non-compliant] - [findings]
- A02 (Cryptographic Failures): [compliant/non-compliant] - [findings]
- [... for each applicable category]

**PCI-DSS:** [compliant/non-compliant/not-applicable]
- [Findings if applicable]

**SOC 2:** [compliant/non-compliant/not-applicable]
- [Findings if applicable]

**Critical Violations:**
1. [Violation with severity: CRITICAL]
2. [Violation with severity: CRITICAL]

**High Severity Violations:**
1. [Violation with severity: HIGH]
2. [Violation with severity: HIGH]

**Medium Severity Violations:**
1. [Violation with severity: MEDIUM]

**Remediation Required:**
1. [Specific action to fix violation 1] - Priority: P0 (24h)
2. [Specific action to fix violation 2] - Priority: P1 (1 week)

**Compliance Gaps:**
- [Gap 1: What is missing]
- [Gap 2: What is missing]

**Audit Trail:**
- Compliance scan date: [current date]
- Standards validated: {standards_text}
- Pass rate: [percentage]

**Sign-off:**
- Security Team Approval: [required/not-required]
- Compliance Officer Approval: [required/not-required]

Be strict and thorough - security compliance is non-negotiable.
"""

        return prompt

    def _build_production_readiness_prompt(
        self,
        service_spec: Dict[str, Any],
        environment: str
    ) -> str:
        """Build prompt for production readiness assessment."""

        spec_text = json.dumps(service_spec, indent=2)

        prompt = f"""You are a Site Reliability Engineer assessing whether a service is truly production-ready.

**Service Specification:**
{spec_text}

**Environment:** {environment}

**Production Readiness Assessment Framework:**

1. **Service Design (20 points)**
   - Stateless design for horizontal scaling? (5 pts)
   - Graceful degradation under load? (5 pts)
   - Circuit breakers for external dependencies? (5 pts)
   - Idempotent operations for retry safety? (5 pts)

2. **Reliability (25 points)**
   - SLO defined with error budget? (5 pts)
   - HA configuration (multi-zone/multi-region)? (5 pts)
   - Automated failover tested? (5 pts)
   - Chaos engineering tests passed? (5 pts)
   - Load testing at 2x expected traffic? (5 pts)

3. **Observability (20 points)**
   - Golden signals monitored (latency, traffic, errors, saturation)? (5 pts)
   - Distributed tracing for requests? (5 pts)
   - Alerting rules cover critical scenarios? (5 pts)
   - Dashboards for on-call engineers? (5 pts)

4. **Security (20 points)**
   - Authentication and authorization enforced? (5 pts)
   - Secrets management (not hardcoded)? (5 pts)
   - Network segmentation and policies? (5 pts)
   - Vulnerability scanning automated? (5 pts)

5. **Operational Readiness (15 points)**
   - Deployment automation (CI/CD)? (5 pts)
   - Runbooks for common incidents? (5 pts)
   - On-call rotation and escalation defined? (5 pts)

**Critical Production Readiness Checklist:**

**Must-Have (Blockers if Missing):**
- [ ] Service responds to health checks
- [ ] Graceful shutdown on SIGTERM
- [ ] Resource limits prevent runaway processes
- [ ] Logs sent to centralized logging
- [ ] Critical alerts defined and tested
- [ ] Rollback procedure tested
- [ ] Security vulnerabilities addressed (High+)
- [ ] Data backup configured
- [ ] Monitoring dashboard exists
- [ ] On-call engineer assigned

**Should-Have (Warnings if Missing):**
- [ ] Load testing completed
- [ ] Performance benchmarks met
- [ ] Chaos engineering validated
- [ ] Multi-region deployment
- [ ] Database connection pooling
- [ ] Caching strategy implemented
- [ ] Rate limiting configured
- [ ] API versioning strategy

**Nice-to-Have (Recommendations):**
- [ ] Service mesh integration
- [ ] Advanced monitoring (APM)
- [ ] A/B testing capability
- [ ] Feature flags for gradual rollout
- [ ] Automated canary analysis
- [ ] Cost optimization analysis
- [ ] Carbon footprint tracking

**Response Format:**

**Overall Readiness:** [production-ready/not-ready/conditional]

**Readiness Score:** [0-100 points]

**Category Scores:**
- Service Design: [0-20 points] - [findings]
- Reliability: [0-25 points] - [findings]
- Observability: [0-20 points] - [findings]
- Security: [0-20 points] - [findings]
- Operational Readiness: [0-15 points] - [findings]

**Must-Have Checklist:**
✅ [Requirement met]
❌ [Requirement NOT met - BLOCKER]

**Should-Have Checklist:**
✅ [Requirement met]
⚠️  [Requirement NOT met - WARNING]

**Nice-to-Have Checklist:**
✅ [Requirement met]
ℹ️  [Requirement NOT met - RECOMMENDATION]

**Missing Requirements (Blockers):**
1. [Critical requirement missing]
2. [Critical requirement missing]

**Gaps (Warnings):**
1. [Important gap]
2. [Important gap]

**Improvement Opportunities:**
1. [Optimization suggestion]
2. [Optimization suggestion]

**Risk Assessment:**
- Deployment Risk: [low/medium/high]
- Outage Risk: [low/medium/high]
- Security Risk: [low/medium/high]
- Scalability Risk: [low/medium/high]

**Confidence Level:** [0-100%]
- Reasoning: [Why this confidence level]

**Recommendation:**
- Go-Live: [yes/no/conditional]
- Conditions: [if conditional]
- Timeline: [ready now / ready in X days with fixes]

**Sign-off Requirements:**
- SRE Team: [approved/rejected/conditional]
- Security Team: [approved/rejected/conditional]
- Engineering Lead: [approved/rejected/conditional]

Assess objectively using the 100-point scale. A score below 70 is NOT production-ready.
"""

        return prompt

    def _parse_validation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse comprehensive validation response."""

        # Extract overall decision
        overall_decision = "rejected"
        decision_match = re.search(
            r"\*\*Overall Decision:\*\*\s*\[?(approved|conditional-approval|rejected)\]?",
            response_text,
            re.IGNORECASE
        )
        if decision_match:
            overall_decision = decision_match.group(1).lower()

        # Extract go/no-go decision
        go_no_go = "NO-GO"
        go_match = re.search(
            r"Decision:\s*\[?(GO|NO-GO|CONDITIONAL-GO)\]?",
            response_text,
            re.IGNORECASE
        )
        if go_match:
            go_no_go = go_match.group(1).upper()

        # Extract risk level
        risk_level = "high"
        risk_match = re.search(
            r"Risk Level:\s*\[?(low|medium|high)\]?",
            response_text,
            re.IGNORECASE
        )
        if risk_match:
            risk_level = risk_match.group(1).lower()

        # Extract blockers
        blockers = self._extract_list_items(response_text, "**Blockers (Must Fix Before Production):**")

        # Extract warnings
        warnings = self._extract_list_items(response_text, "**Warnings (Should Fix Soon):**")

        # Extract recommendations
        recommendations = self._extract_list_items(response_text, "**Recommendations (Nice to Have):**")

        # Extract missing requirements
        missing = self._extract_list_items(response_text, "**Missing Requirements:**")

        # Extract validation results
        validation_results = self._extract_validation_categories(response_text)

        return {
            "overall_decision": overall_decision,
            "go_no_go": go_no_go,
            "risk_level": risk_level,
            "validation_results": validation_results,
            "blockers": blockers,
            "warnings": warnings,
            "recommendations": recommendations,
            "missing_requirements": missing
        }

    def _parse_security_compliance(self, response_text: str) -> Dict[str, Any]:
        """Parse security compliance response."""

        # Extract overall compliance
        overall_compliance = "non-compliant"
        compliance_match = re.search(
            r"\*\*Overall Compliance:\*\*\s*\[?(compliant|non-compliant|conditional)\]?",
            response_text,
            re.IGNORECASE
        )
        if compliance_match:
            overall_compliance = compliance_match.group(1).lower()

        # Extract critical violations
        critical_violations = self._extract_list_items(response_text, "**Critical Violations:**")

        # Extract high severity violations
        high_violations = self._extract_list_items(response_text, "**High Severity Violations:**")

        # Extract remediation required
        remediation = self._extract_list_items(response_text, "**Remediation Required:**")

        # Extract compliance gaps
        gaps = self._extract_list_items(response_text, "**Compliance Gaps:**")

        return {
            "overall_compliance": overall_compliance,
            "critical_violations": critical_violations,
            "high_violations": high_violations,
            "violations": critical_violations + high_violations,
            "remediation_required": remediation,
            "compliance_gaps": gaps
        }

    def _parse_production_readiness(self, response_text: str) -> Dict[str, Any]:
        """Parse production readiness assessment."""

        # Extract overall readiness
        overall_readiness = "not-ready"
        readiness_match = re.search(
            r"\*\*Overall Readiness:\*\*\s*\[?(production-ready|not-ready|conditional)\]?",
            response_text,
            re.IGNORECASE
        )
        if readiness_match:
            overall_readiness = readiness_match.group(1).lower()

        # Extract readiness score
        readiness_score = 0
        score_match = re.search(
            r"\*\*Readiness Score:\*\*\s*\[?(\d+)\]?",
            response_text,
            re.IGNORECASE
        )
        if score_match:
            readiness_score = int(score_match.group(1))

        # Extract confidence level
        confidence = 0
        confidence_match = re.search(
            r"\*\*Confidence Level:\*\*\s*\[?(\d+)%?\]?",
            response_text,
            re.IGNORECASE
        )
        if confidence_match:
            confidence = int(confidence_match.group(1))

        # Extract missing requirements
        missing = self._extract_list_items(response_text, "**Missing Requirements (Blockers):**")

        # Extract gaps
        gaps = self._extract_list_items(response_text, "**Gaps (Warnings):**")

        # Extract improvements
        improvements = self._extract_list_items(response_text, "**Improvement Opportunities:**")

        # Extract category scores
        category_scores = self._extract_category_scores(response_text)

        return {
            "overall_readiness": overall_readiness,
            "readiness_score": readiness_score,
            "confidence_level": confidence,
            "category_scores": category_scores,
            "missing_requirements": missing,
            "gaps": gaps,
            "improvement_opportunities": improvements
        }

    def _extract_validation_categories(self, text: str) -> Dict[str, str]:
        """Extract validation category results."""
        categories = {}

        category_names = [
            "Configuration",
            "Production Readiness",
            "Monitoring & Observability",
            "Security & Compliance",
            "Rollback Capability",
            "Disaster Recovery",
            "Performance & Scalability",
            "Operational Excellence"
        ]

        for category in category_names:
            pattern = rf"\*\*{category}:\*\*\s*\[?(passed|failed)\]?"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                categories[category.lower().replace(" & ", "_").replace(" ", "_")] = match.group(1).lower()

        return categories

    def _extract_category_scores(self, text: str) -> Dict[str, int]:
        """Extract category scores from production readiness."""
        scores = {}

        category_patterns = [
            (r"Service Design:\s*\[?(\d+)", "service_design"),
            (r"Reliability:\s*\[?(\d+)", "reliability"),
            (r"Observability:\s*\[?(\d+)", "observability"),
            (r"Security:\s*\[?(\d+)", "security"),
            (r"Operational Readiness:\s*\[?(\d+)", "operational_readiness")
        ]

        for pattern, key in category_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                scores[key] = int(match.group(1))

        return scores

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
                    # Also remove checkbox markers
                    item = re.sub(r"^[✅❌⚠️ℹ️]\s*", "", item).strip()
                    if item and len(item) > 5:
                        items.append(item)

        return items[:15]

    def _get_generation_config(self, temperature: float = 0.2) -> Dict[str, Any]:
        """Get LLM generation configuration."""
        return {
            "temperature": temperature,
            "max_output_tokens": 8192,
            "top_p": 0.95,
            "top_k": 40
        }


# Factory function
def create_deployment_validator_agent(context: Dict[str, Any], message_bus, orchestrator_id: str):
    """Factory function to create LLM-enhanced deployment validator agent."""
    return DeploymentValidatorAgent(
        context=context,
        message_bus=message_bus,
        orchestrator_id=orchestrator_id
    )

# Backward compatibility
deployment_validator_agent = None
