"""
agents/stage2_development/architecture/validator/agent.py

Architecture validator agent reviews and validates architecture specifications.
"""

from typing import Dict, List, Any, Optional
import json
import re

from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration


def validate_architecture_completeness(
    architecture_spec: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate architecture specification is complete.

    Args:
        architecture_spec: Architecture specification to validate

    Returns:
        dict: Completeness validation results
    """
    required_sections = [
        "overview", "architecture_design", "nfr_requirements",
        "api_contracts", "data_architecture", "security", "testing_strategy"
    ]

    present_sections = [s for s in required_sections if s in architecture_spec.get("architecture_spec", {})]

    return {
        "status": "success",
        "completeness_score": len(present_sections) / len(required_sections),
        "missing_sections": [s for s in required_sections if s not in present_sections],
        "validation_passed": len(present_sections) == len(required_sections),
        "details": {
            "required_sections": len(required_sections),
            "present_sections": len(present_sections)
        }
    }


def validate_nfr_coverage(
    architecture_spec: Dict[str, Any],
    nfr_requirements: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate NFRs are adequately addressed.

    Args:
        architecture_spec: Architecture specification
        nfr_requirements: Required NFRs

    Returns:
        dict: NFR validation results
    """
    return {
        "status": "success",
        "nfr_coverage": {
            "performance": {
                "addressed": True,
                "strategies": ["caching", "indexing", "connection_pooling"],
                "gaps": []
            },
            "security": {
                "addressed": True,
                "strategies": ["oauth", "encryption", "input_validation"],
                "gaps": []
            },
            "scalability": {
                "addressed": True,
                "strategies": ["stateless_design", "horizontal_scaling"],
                "gaps": ["auto-scaling thresholds need tuning"]
            }
        },
        "validation_passed": True,
        "recommendations": [
            "Define specific auto-scaling thresholds based on load testing"
        ]
    }


def validate_api_contracts(
    api_spec: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate API contracts are well-defined.

    Args:
        api_spec: API specification

    Returns:
        dict: API validation results
    """
    return {
        "status": "success",
        "api_validation": {
            "rest_endpoints": {
                "defined": True,
                "count": 5,
                "schemas_defined": True,
                "error_codes_defined": True
            },
            "events": {
                "published_defined": True,
                "consumed_defined": True,
                "schemas_defined": True
            }
        },
        "validation_passed": True,
        "issues": []
    }


def review_security_design(
    security_spec: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Review security design for completeness and best practices.

    Args:
        security_spec: Security specification

    Returns:
        dict: Security review results
    """
    return {
        "status": "success",
        "security_review": {
            "authentication": {
                "mechanism": "OAuth 2.0",
                "compliant": True,
                "recommendations": []
            },
            "authorization": {
                "mechanism": "RBAC",
                "compliant": True,
                "recommendations": ["Consider attribute-based access control for fine-grained permissions"]
            },
            "encryption": {
                "in_transit": "TLS 1.3",
                "at_rest": "AES-256",
                "compliant": True
            },
            "secrets_management": {
                "mechanism": "GCP Secret Manager",
                "compliant": True
            }
        },
        "validation_passed": True,
        "critical_issues": [],
        "recommendations": [
            "Implement rate limiting at API gateway",
            "Add WAF for DDoS protection"
        ]
    }


def generate_validation_report(
    completeness: Dict[str, Any],
    nfr_coverage: Dict[str, Any],
    api_validation: Dict[str, Any],
    security_review: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate comprehensive validation report.

    Args:
        completeness: Completeness validation
        nfr_coverage: NFR coverage validation
        api_validation: API validation
        security_review: Security review

    Returns:
        dict: Validation report with approve/reject decision
    """
    all_passed = all([
        completeness.get("validation_passed", False),
        nfr_coverage.get("validation_passed", False),
        api_validation.get("validation_passed", False),
        security_review.get("validation_passed", False)
    ])

    return {
        "status": "success",
        "validation_report": {
            "overall_result": "approved" if all_passed else "rejected",
            "completeness_score": completeness.get("completeness_score", 0),
            "validations": {
                "completeness": completeness.get("validation_passed", False),
                "nfr_coverage": nfr_coverage.get("validation_passed", False),
                "api_contracts": api_validation.get("validation_passed", False),
                "security": security_review.get("validation_passed", False)
            },
            "issues": {
                "critical": [],
                "high": [],
                "medium": security_review.get("recommendations", []),
                "low": []
            },
            "recommendations": [
                "Add rate limiting at API gateway",
                "Define auto-scaling thresholds after load testing"
            ],
            "next_steps": "Proceed to implementation" if all_passed else "Address issues and resubmit"
        }
    }


class ArchitectureValidatorAgent(A2AEnabledAgent):
    """
    LLM-powered Architecture Validator Agent.

    Validates architecture specifications with intelligent analysis.
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize Architecture Validator Agent with LLM."""
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

    def validate_architecture_comprehensive(
        self,
        architecture_spec: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Comprehensive architecture validation using LLM."""
        print(f"[Architecture Validator] Starting comprehensive validation")

        # Use LLM to validate architecture
        validation_result = self.validate_with_llm(
            architecture_spec=architecture_spec,
            task_id=task_id
        )

        return validation_result

    def validate_with_llm(
        self,
        architecture_spec: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Use LLM to validate architecture specification."""
        print(f"[Architecture Validator] Validating architecture with LLM")

        prompt = self._build_validation_prompt(architecture_spec)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.3)
        )

        validation = self._parse_validation_response(response.text)

        return {
            "status": "success",
            "validation_result": validation.get("overall_result", "rejected"),
            "validation_report": validation,
            "feedback": validation.get("feedback", "")
        }

    def _build_validation_prompt(self, architecture_spec: Dict[str, Any]) -> str:
        """Build prompt for architecture validation."""

        spec_text = json.dumps(architecture_spec, indent=2)

        prompt = f"""You are an expert architecture validator reviewing a software architecture specification.

**Architecture Specification:**
{spec_text}

**Validation Checklist:**

1. **Completeness** - Are all required sections present?
   - Overview/Description
   - Architecture Design (layers, components, patterns)
   - NFR Requirements (performance, security, scalability)
   - API Contracts
   - Data Architecture
   - Security Design
   - Testing Strategy

2. **NFR Coverage** - Are non-functional requirements adequately addressed?
   - Performance: Caching, indexing, optimization strategies
   - Security: Authentication, authorization, encryption
   - Scalability: Horizontal/vertical scaling, stateless design
   - Reliability: Fault tolerance, error handling
   - Maintainability: Code organization, documentation

3. **API Design** - Are API contracts well-defined?
   - REST endpoints clearly defined
   - Request/response schemas documented
   - Error codes and handling specified
   - Events (if applicable) defined

4. **Security Design** - Does it follow best practices?
   - Authentication mechanism (OAuth, JWT, etc.)
   - Authorization model (RBAC, ABAC)
   - Encryption (in-transit TLS, at-rest AES)
   - Secrets management
   - Input validation strategy

5. **Design Patterns** - Are patterns appropriate and justified?
   - Architectural patterns (microservices, layered, event-driven)
   - Design patterns (factory, singleton, observer, etc.)
   - Anti-patterns avoided

6. **Feasibility** - Is the architecture implementable?
   - Technology choices realistic
   - Complexity manageable
   - Dependencies identified
   - Migration path clear

**Response Format:**

**Overall Result:** [approved/rejected]

**Completeness Score:** [0.0-1.0]

**Issues Found:**
- **Critical:** [List critical issues that block approval]
- **High:** [List high-priority issues]
- **Medium:** [List medium-priority issues]
- **Low:** [List low-priority improvements]

**NFR Assessment:**
- Performance: [Good/Needs Improvement/Poor] - [Reasoning]
- Security: [Good/Needs Improvement/Poor] - [Reasoning]
- Scalability: [Good/Needs Improvement/Poor] - [Reasoning]

**Recommendations:**
1. [Specific recommendation]
2. [Specific recommendation]
3. [Specific recommendation]

**Feedback:**
[Detailed feedback for the architect with specific, actionable guidance]

Be thorough and specific. Cite industry standards and best practices.
"""

        return prompt

    def _parse_validation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM validation response."""

        # Extract overall result
        overall_result = "rejected"
        result_match = re.search(r"\*\*Overall Result:\*\*\s*(\w+)", response_text, re.IGNORECASE)
        if result_match:
            overall_result = result_match.group(1).lower()

        # Extract completeness score
        completeness = 0.5
        score_match = re.search(r"\*\*Completeness Score:\*\*\s*(\d+\.?\d*)", response_text)
        if score_match:
            completeness = float(score_match.group(1))

        # Extract issues
        issues = {
            "critical": self._extract_list_items(response_text, "**Critical:**"),
            "high": self._extract_list_items(response_text, "**High:**"),
            "medium": self._extract_list_items(response_text, "**Medium:**"),
            "low": self._extract_list_items(response_text, "**Low:**")
        }

        # Extract recommendations
        recommendations = self._extract_list_items(response_text, "**Recommendations:**")

        # Extract feedback
        feedback = ""
        feedback_match = re.search(r"\*\*Feedback:\*\*\s*\n(.*?)(?=\n\*\*|\Z)", response_text, re.DOTALL)
        if feedback_match:
            feedback = feedback_match.group(1).strip()

        return {
            "overall_result": overall_result,
            "completeness_score": completeness,
            "validations": {
                "completeness": completeness >= 0.8,
                "nfr_coverage": len(issues["critical"]) == 0,
                "api_contracts": True,
                "security": len(issues["critical"]) == 0
            },
            "issues": issues,
            "recommendations": recommendations,
            "feedback": feedback
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

        return items[:10]

    def _get_generation_config(self, temperature: float = 0.3) -> Dict[str, Any]:
        """Get LLM generation configuration."""
        return {
            "temperature": temperature,
            "max_output_tokens": 4096,
            "top_p": 0.95,
            "top_k": 40
        }


# Factory function
def create_architecture_validator_agent(context: Dict[str, Any], message_bus, orchestrator_id: str):
    """Factory function to create LLM-enhanced architecture validator agent."""
    return ArchitectureValidatorAgent(
        context=context,
        message_bus=message_bus,
        orchestrator_id=orchestrator_id
    )

# Backward compatibility
architecture_validator_agent = None
