"""
shared/models/agent_capability.py

Agent capability model for dynamic agent selection and orchestration.
Defines what each agent can do, their constraints, and performance characteristics.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any
from enum import Enum
import json


class AgentType(Enum):
    """High-level categorization of agent types."""
    # Phase 1: Legacy Modernization
    LEGACY_MODERNIZATION = "legacy_modernization"
    ORCHESTRATION = "orchestration"
    DISCOVERY = "discovery"
    ETL = "etl"
    ARCHITECTURE = "architecture"
    DEVELOPMENT = "development"
    VALIDATION = "validation"
    BUILD = "build"
    QA = "qa"
    INTEGRATION = "integration"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    SECURITY = "security"

    # Phase 2: Dynamic Multi-Agent System
    FRONTEND_ENGINEER = "frontend_engineer"
    BACKEND_ENGINEER = "backend_engineer"
    DATABASE_ENGINEER = "database_engineer"
    DEVOPS_ENGINEER = "devops_engineer"
    MOBILE_ENGINEER = "mobile_engineer"
    DATA_ENGINEER = "data_engineer"
    QA_ENGINEER = "qa_engineer"
    SECURITY_ENGINEER = "security_engineer"
    PERFORMANCE_ENGINEER = "performance_engineer"
    COMPLIANCE_ENGINEER = "compliance_engineer"

    # Multimodal Processing
    MULTIMODAL_PROCESSOR = "multimodal_processor"
    VISION_PROCESSOR = "vision_processor"
    DOCUMENT_PROCESSOR = "document_processor"
    AUDIO_PROCESSOR = "audio_processor"
    VIDEO_PROCESSOR = "video_processor"


class InputModality(Enum):
    """Types of input modalities agents can process."""
    TEXT = "text"
    CODE = "code"
    IMAGE = "image"
    PDF = "pdf"
    VIDEO = "video"
    AUDIO = "audio"
    DESIGN_FILE = "design_file"  # Figma, Sketch, etc.
    DIAGRAM = "diagram"
    DATABASE_SCHEMA = "database_schema"
    API_SPEC = "api_spec"  # OpenAPI, GraphQL schema, etc.


class KBQueryStrategy(Enum):
    """Knowledge base query strategies."""
    NEVER = "never"  # Never query KB
    ONCE = "once"  # Query once at initialization
    MINIMAL = "minimal"  # Query sparingly (initialization + major decisions)
    ADAPTIVE = "adaptive"  # Query based on context changes and checkpoints
    AGGRESSIVE = "aggressive"  # Query very frequently


@dataclass
class PerformanceMetrics:
    """Performance metrics for an agent."""
    avg_task_duration_minutes: float = 15.0
    p95_task_duration_minutes: float = 30.0
    success_rate: float = 1.0  # 0.0 to 1.0
    retry_rate: float = 0.0  # 0.0 to 1.0
    avg_validation_failures: float = 0.0
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0

    def calculate_success_rate(self) -> float:
        """Calculate success rate from task counts."""
        total = self.total_tasks_completed + self.total_tasks_failed
        if total == 0:
            return 1.0
        return self.total_tasks_completed / total


@dataclass
class CostMetrics:
    """Cost metrics for running an agent."""
    cost_per_task_usd: float = 0.0
    cost_per_hour_usd: float = 0.0
    token_usage_per_task: int = 0
    kb_queries_per_task: int = 0
    estimated_monthly_cost_usd: float = 0.0


@dataclass
class KBIntegrationConfig:
    """Configuration for knowledge base integration."""
    has_vector_db_access: bool = True
    kb_query_strategy: KBQueryStrategy = KBQueryStrategy.ADAPTIVE
    kb_query_frequency: int = 10  # Query every N operations
    kb_query_triggers: List[str] = field(default_factory=lambda: [
        "start", "error", "validation_fail", "checkpoint"
    ])
    preferred_query_types: List[str] = field(default_factory=lambda: [
        "similar_code", "best_practices"
    ])
    max_kb_queries_per_task: int = 50
    kb_cache_enabled: bool = True
    kb_cache_ttl_seconds: int = 300


@dataclass
class AgentCapability:
    """
    Comprehensive agent capability definition.

    Describes what an agent can do, its constraints, performance characteristics,
    and knowledge base integration strategy.
    """

    # ============================================================================
    # Core Metadata
    # ============================================================================
    agent_id: str  # Unique identifier (Vertex AI resource ID in production)
    agent_name: str  # Human-readable name
    agent_type: AgentType  # High-level type
    description: str  # What this agent does
    version: str = "1.0.0"

    # ============================================================================
    # Capabilities
    # ============================================================================
    capabilities: Set[str] = field(default_factory=set)
    """
    Set of capability tags, e.g.:
    - "code_implementation", "legacy_translation", "test_generation"
    - "react_development", "api_design", "database_schema_design"
    - "ui_mockup_analysis", "pdf_parsing", "video_transcription"
    """

    input_modalities: Set[InputModality] = field(default_factory=lambda: {InputModality.TEXT})
    output_types: Set[str] = field(default_factory=set)
    """
    Types of output this agent produces, e.g.:
    - "python_code", "java_code", "typescript_code"
    - "architecture_diagram", "api_spec", "test_cases"
    - "ui_components", "database_schema", "deployment_manifest"
    """

    # ============================================================================
    # Technology Stack
    # ============================================================================
    supported_languages: List[str] = field(default_factory=list)
    """Programming languages: python, java, typescript, go, rust, etc."""

    supported_frameworks: List[str] = field(default_factory=list)
    """Frameworks: React, Vue, Django, Spring Boot, Express, etc."""

    supported_platforms: List[str] = field(default_factory=list)
    """Platforms: web, mobile, cloud, embedded, etc."""

    supported_cloud_providers: List[str] = field(default_factory=list)
    """Cloud providers: gcp, aws, azure, etc."""

    # ============================================================================
    # Dependencies and Relationships
    # ============================================================================
    required_agents: List[str] = field(default_factory=list)
    """Agent IDs that must be available for this agent to function."""

    optional_agents: List[str] = field(default_factory=list)
    """Agent IDs that enhance this agent's capabilities if available."""

    replaces_agents: List[str] = field(default_factory=list)
    """Agent IDs that this agent can replace (for versioning/upgrades)."""

    collaborates_with: List[str] = field(default_factory=list)
    """Agent IDs this agent frequently works with."""

    # ============================================================================
    # Performance Characteristics
    # ============================================================================
    performance_metrics: PerformanceMetrics = field(default_factory=PerformanceMetrics)

    parallel_capacity: int = 1
    """Number of tasks this agent can handle concurrently."""

    max_concurrent_tasks: int = 5
    """Maximum concurrent tasks allowed."""

    priority_levels: List[str] = field(default_factory=lambda: ["low", "medium", "high", "critical"])
    """Priority levels this agent supports."""

    # ============================================================================
    # Constraints
    # ============================================================================
    max_complexity_score: Optional[int] = None
    """Maximum code complexity this agent can handle (cyclomatic complexity)."""

    max_lines_of_code: Optional[int] = None
    """Maximum lines of code per task."""

    min_context_length: int = 0
    """Minimum context length (tokens) required."""

    max_context_length: int = 100000
    """Maximum context length (tokens) supported."""

    timeout_seconds: int = 600
    """Default timeout for tasks (10 minutes)."""

    max_retries: int = 3
    """Maximum retry attempts on failure."""

    # ============================================================================
    # Cost Metrics
    # ============================================================================
    cost_metrics: CostMetrics = field(default_factory=CostMetrics)

    # ============================================================================
    # Model Configuration
    # ============================================================================
    model: str = "gemini-2.0-flash"
    """LLM model used by this agent."""

    model_parameters: Dict[str, Any] = field(default_factory=dict)
    """Model-specific parameters (temperature, top_p, etc.)."""

    uses_vision_model: bool = False
    """Whether this agent uses vision/multimodal capabilities."""

    uses_reasoning_model: bool = False
    """Whether this agent uses advanced reasoning (e.g., Gemini Thinking)."""

    # ============================================================================
    # Knowledge Base Integration
    # ============================================================================
    kb_integration: KBIntegrationConfig = field(default_factory=KBIntegrationConfig)

    # ============================================================================
    # Metadata and Tags
    # ============================================================================
    tags: Set[str] = field(default_factory=set)
    """Additional tags for categorization and search."""

    domain_expertise: List[str] = field(default_factory=list)
    """Domain expertise areas (e.g., "fintech", "healthcare", "ecommerce")."""

    compliance_standards: List[str] = field(default_factory=list)
    """Compliance standards supported (e.g., "GDPR", "HIPAA", "PCI-DSS")."""

    # ============================================================================
    # Status and Availability
    # ============================================================================
    is_active: bool = True
    is_deployed: bool = False
    last_updated: str = ""
    created_at: str = ""

    # ============================================================================
    # Methods
    # ============================================================================

    def matches_requirements(
        self,
        required_capabilities: Set[str],
        optional_capabilities: Optional[Set[str]] = None,
        language: Optional[str] = None,
        framework: Optional[str] = None
    ) -> bool:
        """
        Check if this agent matches the given requirements.

        Args:
            required_capabilities: Required capability tags
            optional_capabilities: Optional capability tags (bonus if matched)
            language: Required programming language
            framework: Required framework

        Returns:
            True if agent matches all required criteria
        """
        # Check required capabilities
        if not required_capabilities.issubset(self.capabilities):
            return False

        # Check language
        if language and language not in self.supported_languages:
            return False

        # Check framework
        if framework and framework not in self.supported_frameworks:
            return False

        return True

    def calculate_match_score(
        self,
        required_capabilities: Set[str],
        optional_capabilities: Optional[Set[str]] = None,
        language: Optional[str] = None,
        framework: Optional[str] = None,
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calculate match score (0.0 to 1.0) for given requirements.

        Args:
            required_capabilities: Required capabilities
            optional_capabilities: Optional capabilities
            language: Programming language
            framework: Framework
            weights: Scoring weights

        Returns:
            Match score between 0.0 and 1.0
        """
        if weights is None:
            weights = {
                "capabilities": 0.4,
                "performance": 0.3,
                "cost": 0.2,
                "availability": 0.1
            }

        score = 0.0

        # Capability match score
        if required_capabilities:
            matched = len(required_capabilities & self.capabilities)
            required = len(required_capabilities)
            capability_score = matched / required if required > 0 else 0.0
        else:
            capability_score = 1.0

        # Optional capabilities bonus
        if optional_capabilities:
            optional_matched = len(optional_capabilities & self.capabilities)
            optional_total = len(optional_capabilities)
            optional_score = optional_matched / optional_total if optional_total > 0 else 0.0
            capability_score = (capability_score * 0.8) + (optional_score * 0.2)

        score += capability_score * weights["capabilities"]

        # Performance score
        performance_score = self.performance_metrics.calculate_success_rate()
        score += performance_score * weights["performance"]

        # Cost score (inverse - lower cost is better)
        if self.cost_metrics.cost_per_task_usd > 0:
            # Normalize to 0-1 range (assuming max cost of $1 per task)
            cost_score = max(0.0, 1.0 - (self.cost_metrics.cost_per_task_usd / 1.0))
        else:
            cost_score = 1.0
        score += cost_score * weights["cost"]

        # Availability score
        availability_score = 1.0 if self.is_active and self.is_deployed else 0.0
        score += availability_score * weights["availability"]

        return min(1.0, max(0.0, score))

    def can_handle_complexity(self, complexity_score: int) -> bool:
        """Check if agent can handle given complexity."""
        if self.max_complexity_score is None:
            return True
        return complexity_score <= self.max_complexity_score

    def can_handle_size(self, lines_of_code: int) -> bool:
        """Check if agent can handle given code size."""
        if self.max_lines_of_code is None:
            return True
        return lines_of_code <= self.max_lines_of_code

    def supports_modality(self, modality: InputModality) -> bool:
        """Check if agent supports given input modality."""
        return modality in self.input_modalities

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "agent_type": self.agent_type.value,
            "description": self.description,
            "version": self.version,
            "capabilities": list(self.capabilities),
            "input_modalities": [m.value for m in self.input_modalities],
            "output_types": list(self.output_types),
            "supported_languages": self.supported_languages,
            "supported_frameworks": self.supported_frameworks,
            "supported_platforms": self.supported_platforms,
            "performance_metrics": {
                "avg_task_duration_minutes": self.performance_metrics.avg_task_duration_minutes,
                "success_rate": self.performance_metrics.success_rate,
                "total_tasks_completed": self.performance_metrics.total_tasks_completed
            },
            "cost_metrics": {
                "cost_per_task_usd": self.cost_metrics.cost_per_task_usd
            },
            "kb_integration": {
                "has_vector_db_access": self.kb_integration.has_vector_db_access,
                "kb_query_strategy": self.kb_integration.kb_query_strategy.value,
                "kb_query_frequency": self.kb_integration.kb_query_frequency
            },
            "model": self.model,
            "is_active": self.is_active,
            "is_deployed": self.is_deployed
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentCapability':
        """Create AgentCapability from dictionary."""
        # Parse enums
        agent_type = AgentType(data["agent_type"])
        input_modalities = {InputModality(m) for m in data.get("input_modalities", ["text"])}

        # Parse nested objects
        performance_metrics = PerformanceMetrics(**data.get("performance_metrics", {}))
        cost_metrics = CostMetrics(**data.get("cost_metrics", {}))

        kb_config_data = data.get("kb_integration", {})
        if "kb_query_strategy" in kb_config_data:
            kb_config_data["kb_query_strategy"] = KBQueryStrategy(kb_config_data["kb_query_strategy"])
        kb_integration = KBIntegrationConfig(**kb_config_data)

        return cls(
            agent_id=data["agent_id"],
            agent_name=data["agent_name"],
            agent_type=agent_type,
            description=data["description"],
            version=data.get("version", "1.0.0"),
            capabilities=set(data.get("capabilities", [])),
            input_modalities=input_modalities,
            output_types=set(data.get("output_types", [])),
            supported_languages=data.get("supported_languages", []),
            supported_frameworks=data.get("supported_frameworks", []),
            supported_platforms=data.get("supported_platforms", []),
            performance_metrics=performance_metrics,
            cost_metrics=cost_metrics,
            kb_integration=kb_integration,
            model=data.get("model", "gemini-2.0-flash"),
            is_active=data.get("is_active", True),
            is_deployed=data.get("is_deployed", False)
        )

    def __str__(self) -> str:
        """String representation."""
        return f"AgentCapability({self.agent_name}, type={self.agent_type.value}, capabilities={len(self.capabilities)})"

    def __repr__(self) -> str:
        """Detailed representation."""
        return self.__str__()
