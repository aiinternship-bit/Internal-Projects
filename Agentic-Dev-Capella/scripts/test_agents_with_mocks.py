#!/usr/bin/env python3
"""
scripts/test_agents_with_mocks.py

Test all agents with mock inputs to verify their outputs.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_escalation_agent():
    """Test escalation agent with mock inputs."""
    from agents.orchestration.escalation.agent import escalation_agent

    print("\n" + "="*80)
    print("TESTING: escalation_agent")
    print("="*80)

    # Test 1: Analyze rejection pattern
    print("\n[Test 1] Analyze Rejection Pattern")
    print("-" * 80)
    result = escalation_agent.tools[0](  # analyze_rejection_pattern
        task_id="dev_001",
        rejection_history=[
            {"reason": "missing_error_handling", "attempt": 1},
            {"reason": "missing_error_handling", "attempt": 2},
            {"reason": "missing_error_handling", "attempt": 3}
        ]
    )
    print(f"✓ Result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert result["is_deadlock"] == True
    assert result["root_cause"] == "missing_error_handling"
    print("✓ All assertions passed")

    # Test 2: Determine resolution strategy
    print("\n[Test 2] Determine Resolution Strategy")
    print("-" * 80)
    result = escalation_agent.tools[1](  # determine_resolution_strategy
        deadlock_analysis={
            "is_deadlock": True,
            "total_rejections": 4,
            "root_cause": "unclear_requirements"
        },
        task_context={
            "component_id": "payment_processor",
            "priority": "high"
        }
    )
    print(f"✓ Result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert len(result["strategies"]) > 0
    print("✓ All assertions passed")


def test_telemetry_agent():
    """Test telemetry agent with mock inputs."""
    from agents.orchestration.telemetry.agent import telemetry_agent

    print("\n" + "="*80)
    print("TESTING: telemetry_agent")
    print("="*80)

    # Test 1: Log agent activity
    print("\n[Test 1] Log Agent Activity")
    print("-" * 80)
    result = telemetry_agent.tools[0](  # log_agent_activity
        agent_name="developer_agent",
        activity_type="task_complete",
        task_id="dev_001",
        details={"execution_time_seconds": 45.3}
    )
    print(f"✓ Result: {json.dumps(result, indent=2)}")
    assert result["status"] == "logged"
    assert "log_id" in result
    print("✓ All assertions passed")

    # Test 2: Track task metrics
    print("\n[Test 2] Track Task Metrics")
    print("-" * 80)
    result = telemetry_agent.tools[1](  # track_task_metrics
        task_id="dev_002",
        component_id="auth_service",
        metrics={
            "execution_time_seconds": 120.5,
            "retry_count": 2,
            "validation_attempts": 3,
            "success": True
        }
    )
    print(f"✓ Result: {json.dumps(result, indent=2)}")
    assert result["status"] == "tracked"
    assert "metrics" in result
    print("✓ All assertions passed")


def test_discovery_agent():
    """Test discovery agent with mock inputs."""
    from agents.stage0_discovery.discovery.agent import discovery_agent

    print("\n" + "="*80)
    print("TESTING: discovery_agent")
    print("="*80)

    # Test 1: Scan repository
    print("\n[Test 1] Scan Repository")
    print("-" * 80)
    result = discovery_agent.tools[0](  # scan_repository
        repo_path="/mock/legacy/cobol",
        include_patterns=["*.cbl", "*.cobol", "*.sql"]
    )
    print(f"✓ Result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert "inventory" in result
    print("✓ All assertions passed")

    # Test 2: Identify technology stack
    print("\n[Test 2] Identify Technology Stack")
    print("-" * 80)
    result = discovery_agent.tools[1](  # identify_technology_stack
        asset_inventory={
            "source_code": ["payment.cbl", "auth.java", "utils.py"],
            "database_schemas": ["schema.sql"],
            "configuration_files": ["config.yaml"],
            "infrastructure_code": ["main.tf"],
            "documentation": [],
            "api_contracts": []
        }
    )
    print(f"✓ Result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert "technology_stack" in result
    print("✓ All assertions passed")


def test_domain_expert_agent():
    """Test domain expert agent with mock inputs."""
    from agents.stage0_discovery.domain_expert.agent import domain_expert_agent

    print("\n" + "="*80)
    print("TESTING: domain_expert_agent")
    print("="*80)

    # Test 1: Analyze business domain
    print("\n[Test 1] Analyze Business Domain")
    print("-" * 80)
    result = domain_expert_agent.tools[0](  # analyze_business_domain
        legacy_codebase_path="/mock/legacy/cobol",
        documentation={
            "readme": "Payment processing system",
            "business_docs": ["Requirements.doc", "Process_Flow.pdf"]
        }
    )
    print(f"✓ Result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert "bounded_contexts" in result
    assert "domain_events" in result
    print("✓ All assertions passed")

    # Test 2: Identify business entities
    print("\n[Test 2] Identify Business Entities")
    print("-" * 80)
    result = domain_expert_agent.tools[1](  # identify_business_entities
        domain_analysis=result,  # Use result from previous test
        code_artifacts=["payment_processor.cbl", "order_manager.cbl"]
    )
    print(f"✓ Result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert "entities" in result
    print("✓ All assertions passed")


def test_developer_agent():
    """Test developer agent with mock inputs."""
    from agents.stage2_development.developer.agent import developer_agent

    print("\n" + "="*80)
    print("TESTING: developer_agent")
    print("="*80)

    # Test 1: Query Vector DB
    print("\n[Test 1] Query Vector DB")
    print("-" * 80)
    result = developer_agent.tools[0](  # query_vector_db
        component_id="payment_processor",
        query_type="business_logic"
    )
    print(f"✓ Result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert "context" in result
    print("✓ All assertions passed")

    # Test 2: Implement component
    print("\n[Test 2] Implement Component")
    print("-" * 80)
    result = developer_agent.tools[1](  # implement_component
        architecture_spec={
            "component_name": "PaymentProcessor",
            "language": "python",
            "patterns": ["repository"]
        },
        legacy_context={
            "business_logic": {
                "description": "Processes credit card payments"
            }
        },
        output_language="python"
    )
    print(f"✓ Result keys: {list(result.keys())}")
    print(f"✓ Generated code preview:")
    print(result["code"][:200] + "...")
    assert result["status"] == "success"
    assert "code" in result
    assert "unit_tests" in result
    assert "def " in result["code"]  # Has function definitions
    print("✓ All assertions passed")

    # Test 3: Refactor existing code
    print("\n[Test 3] Refactor Existing Code")
    print("-" * 80)
    result = developer_agent.tools[2](  # refactor_existing_code
        existing_code="def process_payment(amt, curr):\n    return amt",
        refactor_goals=["modernize", "add_type_hints"]
    )
    print(f"✓ Result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert "refactored_code" in result
    print("✓ All assertions passed")


def test_code_validator_agent():
    """Test code validator agent with mock inputs."""
    from agents.stage2_development.validation.code_validator.agent import code_validator_agent

    print("\n" + "="*80)
    print("TESTING: code_validator_agent")
    print("="*80)

    # Test 1: Check correctness
    print("\n[Test 1] Check Code Correctness")
    print("-" * 80)
    result = code_validator_agent.tools[0](  # check_correctness
        code="""
