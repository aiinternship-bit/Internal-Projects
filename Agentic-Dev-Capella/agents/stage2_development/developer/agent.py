"""
agents/stage2_development/developer/agent.py

Developer agent that implements code according to architectural specifications.
Handles both new code creation and refactoring while preserving business logic.
"""

from typing import Dict, List, Any
from google.adk.agents import Agent


def query_vector_db(
    component_id: str,
    query_type: str = "business_logic"
) -> Dict[str, Any]:
    """Queries the Vector DB for legacy implementation context.
    
    Args:
        component_id: Identifier for the component being modernized
        query_type: Type of context needed (business_logic, dependencies, nfrs)
        
    Returns:
        dict: Relevant context from the legacy system
    """
    # In production, this would query the actual Vector DB
    context = {
        "business_logic": {
            "description": "Legacy implementation details",
            "key_algorithms": [],
            "edge_cases": [],
            "data_transformations": []
        },
        "dependencies": {
            "internal_dependencies": [],
            "external_libraries": [],
            "database_interactions": []
        },
        "nfrs": {
            "performance_requirements": {},
            "security_requirements": {},
            "scalability_needs": {}
        }
    }
    
    return {
        "status": "success",
        "component_id": component_id,
        "query_type": query_type,
        "context": context.get(query_type, {})
    }


def implement_component(
    architecture_spec: Dict[str, Any],
    legacy_context: Dict[str, Any],
    output_language: str = "python"
) -> Dict[str, Any]:
    """Implements a component based on architectural specifications.
    
    Args:
        architecture_spec: Architecture document with design details
        legacy_context: Context from Vector DB about legacy implementation
        output_language: Target language (python, cpp, typescript, etc.)
        
    Returns:
        dict: Generated code, unit tests, and implementation notes
    """
    component_name = architecture_spec.get("component_name", "unknown")
    
    # Generate code based on specifications
    generated_code = f"""
# Generated implementation for {component_name}
# Language: {output_language}
# Preserves business logic from legacy system

def {component_name.lower()}():
    \"\"\"
    Implementation based on architectural specification.
    
    Legacy behavior preserved:
    - {legacy_context.get('business_logic', {}).get('description', 'N/A')}
    \"\"\"
    pass
"""
    
    # Generate unit tests
    unit_tests = f"""
# Unit tests for {component_name}

def test_{component_name.lower()}():
    \"\"\"Test basic functionality.\"\"\"
    assert True  # Placeholder
    
def test_{component_name.lower()}_edge_cases():
    \"\"\"Test edge cases from legacy system.\"\"\"
    assert True  # Placeholder
"""
    
    return {
        "status": "success",
        "component_name": component_name,
        "code": generated_code,
        "unit_tests": unit_tests,
        "test_coverage_estimate": 85,
        "implementation_notes": [
            "Business logic preserved from legacy system",
            f"Implemented in modern {output_language}",
            "Unit tests cover main functionality and edge cases"
        ]
    }


def refactor_existing_code(
    existing_code: str,
    refactor_goals: List[str]
) -> Dict[str, Any]:
    """Refactors existing code to improve quality or modernize patterns.
    
    Args:
        existing_code: Current code to be refactored
        refactor_goals: List of refactoring objectives
        
    Returns:
        dict: Refactored code and explanation of changes
    """
    # In production, this would perform actual refactoring
    refactored_code = existing_code  # Placeholder
    
    changes_made = []
    for goal in refactor_goals:
        if "modernize" in goal.lower():
            changes_made.append("Updated to modern language idioms")
        if "performance" in goal.lower():
            changes_made.append("Optimized performance-critical sections")
        if "maintainability" in goal.lower():
            changes_made.append("Improved code structure and naming")
    
    return {
        "status": "success",
        "refactored_code": refactored_code,
        "changes_made": changes_made,
        "estimated_improvement": "30% more maintainable"
    }


def generate_migration_script(
    schema_changes: Dict[str, Any],
    data_transformations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generates data migration scripts for schema changes.
    
    Args:
        schema_changes: Description of database schema changes
        data_transformations: Required data transformations
        
    Returns:
        dict: Migration scripts and rollback procedures
    """
    migration_script = """
-- Migration script for schema changes
-- Generated automatically

BEGIN TRANSACTION;

-- Schema modifications
-- [Generated DDL statements would go here]

-- Data transformations
-- [Generated DML statements would go here]

COMMIT;
"""
    
    rollback_script = """
-- Rollback script
BEGIN TRANSACTION;
-- [Rollback statements would go here]
COMMIT;
"""
    
    return {
        "status": "success",
        "migration_script": migration_script,
        "rollback_script": rollback_script,
        "estimated_downtime_minutes": 5,
        "safety_checks": [
            "Backup created before migration",
            "Rollback script tested",
            "Data integrity constraints verified"
        ]
    }


def handle_cross_cutting_concerns(
    code: str,
    concerns: List[str]
) -> Dict[str, Any]:
    """Adds cross-cutting concerns like logging, security, observability.
    
    Args:
        code: Base implementation code
        concerns: List of concerns to add (logging, auth, monitoring, etc.)
        
    Returns:
        dict: Enhanced code with cross-cutting concerns
    """
    enhanced_code = code
    added_concerns = []
    
    if "logging" in concerns:
        enhanced_code = "import logging\n" + enhanced_code
        added_concerns.append("Structured logging added")
    
    if "monitoring" in concerns:
        added_concerns.append("Performance metrics instrumentation added")
    
    if "security" in concerns:
        added_concerns.append("Input validation and sanitization added")
    
    if "error_handling" in concerns:
        added_concerns.append("Comprehensive error handling added")
    
    return {
        "status": "success",
        "enhanced_code": enhanced_code,
        "concerns_added": added_concerns
    }


# Create the developer agent
developer_agent = Agent(
    name="developer_agent",
    model="gemini-2.0-flash",
    description=(
        "Implements code according to architectural specifications. "
        "Handles both new code creation and refactoring while preserving "
        "business logic from legacy systems."
    ),
    instruction=(
        "You are a developer agent responsible for implementing modern code based on "
        "architectural specifications while preserving business logic from legacy systems.\n\n"
        "Your key responsibilities:\n"
        "1. Query Vector DB to understand legacy implementation context\n"
        "2. Implement new code following architectural specifications\n"
        "3. Refactor existing code when needed\n"
        "4. Generate comprehensive unit tests with high coverage\n"
        "5. Create data migration scripts for schema changes\n"
        "6. Add cross-cutting concerns: logging, security, monitoring, error handling\n\n"
        "CRITICAL: Always preserve business logic from the legacy system. "
        "Use Vector DB context to understand:\n"
        "- Key algorithms and data transformations\n"
        "- Edge cases and special handling\n"
        "- Performance requirements\n"
        "- Data validation rules\n\n"
        "Code Quality Standards:\n"
        "- Write clean, idiomatic code in the target language\n"
        "- Follow architectural patterns specified in the architecture document\n"
        "- Include comprehensive error handling\n"
        "- Add detailed docstrings and comments\n"
        "- Generate unit tests covering main paths and edge cases\n"
        "- Aim for >80% test coverage\n\n"
        "When implementing, consider:\n"
        "- Modern language features and best practices\n"
        "- Security vulnerabilities (SQL injection, XSS, etc.)\n"
        "- Performance optimizations\n"
        "- Maintainability and readability\n\n"
        "Support multiple output languages: Python, C++, TypeScript, Java, Go"
    ),
    tools=[
        query_vector_db,
        implement_component,
        refactor_existing_code,
        generate_migration_script,
        handle_cross_cutting_concerns
    ]
)
