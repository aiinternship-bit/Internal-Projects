"""
examples/a2a_usage_example.py

Comprehensive examples showing how to use A2A communication in agents.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.utils.vertex_a2a_protocol import (
    VertexA2AMessageBus,
    A2AProtocolHelper,
    A2AMessageType,
    A2AMessage
)
from shared.utils.a2a_integration import (
    A2AIntegration,
    ValidationLoopHandler,
    create_a2a_integration
)
from shared.utils.agent_base import AgentContext, create_agent_context


# ============================================================================
# Example 1: Basic A2A Communication Between Agents
# ============================================================================

def example_basic_a2a_communication():
    """
    Example: Basic message passing between orchestrator and developer agent.
    """
    print("=" * 80)
    print("Example 1: Basic A2A Communication")
    print("=" * 80)

    # Initialize message bus
    project_id = "your-project-id"
    message_bus = VertexA2AMessageBus(
        project_id=project_id,
        topic_name="legacy-modernization-messages"
    )

    # Create agent contexts
    orchestrator_id = f"projects/{project_id}/locations/us-central1/agents/orchestrator"
    developer_id = f"projects/{project_id}/locations/us-central1/agents/developer"

    # Send task assignment from orchestrator to developer
    task_message = A2AProtocolHelper.create_task_assignment(
        sender_id=orchestrator_id,
        sender_name="orchestrator_agent",
        recipient_id=developer_id,
        recipient_name="developer_agent",
        task_data={
            "task_id": "dev_001",
            "task_type": "development",
            "component_id": "payment_processor",
            "architecture_spec": {
                "component_name": "PaymentProcessor",
                "language": "python",
                "patterns": ["repository", "dependency_injection"],
                "nfrs": {
                    "performance": "< 100ms p95",
                    "security": "PCI-DSS compliant"
                }
            }
        }
    )

    # Publish message
    message_id = message_bus.publish_message(task_message)
    print(f"✓ Task assigned to developer: {message_id}")
    print(f"  Task ID: dev_001")
    print(f"  Component: payment_processor")


# ============================================================================
# Example 2: Validation Loop with Retry
# ============================================================================

def example_validation_loop():
    """
    Example: Developer submits code for validation with automatic retry.
    """
    print("\n" + "=" * 80)
    print("Example 2: Validation Loop with Retry")
    print("=" * 80)

    project_id = "your-project-id"
    message_bus = VertexA2AMessageBus(project_id=project_id)

    # Create A2A integration for developer agent
    developer_context = create_agent_context(
        agent_name="developer_agent",
        project_id=project_id
    )

    a2a = A2AIntegration(
        agent_context=developer_context,
        message_bus=message_bus,
        orchestrator_id=f"projects/{project_id}/locations/us-central1/agents/orchestrator"
    )

    # Create validation loop handler
    validator_id = f"projects/{project_id}/locations/us-central1/agents/code_validator"
    validation_handler = ValidationLoopHandler(
        a2a_integration=a2a,
        max_retries=3,
        escalation_agent_id=f"projects/{project_id}/locations/us-central1/agents/escalation"
    )

    # Simulated artifact generator (would incorporate feedback in real implementation)
    def generate_code_artifact(feedback: str = None) -> Dict[str, Any]:
        """Generate code artifact, incorporating feedback if provided."""
        code = """
def process_payment(amount: float, currency: str) -> dict:
    # Validate inputs
    if amount <= 0:
        raise ValueError("Amount must be positive")

    # Process payment
    result = {"status": "success", "amount": amount, "currency": currency}
    return result
