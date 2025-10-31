"""
tests/quality_agents/test_security_auditor.py

Unit tests for Security Auditor Agent.
"""

import pytest
from agents.quality.security_auditor.agent import (
    security_auditor_agent,
    AGENT_CAPABILITY,
    scan_vulnerabilities,
    perform_penetration_test,
    analyze_code_security,
    check_dependency_vulnerabilities,
    generate_security_recommendations,
    generate_security_report
)
from shared.models.agent_capability import AgentType, InputModality


class TestSecurityAuditorAgentCapability:
    """Test agent capability declaration."""

    def test_agent_capability_exists(self):
        """Test that agent capability is properly defined."""
        assert AGENT_CAPABILITY is not None
        assert AGENT_CAPABILITY.agent_id == "security_auditor_agent"
        assert AGENT_CAPABILITY.agent_name == "Security Auditor Agent"
        assert AGENT_CAPABILITY.agent_type == AgentType.SECURITY_ENGINEER

    def test_agent_capabilities(self):
        """Test that agent has correct capabilities."""
        expected_capabilities = {
            "vulnerability_scanning",
            "penetration_testing",
            "sast_analysis",
            "dependency_scanning",
            "security_auditing"
        }
        assert expected_capabilities.issubset(AGENT_CAPABILITY.capabilities)

    def test_agent_compliance_standards(self):
        """Test that agent supports compliance standards."""
        expected_standards = ["OWASP Top 10", "CWE Top 25"]
        for standard in expected_standards:
            assert standard in AGENT_CAPABILITY.compliance_standards


class TestVulnerabilityScanning:
    """Test vulnerability scanning functionality."""

    def test_scan_vulnerabilities_success(self):
        """Test successful vulnerability scan."""
        result = scan_vulnerabilities("https://api.example.com")

        assert result["status"] == "success"
        assert "scan_execution" in result
        assert "vulnerabilities" in result
        assert "summary" in result

    def test_scan_with_type(self):
        """Test scan with different scan types."""
        for scan_type in ["quick", "comprehensive", "deep"]:
            result = scan_vulnerabilities(
                "https://api.example.com",
                scan_type=scan_type
            )
            assert result["status"] == "success"
            assert result["scan_execution"]["scan_type"] == scan_type

    def test_vulnerability_details(self):
        """Test vulnerability includes all required details."""
        result = scan_vulnerabilities("https://api.example.com")

        for vuln in result["vulnerabilities"]:
            assert "id" in vuln
            assert "severity" in vuln
            assert "category" in vuln
            assert "cwe_id" in vuln
            assert "cvss_score" in vuln
            assert "description" in vuln
            assert "exploitability" in vuln

    def test_vulnerability_severity_levels(self):
        """Test vulnerabilities have valid severity levels."""
        result = scan_vulnerabilities("https://api.example.com")

        valid_severities = ["critical", "high", "medium", "low", "informational"]
        for vuln in result["vulnerabilities"]:
            assert vuln["severity"] in valid_severities

    def test_scan_summary(self):
        """Test scan summary includes counts by severity."""
        result = scan_vulnerabilities("https://api.example.com")

        summary = result["summary"]
        assert "total_vulnerabilities" in summary
        assert "critical" in summary
        assert "high" in summary
        assert "medium" in summary
        assert "low" in summary


class TestPenetrationTesting:
    """Test penetration testing functionality."""

    def test_perform_pentest_success(self):
        """Test successful penetration test."""
        target = "https://api.example.com"
        scope = ["/api/orders", "/api/users"]
        authorization = {"approved": True, "scope": "full"}

        result = perform_penetration_test(target, scope, authorization)

        assert result["status"] == "success"
        assert "pentest_execution" in result
        assert "test_results" in result

    def test_pentest_categories(self):
        """Test penetration test covers all major categories."""
        target = "https://api.example.com"
        scope = ["/api/*"]
        authorization = {"approved": True}

        result = perform_penetration_test(target, scope, authorization)

        test_results = result["test_results"]
        expected_categories = [
            "authentication_tests",
            "authorization_tests",
            "injection_tests",
            "data_exposure_tests"
        ]

        for category in expected_categories:
            assert category in test_results

    def test_pentest_findings_structure(self):
        """Test penetration test findings have proper structure."""
        target = "https://api.example.com"
        scope = ["/api/*"]
        authorization = {"approved": True}

        result = perform_penetration_test(target, scope, authorization)

        auth_tests = result["test_results"]["authentication_tests"]
        for finding in auth_tests["findings"]:
            assert "test" in finding
            assert "status" in finding
            assert "description" in finding
            assert "severity" in finding

    def test_pentest_summary(self):
        """Test penetration test includes summary."""
        target = "https://api.example.com"
        scope = ["/api/*"]
        authorization = {"approved": True}

        result = perform_penetration_test(target, scope, authorization)

        summary = result["summary"]
        assert "total_tests" in summary
        assert "passed" in summary
        assert "failed" in summary
        assert "critical_findings" in summary


