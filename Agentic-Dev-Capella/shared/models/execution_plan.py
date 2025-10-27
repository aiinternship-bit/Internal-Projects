"""
shared/models/execution_plan.py

Execution plan model with DAG-based parallel scheduling.
Supports intelligent task decomposition and parallel execution up to 20 concurrent agents.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json

try:
    import networkx as nx
except ImportError:
    # networkx will be added to requirements.txt
    nx = None


class ExecutionStatus(Enum):
    """Status of execution plan or phase."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class DependencyType(Enum):
    """Type of dependency between tasks."""
    HARD = "hard"  # Must complete before dependent can start
    SOFT = "soft"  # Preferred to complete first, but not required
    DATA = "data"  # Output of one task is input to another
    RESOURCE = "resource"  # Share same resource (can't run in parallel)


@dataclass
class AgentAssignment:
    """
    Represents assignment of a task to a specific agent.
    """
    assignment_id: str
    task_id: str
    agent_id: str
    agent_name: str
    agent_type: str

    # Estimates
    estimated_duration_minutes: float
    estimated_cost_usd: float = 0.0
    estimated_kb_queries: int = 0

    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    """List of task_ids that must complete before this can start."""

    dependency_types: Dict[str, DependencyType] = field(default_factory=dict)
    """Map of task_id -> dependency type."""

    blocks: List[str] = field(default_factory=list)
    """List of task_ids that this assignment blocks."""

    # Resource requirements
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    """Resource requirements (CPU, memory, etc.)."""

    # Execution tracking
    status: ExecutionStatus = ExecutionStatus.PENDING
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    actual_duration_minutes: Optional[float] = None
    actual_cost_usd: Optional[float] = None
    retry_count: int = 0
    error_message: Optional[str] = None

    # Metadata
    priority: int = 0  # Higher = more important
    is_critical_path: bool = False
    parallelizable: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def can_start(self, completed_tasks: Set[str]) -> bool:
        """
        Check if this assignment can start given completed tasks.

        Args:
            completed_tasks: Set of task_ids that have completed

        Returns:
            True if all hard dependencies are satisfied
        """
        if self.status != ExecutionStatus.PENDING:
            return False

        # Check hard dependencies
        for dep_task_id in self.dependencies:
            dep_type = self.dependency_types.get(dep_task_id, DependencyType.HARD)

            if dep_type == DependencyType.HARD and dep_task_id not in completed_tasks:
                return False

        return True

    def mark_started(self):
        """Mark assignment as started."""
        self.status = ExecutionStatus.IN_PROGRESS
        self.started_at = datetime.utcnow().isoformat()

    def mark_completed(self, actual_duration: float, actual_cost: float = 0.0):
        """Mark assignment as completed."""
        self.status = ExecutionStatus.COMPLETED
        self.completed_at = datetime.utcnow().isoformat()
        self.actual_duration_minutes = actual_duration
        self.actual_cost_usd = actual_cost

    def mark_failed(self, error: str):
        """Mark assignment as failed."""
        self.status = ExecutionStatus.FAILED
        self.error_message = error
        self.completed_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "assignment_id": self.assignment_id,
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "estimated_duration_minutes": self.estimated_duration_minutes,
            "estimated_cost_usd": self.estimated_cost_usd,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "is_critical_path": self.is_critical_path,
            "priority": self.priority
        }


