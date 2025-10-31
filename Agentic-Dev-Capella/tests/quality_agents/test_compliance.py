"""
tests/quality_agents/test_compliance.py

Unit tests for Compliance Agent.
"""

import pytest
from agents.quality.compliance.agent import (
    compliance_agent,
    AGENT_CAPABILITY,
    check_gdpr_compliance,
    check_hipaa_compliance,
    check_soc2_compliance,
    check_pci_dss_compliance,
    generate_compliance_recommendations,
    generate_compliance_report
)
from shared.models.agent_capability import AgentType, InputModality


class TestComplianceAgentCapability:
    """Test agent capability declaration."""

    def test_agent_capability_exists(self):
        """Test that agent capability is properly defined."""
        assert AGENT_CAPABILITY is not None
        assert AGENT_CAPABILITY.agent_id == "compliance_agent"
        assert AGENT_CAPABILITY.agent_name == "Compliance Agent"
        assert AGENT_CAPABILITY.agent_type == AgentType.COMPLIANCE_ENGINEER

    def test_agent_capabilities(self):
        """Test that agent has correct capabilities."""
        expected_capabilities = {
            "gdpr_compliance",
            "hipaa_compliance",
            "soc2_compliance",
            "pci_dss_compliance",
            "compliance_auditing"
        }
        assert expected_capabilities.issubset(AGENT_CAPABILITY.capabilities)

    def test_agent_compliance_standards(self):
        """Test that agent supports compliance standards."""
        expected_standards = ["GDPR", "HIPAA", "SOC 2", "PCI-DSS"]
        for standard in expected_standards:
            assert standard in AGENT_CAPABILITY.compliance_standards


class TestGDPRCompliance:
    """Test GDPR compliance checking."""

    def test_check_gdpr_success(self):
        """Test successful GDPR compliance check."""
        result = check_gdpr_compliance("test_application")

        assert result["status"] == "success"
        assert "gdpr_assessment" in result
        assert "compliance_checks" in result
        assert "summary" in result

    def test_gdpr_articles_coverage(self):
        """Test GDPR check covers key articles."""
        result = check_gdpr_compliance("test_application")

        checks = result["compliance_checks"]
        expected_checks = [
            "lawful_basis",
            "data_minimization",
            "consent_management",
            "right_to_access",
            "right_to_erasure",
            "data_portability"
        ]

        for check_name in expected_checks:
            assert check_name in checks

    def test_gdpr_check_status(self):
        """Test GDPR checks have valid status values."""
        result = check_gdpr_compliance("test_application")

        valid_statuses = ["compliant", "partially_compliant", "non_compliant"]
        for check_name, check_data in result["compliance_checks"].items():
            assert "status" in check_data
            assert check_data["status"] in valid_statuses

    def test_gdpr_issues_documented(self):
        """Test non-compliant checks have documented issues."""
        result = check_gdpr_compliance("test_application")

        for check_name, check_data in result["compliance_checks"].items():
            if check_data["status"] == "non_compliant":
                assert "issues" in check_data
                assert len(check_data["issues"]) > 0

    def test_gdpr_summary(self):
        """Test GDPR summary includes compliance metrics."""
        result = check_gdpr_compliance("test_application")

        summary = result["summary"]
        assert "total_requirements" in summary
        assert "compliant" in summary
        assert "partially_compliant" in summary
        assert "non_compliant" in summary
        assert "compliance_score" in summary
        assert "risk_level" in summary


