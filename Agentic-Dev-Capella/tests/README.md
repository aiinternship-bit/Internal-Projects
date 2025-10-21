# Agent Testing Suite

Complete testing framework for the Legacy Modernization multi-agent system.

## Quick Start

### 1. Run All Pre-Built Tests
```bash
python tests/agent_tests/test_all_agents.py --agent all
```

### 2. Test a Specific Agent
```bash
python tests/agent_tests/test_all_agents.py --agent developer_agent
```

### 3. Interactive Testing
```bash
python scripts/test_agent_interactive.py
```

### 4. View Results
```bash
# List all result files
python scripts/view_test_results.py --list

# View summary
python scripts/view_test_results.py tests/agent_tests/results/developer_agent_results.json

# View detailed results
python scripts/view_test_results.py tests/agent_tests/results/developer_agent_results.json --detailed

# View specific test output
python scripts/view_test_results.py tests/agent_tests/results/developer_agent_results.json --test-id dev_001

# Compare two test runs
python scripts/view_test_results.py file1.json --compare file2.json
```

## Features

### ✅ Prompt-Based Testing
Test agents with natural language prompts:
```python
input_prompt="Implement a payment processor in Python with fraud detection"
```

### ✅ Automatic Validation
Built-in validation for:
- Expected status codes
- Required output fields
- Custom validation functions

### ✅ Interactive Mode
Guided testing experience:
- Select agent from menu
- Choose tool to test
- Step-by-step input prompts
- Immediate results

### ✅ Results Tracking
- JSON output for all tests
- Execution time tracking
- Detailed failure information
- Comparison between test runs

### ✅ Extensible Framework
Easy to add new tests:
```python
suite.add_test(
    test_id="my_test",
    test_name="My Test Name",
    description="What this tests",
    input_prompt="Natural language prompt",
    input_data={...},
    expected_status="success",
    expected_fields=["field1", "field2"]
)
```

## Available Test Suites

### Orchestration Agents
- **escalation_agent** - 4 tests covering deadlock detection and resolution
- **telemetry_audit_agent** - 4 tests covering logging and monitoring

### Discovery Agents
- **discovery_agent** - 2 tests covering codebase scanning

### Development Agents
- **developer_agent** - 4 tests covering code implementation and refactoring

## Directory Structure

```
tests/
├── __init__.py
├── README.md                          # This file
├── agent_tests/
│   ├── __init__.py
│   ├── agent_test_framework.py        # Core testing framework
│   ├── test_all_agents.py             # Pre-built test suites
│   └── results/                       # Test results (gitignored)
│       ├── developer_agent_results.json
│       ├── escalation_agent_results.json
│       └── ...
├── unit/                              # Unit tests
│   └── ...
├── integration/                       # Integration tests
│   └── ...
└── fixtures/                          # Test fixtures
    └── ...
```

## Usage Examples

### Example 1: Test Developer Agent

```bash
$ python tests/agent_tests/test_all_agents.py --agent developer_agent

################################################################################
# TESTING AGENT: developer_agent
# Test Cases: 4
################################################################################

================================================================================
Running: Query Vector DB for Context
================================================================================
Description: Test querying Vector DB for legacy implementation context

Input Prompt:
  Query Vector DB for payment processor business logic

Input Data:
  component_id: payment_processor
  query_type: business_logic

✓ TEST PASSED (0.05s)

...

================================================================================
TEST SUMMARY: developer_agent
================================================================================
Total Tests:   4
✓ Passed:      4
✗ Failed:      0
⚠ Errors:      0
Success Rate:  100.0%
================================================================================

✓ Test results saved to: tests/agent_tests/results/developer_agent_results.json
```

### Example 2: Interactive Testing

```bash
$ python scripts/test_agent_interactive.py

================================================================================
INTERACTIVE AGENT TESTER
================================================================================

Test individual agents with custom prompts and inputs
Type 'quit' or 'exit' at any time to exit

--------------------------------------------------------------------------------
SELECT AGENT TO TEST
--------------------------------------------------------------------------------
1. escalation_agent
2. telemetry_audit_agent
3. discovery_agent
4. developer_agent

Select agent (1-4): 4

--------------------------------------------------------------------------------
SELECT TOOL FOR developer_agent
--------------------------------------------------------------------------------
1. query_vector_db - Query Vector DB
2. implement_component - Implement component
3. refactor_existing_code - Refactor code
4. generate_migration_script - Generate migration script
5. handle_cross_cutting_concerns - Handle cross-cutting concerns

Select tool (1-5): 2

--------------------------------------------------------------------------------
CREATE TEST CASE FOR implement_component
--------------------------------------------------------------------------------

Test name: Implement Auth Service
Description: Test implementing authentication service
Input prompt (natural language description):
> Implement a user authentication service with JWT tokens

Input data (JSON format):
Example: {"task_id": "test_001", "component_id": "payment_processor"}
(Or press Enter for guided input)
>

Guided input creation:
Task ID (press Enter to skip): auth_001
Component ID (press Enter to skip): auth_service
Output language (python/cpp/java): python
...
```

### Example 3: View Test Results

