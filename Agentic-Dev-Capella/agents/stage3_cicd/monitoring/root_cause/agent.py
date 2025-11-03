"""
agents/stage3_cicd/monitoring/root_cause/agent.py

Root cause analysis agent investigates incidents and identifies root causes.
"""

from typing import Dict, List, Any, Optional
import re
import json

from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration


def analyze_incident(incident: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze incident to identify root cause."""
    return {
        "status": "success",
        "analysis": {
            "incident_id": incident.get("id"),
            "symptoms": ["High error rate", "Slow response times"],
            "affected_services": ["order-service"],
            "timeline": "Started at 10:15 AM, peaked at 10:20 AM"
        }
    }


def trace_dependencies(service: str, timestamp: str) -> Dict[str, Any]:
    """Trace service dependencies at time of incident."""
    return {
        "status": "success",
        "dependency_trace": {
            "service": service,
            "dependencies": [
                {"service": "payment-service", "status": "healthy"},
                {"service": "inventory-service", "status": "degraded"},
                {"service": "database", "status": "healthy"}
            ],
            "root_service": "inventory-service"
        }
    }


def analyze_logs(service: str, time_range: str) -> Dict[str, Any]:
    """Analyze logs for errors and patterns."""
    return {
        "status": "success",
        "log_analysis": {
            "error_count": 234,
            "error_patterns": [
                {"pattern": "Connection timeout to inventory-service", "count": 198},
                {"pattern": "Null pointer exception", "count": 36}
            ],
            "root_cause_indicators": ["Connection timeout to inventory-service"]
        }
    }


def correlate_events(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Correlate events to find root cause."""
    return {
        "status": "success",
        "correlation": {
            "root_cause": "Inventory service database connection pool exhausted",
            "contributing_factors": [
                "Sudden spike in traffic",
                "Connection pool size too small"
            ],
            "confidence": 0.92
        }
    }


def generate_rca_report(
    analysis: Dict, dependencies: Dict, logs: Dict, correlation: Dict
) -> Dict[str, Any]:
    """Generate root cause analysis report."""
    return {
        "status": "success",
        "rca_report": {
            "incident_id": analysis.get("analysis", {}).get("incident_id"),
            "root_cause": correlation.get("correlation", {}).get("root_cause"),
            "contributing_factors": correlation.get("correlation", {}).get("contributing_factors", []),
            "affected_services": analysis.get("analysis", {}).get("affected_services", []),
            "timeline": analysis.get("analysis", {}).get("timeline"),
            "remediation_actions": [
                "Increase inventory-service database connection pool size from 20 to 50",
                "Add connection pool monitoring and alerting",
                "Implement circuit breaker for inventory-service calls"
            ],
            "preventive_measures": [
                "Load testing with realistic traffic patterns",
                "Auto-scaling for database connections",
                "Improved capacity planning"
            ]
        }
    }


class RootCauseAnalysisAgent(A2AEnabledAgent):
    """
    LLM-powered Root Cause Analysis Agent.

    Investigates production incidents with intelligent correlation and pattern recognition.
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize Root Cause Analysis Agent with LLM."""
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

    def analyze_incident_llm(
        self,
        incident_data: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Deep incident analysis with timeline reconstruction."""
        print(f"[Root Cause Analysis] Analyzing incident with LLM")

        prompt = self._build_incident_analysis_prompt(incident_data)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.3)
        )

        analysis = self._parse_incident_analysis(response.text)

        return {
            "status": "success",
            "incident_analysis": analysis
        }

    def correlate_events_llm(
        self,
        events: List[Dict[str, Any]],
        metrics: Dict[str, Any],
        logs: List[str],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Intelligent event correlation across services."""
        print(f"[Root Cause Analysis] Correlating events with LLM")

        prompt = self._build_event_correlation_prompt(events, metrics, logs)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.2)
        )

        correlation = self._parse_event_correlation(response.text)

        return {
            "status": "success",
            "correlation": correlation,
            "root_cause": correlation.get("root_cause", "Unknown"),
            "confidence": correlation.get("confidence", 0.0)
        }

    def analyze_logs_llm(
        self,
        logs: List[str],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Natural language log analysis to extract patterns."""
        print(f"[Root Cause Analysis] Analyzing logs with LLM")

        prompt = self._build_log_analysis_prompt(logs)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.3)
        )

        log_analysis = self._parse_log_analysis(response.text)

        return {
            "status": "success",
            "log_analysis": log_analysis
        }

    def generate_remediation_plan_llm(
        self,
        root_cause: str,
        incident_context: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate specific remediation and preventive measures."""
        print(f"[Root Cause Analysis] Generating remediation plan with LLM")

        prompt = self._build_remediation_prompt(root_cause, incident_context)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.3)
        )

        remediation = self._parse_remediation_plan(response.text)

        return {
            "status": "success",
            "remediation_plan": remediation
        }

    def _build_incident_analysis_prompt(self, incident_data: Dict[str, Any]) -> str:
        """Build prompt for incident analysis."""

        incident_text = json.dumps(incident_data, indent=2)

        prompt = f"""You are a senior Site Reliability Engineer conducting a root cause analysis of a production incident.

**Incident Data:**
{incident_text}

**Analysis Requirements:**

1. **Timeline Reconstruction**
   - Identify trigger event (what started the incident)
   - Sequence of events (cascade of failures)
   - Peak impact time
   - Resolution time
   - Time to detect vs time to resolve

2. **Symptom Analysis**
   - User-visible symptoms
   - System-level symptoms
   - Metrics anomalies
   - Error patterns

3. **Affected Services**
   - Primary affected services
   - Secondary affected services (cascading failures)
   - Blast radius assessment
   - User impact quantification

4. **Initial Hypothesis**
   - Most likely root cause categories:
     - Code bug
     - Configuration error
     - Infrastructure failure
     - Dependency failure
     - Capacity/scaling issue
     - Security incident
     - Data corruption

**Response Format:**

**Timeline:**
- [HH:MM] Trigger Event: [description]
- [HH:MM] First Symptom: [description]
- [HH:MM] Alert Fired: [description]
- [HH:MM] Investigation Started: [description]
- [HH:MM] Peak Impact: [description]
- [HH:MM] Mitigation Applied: [description]
- [HH:MM] Incident Resolved: [description]

**Symptoms:**
- User Impact: [description with severity]
- System Symptoms: [list of observable system issues]
- Error Patterns: [common error messages/patterns]

**Affected Services:**
- Primary: [service name] - [impact level]
- Secondary: [service name] - [impact level]
- Blast Radius: [% of users/requests affected]

**Initial Hypotheses:**
1. **Hypothesis 1**: [description] - Likelihood: [high/medium/low]
   - Supporting Evidence: [evidence]
   - Contradicting Evidence: [evidence]

2. **Hypothesis 2**: [description] - Likelihood: [high/medium/low]
   - Supporting Evidence: [evidence]
   - Contradicting Evidence: [evidence]

**Severity Assessment:** [SEV-1/SEV-2/SEV-3]

**Detection Gap:**
[Why didn't we catch this earlier? What monitoring was missing?]

Provide detailed, evidence-based analysis.
"""

        return prompt

    def _build_event_correlation_prompt(
        self,
        events: List[Dict[str, Any]],
        metrics: Dict[str, Any],
        logs: List[str]
    ) -> str:
        """Build prompt for event correlation."""

        events_text = json.dumps(events, indent=2)
        metrics_text = json.dumps(metrics, indent=2)
        logs_sample = "\n".join(logs[:100])  # First 100 log lines

        prompt = f"""You are an AI system correlating events across distributed services to identify root causes.

**Events (time-ordered):**
{events_text}

**Metrics:**
{metrics_text}

**Log Sample:**
{logs_sample}

**Correlation Analysis Requirements:**

1. **Temporal Correlation**
   - Which events happened first (potential triggers)?
   - Lag between events (propagation time)
   - Simultaneous events (common cause indicator)

2. **Causal Relationships**
   - Event A caused Event B (directional causality)
   - Events A & B both caused by C (common root cause)
   - Cascading failures (chain of causality)

3. **Service Dependencies**
   - Which service failure triggered others?
   - Upstream vs downstream failures
   - Critical path identification

4. **Pattern Recognition**
   - Similar incidents in the past?
   - Known failure modes?
   - Correlation with deployments/changes?

5. **Statistical Correlation**
   - Metric deviations correlated with errors
   - Request rate vs error rate correlation
   - Resource exhaustion indicators

**Response Format:**

**Root Cause:** [Single sentence summary]

**Confidence:** [0.0-1.0]

**Causal Chain:**
1. [Initial trigger event] →
2. [Consequence 1] →
3. [Consequence 2] →
4. [Final symptom observed]

**Evidence:**
- **Strong Evidence**: [Evidence supporting root cause]
- **Weak Evidence**: [Circumstantial evidence]
- **Contradicting Evidence**: [Evidence against this root cause]

**Alternative Root Causes:**
1. [Alternative explanation] - Likelihood: [%]
2. [Alternative explanation] - Likelihood: [%]

**Key Insights:**
- [Insight 1 about the failure mode]
- [Insight 2 about propagation]
- [Insight 3 about detection]

**Missing Information:**
- [What additional data would increase confidence?]
- [What monitoring gaps prevent definitive RCA?]

Focus on the most parsimonious explanation that fits all observed evidence.
"""

        return prompt

    def _build_log_analysis_prompt(self, logs: List[str]) -> str:
        """Build prompt for log analysis."""

        logs_sample = "\n".join(logs[:200])  # First 200 log lines

        prompt = f"""You are a log analysis expert extracting actionable insights from application logs.

**Log Sample:**
```
{logs_sample}
```

**Analysis Requirements:**

1. **Error Pattern Extraction**
   - Common error messages
   - Error frequencies
   - Error progression over time
   - Unique vs repeated errors

2. **Stack Trace Analysis**
   - Root exception types
   - Common stack trace patterns
   - Code locations with issues
   - Third-party library errors

3. **Request Flow Analysis**
   - Failed request patterns
   - Timeout indicators
   - Retry storms
   - Request ID correlation

4. **Resource Issues**
   - Connection pool exhaustion
   - Thread pool exhaustion
   - Memory pressure indicators
   - Database query timeouts

5. **Security Indicators**
   - Authentication failures
   - Authorization errors
   - Suspicious request patterns
   - Injection attempt indicators

**Response Format:**

**Error Summary:**
- Total Errors: [count]
- Unique Error Types: [count]
- Error Rate Trend: [increasing/stable/decreasing]

**Top Error Patterns:**
1. **Pattern**: [error message pattern]
   - **Count**: [X occurrences]
   - **Severity**: [critical/high/medium/low]
   - **Affected Component**: [service/module]
   - **Root Exception**: [exception type]
   - **Likely Cause**: [hypothesis]

2. **Pattern**: [error message pattern]
   - [same structure as above]

**Stack Trace Analysis:**
- Most Common Root Exception: [exception type]
- Affected Code Locations: [file:line references]
- Third-Party Library Issues: [library name and version]

**Resource Exhaustion Indicators:**
- [Indicator 1 with evidence from logs]
- [Indicator 2 with evidence from logs]

**Security Concerns:**
- [Any security-related patterns observed]

**Temporal Patterns:**
- Error burst at [time]: [description]
- Sustained errors from [time] to [time]: [description]

**Actionable Insights:**
1. [Specific action based on log analysis]
2. [Specific action based on log analysis]
3. [Specific action based on log analysis]

Extract concrete, actionable information from the logs.
"""

        return prompt

    def _build_remediation_prompt(
        self,
        root_cause: str,
        incident_context: Dict[str, Any]
    ) -> str:
        """Build prompt for remediation planning."""

        context_text = json.dumps(incident_context, indent=2)

        prompt = f"""You are an incident response expert creating a remediation plan for a production incident.

**Root Cause:**
{root_cause}

**Incident Context:**
{context_text}

**Remediation Plan Requirements:**

1. **Immediate Actions** (stop the bleeding)
   - Actions to restore service immediately
   - Rollback procedures
   - Traffic shifting
   - Manual interventions

2. **Short-Term Fixes** (within 24-48 hours)
   - Quick code fixes
   - Configuration changes
   - Capacity adjustments
   - Temporary workarounds

3. **Long-Term Solutions** (within 1-2 weeks)
   - Architectural improvements
   - Code refactoring
   - Infrastructure upgrades
   - Process improvements

4. **Preventive Measures**
   - Monitoring improvements
   - Alerting enhancements
   - Testing improvements
   - Documentation updates
   - Runbooks

5. **Post-Incident Review**
   - Stakeholders to involve
   - Questions to answer
   - Metrics to track
   - Follow-up items

**Response Format:**

**Immediate Actions** (execute now):
1. [Action] - Owner: [team/person] - ETA: [minutes]
   - Command: [specific command to run]
   - Expected Outcome: [what success looks like]
   - Rollback: [how to undo if it makes things worse]

**Short-Term Fixes** (24-48 hours):
1. [Action] - Owner: [team] - Priority: [P0/P1/P2]
   - Description: [detailed description]
   - Implementation Steps: [specific steps]
   - Testing Required: [what to test]

**Long-Term Solutions** (1-2 weeks):
1. [Action] - Owner: [team] - Priority: [P1/P2]
   - Problem: [what this solves]
   - Solution: [architectural/code change]
   - Effort Estimate: [person-days]

**Preventive Measures:**
1. **Monitoring**: [specific metric/alert to add]
2. **Testing**: [test scenario to add to prevent recurrence]
3. **Documentation**: [runbook or doc to create/update]
4. **Process**: [process improvement]

**Success Metrics:**
- Service restored by: [time]
- Short-term fixes deployed by: [date]
- Long-term solutions implemented by: [date]
- Incident recurrence: [target: 0]

**Post-Incident Review:**
- Schedule: [within 48 hours]
- Attendees: [stakeholders]
- Key Questions:
  1. [Question about detection]
  2. [Question about response]
  3. [Question about prevention]

**Communication Plan:**
- Internal Status Update: [frequency and channel]
- Customer Communication: [what to say and when]
- Postmortem Distribution: [who needs to read it]

Provide specific, actionable remediation steps with clear ownership and timelines.
"""

        return prompt

    def _parse_incident_analysis(self, response_text: str) -> Dict[str, Any]:
        """Parse incident analysis response."""

        # Extract timeline
        timeline = self._extract_list_items(response_text, "**Timeline:**")

        # Extract symptoms
        symptoms = self._extract_list_items(response_text, "**Symptoms:**")

        # Extract affected services
        affected_services = self._extract_list_items(response_text, "**Affected Services:**")

        # Extract hypotheses
        hypotheses = self._extract_list_items(response_text, "**Initial Hypotheses:**")

        # Extract severity
        severity = "SEV-3"
        sev_match = re.search(r"\*\*Severity Assessment:\*\*\s*\[?(SEV-\d)\]?", response_text)
        if sev_match:
            severity = sev_match.group(1)

        return {
            "timeline": timeline,
            "symptoms": symptoms,
            "affected_services": affected_services,
            "hypotheses": hypotheses,
            "severity": severity
        }

    def _parse_event_correlation(self, response_text: str) -> Dict[str, Any]:
        """Parse event correlation response."""

        # Extract root cause
        root_cause = ""
        cause_match = re.search(r"\*\*Root Cause:\*\*\s*(.*?)(?=\n\*\*|\Z)", response_text, re.DOTALL)
        if cause_match:
            root_cause = cause_match.group(1).strip()

        # Extract confidence
        confidence = 0.0
        conf_match = re.search(r"\*\*Confidence:\*\*\s*\[?([\d.]+)\]?", response_text)
        if conf_match:
            confidence = float(conf_match.group(1))

        # Extract causal chain
        causal_chain = self._extract_list_items(response_text, "**Causal Chain:**")

        # Extract evidence
        strong_evidence = self._extract_list_items(response_text, "**Strong Evidence**:")
        weak_evidence = self._extract_list_items(response_text, "**Weak Evidence**:")

        # Extract alternatives
        alternatives = self._extract_list_items(response_text, "**Alternative Root Causes:**")

        return {
            "root_cause": root_cause,
            "confidence": confidence,
            "causal_chain": causal_chain,
            "strong_evidence": strong_evidence,
            "weak_evidence": weak_evidence,
            "alternative_causes": alternatives
        }

    def _parse_log_analysis(self, response_text: str) -> Dict[str, Any]:
        """Parse log analysis response."""

        # Extract error patterns
        error_patterns = self._extract_list_items(response_text, "**Top Error Patterns:**")

        # Extract resource indicators
        resource_issues = self._extract_list_items(response_text, "**Resource Exhaustion Indicators:**")

        # Extract actionable insights
        insights = self._extract_list_items(response_text, "**Actionable Insights:**")

        return {
            "error_patterns": error_patterns,
            "resource_exhaustion": resource_issues,
            "actionable_insights": insights
        }

    def _parse_remediation_plan(self, response_text: str) -> Dict[str, Any]:
        """Parse remediation plan response."""

        # Extract immediate actions
        immediate = self._extract_list_items(response_text, "**Immediate Actions**")

        # Extract short-term fixes
        short_term = self._extract_list_items(response_text, "**Short-Term Fixes**")

        # Extract long-term solutions
        long_term = self._extract_list_items(response_text, "**Long-Term Solutions**")

        # Extract preventive measures
        preventive = self._extract_list_items(response_text, "**Preventive Measures:**")

        return {
            "immediate_actions": immediate,
            "short_term_fixes": short_term,
            "long_term_solutions": long_term,
            "preventive_measures": preventive
        }

    def _extract_list_items(self, text: str, section_header: str) -> List[str]:
        """Extract list items from a section."""
        items = []

        if section_header in text:
            section_start = text.find(section_header)
            section_text = text[section_start:]

            # Find next section or end
            next_section = re.search(r"\n\*\*[A-Z]", section_text[len(section_header):])
            if next_section:
                section_text = section_text[:len(section_header) + next_section.start()]

            # Extract list items
            for line in section_text.split("\n"):
                line = line.strip()
                if line.startswith("-") or line.startswith("*") or re.match(r"^\d+\.", line):
                    item = re.sub(r"^[-*\d.]+\s*", "", line).strip()
                    if item and len(item) > 5:
                        items.append(item)

        return items[:20]

    def _get_generation_config(self, temperature: float = 0.3) -> Dict[str, Any]:
        """Get LLM generation configuration."""
        return {
            "temperature": temperature,
            "max_output_tokens": 8192,
            "top_p": 0.95,
            "top_k": 40
        }


# Factory function
def create_root_cause_agent(context: Dict[str, Any], message_bus, orchestrator_id: str):
    """Factory function to create LLM-enhanced root cause analysis agent."""
    return RootCauseAnalysisAgent(
        context=context,
        message_bus=message_bus,
        orchestrator_id=orchestrator_id
    )

# Backward compatibility
root_cause_agent = None