class TestHIPAACompliance:
    """Test HIPAA compliance checking."""

    def test_check_hipaa_success(self):
        """Test successful HIPAA compliance check."""
        result = check_hipaa_compliance("test_application")

        assert result["status"] == "success"
        assert "hipaa_assessment" in result
        assert "compliance_checks" in result

    def test_hipaa_safeguards_coverage(self):
        """Test HIPAA check covers all safeguard categories."""
        result = check_hipaa_compliance("test_application")

        checks = result["compliance_checks"]
        expected_safeguards = [
            "administrative_safeguards",
            "physical_safeguards",
            "technical_safeguards",
            "privacy_rule",
            "breach_notification"
        ]

        for safeguard in expected_safeguards:
            assert safeguard in checks

    def test_hipaa_administrative_safeguards(self):
        """Test administrative safeguards are evaluated."""
        result = check_hipaa_compliance("test_application")

        admin_safeguards = result["compliance_checks"]["administrative_safeguards"]
        assert "section" in admin_safeguards
        assert "requirements" in admin_safeguards

        requirements = admin_safeguards["requirements"]
        expected_requirements = [
            "security_management",
            "workforce_security",
            "access_management"
        ]

        for req in expected_requirements:
            assert req in requirements

    def test_hipaa_technical_safeguards(self):
        """Test technical safeguards are evaluated."""
        result = check_hipaa_compliance("test_application")

        tech_safeguards = result["compliance_checks"]["technical_safeguards"]
        requirements = tech_safeguards["requirements"]

        expected_requirements = [
            "access_control",
            "audit_controls",
            "integrity",
            "transmission_security",
            "encryption"
        ]

        for req in expected_requirements:
            assert req in requirements

    def test_hipaa_summary(self):
        """Test HIPAA summary includes compliance metrics."""
        result = check_hipaa_compliance("test_application")

        summary = result["summary"]
        assert "compliance_score" in summary
        assert "risk_level" in summary
        assert 0 <= summary["compliance_score"] <= 100


class TestSOC2Compliance:
    """Test SOC 2 compliance checking."""

    def test_check_soc2_success(self):
        """Test successful SOC 2 compliance check."""
        result = check_soc2_compliance("test_application")

        assert result["status"] == "success"
        assert "soc2_assessment" in result
        assert "trust_service_criteria" in result

    def test_soc2_trust_criteria_coverage(self):
        """Test SOC 2 check covers trust service criteria."""
        result = check_soc2_compliance("test_application")

        criteria = result["trust_service_criteria"]
        expected_criteria = ["security", "availability", "confidentiality"]

        for criterion in expected_criteria:
            assert criterion in criteria

    def test_soc2_common_criteria(self):
        """Test SOC 2 includes Common Criteria controls."""
        result = check_soc2_compliance("test_application")

        security_controls = result["trust_service_criteria"]["security"]["controls"]

        expected_controls = [
            "CC1_control_environment",
            "CC2_communication",
            "CC3_risk_assessment",
            "CC6_logical_access",
            "CC8_change_management"
        ]

        for control in expected_controls:
            assert control in security_controls

    def test_soc2_control_gaps(self):
        """Test SOC 2 identifies control gaps."""
        result = check_soc2_compliance("test_application")

        assert "control_gaps" in result
        for gap in result["control_gaps"]:
            assert "control" in gap
            assert "gap" in gap
            assert "remediation" in gap
            assert "priority" in gap

    def test_soc2_audit_readiness(self):
        """Test SOC 2 summary includes audit readiness."""
        result = check_soc2_compliance("test_application")

        summary = result["summary"]
        assert "audit_readiness" in summary
        assert summary["audit_readiness"] in ["low", "medium", "high"]


class TestPCIDSSCompliance:
    """Test PCI-DSS compliance checking."""

    def test_check_pci_dss_success(self):
        """Test successful PCI-DSS compliance check."""
        result = check_pci_dss_compliance("test_application")

        assert result["status"] == "success"
        assert "pci_dss_assessment" in result
        assert "requirements" in result

    def test_pci_dss_requirements_coverage(self):
        """Test PCI-DSS check covers all 12 requirements."""
        result = check_pci_dss_compliance("test_application")

        requirements = result["requirements"]

        expected_requirement_groups = [
            "build_maintain_secure_network",
            "protect_cardholder_data",
            "maintain_vulnerability_management",
            "implement_access_control",
            "monitor_test_networks",
            "maintain_information_security"
        ]

        for req_group in expected_requirement_groups:
            assert req_group in requirements

    def test_pci_dss_protect_cardholder_data(self):
        """Test PCI-DSS evaluates cardholder data protection."""
        result = check_pci_dss_compliance("test_application")

        protect_data = result["requirements"]["protect_cardholder_data"]
        assert "req_3_data_protection" in protect_data
        assert "req_4_encryption_transmission" in protect_data

    def test_pci_dss_critical_gaps(self):
        """Test PCI-DSS identifies critical gaps."""
        result = check_pci_dss_compliance("test_application")

        assert "critical_gaps" in result
        assert len(result["critical_gaps"]) >= 0

    def test_pci_dss_certification_readiness(self):
        """Test PCI-DSS summary includes certification readiness."""
        result = check_pci_dss_compliance("test_application")

        summary = result["summary"]
        assert "certification_readiness" in summary
        assert summary["certification_readiness"] in ["ready", "not_ready", "needs_improvement"]


