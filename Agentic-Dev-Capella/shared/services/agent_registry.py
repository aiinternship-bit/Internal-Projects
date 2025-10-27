"""
shared/services/agent_registry.py

Centralized registry service for agent capabilities, metrics, and availability.
Provides capability search, performance tracking, and KB usage statistics.
"""

from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import asdict
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

from shared.models.agent_capability import (
    AgentCapability,
    AgentType,
    InputModality,
    KBQueryStrategy,
    PerformanceMetrics
)


class AgentRegistryService:
    """
    Centralized registry for agent capabilities and performance tracking.

    Responsibilities:
    1. Register/deregister agents with their capabilities
    2. Search for agents by capability, language, framework
    3. Track agent performance metrics (success rate, duration, cost)
    4. Monitor agent availability and load
    5. Track KB query usage and effectiveness
    6. Provide agent recommendations based on requirements
    """

    def __init__(
        self,
        persistence_path: Optional[str] = None,
        enable_persistence: bool = True,
        auto_save: bool = True
    ):
        """
        Initialize Agent Registry Service.

        Args:
            persistence_path: Path to save registry data
            enable_persistence: Enable saving/loading from disk
            auto_save: Automatically save after modifications
        """
        # Core registry storage
        self._agents: Dict[str, AgentCapability] = {}
        self._agent_name_to_id: Dict[str, str] = {}

        # Capability indexes for fast search
        self._capability_index: Dict[str, Set[str]] = {}
        self._language_index: Dict[str, Set[str]] = {}
        self._framework_index: Dict[str, Set[str]] = {}
        self._type_index: Dict[AgentType, Set[str]] = {}
        self._modality_index: Dict[InputModality, Set[str]] = {}

        # Performance tracking
        self._performance_history: Dict[str, List[Dict[str, Any]]] = {}

        # KB usage tracking
        self._kb_usage_stats: Dict[str, Dict[str, Any]] = {}

        # Availability tracking
        self._agent_load: Dict[str, int] = {}
        self._agent_last_seen: Dict[str, str] = {}

        # Persistence
        self._persistence_path = persistence_path or "./data/agent_registry.json"
        self._enable_persistence = enable_persistence
        self._auto_save = auto_save

        # Load existing registry if available
        if self._enable_persistence:
            self._load_from_disk()

    # ============================================================================
    # Agent Registration and Management
    # ============================================================================

    def register_agent(self, capability: AgentCapability) -> bool:
        """Register an agent with its capabilities."""
        # Check if agent already exists
        if capability.agent_id in self._agents:
            return False

        # Store agent capability
        self._agents[capability.agent_id] = capability

        # Update name index
        self._agent_name_to_id[capability.agent_name] = capability.agent_id

        # Update capability index
        for cap in capability.capabilities:
            if cap not in self._capability_index:
                self._capability_index[cap] = set()
            self._capability_index[cap].add(capability.agent_id)

        # Update language index
        for lang in capability.supported_languages:
            if lang not in self._language_index:
                self._language_index[lang] = set()
            self._language_index[lang].add(capability.agent_id)

        # Update framework index
        for fw in capability.supported_frameworks:
            if fw not in self._framework_index:
                self._framework_index[fw] = set()
            self._framework_index[fw].add(capability.agent_id)

        # Update type index
        if capability.agent_type not in self._type_index:
            self._type_index[capability.agent_type] = set()
        self._type_index[capability.agent_type].add(capability.agent_id)

        # Update modality index
        for modality in capability.input_modalities:
            if modality not in self._modality_index:
                self._modality_index[modality] = set()
            self._modality_index[modality].add(capability.agent_id)

        # Initialize performance tracking
        self._performance_history[capability.agent_id] = []

        # Initialize KB usage stats
        self._kb_usage_stats[capability.agent_id] = {
            "total_queries": 0,
            "queries_by_type": {},
            "avg_query_time_ms": 0.0,
            "cache_hit_rate": 0.0,
            "total_cache_hits": 0,
            "total_cache_misses": 0
        }

        # Set initial load and last seen
        self._agent_load[capability.agent_id] = 0
        self._agent_last_seen[capability.agent_id] = datetime.utcnow().isoformat()

        # Auto-save if enabled
        if self._auto_save:
            self._save_to_disk()

        return True

    def deregister_agent(self, agent_id: str) -> bool:
        """Deregister an agent from the registry."""
        if agent_id not in self._agents:
            return False

        agent = self._agents[agent_id]

        # Remove from name index
        if agent.agent_name in self._agent_name_to_id:
            del self._agent_name_to_id[agent.agent_name]

        # Remove from capability index
        for cap in agent.capabilities:
            if cap in self._capability_index:
                self._capability_index[cap].discard(agent_id)
                if not self._capability_index[cap]:
                    del self._capability_index[cap]

        # Remove from language index
        for lang in agent.supported_languages:
            if lang in self._language_index:
                self._language_index[lang].discard(agent_id)
                if not self._language_index[lang]:
                    del self._language_index[lang]

        # Remove from framework index
        for fw in agent.supported_frameworks:
            if fw in self._framework_index:
                self._framework_index[fw].discard(agent_id)
                if not self._framework_index[fw]:
                    del self._framework_index[fw]

        # Remove from type index
        if agent.agent_type in self._type_index:
            self._type_index[agent.agent_type].discard(agent_id)
            if not self._type_index[agent.agent_type]:
                del self._type_index[agent.agent_type]

        # Remove from modality index
        for modality in agent.input_modalities:
            if modality in self._modality_index:
                self._modality_index[modality].discard(agent_id)
                if not self._modality_index[modality]:
                    del self._modality_index[modality]

        # Remove from main storage
        del self._agents[agent_id]

        # Optionally preserve performance history
        # (keeping it for analytics even after deregistration)

        # Auto-save if enabled
        if self._auto_save:
            self._save_to_disk()

        return True

    def update_agent_capability(
        self,
        agent_id: str,
        capability: AgentCapability
    ) -> bool:
        """Update an existing agent's capability definition."""
        if agent_id not in self._agents:
            return False

        # Preserve performance history and KB stats
        perf_history = self._performance_history.get(agent_id, [])
        kb_stats = self._kb_usage_stats.get(agent_id, {})
        load = self._agent_load.get(agent_id, 0)
        last_seen = self._agent_last_seen.get(agent_id)

        # Deregister old capability
        self.deregister_agent(agent_id)

        # Register new capability (will reinitialize tracking)
        success = self.register_agent(capability)

        if success:
            # Restore preserved data
            self._performance_history[agent_id] = perf_history
            self._kb_usage_stats[agent_id] = kb_stats
            self._agent_load[agent_id] = load
            if last_seen:
                self._agent_last_seen[agent_id] = last_seen

        return success

    def get_agent(self, agent_id: str) -> Optional[AgentCapability]:
        """Get agent capability by ID."""
        return self._agents.get(agent_id)

    def get_agent_by_name(self, agent_name: str) -> Optional[AgentCapability]:
        """Get agent capability by name."""
        agent_id = self._agent_name_to_id.get(agent_name)
        if agent_id:
            return self._agents.get(agent_id)
        return None

    def list_all_agents(
        self,
        active_only: bool = True,
        deployed_only: bool = False
    ) -> List[AgentCapability]:
        """List all registered agents."""
        agents = list(self._agents.values())

        # Filter by active status
        if active_only:
            agents = [a for a in agents if a.is_active]

        # Filter by deployed status
        if deployed_only:
            agents = [a for a in agents if a.is_deployed]

        return agents

    # ============================================================================
    # Capability Search and Filtering
    # ============================================================================

    def search_by_capability(
        self,
        required_capabilities: Set[str],
        optional_capabilities: Optional[Set[str]] = None,
        language: Optional[str] = None,
        framework: Optional[str] = None,
        agent_type: Optional[AgentType] = None,
        input_modality: Optional[InputModality] = None
    ) -> List[AgentCapability]:
        """Search for agents by capabilities and filters."""
        # Start with agents that have at least one required capability
        candidate_ids = set()

        if required_capabilities:
            # Find agents with each required capability
            capability_matches = []
            for cap in required_capabilities:
                if cap in self._capability_index:
                    capability_matches.append(self._capability_index[cap])

            # Intersect to find agents with ALL required capabilities
            if capability_matches:
                candidate_ids = set.intersection(*capability_matches)
            else:
                # No agents have the required capabilities
                return []
        else:
            # No required capabilities - start with all agents
            candidate_ids = set(self._agents.keys())

        # Apply language filter
        if language and language in self._language_index:
            candidate_ids &= self._language_index[language]

        # Apply framework filter
        if framework and framework in self._framework_index:
            candidate_ids &= self._framework_index[framework]

        # Apply type filter
        if agent_type and agent_type in self._type_index:
            candidate_ids &= self._type_index[agent_type]

        # Apply modality filter
        if input_modality and input_modality in self._modality_index:
            candidate_ids &= self._modality_index[input_modality]

        # Get agent capabilities
        candidates = [self._agents[aid] for aid in candidate_ids if aid in self._agents]

        # Calculate match scores
        scored_agents = []
        for agent in candidates:
            score = agent.calculate_match_score(
                required_capabilities=required_capabilities,
                optional_capabilities=optional_capabilities,
                language=language,
                framework=framework
            )
            scored_agents.append((agent, score))

        # Sort by score descending
        scored_agents.sort(key=lambda x: x[1], reverse=True)

        # Return agents only (without scores)
        return [agent for agent, score in scored_agents]

    def search_by_language(self, language: str) -> List[AgentCapability]:
        """Search for agents supporting a specific language."""
        if language not in self._language_index:
            return []

        agent_ids = self._language_index[language]
        return [self._agents[aid] for aid in agent_ids if aid in self._agents]

    def search_by_framework(self, framework: str) -> List[AgentCapability]:
        """Search for agents supporting a specific framework."""
        if framework not in self._framework_index:
            return []

        agent_ids = self._framework_index[framework]
        return [self._agents[aid] for aid in agent_ids if aid in self._agents]

    def search_by_type(self, agent_type: AgentType) -> List[AgentCapability]:
        """Search for agents of a specific type."""
        if agent_type not in self._type_index:
            return []

        agent_ids = self._type_index[agent_type]
        return [self._agents[aid] for aid in agent_ids if aid in self._agents]

    def search_by_modality(
        self,
        modality: InputModality
    ) -> List[AgentCapability]:
        """Search for agents supporting a specific input modality."""
        if modality not in self._modality_index:
            return []

        agent_ids = self._modality_index[modality]
        return [self._agents[aid] for aid in agent_ids if aid in self._agents]

    def recommend_agents(
        self,
        required_capabilities: Set[str],
        constraints: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> List[Tuple[AgentCapability, float]]:
        """Recommend top agents for given requirements."""
        # Search for matching agents
        candidates = self.search_by_capability(required_capabilities)

        if not candidates:
            return []

        # Calculate comprehensive scores
        scored_agents = []
        for agent in candidates:
            # Base capability score
            cap_score = agent.calculate_match_score(required_capabilities)

            # Performance factor (success rate)
            perf_factor = agent.performance_metrics.success_rate

            # Availability factor (lower load is better)
            load = self._agent_load.get(agent.agent_id, 0)
            max_load = agent.max_concurrent_tasks
            availability_factor = 1.0 - (load / max_load) if max_load > 0 else 0.0

            # Cost factor (lower cost is better, normalize)
            cost_factor = 1.0
            if constraints and "max_cost_usd" in constraints:
                max_cost = constraints["max_cost_usd"]
                if agent.cost_metrics.cost_per_task_usd > 0:
                    cost_factor = max(0.0, 1.0 - (agent.cost_metrics.cost_per_task_usd / max_cost))

            # Weighted comprehensive score
            comprehensive_score = (
                cap_score * 0.4 +
                perf_factor * 0.3 +
                availability_factor * 0.2 +
                cost_factor * 0.1
            )

            scored_agents.append((agent, comprehensive_score))

        # Sort by score descending
        scored_agents.sort(key=lambda x: x[1], reverse=True)

        # Return top_k
        return scored_agents[:top_k]

    # ============================================================================
    # Performance Tracking
    # ============================================================================

    def update_performance(
        self,
        agent_id: str,
        success: bool,
        duration_minutes: float,
        cost_usd: float = 0.0,
        task_type: Optional[str] = None,
        validation_failures: int = 0
    ) -> bool:
        """Update agent performance metrics after task completion."""
        if agent_id not in self._agents:
            return False

        agent = self._agents[agent_id]

        # Create performance record
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "success": success,
            "duration_minutes": duration_minutes,
            "cost_usd": cost_usd,
            "task_type": task_type,
            "validation_failures": validation_failures
        }

        # Add to history
        self._performance_history[agent_id].append(record)

        # Update aggregate metrics
        metrics = agent.performance_metrics

        if success:
            metrics.total_tasks_completed += 1
        else:
            metrics.total_tasks_failed += 1

        # Update moving average for duration (last 100 tasks)
        recent_history = self._performance_history[agent_id][-100:]
        durations = [r["duration_minutes"] for r in recent_history]
        metrics.avg_task_duration_minutes = sum(durations) / len(durations) if durations else 0.0

        # Update p95 duration
        if durations:
            sorted_durations = sorted(durations)
            p95_index = int(len(sorted_durations) * 0.95)
            metrics.p95_task_duration_minutes = sorted_durations[p95_index]

        # Update success rate
        metrics.success_rate = metrics.calculate_success_rate()

        # Update average validation failures
        validation_counts = [r["validation_failures"] for r in recent_history]
        metrics.avg_validation_failures = sum(validation_counts) / len(validation_counts) if validation_counts else 0.0

        # Update retry rate
        tasks_with_retries = sum(1 for v in validation_counts if v > 0)
        metrics.retry_rate = tasks_with_retries / len(validation_counts) if validation_counts else 0.0

        # Auto-save if enabled
        if self._auto_save:
            self._save_to_disk()

        return True

    def get_performance_metrics(
        self,
        agent_id: str
    ) -> Optional[PerformanceMetrics]:
        """Get current performance metrics for an agent."""
        agent = self._agents.get(agent_id)
        if agent:
            return agent.performance_metrics
        return None

    def get_performance_history(
        self,
        agent_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get performance history for an agent."""
        history = self._performance_history.get(agent_id, [])
        return history[-limit:] if limit else history

    def compare_agents(
        self,
        agent_ids: List[str],
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Compare performance metrics across multiple agents."""
        if metrics is None:
            metrics = ["success_rate", "avg_duration", "avg_cost"]

        comparison = {
            "agents": [],
            "metrics": {}
        }

        for agent_id in agent_ids:
            agent = self._agents.get(agent_id)
            if not agent:
                continue

            agent_data = {
                "agent_id": agent_id,
                "agent_name": agent.agent_name
            }

            perf = agent.performance_metrics

            if "success_rate" in metrics:
                agent_data["success_rate"] = perf.success_rate

            if "avg_duration" in metrics:
                agent_data["avg_duration_minutes"] = perf.avg_task_duration_minutes

            if "avg_cost" in metrics:
                agent_data["avg_cost_usd"] = agent.cost_metrics.cost_per_task_usd

            if "total_tasks" in metrics:
                agent_data["total_tasks"] = perf.total_tasks_completed + perf.total_tasks_failed

            comparison["agents"].append(agent_data)

        return comparison

    # ============================================================================
    # KB Usage Tracking
    # ============================================================================

    def update_kb_usage(
        self,
        agent_id: str,
        query_type: str,
        query_time_ms: float,
        cache_hit: bool = False
    ) -> bool:
        """Update KB usage statistics for an agent."""
        if agent_id not in self._kb_usage_stats:
            return False

        stats = self._kb_usage_stats[agent_id]

        # Update total queries
        stats["total_queries"] += 1

        # Update queries by type
        if query_type not in stats["queries_by_type"]:
            stats["queries_by_type"][query_type] = 0
        stats["queries_by_type"][query_type] += 1

        # Update cache stats
        if cache_hit:
            stats["total_cache_hits"] += 1
        else:
            stats["total_cache_misses"] += 1

        total_cache_attempts = stats["total_cache_hits"] + stats["total_cache_misses"]
        stats["cache_hit_rate"] = stats["total_cache_hits"] / total_cache_attempts if total_cache_attempts > 0 else 0.0

        # Update moving average for query time
        # Simple moving average over all queries
        prev_avg = stats["avg_query_time_ms"]
        n = stats["total_queries"]
        stats["avg_query_time_ms"] = ((prev_avg * (n - 1)) + query_time_ms) / n

        # Auto-save if enabled
        if self._auto_save:
            self._save_to_disk()

        return True

    def get_kb_usage_stats(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get KB usage statistics for an agent."""
        return self._kb_usage_stats.get(agent_id)

    def get_kb_effectiveness_score(self, agent_id: str) -> float:
        """Calculate KB effectiveness score for an agent."""
        stats = self._kb_usage_stats.get(agent_id)
        if not stats or stats["total_queries"] == 0:
            return 0.0

        agent = self._agents.get(agent_id)
        if not agent:
            return 0.0

        # Factor 1: Cache hit rate (higher is better)
        cache_score = stats["cache_hit_rate"]

        # Factor 2: Query efficiency (faster is better, normalize to 0-1)
        avg_time = stats["avg_query_time_ms"]
        # Assume 2000ms is the baseline, under 500ms is excellent
        time_score = max(0.0, 1.0 - (avg_time / 2000.0))

        # Factor 3: Success rate correlation (agents using KB should succeed)
        success_score = agent.performance_metrics.success_rate

        # Factor 4: Query frequency (using KB is good, but not excessively)
        queries_per_task = stats["total_queries"] / max(1, agent.performance_metrics.total_tasks_completed)
        # Optimal is 5-10 queries per task
        if 5 <= queries_per_task <= 10:
            frequency_score = 1.0
        elif queries_per_task < 5:
            frequency_score = queries_per_task / 5.0
        else:
            frequency_score = max(0.0, 1.0 - ((queries_per_task - 10) / 20.0))

        # Weighted effectiveness score
        effectiveness = (
            cache_score * 0.3 +
            time_score * 0.2 +
            success_score * 0.3 +
            frequency_score * 0.2
        )

        return effectiveness

    # ============================================================================
    # Availability and Load Tracking
    # ============================================================================

    def update_agent_load(
        self,
        agent_id: str,
        active_tasks: int
    ) -> bool:
        """Update current load for an agent."""
        if agent_id not in self._agents:
            return False

        self._agent_load[agent_id] = active_tasks
        self._agent_last_seen[agent_id] = datetime.utcnow().isoformat()

        return True

    def get_agent_load(self, agent_id: str) -> int:
        """Get current load for an agent."""
        return self._agent_load.get(agent_id, 0)

    def get_available_agents(
        self,
        max_load: Optional[int] = None
    ) -> List[AgentCapability]:
        """Get agents currently available for new tasks."""
        available = []

        for agent_id, agent in self._agents.items():
            # Only include active and deployed agents
            if not agent.is_active or not agent.is_deployed:
                continue

            current_load = self._agent_load.get(agent_id, 0)
            max_concurrent = max_load if max_load is not None else agent.max_concurrent_tasks

            if current_load < max_concurrent:
                available.append(agent)

        return available

    def is_agent_available(
        self,
        agent_id: str,
        required_capacity: int = 1
    ) -> bool:
        """Check if agent is available for new tasks."""
        agent = self._agents.get(agent_id)
        if not agent or not agent.is_active or not agent.is_deployed:
            return False

        current_load = self._agent_load.get(agent_id, 0)
        return (current_load + required_capacity) <= agent.max_concurrent_tasks

    # ============================================================================
    # Statistics and Analytics
    # ============================================================================

    def get_registry_stats(self) -> Dict[str, Any]:
        """Get overall registry statistics."""
        return {
            "total_agents": len(self._agents),
            "active_agents": sum(1 for a in self._agents.values() if a.is_active),
            "deployed_agents": sum(1 for a in self._agents.values() if a.is_deployed),
            "agents_by_type": {
                agent_type.value: len(agent_ids)
                for agent_type, agent_ids in self._type_index.items()
            },
            "total_capabilities": len(self._capability_index),
            "total_languages": len(self._language_index),
            "total_frameworks": len(self._framework_index),
            "total_tasks_completed": sum(
                a.performance_metrics.total_tasks_completed
                for a in self._agents.values()
            ),
            "total_kb_queries": sum(
                stats["total_queries"]
                for stats in self._kb_usage_stats.values()
            ),
            "avg_agent_load": (
                sum(self._agent_load.values()) / len(self._agent_load)
                if self._agent_load else 0.0
            )
        }

    def get_capability_coverage(self) -> Dict[str, int]:
        """Get coverage statistics for all capabilities."""
        return {
            capability: len(agent_ids)
            for capability, agent_ids in self._capability_index.items()
        }

    def identify_capability_gaps(
        self,
        required_capabilities: Set[str]
    ) -> Set[str]:
        """Identify capabilities with no or insufficient agent coverage."""
        gaps = set()

        for capability in required_capabilities:
            agent_count = len(self._capability_index.get(capability, set()))

            # No agents have this capability
            if agent_count == 0:
                gaps.add(capability)
            # Only one agent (no redundancy)
            elif agent_count < 2:
                gaps.add(f"{capability}_insufficient_redundancy")

        return gaps

    # ============================================================================
    # Persistence
    # ============================================================================

    def _save_to_disk(self) -> bool:
        """Save registry to disk."""
        if not self._enable_persistence:
            return False

        try:
            # Create directory if doesn't exist
            path = Path(self._persistence_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            # Prepare data for serialization
            data = {
                "version": "1.0",
                "timestamp": datetime.utcnow().isoformat(),
                "agents": {
                    agent_id: agent.to_dict()
                    for agent_id, agent in self._agents.items()
                },
                "performance_history": self._performance_history,
                "kb_usage_stats": self._kb_usage_stats,
                "agent_load": self._agent_load,
                "agent_last_seen": self._agent_last_seen
            }

            # Write to temp file first (atomic write)
            temp_path = str(path) + ".tmp"
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)

            # Rename to actual file (atomic operation)
            os.replace(temp_path, str(path))

            return True

        except Exception as e:
            print(f"Error saving registry to disk: {str(e)}")
            return False

    def _load_from_disk(self) -> bool:
        """Load registry from disk."""
        if not self._enable_persistence:
            return False

        try:
            path = Path(self._persistence_path)

            if not path.exists():
                return False

            with open(path, 'r') as f:
                data = json.load(f)

            # Load agents
            for agent_id, agent_dict in data.get("agents", {}).items():
                agent = AgentCapability.from_dict(agent_dict)
                # Register will rebuild all indexes
                self.register_agent(agent)

            # Restore performance history
            self._performance_history = data.get("performance_history", {})

            # Restore KB usage stats
            self._kb_usage_stats = data.get("kb_usage_stats", {})

            # Restore agent load and last seen
            self._agent_load = data.get("agent_load", {})
            self._agent_last_seen = data.get("agent_last_seen", {})

            return True

        except Exception as e:
            print(f"Error loading registry from disk: {str(e)}")
            return False

    def export_to_json(self, file_path: Optional[str] = None) -> str:
        """Export registry to JSON string or file."""
        data = {
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "registry_stats": self.get_registry_stats(),
            "agents": {
                agent_id: agent.to_dict()
                for agent_id, agent in self._agents.items()
            }
        }

        json_str = json.dumps(data, indent=2)

        if file_path:
            with open(file_path, 'w') as f:
                f.write(json_str)

        return json_str

    def import_from_json(
        self,
        json_data: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> bool:
        """Import registry from JSON string or file."""
        try:
            if file_path:
                with open(file_path, 'r') as f:
                    data = json.load(f)
            elif json_data:
                data = json.loads(json_data)
            else:
                return False

            # Clear existing registry
            self.clear_registry(confirm=True)

            # Register all imported agents
            for agent_id, agent_dict in data.get("agents", {}).items():
                agent = AgentCapability.from_dict(agent_dict)
                self.register_agent(agent)

            return True

        except Exception as e:
            print(f"Error importing registry: {str(e)}")
            return False

    # ============================================================================
    # Utility Methods
    # ============================================================================

    def clear_registry(self, confirm: bool = False):
        """Clear all agents from registry."""
        if not confirm:
            raise ValueError("Must set confirm=True to clear registry")

        self._agents.clear()
        self._agent_name_to_id.clear()
        self._capability_index.clear()
        self._language_index.clear()
        self._framework_index.clear()
        self._type_index.clear()
        self._modality_index.clear()
        self._performance_history.clear()
        self._kb_usage_stats.clear()
        self._agent_load.clear()
        self._agent_last_seen.clear()

    def validate_registry_consistency(self) -> Dict[str, List[str]]:
        """Validate registry internal consistency."""
        issues = {
            "missing_agents": [],
            "orphaned_indexes": [],
            "name_conflicts": [],
            "performance_orphans": []
        }

        # Check all agents in indexes exist in main storage
        all_indexed_ids = set()

        for agent_ids in self._capability_index.values():
            all_indexed_ids.update(agent_ids)
        for agent_ids in self._language_index.values():
            all_indexed_ids.update(agent_ids)
        for agent_ids in self._framework_index.values():
            all_indexed_ids.update(agent_ids)
        for agent_ids in self._type_index.values():
            all_indexed_ids.update(agent_ids)
        for agent_ids in self._modality_index.values():
            all_indexed_ids.update(agent_ids)

        for agent_id in all_indexed_ids:
            if agent_id not in self._agents:
                issues["orphaned_indexes"].append(agent_id)

        # Check name index consistency
        name_to_agents = {}
        for name, agent_id in self._agent_name_to_id.items():
            if agent_id not in self._agents:
                issues["missing_agents"].append(f"Name '{name}' points to missing agent {agent_id}")

            if name in name_to_agents:
                issues["name_conflicts"].append(f"Duplicate name: {name}")
            name_to_agents[name] = agent_id

        # Check for orphaned performance tracking
        for agent_id in self._performance_history:
            if agent_id not in self._agents:
                issues["performance_orphans"].append(agent_id)

        return issues

    def __len__(self) -> int:
        """Return number of registered agents."""
        return len(self._agents)

    def __contains__(self, agent_id: str) -> bool:
        """Check if agent is registered."""
        return agent_id in self._agents

    def __str__(self) -> str:
        """String representation."""
        return f"AgentRegistryService(agents={len(self._agents)}, capabilities={len(self._capability_index)})"

    def __repr__(self) -> str:
        """Detailed representation."""
        return self.__str__()


# ============================================================================
# Factory Function
# ============================================================================

def create_agent_registry(
    persistence_path: Optional[str] = None,
    enable_persistence: bool = True
) -> AgentRegistryService:
    """
    Factory function to create Agent Registry Service.

    Args:
        persistence_path: Path to save registry data
        enable_persistence: Enable saving/loading from disk

    Returns:
        Configured AgentRegistryService instance
    """
    return AgentRegistryService(
        persistence_path=persistence_path,
        enable_persistence=enable_persistence
    )