```bash
$ python scripts/view_test_results.py tests/agent_tests/results/developer_agent_results.json --detailed

================================================================================
TEST RESULTS: developer_agent
================================================================================
Timestamp: 2024-01-01T12:00:00
Total Tests: 4

✓ Passed: 4
✗ Failed: 0
⚠ Errors: 0

Success Rate: 100.0%
Avg Execution Time: 0.12s

================================================================================
DETAILED RESULTS
================================================================================

1. ✓ Query Vector DB for Context
   ID: developer_001
   Status: passed
   Time: 0.05s
   Output Keys: status, context, component_id

2. ✓ Implement Component - Payment Processor
   ID: developer_002
   Status: passed
   Time: 0.15s
   Output Keys: status, code, unit_tests, implementation_notes

...
```

## Creating Custom Tests

### Simple Test

```python
from tests.agent_tests.agent_test_framework import (
    AgentTestRunner,
    AgentTestCase
)
from agents.stage2_development.developer.agent import developer_agent

# Create test case
test = AgentTestCase(
    test_id="custom_001",
    test_name="My Custom Test",
    description="Test description",
    input_prompt="What you want the agent to do",
    input_data={
        "param1": "value1",
        "param2": "value2"
    },
    expected_status="success",
    expected_fields=["output_field"]
)

# Run test
runner = AgentTestRunner(developer_agent, "developer_agent")
result = runner.run_test_case(test)

print(f"Status: {result.status}")
print(f"Output: {result.actual_output}")
```

### Test Suite

```python
from tests.agent_tests.agent_test_framework import AgentTestSuite

suite = AgentTestSuite("my_agent")

# Add multiple tests
suite.add_test(
    test_id="test_001",
    test_name="Test Basic",
    description="Basic functionality test",
    input_prompt="Basic test prompt",
    input_data={"task_id": "001"}
)

suite.add_test(
    test_id="test_002",
    test_name="Test Advanced",
    description="Advanced functionality test",
    input_prompt="Advanced test prompt",
    input_data={"task_id": "002", "complex_param": {...}}
)

# Get all tests
tests = suite.get_test_cases()

# Run with runner
runner = AgentTestRunner(my_agent, "my_agent")
summary = runner.run_test_suite(tests)
```

### Custom Validation

```python
def validate_code_output(result):
    """Custom validation for code generation."""
    code = result.get("code", "")

    # Check for required elements
    has_functions = "def " in code
    has_docstrings = '"""' in code
    has_types = "->" in code

    if not all([has_functions, has_docstrings, has_types]):
        return {
            "valid": False,
            "reason": "Code missing required elements",
            "details": {
                "has_functions": has_functions,
                "has_docstrings": has_docstrings,
                "has_types": has_types
            }
        }

    return {"valid": True}

# Use in test
test = AgentTestCase(
    ...,
    validation_function=validate_code_output
)
```

## Test Result Format

```json
{
  "agent_name": "developer_agent",
  "timestamp": "2024-01-01T12:00:00",
  "test_results": [
    {
      "test_case": {
        "test_id": "dev_001",
        "test_name": "Implement Component",
        "description": "Test implementing a component",
        "input_prompt": "Implement a payment processor",
        "input_data": {
          "architecture_spec": {...},
          "output_language": "python"
        }
      },
      "status": "passed",
      "actual_output": {
        "status": "success",
        "code": "...",
        "unit_tests": "..."
      },
      "execution_time_seconds": 0.15,
      "validation_details": {
        "valid": true,
        "checks": [
          {
            "check": "status",
            "expected": "success",
            "actual": "success",
            "passed": true
          }
        ]
      },
      "timestamp": "2024-01-01T12:00:01"
    }
  ]
}
```

## Best Practices

1. **Test each tool individually** - Don't test the entire agent
2. **Use descriptive names** - Make tests self-documenting
3. **Test edge cases** - Not just happy path
4. **Validate both structure and content** - Check fields AND values
5. **Save results** - Track progress over time
6. **Compare results** - Detect regressions

## Troubleshooting

### Agent has no tools
```python
# Check that agent is properly imported
from agents.your_agent import your_agent
print(your_agent.tools)  # Should show list
```

### Test always fails
```python
# Debug by printing actual output
result = runner.run_test_case(test)
print(json.dumps(result.actual_output, indent=2))
```

### Validation function errors
```python
# Add try-except in validation function
def validate(result):
    try:
        # validation logic
        return {"valid": True}
    except Exception as e:
        return {"valid": False, "reason": str(e)}
```

## Adding Tests for New Agents

1. Import the agent:
```python
from agents.your_stage.your_agent.agent import your_agent
```

2. Create test suite:
```python
def create_your_agent_tests():
    suite = AgentTestSuite("your_agent")
    # Add tests...
    return suite
```

3. Add to test registry in `test_all_agents.py`:
```python
test_suites = {
    ...,
    "your_agent": (create_your_agent_tests, your_agent)
}
```

4. Run tests:
```bash
python tests/agent_tests/test_all_agents.py --agent your_agent
```

## CI/CD Integration

Run tests in CI:
```yaml
# .github/workflows/test-agents.yml
- name: Test Agents
  run: |
    python tests/agent_tests/test_all_agents.py --agent all
```

## Documentation

- [AGENT-TESTING-GUIDE.md](../AGENT-TESTING-GUIDE.md) - Comprehensive testing guide
- [agent_test_framework.py](agent_tests/agent_test_framework.py) - Framework documentation
- [test_all_agents.py](agent_tests/test_all_agents.py) - Example test suites
