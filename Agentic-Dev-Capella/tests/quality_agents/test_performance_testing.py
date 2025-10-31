"""
tests/quality_agents/test_performance_testing.py

Unit tests for Performance Testing Agent.
"""

import pytest
from agents.quality.performance_testing.agent import (
    performance_testing_agent,
    AGENT_CAPABILITY,
    generate_load_test_script,
    execute_load_test,
    analyze_performance_bottlenecks,
    generate_performance_profile,
    run_benchmark_suite,
    generate_optimization_recommendations,
    generate_performance_report
)
from shared.models.agent_capability import AgentType, InputModality


class TestPerformanceTestingAgentCapability:
    """Test agent capability declaration."""

    def test_agent_capability_exists(self):
        """Test that agent capability is properly defined."""
        assert AGENT_CAPABILITY is not None
        assert AGENT_CAPABILITY.agent_id == "performance_testing_agent"
        assert AGENT_CAPABILITY.agent_name == "Performance Testing Agent"
        assert AGENT_CAPABILITY.agent_type == AgentType.PERFORMANCE_ENGINEER

    def test_agent_capabilities(self):
        """Test that agent has correct capabilities."""
        expected_capabilities = {
            "load_testing",
            "stress_testing",
            "performance_profiling",
            "bottleneck_analysis",
            "benchmark_generation"
        }
        assert expected_capabilities.issubset(AGENT_CAPABILITY.capabilities)

    def test_agent_input_modalities(self):
        """Test that agent supports correct input modalities."""
        assert InputModality.TEXT in AGENT_CAPABILITY.input_modalities
        assert InputModality.CODE in AGENT_CAPABILITY.input_modalities
        assert InputModality.API_SPEC in AGENT_CAPABILITY.input_modalities

    def test_agent_output_types(self):
        """Test that agent produces correct output types."""
        expected_outputs = {
            "load_test_script",
            "performance_report",
            "benchmark_results"
        }
        assert expected_outputs.issubset(AGENT_CAPABILITY.output_types)


class TestLoadTestGeneration:
    """Test load test script generation."""

    def test_generate_load_test_script_success(self):
        """Test successful load test script generation."""
        api_spec = {"endpoints": ["/api/orders", "/api/products"]}
        result = generate_load_test_script(api_spec)

        assert result["status"] == "success"
        assert "scripts" in result
        assert "k6_script" in result["scripts"]
        assert "jmeter_config" in result["scripts"]

    def test_generate_load_test_script_with_config(self):
        """Test load test generation with custom config."""
        api_spec = {"endpoints": ["/api/orders"]}
        test_config = {
            "virtual_users": 200,
            "duration_minutes": 15,
            "ramp_up_minutes": 3
        }
        result = generate_load_test_script(api_spec, test_config)

        assert result["status"] == "success"
        assert result["test_config"]["virtual_users"] == 200
        assert result["test_config"]["duration_minutes"] == 15

    def test_k6_script_structure(self):
        """Test k6 script has proper structure."""
        api_spec = {"endpoints": ["/api/test"]}
        result = generate_load_test_script(api_spec)

        k6_script = result["scripts"]["k6_script"]
        assert "filename" in k6_script
        assert "content" in k6_script
        assert "export let options" in k6_script["content"]
        assert "http.get" in k6_script["content"]


class TestLoadTestExecution:
    """Test load test execution."""

    def test_execute_load_test_success(self):
        """Test successful load test execution."""
        test_script = {"type": "k6", "filename": "test.js"}
        result = execute_load_test(test_script, "staging")

        assert result["status"] == "success"
        assert "test_execution" in result
        assert "metrics" in result
        assert result["test_execution"]["environment"] == "staging"

    def test_load_test_metrics(self):
        """Test load test returns proper metrics."""
        test_script = {"type": "k6"}
        result = execute_load_test(test_script)

        metrics = result["metrics"]
        assert "total_requests" in metrics
        assert "successful_requests" in metrics
        assert "failed_requests" in metrics
        assert "requests_per_second" in metrics
        assert "response_time_ms" in metrics
        assert "error_rate" in metrics

    def test_response_time_percentiles(self):
        """Test response time includes percentiles."""
        test_script = {"type": "k6"}
        result = execute_load_test(test_script)

        response_time = result["metrics"]["response_time_ms"]
        assert "average" in response_time
        assert "median" in response_time
        assert "p95" in response_time
        assert "p99" in response_time