def process_payment(amount: float, currency: str) -> dict:
    if amount <= 0:
        raise ValueError("Amount must be positive")
    return {"status": "success", "amount": amount}
""",
        specification={
            "function_name": "process_payment",
            "requirements": ["validate amount", "return dict with status"]
        }
    )
    print(f"✓ Result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert "correctness" in result
    print("✓ All assertions passed")

    # Test 2: Check security
    print("\n[Test 2] Check Security")
    print("-" * 80)
    result = code_validator_agent.tools[1](  # check_security
        code="""
def process_payment(amount: float, currency: str) -> dict:
    if amount <= 0:
        raise ValueError("Amount must be positive")
    return {"status": "success", "amount": amount}
"""
    )
    print(f"✓ Result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert "security" in result
    print("✓ All assertions passed")


def test_architect_agent():
    """Test architect agent with mock inputs."""
    from agents.stage2_development.architecture.architect.agent import architect_agent

    print("\n" + "="*80)
    print("TESTING: architect_agent")
    print("="*80)

    # Test 1: Design architecture
    print("\n[Test 1] Design Architecture")
    print("-" * 80)
    result = architect_agent.tools[0](  # design_architecture
        component_spec={
            "component_id": "payment_processor",
            "component_name": "PaymentProcessor"
        },
        domain_model={"domain": "fintech"},
        nfr_requirements={
            "performance": "< 100ms p95",
            "security": "PCI-DSS compliant"
        }
    )
    print(f"✓ Result keys: {list(result.keys())}")
    assert result["status"] == "success"
    print("✓ All assertions passed")


def test_qa_tester_agent():
    """Test QA tester agent with mock inputs."""
    from agents.stage2_development.qa.tester.agent import qa_tester_agent

    print("\n" + "="*80)
    print("TESTING: qa_tester_agent")
    print("="*80)

    # Test 1: Generate test cases
    print("\n[Test 1] Generate Test Cases")
    print("-" * 80)
    result = qa_tester_agent.tools[0](  # generate_test_cases
        specification={
            "component_name": "PaymentProcessor",
            "functions": ["process_payment", "validate_card"],
            "requirements": ["Process credit card payments", "Validate card numbers"]
        }
    )
    print(f"✓ Result keys: {list(result.keys())}")
    assert result["status"] == "success"
    assert "test_cases" in result
    print("✓ All assertions passed")

    # Test 2: Run tests
    print("\n[Test 2] Run Tests")
    print("-" * 80)
    result = qa_tester_agent.tools[1](  # run_tests
        test_cases=result["test_cases"],
        environment="staging"
    )
    print(f"✓ Result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert "test_execution" in result
    print("✓ All assertions passed")


def test_deployer_agent():
    """Test deployer agent with mock inputs."""
    from agents.stage3_cicd.deployment.deployer.agent import deployer_agent

    print("\n" + "="*80)
    print("TESTING: deployer_agent")
    print("="*80)

    # Test 1: Deploy to environment
    print("\n[Test 1] Deploy to Environment")
    print("-" * 80)
    result = deployer_agent.tools[0](  # deploy_to_environment
        service="payment-service",
        environment="staging",
        artifacts={"name": "payment-service", "version": "1.0.0"}
    )
    print(f"✓ Result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert "deployment" in result
    print("✓ All assertions passed")

    # Test 2: Run health checks
    print("\n[Test 2] Run Health Checks")
    print("-" * 80)
    result = deployer_agent.tools[1](  # run_health_checks
        service="payment-service",
        environment="staging"
    )
    print(f"✓ Result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert result["health_checks"]["all_healthy"] == True
    print("✓ All assertions passed")


def test_monitor_agent():
    """Test monitor agent with mock inputs."""
    from agents.stage3_cicd.monitoring.monitor.agent import monitor_agent

    print("\n" + "="*80)
    print("TESTING: monitor_agent")
    print("="*80)

    # Test 1: Collect metrics
    print("\n[Test 1] Collect Metrics")
    print("-" * 80)
    result = monitor_agent.tools[0](  # collect_metrics
        service="payment-service",
        time_range="1h"
    )
    print(f"✓ Result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert "metrics" in result
    print("✓ All assertions passed")

    # Test 2: Check SLA compliance
    print("\n[Test 2] Check SLA Compliance")
    print("-" * 80)
    result = monitor_agent.tools[1](  # check_sla_compliance
        metrics=result["metrics"],
        sla={
            "response_time_p95_ms": 200,
            "error_rate_percent": 0.5,
            "availability": 0.999
        }
    )
    print(f"✓ Result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert "sla_compliance" in result
    print("✓ All assertions passed")


def run_all_tests():
    """Run all agent tests."""
    print("\n" + "#"*80)
    print("# TESTING ALL AGENTS WITH MOCK INPUTS")
    print("#"*80)

    tests = [
        ("Escalation Agent", test_escalation_agent),
        ("Telemetry Agent", test_telemetry_agent),
        ("Discovery Agent", test_discovery_agent),
        ("Domain Expert Agent", test_domain_expert_agent),
        ("Developer Agent", test_developer_agent),
        ("Code Validator Agent", test_code_validator_agent),
        ("Architect Agent", test_architect_agent),
        ("QA Tester Agent", test_qa_tester_agent),
        ("Deployer Agent", test_deployer_agent),
        ("Monitor Agent", test_monitor_agent),
    ]

    passed = 0
    failed = []

    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
            print(f"\n✓ {test_name} - ALL TESTS PASSED\n")
        except Exception as e:
            failed.append((test_name, str(e)))
            print(f"\n✗ {test_name} - FAILED: {e}\n")

    # Summary
    print("\n" + "#"*80)
    print("# TEST SUMMARY")
    print("#"*80)
    print(f"Total Agents Tested: {len(tests)}")
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {len(failed)}")

    if failed:
        print("\nFailed Tests:")
        for agent_name, error in failed:
            print(f"  - {agent_name}: {error}")
    else:
        print("\n🎉 ALL AGENT TESTS PASSED!")

    print("#"*80)

    return len(failed) == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
