"""
agents/stage2_development/validation/code_validator/agent.py

Code validator agent validates code correctness, security, and quality using LLM analysis.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re

from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration


class CodeValidatorAgent(A2AEnabledAgent):
    """
    Code Validator Agent for comprehensive code validation.

    Capabilities:
    - Validate code correctness against specifications
    - Security vulnerability detection
    - Error handling verification
    - Code quality assessment
    - Generate detailed validation reports with feedback
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize Code Validator Agent."""
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

        # Validation history
        self.validation_history: List[Dict[str, Any]] = []

    def handle_task_assignment(self, message: Dict[str, Any]) -> None:
        """Handle TASK_ASSIGNMENT message from orchestrator."""
        payload = message.get("payload", {})
        task_id = payload.get("task_id")
        task_type = payload.get("task_type")
        parameters = payload.get("parameters", {})

        try:
            if task_type == "validate_code":
                result = self.validate_code_complete(task_id=task_id, **parameters)
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            # Send completion
            self.a2a.send_completion(
                task_id=task_id,
                artifacts=result,
                metrics={
                    "validation_passed": result.get("validation_result") == "approved"
                }
            )

        except Exception as e:
            self.a2a.send_error_report(
                task_id=task_id,
                error_type="VALIDATION_FAILED",
                error_message=str(e),
                stack_trace=""
            )

    def validate_code_complete(
        self,
        code: str,
        specification: Dict[str, Any],
        language: str = "python",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete code validation including all checks.

        Args:
            code: Code to validate
            specification: Requirements/spec to validate against
            language: Programming language
            task_id: Optional task ID

        Returns:
            Complete validation report with pass/fail and feedback
        """
        start_time = datetime.utcnow()

        print(f"[Code Validator] Validating code ({language})")

        # Run all validation checks
        correctness = self.check_correctness(code, specification, language, task_id)
        security = self.check_security(code, language, task_id)
        error_handling = self.check_error_handling(code, language, task_id)
        quality = self.check_code_quality(code, language, task_id)

        # Generate report
        report = self.generate_code_validation_report(
            correctness, security, error_handling, quality, task_id
        )

        duration = (datetime.utcnow() - start_time).total_seconds() / 60

        report.update({
            "duration_minutes": duration,
            "timestamp": datetime.utcnow().isoformat(),
            "language": language
        })

        # Store in history
        self.validation_history.append({
            "task_id": task_id,
            "timestamp": datetime.utcnow().isoformat(),
            "result": report.get("validation_result"),
            "issues_count": len(report.get("issues", []))
        })

        return report

    def check_correctness(
        self,
        code: str,
        specification: Dict[str, Any],
        language: str = "python",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check if code correctly implements specification using LLM."""
        print(f"[Code Validator] Checking correctness")

        prompt = self._build_correctness_prompt(code, specification, language)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.3)
        )

        result = self._parse_correctness_response(response.text)

        return {
            "status": "success",
            "correctness": result
        }

    def check_security(
        self,
        code: str,
        language: str = "python",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check for security vulnerabilities using LLM."""
        print(f"[Code Validator] Checking security")

        prompt = self._build_security_prompt(code, language)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.3)
        )

        result = self._parse_security_response(response.text)

        return {
            "status": "success",
            "security": result
        }

    def check_error_handling(
        self,
        code: str,
        language: str = "python",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate error handling and resilience using LLM."""
        print(f"[Code Validator] Checking error handling")

        prompt = self._build_error_handling_prompt(code, language)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.3)
        )

        result = self._parse_error_handling_response(response.text)

        return {
            "status": "success",
            "error_handling": result
        }

    def check_code_quality(
        self,
        code: str,
        language: str = "python",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check code quality metrics using LLM."""
        print(f"[Code Validator] Checking code quality")

        prompt = self._build_quality_prompt(code, language)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.3)
        )

        result = self._parse_quality_response(response.text)

        return {
            "status": "success",
            "quality": result
        }

    def generate_code_validation_report(
        self,
        correctness: Dict,
        security: Dict,
        error_handling: Dict,
        quality: Dict,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        print(f"[Code Validator] Generating validation report")

        # Extract results
        correctness_data = correctness.get("correctness", {})
        security_data = security.get("security", {})
        error_data = error_handling.get("error_handling", {})
        quality_data = quality.get("quality", {})

        # Determine if validation passed
        all_passed = all([
            correctness_data.get("business_logic_correct", False),
            len(security_data.get("vulnerabilities", [])) == 0,
            error_data.get("exceptions_handled", False),
            quality_data.get("passed", False)
        ])

        # Collect all issues
        issues = []
        issues.extend(correctness_data.get("issues", []))
        issues.extend(security_data.get("vulnerabilities", []))
        issues.extend(error_data.get("issues", []))
        issues.extend(quality_data.get("issues", []))

        # Collect recommendations
        recommendations = []
        recommendations.extend(correctness_data.get("recommendations", []))
        recommendations.extend(security_data.get("recommendations", []))
        recommendations.extend(error_data.get("recommendations", []))
        recommendations.extend(quality_data.get("recommendations", []))

        return {
            "status": "success",
            "validation_result": "approved" if all_passed else "rejected",
            "summary": {
                "correctness_score": correctness_data.get("requirements_met", 0.0),
                "security_score": security_data.get("score", 0.0),
                "error_handling_score": error_data.get("score", 0.0),
                "quality_score": quality_data.get("maintainability", 0.0),
                "overall_passed": all_passed
            },
            "issues": issues,
            "recommendations": recommendations[:10] if recommendations else [],
            "feedback": self._generate_feedback(issues, recommendations)
        }

    # ========================================================================
    # PROMPT BUILDERS
    # ========================================================================

    def _build_correctness_prompt(
        self,
        code: str,
        specification: Dict[str, Any],
        language: str
    ) -> str:
        """Build prompt for correctness validation."""

        spec_text = json.dumps(specification, indent=2) if specification else "No specification provided"

        prompt = f"""You are an expert code reviewer specializing in {language}.

Validate the following code against the specification to determine if it correctly implements the requirements.

**Code to Validate:**
```{language}
{code}
```

**Specification:**
{spec_text}

**Validation Criteria:**
1. Does the code implement all specified requirements?
2. Is the business logic correct and complete?
3. Are edge cases properly handled?
4. Are input validations in place?
5. Does the code match the specified interface/API?

**Response Format:**
Provide your analysis in this format:

**Requirements Met:** [0.0 to 1.0 score]
**Business Logic Correct:** [true/false]
**Edge Cases Handled:** [true/false]

**Issues Found:**
- Issue 1 (if any)
- Issue 2 (if any)

**Recommendations:**
- Recommendation 1
- Recommendation 2

Be thorough and specific. Identify real problems, not theoretical ones.
"""

        return prompt

    def _build_security_prompt(self, code: str, language: str) -> str:
        """Build prompt for security validation."""

        prompt = f"""You are a security expert specializing in {language} code security.

Analyze the following code for security vulnerabilities and weaknesses.

**Code to Analyze:**
```{language}
{code}
```

**Security Checks:**
1. SQL Injection vulnerabilities
2. XSS (Cross-Site Scripting) vulnerabilities
3. Command Injection
4. Path Traversal
5. Input validation issues
6. Authentication/Authorization flaws
7. Sensitive data exposure
8. Insecure dependencies
9. Cryptographic issues
10. Race conditions

**Response Format:**

**Vulnerabilities Found:**
- [List each vulnerability with severity: CRITICAL/HIGH/MEDIUM/LOW]

**Security Score:** [0.0 to 10.0]

**Input Validation:** [Good/Needs Improvement/Poor]

**SQL Injection Safe:** [true/false]

**XSS Safe:** [true/false]

**Recommendations:**
- Recommendation 1
- Recommendation 2

Be specific about locations and provide actionable feedback.
"""

        return prompt

    def _build_error_handling_prompt(self, code: str, language: str) -> str:
        """Build prompt for error handling validation."""

        prompt = f"""You are an expert in {language} error handling and resilience patterns.

Evaluate the error handling in the following code.

**Code to Analyze:**
```{language}
{code}
```

**Error Handling Criteria:**
1. Are exceptions/errors properly caught and handled?
2. Is logging implemented for errors?
3. Are error messages informative but not exposing sensitive data?
4. Is graceful degradation implemented where appropriate?
5. Are resources properly cleaned up in error scenarios?
6. Are errors propagated correctly?

**Response Format:**

**Exceptions Handled:** [true/false]

**Logging Present:** [true/false]

**Graceful Degradation:** [true/false]

**Error Handling Score:** [0.0 to 10.0]

**Issues:**
- Issue 1 (if any)
- Issue 2 (if any)

**Recommendations:**
- Recommendation 1
- Recommendation 2

Focus on practical error scenarios that could occur in production.
"""

        return prompt

    def _build_quality_prompt(self, code: str, language: str) -> str:
        """Build prompt for code quality validation."""

        prompt = f"""You are a code quality expert specializing in {language}.

Assess the quality of the following code.

**Code to Assess:**
```{language}
{code}
```

**Quality Criteria:**
1. Code complexity (cyclomatic complexity)
2. Maintainability
3. Readability
4. Code duplication
5. Naming conventions
6. Documentation/comments
7. SOLID principles adherence
8. Design patterns usage

**Response Format:**

**Complexity:** [1-10 score, lower is better]

**Maintainability:** [0-100 score, higher is better]

**Duplication:** [0.0-1.0 ratio]

**Quality Passed:** [true/false]

**Issues:**
- Issue 1 (if any)
- Issue 2 (if any)

**Recommendations:**
- Recommendation 1
- Recommendation 2

Provide constructive feedback that helps improve the code.
"""

        return prompt

    # ========================================================================
    # RESPONSE PARSERS
    # ========================================================================

    def _parse_correctness_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response for correctness validation."""

        # Extract requirements met score
        requirements_met = 0.8  # Default
        req_match = re.search(r"Requirements Met.*?(\d+\.?\d*)", response_text, re.IGNORECASE)
        if req_match:
            requirements_met = float(req_match.group(1))
            if requirements_met > 1.0:
                requirements_met = requirements_met / 100.0

        # Extract boolean values
        business_logic = "true" in response_text.lower() and "business logic correct" in response_text.lower()
        edge_cases = "edge cases handled" in response_text.lower() and "true" in response_text.lower()

        # Extract issues
        issues = self._extract_list_items(response_text, "Issues Found:")
        recommendations = self._extract_list_items(response_text, "Recommendations:")

        return {
            "requirements_met": requirements_met,
            "business_logic_correct": business_logic or requirements_met >= 0.8,
            "edge_cases_handled": edge_cases or requirements_met >= 0.7,
            "issues": issues,
            "recommendations": recommendations
        }

    def _parse_security_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response for security validation."""

        # Extract vulnerabilities
        vulnerabilities = self._extract_list_items(response_text, "Vulnerabilities Found:")

        # Extract security score
        score = 8.0  # Default
        score_match = re.search(r"Security Score.*?(\d+\.?\d*)", response_text, re.IGNORECASE)
        if score_match:
            score = float(score_match.group(1))

        # Extract checks
        sql_safe = "sql injection safe" in response_text.lower() and "true" in response_text.lower()
        xss_safe = "xss safe" in response_text.lower() and "true" in response_text.lower()

        recommendations = self._extract_list_items(response_text, "Recommendations:")

        return {
            "vulnerabilities": vulnerabilities,
            "score": score,
            "input_validation": len(vulnerabilities) == 0,
            "sql_injection_safe": sql_safe or len(vulnerabilities) == 0,
            "xss_safe": xss_safe or len(vulnerabilities) == 0,
            "recommendations": recommendations
        }

    def _parse_error_handling_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response for error handling validation."""

        exceptions_handled = "exceptions handled" in response_text.lower() and "true" in response_text.lower()
        logging_present = "logging present" in response_text.lower() and "true" in response_text.lower()
        graceful = "graceful degradation" in response_text.lower() and "true" in response_text.lower()

        # Extract score
        score = 7.0  # Default
        score_match = re.search(r"Error Handling Score.*?(\d+\.?\d*)", response_text, re.IGNORECASE)
        if score_match:
            score = float(score_match.group(1))

        issues = self._extract_list_items(response_text, "Issues:")
        recommendations = self._extract_list_items(response_text, "Recommendations:")

        return {
            "exceptions_handled": exceptions_handled or score >= 7.0,
            "logging_present": logging_present,
            "graceful_degradation": graceful,
            "score": score,
            "issues": issues,
            "recommendations": recommendations
        }

    def _parse_quality_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response for quality validation."""

        # Extract complexity
        complexity = 5  # Default
        complex_match = re.search(r"Complexity.*?(\d+)", response_text, re.IGNORECASE)
        if complex_match:
            complexity = int(complex_match.group(1))

        # Extract maintainability
        maintainability = 75  # Default
        maint_match = re.search(r"Maintainability.*?(\d+)", response_text, re.IGNORECASE)
        if maint_match:
            maintainability = int(maint_match.group(1))

        # Extract duplication
        duplication = 0.05  # Default
        dup_match = re.search(r"Duplication.*?(\d+\.?\d*)", response_text, re.IGNORECASE)
        if dup_match:
            duplication = float(dup_match.group(1))

        quality_passed = "quality passed" in response_text.lower() and "true" in response_text.lower()

        issues = self._extract_list_items(response_text, "Issues:")
        recommendations = self._extract_list_items(response_text, "Recommendations:")

        return {
            "complexity": complexity,
            "maintainability": maintainability,
            "duplication": duplication,
            "passed": quality_passed or (maintainability >= 70 and complexity <= 7),
            "issues": issues,
            "recommendations": recommendations
        }

    def _extract_list_items(self, text: str, section_header: str) -> List[str]:
        """Extract list items from a section."""
        items = []

        # Find section
        if section_header in text:
            section_start = text.find(section_header)
            section_text = text[section_start:]

            # Find next section or end
            next_section = re.search(r"\n\n\*\*[A-Z]", section_text[len(section_header):])
            if next_section:
                section_text = section_text[:len(section_header) + next_section.start()]

            # Extract list items
            for line in section_text.split("\n"):
                line = line.strip()
                if line.startswith("-") or line.startswith("*"):
                    item = line[1:].strip()
                    if item and len(item) > 5:
                        items.append(item)

        return items[:10]  # Limit to 10 items

    def _generate_feedback(self, issues: List[str], recommendations: List[str]) -> str:
        """Generate human-readable feedback."""
        if not issues and not recommendations:
            return "Code validation passed. No issues found."

        feedback = []

        if issues:
            feedback.append(f"Found {len(issues)} issue(s) that need attention:")
            for i, issue in enumerate(issues[:5], 1):
                feedback.append(f"{i}. {issue}")

        if recommendations:
            feedback.append("\nRecommendations for improvement:")
            for i, rec in enumerate(recommendations[:5], 1):
                feedback.append(f"{i}. {rec}")

        return "\n".join(feedback)

    def _get_generation_config(self, temperature: float = 0.3) -> Dict[str, Any]:
        """Get LLM generation configuration."""
        return {
            "temperature": temperature,
            "max_output_tokens": 4096,
            "top_p": 0.95,
            "top_k": 40
        }


# Factory function
def create_code_validator_agent(context: Dict[str, Any], message_bus, orchestrator_id: str):
    """Factory function to create code validator agent."""
    return CodeValidatorAgent(
        context=context,
        message_bus=message_bus,
        orchestrator_id=orchestrator_id
    )

# Export for backward compatibility
code_validator_agent = None  # Will be instantiated when needed