class TestBottleneckAnalysis:
    """Test performance bottleneck analysis."""

    def test_analyze_bottlenecks_success(self):
        """Test successful bottleneck analysis."""
        test_results = {
            "metrics": {
                "response_time_ms": {"p95": 500, "p99": 1000}
            }
        }
        result = analyze_performance_bottlenecks(test_results)

        assert result["status"] == "success"
        assert "analysis" in result
        assert "bottlenecks" in result["analysis"]

    def test_bottleneck_severity_classification(self):
        """Test bottlenecks are classified by severity."""
        test_results = {"metrics": {}}
        result = analyze_performance_bottlenecks(test_results)

        bottlenecks = result["analysis"]["bottlenecks"]
        for bottleneck in bottlenecks:
            assert "severity" in bottleneck
            assert bottleneck["severity"] in ["high", "medium", "low"]

    def test_sla_compliance_check(self):
        """Test SLA compliance is evaluated."""
        test_results = {"metrics": {}}
        result = analyze_performance_bottlenecks(test_results)

        sla_compliance = result["analysis"]["sla_compliance"]
        assert "response_time_p95" in sla_compliance
        assert "response_time_p99" in sla_compliance
        assert "error_rate" in sla_compliance

        for metric, check in sla_compliance.items():
            assert "target" in check
            assert "actual" in check
            assert "status" in check


class TestPerformanceProfiling:
    """Test performance profiling."""

    def test_generate_profile_success(self):
        """Test successful performance profile generation."""
        result = generate_performance_profile("test_app")

        assert result["status"] == "success"
        assert "performance_profile" in result

    def test_profile_includes_resource_usage(self):
        """Test profile includes CPU, memory, and I/O usage."""
        result = generate_performance_profile("test_app")

        profile = result["performance_profile"]
        assert "cpu_usage" in profile
        assert "memory_usage" in profile
        assert "io_operations" in profile

    def test_hotspot_identification(self):
        """Test CPU hotspots are identified."""
        result = generate_performance_profile("test_app")

        cpu_usage = result["performance_profile"]["cpu_usage"]
        assert "hotspots" in cpu_usage
        assert len(cpu_usage["hotspots"]) > 0

        for hotspot in cpu_usage["hotspots"]:
            assert "function" in hotspot
            assert "file" in hotspot
            assert "cpu_percent" in hotspot


class TestBenchmarking:
    """Test benchmark suite execution."""

    def test_run_benchmark_success(self):
        """Test successful benchmark execution."""
        result = run_benchmark_suite("test_app")

        assert result["status"] == "success"
        assert "benchmarks" in result

    def test_benchmark_includes_endpoints(self):
        """Test benchmarks include API endpoint tests."""
        result = run_benchmark_suite("test_app")

        benchmarks = result["benchmarks"]
        assert "api_endpoints" in benchmarks
        assert len(benchmarks["api_endpoints"]) > 0

    def test_benchmark_comparison(self):
        """Test benchmark includes version comparison."""
        result = run_benchmark_suite("test_app")

        comparison = result["benchmarks"]["comparison"]
        assert "baseline_version" in comparison
        assert "current_version" in comparison
        assert "performance_change" in comparison


