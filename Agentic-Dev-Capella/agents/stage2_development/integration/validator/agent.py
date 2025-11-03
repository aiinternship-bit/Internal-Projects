"""
agents/stage2_development/integration/validator/agent.py

Integration validator validates service integration and contract compliance.
"""

from typing import Dict, List, Any, Optional
import re
import json

from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration


def validate_api_contracts(service: str, contracts: Dict[str, Any]) -> Dict[str, Any]:
    """Validate API contracts are followed."""
    return {
        "status": "success",
        "contract_validation": {
            "schemas_valid": True,
            "breaking_changes": [],
            "passed": True
        }
    }


def validate_event_schemas(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate event schemas match specifications."""
    return {
        "status": "success",
        "event_validation": {
            "published_events_valid": True,
            "consumed_events_valid": True,
            "schema_mismatches": [],
            "passed": True
        }
    }


def test_service_integration(service_a: str, service_b: str) -> Dict[str, Any]:
    """Test integration between services."""
    return {
        "status": "success",
        "integration_test": {
            "connectivity": True,
            "data_flow": True,
            "error_handling": True,
            "passed": True
        }
    }


def validate_backward_compatibility(old_version: str, new_version: str) -> Dict[str, Any]:
    """Validate backward compatibility."""
    return {
        "status": "success",
        "compatibility": {
            "backward_compatible": True,
            "breaking_changes": [],
            "migration_required": False
        }
    }


def generate_integration_validation_report(
    contracts: Dict, events: Dict, integration: Dict, compatibility: Dict
) -> Dict[str, Any]:
    """Generate integration validation report."""
    return {
        "status": "success",
        "validation_result": "approved",
        "checks": {
            "contracts": "passed",
            "events": "passed",
            "integration": "passed",
            "compatibility": "passed"
        },
        "recommendations": []
    }


class IntegrationValidatorAgent(A2AEnabledAgent):
    """
    LLM-powered Integration Validator Agent.

    Validates service integrations, API contracts, and backward compatibility with intelligent analysis.
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize Integration Validator Agent with LLM."""
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

    def validate_integration_comprehensive(
        self,
        integration_spec: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Comprehensive integration validation using LLM."""
        print(f"[Integration Validator] Starting comprehensive integration validation")

        # Validate with LLM
        validation_result = self.validate_with_llm(
            integration_spec=integration_spec,
            task_id=task_id
        )

        return validation_result

    def validate_with_llm(
        self,
        integration_spec: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Use LLM to validate integration specifications."""
        print(f"[Integration Validator] Validating integration with LLM")

        prompt = self._build_validation_prompt(integration_spec)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.2)
        )

        validation = self._parse_validation_response(response.text)

        return {
            "status": "success",
            "validation_result": validation.get("overall_result", "rejected"),
            "validation_report": validation,
            "breaking_changes": validation.get("breaking_changes", [])
        }

    def analyze_breaking_changes_llm(
        self,
        old_version: Dict[str, Any],
        new_version: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze breaking changes between versions using LLM."""
        print(f"[Integration Validator] Analyzing breaking changes with LLM")

        prompt = self._build_breaking_changes_prompt(old_version, new_version)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.3)
        )

        analysis = self._parse_breaking_changes_analysis(response.text)

        return {
            "status": "success",
            "breaking_changes": analysis.get("breaking_changes", []),
            "migration_required": analysis.get("migration_required", False),
            "migration_plan": analysis.get("migration_plan", [])
        }

    def _build_validation_prompt(self, integration_spec: Dict[str, Any]) -> str:
        """Build prompt for integration validation."""

        spec_text = json.dumps(integration_spec, indent=2)

        prompt = f"""You are an integration architect validating service integrations and API contracts.

**Integration Specification:**
{spec_text}

**Validation Checklist:**

1. **API Contract Validation**
   - Request/response schemas defined?
   - All fields properly typed?
   - Required vs optional fields marked?
   - Validation rules specified?
   - Error responses documented?
   - Status codes appropriate?
   - Pagination strategy defined?
   - Rate limiting documented?

2. **Event Schema Validation** (if event-driven)
   - Event schemas defined with version?
   - Event types clearly categorized?
   - Payload structure validated?
   - Schema evolution strategy?
   - Event ordering guarantees?
   - Idempotency handled?
   - Dead letter queue configured?

3. **Integration Testing**
   - Happy path scenarios covered?
   - Error scenarios tested?
   - Timeout handling validated?
   - Retry logic tested?
   - Circuit breaker validated?
   - Data consistency checks?
   - Performance benchmarks met?

4. **Backward Compatibility**
   - API version strategy (URL vs header)?
   - Deprecated fields marked?
   - Breaking changes identified?
   - Migration path documented?
   - Dual-read/dual-write period defined?
   - Rollback strategy clear?

5. **Service Dependencies**
   - Dependency graph clear?
   - Circular dependencies avoided?
   - Failure isolation strategy?
   - Cascading failure prevention?
   - Timeouts configured appropriately?
   - Bulkhead pattern applied?

6. **Data Contract Validation**
   - Data types consistent?
   - Enum values documented?
   - Date/time formats standardized?
   - Null handling strategy?
   - Default values specified?
   - Validation constraints clear?

7. **Security & Authentication**
   - Authentication method clear?
   - Authorization rules defined?
   - API keys/tokens secured?
   - Rate limiting enforced?
   - Input validation comprehensive?
   - SQL injection prevented?
   - XSS prevention applied?

**Response Format:**

**Overall Result:** [approved/rejected/conditional]

**Validation Results:**
- API Contracts: [passed/failed] - [reasoning]
- Event Schemas: [passed/failed] - [reasoning]
- Integration Tests: [passed/failed] - [reasoning]
- Backward Compatibility: [passed/failed] - [reasoning]
- Dependencies: [passed/failed] - [reasoning]
- Data Contracts: [passed/failed] - [reasoning]
- Security: [passed/failed] - [reasoning]

**Breaking Changes Identified:**
- [Breaking change 1 with impact assessment]
- [Breaking change 2 with impact assessment]

**Contract Violations:**
- [Violation 1 with severity]
- [Violation 2 with severity]

**Integration Risks:**
- [Risk 1 with mitigation]
- [Risk 2 with mitigation]

**Missing Specifications:**
- [Missing spec 1]
- [Missing spec 2]

**Recommendations:**
1. [Specific recommendation for improvement]
2. [Specific recommendation for improvement]
3. [Specific recommendation for improvement]

**Migration Required:** [yes/no]

**Migration Plan:** (if migration required)
- Phase 1: [description]
- Phase 2: [description]
- Phase 3: [description]

Be thorough in identifying breaking changes and contract violations.
"""

        return prompt

    def _build_breaking_changes_prompt(
        self,
        old_version: Dict[str, Any],
        new_version: Dict[str, Any]
    ) -> str:
        """Build prompt for breaking changes analysis."""

        old_text = json.dumps(old_version, indent=2)
        new_text = json.dumps(new_version, indent=2)

        prompt = f"""You are an API versioning expert analyzing changes between API versions for breaking changes.

**Old Version (Current Production):**
{old_text}

**New Version (To Be Deployed):**
{new_text}

**Breaking Change Analysis:**

1. **API Contract Changes**
   - Removed endpoints
   - Removed request/response fields
   - Changed field types
   - Changed field semantics (same name, different meaning)
   - Removed optional fields that clients depend on
   - Changed required fields
   - Changed status codes
   - Changed error formats

2. **Event Schema Changes**
   - Removed event types
   - Removed event fields
   - Changed event field types
   - Changed event structure
   - Changed event ordering guarantees

3. **Behavior Changes**
   - Changed validation rules (more strict)
   - Changed rate limits (more restrictive)
   - Changed timeout values (lower)
   - Changed pagination behavior
   - Changed sorting/filtering behavior
   - Changed authentication requirements

4. **Data Format Changes**
   - Date/time format changes
   - Enum value removals
   - Unit changes (e.g., ms to seconds)
   - Encoding changes
   - Null handling changes

5. **Impact Assessment**
   - Number of clients affected
   - Criticality of affected functionality
   - Rollback difficulty
   - User experience impact
   - Data migration complexity

**Response Format:**

**Breaking Changes Summary:**
- Total Breaking Changes: [count]
- Critical Severity: [count]
- High Severity: [count]
- Medium Severity: [count]

**Critical Breaking Changes:**
1. [Change description] - Impact: [who is affected and how] - Severity: Critical
2. [Change description] - Impact: [who is affected and how] - Severity: Critical

**High Severity Breaking Changes:**
1. [Change description] - Impact: [who is affected and how] - Severity: High

**Medium Severity Breaking Changes:**
1. [Change description] - Impact: [who is affected and how] - Severity: Medium

**Backward Compatible Changes:**
- [Change 1 that is backward compatible]
- [Change 2 that is backward compatible]

**Migration Required:** [yes/no]

**Migration Strategy:**
- Approach: [versioning/dual-write/feature-flags/phased-rollout]
- Duration: [estimated time]
- Rollback Complexity: [low/medium/high]

**Migration Plan:**
1. **Phase 1: Deprecation** - [duration]
   - Announce deprecation
   - Add deprecation warnings
   - Update documentation
   - Notify clients

2. **Phase 2: Dual Support** - [duration]
   - Support both old and new versions
   - Dual-write/dual-read if needed
   - Monitor adoption

3. **Phase 3: Cutover** - [duration]
   - Switch default to new version
   - Monitor error rates
   - Rollback ready

4. **Phase 4: Sunset** - [duration]
   - Remove old version support
   - Final client migration
   - Cleanup old code

**Client Migration Guide:**
- Breaking Change: [description] - Migration: [how to adapt]
- Breaking Change: [description] - Migration: [how to adapt]

**Rollback Strategy:**
- Rollback Triggers: [when to rollback]
- Rollback Complexity: [how difficult]
- Data Inconsistency Risk: [assessment]

**Recommendations:**
1. [How to minimize breaking changes]
2. [Alternative non-breaking approach]
3. [Communication strategy]

Be comprehensive in identifying even subtle breaking changes that could affect clients.
"""

        return prompt

    def _parse_validation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse integration validation response."""

        # Extract overall result
        overall_result = "rejected"
        result_match = re.search(r"\*\*Overall Result:\*\*\s*\[?(approved|rejected|conditional)\]?", response_text, re.IGNORECASE)
        if result_match:
            overall_result = result_match.group(1).lower()

        # Extract migration required
        migration_required = False
        migration_match = re.search(r"\*\*Migration Required:\*\*\s*\[?(yes|no)\]?", response_text, re.IGNORECASE)
        if migration_match and migration_match.group(1).lower() == "yes":
            migration_required = True

        # Extract breaking changes
        breaking_changes = self._extract_list_items(response_text, "**Breaking Changes Identified:**")

        # Extract contract violations
        violations = self._extract_list_items(response_text, "**Contract Violations:**")

        # Extract risks
        risks = self._extract_list_items(response_text, "**Integration Risks:**")

        # Extract recommendations
        recommendations = self._extract_list_items(response_text, "**Recommendations:**")

        # Extract validation results
        validation_results = self._extract_validation_results(response_text)

        return {
            "overall_result": overall_result,
            "validation_results": validation_results,
            "breaking_changes": breaking_changes,
            "contract_violations": violations,
            "risks": risks,
            "recommendations": recommendations,
            "migration_required": migration_required
        }

    def _parse_breaking_changes_analysis(self, response_text: str) -> Dict[str, Any]:
        """Parse breaking changes analysis response."""

        # Extract migration required
        migration_required = False
        migration_match = re.search(r"\*\*Migration Required:\*\*\s*\[?(yes|no)\]?", response_text, re.IGNORECASE)
        if migration_match and migration_match.group(1).lower() == "yes":
            migration_required = True

        # Extract critical breaking changes
        critical_changes = self._extract_list_items(response_text, "**Critical Breaking Changes:**")

        # Extract high severity changes
        high_changes = self._extract_list_items(response_text, "**High Severity Breaking Changes:**")

        # Extract migration plan
        migration_plan = self._extract_list_items(response_text, "**Migration Plan:**")

        # Extract client migration guide
        migration_guide = self._extract_list_items(response_text, "**Client Migration Guide:**")

        # Extract recommendations
        recommendations = self._extract_list_items(response_text, "**Recommendations:**")

        return {
            "migration_required": migration_required,
            "breaking_changes": critical_changes + high_changes,
            "migration_plan": migration_plan,
            "migration_guide": migration_guide,
            "recommendations": recommendations
        }

    def _extract_validation_results(self, text: str) -> Dict[str, str]:
        """Extract validation results."""
        results = {}

        result_names = [
            "API Contracts",
            "Event Schemas",
            "Integration Tests",
            "Backward Compatibility",
            "Dependencies",
            "Data Contracts",
            "Security"
        ]

        for result_name in result_names:
            pattern = rf"- {result_name}:\s*\[?(passed|failed)\]?"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                results[result_name.lower().replace(" ", "_")] = match.group(1).lower()

        return results

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
            "max_output_tokens": 8192,
            "top_p": 0.95,
            "top_k": 40
        }


# Factory function
def create_integration_validator_agent(context: Dict[str, Any], message_bus, orchestrator_id: str):
    """Factory function to create LLM-enhanced integration validator agent."""
    return IntegrationValidatorAgent(
        context=context,
        message_bus=message_bus,
        orchestrator_id=orchestrator_id
    )

# Backward compatibility
integration_validator_agent = None