class TestComplianceRecommendations:
    """Test compliance recommendation generation."""

    def test_generate_recommendations_success(self):
        """Test successful recommendation generation."""
        gdpr_results = {"summary": {}}
        hipaa_results = {"summary": {}}
        soc2_results = {"summary": {}}
        pci_dss_results = {"summary": {}}

        result = generate_compliance_recommendations(
            gdpr_results,
            hipaa_results,
            soc2_results,
            pci_dss_results
        )

        assert result["status"] == "success"
        assert "recommendations" in result

    def test_recommendations_prioritized(self):
        """Test recommendations are properly prioritized."""
        gdpr_results = {"summary": {}}
        hipaa_results = {"summary": {}}

        result = generate_compliance_recommendations(
            gdpr_results=gdpr_results,
            hipaa_results=hipaa_results
        )

        for rec in result["recommendations"]:
            assert "priority" in rec
            assert rec["priority"] in ["critical", "high", "medium", "low"]

    def test_recommendation_details(self):
        """Test recommendations include all required details."""
        gdpr_results = {"summary": {}}

        result = generate_compliance_recommendations(gdpr_results=gdpr_results)

        for rec in result["recommendations"]:
            assert "standard" in rec
            assert "requirement" in rec
            assert "issue" in rec
            assert "recommendation" in rec
            assert "remediation_steps" in rec
            assert "estimated_effort" in rec
            assert "compliance_impact" in rec

    def test_regulatory_risk_documented(self):
        """Test recommendations document regulatory risk."""
        gdpr_results = {"summary": {}}
        pci_dss_results = {"summary": {}}

        result = generate_compliance_recommendations(
            gdpr_results=gdpr_results,
            pci_dss_results=pci_dss_results
        )

        for rec in result["recommendations"]:
            if rec["priority"] in ["critical", "high"]:
                assert "regulatory_risk" in rec

    def test_quick_wins(self):
        """Test recommendations include quick wins."""
        gdpr_results = {"summary": {}}

        result = generate_compliance_recommendations(gdpr_results=gdpr_results)

        assert "quick_wins" in result
        assert len(result["quick_wins"]) > 0


