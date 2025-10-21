# Testing Quick Start

Get started testing agents in under 5 minutes!

## 1. Test All Agents (Fastest)

```bash
cd /Users/dharv/Downloads/Agentic-Dev-Team-Capella
python tests/agent_tests/test_all_agents.py --agent all
```

**What it does**: Runs all pre-built test cases for all agents
**Time**: ~30 seconds
**Output**: Summary of all tests with pass/fail status

## 2. Test One Agent

```bash
python tests/agent_tests/test_all_agents.py --agent developer_agent
```

**Available agents**:
- `escalation_agent`
- `telemetry_audit_agent`
- `discovery_agent`
- `developer_agent`

## 3. Interactive Testing

```bash
python scripts/test_agent_interactive.py
```

**What you do**:
1. Select agent from menu
2. Choose tool to test
3. Enter test data (guided)
4. See results immediately

## 4. View Results

```bash
# List all results
python scripts/view_test_results.py --list

# View specific result
python scripts/view_test_results.py tests/agent_tests/results/developer_agent_results.json

# Detailed view
python scripts/view_test_results.py tests/agent_tests/results/developer_agent_results.json --detailed
```

## Common Test Scenarios

### Test Code Generation
```bash
python tests/agent_tests/test_all_agents.py --agent developer_agent
```
Tests:
- Implement component from architecture
- Refactor existing code
- Add cross-cutting concerns

### Test Escalation Logic
```bash
python tests/agent_tests/test_all_agents.py --agent escalation_agent
```
Tests:
- Analyze rejection patterns
- Determine resolution strategy
- Create escalation reports

### Test Discovery
```bash
python tests/agent_tests/test_all_agents.py --agent discovery_agent
```
Tests:
- Scan legacy codebase
- Identify components

## Custom Test Example

```python
# my_test.py
from tests.agent_tests.agent_test_framework import AgentTestRunner, AgentTestCase
from agents.stage2_development.developer.agent import developer_agent

test = AgentTestCase(
    test_id="my_test_001",
    test_name="Test Payment Processor",
    description="Test implementing payment processor",
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

runner = AgentTestRunner(developer_agent, "developer_agent")
result = runner.run_test_case(test)

print(f"✓ Status: {result.status}")
print(f"✓ Output has code: {'code' in result.actual_output}")
```

Run it:
```bash
python my_test.py
```

## Troubleshooting

**No tools found?**
```bash
# Check agent is properly defined
python -c "from agents.stage2_development.developer.agent import developer_agent; print(developer_agent.tools)"
```

**Test fails?**
```bash
# Run with detailed output to see actual vs expected
python tests/agent_tests/test_all_agents.py --agent developer_agent
# Then view detailed results
python scripts/view_test_results.py tests/agent_tests/results/developer_agent_results.json --detailed
```

## Next Steps

1. ✅ Run pre-built tests: `python tests/agent_tests/test_all_agents.py --agent all`
2. ✅ Try interactive mode: `python scripts/test_agent_interactive.py`
3. ✅ Create your own test (see example above)
4. 📖 Read full guide: [AGENT-TESTING-GUIDE.md](AGENT-TESTING-GUIDE.md)

## File Locations

- **Test Framework**: `tests/agent_tests/agent_test_framework.py`
- **Pre-Built Tests**: `tests/agent_tests/test_all_agents.py`
- **Interactive Tool**: `scripts/test_agent_interactive.py`
- **Results Viewer**: `scripts/view_test_results.py`
- **Results Folder**: `tests/agent_tests/results/`
- **Full Guide**: [AGENT-TESTING-GUIDE.md](AGENT-TESTING-GUIDE.md)
- **README**: [tests/README.md](tests/README.md)
