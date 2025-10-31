"""
agents/orchestration/escalation/agent.py

Escalation agent handles validation deadlocks using LLM analysis to determine resolution strategies.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re

from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration


class EscalationAgent(A2AEnabledAgent):
    """
    Escalation Agent for handling validation deadlocks and failures.

    Capabilities:
    - Analyze rejection patterns using LLM
    - Identify root causes of repeated failures
    - Determine resolution strategies
    - Create escalation reports
    - Decide when human intervention is needed
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize Escalation Agent."""
        A2AEnabledAgent.__init__(self, context, message_bus)

        self.context = context
        self.orchestrator_id = orchestrator_id
        self.model_name = model_name

        # Initialize A2A integration
        self.a2a = A2AIntegration(
            agent_context=context,
            message_bus=message_bus,
            orchestrator_id=orchestrator_id
        )

        # Initialize Vertex AI
        aiplatform.init(
            project=context.get("project_id") if hasattr(context, 'get') else getattr(context, 'project_id', None),
            location=context.get("location", "us-central1") if hasattr(context, 'get') else getattr(context, 'location', "us-central1")
        )

        self.model = GenerativeModel(model_name)

        # Escalation history
        self.escalation_history: List[Dict[str, Any]] = []

    def handle_task_assignment(self, message: Dict[str, Any]) -> None:
        """Handle TASK_ASSIGNMENT message from orchestrator."""
        payload = message.get("payload", {})
        task_id = payload.get("task_id")
        task_type = payload.get("task_type")
        parameters = payload.get("parameters", {})

        try:
            if task_type == "analyze_escalation":
                result = self.analyze_and_escalate(task_id=task_id, **parameters)
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            # Send completion
            self.a2a.send_completion(
                task_id=task_id,
                artifacts=result,
                metrics={}
            )

        except Exception as e:
            self.a2a.send_error_report(
                task_id=task_id,
                error_type="ESCALATION_ANALYSIS_FAILED",
                error_message=str(e),
                stack_trace=""
            )

    def analyze_and_escalate(
        self,
        rejection_history: List[Dict[str, Any]],
        task_context: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Complete escalation analysis and resolution."""
        print(f"[Escalation] Analyzing escalation for task {task_id}")

        # Analyze rejection pattern
        deadlock_analysis = self.analyze_rejection_pattern(task_id, rejection_history)

        # Determine resolution strategy
        resolution_strategy = self.determine_resolution_strategy(
            deadlock_analysis, task_context
        )

        # Create escalation report
        report = self.create_escalation_report(
            task_id, deadlock_analysis, resolution_strategy, task_context
        )

        return report

    def analyze_rejection_pattern(
        self,
        task_id: str,
        rejection_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze rejection patterns using LLM to identify root cause.

        Args:
            task_id: Task identifier
            rejection_history: List of rejection events with reasons

        Returns:
            dict: LLM analysis of rejection pattern and root cause
        """
        print(f"[Escalation] Analyzing {len(rejection_history)} rejections")

        if not rejection_history:
            return {
                "status": "no_history",
                "task_id": task_id,
                "total_rejections": 0,
                "root_cause": "No rejection history available"
            }

        # Build prompt for LLM analysis
        prompt = self._build_rejection_analysis_prompt(task_id, rejection_history)

        # Get LLM analysis
        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.3)
        )

        # Parse response
        analysis = self._parse_rejection_analysis(response.text, rejection_history)

        analysis["status"] = "success"
        analysis["task_id"] = task_id

        return analysis

    def determine_resolution_strategy(
        self,
        deadlock_analysis: Dict[str, Any],
        task_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine resolution strategy using LLM.

        Args:
            deadlock_analysis: Analysis from analyze_rejection_pattern
            task_context: Context about the task

        Returns:
            dict: LLM-determined resolution strategy and actions
        """
        print(f"[Escalation] Determining resolution strategy")

        prompt = self._build_resolution_strategy_prompt(deadlock_analysis, task_context)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.4)
        )

        strategy = self._parse_resolution_strategy(response.text, deadlock_analysis)

        strategy["task_id"] = deadlock_analysis.get("task_id")
        strategy["status"] = "success"

        return strategy

    def create_escalation_report(
        self,
        task_id: str,
        deadlock_analysis: Dict[str, Any],
        resolution_strategy: Dict[str, Any],
        task_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create comprehensive escalation report using LLM.

        Args:
            task_id: Task identifier
            deadlock_analysis: Deadlock analysis results
            resolution_strategy: Proposed resolution strategy
            task_context: Task context information

        Returns:
            dict: Formatted escalation report
        """
        print(f"[Escalation] Creating escalation report")

        prompt = self._build_report_prompt(
            task_id, deadlock_analysis, resolution_strategy, task_context
        )

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.3)
        )

        report_content = self._parse_report(response.text)

        report = {
            "task_id": task_id,
            "escalation_timestamp": datetime.utcnow().isoformat(),
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

            "recommendations": report_content.get("recommendations", []),
            "detailed_analysis": report_content.get("analysis", ""),
            "next_steps": report_content.get("next_steps", [])
        }

        return {
            "status": "success",
            "report": report,
            "requires_immediate_attention": resolution_strategy.get("requires_human_intervention", False)
        }

    def request_human_approval(
        self,
        escalation_report: Dict[str, Any],
        approval_timeout_hours: int = 24
    ) -> Dict[str, Any]:
        """Request human approval/guidance."""
        task_id = escalation_report.get("task_id", "unknown")

        return {
            "status": "approval_requested",
            "report": escalation_report,
            "approval_channels": ["email", "slack"],
            "timeout_hours": approval_timeout_hours,
            "request_id": f"approval_{task_id}",
            "message": (
                f"Task {task_id} requires human review. "
                f"Rejections: {escalation_report.get('summary', {}).get('total_rejections', 0)}. "
                f"Please review and provide guidance."
            )
        }

    # ========================================================================
    # PROMPT BUILDERS
    # ========================================================================

    def _build_rejection_analysis_prompt(
        self,
        task_id: str,
        rejection_history: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for analyzing rejection patterns."""

        history_text = "\n".join([
            f"{i+1}. {r.get('reason', 'No reason provided')} "
            f"(Feedback: {r.get('feedback', 'None')})"
            for i, r in enumerate(rejection_history)
        ])

        prompt = f"""You are an expert at analyzing software development failures and identifying root causes.

Analyze the following rejection history for task: **{task_id}**

**Rejection History ({len(rejection_history)} rejections):**
{history_text}

**Your Analysis Should Determine:**

1. **Root Cause**: What is the fundamental issue causing these rejections?
   - Is it unclear requirements?
   - Implementation approach problems?
   - Validation criteria issues?
   - Technical constraints?
   - Communication gaps?

2. **Is This a Deadlock?**: Are the same issues repeating without progress?
   - Look for identical or very similar rejection reasons
   - Identify if feedback is being incorporated

3. **Pattern Recognition**: Are there trends in the rejections?
   - Early rejections vs later rejections
   - Severity increasing or decreasing?
   - New issues appearing or same issues?

**Response Format:**

**Root Cause:** [Single sentence describing the fundamental issue]

**Is Deadlock:** [true/false]

**Most Common Issue:** [The most frequent problem]

**Unique Issues Count:** [Number of different issues]

**Pattern Analysis:** [2-3 sentences describing the pattern]

**Detailed Findings:**
- Finding 1
- Finding 2
- Finding 3

Be specific and actionable in your analysis.
"""

        return prompt

    def _build_resolution_strategy_prompt(
        self,
        deadlock_analysis: Dict[str, Any],
        task_context: Dict[str, Any]
    ) -> str:
        """Build prompt for determining resolution strategy."""

        analysis_text = json.dumps(deadlock_analysis, indent=2)
        context_text = json.dumps(task_context, indent=2)

        prompt = f"""You are an expert project manager and technical lead.

Determine the best strategy to resolve this escalation:

**Deadlock Analysis:**
{analysis_text}

**Task Context:**
{context_text}

**Available Resolution Strategies:**

1. **Clarify Specification**
   - When: Requirements are unclear or ambiguous
   - Action: Request architect to provide more detail
   - Time: 2-4 hours

2. **Alternative Implementation**
   - When: Current approach isn't working
   - Action: Suggest different technical approach
   - Time: 4-8 hours

3. **Validator Adjustment**
   - When: Validation criteria may be too strict
   - Action: Review and adjust validation rules
   - Time: 1-2 hours

4. **Break Down Component**
   - When: Component is too complex
   - Action: Split into smaller pieces
   - Time: 8-16 hours

5. **Human Intervention**
   - When: Automated resolution unlikely to work
   - Action: Escalate to technical lead
   - Time: 24+ hours

**Consider:**
- Number of rejections ({deadlock_analysis.get('total_rejections', 0)})
- Is deadlock detected? ({deadlock_analysis.get('is_deadlock', False)})
- Task priority: {task_context.get('priority', 'medium')}
- Root cause: {deadlock_analysis.get('root_cause', 'unknown')}

**Response Format:**

**Requires Human Intervention:** [true/false]

**Recommended Strategy:** [Strategy name and brief reasoning]

**All Applicable Strategies:**
1. [Strategy name]: [Why it might work]
2. [Strategy name]: [Why it might work]

**Estimated Resolution Time:** [Hours]

**Justification:** [2-3 sentences explaining the recommendation]

Be pragmatic - choose strategies likely to succeed quickly.
"""

        return prompt

    def _build_report_prompt(
        self,
        task_id: str,
        deadlock_analysis: Dict[str, Any],
        resolution_strategy: Dict[str, Any],
        task_context: Dict[str, Any]
    ) -> str:
        """Build prompt for creating escalation report."""

        prompt = f"""You are writing an escalation report for technical leadership.

Create a clear, actionable report for the following escalation:

**Task ID:** {task_id}
**Component:** {task_context.get('component_name', 'Unknown')}
**Total Rejections:** {deadlock_analysis.get('total_rejections', 0)}
**Root Cause:** {deadlock_analysis.get('root_cause', 'Unknown')}

**Resolution Strategy:**
{json.dumps(resolution_strategy, indent=2)}

**Response Format:**

**Detailed Analysis:**
[2-3 paragraphs explaining:
- What went wrong
- Why it happened
- Impact on the project
- Lessons learned]

**Recommendations:**
1. [Immediate action 1]
2. [Immediate action 2]
3. [Long-term improvement 1]

**Next Steps:**
1. [Specific action with owner]
2. [Specific action with timeline]
3. [Specific action with expected outcome]

Make the report professional, clear, and actionable.
"""

        return prompt

    # ========================================================================
    # RESPONSE PARSERS
    # ========================================================================

    def _parse_rejection_analysis(
        self,
        response_text: str,
        rejection_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Parse LLM response for rejection analysis."""

        # Extract root cause
        root_cause = "Unknown"
        root_match = re.search(r"Root Cause:?\s*([^\n]+)", response_text, re.IGNORECASE)
        if root_match:
            root_cause = root_match.group(1).strip()

        # Extract deadlock status
        is_deadlock = False
        deadlock_match = re.search(r"Is Deadlock:?\s*(true|false)", response_text, re.IGNORECASE)
        if deadlock_match:
            is_deadlock = deadlock_match.group(1).lower() == "true"

        # Extract most common issue
        most_common = "Unknown"
        common_match = re.search(r"Most Common Issue:?\s*([^\n]+)", response_text, re.IGNORECASE)
        if common_match:
            most_common = common_match.group(1).strip()

        # Extract unique issues count
        unique_count = len(set(r.get("reason", "") for r in rejection_history))
        count_match = re.search(r"Unique Issues Count:?\s*(\d+)", response_text, re.IGNORECASE)
        if count_match:
            unique_count = int(count_match.group(1))

        # Extract detailed findings
        findings = []
        findings_match = re.search(r"Detailed Findings:?\s*\n(.*?)(?=\n\n|\Z)", response_text, re.DOTALL | re.IGNORECASE)
        if findings_match:
            findings_text = findings_match.group(1)
            for line in findings_text.split("\n"):
                line = line.strip()
                if line.startswith("-") or line.startswith("*"):
                    findings.append(line[1:].strip())

        # Get all rejection reasons
        all_reasons = list(set(r.get("reason", "Unknown") for r in rejection_history))

        # Count most common
        reason_counts = {}
        for r in rejection_history:
            reason = r.get("reason", "Unknown")
            reason_counts[reason] = reason_counts.get(reason, 0) + 1

        most_common_count = max(reason_counts.values()) if reason_counts else 0

        return {
            "total_rejections": len(rejection_history),
            "unique_issues": unique_count,
            "root_cause": root_cause,
            "is_deadlock": is_deadlock,
            "most_common_issue": most_common,
            "most_common_count": most_common_count,
            "all_reasons": all_reasons,
            "detailed_findings": findings
        }

    def _parse_resolution_strategy(
        self,
        response_text: str,
        deadlock_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse LLM response for resolution strategy."""

        # Extract requires human intervention
        requires_human = False
        human_match = re.search(r"Requires Human Intervention:?\s*(true|false)", response_text, re.IGNORECASE)
        if human_match:
            requires_human = human_match.group(1).lower() == "true"

        # Extract recommended strategy
        recommended = "Human Intervention"
        rec_match = re.search(r"Recommended Strategy:?\s*([^\n]+)", response_text, re.IGNORECASE)
        if rec_match:
            recommended = rec_match.group(1).strip()

        # Extract estimated time
        estimated_time = 24 if requires_human else 4
        time_match = re.search(r"Estimated Resolution Time:?\s*(\d+)", response_text, re.IGNORECASE)
        if time_match:
            estimated_time = int(time_match.group(1))

        # Extract all strategies
        strategies = []
        strategies_match = re.search(r"All Applicable Strategies:?\s*\n(.*?)(?=\n\n|\Z)", response_text, re.DOTALL | re.IGNORECASE)
        if strategies_match:
            strategies_text = strategies_match.group(1)
            for line in strategies_text.split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith("-")):
                    # Extract strategy name
                    strategy_match = re.match(r"[\d\-\*]*\s*([^:]+):?\s*(.*)", line)
                    if strategy_match:
                        strategies.append({
                            "type": strategy_match.group(1).strip(),
                            "description": strategy_match.group(2).strip() if strategy_match.group(2) else ""
                        })

        # If no strategies extracted, create default
        if not strategies:
            strategies = [{"type": recommended, "description": "Primary resolution approach"}]

        return {
            "requires_human_intervention": requires_human,
            "recommended_strategy": strategies[0] if strategies else None,
            "strategies": strategies,
            "estimated_resolution_time_hours": estimated_time
        }

    def _parse_report(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response for escalation report."""

        # Extract detailed analysis
        analysis = ""
        analysis_match = re.search(r"Detailed Analysis:?\s*\n(.*?)(?=\n\n\*\*|\Z)", response_text, re.DOTALL | re.IGNORECASE)
        if analysis_match:
            analysis = analysis_match.group(1).strip()

        # Extract recommendations
        recommendations = []
        rec_match = re.search(r"Recommendations:?\s*\n(.*?)(?=\n\n\*\*|\Z)", response_text, re.DOTALL | re.IGNORECASE)
        if rec_match:
            rec_text = rec_match.group(1)
            for line in rec_text.split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith("-")):
                    rec = re.sub(r"^[\d\-\*\.]+\s*", "", line)
                    if rec:
                        recommendations.append(rec)

        # Extract next steps
        next_steps = []
        steps_match = re.search(r"Next Steps:?\s*\n(.*?)(?=\n\n\*\*|\Z)", response_text, re.DOTALL | re.IGNORECASE)
        if steps_match:
            steps_text = steps_match.group(1)
            for line in steps_text.split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith("-")):
                    step = re.sub(r"^[\d\-\*\.]+\s*", "", line)
                    if step:
                        next_steps.append(step)

        return {
            "analysis": analysis,
            "recommendations": recommendations[:10],  # Limit
            "next_steps": next_steps[:10]
        }

    def _get_generation_config(self, temperature: float = 0.3) -> Dict[str, Any]:
        """Get LLM generation configuration."""
        return {
            "temperature": temperature,
            "max_output_tokens": 4096,
            "top_p": 0.95,
            "top_k": 40
        }


# Factory function
def create_escalation_agent(context: Dict[str, Any], message_bus, orchestrator_id: str):
    """Factory function to create escalation agent."""
    return EscalationAgent(
        context=context,
        message_bus=message_bus,
        orchestrator_id=orchestrator_id
    )

# Export for backward compatibility
escalation_agent = None  # Will be instantiated when needed
