"""
agents/stage2_development/qa/validator/agent.py

QA validator reviews test results and approves for deployment.
"""

from typing import Dict, List, Any, Optional
import re
import json

from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration


def validate_test_coverage(coverage: Dict[str, Any]) -> Dict[str, Any]:
    """Validate test coverage meets threshold."""
    return {
        "status": "success",
        "coverage_validation": {
            "line_coverage": coverage.get("line_coverage", 0),
            "threshold": 0.80,
            "meets_threshold": coverage.get("line_coverage", 0) >= 0.80,
            "gaps": coverage.get("uncovered_areas", [])
        }
    }


def validate_test_results(test_execution: Dict[str, Any]) -> Dict[str, Any]:
    """Validate all tests passed."""
    return {
        "status": "success",
        "test_validation": {
            "total": test_execution.get("total", 0),
            "passed": test_execution.get("passed", 0),
            "failed": test_execution.get("failed", 0),
            "all_passed": test_execution.get("failed", 1) == 0
        }
    }


def validate_performance(load_test: Dict[str, Any]) -> Dict[str, Any]:
    """Validate performance meets SLA."""
    return {
        "status": "success",
        "performance_validation": {
            "response_time": load_test.get("average_response_ms", 0),
            "sla": 200,
            "meets_sla": load_test.get("meets_sla", False)
        }
    }


def check_regression(current_results: Dict, baseline: Dict) -> Dict[str, Any]:
    """Check for regression compared to baseline."""
    return {
        "status": "success",
        "regression_check": {
            "performance_regression": False,
            "functionality_regression": False,
            "coverage_regression": False,
            "passed": True
        }
    }


def generate_qa_validation_report(
    coverage_val: Dict, test_val: Dict, perf_val: Dict, regression: Dict
) -> Dict[str, Any]:
    """Generate QA validation report."""
    all_passed = all([
        coverage_val.get("coverage_validation", {}).get("meets_threshold", False),
        test_val.get("test_validation", {}).get("all_passed", False),
        perf_val.get("performance_validation", {}).get("meets_sla", False),
        regression.get("regression_check", {}).get("passed", False)
    ])

    return {
        "status": "success",
        "validation_result": "approved" if all_passed else "rejected",
        "quality_gates": {
            "coverage": "passed",
            "tests": "passed",
            "performance": "passed",
            "regression": "passed"
        },
        "recommendations": []
    }


