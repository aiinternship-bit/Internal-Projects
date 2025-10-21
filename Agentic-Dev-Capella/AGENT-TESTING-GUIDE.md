# Agent Testing Guide

Complete guide for testing individual agents in the Legacy Modernization system.

## Overview

This testing framework allows you to:
- Test individual agents with custom prompts
- Validate agent outputs against expected results
- Run comprehensive test suites for all agents
- Interactively test agents with guided input
- Save and review test results

## Quick Start

### Method 1: Run Pre-Built Test Suites

Test all agents:
```bash
python tests/agent_tests/test_all_agents.py --agent all
```

Test a specific agent:
```bash
python tests/agent_tests/test_all_agents.py --agent developer_agent
```

### Method 2: Interactive Testing

Launch the interactive CLI:
```bash
python scripts/test_agent_interactive.py
```

This provides a guided experience:
1. Select an agent
2. Choose which tool to test
3. Provide input data (JSON or guided)
4. See results immediately
5. Option to save results

### Method 3: Custom Test Scripts

Create your own test:
```python
from tests.agent_tests.agent_test_framework import AgentTestRunner, AgentTestCase
from agents.stage2_development.developer.agent import developer_agent

# Create test case
test_case = AgentTestCase(
    test_id="custom_001",
    test_name="Test Payment Processing Implementation",
    description="Test implementing a payment processor",
    input_prompt="Implement a payment processor in Python",
    input_data={
        "architecture_spec": {
            "component_name": "PaymentProcessor",
            "language": "python"
        },
        "legacy_context": {},
        "output_language": "python"
    },
    expected_status="success",
    expected_fields=["code", "unit_tests"]
)

# Run test
runner = AgentTestRunner(developer_agent, "developer_agent")
result = runner.run_test_case(test_case)

print(f"Status: {result.status}")
print(f"Output: {result.actual_output}")
```

## Available Agents to Test

### Orchestration Agents (3)
- ✅ `escalation_agent` - Handles deadlocks and escalations
- ✅ `telemetry_audit_agent` - Tracks activities and metrics
- ⚠️ `orchestrator_agent` - Central coordinator (requires full deployment)

### Stage 0: Discovery (2)
- ✅ `discovery_agent` - Scans legacy codebase
- ✅ `domain_expert_agent` - Infers business domain

### Stage 2: Development (4 currently testable)
- ✅ `developer_agent` - Implements code
- ✅ `code_validator_agent` - Validates code
- ✅ `qa_tester_agent` - Generates and runs tests
- ✅ `build_agent` - Builds artifacts

## Test Case Structure

Every test case includes:

```python
AgentTestCase(
    test_id="unique_id",              # Unique identifier
    test_name="Human Readable Name",  # Display name
    description="What this tests",    # Description
    input_prompt="Natural language",  # What you're asking the agent
    input_data={...},                 # Input data for the tool
    expected_status="success",        # Expected status in result
    expected_fields=["field1"],       # Fields that must be present
    validation_function=custom_fn     # Optional custom validation
)
```

## Example Test Cases

### Example 1: Test Escalation Agent

```python
test_case = AgentTestCase(
    test_id="escalation_001",
    test_name="Analyze Validation Deadlock",
    description="Test analyzing 3 failed validation attempts",
    input_prompt="Analyze rejection pattern where validation fails 3 times for same reason",
    input_data={
        "task_id": "dev_001",
        "rejection_history": [
            {"reason": "missing_error_handling", "attempt": 1},
            {"reason": "missing_error_handling", "attempt": 2},
            {"reason": "missing_error_handling", "attempt": 3}
        ]
    },
    expected_status="success",
    expected_fields=["is_deadlock", "root_cause"],
    validation_function=lambda r: {
        "valid": r.get("is_deadlock") == True,
        "details": "Should detect deadlock with 3 same failures"
    }
)
```

### Example 2: Test Developer Agent