class TestCodeSecurityAnalysis:
    """Test static code security analysis."""

    def test_analyze_code_success(self):
        """Test successful code analysis."""
        result = analyze_code_security("/path/to/codebase")

        assert result["status"] == "success"
        assert "analysis" in result
        assert "security_issues" in result

    def test_code_analysis_languages(self):
        """Test code analysis supports multiple languages."""
        languages = ["python", "javascript"]
        result = analyze_code_security("/path/to/codebase", languages)

        assert result["status"] == "success"
        assert result["analysis"]["languages_analyzed"] == languages

    def test_security_issue_details(self):
        """Test security issues have required details."""
        result = analyze_code_security("/path/to/codebase")

        for issue in result["security_issues"]:
            assert "id" in issue
            assert "severity" in issue
            assert "category" in issue
            assert "file" in issue
            assert "line" in issue
            assert "code" in issue
            assert "description" in issue
            assert "cwe_id" in issue

    def test_best_practices_violations(self):
        """Test analysis includes best practices violations."""
        result = analyze_code_security("/path/to/codebase")

        assert "best_practices_violations" in result
        for violation in result["best_practices_violations"]:
            assert "category" in violation
            assert "count" in violation
            assert "description" in violation

    def test_security_score(self):
        """Test analysis includes security score."""
        result = analyze_code_security("/path/to/codebase")

        summary = result["summary"]
        assert "security_score" in summary
        assert 0 <= summary["security_score"] <= 100


class TestDependencyScanning:
    """Test dependency vulnerability scanning."""

    def test_check_dependencies_success(self):
        """Test successful dependency scan."""
        result = check_dependency_vulnerabilities(
            "requirements.txt",
            package_manager="pip"
        )

        assert result["status"] == "success"
        assert "scan" in result
        assert "vulnerable_packages" in result

    def test_vulnerable_package_details(self):
        """Test vulnerable packages have CVE details."""
        result = check_dependency_vulnerabilities("requirements.txt")

        for package in result["vulnerable_packages"]:
            assert "package" in package
            assert "current_version" in package
            assert "fixed_version" in package
            assert "severity" in package
            assert "cve_ids" in package
            assert "cvss_score" in package
            assert "fix_available" in package

    def test_license_issues(self):
        """Test scan includes license issues."""
        result = check_dependency_vulnerabilities("requirements.txt")

        assert "license_issues" in result
        for issue in result["license_issues"]:
            assert "package" in issue
            assert "license" in issue
            assert "severity" in issue

    def test_dependency_summary(self):
        """Test scan includes summary statistics."""
        result = check_dependency_vulnerabilities("requirements.txt")

        summary = result["summary"]
        assert "total_vulnerabilities" in summary
        assert "critical" in summary
        assert "high" in summary
        assert "fixable" in summary


class TestSecurityRecommendations:
    """Test security recommendation generation."""

    def test_generate_recommendations_success(self):
        """Test successful recommendation generation."""
        vulnerabilities = {"vulnerabilities": [], "summary": {}}
        pentest_results = {"test_results": {}, "summary": {}}
        code_analysis = {"security_issues": [], "summary": {}}
        dependency_scan = {"vulnerable_packages": [], "summary": {}}

        result = generate_security_recommendations(
            vulnerabilities,
            pentest_results,
            code_analysis,
            dependency_scan
        )

        assert result["status"] == "success"
        assert "recommendations" in result

    def test_recommendations_prioritized(self):
        """Test recommendations are properly prioritized."""
        vulnerabilities = {"vulnerabilities": [], "summary": {}}
        pentest_results = {"test_results": {}, "summary": {}}
        code_analysis = {"security_issues": [], "summary": {}}
        dependency_scan = {"vulnerable_packages": [], "summary": {}}

        result = generate_security_recommendations(
            vulnerabilities,
            pentest_results,
            code_analysis,
            dependency_scan
        )

        for rec in result["recommendations"]:
            assert "priority" in rec
            assert rec["priority"] in ["critical", "high", "medium", "low"]

    def test_recommendation_details(self):
        """Test recommendations include all required details."""
        vulnerabilities = {"vulnerabilities": [], "summary": {}}
        pentest_results = {"test_results": {}, "summary": {}}
        code_analysis = {"security_issues": [], "summary": {}}
        dependency_scan = {"vulnerable_packages": [], "summary": {}}

        result = generate_security_recommendations(
            vulnerabilities,
            pentest_results,
            code_analysis,
            dependency_scan
        )

        for rec in result["recommendations"]:
            assert "category" in rec
            assert "issue" in rec
            assert "recommendation" in rec
            assert "remediation_steps" in rec
            assert "estimated_effort" in rec
            assert "business_impact" in rec

    def test_code_examples(self):
        """Test recommendations include code examples."""
        vulnerabilities = {"vulnerabilities": [], "summary": {}}
        pentest_results = {"test_results": {}, "summary": {}}
        code_analysis = {"security_issues": [], "summary": {}}
        dependency_scan = {"vulnerable_packages": [], "summary": {}}

        result = generate_security_recommendations(
            vulnerabilities,
            pentest_results,
            code_analysis,
            dependency_scan
        )

        # At least some recommendations should have code examples
        has_code_examples = any(
            "code_example" in rec
            for rec in result["recommendations"]
        )
        assert has_code_examples

    def test_quick_wins(self):
        """Test recommendations include quick wins."""
        vulnerabilities = {"vulnerabilities": [], "summary": {}}
        pentest_results = {"test_results": {}, "summary": {}}
        code_analysis = {"security_issues": [], "summary": {}}
        dependency_scan = {"vulnerable_packages": [], "summary": {}}

        result = generate_security_recommendations(
            vulnerabilities,
            pentest_results,
            code_analysis,
            dependency_scan
        )

        assert "quick_wins" in result
        assert len(result["quick_wins"]) > 0