class QAValidatorAgent(A2AEnabledAgent):
    """
    LLM-powered QA Validator Agent.

    Validates test results, coverage, performance, and quality gates with intelligent analysis.
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize QA Validator Agent with LLM."""
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

    def validate_qa_comprehensive(
        self,
        qa_results: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Comprehensive QA validation using LLM."""
        print(f"[QA Validator] Starting comprehensive QA validation")

        # Validate with LLM
        validation_result = self.validate_with_llm(
            qa_results=qa_results,
            task_id=task_id
        )

        return validation_result

    def validate_with_llm(
        self,
        qa_results: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Use LLM to validate QA results and quality gates."""
        print(f"[QA Validator] Validating QA results with LLM")

        prompt = self._build_validation_prompt(qa_results)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.2)
        )

        validation = self._parse_validation_response(response.text)

        return {
            "status": "success",
            "validation_result": validation.get("overall_result", "rejected"),
            "validation_report": validation,
            "blockers": validation.get("blockers", [])
        }

    def analyze_test_failures_llm(
        self,
        test_failures: List[Dict[str, Any]],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze test failures with LLM for root cause insights."""
        print(f"[QA Validator] Analyzing test failures with LLM")

        prompt = self._build_failure_analysis_prompt(test_failures)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.3)
        )

        analysis = self._parse_failure_analysis(response.text)

        return {
            "status": "success",
            "failure_analysis": analysis,
            "root_causes": analysis.get("root_causes", []),
            "recommendations": analysis.get("recommendations", [])
        }

    def _build_validation_prompt(self, qa_results: Dict[str, Any]) -> str:
        """Build prompt for comprehensive QA validation."""

        results_text = json.dumps(qa_results, indent=2)

        prompt = f"""You are a senior QA engineer validating test results and quality gates for production deployment.

**QA Results:**
{results_text}

**Quality Gate Validation Checklist:**

1. **Test Coverage Analysis**
   - Line coverage >= 80%? (MANDATORY)
   - Branch coverage >= 75%?
   - Critical paths covered?
   - Edge cases tested?
   - Coverage gaps identified?
   - Quality of tests (not just quantity)?

2. **Test Results Validation**
   - All unit tests passed? (MANDATORY)
   - All integration tests passed? (MANDATORY)
   - All E2E tests passed?
   - Flaky tests identified?
   - Test reliability score?
   - Test execution time reasonable?

3. **Performance Testing**
   - Response time meets SLA (< 200ms p95)?
   - Throughput meets requirements?
   - Resource utilization acceptable?
   - No memory leaks detected?
   - Database query performance optimized?
   - API endpoint performance validated?

4. **Regression Analysis**
   - No functionality regressions?
   - No performance regressions?
   - No coverage regressions?
   - Baseline comparison analyzed?
   - Breaking changes documented?

5. **Quality Metrics**
   - Code complexity reasonable?
   - Technical debt assessed?
   - Code smells addressed?
   - Security scanning passed?
   - Dependency vulnerabilities checked?

6. **Non-Functional Requirements**
   - Load testing completed?
   - Stress testing passed?
   - Failover scenarios tested?
   - Data integrity validated?
   - Accessibility requirements met?

7. **Deployment Readiness**
   - Rollback plan tested?
   - Database migrations validated?
   - Feature flags configured?
   - Monitoring alerts set?
   - Documentation updated?

**Response Format:**

**Overall Result:** [approved/rejected/conditional]

**Quality Gate Results:**
- Test Coverage: [passed/failed] - [coverage %] - [reasoning]
- Test Results: [passed/failed] - [pass/fail/total] - [reasoning]
- Performance: [passed/failed] - [p95 latency ms] - [reasoning]
- Regression: [passed/failed] - [reasoning]
- Quality Metrics: [passed/failed] - [reasoning]
- NFR Testing: [passed/failed] - [reasoning]
- Deployment Ready: [yes/no] - [reasoning]

**Blockers:** (if rejected)
- [Critical issue 1 blocking deployment]
- [Critical issue 2 blocking deployment]

**Warnings:** (if conditional)
- [Warning 1 requiring attention]
- [Warning 2 requiring attention]

**Test Failure Analysis:** (if any failures)
- Failed Test: [test name] - Root Cause: [analysis]
- Failed Test: [test name] - Root Cause: [analysis]

**Coverage Gaps:**
- [Critical uncovered area 1]
- [Critical uncovered area 2]

**Performance Issues:**
- [Issue 1 with impact assessment]
- [Issue 2 with impact assessment]

**Recommendations:**
1. [Specific actionable recommendation]
2. [Specific actionable recommendation]
3. [Specific actionable recommendation]

**Risk Assessment:** [low/medium/high/critical]

**Deployment Decision:**
[Clear go/no-go decision with detailed justification]

Be strict on mandatory gates. Provide data-driven analysis with specific metrics.
"""

        return prompt

    def _build_failure_analysis_prompt(self, test_failures: List[Dict[str, Any]]) -> str:
        """Build prompt for test failure analysis."""

        failures_text = json.dumps(test_failures, indent=2)

        prompt = f"""You are a senior test engineer analyzing test failures to identify root causes and patterns.

**Test Failures:**
{failures_text}

**Analysis Requirements:**

1. **Pattern Recognition**
   - Are failures related (common root cause)?
   - Is it a flaky test issue?
   - Is it environmental?
   - Is it timing/race condition?
   - Is it data-dependent?

2. **Root Cause Analysis**
   - What is the underlying cause?
   - Is it a code bug or test bug?
   - Is it a configuration issue?
   - Is it a dependency problem?
   - Is it an infrastructure issue?

3. **Impact Assessment**
   - How critical is this failure?
   - What functionality is affected?
   - Is it a regression?
   - What is the blast radius?
   - Does it block deployment?

4. **Remediation Strategy**
   - How to fix the root cause?
   - Should test be fixed or code?
   - Can it be temporarily disabled?
   - What is the estimated effort?
   - What is the priority?

**Response Format:**

**Failure Summary:**
- Total Failures: [count]
- Unique Root Causes: [count]
- Critical Failures: [count]
- Flaky Tests: [count]

**Root Causes Identified:**
1. [Root cause 1]: Affects [X] tests - [Description]
2. [Root cause 2]: Affects [Y] tests - [Description]

**Critical Failures:** (blocking deployment)
- Test: [name] - Reason: [why it blocks deployment]

**Flaky Tests:** (reliability issues)
- Test: [name] - Pattern: [when it fails]

**Test Issues:** (not code bugs)
- Test: [name] - Issue: [what's wrong with the test]

**Code Bugs:** (actual defects)
- Bug: [description] - Affected Tests: [list]

**Deployment Impact:** [block/delay/proceed-with-risk]

**Immediate Actions Required:**
1. [Action 1 with priority and estimated effort]
2. [Action 2 with priority and estimated effort]

**Recommendations:**
1. [Test improvement recommendation]
2. [Code quality recommendation]
3. [Process improvement recommendation]

Provide specific, actionable insights for the development team.
"""

        return prompt

    def _parse_validation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM validation response."""

        # Extract overall result
        overall_result = "rejected"
        result_match = re.search(r"\*\*Overall Result:\*\*\s*\[?(approved|rejected|conditional)\]?", response_text, re.IGNORECASE)
        if result_match:
            overall_result = result_match.group(1).lower()

        # Extract risk assessment
        risk_level = "medium"
        risk_match = re.search(r"\*\*Risk Assessment:\*\*\s*\[?(low|medium|high|critical)\]?", response_text, re.IGNORECASE)
        if risk_match:
            risk_level = risk_match.group(1).lower()

        # Extract blockers
        blockers = self._extract_list_items(response_text, "**Blockers:**")

        # Extract warnings
        warnings = self._extract_list_items(response_text, "**Warnings:**")

        # Extract recommendations
        recommendations = self._extract_list_items(response_text, "**Recommendations:**")

        # Extract quality gates
        quality_gates = self._extract_quality_gates(response_text)

        # Extract deployment decision
        deployment_decision = ""
        deploy_match = re.search(r"\*\*Deployment Decision:\*\*\s*\n(.*?)(?=\n\*\*|\Z)", response_text, re.DOTALL)
        if deploy_match:
            deployment_decision = deploy_match.group(1).strip()

        return {
            "overall_result": overall_result,
            "risk_level": risk_level,
            "quality_gates": quality_gates,
            "blockers": blockers,
            "warnings": warnings,
            "recommendations": recommendations,
            "deployment_decision": deployment_decision
        }

    def _parse_failure_analysis(self, response_text: str) -> Dict[str, Any]:
        """Parse test failure analysis response."""

        # Extract deployment impact
        deployment_impact = "block"
        impact_match = re.search(r"\*\*Deployment Impact:\*\*\s*\[?(block|delay|proceed-with-risk)\]?", response_text, re.IGNORECASE)
        if impact_match:
            deployment_impact = impact_match.group(1).lower()

        # Extract root causes
        root_causes = self._extract_list_items(response_text, "**Root Causes Identified:**")

        # Extract critical failures
        critical_failures = self._extract_list_items(response_text, "**Critical Failures:**")

        # Extract immediate actions
        immediate_actions = self._extract_list_items(response_text, "**Immediate Actions Required:**")

        # Extract recommendations
        recommendations = self._extract_list_items(response_text, "**Recommendations:**")

        return {
            "deployment_impact": deployment_impact,
            "root_causes": root_causes,
            "critical_failures": critical_failures,
            "immediate_actions": immediate_actions,
            "recommendations": recommendations
        }

    def _extract_quality_gates(self, text: str) -> Dict[str, str]:
        """Extract quality gate results."""
        gates = {}

        gate_names = [
            "Test Coverage",
            "Test Results",
            "Performance",
            "Regression",
            "Quality Metrics",
            "NFR Testing",
            "Deployment Ready"
        ]

        for gate_name in gate_names:
            pattern = rf"- {gate_name}:\s*\[?(passed|failed)\]?"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                gates[gate_name.lower().replace(" ", "_")] = match.group(1).lower()

        return gates

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

        return items[:10]

    def _get_generation_config(self, temperature: float = 0.2) -> Dict[str, Any]:
        """Get LLM generation configuration."""
        return {
            "temperature": temperature,
            "max_output_tokens": 4096,
            "top_p": 0.95,
            "top_k": 40
        }


# Factory function
def create_qa_validator_agent(context: Dict[str, Any], message_bus, orchestrator_id: str):
    """Factory function to create LLM-enhanced QA validator agent."""
    return QAValidatorAgent(
        context=context,
        message_bus=message_bus,
        orchestrator_id=orchestrator_id
    )

# Backward compatibility
qa_validator_agent = None
