"""
agents/orchestration/dynamic_orchestrator/agent.py

Dynamic Orchestrator Agent - Main coordinator for dynamic multi-agent orchestration.

This orchestrator:
- Receives tasks with multimodal inputs
- Analyzes requirements using TaskAnalyzer
- Selects optimal agents using AgentSelector
- Creates execution plans using ExecutionPlanner
- Coordinates execution via A2A messaging
- Tracks progress and handles failures
"""

from typing import Dict, List, Set, Optional, Any
from datetime import datetime
import uuid

from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration
from shared.services.agent_registry import AgentRegistryService
from shared.models.execution_plan import ExecutionPlan, ExecutionPhase, AgentAssignment
from shared.models.task_requirements import TaskRequirements
from shared.models.agent_capability import AgentCapability

from .task_analyzer import TaskAnalyzer
from .agent_selector import AgentSelector
from .execution_planner import ExecutionPlanner


class DynamicOrchestrator(A2AEnabledAgent):
    """
    Dynamic Orchestrator Agent for intelligent multi-agent coordination.

    Uses AI-powered analysis to dynamically select and coordinate agents
    based on task requirements and agent capabilities.
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        agent_registry_path: str = "./config/agent_registry.json",
        max_parallel_agents: int = 20,
        enable_critical_path_tracking: bool = True
    ):
        """
        Initialize Dynamic Orchestrator.

        Args:
            context: Agent context (project_id, location, etc.)
            message_bus: A2A message bus
            agent_registry_path: Path to agent registry JSON
            max_parallel_agents: Max concurrent agents
            enable_critical_path_tracking: Track critical paths
        """
        super().__init__(context, message_bus)

        self.context = context
        self.agent_registry_path = agent_registry_path
        self.max_parallel_agents = max_parallel_agents
        self.enable_critical_path_tracking = enable_critical_path_tracking

        # Initialize A2A integration
        self.a2a = A2AIntegration(
            context=context,
            message_bus=message_bus,
            orchestrator_id=context.get("agent_id", "dynamic_orchestrator")
        )

        # Initialize Vertex AI
        aiplatform.init(
            project=context.get("project_id"),
            location=context.get("location", "us-central1")
        )

        # Initialize agent registry
        self.agent_registry = AgentRegistryService(
            persistence_path=agent_registry_path,
            enable_persistence=True
        )

        # Initialize components
        self.task_analyzer = TaskAnalyzer(
            context=context,
            message_bus=message_bus,
            orchestrator_id=context.get("agent_id", "dynamic_orchestrator")
        )

        self.agent_selector = AgentSelector(
            agent_registry=self.agent_registry,
            max_agents_per_task=5
        )

        self.execution_planner = ExecutionPlanner(
            max_parallel_agents=max_parallel_agents,
            enable_critical_path_analysis=enable_critical_path_tracking
        )

        # Orchestration state
        self.active_plans: Dict[str, ExecutionPlan] = {}
        self.plan_states: Dict[str, Dict[str, Any]] = {}
        self.completed_tasks: Dict[str, Set[str]] = {}  # plan_id -> completed task_ids
        self.failed_tasks: Dict[str, Set[str]] = {}  # plan_id -> failed task_ids

        # Orchestration history
        self.orchestration_history: List[Dict[str, Any]] = []

    def handle_task_assignment(self, message: Dict[str, Any]) -> None:
        """
        Handle incoming task from external source (e.g., user request).

        Expected payload:
        {
            "task_description": str,
            "input_files": List[Dict],  # Multimodal inputs
            "context": Dict,
            "constraints": Dict
        }
        """
        payload = message.get("payload", {})
        task_id = payload.get("task_id", f"task_{uuid.uuid4().hex[:8]}")

        try:
            # Orchestrate the task
            result = self.orchestrate_task(
                task_description=payload.get("task_description"),
                input_files=payload.get("input_files", []),
                context=payload.get("context", {}),
                constraints=payload.get("constraints", {}),
                task_id=task_id
            )

            # Send completion
            self.a2a.send_completion(
                task_id=task_id,
                artifacts=result,
                metrics={
                    "total_duration_minutes": result.get("total_duration_minutes", 0),
                    "agents_used": len(result.get("agent_assignments", {}))
                }
            )

        except Exception as e:
            self.a2a.send_error_report(
                task_id=task_id,
                error_type="ORCHESTRATION_FAILED",
                error_message=str(e),
                stack_trace=""
            )

    @A2AIntegration.with_task_tracking
    def orchestrate_task(
        self,
        task_description: str,
        input_files: List[Dict[str, Any]] = None,
        context: Dict[str, Any] = None,
        constraints: Dict[str, Any] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate a task from requirements to execution.

        This is the main entry point for dynamic orchestration.

        Args:
            task_description: Natural language task description
            input_files: Multimodal input files
            context: Additional context
            constraints: Constraints (budget, timeline, etc.)
            task_id: Optional task ID

        Returns:
            {
                "plan_id": str,
                "execution_plan": Dict,
                "agent_assignments": Dict,
                "status": str,
                "timeline": Dict
            }
        """
        task_id = task_id or f"task_{uuid.uuid4().hex[:8]}"
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"

        print(f"[Dynamic Orchestrator] Starting orchestration for task: {task_id}")

        # Step 1: Analyze task requirements
        print("[1/5] Analyzing task requirements...")
        task_requirements = self.task_analyzer.analyze_task(
            task_description=task_description,
            input_files=input_files,
            context=context,
            constraints=constraints,
            task_id=task_id
        )

        print(f"  Required capabilities: {task_requirements.required_capabilities}")
        print(f"  Complexity: {task_requirements.estimated_complexity.name}")
        print(f"  Estimated duration: {task_requirements.estimated_duration_hours:.1f} hours")

        # Step 2: Select agents
        print("[2/5] Selecting agents...")
        selected_agents = self.agent_selector.select_agents(
            task_requirements=task_requirements,
            allow_multiple=True,
            prefer_specialists=True
        )

        if not selected_agents:
            raise ValueError(f"No agents available for capabilities: {task_requirements.required_capabilities}")

        print(f"  Selected {len(selected_agents)} agents:")
        for agent in selected_agents:
            print(f"    - {agent.agent_name} ({agent.agent_id})")

        # Step 3: Create execution plan
        print("[3/5] Creating execution plan...")

        # For single task, wrap in list
        tasks = [task_requirements]
        agent_assignments = {task_id: selected_agents}

        execution_plan = self.execution_planner.create_execution_plan(
            tasks=tasks,
            agent_assignments=agent_assignments
        )

        print(f"  Plan phases: {len(execution_plan.phases)}")
        print(f"  Total duration: {execution_plan.get_total_duration():.1f} minutes")

        if execution_plan.critical_path:
            print(f"  Critical path: {execution_plan.critical_path.total_duration_minutes:.1f} minutes")

        # Step 4: Store plan state
        self.active_plans[plan_id] = execution_plan
        self.plan_states[plan_id] = {
            "status": "ready",
            "created_at": datetime.utcnow().isoformat(),
            "current_phase": 0,
            "tasks": {task_id: task_requirements}
        }
        self.completed_tasks[plan_id] = set()
        self.failed_tasks[plan_id] = set()

        # Step 5: Start execution (async via A2A)
        print("[4/5] Starting execution...")
        self._execute_plan(plan_id, execution_plan)

        # Step 6: Record orchestration
        print("[5/5] Orchestration complete. Monitoring execution...")
        self._record_orchestration(
            plan_id=plan_id,
            task_id=task_id,
            requirements=task_requirements,
            selected_agents=selected_agents,
            execution_plan=execution_plan
        )

        return {
            "plan_id": plan_id,
            "task_id": task_id,
            "execution_plan": execution_plan.to_dict(),
            "agent_assignments": {
                agent.agent_id: agent.to_dict() for agent in selected_agents
            },
            "status": "executing",
            "estimated_completion_minutes": execution_plan.get_total_duration(),
            "timeline": {
                "phases": len(execution_plan.phases),
                "total_duration_minutes": execution_plan.get_total_duration()
            }
        }

    def _execute_plan(self, plan_id: str, plan: ExecutionPlan) -> None:
        """
        Execute a plan by sending task assignments to agents.

        Execution is asynchronous via A2A messaging.
        """
        self.plan_states[plan_id]["status"] = "executing"

        # Start with phase 0
        self._execute_phase(plan_id, plan, phase_number=0)

    def _execute_phase(self, plan_id: str, plan: ExecutionPlan, phase_number: int) -> None:
        """
        Execute a single phase (all tasks in parallel).
        """
        if phase_number >= len(plan.phases):
            # All phases complete
            self._complete_plan(plan_id)
            return

        phase = plan.phases[phase_number]
        self.plan_states[plan_id]["current_phase"] = phase_number

        print(f"[Execution] Starting phase {phase_number} with {len(phase.assignments)} tasks")

        # Send task assignments to all agents in this phase
        for assignment in phase.assignments:
            self._assign_task_to_agent(plan_id, assignment)

    def _assign_task_to_agent(self, plan_id: str, assignment: AgentAssignment) -> None:
        """
        Send TASK_ASSIGNMENT message to agent via A2A.
        """
        # Get task details from plan state
        task = self.plan_states[plan_id]["tasks"].get(assignment.task_id)

        # Build task assignment message
        self.a2a.send_task_assignment(
            task_id=assignment.task_id,
            agent_id=assignment.agent_id,
            task_type=task.description if task else "development",
            payload={
                "task_requirements": task.to_dict() if task else {},
                "assignment_id": assignment.assignment_id,
                "plan_id": plan_id
            }
        )

        print(f"  Assigned {assignment.task_id} to {assignment.agent_id}")

    def handle_task_completion(self, message: Dict[str, Any]) -> None:
        """
        Handle TASK_COMPLETION message from agents.
        """
        payload = message.get("payload", {})
        task_id = payload.get("task_id")
        plan_id = payload.get("plan_id")
        artifacts = payload.get("artifacts", {})

        print(f"[Completion] Task {task_id} completed in plan {plan_id}")

        if plan_id not in self.completed_tasks:
            print(f"  Warning: Unknown plan {plan_id}")
            return

        # Mark task as completed
        self.completed_tasks[plan_id].add(task_id)

        # Update agent performance metrics
        sender_agent_id = message.get("sender_agent_id")
        if sender_agent_id:
            self.agent_registry.update_performance(
                agent_id=sender_agent_id,
                success=True,
                duration_minutes=payload.get("duration_minutes", 10.0),
                cost_usd=payload.get("cost_usd", 0.0)
            )

        # Check if phase is complete
        self._check_phase_completion(plan_id)

    def handle_error_report(self, message: Dict[str, Any]) -> None:
        """
        Handle ERROR_REPORT message from agents.
        """
        payload = message.get("payload", {})
        task_id = payload.get("task_id")
        plan_id = payload.get("plan_id")
        error_message = payload.get("error_message", "Unknown error")

        print(f"[Error] Task {task_id} failed in plan {plan_id}: {error_message}")

        if plan_id not in self.failed_tasks:
            print(f"  Warning: Unknown plan {plan_id}")
            return

        # Mark task as failed
        self.failed_tasks[plan_id].add(task_id)

        # Update agent performance
        sender_agent_id = message.get("sender_agent_id")
        if sender_agent_id:
            self.agent_registry.update_performance(
                agent_id=sender_agent_id,
                success=False,
                duration_minutes=0.0,
                cost_usd=0.0
            )

        # Handle failure (retry, escalate, or fail plan)
        self._handle_task_failure(plan_id, task_id, error_message)

    def _check_phase_completion(self, plan_id: str) -> None:
        """
        Check if current phase is complete and advance to next.
        """
        plan = self.active_plans.get(plan_id)
        if not plan:
            return

        current_phase_num = self.plan_states[plan_id]["current_phase"]
        current_phase = plan.phases[current_phase_num]

        # Check if all tasks in phase are complete
        phase_task_ids = {a.task_id for a in current_phase.assignments}
        completed = self.completed_tasks[plan_id]
        failed = self.failed_tasks[plan_id]

        if phase_task_ids.issubset(completed | failed):
            print(f"[Execution] Phase {current_phase_num} complete")

            # Check for failures
            if phase_task_ids & failed:
                print(f"  Warning: {len(phase_task_ids & failed)} tasks failed")

            # Advance to next phase
            next_phase = current_phase_num + 1
            self._execute_phase(plan_id, plan, next_phase)

    def _complete_plan(self, plan_id: str) -> None:
        """
        Mark plan as complete.
        """
        self.plan_states[plan_id]["status"] = "completed"
        self.plan_states[plan_id]["completed_at"] = datetime.utcnow().isoformat()

        print(f"[Execution] Plan {plan_id} completed!")
        print(f"  Tasks completed: {len(self.completed_tasks[plan_id])}")
        print(f"  Tasks failed: {len(self.failed_tasks[plan_id])}")

    def _handle_task_failure(self, plan_id: str, task_id: str, error_message: str) -> None:
        """
        Handle task failure (retry, escalate, or fail plan).
        """
        # TODO: Implement retry logic
        # For now, just log the failure
        print(f"[Failure] Task {task_id} in plan {plan_id} failed: {error_message}")
        print("  (Retry logic not yet implemented)")

    def _record_orchestration(
        self,
        plan_id: str,
        task_id: str,
        requirements: TaskRequirements,
        selected_agents: List[AgentCapability],
        execution_plan: ExecutionPlan
    ) -> None:
        """
        Record orchestration for analytics.
        """
        self.orchestration_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "plan_id": plan_id,
            "task_id": task_id,
            "requirements": requirements.to_dict(),
            "selected_agents": [a.agent_id for a in selected_agents],
            "execution_plan": execution_plan.to_dict()
        })

    def get_plan_status(self, plan_id: str) -> Dict[str, Any]:
        """
        Get current status of a plan.
        """
        if plan_id not in self.plan_states:
            return {"error": "Plan not found"}

        state = self.plan_states[plan_id]
        plan = self.active_plans.get(plan_id)

        return {
            "plan_id": plan_id,
            "status": state["status"],
            "current_phase": state["current_phase"],
            "total_phases": len(plan.phases) if plan else 0,
            "completed_tasks": len(self.completed_tasks.get(plan_id, set())),
            "failed_tasks": len(self.failed_tasks.get(plan_id, set())),
            "created_at": state["created_at"],
            "completed_at": state.get("completed_at")
        }

    def get_orchestration_stats(self) -> Dict[str, Any]:
        """
        Get orchestration statistics.
        """
        return {
            "total_orchestrations": len(self.orchestration_history),
            "active_plans": len([p for p in self.plan_states.values() if p["status"] == "executing"]),
            "completed_plans": len([p for p in self.plan_states.values() if p["status"] == "completed"]),
            "agent_registry_stats": self.agent_registry.get_registry_stats(),
            "recent_orchestrations": self.orchestration_history[-5:]
        }


# Tool functions for Vertex AI Reasoning Engine deployment
def orchestrate_task_tool(
    task_description: str,
    input_files: List[Dict[str, Any]] = None,
    context: Dict[str, Any] = None,
    constraints: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Tool function: Orchestrate a task using dynamic orchestration.

    This is the main entry point when deployed as Vertex AI Reasoning Engine.
    """
    # This will be injected with actual context during deployment
    orchestrator = DynamicOrchestrator(
        context={},  # Filled by deployment script
        message_bus=None  # Filled by deployment script
    )

    result = orchestrator.orchestrate_task(
        task_description=task_description,
        input_files=input_files,
        context=context,
        constraints=constraints
    )

    return result


def get_plan_status_tool(plan_id: str) -> Dict[str, Any]:
    """
    Tool function: Get status of an execution plan.
    """
    orchestrator = DynamicOrchestrator(
        context={},
        message_bus=None
    )

    return orchestrator.get_plan_status(plan_id)