@dataclass
class ExecutionPhase:
    """
    Group of tasks that can execute in parallel.
    Represents one level in the dependency DAG.
    """
    phase_number: int
    phase_name: str
    assignments: List[AgentAssignment] = field(default_factory=list)

    # Phase characteristics
    max_parallelism: int = 20
    estimated_duration_minutes: float = 0.0
    """Duration is max of all assignments in phase (parallel execution)."""

    estimated_cost_usd: float = 0.0
    """Cost is sum of all assignments in phase."""

    # Execution tracking
    status: ExecutionStatus = ExecutionStatus.PENDING
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    actual_duration_minutes: Optional[float] = None

    # Dependencies
    depends_on_phases: List[int] = field(default_factory=list)
    """Phase numbers that must complete before this phase."""

    def add_assignment(self, assignment: AgentAssignment):
        """Add an assignment to this phase."""
        self.assignments.append(assignment)

        # Update phase duration (max of all assignments)
        self.estimated_duration_minutes = max(
            self.estimated_duration_minutes,
            assignment.estimated_duration_minutes
        )

        # Update phase cost (sum of all assignments)
        self.estimated_cost_usd += assignment.estimated_cost_usd

    def get_parallelism(self) -> int:
        """Get actual parallelism (number of assignments)."""
        return len(self.assignments)

    def is_within_parallelism_limit(self) -> bool:
        """Check if phase exceeds parallelism limit."""
        return len(self.assignments) <= self.max_parallelism

    def can_start(self, completed_phases: Set[int]) -> bool:
        """Check if this phase can start."""
        if self.status != ExecutionStatus.PENDING:
            return False

        return all(dep in completed_phases for dep in self.depends_on_phases)

    def mark_started(self):
        """Mark phase as started."""
        self.status = ExecutionStatus.IN_PROGRESS
        self.started_at = datetime.utcnow().isoformat()

    def mark_completed(self):
        """Mark phase as completed."""
        self.status = ExecutionStatus.COMPLETED
        self.completed_at = datetime.utcnow().isoformat()

        if self.started_at:
            start = datetime.fromisoformat(self.started_at)
            end = datetime.utcnow()
            self.actual_duration_minutes = (end - start).total_seconds() / 60.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "phase_number": self.phase_number,
            "phase_name": self.phase_name,
            "assignments": [a.to_dict() for a in self.assignments],
            "parallelism": self.get_parallelism(),
            "estimated_duration_minutes": self.estimated_duration_minutes,
            "estimated_cost_usd": self.estimated_cost_usd,
            "status": self.status.value
        }


