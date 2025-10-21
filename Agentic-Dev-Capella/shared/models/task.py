"""
shared/models/task.py

Data models for tasks flowing through the pipeline.
Defines task structure, status, and metadata.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
import uuid


class TaskType(Enum):
    """Types of tasks in the pipeline."""
    DISCOVERY = "discovery"
    CODE_INGESTION = "code_ingestion"
    STATIC_ANALYSIS = "static_analysis"
    ARCHITECTURE = "architecture"
    DEVELOPMENT = "development"
    CODE_VALIDATION = "code_validation"
    QUALITY_CHECK = "quality_check"
    BUILD = "build"
    QA_TESTING = "qa_testing"
    INTEGRATION_TEST = "integration_test"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"


class TaskStatus(Enum):
    """Status of a task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VALIDATION_FAILED = "validation_failed"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Priority levels for tasks."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class HierarchyLevel(Enum):
    """Hierarchical levels for task ordering."""
    INFRASTRUCTURE = 0
    BACKEND = 1
    INTEGRATION = 2
    UI = 3


@dataclass
class TaskDependency:
    """Represents a dependency between tasks."""
    task_id: str
    dependency_type: str  # blocks, requires, enhances
    required: bool = True


@dataclass
class ValidationResult:
    """Result from a validation agent."""
    passed: bool
    validator_name: str
    timestamp: datetime
    issues: List[str] = field(default_factory=list)
    feedback: Optional[str] = None
    retry_count: int = 0


@dataclass
class Task:
    """
    Core task model representing work items in the pipeline.
    """
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: TaskType = TaskType.DEVELOPMENT
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    
    # Component information
    component_id: str = ""
    component_name: str = ""
    hierarchy_level: HierarchyLevel = HierarchyLevel.BACKEND
    
    # Dependencies
    dependencies: List[TaskDependency] = field(default_factory=list)
    blocked_by: List[str] = field(default_factory=list)
    
    # Content and context
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Validation tracking
    validation_results: List[ValidationResult] = field(default_factory=list)
    rejection_count: int = 0
    escalation_threshold: int = 3
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    assigned_to: Optional[str] = None  # Agent name
    created_by: Optional[str] = None  # Agent that created this task
    
    # Audit trail
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_validation_result(self, result: ValidationResult):
        """Add a validation result and update rejection count."""
        self.validation_results.append(result)
        if not result.passed:
            self.rejection_count += 1
            result.retry_count = self.rejection_count
            
            if self.rejection_count >= self.escalation_threshold:
                self.status = TaskStatus.ESCALATED
    
    def should_escalate(self) -> bool:
        """Check if task should be escalated."""
        return self.rejection_count >= self.escalation_threshold
    
    def update_status(self, new_status: TaskStatus, agent_name: str):
        """Update status and record in history."""
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        self.history.append({
            "timestamp": self.updated_at,
            "agent": agent_name,
            "old_status": old_status.value,
            "new_status": new_status.value
        })
    
    def is_blocked(self) -> bool:
        """Check if task is blocked by dependencies."""
        return len(self.blocked_by) > 0 or self.status == TaskStatus.BLOCKED
    
    def can_start(self, completed_tasks: set) -> bool:
        """Check if all dependencies are satisfied."""
        if self.is_blocked():
            return False
        
        required_deps = [
            dep.task_id for dep in self.dependencies if dep.required
        ]
        return all(dep_id in completed_tasks for dep_id in required_deps)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type.value,
            "status": self.status.value,
            "priority": self.priority.value,
            "component_id": self.component_id,
            "component_name": self.component_name,
            "hierarchy_level": self.hierarchy_level.value,
            "rejection_count": self.rejection_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "assigned_to": self.assigned_to,
            "validation_count": len(self.validation_results),
            "dependencies_count": len(self.dependencies),
            "blocked": self.is_blocked()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary."""
        task = cls(
            task_id=data.get("task_id", str(uuid.uuid4())),
            task_type=TaskType(data.get("task_type", "development")),
            status=TaskStatus(data.get("status", "pending")),
            priority=TaskPriority(data.get("priority", "medium")),
            component_id=data.get("component_id", ""),
            component_name=data.get("component_name", "")
        )
        return task


@dataclass
class TaskTicket:
    """
    Simplified task ticket for communication between agents.
    """
    ticket_id: str
    task_type: TaskType
    component_id: str
    priority: TaskPriority
    context: Dict[str, Any]
    
    def to_full_task(self) -> Task:
        """Convert ticket to full Task object."""
        return Task(
            task_id=self.ticket_id,
            task_type=self.task_type,
            component_id=self.component_id,
            priority=self.priority,
            context=self.context
        )
