"""
tests/agent_tests/agent_test_framework.py

Framework for testing individual agents with prompt-based inputs.
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@dataclass
class AgentTestCase:
    """Single test case for an agent."""
    test_id: str
    test_name: str
    description: str
    input_prompt: str
    input_data: Dict[str, Any]
    expected_status: str = "success"
    expected_fields: List[str] = field(default_factory=list)
    validation_function: Optional[Callable] = None
    timeout_seconds: int = 30


@dataclass
class AgentTestResult:
    """Result of running an agent test."""
    test_case: AgentTestCase
    status: str  # passed, failed, error
    actual_output: Optional[Dict[str, Any]] = None
    execution_time_seconds: float = 0.0
    error_message: Optional[str] = None
    validation_details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class AgentTestRunner:
    """
    Test runner for individual agents.

    Allows testing agents with specific prompts and validating outputs.
    """

    def __init__(self, agent, agent_name: str):
        """
        Initialize test runner.

        Args:
            agent: Agent instance to test
            agent_name: Name of the agent
        """
        self.agent = agent
        self.agent_name = agent_name
        self.test_results: List[AgentTestResult] = []

    def run_test_case(self, test_case: AgentTestCase) -> AgentTestResult:
        """
        Run a single test case.

        Args:
            test_case: Test case to run

        Returns:
            AgentTestResult with test outcome
        """
        print(f"\n{'='*80}")
        print(f"Running: {test_case.test_name}")
        print(f"{'='*80}")
        print(f"Description: {test_case.description}")
        print(f"\nInput Prompt:")
        print(f"  {test_case.input_prompt}")
        print(f"\nInput Data:")
        for key, value in test_case.input_data.items():
            print(f"  {key}: {value}")
        print()

        import time
        start_time = time.time()

        try:
            # Run the agent with the test input
            # Note: This is a simplified version. In production, you'd invoke
            # the actual agent through Vertex AI or the ADK
            result = self._invoke_agent_tool(test_case)

            execution_time = time.time() - start_time

            # Validate result
            validation_result = self._validate_result(test_case, result)

            if validation_result["valid"]:
                status = "passed"
                print(f"✓ TEST PASSED ({execution_time:.2f}s)")
            else:
                status = "failed"
                print(f"✗ TEST FAILED ({execution_time:.2f}s)")
                print(f"  Reason: {validation_result['reason']}")

            test_result = AgentTestResult(
                test_case=test_case,
                status=status,
                actual_output=result,
                execution_time_seconds=execution_time,
                validation_details=validation_result
            )

        except Exception as e:
            execution_time = time.time() - start_time
            status = "error"
            print(f"✗ TEST ERROR ({execution_time:.2f}s)")
            print(f"  Error: {str(e)}")

            test_result = AgentTestResult(
                test_case=test_case,
                status=status,
                execution_time_seconds=execution_time,
                error_message=str(e)
            )

        self.test_results.append(test_result)
        return test_result

    def _invoke_agent_tool(self, test_case: AgentTestCase) -> Dict[str, Any]:
        """
        Invoke agent tool with test inputs.

        Args:
            test_case: Test case

        Returns:
            Agent output
        """
        # Get the first tool from the agent (simplified)
        if hasattr(self.agent, 'tools') and self.agent.tools:
            tool = self.agent.tools[0]

            # Call the tool with input data
            result = tool(**test_case.input_data)
            return result
        else:
            raise ValueError(f"Agent {self.agent_name} has no tools")

    def _validate_result(
        self,
        test_case: AgentTestCase,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate agent output against test case expectations.

        Args:
            test_case: Test case with expectations
            result: Actual agent output

        Returns:
            Validation result dict
        """
        validation = {
            "valid": True,
            "reason": None,
            "checks": []
        }

        # Check expected status
        if result.get("status") != test_case.expected_status:
            validation["valid"] = False
            validation["reason"] = (
                f"Expected status '{test_case.expected_status}', "
                f"got '{result.get('status')}'"
            )
            validation["checks"].append({
                "check": "status",
                "expected": test_case.expected_status,
                "actual": result.get("status"),
                "passed": False
            })
        else:
            validation["checks"].append({
                "check": "status",
                "expected": test_case.expected_status,
                "actual": result.get("status"),
                "passed": True
            })

        # Check expected fields
        for field in test_case.expected_fields:
            if field not in result:
                validation["valid"] = False
                validation["reason"] = f"Missing expected field: {field}"
                validation["checks"].append({
                    "check": f"field_{field}",
                    "expected": "present",
                    "actual": "missing",
                    "passed": False
                })
            else:
                validation["checks"].append({
                    "check": f"field_{field}",
                    "expected": "present",
                    "actual": "present",
                    "passed": True
                })

        # Custom validation function
        if test_case.validation_function:
            try:
                custom_result = test_case.validation_function(result)
                if not custom_result.get("valid", True):
                    validation["valid"] = False
                    validation["reason"] = custom_result.get("reason", "Custom validation failed")
                validation["checks"].append({
                    "check": "custom_validation",
                    "passed": custom_result.get("valid", True),
                    "details": custom_result.get("details")
                })
            except Exception as e:
                validation["valid"] = False
                validation["reason"] = f"Custom validation error: {str(e)}"

        return validation

    def run_test_suite(self, test_cases: List[AgentTestCase]) -> Dict[str, Any]:
        """
        Run multiple test cases.

        Args:
            test_cases: List of test cases to run

        Returns:
            Test suite results summary
        """
        print(f"\n{'#'*80}")
        print(f"# TESTING AGENT: {self.agent_name}")
        print(f"# Test Cases: {len(test_cases)}")
        print(f"{'#'*80}")

        for test_case in test_cases:
            self.run_test_case(test_case)

        # Generate summary
        passed = sum(1 for r in self.test_results if r.status == "passed")
        failed = sum(1 for r in self.test_results if r.status == "failed")
        errors = sum(1 for r in self.test_results if r.status == "error")
        total = len(self.test_results)

        summary = {
            "agent_name": self.agent_name,
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "success_rate": (passed / total * 100) if total > 0 else 0,
            "test_results": [
                {
                    "test_id": r.test_case.test_id,
                    "test_name": r.test_case.test_name,
                    "status": r.status,
                    "execution_time": r.execution_time_seconds,
                    "error": r.error_message
                }
                for r in self.test_results
            ]
        }

        # Print summary
        print(f"\n{'='*80}")
        print(f"TEST SUMMARY: {self.agent_name}")
        print(f"{'='*80}")
        print(f"Total Tests:   {total}")
        print(f"✓ Passed:      {passed}")
        print(f"✗ Failed:      {failed}")
        print(f"⚠ Errors:      {errors}")
        print(f"Success Rate:  {summary['success_rate']:.1f}%")
        print(f"{'='*80}")

        return summary

    def save_results(self, output_path: str):
        """
        Save test results to JSON file.

        Args:
            output_path: Path to save results
        """
        results = {
            "agent_name": self.agent_name,
            "timestamp": datetime.utcnow().isoformat(),
            "test_results": [
                {
                    "test_case": {
                        "test_id": r.test_case.test_id,
                        "test_name": r.test_case.test_name,
                        "description": r.test_case.description,
                        "input_prompt": r.test_case.input_prompt,
                        "input_data": r.test_case.input_data
                    },
                    "status": r.status,
                    "actual_output": r.actual_output,
                    "execution_time_seconds": r.execution_time_seconds,
                    "error_message": r.error_message,
                    "validation_details": r.validation_details,
                    "timestamp": r.timestamp
                }
                for r in self.test_results
            ]
        }

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n✓ Test results saved to: {output_path}")