```python
test_case = AgentTestCase(
    test_id="dev_001",
    test_name="Implement Authentication Service",
    description="Test implementing an auth service in Python",
    input_prompt="Implement a user authentication service with JWT tokens",
    input_data={
        "architecture_spec": {
            "component_name": "AuthService",
            "language": "python",
            "patterns": ["dependency_injection"],
            "nfrs": {
                "security": "JWT token-based auth",
                "performance": "< 50ms p95"
            }
        },
        "legacy_context": {
            "business_logic": {
                "description": "Authenticates users with username/password"
            }
        },
        "output_language": "python"
    },
    expected_status="success",
    expected_fields=["code", "unit_tests", "implementation_notes"],
    validation_function=lambda r: {
        "valid": "def " in r.get("code", "") and "jwt" in r.get("code", "").lower(),
        "details": "Code should contain function definitions and JWT logic"
    }
)
```

### Example 3: Test Telemetry Agent

```python
test_case = AgentTestCase(
    test_id="telemetry_001",
    test_name="Track Task Metrics",
    description="Test tracking metrics for a completed task",
    input_prompt="Track execution metrics for a successful development task",
    input_data={
        "task_id": "dev_005",
        "component_id": "payment_processor",
        "metrics": {
            "execution_time_seconds": 125.5,
            "retry_count": 1,
            "validation_attempts": 2,
            "success": True,
            "error_count": 0
        }
    },
    expected_status="tracked",
    expected_fields=["metrics"]
)
```

## Custom Validation Functions

Create custom validation logic:

```python
def validate_code_quality(result: Dict[str, Any]) -> Dict[str, Any]:
    """Validate that generated code meets quality standards."""
    code = result.get("code", "")

    # Check for docstrings
    has_docstrings = '"""' in code or "'''" in code

    # Check for type hints
    has_type_hints = "->" in code or ": " in code

    # Check for error handling
    has_error_handling = "try:" in code or "except" in code

    if not (has_docstrings and has_type_hints and has_error_handling):
        return {
            "valid": False,
            "reason": "Code quality checks failed",
            "details": {
                "has_docstrings": has_docstrings,
                "has_type_hints": has_type_hints,
                "has_error_handling": has_error_handling
            }
        }

    return {
        "valid": True,
        "details": "All quality checks passed"
    }

# Use in test case
test_case = AgentTestCase(
    ...,
    validation_function=validate_code_quality
)
```

## Test Results

Test results are saved in JSON format:

```json
{
  "agent_name": "developer_agent",
  "timestamp": "2024-01-01T00:00:00",
  "test_results": [
    {
      "test_case": {
        "test_id": "dev_001",
        "test_name": "Implement Payment Processor",
        "input_prompt": "...",
        "input_data": {...}
      },
      "status": "passed",
      "actual_output": {
        "status": "success",
        "code": "...",
        "unit_tests": "..."
      },
      "execution_time_seconds": 2.34,
      "validation_details": {
        "valid": true,
        "checks": [...]
      }
    }
  ]
}
```

Results are saved to: `tests/agent_tests/results/{agent_name}_results.json`

## Running Tests

### Command Line Options

```bash
# Test specific agent
python tests/agent_tests/test_all_agents.py --agent developer_agent

# Test all agents
python tests/agent_tests/test_all_agents.py --agent all

# Don't save results to file
python tests/agent_tests/test_all_agents.py --agent developer_agent --no-save

# Interactive mode (no arguments)
python tests/agent_tests/test_all_agents.py
```

### Interactive Mode

```bash
python scripts/test_agent_interactive.py
```

Interactive flow:
1. Select agent from list
2. Select tool to test
3. Enter test name and description
4. Provide input data:
   - JSON format: `{"task_id": "001", "component_id": "auth"}`
   - Guided mode: Step-by-step prompts
5. Review results
6. Option to save results
7. Test another agent or exit

## Creating Test Suites

Create a test suite for your agent:

