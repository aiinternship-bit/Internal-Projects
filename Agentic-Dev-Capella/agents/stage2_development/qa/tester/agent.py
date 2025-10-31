"""
agents/stage2_development/qa/tester/agent.py

QA tester agent generates test cases and creates test plans using LLM.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re

from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration


class QATesterAgent(A2AEnabledAgent):
    """
    QA Tester Agent for comprehensive testing strategy.

    Capabilities:
    - Generate test cases from specifications
    - Create test plans with coverage analysis
    - Design load/performance tests
    - Generate test reports
    - Recommend testing improvements
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize QA Tester Agent."""
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

        # Test history
        self.test_history: List[Dict[str, Any]] = []

    def handle_task_assignment(self, message: Dict[str, Any]) -> None:
        """Handle TASK_ASSIGNMENT message from orchestrator."""
        payload = message.get("payload", {})
        task_id = payload.get("task_id")
        task_type = payload.get("task_type")
        parameters = payload.get("parameters", {})

        try:
            if task_type == "generate_tests":
                result = self.generate_comprehensive_tests(task_id=task_id, **parameters)
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            # Send completion
            self.a2a.send_completion(
                task_id=task_id,
                artifacts=result,
                metrics={
                    "test_cases_count": result.get("total_cases", 0)
                }
            )

        except Exception as e:
            self.a2a.send_error_report(
                task_id=task_id,
                error_type="TEST_GENERATION_FAILED",
                error_message=str(e),
                stack_trace=""
            )

    def generate_comprehensive_tests(
        self,
        specification: Dict[str, Any],
        code: Optional[str] = None,
        language: str = "python",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive test suite."""
        print(f"[QA Tester] Generating comprehensive test suite")

        # Generate test cases
        test_cases = self.generate_test_cases(specification, language)

        # Analyze what coverage is needed
        coverage_analysis = self.analyze_test_coverage_needs(specification, code, language)

        # Generate test report structure
        report = self.generate_test_plan(test_cases, coverage_analysis, specification)

        return report

    def generate_test_cases(
        self,
        specification: Dict[str, Any],
        language: str = "python"
    ) -> Dict[str, Any]:
        """
        Generate test cases from specification using LLM.

        Args:
            specification: Component specification
            language: Programming language

        Returns:
            dict: Generated test cases with categories
        """
        print(f"[QA Tester] Generating test cases")

        prompt = self._build_test_case_prompt(specification, language)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.4)
        )

        test_cases = self._parse_test_cases(response.text)

        return {
            "status": "success",
            "test_cases": test_cases,
            "total_cases": len(test_cases),
            "coverage": self._categorize_tests(test_cases)
        }

    def analyze_test_coverage_needs(
        self,
        specification: Dict[str, Any],
        code: Optional[str],
        language: str = "python"
    ) -> Dict[str, Any]:
        """Analyze what test coverage is needed using LLM."""
        print(f"[QA Tester] Analyzing coverage needs")

        prompt = self._build_coverage_analysis_prompt(specification, code, language)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.3)
        )

        coverage_needs = self._parse_coverage_analysis(response.text)

        return {
            "status": "success",
            "coverage_needs": coverage_needs
        }

    def run_tests(
        self,
        test_cases: List[Dict[str, Any]],
        environment: str = "test"
    ) -> Dict[str, Any]:
        """Simulate test execution (mock for now)."""
        print(f"[QA Tester] Running {len(test_cases)} tests in {environment}")

        # Mock execution results
        total = len(test_cases)
        passed = int(total * 0.95)  # 95% pass rate
        failed = total - passed

        return {
            "status": "success",
            "test_execution": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "environment": environment,
                "duration_minutes": max(1, total // 3)
            },
            "failed_tests": [
                {"id": f"TC{i:03d}", "reason": "Simulated failure"}
                for i in range(failed)
            ]
        }

    def analyze_coverage(
        self,
        test_results: Dict[str, Any],
        code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze test coverage (mock for now)."""
        print(f"[QA Tester] Analyzing test coverage")

        return {
            "status": "success",
            "coverage": {
                "line_coverage": 0.87,
                "branch_coverage": 0.82,
                "function_coverage": 0.95,
                "meets_threshold": True,
                "uncovered_areas": ["error_recovery:45-67"]
            }
        }

    def run_load_tests(
        self,
        endpoint: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Design load test plan using LLM."""
        print(f"[QA Tester] Designing load test for {endpoint}")

        prompt = self._build_load_test_prompt(endpoint, config)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.3)
        )

        load_test_plan = self._parse_load_test_plan(response.text)

        return {
            "status": "success",
            "load_test_plan": load_test_plan,
            "simulated_results": {
                "requests_per_second": 1200,
                "average_response_ms": 150,
                "p95_response_ms": 280,
                "p99_response_ms": 450,
                "errors": 0,
                "meets_sla": True
            }
        }

    def generate_test_plan(
        self,
        test_cases: Dict[str, Any],
        coverage_analysis: Dict[str, Any],
        specification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive test plan using LLM."""
        print(f"[QA Tester] Generating test plan")

        prompt = self._build_test_plan_prompt(test_cases, coverage_analysis, specification)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.3)
        )

        test_plan = self._parse_test_plan(response.text)

        return {
            "status": "success",
            "test_plan": test_plan,
            "test_cases": test_cases.get("test_cases", []),
            "total_cases": test_cases.get("total_cases", 0),
            "timestamp": datetime.utcnow().isoformat()
        }

    def generate_test_report(
        self,
        test_cases: Dict,
        execution: Dict,
        coverage: Dict,
        load_test: Dict
    ) -> Dict[str, Any]:
        """Generate test report using LLM."""
        print(f"[QA Tester] Generating test report")

        prompt = self._build_test_report_prompt(test_cases, execution, coverage, load_test)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.3)
        )

        report_content = self._parse_test_report(response.text)

        return {
            "status": "success",
            "test_report": {
                "summary": {
                    "total_tests": execution.get("test_execution", {}).get("total", 0),
                    "passed": execution.get("test_execution", {}).get("passed", 0),
                    "failed": execution.get("test_execution", {}).get("failed", 0),
                    "coverage": coverage.get("coverage", {}).get("line_coverage", 0),
                    "performance_sla_met": load_test.get("load_test_plan", {}).get("meets_sla", True)
                },
                "validation_result": report_content.get("validation_result", "approved"),
                "recommendations": report_content.get("recommendations", []),
                "detailed_findings": report_content.get("findings", "")
            }
        }

    # ========================================================================
    # PROMPT BUILDERS
    # ========================================================================

    def _build_test_case_prompt(
        self,
        specification: Dict[str, Any],
        language: str
    ) -> str:
        """Build prompt for test case generation."""

        spec_text = json.dumps(specification, indent=2)

        prompt = f"""You are an expert QA engineer specializing in {language} testing.

Generate comprehensive test cases for the following component:

**Specification:**
{spec_text}

**Test Categories to Cover:**

1. **Functional Tests** (Happy Path)
   - Core functionality works as expected
   - Valid inputs produce correct outputs

2. **Negative Tests** (Error Handling)
   - Invalid inputs are rejected
   - Error messages are appropriate
   - System handles failures gracefully

3. **Edge Cases**
   - Boundary values
   - Null/empty inputs
   - Large data sets
   - Concurrent operations

4. **Integration Tests**
   - Component interactions
   - API contracts
   - Database operations

5. **Security Tests**
   - Input validation
   - Authentication/authorization
   - SQL injection prevention
   - XSS prevention

**For Each Test Case, Provide:**

**Test ID:** TC001
**Name:** [Descriptive test name]
**Type:** [functional/negative/edge_case/integration/security]
**Priority:** [high/medium/low]
**Description:** [What the test validates]
**Steps:**
1. [Action 1]
2. [Action 2]
3. [Expected result]

Generate 10-15 diverse test cases covering all categories.
Be specific and actionable.
"""

        return prompt

    def _build_coverage_analysis_prompt(
        self,
        specification: Dict[str, Any],
        code: Optional[str],
        language: str
    ) -> str:
        """Build prompt for coverage analysis."""

        spec_text = json.dumps(specification, indent=2)
        code_text = code[:2000] if code else "No code provided"

        prompt = f"""You are an expert at test coverage analysis.

Analyze what test coverage is needed for this component:

**Specification:**
{spec_text}

**Code Sample:**
{code_text}

**Analysis Required:**

1. **Critical Paths**: Which code paths must be tested?
2. **Risk Areas**: Where are bugs most likely?
3. **Edge Cases**: What boundary conditions exist?
4. **Coverage Goals**: What coverage percentages are appropriate?
   - Line coverage: [target %]
   - Branch coverage: [target %]
   - Function coverage: [target %]

5. **Uncovered Areas**: What typically gets missed?

**Response Format:**

**Critical Paths:**
- Path 1: [Description]
- Path 2: [Description]

**Risk Areas:**
- Area 1: [Why risky]
- Area 2: [Why risky]

**Coverage Goals:**
- Line Coverage: [%]
- Branch Coverage: [%]

**Recommended Test Priorities:**
1. [High priority area]
2. [Medium priority area]

Be specific about what needs testing and why.
"""

        return prompt

    def _build_load_test_prompt(
        self,
        endpoint: str,
        config: Dict[str, Any]
    ) -> str:
        """Build prompt for load test design."""

        config_text = json.dumps(config, indent=2)

        prompt = f"""You are an expert in performance and load testing.

Design a load test plan for this endpoint:

**Endpoint:** {endpoint}
**Configuration:**
{config_text}

**Load Test Design Should Include:**

1. **Test Scenarios**
   - Normal load scenario
   - Peak load scenario
   - Stress test scenario

2. **Metrics to Measure**
   - Requests per second
   - Response time (avg, p95, p99)
   - Error rate
   - Resource utilization

3. **Success Criteria**
   - What performance is acceptable?
   - What response times meet SLA?
   - What error rate is tolerable?

4. **Test Configuration**
   - Ramp-up period
   - Duration
   - Number of virtual users
   - Think time

**Response Format:**

**Test Scenarios:**
1. **Normal Load**
   - Users: [number]
   - Duration: [minutes]
   - Expected RPS: [number]

**Metrics:**
- Response Time Target: < [ms]
- Error Rate Target: < [%]

**Success Criteria:**
- Criterion 1
- Criterion 2

Provide specific, measurable criteria.
"""

        return prompt

    def _build_test_plan_prompt(
        self,
        test_cases: Dict[str, Any],
        coverage_analysis: Dict[str, Any],
        specification: Dict[str, Any]
    ) -> str:
        """Build prompt for test plan generation."""

        prompt = f"""You are creating a comprehensive test plan.

**Test Cases Generated:** {test_cases.get('total_cases', 0)}
**Coverage Analysis:** {json.dumps(coverage_analysis, indent=2)}

Create a test execution plan that includes:

1. **Test Strategy**
   - Testing approach
   - Test levels (unit, integration, system)
   - Entry and exit criteria

2. **Test Phases**
   - Phase 1: Unit testing
   - Phase 2: Integration testing
   - Phase 3: System testing
   - Phase 4: Performance testing

3. **Resource Requirements**
   - Test environments needed
   - Test data requirements
   - Tools required

4. **Schedule**
   - Estimated duration for each phase
   - Dependencies between phases

5. **Risk Mitigation**
   - Testing risks
   - Mitigation strategies

**Response Format:**

**Test Strategy:**
[2-3 sentences describing approach]

**Test Phases:**
1. **Phase 1**: [Description, duration]
2. **Phase 2**: [Description, duration]

**Resource Requirements:**
- Environments: [list]
- Tools: [list]

**Estimated Timeline:** [Total days]

**Risks:**
- Risk 1: [Mitigation]

Make it practical and executable.
"""

        return prompt

    def _build_test_report_prompt(
        self,
        test_cases: Dict,
        execution: Dict,
        coverage: Dict,
        load_test: Dict
    ) -> str:
        """Build prompt for test report generation."""

        prompt = f"""You are writing a test execution report.

**Test Results:**
- Total Tests: {execution.get('test_execution', {}).get('total', 0)}
- Passed: {execution.get('test_execution', {}).get('passed', 0)}
- Failed: {execution.get('test_execution', {}).get('failed', 0)}
- Coverage: {coverage.get('coverage', {}).get('line_coverage', 0)}

**Create Report With:**

1. **Validation Result**: approved or rejected
   - Approve if: all tests pass, coverage > 80%, no critical failures
   - Reject if: test failures exist or coverage insufficient

2. **Key Findings**
   - What worked well
   - What issues were found
   - Coverage gaps

3. **Recommendations**
   - Immediate actions needed
   - Long-term improvements

**Response Format:**

**Validation Result:** [approved/rejected]

**Key Findings:**
[2-3 paragraphs summary]

**Recommendations:**
1. [Action 1]
2. [Action 2]
3. [Action 3]

Be clear and actionable.
"""

        return prompt

    # ========================================================================
    # RESPONSE PARSERS
    # ========================================================================

    def _parse_test_cases(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse test cases from LLM response."""
        test_cases = []

        # Find all test case blocks
        pattern = r"\*\*Test ID:\*\*\s*(\w+).*?\*\*Name:\*\*\s*([^\n]+).*?\*\*Type:\*\*\s*([^\n]+).*?\*\*Priority:\*\*\s*([^\n]+)"

        for match in re.finditer(pattern, response_text, re.DOTALL):
            test_id = match.group(1).strip()
            name = match.group(2).strip()
            test_type = match.group(3).strip()
            priority = match.group(4).strip()

            # Extract steps
            steps_match = re.search(
                rf"{re.escape(match.group(0))}.*?\*\*Steps:\*\*\s*\n(.*?)(?=\n\n|\*\*Test ID|\Z)",
                response_text,
                re.DOTALL
            )

            steps = []
            if steps_match:
                steps_text = steps_match.group(1)
                for line in steps_text.split("\n"):
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith("-")):
                        step = re.sub(r"^[\d\-\.\)]+\s*", "", line)
                        if step:
                            steps.append(step)

            test_cases.append({
                "id": test_id,
                "name": name,
                "type": test_type.lower(),
                "priority": priority.lower(),
                "steps": steps[:10]  # Limit steps
            })

        return test_cases[:20]  # Limit total test cases

    def _parse_coverage_analysis(self, response_text: str) -> Dict[str, Any]:
        """Parse coverage analysis from LLM response."""

        # Extract coverage goals
        line_coverage = 80
        line_match = re.search(r"Line Coverage:?\s*(\d+)", response_text, re.IGNORECASE)
        if line_match:
            line_coverage = int(line_match.group(1))

        branch_coverage = 75
        branch_match = re.search(r"Branch Coverage:?\s*(\d+)", response_text, re.IGNORECASE)
        if branch_match:
            branch_coverage = int(branch_match.group(1))

        return {
            "coverage_goals": {
                "line_coverage": line_coverage,
                "branch_coverage": branch_coverage
            },
            "critical_paths": self._extract_list_items(response_text, "Critical Paths:"),
            "risk_areas": self._extract_list_items(response_text, "Risk Areas:")
        }

    def _parse_load_test_plan(self, response_text: str) -> Dict[str, Any]:
        """Parse load test plan from LLM response."""

        return {
            "scenarios": self._extract_list_items(response_text, "Test Scenarios:"),
            "success_criteria": self._extract_list_items(response_text, "Success Criteria:"),
            "meets_sla": True  # Default
        }

    def _parse_test_plan(self, response_text: str) -> Dict[str, Any]:
        """Parse test plan from LLM response."""

        # Extract test strategy
        strategy = ""
        strategy_match = re.search(r"Test Strategy:?\s*\n(.*?)(?=\n\n\*\*|\Z)", response_text, re.DOTALL | re.IGNORECASE)
        if strategy_match:
            strategy = strategy_match.group(1).strip()

        # Extract timeline
        timeline = "2-3 weeks"
        timeline_match = re.search(r"Estimated Timeline:?\s*([^\n]+)", response_text, re.IGNORECASE)
        if timeline_match:
            timeline = timeline_match.group(1).strip()

        return {
            "test_strategy": strategy,
            "phases": self._extract_list_items(response_text, "Test Phases:"),
            "resources": self._extract_list_items(response_text, "Resource Requirements:"),
            "timeline": timeline,
            "risks": self._extract_list_items(response_text, "Risks:")
        }

    def _parse_test_report(self, response_text: str) -> Dict[str, Any]:
        """Parse test report from LLM response."""

        # Extract validation result
        validation_result = "approved"
        val_match = re.search(r"Validation Result:?\s*(approved|rejected)", response_text, re.IGNORECASE)
        if val_match:
            validation_result = val_match.group(1).lower()

        # Extract findings
        findings = ""
        findings_match = re.search(r"Key Findings:?\s*\n(.*?)(?=\n\n\*\*|\Z)", response_text, re.DOTALL | re.IGNORECASE)
        if findings_match:
            findings = findings_match.group(1).strip()

        return {
            "validation_result": validation_result,
            "findings": findings,
            "recommendations": self._extract_list_items(response_text, "Recommendations:")
        }

    def _extract_list_items(self, text: str, section_header: str) -> List[str]:
        """Extract list items from a section."""
        items = []

        if section_header in text:
            section_start = text.find(section_header)
            section_text = text[section_start:]

            # Find next section
            next_section = re.search(r"\n\n\*\*[A-Z]", section_text[len(section_header):])
            if next_section:
                section_text = section_text[:len(section_header) + next_section.start()]

            # Extract items
            for line in section_text.split("\n"):
                line = line.strip()
                if line and (line.startswith("-") or line.startswith("*") or line[0].isdigit()):
                    item = re.sub(r"^[\d\-\*\.]+\s*", "", line)
                    if item and len(item) > 3:
                        items.append(item)

        return items[:10]  # Limit

    def _categorize_tests(self, test_cases: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize test cases by type."""
        categories = {}
        for test in test_cases:
            test_type = test.get("type", "functional")
            categories[test_type] = categories.get(test_type, 0) + 1
        return categories

    def _get_generation_config(self, temperature: float = 0.3) -> Dict[str, Any]:
        """Get LLM generation configuration."""
        return {
            "temperature": temperature,
            "max_output_tokens": 4096,
            "top_p": 0.95,
            "top_k": 40
        }


# Factory function
def create_qa_tester_agent(context: Dict[str, Any], message_bus, orchestrator_id: str):
    """Factory function to create QA tester agent."""
    return QATesterAgent(
        context=context,
        message_bus=message_bus,
        orchestrator_id=orchestrator_id
    )

# Export for backward compatibility
qa_tester_agent = None  # Will be instantiated when needed
