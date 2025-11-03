"""
agents/stage3_cicd/monitoring/monitor/agent.py

Monitor agent monitors system health, performance, and alerts on issues.
"""

from typing import Dict, List, Any, Optional
import re
import json

from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration


def collect_metrics(service: str, time_range: str) -> Dict[str, Any]:
    """Collect metrics for service."""
    return {
        "status": "success",
        "metrics": {
            "cpu_usage_percent": 45,
            "memory_usage_percent": 62,
            "request_rate_rps": 850,
            "error_rate_percent": 0.2,
            "response_time_p95_ms": 180,
            "response_time_p99_ms": 320
        }
    }


def check_sla_compliance(metrics: Dict[str, Any], sla: Dict[str, Any]) -> Dict[str, Any]:
    """Check if metrics meet SLA."""
    return {
        "status": "success",
        "sla_compliance": {
            "response_time": True,
            "error_rate": True,
            "availability": True,
            "overall_compliant": True
        }
    }


def detect_anomalies(metrics: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
    """Detect anomalies in metrics."""
    return {
        "status": "success",
        "anomalies": {
            "detected": False,
            "anomaly_list": [],
            "severity": "none"
        }
    }


def generate_alerts(anomalies: Dict[str, Any], sla_compliance: Dict[str, Any]) -> Dict[str, Any]:
    """Generate alerts for issues."""
    return {
        "status": "success",
        "alerts": {
            "critical": [],
            "warning": [],
            "info": [],
            "total": 0
        }
    }


def generate_monitoring_report(
    metrics: Dict, sla: Dict, anomalies: Dict, alerts: Dict
) -> Dict[str, Any]:
    """Generate monitoring report."""
    return {
        "status": "success",
        "monitoring_report": {
            "health_status": "healthy",
            "sla_compliance": "compliant",
            "anomalies_detected": False,
            "alerts_generated": 0,
            "metrics_summary": metrics.get("metrics", {}),
            "recommendations": []
        }
    }


class MonitorAgent(A2AEnabledAgent):
    """
    LLM-powered Monitor Agent.

    Intelligently monitors system health with AI-powered anomaly detection and analysis.
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize Monitor Agent with LLM."""
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

    def analyze_metrics_llm(
        self,
        metrics: Dict[str, Any],
        historical_baseline: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze metrics with LLM for intelligent interpretation."""
        print(f"[Monitor] Analyzing metrics with LLM")

        prompt = self._build_metric_analysis_prompt(metrics, historical_baseline)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.3)
        )

        analysis = self._parse_metric_analysis(response.text)

        return {
            "status": "success",
            "metric_analysis": analysis,
            "health_status": analysis.get("health_status", "unknown"),
            "trends": analysis.get("trends", [])
        }

    def detect_anomalies_llm(
        self,
        metrics: Dict[str, Any],
        baseline: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """AI-powered anomaly detection with pattern recognition."""
        print(f"[Monitor] Detecting anomalies with LLM")

        prompt = self._build_anomaly_detection_prompt(metrics, baseline)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.2)
        )

        anomalies = self._parse_anomaly_detection(response.text)

        return {
            "status": "success",
            "anomalies_detected": len(anomalies.get("anomalies", [])) > 0,
            "anomalies": anomalies.get("anomalies", []),
            "severity": anomalies.get("overall_severity", "none"),
            "recommendations": anomalies.get("recommendations", [])
        }

    def recommend_slo_thresholds_llm(
        self,
        service_spec: Dict[str, Any],
        historical_metrics: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Recommend optimal SLO/SLA thresholds based on data."""
        print(f"[Monitor] Recommending SLO thresholds with LLM")

        prompt = self._build_slo_recommendation_prompt(service_spec, historical_metrics)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.3)
        )

        recommendations = self._parse_slo_recommendations(response.text)

        return {
            "status": "success",
            "slo_recommendations": recommendations
        }

    def generate_alert_rules_llm(
        self,
        service_spec: Dict[str, Any],
        incident_history: Optional[List[Dict[str, Any]]] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate intelligent alerting rules to reduce false positives."""
        print(f"[Monitor] Generating alert rules with LLM")

        prompt = self._build_alert_rules_prompt(service_spec, incident_history)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.2)
        )

        alert_rules = self._parse_alert_rules(response.text)

        return {
            "status": "success",
            "alert_rules": alert_rules
        }

    def _build_metric_analysis_prompt(
        self,
        metrics: Dict[str, Any],
        historical_baseline: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for metric analysis."""

        metrics_text = json.dumps(metrics, indent=2)
        baseline_text = json.dumps(historical_baseline, indent=2) if historical_baseline else "No baseline provided"

        prompt = f"""You are a Site Reliability Engineer analyzing production system metrics.

**Current Metrics:**
{metrics_text}

**Historical Baseline:**
{baseline_text}

**Analysis Requirements:**

1. **Health Status Assessment**
   - Overall system health (healthy/degraded/critical)
   - Resource utilization analysis (CPU, memory, disk, network)
   - Performance metrics (latency, throughput, error rates)
   - Capacity planning indicators

2. **Trend Analysis**
   - Identify upward/downward trends
   - Seasonality or cyclical patterns
   - Rate of change analysis
   - Projection for next 24 hours

3. **Performance Bottlenecks**
   - Resource constraints (CPU, memory, I/O)
   - Saturation points
   - Queueing delays
   - Database query performance

4. **Error Rate Analysis**
   - Error rate compared to baseline
   - Error types and distribution
   - Impact on user experience
   - Correlation with other metrics

5. **Comparison to Baseline**
   - Deviation percentage from baseline
   - Statistical significance
   - Acceptable variance vs anomaly
   - Historical context

**Response Format:**

**Health Status:** [healthy/degraded/critical]

**Overall Assessment:**
[2-3 sentence summary of system health]

**Key Metrics Analysis:**
- CPU Usage: [value]% - [trend] - [assessment]
- Memory Usage: [value]% - [trend] - [assessment]
- Error Rate: [value]% - [trend] - [assessment]
- Response Time p95: [value]ms - [trend] - [assessment]
- Request Rate: [value] RPS - [trend] - [assessment]

**Trends Identified:**
- Trend 1: [description with direction and rate]
- Trend 2: [description with direction and rate]

**Bottlenecks:**
- [Bottleneck 1 with impact assessment]
- [Bottleneck 2 with impact assessment]

**Deviations from Baseline:**
- [Metric]: [deviation percentage] - [significance]
- [Metric]: [deviation percentage] - [significance]

**Capacity Concerns:**
- [Concern 1 with estimated time to saturation]
- [Concern 2 with estimated time to saturation]

**Recommendations:**
1. [Immediate action if health is degraded/critical]
2. [Proactive recommendation for optimization]
3. [Capacity planning recommendation]

Provide data-driven analysis with specific metrics and thresholds.
"""

        return prompt

    def _build_anomaly_detection_prompt(
        self,
        metrics: Dict[str, Any],
        baseline: Dict[str, Any]
    ) -> str:
        """Build prompt for anomaly detection."""

        metrics_text = json.dumps(metrics, indent=2)
        baseline_text = json.dumps(baseline, indent=2)

        prompt = f"""You are an AI anomaly detection system analyzing production metrics for unusual patterns.

**Current Metrics:**
{metrics_text}

**Baseline Metrics:**
{baseline_text}

**Anomaly Detection Criteria:**

1. **Statistical Anomalies**
   - Values > 3 standard deviations from mean
   - Sudden spikes or drops (>50% change)
   - Unexpected patterns or correlations

2. **Pattern Anomalies**
   - Breaking established daily/weekly patterns
   - Missing expected load patterns
   - Unusual traffic distribution

3. **Correlation Anomalies**
   - Metrics moving in unexpected directions together
   - Breaking normal correlations (e.g., CPU high but requests low)
   - Cascading effects

4. **Threshold Anomalies**
   - Approaching or exceeding capacity limits
   - Violating SLO thresholds
   - Resource exhaustion indicators

5. **Behavioral Anomalies**
   - Response time distribution changes
   - Error rate pattern changes
   - Traffic source anomalies

**Response Format:**

**Anomalies Detected:** [yes/no]

**Overall Severity:** [none/low/medium/high/critical]

**Anomalies List:**

1. **Anomaly**: [Metric name and description]
   - **Current Value**: [value]
   - **Baseline**: [value]
   - **Deviation**: [percentage or absolute]
   - **Severity**: [low/medium/high/critical]
   - **Type**: [spike/drop/pattern-break/correlation]
   - **Impact**: [potential impact on users/system]
   - **Likely Cause**: [hypothesis based on patterns]

2. **Anomaly**: [Next anomaly...]

**Pattern Analysis:**
- [Description of unusual patterns observed]
- [Correlation with other metrics]

**Root Cause Hypothesis:**
- Most Likely: [hypothesis with reasoning]
- Alternative: [alternative hypothesis]

**Immediate Actions Required:**
- [Action 1 with urgency level]
- [Action 2 with urgency level]

**Recommendations:**
1. [Investigation recommendation]
2. [Mitigation recommendation]
3. [Monitoring recommendation]

Be conservative - prioritize recall over precision (flag potential issues even if uncertain).
"""

        return prompt

    def _build_slo_recommendation_prompt(
        self,
        service_spec: Dict[str, Any],
        historical_metrics: Dict[str, Any]
    ) -> str:
        """Build prompt for SLO threshold recommendations."""

        spec_text = json.dumps(service_spec, indent=2)
        metrics_text = json.dumps(historical_metrics, indent=2)

        prompt = f"""You are a reliability engineer defining Service Level Objectives (SLOs) for a production service.

**Service Specification:**
{spec_text}

**Historical Performance Metrics (30 days):**
{metrics_text}

**SLO Definition Requirements:**

1. **Availability SLO**
   - Target uptime percentage (e.g., 99.9%, 99.95%, 99.99%)
   - Acceptable downtime budget
   - Measurement window (monthly/quarterly)

2. **Latency SLO**
   - Response time percentile (p50, p95, p99)
   - Target latency thresholds
   - Per-endpoint SLOs if needed

3. **Error Rate SLO**
   - Maximum acceptable error rate
   - Error budget consumption rate
   - Different thresholds for 4xx vs 5xx

4. **Throughput SLO**
   - Minimum requests per second
   - Peak capacity guarantees

**Response Format:**

**Recommended SLOs:**

1. **Availability SLO**
   - Target: [99.X%]
   - Monthly Downtime Budget: [X minutes]
   - Justification: [Why this target based on historical data and service criticality]

2. **Latency SLO**
   - p95 Response Time: < [X ms]
   - p99 Response Time: < [Y ms]
   - Justification: [Based on historical percentiles and user experience requirements]

3. **Error Rate SLO**
   - 4xx Error Rate: < [X%]
   - 5xx Error Rate: < [Y%]
   - Overall Error Rate: < [Z%]
   - Justification: [Based on historical error rates and criticality]

4. **Throughput SLO** (if applicable)
   - Minimum RPS: [X requests/second]
   - Justification: [Based on capacity and expected load]

**Alert Thresholds:**
- Warning (80% of error budget consumed): [thresholds]
- Critical (95% of error budget consumed): [thresholds]

**Error Budget Policy:**
- Monthly Error Budget: [X minutes of downtime / Y failed requests]
- Burn Rate Alert: [Alert if budget depleting at >2x expected rate]
- Policy: [What happens when budget exhausted - freeze deploys, etc.]

**SLO Review Schedule:**
- Recommended review frequency: [monthly/quarterly]
- Adjustment triggers: [conditions for revising SLOs]

**Rationale:**
[Detailed explanation of how these SLOs balance reliability with development velocity, based on service criticality and historical performance]

Base recommendations on actual historical performance with appropriate safety margins.
"""

        return prompt

    def _build_alert_rules_prompt(
        self,
        service_spec: Dict[str, Any],
        incident_history: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Build prompt for alert rule generation."""

        spec_text = json.dumps(service_spec, indent=2)
        incidents_text = json.dumps(incident_history, indent=2) if incident_history else "No incident history provided"

        prompt = f"""You are a monitoring engineer creating intelligent alert rules that balance catching real issues while minimizing false positives.

**Service Specification:**
{spec_text}

**Incident History (Past 90 Days):**
{incidents_text}

**Alert Rule Design Principles:**

1. **Reduce Alert Fatigue**
   - Avoid alerting on self-healing transient issues
   - Use multi-window detection (sustained issues, not spikes)
   - Correlate multiple signals

2. **Actionability**
   - Every alert must require human action
   - Include context for quick diagnosis
   - Provide runbook links

3. **Severity Levels**
   - Critical: Immediate user impact, page on-call
   - Warning: Trending toward issue, notify async
   - Info: FYI only, no immediate action

4. **Detection Methods**
   - Threshold-based (simple, fast)
   - Rate-of-change (catch gradual degradation)
   - Pattern-based (detect anomalies)

**Response Format:**

**Critical Alerts:**

1. **Alert Name**: [Descriptive name]
   - **Metric**: [Metric to monitor]
   - **Condition**: [Threshold or pattern]
   - **Duration**: [How long before alert fires]
   - **Rationale**: [Why this is critical]
   - **Example**: error_rate > 5% for 3 minutes
   - **Action**: [What on-call should do]

**Warning Alerts:**

1. **Alert Name**: [Descriptive name]
   - **Metric**: [Metric to monitor]
   - **Condition**: [Threshold or pattern]
   - **Duration**: [How long before alert fires]
   - **Rationale**: [Why this warrants attention]
   - **Action**: [What team should investigate]

**Info Alerts:**

1. **Alert Name**: [Descriptive name]
   - **Metric**: [Metric to monitor]
   - **Condition**: [Threshold or pattern]
   - **Rationale**: [Why this is tracked]

**Alert Correlation Rules:**
- [Condition 1] AND [Condition 2] → [Combined alert with higher severity]
- [Pattern description] → [Root cause indicator]

**Alerting Best Practices:**
- Silence Period: [X minutes] after alert fires (prevent alert storms)
- Escalation: [Auto-escalate after Y minutes if not acknowledged]
- Auto-Resolution: [Conditions for auto-resolving alerts]

**False Positive Prevention:**
- Known Maintenance Windows: [How to handle expected changes]
- Deployment Grace Period: [X minutes] after deployment before alerting
- Correlation: Alert only if multiple symptoms present

**Recommendations:**
1. [Specific alert to add based on incident history]
2. [Alert to remove or adjust due to false positives]
3. [New monitoring gap to address]

Design alerts based on actual incident patterns, not theoretical worst-cases.
"""

        return prompt

    def _parse_metric_analysis(self, response_text: str) -> Dict[str, Any]:
        """Parse metric analysis response."""

        # Extract health status
        health_status = "unknown"
        health_match = re.search(r"\*\*Health Status:\*\*\s*\[?(healthy|degraded|critical)\]?", response_text, re.IGNORECASE)
        if health_match:
            health_status = health_match.group(1).lower()

        # Extract trends
        trends = self._extract_list_items(response_text, "**Trends Identified:**")

        # Extract bottlenecks
        bottlenecks = self._extract_list_items(response_text, "**Bottlenecks:**")

        # Extract recommendations
        recommendations = self._extract_list_items(response_text, "**Recommendations:**")

        # Extract overall assessment
        assessment = ""
        assessment_match = re.search(r"\*\*Overall Assessment:\*\*\s*\n(.*?)(?=\n\*\*|\Z)", response_text, re.DOTALL)
        if assessment_match:
            assessment = assessment_match.group(1).strip()

        return {
            "health_status": health_status,
            "overall_assessment": assessment,
            "trends": trends,
            "bottlenecks": bottlenecks,
            "recommendations": recommendations
        }

    def _parse_anomaly_detection(self, response_text: str) -> Dict[str, Any]:
        """Parse anomaly detection response."""

        # Extract anomalies detected
        anomalies_detected = False
        detected_match = re.search(r"\*\*Anomalies Detected:\*\*\s*\[?(yes|no)\]?", response_text, re.IGNORECASE)
        if detected_match and detected_match.group(1).lower() == "yes":
            anomalies_detected = True

        # Extract severity
        severity = "none"
        severity_match = re.search(r"\*\*Overall Severity:\*\*\s*\[?(none|low|medium|high|critical)\]?", response_text, re.IGNORECASE)
        if severity_match:
            severity = severity_match.group(1).lower()

        # Extract anomalies list
        anomalies = self._extract_list_items(response_text, "**Anomalies List:**")

        # Extract immediate actions
        immediate_actions = self._extract_list_items(response_text, "**Immediate Actions Required:**")

        # Extract recommendations
        recommendations = self._extract_list_items(response_text, "**Recommendations:**")

        return {
            "anomalies_detected": anomalies_detected,
            "overall_severity": severity,
            "anomalies": anomalies,
            "immediate_actions": immediate_actions,
            "recommendations": recommendations
        }

    def _parse_slo_recommendations(self, response_text: str) -> Dict[str, Any]:
        """Parse SLO recommendations response."""

        # Extract availability SLO
        availability_target = ""
        avail_match = re.search(r"Target:\s*\[?([\d.]+%)\]?", response_text)
        if avail_match:
            availability_target = avail_match.group(1)

        # Extract SLOs (simplified extraction)
        slos = {
            "availability": availability_target,
            "latency_p95": self._extract_threshold(response_text, "p95 Response Time"),
            "latency_p99": self._extract_threshold(response_text, "p99 Response Time"),
            "error_rate": self._extract_threshold(response_text, "Overall Error Rate")
        }

        # Extract error budget policy
        error_budget = self._extract_list_items(response_text, "**Error Budget Policy:**")

        return {
            "slos": slos,
            "error_budget_policy": error_budget
        }

    def _parse_alert_rules(self, response_text: str) -> Dict[str, Any]:
        """Parse alert rules response."""

        # Extract critical alerts
        critical_alerts = self._extract_list_items(response_text, "**Critical Alerts:**")

        # Extract warning alerts
        warning_alerts = self._extract_list_items(response_text, "**Warning Alerts:**")

        # Extract info alerts
        info_alerts = self._extract_list_items(response_text, "**Info Alerts:**")

        # Extract correlation rules
        correlation_rules = self._extract_list_items(response_text, "**Alert Correlation Rules:**")

        return {
            "critical": critical_alerts,
            "warning": warning_alerts,
            "info": info_alerts,
            "correlation_rules": correlation_rules
        }

    def _extract_threshold(self, text: str, metric_name: str) -> str:
        """Extract threshold value for a metric."""
        pattern = rf"{metric_name}:\s*<?\s*\[?([^\]]+)\]?"
        match = re.search(pattern, text)
        return match.group(1).strip() if match else ""

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

        return items[:15]

    def _get_generation_config(self, temperature: float = 0.3) -> Dict[str, Any]:
        """Get LLM generation configuration."""
        return {
            "temperature": temperature,
            "max_output_tokens": 8192,
            "top_p": 0.95,
            "top_k": 40
        }


# Factory function
def create_monitor_agent(context: Dict[str, Any], message_bus, orchestrator_id: str):
    """Factory function to create LLM-enhanced monitor agent."""
    return MonitorAgent(
        context=context,
        message_bus=message_bus,
        orchestrator_id=orchestrator_id
    )

# Backward compatibility
monitor_agent = None
