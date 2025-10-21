#!/usr/bin/env python3
"""
scripts/test_agents_with_llm.py

Test agents with actual LLM API calls to verify real-world behavior.
Requires: Google Cloud credentials and Vertex AI API enabled.
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Check for Google Cloud credentials
def check_credentials():
    """Check if Google Cloud credentials are available."""
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        print("\n" + "="*80)
        print("⚠️  WARNING: No Google Cloud credentials found")
        print("="*80)
        print("\nTo run these tests, you need to:")
        print("1. Set up a Google Cloud project")
        print("2. Enable Vertex AI API")
        print("3. Create a service account with Vertex AI permissions")
        print("4. Download the JSON key file")
        print("5. Set environment variable:")
        print("   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json")
        print("\nOr authenticate with:")
        print("   gcloud auth application-default login")
        print("="*80)
        return False
    return True


def test_escalation_agent_with_llm():
    """Test escalation agent with real LLM calls."""
    from agents.orchestration.escalation.agent import escalation_agent

    print("\n" + "="*80)
    print("TESTING: escalation_agent (WITH LLM)")
    print("="*80)

    # Test 1: Natural language prompt for analyzing deadlock
    print("\n[Test 1] Analyze Deadlock with Natural Language")
    print("-" * 80)

    prompt = """
    I have a task that has been rejected 3 times by the validator:
    - Attempt 1: Missing error handling
    - Attempt 2: Missing error handling
    - Attempt 3: Missing error handling

    The developer keeps making the same mistake. Can you analyze if this is a deadlock
    and suggest what we should do?
    """

    print(f"Prompt: {prompt.strip()}")
    print("\nInvoking agent with LLM...")

    try:
        # This will use the LLM to understand the prompt and call tools
        response = escalation_agent.query(prompt)
        print(f"\n✓ LLM Response:\n{json.dumps(response, indent=2)}")
        return {"status": "success", "response": response}
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return {"status": "error", "error": str(e)}


def test_discovery_agent_with_llm():
    """Test discovery agent with real LLM calls."""
    from agents.stage0_discovery.discovery.agent import discovery_agent

    print("\n" + "="*80)
    print("TESTING: discovery_agent (WITH LLM)")
    print("="*80)

    # Test 1: Natural language prompt for scanning codebase
    print("\n[Test 1] Scan Legacy Codebase with Natural Language")
    print("-" * 80)

    prompt = """
    I have a legacy COBOL application at /mock/legacy/cobol that I need to modernize.
    Can you scan it and tell me what technology stack it uses? I'm particularly
    interested in finding all the source code files, database schemas, and configuration files.
    """

    print(f"Prompt: {prompt.strip()}")
    print("\nInvoking agent with LLM...")

    try:
        response = discovery_agent.query(prompt)
        print(f"\n✓ LLM Response:\n{json.dumps(response, indent=2)}")
        return {"status": "success", "response": response}
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return {"status": "error", "error": str(e)}


def test_domain_expert_agent_with_llm():
    """Test domain expert agent with real LLM calls."""
    from agents.stage0_discovery.domain_expert.agent import domain_expert_agent

    print("\n" + "="*80)
    print("TESTING: domain_expert_agent (WITH LLM)")
    print("="*80)

    # Test 1: Extract domain knowledge from description
    print("\n[Test 1] Analyze Business Domain from Description")
    print("-" * 80)

    prompt = """
    I have a legacy system that handles customer orders, inventory management,
    and payment processing. It's built in COBOL and has been running for 20 years.

    The main workflows are:
    1. Customer places order
    2. System checks inventory
    3. If stock available, reserves it
    4. Processes payment
    5. Fulfills order

    Can you analyze this and identify the business domain, bounded contexts,
    and key entities? Use Domain-Driven Design principles.
    """

    print(f"Prompt: {prompt.strip()}")
    print("\nInvoking agent with LLM...")

    try:
        response = domain_expert_agent.query(prompt)
        print(f"\n✓ LLM Response:\n{json.dumps(response, indent=2)}")
        return {"status": "success", "response": response}
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return {"status": "error", "error": str(e)}


def test_developer_agent_with_llm():
    """Test developer agent with real LLM calls."""
    from agents.stage2_development.developer.agent import developer_agent

    print("\n" + "="*80)
    print("TESTING: developer_agent (WITH LLM)")
    print("="*80)

    # Test 1: Generate code from natural language
    print("\n[Test 1] Generate Payment Processor Code")
    print("-" * 80)

    prompt = """
    I need you to implement a PaymentProcessor component in Python.

    Requirements:
    - Must validate credit card numbers using Luhn algorithm
    - Must handle different payment methods (credit card, debit card, PayPal)
    - Must include error handling for invalid amounts, expired cards
    - Must log all transactions for audit
    - Must be PCI-DSS compliant (no storing raw card numbers)

    The legacy COBOL system had business rules like:
    - Minimum payment amount is $1.00
    - Maximum single transaction is $50,000
    - Refunds allowed within 30 days

    Please generate the Python code with unit tests.
    """

    print(f"Prompt: {prompt.strip()}")
    print("\nInvoking agent with LLM...")

    try:
        response = developer_agent.query(prompt)
        print(f"\n✓ LLM Response:")
        print(f"Generated {len(response.get('code', ''))} characters of code")
        if 'code' in response:
            print(f"\nCode preview (first 500 chars):")
            print(response['code'][:500] + "...")
        return {"status": "success", "response": response}
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return {"status": "error", "error": str(e)}


def test_code_validator_agent_with_llm():
    """Test code validator agent with real LLM calls."""
    from agents.stage2_development.validation.code_validator.agent import code_validator_agent

    print("\n" + "="*80)
    print("TESTING: code_validator_agent (WITH LLM)")
    print("="*80)

    # Test 1: Validate code with security issues
    print("\n[Test 1] Validate Code for Security Issues")
    print("-" * 80)

    code_to_validate = '''
def process_payment(user_input):
    # BAD: SQL injection vulnerability
    query = f"SELECT * FROM payments WHERE user_id = {user_input}"

    # BAD: No input validation
    amount = user_input['amount']

    # BAD: Storing raw credit card number
    card_number = user_input['card']

    return {"status": "success"}
'''

    prompt = f"""
    Please validate this payment processing code for security issues, correctness,
    and best practices:

    {code_to_validate}

    Check for:
    - SQL injection vulnerabilities
    - Input validation
    - PCI-DSS compliance
    - Error handling
    - Code quality

    Tell me if it passes validation or what needs to be fixed.
    """

    print(f"Prompt: {prompt.strip()}")
    print("\nInvoking agent with LLM...")

    try:
        response = code_validator_agent.query(prompt)
        print(f"\n✓ LLM Response:\n{json.dumps(response, indent=2)}")
        return {"status": "success", "response": response}
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return {"status": "error", "error": str(e)}


def test_architect_agent_with_llm():
    """Test architect agent with real LLM calls."""
    from agents.stage2_development.architecture.architect.agent import architect_agent

    print("\n" + "="*80)
    print("TESTING: architect_agent (WITH LLM)")
    print("="*80)

    # Test 1: Design microservices architecture
    print("\n[Test 1] Design Microservices Architecture")
    print("-" * 80)

    prompt = """
    I'm modernizing a monolithic COBOL application to microservices.

    The system has these components:
    - Order Management (handles customer orders)
    - Inventory Management (tracks stock levels)
    - Payment Processing (processes payments)
    - Shipping (manages fulfillment)
    - Customer Management (customer data)

    Non-functional requirements:
    - Must handle 10,000 requests/second
    - 99.9% availability
    - Response time < 100ms p95
    - PCI-DSS compliant for payments
    - GDPR compliant for customer data

    Please design a microservices architecture with:
    - Service boundaries
    - Communication patterns (sync/async)
    - Data storage strategy
    - Deployment architecture
    """

    print(f"Prompt: {prompt.strip()}")
    print("\nInvoking agent with LLM...")

    try:
        response = architect_agent.query(prompt)
        print(f"\n✓ LLM Response:\n{json.dumps(response, indent=2)}")
        return {"status": "success", "response": response}
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return {"status": "error", "error": str(e)}


def test_qa_tester_agent_with_llm():
    """Test QA tester agent with real LLM calls."""
    from agents.stage2_development.qa.tester.agent import qa_tester_agent

    print("\n" + "="*80)
    print("TESTING: qa_tester_agent (WITH LLM)")
    print("="*80)

    # Test 1: Generate test cases from requirements
    print("\n[Test 1] Generate Test Cases from Requirements")
    print("-" * 80)

    prompt = """
    I need test cases for a PaymentProcessor component with these requirements:

    Functional Requirements:
    - Process credit card payments
    - Validate card numbers using Luhn algorithm
    - Support multiple payment methods (credit, debit, PayPal)
    - Calculate tax based on billing address
    - Apply discount codes

    Business Rules:
    - Minimum payment: $1.00
    - Maximum payment: $50,000
    - Discounts cannot exceed 50% of order total
    - Refunds allowed within 30 days

    Please generate:
    1. Functional test cases (happy path)
    2. Negative test cases (error conditions)
    3. Edge cases (boundary conditions)
    4. Security test cases

    For each test case, provide: test ID, description, steps, and expected result.
    """

    print(f"Prompt: {prompt.strip()}")
    print("\nInvoking agent with LLM...")

    try:
        response = qa_tester_agent.query(prompt)
        print(f"\n✓ LLM Response:")
        if isinstance(response, dict) and 'test_cases' in response:
            print(f"Generated {len(response['test_cases'])} test cases")
            print(f"\nFirst test case:")
            print(json.dumps(response['test_cases'][0], indent=2))
        else:
            print(json.dumps(response, indent=2))
        return {"status": "success", "response": response}
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return {"status": "error", "error": str(e)}


def run_all_llm_tests():
    """Run all agent tests with LLM."""
    print("\n" + "#"*80)
    print("# TESTING ALL AGENTS WITH LLM API CALLS")
    print("#"*80)

    # Check credentials first
    if not check_credentials():
        print("\n❌ Cannot proceed without Google Cloud credentials")
        print("Set up credentials and try again.")
        return False

    print("\n✓ Google Cloud credentials found")
    print("Proceeding with LLM tests...")

    tests = [
        ("Escalation Agent", test_escalation_agent_with_llm),
        ("Discovery Agent", test_discovery_agent_with_llm),
        ("Domain Expert Agent", test_domain_expert_agent_with_llm),
        ("Developer Agent", test_developer_agent_with_llm),
        ("Code Validator Agent", test_code_validator_agent_with_llm),
        ("Architect Agent", test_architect_agent_with_llm),
        ("QA Tester Agent", test_qa_tester_agent_with_llm),
    ]

    results = []
    passed = 0
    failed = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            if result.get("status") == "success":
                passed += 1
                print(f"\n✓ {test_name} - LLM TEST PASSED\n")
            else:
                failed.append((test_name, result.get("error", "Unknown error")))
                print(f"\n✗ {test_name} - LLM TEST FAILED\n")
            results.append(result)
        except Exception as e:
            failed.append((test_name, str(e)))
            print(f"\n✗ {test_name} - LLM TEST FAILED: {e}\n")

    # Summary
    print("\n" + "#"*80)
    print("# LLM TEST SUMMARY")
    print("#"*80)
    print(f"Total Agents Tested: {len(tests)}")
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {len(failed)}")

    if failed:
        print("\nFailed Tests:")
        for agent_name, error in failed:
            print(f"  - {agent_name}: {error}")
    else:
        print("\n🎉 ALL LLM AGENT TESTS PASSED!")

    print("#"*80)

    # Save results
    output_dir = Path("tests/agent_tests/results")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"llm_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(tests),
            "passed": passed,
            "failed": len(failed),
            "results": results
        }, f, indent=2)

    print(f"\n📄 Results saved to: {output_file}")

    return len(failed) == 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test agents with LLM API calls")
    parser.add_argument(
        "--agent",
        help="Agent to test (or 'all' for all agents)",
        choices=[
            "all",
            "escalation",
            "discovery",
            "domain_expert",
            "developer",
            "code_validator",
            "architect",
            "qa_tester"
        ]
    )

    args = parser.parse_args()

    if args.agent == "all" or not args.agent:
        success = run_all_llm_tests()
        sys.exit(0 if success else 1)
    else:
        # Run individual test
        test_map = {
            "escalation": test_escalation_agent_with_llm,
            "discovery": test_discovery_agent_with_llm,
            "domain_expert": test_domain_expert_agent_with_llm,
            "developer": test_developer_agent_with_llm,
            "code_validator": test_code_validator_agent_with_llm,
            "architect": test_architect_agent_with_llm,
            "qa_tester": test_qa_tester_agent_with_llm,
        }

        if args.agent in test_map:
            if not check_credentials():
                print("\n❌ Cannot proceed without Google Cloud credentials")
                sys.exit(1)

            result = test_map[args.agent]()
            sys.exit(0 if result.get("status") == "success" else 1)
        else:
            print(f"Unknown agent: {args.agent}")
            sys.exit(1)