```python
from tests.agent_tests.agent_test_framework import AgentTestSuite

# Create suite
suite = AgentTestSuite("my_agent")

# Add test cases
suite.add_test(
    test_id="test_001",
    test_name="Test Basic Functionality",
    description="Test that agent handles basic input",
    input_prompt="Process basic input data",
    input_data={"task_id": "001"},
    expected_status="success",
    expected_fields=["result"]
)

suite.add_test(
    test_id="test_002",
    test_name="Test Error Handling",
    description="Test agent handles errors gracefully",
    input_prompt="Handle invalid input",
    input_data={"task_id": None},  # Invalid input
    expected_status="error"
)

# Get all test cases
test_cases = suite.get_test_cases()

# Run with runner
from tests.agent_tests.agent_test_framework import AgentTestRunner
from agents.my_agent import my_agent

runner = AgentTestRunner(my_agent, "my_agent")
summary = runner.run_test_suite(test_cases)
```

## Test Output Example

```
================================================================================
Running: Analyze Rejection Pattern - Simple Case
================================================================================
Description: Test analyzing a simple rejection pattern with repeated issues

Input Prompt:
  Analyze rejection history where same issue appears 3 times

Input Data:
  task_id: test_task_001
  rejection_history: [{'reason': 'missing_error_handling', 'attempt': 1}, ...]

✓ TEST PASSED (0.12s)

================================================================================
TEST SUMMARY: escalation_agent
================================================================================
Total Tests:   4
✓ Passed:      4
✗ Failed:      0
⚠ Errors:      0
Success Rate:  100.0%
================================================================================
```

## Best Practices

### 1. Test Each Tool Individually
```python
# ✅ Good - Test each tool
test_query_vector_db()
test_implement_component()
test_refactor_code()

# ❌ Bad - Test agent as a whole (too broad)
test_developer_agent()
```

### 2. Use Descriptive Names and Prompts
```python
# ✅ Good
test_name="Implement Payment Processor with Fraud Detection"
input_prompt="Implement a payment processor that includes fraud detection logic"

# ❌ Bad
test_name="Test 1"
input_prompt="Test the thing"
```

### 3. Validate Both Structure and Content
```python
# ✅ Good - Check structure AND content
validation_function=lambda r: {
    "valid": "code" in r and "def process_payment" in r["code"],
    "details": "Must have code with process_payment function"
}

# ❌ Bad - Only check structure
expected_fields=["code"]
```

### 4. Test Edge Cases
```python
# Test normal case
test_implement_component(valid_spec)

# Test edge cases
test_implement_component(empty_spec)
test_implement_component(missing_required_fields)
test_implement_component(invalid_language)
```

## Troubleshooting

### Test Fails with "Agent has no tools"
**Cause**: Agent not properly imported or doesn't have tools defined

**Solution**: Check that agent is imported correctly:
```python
from agents.stage2_development.developer.agent import developer_agent
print(developer_agent.tools)  # Should show list of tools
```

### Validation Always Fails
**Cause**: Expected fields don't match actual output

**Solution**: Print actual output to debug:
```python
result = runner.run_test_case(test_case)
print(json.dumps(result.actual_output, indent=2))
```

### Test Timeouts
**Cause**: Agent tool takes too long

**Solution**: Increase timeout:
```python
test_case = AgentTestCase(
    ...,
    timeout_seconds=60  # Increase from default 30
)
```

## Next Steps

1. **Run the pre-built tests**: `python tests/agent_tests/test_all_agents.py --agent all`
2. **Try interactive testing**: `python scripts/test_agent_interactive.py`
3. **Create custom tests** for your specific use cases
4. **Add tests for remaining agents** following the examples
5. **Integrate with CI/CD** for automated testing

## Additional Resources

- `tests/agent_tests/agent_test_framework.py` - Testing framework code
- `tests/agent_tests/test_all_agents.py` - Example test suites
- `scripts/test_agent_interactive.py` - Interactive testing tool
- `CLAUDE.md` - General development guidance
- `A2A-IMPLEMENTATION-GUIDE.md` - A2A communication details