"""
        if feedback:
            print(f"  Incorporating feedback: {feedback}")
            # In real implementation, would use AI to incorporate feedback

        return {
            "type": "code",
            "content": code,
            "language": "python",
            "component": "payment_processor"
        }

    # Run validation loop
    print("\nStarting validation loop...")
    result = validation_handler.validate_with_retry(
        task_id="dev_001",
        validator_id=validator_id,
        validator_name="code_validator_agent",
        artifact_generator=generate_code_artifact,
        validation_criteria=["correctness", "security", "error_handling"]
    )

    print(f"\n✓ Validation result: {result['status']}")
    print(f"  Retry count: {result.get('retry_count', 0)}")


# ============================================================================
# Example 3: Task Tracking with Automatic Updates
# ============================================================================

def example_task_tracking():
    """
    Example: Automatic task tracking with state updates to orchestrator.
    """
    print("\n" + "=" * 80)
    print("Example 3: Automatic Task Tracking")
    print("=" * 80)

    from typing import Dict, Any

    project_id = "your-project-id"
    message_bus = VertexA2AMessageBus(project_id=project_id)

    # Create A2A integration
    architect_context = create_agent_context(
        agent_name="architect_agent",
        project_id=project_id
    )

    a2a = A2AIntegration(
        agent_context=architect_context,
        message_bus=message_bus,
        orchestrator_id=f"projects/{project_id}/locations/us-central1/agents/orchestrator"
    )

    # Define a tool function with automatic task tracking
    @a2a.with_task_tracking
    def design_architecture(task_id: str, component_id: str, **kwargs) -> Dict[str, Any]:
        """Design architecture for a component."""
        print(f"\n  Designing architecture for {component_id}...")

        # Simulate work
        import time
        time.sleep(1)

        architecture_spec = {
            "component_id": component_id,
            "component_name": "PaymentProcessor",
            "architecture_pattern": "microservice",
            "technology_stack": {
                "language": "python",
                "framework": "fastapi",
                "database": "postgresql"
            },
            "nfrs": {
                "performance": "< 100ms p95",
                "scalability": "horizontal scaling",
                "security": "PCI-DSS compliant",
                "reliability": "99.9% uptime"
            }
        }

        return {
            "status": "success",
            "architecture_spec": architecture_spec
        }

    # Execute tool - automatically sends state updates
    print("\nExecuting design_architecture with automatic tracking...")
    result = design_architecture(
        task_id="arch_001",
        component_id="payment_processor"
    )

    print(f"\n✓ Architecture designed")
    print(f"  Automatic state updates sent:")
    print(f"    - Task started (pending → in_progress)")
    print(f"    - Task completed (in_progress → completed)")


# ============================================================================
# Example 4: Error Reporting
# ============================================================================

def example_error_reporting():
    """
    Example: Automatic error reporting when tasks fail.
    """
    print("\n" + "=" * 80)
    print("Example 4: Automatic Error Reporting")
    print("=" * 80)

    from typing import Dict, Any

    project_id = "your-project-id"
    message_bus = VertexA2AMessageBus(project_id=project_id)

    # Create A2A integration
    qa_context = create_agent_context(
        agent_name="qa_agent",
        project_id=project_id
    )

    a2a = A2AIntegration(
        agent_context=qa_context,
        message_bus=message_bus,
        orchestrator_id=f"projects/{project_id}/locations/us-central1/agents/orchestrator"
    )

    # Define a tool that might fail
    @a2a.with_task_tracking
    def run_tests(task_id: str, test_suite: str, **kwargs) -> Dict[str, Any]:
        """Run test suite."""
        print(f"\n  Running test suite: {test_suite}...")

        # Simulate test failure
        raise RuntimeError(f"Test suite '{test_suite}' failed: 3 tests failed")

    # Execute tool - automatically reports error
    print("\nExecuting run_tests (will fail and report error)...")
    try:
        result = run_tests(
            task_id="qa_001",
            test_suite="integration_tests"
        )
    except RuntimeError as e:
        print(f"\n✓ Error occurred: {e}")
        print(f"  Automatic error report sent:")
        print(f"    - Error message: {str(e)}")
        print(f"    - Task state updated: in_progress → failed")
        print(f"    - Orchestrator notified")


# ============================================================================
# Example 5: Multi-Agent Workflow
# ============================================================================

def example_multi_agent_workflow():
    """
    Example: Complete workflow with multiple agents communicating.

    Flow: Orchestrator → Architect → Developer → Code Validator → QA
    """
    print("\n" + "=" * 80)
    print("Example 5: Multi-Agent Workflow")
    print("=" * 80)

    project_id = "your-project-id"
    message_bus = VertexA2AMessageBus(project_id=project_id)

    # Agent IDs
    orchestrator_id = f"projects/{project_id}/locations/us-central1/agents/orchestrator"
    architect_id = f"projects/{project_id}/locations/us-central1/agents/architect"
    developer_id = f"projects/{project_id}/locations/us-central1/agents/developer"
    validator_id = f"projects/{project_id}/locations/us-central1/agents/code_validator"
    qa_id = f"projects/{project_id}/locations/us-central1/agents/qa"

    print("\nWorkflow Steps:")
    print("-" * 80)

    # Step 1: Orchestrator → Architect
    print("\n1. Orchestrator assigns architecture task to Architect")
    arch_task = A2AProtocolHelper.create_task_assignment(
        sender_id=orchestrator_id,
        sender_name="orchestrator_agent",
        recipient_id=architect_id,
        recipient_name="architect_agent",
        task_data={
            "task_id": "workflow_001_arch",
            "component_id": "payment_processor"
        }
    )
    message_bus.publish_message(arch_task)
    print("   ✓ Task assigned")

    # Step 2: Architect → Developer
    print("\n2. Architect completes design, sends spec to Developer")
    dev_task = A2AProtocolHelper.create_task_assignment(
        sender_id=architect_id,
        sender_name="architect_agent",
        recipient_id=developer_id,
        recipient_name="developer_agent",
        task_data={
            "task_id": "workflow_001_dev",
            "component_id": "payment_processor",
            "architecture_spec": {
                "pattern": "microservice",
                "language": "python"
            }
        }
    )
    message_bus.publish_message(dev_task)
    print("   ✓ Architecture spec sent")

    # Step 3: Developer → Code Validator
    print("\n3. Developer submits code for validation")
    validation_request = A2AProtocolHelper.create_validation_request(
        sender_id=developer_id,
        sender_name="developer_agent",
        validator_id=validator_id,
        validator_name="code_validator_agent",
        artifact={
            "task_id": "workflow_001_dev",
            "type": "code",
            "content": "# Generated code here",
            "criteria": ["correctness", "security"]
        }
    )
    message_bus.publish_message(validation_request)
    print("   ✓ Validation requested")

    # Step 4: Validator → Developer (validation result)
    print("\n4. Validator returns validation result")
    validation_result = A2AProtocolHelper.create_validation_result(
        validator_id=validator_id,
        validator_name="code_validator_agent",
        recipient_id=developer_id,
        recipient_name="developer_agent",
        task_id="workflow_001_dev",
        passed=True,
        issues=[],
        feedback="Code looks good, all checks passed"
    )
    message_bus.publish_message(validation_result)
    print("   ✓ Validation passed")

    # Step 5: Developer → QA
    print("\n5. Developer sends validated code to QA for testing")
    qa_task = A2AProtocolHelper.create_task_assignment(
        sender_id=developer_id,
        sender_name="developer_agent",
        recipient_id=qa_id,
        recipient_name="qa_agent",
        task_data={
            "task_id": "workflow_001_qa",
            "component_id": "payment_processor",
            "code_artifact": "# Validated code"
        }
    )
    message_bus.publish_message(qa_task)
    print("   ✓ QA task assigned")

    # Step 6: QA → Orchestrator (completion)
    print("\n6. QA completes testing, notifies Orchestrator")
    completion_update = A2AProtocolHelper.create_state_update(
        sender_id=qa_id,
        sender_name="qa_agent",
        orchestrator_id=orchestrator_id,
        task_id="workflow_001",
        old_status="qa_in_progress",
        new_status="completed",
        metadata={
            "test_results": "all_passed",
            "coverage": "92%"
        }
    )
    message_bus.publish_message(completion_update)
    print("   ✓ Workflow completed")

    print("\n" + "-" * 80)
    print("✓ Multi-agent workflow completed successfully!")


# ============================================================================
# Example 6: Escalation Handling
# ============================================================================

def example_escalation():
    """
    Example: Escalation after repeated validation failures.
    """
    print("\n" + "=" * 80)
    print("Example 6: Escalation Handling")
    print("=" * 80)

    project_id = "your-project-id"
    message_bus = VertexA2AMessageBus(project_id=project_id)

    # Simulate 3 validation failures
    print("\nSimulating validation loop with repeated failures...")

    orchestrator_id = f"projects/{project_id}/locations/us-central1/agents/orchestrator"
    escalation_id = f"projects/{project_id}/locations/us-central1/agents/escalation"

    # After 3 failures, send escalation request
    print("\n  Attempt 1: Failed - Missing error handling")
    print("  Attempt 2: Failed - Security vulnerability")
    print("  Attempt 3: Failed - Performance issue")
    print("\n✗ Maximum retries reached - escalating...")

    escalation_request = A2AProtocolHelper.create_escalation_request(
        sender_id=orchestrator_id,
        sender_name="orchestrator_agent",
        task_id="dev_failed_001",
        reason="validation_deadlock",
        rejection_count=3,
        context={
            "component_id": "payment_processor",
            "rejection_history": [
                {"attempt": 1, "issue": "Missing error handling"},
                {"attempt": 2, "issue": "Security vulnerability"},
                {"attempt": 3, "issue": "Performance issue"}
            ]
        }
    )

    message_bus.publish_message(escalation_request)

    print("\n✓ Escalation request sent to escalation agent")
    print("  Escalation agent will:")
    print("    - Analyze rejection pattern")
    print("    - Determine resolution strategy")
    print("    - Request human intervention if needed")


# ============================================================================
# Main
# ============================================================================

def main():
    """Run all examples."""
    print("\n")
    print("=" * 80)
    print("A2A COMMUNICATION EXAMPLES")
    print("=" * 80)
    print("\nThese examples demonstrate how to use A2A communication in agents.")
    print("Note: These are simulations - in production, agents would be deployed")
    print("      to Vertex AI and messages would be processed asynchronously.")
    print("\n")

    # Run examples
    example_basic_a2a_communication()
    example_validation_loop()
    example_task_tracking()
    example_error_reporting()
    example_multi_agent_workflow()
    example_escalation()

    print("\n" + "=" * 80)
    print("✓ All examples completed!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Deploy agents to Vertex AI using scripts/deploy_vertex_agents.py")
    print("2. Configure agent_registry.json with deployed agent IDs")
    print("3. Run the actual pipeline with scripts/run_vertex_pipeline.py")
    print("\n")


if __name__ == "__main__":
    main()