class AgentTestSuite:
    """
    Collection of test cases for an agent.

    Organizes tests by category and provides easy test case creation.
    """

    def __init__(self, agent_name: str):
        """
        Initialize test suite.

        Args:
            agent_name: Name of agent being tested
        """
        self.agent_name = agent_name
        self.test_cases: List[AgentTestCase] = []

    def add_test(
        self,
        test_id: str,
        test_name: str,
        description: str,
        input_prompt: str,
        input_data: Dict[str, Any],
        expected_status: str = "success",
        expected_fields: Optional[List[str]] = None,
        validation_function: Optional[Callable] = None
    ):
        """
        Add a test case to the suite.

        Args:
            test_id: Unique test identifier
            test_name: Human-readable test name
            description: Test description
            input_prompt: Natural language prompt describing what to test
            input_data: Input data for the agent
            expected_status: Expected status in result
            expected_fields: Expected fields in result
            validation_function: Custom validation function
        """
        test_case = AgentTestCase(
            test_id=test_id,
            test_name=test_name,
            description=description,
            input_prompt=input_prompt,
            input_data=input_data,
            expected_status=expected_status,
            expected_fields=expected_fields or [],
            validation_function=validation_function
        )

        self.test_cases.append(test_case)

    def get_test_cases(self) -> List[AgentTestCase]:
        """Get all test cases."""
        return self.test_cases


def create_validation_function(
    min_length: Optional[int] = None,
    required_keys: Optional[List[str]] = None,
    custom_checks: Optional[List[Callable]] = None
) -> Callable:
    """
    Create a validation function with common checks.

    Args:
        min_length: Minimum length for string results
        required_keys: Required keys in result
        custom_checks: List of custom check functions

    Returns:
        Validation function
    """
    def validate(result: Dict[str, Any]) -> Dict[str, Any]:
        validation = {"valid": True, "details": []}

        # Check minimum length
        if min_length:
            for key, value in result.items():
                if isinstance(value, str) and len(value) < min_length:
                    validation["valid"] = False
                    validation["reason"] = f"Field '{key}' too short: {len(value)} < {min_length}"
                    return validation

        # Check required keys
        if required_keys:
            for key in required_keys:
                if key not in result:
                    validation["valid"] = False
                    validation["reason"] = f"Missing required key: {key}"
                    return validation

        # Custom checks
        if custom_checks:
            for check in custom_checks:
                check_result = check(result)
                if not check_result:
                    validation["valid"] = False
                    validation["reason"] = "Custom check failed"
                    return validation

        return validation

    return validate
