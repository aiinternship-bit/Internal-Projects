"""
agents/orchestration/dynamic_orchestrator/agent_selector.py

Agent Selection Engine - Matches task requirements to optimal agents.

This engine uses the Agent Registry Service to:
- Find agents with required capabilities
- Score agents based on multiple factors (capability match, performance, availability, cost)
- Handle multi-agent assignments for complex tasks
- Optimize for parallel execution
- Consider KB access requirements
"""

from typing import Dict, List, Set, Optional, Any, Tuple
from datetime import datetime

from shared.services.agent_registry import AgentRegistryService
from shared.models.agent_capability import (
    AgentCapability,
    AgentType,
    InputModality,
    KBQueryStrategy
)
from shared.models.task_requirements import TaskRequirements, TaskComplexity


class AgentSelector:
    """
    Agent Selection Engine for dynamic orchestration.

    Uses comprehensive scoring to select optimal agents for tasks.
    Supports multi-agent assignments and parallel execution optimization.
    """

    def __init__(
        self,
        agent_registry: AgentRegistryService,
        scoring_weights: Optional[Dict[str, float]] = None,
        max_agents_per_task: int = 5,
        availability_threshold: float = 0.7
    ):
        """
        Initialize Agent Selector.

        Args:
            agent_registry: Agent Registry Service instance
            scoring_weights: Custom weights for scoring factors
            max_agents_per_task: Max number of agents to assign to one task
            availability_threshold: Minimum availability score to consider agent
        """
        self.agent_registry = agent_registry
        self.max_agents_per_task = max_agents_per_task
        self.availability_threshold = availability_threshold

        # Default scoring weights
        self.scoring_weights = scoring_weights or {
            "capability_match": 0.40,  # 40% - Most important
            "performance": 0.30,        # 30% - Success rate, speed
            "availability": 0.20,       # 20% - Current load
            "cost": 0.10               # 10% - Cost efficiency
        }

        # Selection history
        self.selection_history: List[Dict[str, Any]] = []

    def select_agents(
        self,
        task_requirements: TaskRequirements,
        allow_multiple: bool = True,
        prefer_specialists: bool = True
    ) -> List[AgentCapability]:
        """
        Select optimal agents for a task based on requirements.

        Args:
            task_requirements: Task requirements extracted by TaskAnalyzer
            allow_multiple: Allow multiple agents if needed
            prefer_specialists: Prefer specialized agents over generalists

        Returns:
            List of selected agents (ordered by score)
        """
        # Step 1: Find candidate agents using registry search
        candidates = self._find_candidates(task_requirements)

        if not candidates:
            print(f"No agents found for capabilities: {task_requirements.required_capabilities}")
            return []

        # Step 2: Score all candidates
        scored_agents = self._score_candidates(
            candidates=candidates,
            task_requirements=task_requirements,
            prefer_specialists=prefer_specialists
        )

        # Step 3: Filter by availability
        available_agents = [
            (agent, score) for agent, score in scored_agents
            if self._check_availability(agent)
        ]

        if not available_agents:
            print("No agents available (all overloaded)")
            # Fall back to all candidates, sorted by score
            available_agents = scored_agents

        # Step 4: Select top agents
        if allow_multiple and task_requirements.estimated_complexity in [
            TaskComplexity.HIGH, TaskComplexity.VERY_HIGH
        ]:
            # For complex tasks, select multiple agents
            num_agents = min(
                self.max_agents_per_task,
                max(2, len(task_requirements.required_capabilities) // 3)
            )
            selected = [agent for agent, _ in available_agents[:num_agents]]
        else:
            # For simpler tasks, select single best agent
            selected = [available_agents[0][0]] if available_agents else []

        # Step 5: Record selection
        self._record_selection(task_requirements, selected, scored_agents)

        return selected

    def _find_candidates(self, task_requirements: TaskRequirements) -> List[AgentCapability]:
        """
        Find candidate agents using registry search.
        """
        # Use registry's search_by_capability with all filters
        candidates = self.agent_registry.search_by_capability(
            required_capabilities=task_requirements.required_capabilities,
            optional_capabilities=task_requirements.optional_capabilities,
            language=task_requirements.required_languages[0] if task_requirements.required_languages else None,
            framework=task_requirements.required_frameworks[0] if task_requirements.required_frameworks else None
        )

        # Additional filtering for input modalities
        if task_requirements.requires_multimodal_processing():
            candidates = [
                agent for agent in candidates
                if any(modality in agent.input_modalities for modality in task_requirements.input_modalities)
            ]

        return candidates

    def _score_candidates(
        self,
        candidates: List[AgentCapability],
        task_requirements: TaskRequirements,
        prefer_specialists: bool
    ) -> List[Tuple[AgentCapability, float]]:
        """
        Score all candidate agents using multi-factor scoring.

        Returns:
            List of (agent, score) tuples sorted by score descending
        """
        scored = []

        for agent in candidates:
            # Calculate component scores
            capability_score = self._calculate_capability_score(
                agent=agent,
                task_requirements=task_requirements,
                prefer_specialists=prefer_specialists
            )

            performance_score = self._calculate_performance_score(agent)

            availability_score = self._calculate_availability_score(agent)

            cost_score = self._calculate_cost_score(agent, task_requirements)

            # Weighted combination
            total_score = (
                capability_score * self.scoring_weights["capability_match"] +
                performance_score * self.scoring_weights["performance"] +
                availability_score * self.scoring_weights["availability"] +
                cost_score * self.scoring_weights["cost"]
            )

            scored.append((agent, total_score))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        return scored

    def _calculate_capability_score(
        self,
        agent: AgentCapability,
        task_requirements: TaskRequirements,
        prefer_specialists: bool
    ) -> float:
        """
        Calculate capability match score (0.0 - 1.0).

        Factors:
        - Required capabilities coverage
        - Optional capabilities coverage
        - Language/framework match
        - Specialist vs generalist preference
        """
        # Use agent's built-in match score calculation
        base_score = agent.calculate_match_score(
            required_capabilities=task_requirements.required_capabilities,
            optional_capabilities=task_requirements.optional_capabilities,
            language=task_requirements.required_languages[0] if task_requirements.required_languages else None,
            framework=task_requirements.required_frameworks[0] if task_requirements.required_frameworks else None
        )

        # Adjust for specialist preference
        if prefer_specialists:
            # Penalize generalists (agents with too many capabilities)
            if len(agent.capabilities) > 10:
                base_score *= 0.9  # 10% penalty

        # Bonus for exact modality match
        if task_requirements.input_modalities:
            modality_overlap = len(
                task_requirements.input_modalities & agent.input_modalities
            )
            modality_bonus = modality_overlap / len(task_requirements.input_modalities) * 0.1
            base_score = min(1.0, base_score + modality_bonus)

        return base_score

    def _calculate_performance_score(self, agent: AgentCapability) -> float:
        """
        Calculate performance score (0.0 - 1.0).

        Factors:
        - Success rate
        - Average task duration
        - Retry rate
        """
        metrics = agent.performance_metrics

        # Success rate (0-1)
        success_score = metrics.success_rate

        # Speed score (inverse of normalized duration)
        # Assume 30 min is baseline, penalize slower agents
        duration_score = max(0.0, 1.0 - (metrics.avg_task_duration_minutes / 30.0))

        # Retry penalty
        retry_penalty = metrics.retry_rate * 0.2  # Up to 20% penalty

        performance_score = (success_score * 0.6 + duration_score * 0.4) - retry_penalty

        return max(0.0, min(1.0, performance_score))

    def _calculate_availability_score(self, agent: AgentCapability) -> float:
        """
        Calculate availability score (0.0 - 1.0).

        Factors:
        - Current load vs max capacity
        - Recent activity
        """
        # Get current load from registry
        current_load = self.agent_registry.get_agent_load(agent.agent_id)
        max_capacity = agent.max_concurrent_tasks

        if max_capacity == 0:
            return 0.0

        # Load factor (inverse - lower load is better)
        load_factor = 1.0 - (current_load / max_capacity)

        return max(0.0, min(1.0, load_factor))

    def _calculate_cost_score(
        self,
        agent: AgentCapability,
        task_requirements: TaskRequirements
    ) -> float:
        """
        Calculate cost efficiency score (0.0 - 1.0).

        Factors:
        - Cost per task
        - Estimated KB query costs
        """
        # Get cost metrics
        cost_metrics = agent.cost_metrics

        # Estimate total cost for this task
        estimated_cost = (
            cost_metrics.avg_cost_per_task_usd +
            (task_requirements.expected_kb_queries * cost_metrics.kb_query_cost_usd)
        )

        # Normalize cost (assume $1.00 is expensive, $0.01 is cheap)
        # Lower cost = higher score
        cost_score = max(0.0, 1.0 - (estimated_cost / 1.0))

        return cost_score

    def _check_availability(self, agent: AgentCapability) -> bool:
        """
        Check if agent is available (not overloaded).
        """
        availability_score = self._calculate_availability_score(agent)
        return availability_score >= self.availability_threshold

    def _record_selection(
        self,
        task_requirements: TaskRequirements,
        selected_agents: List[AgentCapability],
        all_scored: List[Tuple[AgentCapability, float]]
    ) -> None:
        """
        Record selection for analytics.
        """
        self.selection_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": task_requirements.task_id,
            "required_capabilities": list(task_requirements.required_capabilities),
            "selected_agents": [agent.agent_id for agent in selected_agents],
            "top_scores": [
                {"agent_id": agent.agent_id, "score": score}
                for agent, score in all_scored[:5]
            ]
        })

    def recommend_with_explanation(
        self,
        task_requirements: TaskRequirements
    ) -> Dict[str, Any]:
        """
        Select agents and provide detailed explanation of choices.

        Returns:
            {
                "selected_agents": List[AgentCapability],
                "explanations": List[str],
                "alternatives": List[Dict],
                "confidence": float
            }
        """
        # Find candidates and score them
        candidates = self._find_candidates(task_requirements)
        scored = self._score_candidates(candidates, task_requirements, prefer_specialists=True)

        if not scored:
            return {
                "selected_agents": [],
                "explanations": ["No agents found with required capabilities"],
                "alternatives": [],
                "confidence": 0.0
            }

        # Select top agent(s)
        selected = [scored[0][0]]  # Top agent
        top_score = scored[0][1]

        # Build explanations
        explanations = []
        agent = selected[0]

        explanations.append(
            f"Selected {agent.agent_name} (score: {top_score:.2f})"
        )

        # Capability match
        cap_match = len(task_requirements.required_capabilities & agent.capabilities)
        explanations.append(
            f"Matches {cap_match}/{len(task_requirements.required_capabilities)} required capabilities"
        )

        # Performance
        explanations.append(
            f"Success rate: {agent.performance_metrics.success_rate:.1%}, "
            f"Avg duration: {agent.performance_metrics.avg_task_duration_minutes:.1f} min"
        )

        # Availability
        load = self.agent_registry.get_agent_load(agent.agent_id)
        explanations.append(
            f"Current load: {load}/{agent.max_concurrent_tasks} tasks"
        )

        # Alternatives
        alternatives = []
        for alt_agent, alt_score in scored[1:4]:  # Next 3 agents
            alternatives.append({
                "agent_id": alt_agent.agent_id,
                "agent_name": alt_agent.agent_name,
                "score": alt_score,
                "reason": f"Alternative with score {alt_score:.2f}"
            })

        # Confidence (based on score gap)
        if len(scored) > 1:
            score_gap = top_score - scored[1][1]
            confidence = min(1.0, 0.5 + score_gap)  # Higher gap = more confidence
        else:
            confidence = top_score  # Only one option

        return {
            "selected_agents": selected,
            "explanations": explanations,
            "alternatives": alternatives,
            "confidence": confidence
        }

    def batch_select(
        self,
        tasks: List[TaskRequirements],
        optimize_for_parallelism: bool = True
    ) -> Dict[str, List[AgentCapability]]:
        """
        Select agents for multiple tasks, optimizing for parallel execution.

        Args:
            tasks: List of task requirements
            optimize_for_parallelism: Try to assign different agents to parallel tasks

        Returns:
            {task_id: [selected_agents]}
        """
        assignments = {}
        agent_load_tracker = {}  # Track temporary load during batch assignment

        # Sort tasks by complexity (assign complex tasks first)
        sorted_tasks = sorted(
            tasks,
            key=lambda t: t.estimated_complexity.value,
            reverse=True
        )

        for task in sorted_tasks:
            # Get candidates
            candidates = self._find_candidates(task)
            scored = self._score_candidates(candidates, task, prefer_specialists=True)

            if optimize_for_parallelism:
                # Adjust scores based on temporary load
                adjusted_scored = []
                for agent, score in scored:
                    temp_load = agent_load_tracker.get(agent.agent_id, 0)
                    # Penalize agents already assigned in this batch
                    adjusted_score = score * (1.0 - 0.1 * temp_load)
                    adjusted_scored.append((agent, adjusted_score))

                adjusted_scored.sort(key=lambda x: x[1], reverse=True)
                selected = [adjusted_scored[0][0]] if adjusted_scored else []
            else:
                selected = [scored[0][0]] if scored else []

            assignments[task.task_id] = selected

            # Update temporary load
            for agent in selected:
                agent_load_tracker[agent.agent_id] = agent_load_tracker.get(agent.agent_id, 0) + 1

        return assignments

    def get_selection_stats(self) -> Dict[str, Any]:
        """
        Get selection statistics.
        """
        if not self.selection_history:
            return {"total_selections": 0}

        # Most frequently selected agents
        agent_counts = {}
        for record in self.selection_history:
            for agent_id in record["selected_agents"]:
                agent_counts[agent_id] = agent_counts.get(agent_id, 0) + 1

        most_used = sorted(agent_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_selections": len(self.selection_history),
            "unique_agents_used": len(agent_counts),
            "most_frequently_selected": [
                {"agent_id": aid, "count": count} for aid, count in most_used
            ],
            "avg_agents_per_task": sum(
                len(r["selected_agents"]) for r in self.selection_history
            ) / len(self.selection_history)
        }


