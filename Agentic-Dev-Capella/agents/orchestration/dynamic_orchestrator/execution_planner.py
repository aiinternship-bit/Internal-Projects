"""
agents/orchestration/dynamic_orchestrator/execution_planner.py

Execution Planner - Creates optimized execution plans with DAG scheduling.

This planner:
- Builds dependency graphs from task requirements
- Identifies parallel execution opportunities
- Calculates critical paths
- Optimizes for throughput and latency
- Handles resource constraints (max parallel agents)
"""

from typing import Dict, List, Set, Optional, Any, Tuple
from datetime import datetime
import uuid

import networkx as nx

from shared.models.execution_plan import (
    ExecutionPlan,
    ExecutionPhase,
    AgentAssignment,
    CriticalPath,
    DependencyType
)
from shared.models.task_requirements import TaskRequirements
from shared.models.agent_capability import AgentCapability


class ExecutionPlanner:
    """
    Execution Planner for dynamic orchestration.

    Creates optimized execution plans with parallel scheduling,
    critical path analysis, and resource optimization.
    """

    def __init__(
        self,
        max_parallel_agents: int = 20,
        enable_critical_path_analysis: bool = True,
        enable_optimizations: bool = True
    ):
        """
        Initialize Execution Planner.

        Args:
            max_parallel_agents: Maximum agents to run in parallel
            enable_critical_path_analysis: Calculate critical paths
            enable_optimizations: Enable plan optimizations
        """
        self.max_parallel_agents = max_parallel_agents
        self.enable_critical_path_analysis = enable_critical_path_analysis
        self.enable_optimizations = enable_optimizations

        # Planning history
        self.planning_history: List[Dict[str, Any]] = []

    def create_execution_plan(
        self,
        tasks: List[TaskRequirements],
        agent_assignments: Dict[str, List[AgentCapability]],
        global_dependencies: Optional[Dict[str, List[str]]] = None
    ) -> ExecutionPlan:
        """
        Create an optimized execution plan for a set of tasks.

        Args:
            tasks: List of task requirements
            agent_assignments: {task_id: [assigned_agents]}
            global_dependencies: Optional explicit dependencies {task_id: [dep_task_ids]}

        Returns:
            ExecutionPlan with DAG, phases, and critical path
        """
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"

        # Step 1: Build dependency graph
        dependency_graph = self._build_dependency_graph(
            tasks=tasks,
            global_dependencies=global_dependencies
        )

        # Step 2: Validate DAG (no cycles)
        if not nx.is_directed_acyclic_graph(dependency_graph):
            raise ValueError("Dependency graph contains cycles - cannot schedule")

        # Step 3: Create agent assignments
        assignments = self._create_agent_assignments(
            tasks=tasks,
            agent_assignments=agent_assignments,
            dependency_graph=dependency_graph
        )

        # Step 4: Calculate phases (topological levels)
        phases = self._calculate_phases(
            assignments=assignments,
            dependency_graph=dependency_graph
        )

        # Step 5: Critical path analysis
        critical_path = None
        if self.enable_critical_path_analysis:
            critical_path = self._calculate_critical_path(
                dependency_graph=dependency_graph,
                assignments=assignments
            )

            # Mark critical path assignments
            if critical_path:
                for assignment in assignments:
                    if assignment.task_id in critical_path.task_ids:
                        assignment.is_critical_path = True

        # Step 6: Create execution plan
        execution_plan = ExecutionPlan(
            plan_id=plan_id,
            phases=phases,
            dependency_graph=dependency_graph,
            critical_path=critical_path,
            max_parallel_agents=self.max_parallel_agents
        )

        # Step 7: Optimize if enabled
        if self.enable_optimizations:
            execution_plan = self._optimize_plan(execution_plan)

        # Step 8: Record planning
        self._record_planning(execution_plan, tasks)

        return execution_plan

    def _build_dependency_graph(
        self,
        tasks: List[TaskRequirements],
        global_dependencies: Optional[Dict[str, List[str]]]
    ) -> nx.DiGraph:
        """
        Build dependency graph from task requirements and explicit dependencies.

        Returns:
            NetworkX directed graph with nodes=task_ids, edges=dependencies
        """
        graph = nx.DiGraph()

        # Add all tasks as nodes
        for task in tasks:
            graph.add_node(
                task.task_id,
                task=task,
                duration=task.estimated_duration_hours * 60,  # Convert to minutes
                complexity=task.estimated_complexity.value
            )

        # Add edges from task requirements (hard dependencies)
        for task in tasks:
            for dep_task_id in task.hard_dependencies:
                if dep_task_id in [t.task_id for t in tasks]:
                    graph.add_edge(
                        dep_task_id,  # From (must complete first)
                        task.task_id,  # To (depends on)
                        dependency_type=DependencyType.HARD
                    )

        # Add explicit global dependencies
        if global_dependencies:
            for task_id, dep_ids in global_dependencies.items():
                for dep_id in dep_ids:
                    if graph.has_node(task_id) and graph.has_node(dep_id):
                        graph.add_edge(dep_id, task_id, dependency_type=DependencyType.HARD)

        # Add soft dependencies (don't block, but hint at ordering)
        for task in tasks:
            for soft_dep_id in task.soft_dependencies:
                if soft_dep_id in [t.task_id for t in tasks]:
                    # Only add if doesn't create cycle
                    if not nx.has_path(graph, task.task_id, soft_dep_id):
                        graph.add_edge(
                            soft_dep_id,
                            task.task_id,
                            dependency_type=DependencyType.SOFT
                        )

        return graph

    def _create_agent_assignments(
        self,
        tasks: List[TaskRequirements],
        agent_assignments: Dict[str, List[AgentCapability]],
        dependency_graph: nx.DiGraph
    ) -> List[AgentAssignment]:
        """
        Create AgentAssignment objects from tasks and agent selections.
        """
        assignments = []

        for task in tasks:
            assigned_agents = agent_assignments.get(task.task_id, [])

            if not assigned_agents:
                print(f"Warning: No agents assigned to task {task.task_id}")
                continue

            # Get dependencies from graph
            predecessors = list(dependency_graph.predecessors(task.task_id))

            # Create assignment for each agent
            # (For now, assume one agent per task; multi-agent coordination is future work)
            for agent in assigned_agents[:1]:  # Take first agent
                assignment = AgentAssignment(
                    assignment_id=f"assign_{uuid.uuid4().hex[:8]}",
                    task_id=task.task_id,
                    agent_id=agent.agent_id,
                    estimated_duration_minutes=task.estimated_duration_hours * 60,
                    dependencies=predecessors,
                    is_critical_path=False  # Will be set later
                )

                assignments.append(assignment)

        return assignments

    def _calculate_phases(
        self,
        assignments: List[AgentAssignment],
        dependency_graph: nx.DiGraph
    ) -> List[ExecutionPhase]:
        """
        Calculate execution phases using topological sorting.

        Each phase contains tasks that can run in parallel.
        """
        # Topological generations (levels in DAG)
        try:
            generations = list(nx.topological_generations(dependency_graph))
        except nx.NetworkXError:
            # Fallback: treat as single phase
            generations = [[assignment.task_id for assignment in assignments]]

        phases = []

        for phase_num, task_ids in enumerate(generations):
            # Get assignments for this phase
            phase_assignments = [
                a for a in assignments if a.task_id in task_ids
            ]

            if not phase_assignments:
                continue

            # Calculate phase duration (max of all parallel tasks)
            max_duration = max(
                a.estimated_duration_minutes for a in phase_assignments
            )

            phase = ExecutionPhase(
                phase_number=phase_num,
                assignments=phase_assignments,
                max_parallelism=self.max_parallel_agents,
                estimated_duration_minutes=max_duration
            )

            phases.append(phase)

        return phases

    def _calculate_critical_path(
        self,
        dependency_graph: nx.DiGraph,
        assignments: List[AgentAssignment]
    ) -> Optional[CriticalPath]:
        """
        Calculate critical path (longest path through DAG).
        """
        if dependency_graph.number_of_nodes() == 0:
            return None

        try:
            # Find longest path using duration as weight
            longest_path = nx.dag_longest_path(
                dependency_graph,
                weight='duration'
            )

            # Calculate total duration
            total_duration = nx.dag_longest_path_length(
                dependency_graph,
                weight='duration'
            )

            # Find bottleneck (task with longest duration on critical path)
            bottleneck_task_id = longest_path[0]
            max_duration = 0.0

            for task_id in longest_path:
                task_duration = dependency_graph.nodes[task_id]['duration']
                if task_duration > max_duration:
                    max_duration = task_duration
                    bottleneck_task_id = task_id

            return CriticalPath(
                task_ids=longest_path,
                total_duration_minutes=total_duration,
                bottleneck_task_id=bottleneck_task_id
            )

        except Exception as e:
            print(f"Error calculating critical path: {str(e)}")
            return None

    def _optimize_plan(self, plan: ExecutionPlan) -> ExecutionPlan:
        """
        Optimize execution plan for better performance.

        Optimizations:
        - Load balancing across phases
        - Reordering tasks within phases for better parallelism
        - Splitting large phases
        """
        # Get optimization suggestions
        suggestions = plan.suggest_optimizations()

        # Apply optimizations
        for suggestion in suggestions:
            if "Split phase" in suggestion:
                # TODO: Implement phase splitting
                pass
            elif "Reorder" in suggestion:
                # TODO: Implement task reordering
                pass

        # For now, just return original plan
        return plan

    def _record_planning(self, plan: ExecutionPlan, tasks: List[TaskRequirements]) -> None:
        """
        Record planning for analytics.
        """
        self.planning_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "plan_id": plan.plan_id,
            "num_tasks": len(tasks),
            "num_phases": len(plan.phases),
            "total_duration_minutes": plan.get_total_duration(),
            "critical_path_duration": plan.critical_path.total_duration_minutes if plan.critical_path else None,
            "parallelism_efficiency": plan.calculate_parallelism_efficiency()
        })

    def visualize_plan(self, plan: ExecutionPlan) -> str:
        """
        Generate text-based visualization of execution plan.

        Returns:
            Multi-line string showing plan structure
        """
        lines = []

        lines.append(f"Execution Plan: {plan.plan_id}")
        lines.append("=" * 60)
        lines.append(f"Total Phases: {len(plan.phases)}")
        lines.append(f"Total Duration: {plan.get_total_duration():.1f} minutes")

        if plan.critical_path:
            lines.append(f"Critical Path: {plan.critical_path.total_duration_minutes:.1f} minutes")
            lines.append(f"Bottleneck: {plan.critical_path.bottleneck_task_id}")

        lines.append(f"Parallelism Efficiency: {plan.calculate_parallelism_efficiency():.1%}")
        lines.append("")

        # Show each phase
        for phase in plan.phases:
            lines.append(f"Phase {phase.phase_number}: {len(phase.assignments)} tasks (parallel)")
            lines.append(f"  Duration: {phase.estimated_duration_minutes:.1f} minutes")

            for assignment in phase.assignments:
                marker = " [CRITICAL]" if assignment.is_critical_path else ""
                lines.append(f"  - {assignment.task_id} → {assignment.agent_id}{marker}")

            lines.append("")

        return "\n".join(lines)

    def get_planning_stats(self) -> Dict[str, Any]:
        """
        Get planning statistics.
        """
        if not self.planning_history:
            return {"total_plans": 0}

        avg_parallelism = sum(
            p["parallelism_efficiency"] for p in self.planning_history
        ) / len(self.planning_history)

        avg_phases = sum(
            p["num_phases"] for p in self.planning_history
        ) / len(self.planning_history)

        return {
            "total_plans": len(self.planning_history),
            "avg_parallelism_efficiency": avg_parallelism,
            "avg_phases_per_plan": avg_phases,
            "recent_plans": self.planning_history[-5:]
        }

    def simulate_execution(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """
        Simulate plan execution to estimate actual timing.

        Returns:
            {
                "total_time_minutes": float,
                "phase_timings": List[float],
                "agent_utilization": Dict[str, float]
            }
        """
        phase_timings = []
        agent_utilization = {}

        for phase in plan.phases:
            # Phase duration is max of parallel tasks
            phase_timings.append(phase.estimated_duration_minutes)

            # Track agent usage
            for assignment in phase.assignments:
                if assignment.agent_id not in agent_utilization:
                    agent_utilization[assignment.agent_id] = 0.0
                agent_utilization[assignment.agent_id] += assignment.estimated_duration_minutes

        total_time = sum(phase_timings)

        # Calculate utilization as % of total plan time
        for agent_id in agent_utilization:
            agent_utilization[agent_id] = agent_utilization[agent_id] / total_time if total_time > 0 else 0.0

        return {
            "total_time_minutes": total_time,
            "phase_timings": phase_timings,
            "agent_utilization": agent_utilization
        }


# Tool functions for standalone usage
def create_execution_plan_tool(
    tasks_dict: List[Dict[str, Any]],
    agent_assignments_dict: Dict[str, List[Dict[str, Any]]],
    global_dependencies: Optional[Dict[str, List[str]]] = None,
    max_parallel_agents: int = 20
) -> Dict[str, Any]:
    """
    Tool function: Create execution plan from task and assignment dictionaries.

    Args:
        tasks_dict: List of task requirement dictionaries
        agent_assignments_dict: {task_id: [agent_capability_dicts]}
        global_dependencies: Optional dependencies
        max_parallel_agents: Max parallel execution

    Returns:
        Execution plan as dictionary
    """
    # Reconstruct objects from dicts
    tasks = [TaskRequirements.from_dict(t) for t in tasks_dict]

    agent_assignments = {}
    for task_id, agents_list in agent_assignments_dict.items():
        agent_assignments[task_id] = [
            AgentCapability.from_dict(a) for a in agents_list
        ]

    # Create planner
    planner = ExecutionPlanner(max_parallel_agents=max_parallel_agents)

    # Create plan
    plan = planner.create_execution_plan(
        tasks=tasks,
        agent_assignments=agent_assignments,
        global_dependencies=global_dependencies
    )

    return plan.to_dict()


def visualize_execution_plan(plan_dict: Dict[str, Any]) -> str:
    """
    Tool function: Visualize execution plan.
    """
    plan = ExecutionPlan.from_dict(plan_dict)

    planner = ExecutionPlanner()
    return planner.visualize_plan(plan)
