"""
tests/agent_tests/test_all_agents.py

Comprehensive test suites for all 26 agents.
Run individual agents or all agents with prompt-based testing.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.agent_tests.agent_test_framework import (
    AgentTestRunner,
    AgentTestSuite,
    create_validation_function
)

# Import all agents
from agents.orchestration.escalation.agent import escalation_agent
from agents.orchestration.telemetry.agent import telemetry_agent
from agents.stage0_discovery.discovery.agent import discovery_agent
from agents.stage2_development.developer.agent import developer_agent


# ============================================================================
# ORCHESTRATION AGENTS
# ============================================================================

def create_escalation_agent_tests() -> AgentTestSuite:
    """Create test suite for escalation agent."""
    suite = AgentTestSuite("escalation_agent")

    # Test 1: Analyze simple rejection pattern
    suite.add_test(
        test_id="escalation_001",
        test_name="Analyze Rejection Pattern - Simple Case",
        description="Test analyzing a simple rejection pattern with repeated issues",
        input_prompt="Analyze rejection history where same issue appears 3 times",
        input_data={
            "task_id": "test_task_001",
            "rejection_history": [
                {"reason": "missing_error_handling", "attempt": 1},
                {"reason": "missing_error_handling", "attempt": 2},
                {"reason": "missing_error_handling", "attempt": 3}
            ]
        },
        expected_status="success",
        expected_fields=["is_deadlock", "root_cause", "most_common_issue"]
    )

    # Test 2: Analyze complex rejection pattern
    suite.add_test(
        test_id="escalation_002",
        test_name="Analyze Rejection Pattern - Multiple Issues",
        description="Test analyzing rejection pattern with multiple different issues",
        input_prompt="Analyze rejection history with varied issues",
        input_data={
            "task_id": "test_task_002",
            "rejection_history": [
                {"reason": "missing_error_handling", "attempt": 1},
                {"reason": "security_vulnerability", "attempt": 2},
                {"reason": "performance_issue", "attempt": 3},
                {"reason": "code_complexity", "attempt": 4}
            ]
        },
        expected_status="success",
        expected_fields=["is_deadlock", "unique_issues", "all_reasons"],
        validation_function=lambda r: {
            "valid": r.get("unique_issues") == 4,
            "details": f"Expected 4 unique issues, got {r.get('unique_issues')}"
        }
    )

    # Test 3: Determine resolution strategy
    suite.add_test(
        test_id="escalation_003",
        test_name="Determine Resolution Strategy",
        description="Test determining resolution strategy for deadlock",
        input_prompt="Determine best resolution strategy for validation deadlock",
        input_data={
            "deadlock_analysis": {
                "is_deadlock": True,
                "total_rejections": 4,
                "root_cause": "unclear_requirements"
            },
            "task_context": {
                "component_id": "payment_processor",
                "priority": "high"
            }
        },
        expected_status="success",
        expected_fields=["requires_human_intervention", "strategies", "recommended_strategy"]
    )

    # Test 4: Create escalation report
    suite.add_test(
        test_id="escalation_004",
        test_name="Create Escalation Report",
        description="Test creating comprehensive escalation report",
        input_prompt="Create escalation report for human review",
        input_data={
            "task_id": "test_task_004",
            "deadlock_analysis": {
                "total_rejections": 5,
                "is_deadlock": True,
                "root_cause": "validation_criteria_too_strict"
            },
            "resolution_strategy": {
                "requires_human_intervention": True,
                "strategies": [{"type": "human_intervention"}]
            },
            "task_context": {
                "component_id": "auth_service",
                "priority": "critical"
            }
        },
        expected_status="success",
        expected_fields=["report", "requires_immediate_attention"]
    )

    return suite


def create_telemetry_agent_tests() -> AgentTestSuite:
    """Create test suite for telemetry agent."""
    suite = AgentTestSuite("telemetry_audit_agent")

    # Test 1: Log agent activity
    suite.add_test(
        test_id="telemetry_001",
        test_name="Log Agent Activity",
        description="Test logging agent activity",
        input_prompt="Log a developer agent completing a task",
        input_data={
            "agent_name": "developer_agent",
            "activity_type": "task_complete",
            "task_id": "dev_001",
            "details": {
                "component_id": "payment_processor",
                "execution_time_seconds": 45.3
            }
        },
        expected_status="logged",
        expected_fields=["log_entry", "log_id"]
    )

    # Test 2: Track task metrics
    suite.add_test(
        test_id="telemetry_002",
        test_name="Track Task Metrics",
        description="Test tracking metrics for a completed task",
        input_prompt="Track metrics for successful task completion",
        input_data={
            "task_id": "dev_002",
            "component_id": "auth_service",
            "metrics": {
                "execution_time_seconds": 120.5,
                "retry_count": 2,
                "validation_attempts": 3,
                "success": True,
                "error_count": 0
            }
        },
        expected_status="tracked",
        expected_fields=["metrics"]
    )

    # Test 3: Track validation event
    suite.add_test(
        test_id="telemetry_003",
        test_name="Track Validation Event",
        description="Test tracking validation events",
        input_prompt="Track a failed validation event",
        input_data={
            "task_id": "dev_003",
            "validator_name": "code_validator_agent",
            "validation_result": "fail",
            "issues": ["missing_error_handling", "security_vulnerability"],
            "feedback": "Add try-catch blocks and sanitize inputs"
        },
        expected_status="tracked",
        expected_fields=["validation_event"]
    )

    # Test 4: Monitor system health
    suite.add_test(
        test_id="telemetry_004",
        test_name="Monitor System Health",
        description="Test system health monitoring",
        input_prompt="Check health of all system components",
        input_data={
            "check_agents": True,
            "check_message_bus": True,
            "check_vector_db": True
        },
        expected_fields=["overall_status", "checks"],
        validation_function=lambda r: {
            "valid": "checks" in r and len(r["checks"]) == 3,
            "details": "Should have 3 health checks"
        }
    )

    return suite


# ============================================================================
# STAGE 0: DISCOVERY AGENTS
# ============================================================================

def create_discovery_agent_tests() -> AgentTestSuite:
    """Create test suite for discovery agent."""
    suite = AgentTestSuite("discovery_agent")

    # Test 1: Scan codebase
    suite.add_test(
        test_id="discovery_001",
        test_name="Scan Codebase - Small Project",
        description="Test scanning a small legacy codebase",
        input_prompt="Scan a small COBOL project with 10 files",
        input_data={
            "legacy_repo_path": "/mock/cobol/project",
            "scan_depth": "recursive",
            "file_types": [".cbl", ".cobol"]
        },
        expected_status="success",
        expected_fields=["files_found", "total_loc"]
    )

    # Test 2: Identify components
    suite.add_test(
        test_id="discovery_002",
        test_name="Identify Components",
        description="Test identifying components in legacy system",
        input_prompt="Identify logical components from scanned code",
        input_data={
            "scanned_files": [
                {"path": "src/payment.cbl", "loc": 500},
                {"path": "src/auth.cbl", "loc": 300},
                {"path": "src/database.cbl", "loc": 200}
            ]
        },
        expected_status="success",
        expected_fields=["components"],
        validation_function=lambda r: {
            "valid": len(r.get("components", [])) >= 3,
            "details": f"Expected at least 3 components, found {len(r.get('components', []))}"
        }
    )

    return suite


# ============================================================================
# STAGE 2: DEVELOPMENT AGENTS
# ============================================================================

def create_developer_agent_tests() -> AgentTestSuite:
    """Create test suite for developer agent."""
    suite = AgentTestSuite("developer_agent")

    # Test 1: Query Vector DB
    suite.add_test(
        test_id="developer_001",
        test_name="Query Vector DB for Context",
        description="Test querying Vector DB for legacy implementation context",
        input_prompt="Query Vector DB for payment processor business logic",
        input_data={
            "component_id": "payment_processor",
            "query_type": "business_logic"
        },
        expected_status="success",
        expected_fields=["context", "component_id"]
    )

    # Test 2: Implement component
    suite.add_test(
        test_id="developer_002",
        test_name="Implement Component - Payment Processor",
        description="Test implementing a payment processor component",
        input_prompt="Implement a payment processor in Python based on architecture spec",
        input_data={
            "architecture_spec": {
                "component_name": "PaymentProcessor",
                "language": "python",
                "patterns": ["repository", "dependency_injection"],
                "nfrs": {
                    "performance": "< 100ms p95",
                    "security": "PCI-DSS compliant"
                }
            },
            "legacy_context": {
                "business_logic": {
                    "description": "Processes credit card payments with fraud detection"
                }
            },
            "output_language": "python"
        },
        expected_status="success",
        expected_fields=["code", "unit_tests", "implementation_notes"],
        validation_function=lambda r: {
            "valid": "def " in r.get("code", "") and "test_" in r.get("unit_tests", ""),
            "details": "Code should contain function definitions and tests"
        }
    )

    # Test 3: Refactor existing code
    suite.add_test(
        test_id="developer_003",
        test_name="Refactor Existing Code",
        description="Test refactoring code for modernization",
        input_prompt="Refactor legacy code to improve maintainability",
        input_data={
            "existing_code": "def process_payment(amt, curr):\n    return amt",
            "refactor_goals": ["modernize", "add_type_hints", "improve_error_handling"]
        },
        expected_status="success",
        expected_fields=["refactored_code", "changes_made"]
    )

    # Test 4: Handle cross-cutting concerns
    suite.add_test(
        test_id="developer_004",
        test_name="Add Cross-Cutting Concerns",
        description="Test adding logging, monitoring, and security",
        input_prompt="Add logging, monitoring, and security to payment code",
        input_data={
            "code": "def process_payment():\n    pass",
            "concerns": ["logging", "monitoring", "security", "error_handling"]
        },
        expected_status="success",
        expected_fields=["enhanced_code", "concerns_added"],
        validation_function=lambda r: {
            "valid": len(r.get("concerns_added", [])) == 4,
            "details": "Should add all 4 requested concerns"
        }
    )

    return suite


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_agent_tests(agent_name: str, save_results: bool = True):
    """
    Run tests for a specific agent.

    Args:
        agent_name: Name of agent to test
        save_results: Whether to save results to file
    """
    # Map agent names to test suite creators and agent instances
    test_suites = {
        "escalation_agent": (create_escalation_agent_tests, escalation_agent),
        "telemetry_audit_agent": (create_telemetry_agent_tests, telemetry_agent),
        "discovery_agent": (create_discovery_agent_tests, discovery_agent),
        "developer_agent": (create_developer_agent_tests, developer_agent),
    }

    if agent_name not in test_suites:
        print(f"Error: No tests defined for '{agent_name}'")
        print(f"Available agents: {', '.join(test_suites.keys())}")
        return

    # Get test suite and agent
    suite_creator, agent = test_suites[agent_name]
    suite = suite_creator()

    # Create test runner
    runner = AgentTestRunner(agent, agent_name)

    # Run tests
    summary = runner.run_test_suite(suite.get_test_cases())

    # Save results
    if save_results:
        output_path = f"tests/agent_tests/results/{agent_name}_results.json"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        runner.save_results(output_path)

    return summary


def run_all_agent_tests(save_results: bool = True):
    """
    Run tests for all agents.

    Args:
        save_results: Whether to save results to file
    """
    agents = [
        "escalation_agent",
        "telemetry_audit_agent",
        "discovery_agent",
        "developer_agent"
    ]

    all_summaries = []

    print("\n" + "="*80)
    print("RUNNING ALL AGENT TESTS")
    print("="*80)

    for agent_name in agents:
        summary = run_agent_tests(agent_name, save_results)
        all_summaries.append(summary)

    # Print overall summary
    print("\n" + "="*80)
    print("OVERALL TEST SUMMARY")
    print("="*80)

    total_tests = sum(s["total_tests"] for s in all_summaries)
    total_passed = sum(s["passed"] for s in all_summaries)
    total_failed = sum(s["failed"] for s in all_summaries)
    total_errors = sum(s["errors"] for s in all_summaries)

    print(f"Total Agents Tested: {len(agents)}")
    print(f"Total Tests:         {total_tests}")
    print(f"✓ Passed:            {total_passed}")
    print(f"✗ Failed:            {total_failed}")
    print(f"⚠ Errors:            {total_errors}")
    print(f"Success Rate:        {(total_passed/total_tests*100):.1f}%")
    print("="*80)

    return all_summaries


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test individual agents")
    parser.add_argument(
        "--agent",
        help="Agent to test (or 'all' for all agents)",
        choices=["all", "escalation_agent", "telemetry_audit_agent", "discovery_agent", "developer_agent"]
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save results to file"
    )

    args = parser.parse_args()

    if args.agent == "all":
        run_all_agent_tests(save_results=not args.no_save)
    elif args.agent:
        run_agent_tests(args.agent, save_results=not args.no_save)
    else:
        # Interactive mode
        print("\nAvailable agents to test:")
        print("1. escalation_agent")
        print("2. telemetry_audit_agent")
        print("3. discovery_agent")
        print("4. developer_agent")
        print("5. all")

        choice = input("\nSelect agent to test (1-5): ")

        agents_map = {
            "1": "escalation_agent",
            "2": "telemetry_audit_agent",
            "3": "discovery_agent",
            "4": "developer_agent",
            "5": "all"
        }

        agent = agents_map.get(choice)
        if agent == "all":
            run_all_agent_tests()
        elif agent:
            run_agent_tests(agent)
        else:
            print("Invalid choice")