class TestSecurityReporting:
    """Test security report generation."""

    def test_generate_report_success(self):
        """Test successful report generation."""
        vulnerabilities = {"summary": {}}
        pentest_results = {"summary": {}}
        code_analysis = {"summary": {}}
        dependency_scan = {"vulnerable_packages": [], "summary": {}}
        recommendations = {"recommendations": []}

        result = generate_security_report(
            vulnerabilities,
            pentest_results,
            code_analysis,
            dependency_scan,
            recommendations
        )

        assert result["status"] == "success"
        assert "security_report" in result

    def test_report_summary(self):
        """Test report includes comprehensive summary."""
        vulnerabilities = {"summary": {"critical": 0}}
        pentest_results = {"summary": {"total_tests": 0}}
        code_analysis = {"summary": {"security_score": 0}}
        dependency_scan = {"vulnerable_packages": [], "summary": {}}
        recommendations = {"recommendations": []}

        result = generate_security_report(
            vulnerabilities,
            pentest_results,
            code_analysis,
            dependency_scan,
            recommendations
        )

        summary = result["security_report"]["summary"]
        assert "overall_security_rating" in summary
        assert "risk_level" in summary
        assert "critical_issues" in summary
        assert "total_vulnerabilities" in summary

    def test_owasp_top_10_coverage(self):
        """Test report includes OWASP Top 10 findings."""
        vulnerabilities = {"summary": {}}
        pentest_results = {"summary": {}}
        code_analysis = {"summary": {}}
        dependency_scan = {"vulnerable_packages": [], "summary": {}}
        recommendations = {"recommendations": []}

        result = generate_security_report(
            vulnerabilities,
            pentest_results,
            code_analysis,
            dependency_scan,
            recommendations
        )

        report = result["security_report"]
        assert "owasp_top_10_findings" in report

        owasp_findings = report["owasp_top_10_findings"]
        assert "A01_Broken_Access_Control" in owasp_findings
        assert "A02_Cryptographic_Failures" in owasp_findings
        assert "A03_Injection" in owasp_findings

    def test_validation_result(self):
        """Test report includes validation decision."""
        vulnerabilities = {"summary": {}}
        pentest_results = {"summary": {}}
        code_analysis = {"summary": {}}
        dependency_scan = {"vulnerable_packages": [], "summary": {}}
        recommendations = {"recommendations": []}

        result = generate_security_report(
            vulnerabilities,
            pentest_results,
            code_analysis,
            dependency_scan,
            recommendations
        )

        report = result["security_report"]
        assert "validation_result" in report
        assert report["validation_result"] in ["approved", "rejected"]


class TestSecurityAuditorAgent:
    """Test agent integration."""

    def test_agent_exists(self):
        """Test that agent is properly defined."""
        assert security_auditor_agent is not None
        assert security_auditor_agent.name == "security_auditor_agent"

    def test_agent_has_tools(self):
        """Test that agent has all required tools."""
        expected_tools = [
            "scan_vulnerabilities",
            "perform_penetration_test",
            "analyze_code_security",
            "check_dependency_vulnerabilities",
            "generate_security_recommendations",
            "generate_security_report"
        ]

        tool_names = [tool.__name__ for tool in security_auditor_agent.tools]
        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    def test_agent_description(self):
        """Test agent has proper description."""
        assert security_auditor_agent.description is not None
        assert "security" in security_auditor_agent.description.lower()
        assert "vulnerability" in security_auditor_agent.description.lower()

    def test_agent_instruction_covers_owasp(self):
        """Test agent instruction covers OWASP Top 10."""
        assert security_auditor_agent.instruction is not None
        assert "owasp" in security_auditor_agent.instruction.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
