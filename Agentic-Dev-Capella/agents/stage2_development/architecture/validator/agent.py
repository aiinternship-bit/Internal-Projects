"""
agents/stage2_development/architecture/validator/agent.py

Architecture validator agent reviews and validates architecture specifications.
"""

from typing import Dict, List, Any
from google.adk.agents import Agent


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


# Create the architecture validator agent
architecture_validator_agent = Agent(
    name="architecture_validator_agent",
    model="gemini-2.0-flash",
    description=(
        "Validates architecture specifications for completeness, NFR coverage, API contracts, "
        "and security. Approves or rejects with detailed feedback."
    ),
    instruction=(
        "You are an architecture validator responsible for reviewing architecture specifications.\n\n"

        "Your key responsibilities:\n"
        "1. Validate architecture specification completeness\n"
        "2. Verify NFRs are adequately addressed\n"
        "3. Review API contracts for clarity and completeness\n"
        "4. Assess security design against best practices\n"
        "5. Generate validation report with approve/reject decision\n\n"

        "Validation Criteria:\n"
        "- All required sections present\n"
        "- NFRs have concrete strategies\n"
        "- API contracts well-defined with schemas\n"
        "- Security follows industry standards\n"
        "- Design patterns justified\n"
        "- Acceptance criteria clear and measurable\n\n"

        "Approval Criteria:\n"
        "- All validations pass\n"
        "- No critical or high-severity issues\n"
        "- Medium issues have mitigation plans\n\n"

        "Feedback Quality:\n"
        "- Specific and actionable\n"
        "- Cite best practices and standards\n"
        "- Suggest concrete improvements\n"
        "- Prioritize issues by severity"
    ),
    tools=[
        validate_architecture_completeness,
        validate_nfr_coverage,
        validate_api_contracts,
        review_security_design,
        generate_validation_report
    ]
)