@dataclass
class CriticalPath:
    """Represents the critical path through the execution plan."""
    task_ids: List[str]
    agent_names: List[str]
    total_duration_minutes: float
    total_cost_usd: float
    bottleneck_task_id: Optional[str] = None
    """Task with longest duration on critical path."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_ids": self.task_ids,
            "agent_names": self.agent_names,
            "total_duration_minutes": self.total_duration_minutes,
            "total_cost_usd": self.total_cost_usd,
            "bottleneck_task_id": self.bottleneck_task_id
        }


@dataclass
class ExecutionMetrics:
    """Metrics for execution plan performance."""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    tasks_in_progress: int = 0

    total_estimated_duration_minutes: float = 0.0
    actual_duration_minutes: float = 0.0
    speedup_factor: float = 1.0
    """Speedup from parallelization (sequential_time / parallel_time)."""

    total_estimated_cost_usd: float = 0.0
    actual_cost_usd: float = 0.0

    parallelism_achieved: float = 1.0
    """Average number of concurrent tasks."""

    efficiency: float = 1.0
    """Ratio of useful work to total time (0.0 to 1.0)."""

    def calculate_completion_rate(self) -> float:
        """Calculate completion rate."""
        if self.total_tasks == 0:
            return 0.0
        return self.completed_tasks / self.total_tasks

    def calculate_speedup(self) -> float:
        """Calculate speedup from parallelization."""
        if self.actual_duration_minutes == 0:
            return 1.0
        return self.total_estimated_duration_minutes / self.actual_duration_minutes

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "completion_rate": self.calculate_completion_rate(),
            "actual_duration_minutes": self.actual_duration_minutes,
            "speedup_factor": self.speedup_factor,
            "actual_cost_usd": self.actual_cost_usd,
            "parallelism_achieved": self.parallelism_achieved,
            "efficiency": self.efficiency
        }


@dataclass
class ExecutionPlan:
    """
    Complete execution plan with parallel phases and DAG scheduling.

    Represents a fully planned execution strategy with task assignments,
    dependencies, parallel phases, and critical path analysis.
    """

    # ============================================================================
    # Core Identification
    # ============================================================================
    plan_id: str
    task_id: str
    """Original task ID this plan was created for."""

    plan_name: Optional[str] = None
    description: Optional[str] = None

    # ============================================================================
    # Execution Phases
    # ============================================================================
    phases: List[ExecutionPhase] = field(default_factory=list)
    """Ordered list of execution phases."""

    assignments: List[AgentAssignment] = field(default_factory=list)
    """All agent assignments across all phases."""

    # ============================================================================
    # Dependency Graph
    # ============================================================================
    dependency_graph: Optional[Any] = None  # nx.DiGraph in production
    """NetworkX directed graph of task dependencies."""

    # ============================================================================
    # Critical Path Analysis
    # ============================================================================
    critical_path: Optional[CriticalPath] = None
    """Critical path through the execution plan."""

    # ============================================================================
    # Estimates and Limits
    # ============================================================================
    total_estimated_duration_minutes: float = 0.0
    """Total wall-clock time for entire plan (accounting for parallelism)."""

    sequential_duration_minutes: float = 0.0
    """Total time if all tasks ran sequentially."""

    total_estimated_cost_usd: float = 0.0

    max_parallel_agents: int = 20
    """Maximum number of agents that can run concurrently."""

    estimated_kb_queries: int = 0
    """Total estimated KB queries across all agents."""

    # ============================================================================
    # Execution Tracking
    # ============================================================================
    status: ExecutionStatus = ExecutionStatus.PENDING

    metrics: ExecutionMetrics = field(default_factory=ExecutionMetrics)

    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    # ============================================================================
    # Metadata
    # ============================================================================
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    created_by: str = "dynamic_orchestrator"

    optimization_strategy: str = "minimize_time"
    """Strategy used for planning: minimize_time, minimize_cost, balanced."""

    metadata: Dict[str, Any] = field(default_factory=dict)

    # ============================================================================
    # Methods: Critical Path Analysis
    # ============================================================================

    def get_critical_path(self) -> Optional[CriticalPath]:
        """
        Calculate and return critical path through execution plan.

        Returns:
            CriticalPath object with longest path through DAG
        """
        if self.critical_path:
            return self.critical_path

        if not self.dependency_graph or nx is None:
            return None

        try:
            # Get longest path using networkx
            longest_path = nx.dag_longest_path(
                self.dependency_graph,
                weight='duration'
            )

            # Calculate total duration and cost
            total_duration = 0.0
            total_cost = 0.0
            agent_names = []
            max_duration = 0.0
            bottleneck_task = None

            for task_id in longest_path:
                assignment = self._get_assignment_by_task_id(task_id)
                if assignment:
                    total_duration += assignment.estimated_duration_minutes
                    total_cost += assignment.estimated_cost_usd
                    agent_names.append(assignment.agent_name)

                    # Track bottleneck
                    if assignment.estimated_duration_minutes > max_duration:
                        max_duration = assignment.estimated_duration_minutes
                        bottleneck_task = task_id

                    # Mark as critical path
                    assignment.is_critical_path = True

            self.critical_path = CriticalPath(
                task_ids=longest_path,
                agent_names=agent_names,
                total_duration_minutes=total_duration,
                total_cost_usd=total_cost,
                bottleneck_task_id=bottleneck_task
            )

            return self.critical_path

        except Exception as e:
            print(f"Error calculating critical path: {str(e)}")
            return None

    def get_bottlenecks(self, threshold_minutes: float = 30.0) -> List[AgentAssignment]:
        """
        Identify bottleneck tasks (long-duration tasks on critical path).

        Args:
            threshold_minutes: Minimum duration to be considered a bottleneck

        Returns:
            List of bottleneck assignments
        """
        critical_path = self.get_critical_path()
        if not critical_path:
            return []

        bottlenecks = []
        for task_id in critical_path.task_ids:
            assignment = self._get_assignment_by_task_id(task_id)
            if assignment and assignment.estimated_duration_minutes >= threshold_minutes:
                bottlenecks.append(assignment)

        return bottlenecks

    # ============================================================================
    # Methods: Phase Management
    # ============================================================================

    def add_phase(self, phase: ExecutionPhase):
        """Add an execution phase to the plan."""
        self.phases.append(phase)

        # Update assignments list
        self.assignments.extend(phase.assignments)

        # Update estimates
        self.total_estimated_duration_minutes += phase.estimated_duration_minutes
        self.total_estimated_cost_usd += phase.estimated_cost_usd

    def get_phase(self, phase_number: int) -> Optional[ExecutionPhase]:
        """Get phase by number."""
        for phase in self.phases:
            if phase.phase_number == phase_number:
                return phase
        return None

    def get_current_phase(self) -> Optional[ExecutionPhase]:
        """Get currently executing phase."""
        for phase in self.phases:
            if phase.status == ExecutionStatus.IN_PROGRESS:
                return phase
        return None

    def get_next_phase(self) -> Optional[ExecutionPhase]:
        """Get next phase to execute."""
        completed_phases = {
            p.phase_number for p in self.phases
            if p.status == ExecutionStatus.COMPLETED
        }

        for phase in self.phases:
            if phase.can_start(completed_phases):
                return phase

        return None

    # ============================================================================
    # Methods: Assignment Management
    # ============================================================================

    def get_assignment(self, assignment_id: str) -> Optional[AgentAssignment]:
        """Get assignment by ID."""
        for assignment in self.assignments:
            if assignment.assignment_id == assignment_id:
                return assignment
        return None

    def _get_assignment_by_task_id(self, task_id: str) -> Optional[AgentAssignment]:
        """Get assignment by task ID."""
        for assignment in self.assignments:
            if assignment.task_id == task_id:
                return assignment
        return None

    def get_ready_assignments(self, completed_tasks: Set[str]) -> List[AgentAssignment]:
        """
        Get assignments that are ready to start.

        Args:
            completed_tasks: Set of completed task IDs

        Returns:
            List of assignments ready to start
        """
        ready = []
        for assignment in self.assignments:
            if assignment.can_start(completed_tasks):
                ready.append(assignment)

        # Sort by priority
        ready.sort(key=lambda a: a.priority, reverse=True)

        return ready

    def get_assignments_by_agent(self, agent_id: str) -> List[AgentAssignment]:
        """Get all assignments for a specific agent."""
        return [a for a in self.assignments if a.agent_id == agent_id]

    # ============================================================================
    # Methods: Execution Control
    # ============================================================================

    def start_execution(self):
        """Mark plan execution as started."""
        self.status = ExecutionStatus.IN_PROGRESS
        self.started_at = datetime.utcnow().isoformat()

        self.metrics.total_tasks = len(self.assignments)
        self.metrics.total_estimated_duration_minutes = self.total_estimated_duration_minutes
        self.metrics.total_estimated_cost_usd = self.total_estimated_cost_usd

    def complete_execution(self):
        """Mark plan execution as completed."""
        self.status = ExecutionStatus.COMPLETED
        self.completed_at = datetime.utcnow().isoformat()

        # Calculate actual duration
        if self.started_at:
            start = datetime.fromisoformat(self.started_at)
            end = datetime.utcnow()
            self.metrics.actual_duration_minutes = (end - start).total_seconds() / 60.0

        # Calculate speedup
        self.metrics.speedup_factor = self.metrics.calculate_speedup()

        # Update completion metrics
        self.metrics.completed_tasks = sum(
            1 for a in self.assignments
            if a.status == ExecutionStatus.COMPLETED
        )
        self.metrics.failed_tasks = sum(
            1 for a in self.assignments
            if a.status == ExecutionStatus.FAILED
        )

    def cancel_execution(self):
        """Cancel plan execution."""
        self.status = ExecutionStatus.CANCELLED
        self.completed_at = datetime.utcnow().isoformat()

    # ============================================================================
    # Methods: Optimization Analysis
    # ============================================================================

    def calculate_parallelism_efficiency(self) -> float:
        """
        Calculate efficiency of parallelization.

        Returns:
            Efficiency ratio (0.0 to 1.0)
        """
        if self.total_estimated_duration_minutes == 0:
            return 0.0

        # Ideal parallel time (if unlimited parallelism)
        ideal_time = max(a.estimated_duration_minutes for a in self.assignments) if self.assignments else 0

        # Actual parallel time (with max_parallel_agents constraint)
        actual_time = self.total_estimated_duration_minutes

        # Sequential time
        sequential_time = sum(a.estimated_duration_minutes for a in self.assignments)

        # Efficiency = (Sequential - Actual) / (Sequential - Ideal)
        if sequential_time == ideal_time:
            return 1.0

        efficiency = (sequential_time - actual_time) / (sequential_time - ideal_time)
        return max(0.0, min(1.0, efficiency))

    def get_underutilized_phases(self, threshold: float = 0.5) -> List[ExecutionPhase]:
        """
        Find phases with low parallelism utilization.

        Args:
            threshold: Minimum utilization ratio (0.0 to 1.0)

        Returns:
            List of underutilized phases
        """
        underutilized = []

        for phase in self.phases:
            utilization = phase.get_parallelism() / self.max_parallel_agents
            if utilization < threshold:
                underutilized.append(phase)

        return underutilized

    def suggest_optimizations(self) -> List[str]:
        """
        Suggest optimizations for the execution plan.

        Returns:
            List of optimization suggestions
        """
        suggestions = []

        # Check for bottlenecks
        bottlenecks = self.get_bottlenecks()
        if bottlenecks:
            suggestions.append(
                f"Found {len(bottlenecks)} bottleneck tasks on critical path. "
                f"Consider breaking them down or using faster agents."
            )

        # Check parallelism efficiency
        efficiency = self.calculate_parallelism_efficiency()
        if efficiency < 0.7:
            suggestions.append(
                f"Parallelism efficiency is {efficiency:.1%}. "
                f"Consider reorganizing dependencies to increase parallelism."
            )

        # Check underutilized phases
        underutilized = self.get_underutilized_phases()
        if len(underutilized) > len(self.phases) / 2:
            suggestions.append(
                f"{len(underutilized)} phases are underutilized. "
                f"Consider merging phases or adding more concurrent tasks."
            )

        # Check long sequential chains
        if self.critical_path and len(self.critical_path.task_ids) > 10:
            suggestions.append(
                f"Critical path has {len(self.critical_path.task_ids)} tasks. "
                f"Look for opportunities to parallelize sequential tasks."
            )

        return suggestions

    # ============================================================================
    # Methods: Serialization
    # ============================================================================

    def to_dict(self) -> Dict[str, Any]:
        """Convert execution plan to dictionary for serialization."""
        return {
            "plan_id": self.plan_id,
            "task_id": self.task_id,
            "plan_name": self.plan_name,
            "description": self.description,
            "phases": [p.to_dict() for p in self.phases],
            "total_estimated_duration_minutes": self.total_estimated_duration_minutes,
            "sequential_duration_minutes": self.sequential_duration_minutes,
            "total_estimated_cost_usd": self.total_estimated_cost_usd,
            "max_parallel_agents": self.max_parallel_agents,
            "estimated_kb_queries": self.estimated_kb_queries,
            "status": self.status.value,
            "metrics": self.metrics.to_dict(),
            "critical_path": self.critical_path.to_dict() if self.critical_path else None,
            "parallelism_efficiency": self.calculate_parallelism_efficiency(),
            "created_at": self.created_at,
            "optimization_strategy": self.optimization_strategy
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    def visualize_dag(self) -> str:
        """
        Generate text visualization of dependency DAG.

        Returns:
            ASCII art representation of the DAG
        """
        if not self.dependency_graph or nx is None:
            return "Dependency graph not available (networkx not installed)"

        # Simple text representation
        lines = ["Execution Plan DAG:", "=" * 50]

        for phase in self.phases:
            lines.append(f"\nPhase {phase.phase_number}: {phase.phase_name}")
            lines.append(f"  Parallelism: {phase.get_parallelism()} tasks")
            lines.append(f"  Duration: {phase.estimated_duration_minutes:.1f} minutes")

            for assignment in phase.assignments:
                prefix = "  * " if assignment.is_critical_path else "  - "
                lines.append(
                    f"{prefix}{assignment.agent_name}: {assignment.task_id}"
                )

        return "\n".join(lines)

    def __str__(self) -> str:
        """String representation."""
        return (
            f"ExecutionPlan({self.plan_id}, "
            f"phases={len(self.phases)}, "
            f"tasks={len(self.assignments)}, "
            f"duration={self.total_estimated_duration_minutes:.1f}m)"
        )

    def __repr__(self) -> str:
        """Detailed representation."""
        return self.__str__()
