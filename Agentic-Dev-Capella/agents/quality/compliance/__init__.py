"""
agents/quality/compliance

Compliance agent package for GDPR, HIPAA, SOC2, and other regulatory
compliance validation and reporting.
"""

from .agent import compliance_agent, AGENT_CAPABILITY

__all__ = ["compliance_agent", "AGENT_CAPABILITY"]
