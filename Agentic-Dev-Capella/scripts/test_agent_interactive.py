#!/usr/bin/env python3
"""
scripts/test_agent_interactive.py

Interactive CLI tool for testing individual agents with custom prompts.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.agent_tests.agent_test_framework import (
    AgentTestRunner,
    AgentTestCase,
    create_validation_function
)

# Import agents
from agents.orchestration.escalation.agent import escalation_agent
from agents.orchestration.telemetry.agent import telemetry_agent
from agents.stage0_discovery.discovery.agent import discovery_agent
from agents.stage2_development.developer.agent import developer_agent


class InteractiveAgentTester:
    """Interactive CLI for testing agents."""

    def __init__(self):
        """Initialize interactive tester."""
        self.agents = {
            "escalation_agent": escalation_agent,
            "telemetry_audit_agent": telemetry_agent,
            "discovery_agent": discovery_agent,
            "developer_agent": developer_agent
        }

        # Agent tool information
        self.agent_tools = {
            "escalation_agent": [
                ("analyze_rejection_pattern", "Analyze rejection patterns"),
                ("determine_resolution_strategy", "Determine resolution strategy"),
                ("create_escalation_report", "Create escalation report"),
                ("request_human_approval", "Request human approval")
            ],
            "telemetry_audit_agent": [
                ("log_agent_activity", "Log agent activity"),
                ("track_task_metrics", "Track task metrics"),
                ("generate_audit_report", "Generate audit report"),
                ("track_validation_event", "Track validation event"),
                ("monitor_system_health", "Monitor system health")
            ],
            "discovery_agent": [
                ("scan_codebase", "Scan legacy codebase"),
                ("identify_components", "Identify components"),
                ("analyze_dependencies", "Analyze dependencies"),
                ("estimate_complexity", "Estimate complexity")
            ],
            "developer_agent": [
                ("query_vector_db", "Query Vector DB"),
                ("implement_component", "Implement component"),
                ("refactor_existing_code", "Refactor code"),
                ("generate_migration_script", "Generate migration script"),
                ("handle_cross_cutting_concerns", "Handle cross-cutting concerns")
            ]
        }

    def run(self):
        """Run interactive testing session."""
        print("\n" + "="*80)
        print("INTERACTIVE AGENT TESTER")
        print("="*80)
        print("\nTest individual agents with custom prompts and inputs")
        print("Type 'quit' or 'exit' at any time to exit\n")

        while True:
            # Select agent
            agent_name = self._select_agent()
            if not agent_name:
                break

            # Select tool
            tool_info = self._select_tool(agent_name)
            if not tool_info:
                continue

            # Get test input
            test_case = self._create_test_case(agent_name, tool_info)
            if not test_case:
                continue

            # Run test
            self._run_test(agent_name, test_case)

            # Ask if continue
            continue_testing = input("\n\nTest another agent? (y/n): ").strip().lower()
            if continue_testing != 'y':
                break

        print("\n✓ Testing session complete!\n")

    def _select_agent(self) -> Optional[str]:
        """Prompt user to select an agent."""
        print("\n" + "-"*80)
        print("SELECT AGENT TO TEST")
        print("-"*80)

        agents_list = list(self.agents.keys())
        for i, agent_name in enumerate(agents_list, 1):
            print(f"{i}. {agent_name}")

        choice = input("\nSelect agent (1-{}): ".format(len(agents_list))).strip()

        if choice.lower() in ['quit', 'exit']:
            return None

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(agents_list):
                return agents_list[idx]
            else:
                print("Invalid choice")
                return self._select_agent()
        except ValueError:
            print("Invalid input")
            return self._select_agent()

    def _select_tool(self, agent_name: str) -> Optional[tuple]:
        """Prompt user to select a tool."""
        print("\n" + "-"*80)
        print(f"SELECT TOOL FOR {agent_name}")
        print("-"*80)

        tools = self.agent_tools.get(agent_name, [])
        for i, (tool_name, description) in enumerate(tools, 1):
            print(f"{i}. {tool_name} - {description}")

        choice = input(f"\nSelect tool (1-{len(tools)}): ").strip()

        if choice.lower() in ['quit', 'exit']:
            return None

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(tools):
                return tools[idx]
            else:
                print("Invalid choice")
                return self._select_tool(agent_name)
        except ValueError:
            print("Invalid input")
            return self._select_tool(agent_name)

    def _create_test_case(self, agent_name: str, tool_info: tuple) -> Optional[AgentTestCase]:
        """Prompt user to create a test case."""
        tool_name, tool_description = tool_info

        print("\n" + "-"*80)
        print(f"CREATE TEST CASE FOR {tool_name}")
        print("-"*80)

        # Get test name
        test_name = input("\nTest name: ").strip()
        if not test_name:
            test_name = f"Test {tool_name}"

        # Get description
        description = input("Description: ").strip()
        if not description:
            description = f"Test {tool_description}"

        # Get prompt
        print("\nInput prompt (natural language description):")
        prompt = input("> ").strip()
        if not prompt:
            prompt = f"Test {tool_name} with sample data"

        # Get input data
        print("\nInput data (JSON format):")
        print("Example: {\"task_id\": \"test_001\", \"component_id\": \"payment_processor\"}")
        print("(Or press Enter for guided input)")

        json_input = input("> ").strip()

        if json_input:
            try:
                input_data = json.loads(json_input)
            except json.JSONDecodeError:
                print("Invalid JSON, using guided input instead")
                input_data = self._guided_input(tool_name)
        else:
            input_data = self._guided_input(tool_name)

        # Create test case
        test_case = AgentTestCase(
            test_id=f"interactive_{tool_name}",
            test_name=test_name,
            description=description,
            input_prompt=prompt,
            input_data=input_data,
            expected_status="success"
        )

        return test_case

    def _guided_input(self, tool_name: str) -> Dict[str, Any]:
        """Guide user through input creation."""
        print("\nGuided input creation:")

        # Common fields for most tools
        input_data = {}

        # Task ID (common)
        task_id = input("Task ID (press Enter to skip): ").strip()
        if task_id:
            input_data["task_id"] = task_id

        # Component ID (common)
        component_id = input("Component ID (press Enter to skip): ").strip()
        if component_id:
            input_data["component_id"] = component_id

        # Tool-specific fields
        if "rejection" in tool_name.lower():
            print("\nRejection history (enter 'done' when finished):")
            rejection_history = []
            attempt = 1
            while True:
                reason = input(f"  Rejection {attempt} reason (or 'done'): ").strip()
                if reason.lower() == 'done':
                    break
                rejection_history.append({"reason": reason, "attempt": attempt})
                attempt += 1
            if rejection_history:
                input_data["rejection_history"] = rejection_history

        elif "implement" in tool_name.lower():
            language = input("Output language (python/cpp/java): ").strip() or "python"
            input_data["output_language"] = language
            input_data["architecture_spec"] = {
                "component_name": input_data.get("component_id", "Component"),
                "language": language
            }
            input_data["legacy_context"] = {}

        elif "refactor" in tool_name.lower():
            code = input("Code to refactor: ").strip()
            if code:
                input_data["existing_code"] = code
            input_data["refactor_goals"] = ["modernize", "improve_maintainability"]

        # Add any additional fields
        print("\nAdd additional fields? (y/n): ", end="")
        if input().strip().lower() == 'y':
            while True:
                key = input("  Field name (or 'done'): ").strip()
                if key.lower() == 'done':
                    break
                value = input(f"  Value for '{key}': ").strip()
                try:
                    # Try to parse as JSON
                    input_data[key] = json.loads(value)
                except:
                    # Use as string
                    input_data[key] = value

        return input_data

    def _run_test(self, agent_name: str, test_case: AgentTestCase):
        """Run the test case."""
        agent = self.agents[agent_name]
        runner = AgentTestRunner(agent, agent_name)

        print("\n" + "="*80)
        print("RUNNING TEST")
        print("="*80)

        result = runner.run_test_case(test_case)

        # Display result
        print("\n" + "-"*80)
        print("TEST RESULT")
        print("-"*80)
        print(f"Status: {result.status}")
        print(f"Execution Time: {result.execution_time_seconds:.2f}s")

        if result.actual_output:
            print("\nOutput:")
            print(json.dumps(result.actual_output, indent=2))

        if result.error_message:
            print(f"\nError: {result.error_message}")

        # Save option
        save = input("\nSave result to file? (y/n): ").strip().lower()
        if save == 'y':
            output_path = f"tests/agent_tests/results/interactive_{agent_name}_{test_case.test_id}.json"
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            runner.save_results(output_path)


def main():
    """Main entry point."""
    tester = InteractiveAgentTester()
    tester.run()


if __name__ == "__main__":
    main()
