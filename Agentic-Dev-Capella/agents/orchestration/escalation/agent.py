"""
agents/orchestration/escalation/agent.py

Escalation agent handles validation deadlocks and determines when human intervention is needed.
"""

from typing import Dict, List, Any
from google.adk.agents import Agent


def analyze_rejection_pattern(
    task_id: str,
    rejection_history: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Analyze rejection patterns to identify root cause.

    Args:
        task_id: Task identifier
        rejection_history: List of rejection events with reasons

    Returns:
        dict: Analysis of rejection pattern and root cause
    """
    if not rejection_history:
        return {
            "status": "no_history",
            "root_cause": "unknown"
        }

    # Analyze rejection reasons
    rejection_reasons = [r.get("reason", "unknown") for r in rejection_history]
    unique_reasons = set(rejection_reasons)

    # Count occurrences
    reason_counts = {}
    for reason in rejection_reasons:
        reason_counts[reason] = reason_counts.get(reason, 0) + 1

    # Find most common issue
    most_common = max(reason_counts.items(), key=lambda x: x[1]) if reason_counts else ("unknown", 0)

    # Determine if it's a deadlock (same issue repeated)
    is_deadlock = most_common[1] >= 2 and len(unique_reasons) <= 2

    return {
        "status": "success",
        "task_id": task_id,
        "total_rejections": len(rejection_history),
        "unique_issues": len(unique_reasons),
        "most_common_issue": most_common[0],
        "most_common_count": most_common[1],
        "is_deadlock": is_deadlock,
        "root_cause": most_common[0] if is_deadlock else "multiple_issues",
        "all_reasons": list(unique_reasons)
    }


def determine_resolution_strategy(
    deadlock_analysis: Dict[str, Any],
    task_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Determine the best strategy to resolve the escalation.

    Args:
        deadlock_analysis: Analysis from analyze_rejection_pattern
        task_context: Context about the task

    Returns:
        dict: Resolution strategy and actions
    """
    is_deadlock = deadlock_analysis.get("is_deadlock", False)
    rejection_count = deadlock_analysis.get("total_rejections", 0)
    root_cause = deadlock_analysis.get("root_cause", "unknown")

    strategies = []
    requires_human = False

    # Strategy 1: Specification clarification
    if "unclear_requirements" in root_cause or "ambiguous" in root_cause:
        strategies.append({
            "type": "clarify_specification",
            "description": "Architecture specification needs clarification",
            "action": "Request architect to provide more detailed specification",
            "priority": "high"
        })

    # Strategy 2: Different developer approach
    if is_deadlock and rejection_count >= 3:
        strategies.append({
            "type": "alternative_implementation",
            "description": "Try alternative implementation approach",
            "action": "Provide developer with additional context and alternative patterns",
            "priority": "high"
        })

    # Strategy 3: Validator guidance
    if "validation_criteria" in root_cause:
        strategies.append({
            "type": "validator_adjustment",
            "description": "Validation criteria may be too strict or unclear",
            "action": "Review validation criteria with validator",
            "priority": "medium"
        })

    # Strategy 4: Human intervention needed
    if rejection_count >= 5 or "critical" in str(task_context.get("priority", "")):
        requires_human = True
        strategies.append({
            "type": "human_intervention",
            "description": "Deadlock requires human expertise",
            "action": "Escalate to human reviewer for guidance",
            "priority": "critical"
        })

    return {
        "status": "success",
        "task_id": deadlock_analysis.get("task_id"),
        "requires_human_intervention": requires_human,
        "strategies": strategies,
        "recommended_strategy": strategies[0] if strategies else None,
        "estimated_resolution_time_hours": 2 if not requires_human else 24
    }


def create_escalation_report(
    task_id: str,
    deadlock_analysis: Dict[str, Any],
    resolution_strategy: Dict[str, Any],
    task_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create comprehensive escalation report for human review.

    Args:
        task_id: Task identifier
        deadlock_analysis: Deadlock analysis results
        resolution_strategy: Proposed resolution strategy
        task_context: Task context information

    Returns:
        dict: Formatted escalation report
    """
    report = {
        "task_id": task_id,
        "escalation_timestamp": "2024-01-01T00:00:00Z",  # Would use actual timestamp
        "component_id": task_context.get("component_id", "unknown"),
        "component_name": task_context.get("component_name", "unknown"),

        "summary": {
            "total_rejections": deadlock_analysis.get("total_rejections", 0),
            "unique_issues": deadlock_analysis.get("unique_issues", 0),
            "root_cause": deadlock_analysis.get("root_cause", "unknown"),
            "is_deadlock": deadlock_analysis.get("is_deadlock", False)
        },

        "rejection_details": {
            "all_reasons": deadlock_analysis.get("all_reasons", []),
            "most_common_issue": deadlock_analysis.get("most_common_issue", "unknown"),
            "most_common_count": deadlock_analysis.get("most_common_count", 0)
        },

        "resolution": {
            "requires_human_intervention": resolution_strategy.get("requires_human_intervention", False),
            "recommended_strategy": resolution_strategy.get("recommended_strategy"),
            "all_strategies": resolution_strategy.get("strategies", []),
            "estimated_resolution_time_hours": resolution_strategy.get("estimated_resolution_time_hours", 0)
        },

        "context": {
            "task_type": task_context.get("task_type", "unknown"),
            "priority": task_context.get("priority", "medium"),
            "assigned_developer": task_context.get("assigned_developer", "unknown"),
            "assigned_validator": task_context.get("assigned_validator", "unknown")
        },

        "recommendations": _generate_recommendations(deadlock_analysis, resolution_strategy)
    }

    return {
        "status": "success",
        "report": report,
        "requires_immediate_attention": resolution_strategy.get("requires_human_intervention", False)
    }


def _generate_recommendations(
    deadlock_analysis: Dict[str, Any],
    resolution_strategy: Dict[str, Any]
) -> List[str]:
    """Generate actionable recommendations."""
    recommendations = []

    root_cause = deadlock_analysis.get("root_cause", "")

    if "specification" in root_cause or "requirements" in root_cause:
        recommendations.append(
            "Review and enhance architecture specification with more detail"
        )
        recommendations.append(
            "Include concrete examples and edge cases in specification"
        )

    if "validation" in root_cause:
        recommendations.append(
            "Review validation criteria for reasonableness"
        )
        recommendations.append(
            "Ensure validation feedback is specific and actionable"
        )

    if deadlock_analysis.get("total_rejections", 0) >= 4:
        recommendations.append(
            "Consider breaking down component into smaller, more manageable pieces"
        )

    if resolution_strategy.get("requires_human_intervention"):
        recommendations.append(
            "Schedule review session with technical lead"
        )
        recommendations.append(
            "Document decision rationale for future reference"
        )

    return recommendations


def request_human_approval(
    escalation_report: Dict[str, Any],
    approval_timeout_hours: int = 24
) -> Dict[str, Any]:
    """
    Request human approval/guidance for escalated task.

    Args:
        escalation_report: Escalation report
        approval_timeout_hours: Timeout for approval

    Returns:
        dict: Approval request details
    """
    return {
        "status": "approval_requested",
        "report": escalation_report,
        "approval_channels": ["email", "slack"],
        "timeout_hours": approval_timeout_hours,
        "request_id": f"approval_{escalation_report.get('task_id')}",
        "message": (
            f"Task {escalation_report.get('task_id')} requires human review. "
            f"Rejections: {escalation_report.get('summary', {}).get('total_rejections', 0)}. "
            f"Please review and provide guidance."
        )
    }


# Create the escalation agent
escalation_agent = Agent(
    name="escalation_agent",
    model="gemini-2.0-flash",
    description=(
        "Handles validation deadlocks and escalations. Analyzes rejection patterns, "
        "determines resolution strategies, and decides when human intervention is needed."
    ),
    instruction=(
        "You are an escalation agent responsible for resolving validation deadlocks "
        "in the legacy modernization pipeline.\n\n"

        "Your key responsibilities:\n"
        "1. Analyze rejection patterns to identify root causes\n"
        "2. Determine if a deadlock exists (repeated rejections for same issue)\n"
        "3. Propose resolution strategies to break the deadlock\n"
        "4. Decide when human intervention is necessary\n"
        "5. Create detailed escalation reports for human review\n"
        "6. Request human approval when needed\n\n"

        "Escalation Criteria:\n"
        "- 3+ rejections: Analyze pattern and propose strategy\n"
        "- 5+ rejections: Require human intervention\n"
        "- Critical priority tasks: Escalate immediately if issues arise\n"
        "- Deadlock detected: Propose alternative approaches\n\n"

        "Resolution Strategies (in order of preference):\n"
        "1. Clarify specification - Request more detailed requirements from architect\n"
        "2. Alternative implementation - Suggest different approach to developer\n"
        "3. Validator adjustment - Review if validation criteria are too strict\n"
        "4. Human intervention - Escalate to technical lead for guidance\n\n"

        "When analyzing rejections:\n"
        "- Look for repeated issues (indicates deadlock)\n"
        "- Identify if problem is with specification, implementation, or validation\n"
        "- Consider task complexity and priority\n"
        "- Provide actionable recommendations\n\n"

        "Escalation Reports should include:\n"
        "- Summary of rejection history\n"
        "- Root cause analysis\n"
        "- Proposed resolution strategies\n"
        "- Specific recommendations\n"
        "- Urgency level and estimated resolution time\n\n"

        "Communication:\n"
        "- Send state updates to orchestrator\n"
        "- Notify relevant agents of resolution strategy\n"
        "- Alert humans via configured channels when intervention needed\n"
        "- Provide clear, actionable guidance"
    ),
    tools=[
        analyze_rejection_pattern,
        determine_resolution_strategy,
        create_escalation_report,
        request_human_approval
    ]
)