class TestOptimizationRecommendations:
    """Test optimization recommendation generation."""

    def test_generate_recommendations_success(self):
        """Test successful recommendation generation."""
        bottlenecks = {"analysis": {"bottlenecks": []}}
        profile = {"performance_profile": {}}
        benchmarks = {"benchmarks": {}}

        result = generate_optimization_recommendations(
            bottlenecks, profile, benchmarks
        )

        assert result["status"] == "success"
        assert "recommendations" in result

    def test_recommendations_prioritized(self):
        """Test recommendations are prioritized."""
        bottlenecks = {"analysis": {"bottlenecks": []}}
        profile = {"performance_profile": {}}
        benchmarks = {"benchmarks": {}}

        result = generate_optimization_recommendations(
            bottlenecks, profile, benchmarks
        )

        for rec in result["recommendations"]:
            assert "priority" in rec
            assert rec["priority"] in ["high", "medium", "low"]

    def test_recommendations_include_steps(self):
        """Test recommendations include implementation steps."""
        bottlenecks = {"analysis": {"bottlenecks": []}}
        profile = {"performance_profile": {}}
        benchmarks = {"benchmarks": {}}

        result = generate_optimization_recommendations(
            bottlenecks, profile, benchmarks
        )

        for rec in result["recommendations"]:
            assert "recommendation" in rec
            assert "implementation_steps" in rec
            assert "expected_improvement" in rec
            assert "effort" in rec


class TestPerformanceReporting:
    """Test performance report generation."""

    def test_generate_report_success(self):
        """Test successful report generation."""
        load_test = {"test_execution": {}, "metrics": {}}
        bottlenecks = {"analysis": {"bottlenecks": []}}
        profile = {"performance_profile": {}}
        benchmarks = {"benchmarks": {}}
        recommendations = {"recommendations": []}

        result = generate_performance_report(
            load_test, bottlenecks, profile, benchmarks, recommendations
        )

        assert result["status"] == "success"
        assert "performance_report" in result

    def test_report_includes_summary(self):
        """Test report includes executive summary."""
        load_test = {"test_execution": {}, "metrics": {"response_time_ms": {}}}
        bottlenecks = {"analysis": {"bottlenecks": []}}
        profile = {"performance_profile": {}}
        benchmarks = {"benchmarks": {}}
        recommendations = {"recommendations": []}

        result = generate_performance_report(
            load_test, bottlenecks, profile, benchmarks, recommendations
        )

        summary = result["performance_report"]["summary"]
        assert "overall_rating" in summary
        assert "sla_compliance" in summary
        assert "critical_issues" in summary

    def test_report_includes_validation_result(self):
        """Test report includes validation decision."""
        load_test = {"test_execution": {}, "metrics": {}}
        bottlenecks = {"analysis": {"bottlenecks": []}}
        profile = {"performance_profile": {}}
        benchmarks = {"benchmarks": {}}
        recommendations = {"recommendations": []}

        result = generate_performance_report(
            load_test, bottlenecks, profile, benchmarks, recommendations
        )

        report = result["performance_report"]
        assert "validation_result" in report
        assert report["validation_result"] in [
            "approved",
            "approved_with_recommendations",
            "rejected"
        ]


class TestPerformanceTestingAgent:
    """Test agent integration."""

    def test_agent_exists(self):
        """Test that agent is properly defined."""
        assert performance_testing_agent is not None
        assert performance_testing_agent.name == "performance_testing_agent"

    def test_agent_has_tools(self):
        """Test that agent has all required tools."""
        expected_tools = [
            "generate_load_test_script",
            "execute_load_test",
            "analyze_performance_bottlenecks",
            "generate_performance_profile",
            "run_benchmark_suite",
            "generate_optimization_recommendations",
            "generate_performance_report"
        ]

        tool_names = [tool.__name__ for tool in performance_testing_agent.tools]
        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    def test_agent_description(self):
        """Test agent has proper description."""
        assert performance_testing_agent.description is not None
        assert len(performance_testing_agent.description) > 0
        assert "performance" in performance_testing_agent.description.lower()

    def test_agent_instruction(self):
        """Test agent has proper instruction."""
        assert performance_testing_agent.instruction is not None
        assert "load test" in performance_testing_agent.instruction.lower()
        assert "sla" in performance_testing_agent.instruction.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