class TestComplianceReporting:
    """Test compliance report generation."""

    def test_generate_report_success(self):
        """Test successful report generation."""
        gdpr_results = {"summary": {"compliance_score": 0}}
        hipaa_results = {"summary": {"compliance_score": 0}}
        soc2_results = {"summary": {"compliance_score": 0}}
        pci_dss_results = {"summary": {"compliance_score": 0}}
        recommendations = {"recommendations": []}

        result = generate_compliance_report(
            gdpr_results,
            hipaa_results,
            soc2_results,
            pci_dss_results,
            recommendations
        )

        assert result["status"] == "success"
        assert "compliance_report" in result

    def test_report_summary(self):
        """Test report includes comprehensive summary."""
        gdpr_results = {"summary": {"compliance_score": 0}}
        recommendations = {"recommendations": []}

        result = generate_compliance_report(
            gdpr_results=gdpr_results,
            recommendations=recommendations
        )

        summary = result["compliance_report"]["summary"]
        assert "audit_date" in summary
        assert "standards_assessed" in summary
        assert "overall_compliance_grade" in summary
        assert "certification_readiness" in summary

    def test_standards_summary(self):
        """Test report includes per-standard summary."""
        gdpr_results = {"summary": {"compliance_score": 45, "risk_level": "high"}}
        hipaa_results = {"summary": {"compliance_score": 56, "risk_level": "high"}}

        result = generate_compliance_report(
            gdpr_results=gdpr_results,
            hipaa_results=hipaa_results
        )

        standards = result["compliance_report"]["standards_summary"]
        assert "gdpr" in standards
        assert "hipaa" in standards

        assert standards["gdpr"]["compliance_score"] == 45
        assert standards["hipaa"]["compliance_score"] == 56

    def test_critical_gaps_highlighted(self):
        """Test report highlights critical compliance gaps."""
        gdpr_results = {"summary": {"compliance_score": 0}}
        recommendations = {"recommendations": []}

        result = generate_compliance_report(
            gdpr_results=gdpr_results,
            recommendations=recommendations
        )

        report = result["compliance_report"]
        assert "critical_gaps" in report
        assert len(report["critical_gaps"]) >= 0

    def test_regulatory_risk_assessment(self):
        """Test report includes regulatory risk assessment."""
        gdpr_results = {"summary": {"compliance_score": 0}}

        result = generate_compliance_report(gdpr_results=gdpr_results)

        report = result["compliance_report"]
        assert "regulatory_risk" in report

        risk = report["regulatory_risk"]
        if "gdpr_max_fine" in risk:
            assert "€" in risk["gdpr_max_fine"]

    def test_validation_result(self):
        """Test report includes validation decision."""
        gdpr_results = {"summary": {"compliance_score": 0}}

        result = generate_compliance_report(gdpr_results=gdpr_results)

        report = result["compliance_report"]
        assert "validation_result" in report
        assert report["validation_result"] in ["approved", "rejected", "conditional"]

    def test_required_actions(self):
        """Test report includes required actions."""
        gdpr_results = {"summary": {"compliance_score": 0}}
        recommendations = {"recommendations": []}

        result = generate_compliance_report(
            gdpr_results=gdpr_results,
            recommendations=recommendations
        )

        report = result["compliance_report"]
        assert "required_actions" in report
        assert len(report["required_actions"]) > 0


class TestComplianceAgent:
    """Test agent integration."""

    def test_agent_exists(self):
        """Test that agent is properly defined."""
        assert compliance_agent is not None
        assert compliance_agent.name == "compliance_agent"

    def test_agent_has_tools(self):
        """Test that agent has all required tools."""
        expected_tools = [
            "check_gdpr_compliance",
            "check_hipaa_compliance",
            "check_soc2_compliance",
            "check_pci_dss_compliance",
            "generate_compliance_recommendations",
            "generate_compliance_report"
        ]

        tool_names = [tool.__name__ for tool in compliance_agent.tools]
        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    def test_agent_description(self):
        """Test agent has proper description."""
        assert compliance_agent.description is not None
        assert "compliance" in compliance_agent.description.lower()
        assert "regulatory" in compliance_agent.description.lower()

    def test_agent_instruction_covers_standards(self):
        """Test agent instruction covers compliance standards."""
        assert compliance_agent.instruction is not None
        instruction_lower = compliance_agent.instruction.lower()

        assert "gdpr" in instruction_lower
        assert "hipaa" in instruction_lower
        assert "soc 2" in instruction_lower or "soc2" in instruction_lower
        assert "pci" in instruction_lower or "pci-dss" in instruction_lower


class TestCrossStandardValidation:
    """Test validation across multiple standards."""

    def test_common_requirements_identified(self):
        """Test that common requirements across standards are identified."""
        # For example, encryption is required by multiple standards
        hipaa_result = check_hipaa_compliance("test_app")
        pci_result = check_pci_dss_compliance("test_app")

        # Both should have encryption requirements
        hipaa_encryption = hipaa_result["compliance_checks"]["technical_safeguards"]["requirements"]["encryption"]
        pci_encryption = pci_result["requirements"]["protect_cardholder_data"]["req_4_encryption_transmission"]

        assert hipaa_encryption["status"] == "compliant"
        assert pci_encryption["status"] == "compliant"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