# Tool functions for standalone usage
def select_agents_for_task(
    task_requirements_dict: Dict[str, Any],
    agent_registry_path: str = "./agent_registry.json",
    allow_multiple: bool = True
) -> List[Dict[str, Any]]:
    """
    Tool function: Select agents for a task.

    Args:
        task_requirements_dict: Task requirements as dict
        agent_registry_path: Path to agent registry file
        allow_multiple: Allow multiple agent assignments

    Returns:
        List of selected agent dictionaries
    """
    # Load registry
    registry = AgentRegistryService(
        persistence_path=agent_registry_path,
        enable_persistence=True
    )

    # Create selector
    selector = AgentSelector(agent_registry=registry)

    # Reconstruct TaskRequirements from dict
    task_requirements = TaskRequirements.from_dict(task_requirements_dict)

    # Select agents
    selected = selector.select_agents(
        task_requirements=task_requirements,
        allow_multiple=allow_multiple
    )

    return [agent.to_dict() for agent in selected]


def recommend_agents_with_explanation(
    task_requirements_dict: Dict[str, Any],
    agent_registry_path: str = "./agent_registry.json"
) -> Dict[str, Any]:
    """
    Tool function: Get agent recommendations with explanations.
    """
    registry = AgentRegistryService(
        persistence_path=agent_registry_path,
        enable_persistence=True
    )

    selector = AgentSelector(agent_registry=registry)
    task_requirements = TaskRequirements.from_dict(task_requirements_dict)

    result = selector.recommend_with_explanation(task_requirements)

    # Convert agents to dicts
    result["selected_agents"] = [agent.to_dict() for agent in result["selected_agents"]]

    return result
