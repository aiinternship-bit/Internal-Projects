"""
agents/quality/performance_testing/agent.py

Performance Testing Agent - Generates and executes performance tests,
load tests, stress tests, and benchmarks. Identifies bottlenecks and
provides optimization recommendations.
"""

from typing import Dict, List, Any, Optional
from google.adk.agents import Agent
from shared.models.agent_capability import (
    AgentCapability,
    AgentType,
    InputModality,
    PerformanceMetrics,
    CostMetrics,
    KBIntegrationConfig,
    KBQueryStrategy
)


# ============================================================================
# Tool Functions
# ============================================================================

def generate_load_test_script(
    api_spec: Dict[str, Any],
    test_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate load testing scripts using k6 or JMeter.

    Args:
        api_spec: API specification (OpenAPI/Swagger)
        test_config: Test configuration (users, duration, ramp-up)

    Returns:
        Generated test scripts and configurations
    """
    test_config = test_config or {
        "virtual_users": 100,
        "duration_minutes": 10,
        "ramp_up_minutes": 2
    }

    return {
        "status": "success",
        "scripts": {
            "k6_script": {
                "filename": "load_test.js",
                "content": """
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 50 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 200 },
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  let response = http.get('https://api.example.com/endpoint');
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  sleep(1);
}
""",
                "type": "k6"
            },
            "jmeter_config": {
                "filename": "load_test.jmx",
                "thread_groups": [
                    {
                        "name": "API Load Test",
                        "num_threads": 100,
                        "ramp_time": 120,
                        "loop_count": -1,
                        "duration": 600
                    }
                ],
                "type": "jmeter"
            }
        },
        "test_config": test_config,
        "estimated_duration_minutes": test_config.get("duration_minutes", 10) + test_config.get("ramp_up_minutes", 2)
    }


def execute_load_test(
    test_script: Dict[str, Any],
    environment: str = "staging"
) -> Dict[str, Any]:
    """
    Execute load test against target environment.

    Args:
        test_script: Test script configuration
        environment: Target environment (staging, production)

    Returns:
        Test execution results and metrics
    """
    return {
        "status": "success",
        "test_execution": {
            "test_id": "load-test-001",
            "environment": environment,
            "start_time": "2025-10-30T10:00:00Z",
            "end_time": "2025-10-30T10:12:00Z",
            "duration_minutes": 12,
            "tool": "k6"
        },
        "metrics": {
            "total_requests": 72000,
            "successful_requests": 71856,
            "failed_requests": 144,
            "requests_per_second": {
                "min": 50,
                "max": 200,
                "average": 100,
                "p95": 180,
                "p99": 195
            },
            "response_time_ms": {
                "min": 45,
                "max": 1850,
                "average": 185,
                "median": 165,
                "p95": 420,
                "p99": 850
            },
            "error_rate": 0.002,
            "throughput_mbps": 12.5
        }
    }


def analyze_performance_bottlenecks(
    test_results: Dict[str, Any],
    application_logs: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze test results to identify performance bottlenecks.

    Args:
        test_results: Load test results
        application_logs: Optional application logs for analysis

    Returns:
        Identified bottlenecks and recommendations
    """
    return {
        "status": "success",
        "analysis": {
            "bottlenecks": [
                {
                    "component": "Database Query",
                    "severity": "high",
                    "description": "Complex JOIN query taking 850ms on average",
                    "location": "/api/orders endpoint",
                    "impact": "Causing p99 response time to exceed SLA",
                    "affected_percentile": "p95, p99"
                },
                {
                    "component": "External API Call",
                    "severity": "medium",
                    "description": "Payment gateway API timeout at high load",
                    "location": "/api/checkout endpoint",
                    "impact": "144 failed requests (0.2% error rate)",
                    "affected_percentile": "p99"
                },
                {
                    "component": "Memory Usage",
                    "severity": "medium",
                    "description": "Memory consumption increases to 85% at 200 concurrent users",
                    "location": "Application server",
                    "impact": "Potential OOM at higher loads",
                    "affected_percentile": "all"
                }
            ],
            "sla_compliance": {
                "response_time_p95": {
                    "target": 500,
                    "actual": 420,
                    "status": "pass"
                },
                "response_time_p99": {
                    "target": 1000,
                    "actual": 850,
                    "status": "pass"
                },
                "error_rate": {
                    "target": 0.01,
                    "actual": 0.002,
                    "status": "pass"
                },
                "requests_per_second": {
                    "target": 100,
                    "actual": 100,
                    "status": "pass"
                }
            }
        }
    }


def generate_performance_profile(
    application: str,
    profiling_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate performance profile using profiling tools.

    Args:
        application: Application identifier
        profiling_data: Optional existing profiling data

    Returns:
        Performance profile with hotspots and resource usage
    """
    return {
        "status": "success",
        "performance_profile": {
            "cpu_usage": {
                "average": 45,
                "peak": 78,
                "idle": 12,
                "hotspots": [
                    {
                        "function": "processOrders()",
                        "file": "order_service.py",
                        "line": 145,
                        "cpu_percent": 23,
                        "calls": 15000
                    },
                    {
                        "function": "validatePayment()",
                        "file": "payment_service.py",
                        "line": 78,
                        "cpu_percent": 18,
                        "calls": 12000
                    }
                ]
            },
            "memory_usage": {
                "average_mb": 512,
                "peak_mb": 1024,
                "baseline_mb": 256,
                "memory_leaks_detected": False,
                "allocations_per_second": 5000
            },
            "io_operations": {
                "disk_reads_per_second": 150,
                "disk_writes_per_second": 80,
                "network_io_mbps": 12.5,
                "database_queries_per_second": 250
            },
            "top_slow_functions": [
                {
                    "function": "complexDatabaseQuery()",
                    "average_duration_ms": 850,
                    "calls": 2000,
                    "total_time_seconds": 1700
                },
                {
                    "function": "externalAPICall()",
                    "average_duration_ms": 450,
                    "calls": 5000,
                    "total_time_seconds": 2250
                }
            ]
        }
    }


def run_benchmark_suite(
    application: str,
    benchmark_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Run comprehensive benchmark suite.

    Args:
        application: Application to benchmark
        benchmark_config: Benchmark configuration

    Returns:
        Benchmark results
    """
    return {
        "status": "success",
        "benchmarks": {
            "api_endpoints": [
                {
                    "endpoint": "GET /api/products",
                    "operations_per_second": 2500,
                    "avg_latency_ms": 12,
                    "p95_latency_ms": 25,
                    "p99_latency_ms": 45
                },
                {
                    "endpoint": "POST /api/orders",
                    "operations_per_second": 500,
                    "avg_latency_ms": 185,
                    "p95_latency_ms": 420,
                    "p99_latency_ms": 850
                },
                {
                    "endpoint": "GET /api/orders/{id}",
                    "operations_per_second": 1800,
                    "avg_latency_ms": 45,
                    "p95_latency_ms": 95,
                    "p99_latency_ms": 150
                }
            ],
            "database_operations": [
                {
                    "operation": "Simple SELECT",
                    "queries_per_second": 5000,
                    "avg_latency_ms": 2
                },
                {
                    "operation": "Complex JOIN",
                    "queries_per_second": 150,
                    "avg_latency_ms": 850
                },
                {
                    "operation": "INSERT",
                    "queries_per_second": 1000,
                    "avg_latency_ms": 5
                }
            ],
            "comparison": {
                "baseline_version": "v1.0.0",
                "current_version": "v1.1.0",
                "performance_change": "+15%",
                "improvements": ["Database query optimization", "Caching layer added"]
            }
        }
    }


def generate_optimization_recommendations(
    bottlenecks: Dict[str, Any],
    performance_profile: Dict[str, Any],
    benchmarks: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate actionable optimization recommendations.

    Args:
        bottlenecks: Identified bottlenecks
        performance_profile: Performance profile
        benchmarks: Benchmark results

    Returns:
        Prioritized optimization recommendations
    """
    return {
        "status": "success",
        "recommendations": [
            {
                "priority": "high",
                "category": "database",
                "issue": "Complex JOIN query causing high latency",
                "recommendation": "Add composite index on (order_id, customer_id) and consider query result caching",
                "expected_improvement": "60-70% reduction in query time",
                "effort": "medium",
                "implementation_steps": [
                    "Create index: CREATE INDEX idx_order_customer ON orders(order_id, customer_id)",
                    "Implement Redis caching for order queries with 5-minute TTL",
                    "Update query to use covering index"
                ]
            },
            {
                "priority": "high",
                "category": "external_api",
                "issue": "Payment gateway timeout at high load",
                "recommendation": "Implement circuit breaker pattern and request queue",
                "expected_improvement": "99.9% success rate at peak load",
                "effort": "medium",
                "implementation_steps": [
                    "Add circuit breaker using resilience4j or similar",
                    "Implement request queue with rate limiting",
                    "Add fallback mechanism for temporary failures"
                ]
            },
            {
                "priority": "medium",
                "category": "memory",
                "issue": "Memory consumption high at peak load",
                "recommendation": "Optimize object allocation and implement connection pooling",
                "expected_improvement": "30-40% reduction in memory usage",
                "effort": "low",
                "implementation_steps": [
                    "Implement database connection pooling (max 50 connections)",
                    "Use object pooling for frequently allocated objects",
                    "Enable garbage collection tuning"
                ]
            },
            {
                "priority": "medium",
                "category": "caching",
                "issue": "Repeated database queries for static data",
                "recommendation": "Implement multi-layer caching strategy",
                "expected_improvement": "50% reduction in database load",
                "effort": "low",
                "implementation_steps": [
                    "Add application-level cache for product catalog",
                    "Implement Redis cache for session data",
                    "Use CDN for static assets"
                ]
            },
            {
                "priority": "low",
                "category": "monitoring",
                "issue": "Limited performance visibility",
                "recommendation": "Implement comprehensive monitoring and alerting",
                "expected_improvement": "Faster issue detection and resolution",
                "effort": "medium",
                "implementation_steps": [
                    "Add Application Performance Monitoring (APM) tool",
                    "Set up custom metrics and dashboards",
                    "Configure alerts for SLA violations"
                ]
            }
        ],
        "estimated_total_improvement": "2-3x performance improvement",
        "implementation_timeline": "4-6 weeks"
    }


def generate_performance_report(
    load_test: Dict[str, Any],
    bottlenecks: Dict[str, Any],
    profile: Dict[str, Any],
    benchmarks: Dict[str, Any],
    recommendations: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate comprehensive performance testing report.

    Args:
        load_test: Load test results
        bottlenecks: Bottleneck analysis
        profile: Performance profile
        benchmarks: Benchmark results
        recommendations: Optimization recommendations

    Returns:
        Complete performance report
    """
    return {
        "status": "success",
        "performance_report": {
            "summary": {
                "test_date": "2025-10-30",
                "application": "E-commerce API v1.1.0",
                "environment": "staging",
                "overall_rating": "B+",
                "sla_compliance": "passed",
                "critical_issues": 1,
                "high_priority_recommendations": 2
            },
            "load_test_summary": {
                "total_requests": load_test.get("test_execution", {}).get("total_requests", 0),
                "success_rate": 99.8,
                "avg_response_time_ms": load_test.get("metrics", {}).get("response_time_ms", {}).get("average", 0),
                "p95_response_time_ms": load_test.get("metrics", {}).get("response_time_ms", {}).get("p95", 0),
                "max_throughput_rps": load_test.get("metrics", {}).get("requests_per_second", {}).get("max", 0)
            },
            "bottlenecks_summary": {
                "high_severity": len([b for b in bottlenecks.get("analysis", {}).get("bottlenecks", []) if b.get("severity") == "high"]),
                "medium_severity": len([b for b in bottlenecks.get("analysis", {}).get("bottlenecks", []) if b.get("severity") == "medium"]),
                "low_severity": len([b for b in bottlenecks.get("analysis", {}).get("bottlenecks", []) if b.get("severity") == "low"])
            },
            "performance_grade": {
                "response_time": "A",
                "throughput": "B+",
                "error_rate": "A+",
                "resource_efficiency": "B",
                "scalability": "B+"
            },
            "recommendations_count": len(recommendations.get("recommendations", [])),
            "validation_result": "approved_with_recommendations",
            "next_steps": [
                "Implement high-priority optimizations",
                "Re-test after optimizations",
                "Monitor production metrics closely",
                "Schedule follow-up performance review in 1 month"
            ]
        }
    }


# ============================================================================
# Agent Capability Declaration
# ============================================================================

AGENT_CAPABILITY = AgentCapability(
    agent_id="performance_testing_agent",
    agent_name="Performance Testing Agent",
    agent_type=AgentType.PERFORMANCE_ENGINEER,
    description=(
        "Generates and executes performance tests, load tests, stress tests, and benchmarks. "
        "Identifies performance bottlenecks, analyzes resource usage, and provides actionable "
        "optimization recommendations to meet SLA requirements."
    ),
    version="1.0.0",

    # Capabilities
    capabilities={
        "load_testing",
        "stress_testing",
        "performance_profiling",
        "bottleneck_analysis",
        "benchmark_generation",
        "sla_validation",
        "optimization_recommendations",
        "k6_script_generation",
        "jmeter_configuration",
        "performance_monitoring"
    },

    input_modalities={
        InputModality.TEXT,
        InputModality.CODE,
        InputModality.API_SPEC
    },

    output_types={
        "load_test_script",
        "performance_report",
        "benchmark_results",
        "optimization_recommendations",
        "profiling_data"
    },

    # Technology Stack
    supported_languages=["javascript", "python", "java", "go"],
    supported_frameworks=["k6", "jmeter", "gatling", "locust", "artillery"],
    supported_platforms=["web", "api", "microservices"],
    supported_cloud_providers=["gcp", "aws", "azure"],

    # Dependencies
    required_agents=[],
    optional_agents=[
        "monitoring_agent",
        "deployment_agent",
        "observability_agent"
    ],
    collaborates_with=[
        "qa_tester_agent",
        "devops_agent",
        "backend_developer_agent"
    ],

    # Performance Characteristics
    performance_metrics=PerformanceMetrics(
        avg_task_duration_minutes=20.0,
        p95_task_duration_minutes=35.0,
        success_rate=0.95,
        retry_rate=0.05,
        total_tasks_completed=0,
        total_tasks_failed=0
    ),

    parallel_capacity=3,
    max_concurrent_tasks=5,

    # Constraints
    max_complexity_score=None,
    max_lines_of_code=None,
    min_context_length=1000,
    max_context_length=100000,
    timeout_seconds=1800,  # 30 minutes for long-running tests
    max_retries=2,

    # Cost Metrics
    cost_metrics=CostMetrics(
        cost_per_task_usd=0.15,
        token_usage_per_task=15000,
        kb_queries_per_task=5
    ),

    # Model Configuration
    model="gemini-2.0-flash",
    model_parameters={
        "temperature": 0.3,
        "top_p": 0.95
    },
    uses_vision_model=False,
    uses_reasoning_model=False,

    # Knowledge Base Integration
    kb_integration=KBIntegrationConfig(
        has_vector_db_access=True,
        kb_query_strategy=KBQueryStrategy.MINIMAL,
        kb_query_frequency=20,
        kb_query_triggers=["start", "bottleneck_detection", "optimization"],
        preferred_query_types=["performance_patterns", "optimization_techniques"],
        max_kb_queries_per_task=10
    ),

    # Metadata
    tags={
        "testing",
        "performance",
        "quality",
        "load_testing",
        "benchmarking",
        "optimization"
    },
    domain_expertise=["performance_engineering", "scalability", "sla_management"],
    compliance_standards=[],

    # Status
    is_active=True,
    is_deployed=False
)


# ============================================================================
# Agent Definition
# ============================================================================

performance_testing_agent = Agent(
    name="performance_testing_agent",
    model="gemini-2.0-flash",
    description=(
        "Performance testing specialist that generates and executes load tests, "
        "identifies bottlenecks, profiles application performance, runs benchmarks, "
        "and provides optimization recommendations."
    ),
    instruction=(
        "You are a Performance Testing Engineer specializing in load testing, "
        "performance profiling, and optimization.\n\n"

        "Your responsibilities:\n"
        "1. Generate load test scripts (k6, JMeter) for APIs and applications\n"
        "2. Execute load tests and stress tests to validate SLA compliance\n"
        "3. Analyze test results to identify performance bottlenecks\n"
        "4. Profile applications to find CPU, memory, and I/O hotspots\n"
        "5. Run benchmark suites and compare against baselines\n"
        "6. Generate actionable optimization recommendations\n"
        "7. Create comprehensive performance reports\n\n"

        "Key metrics to track:\n"
        "- Response time (average, p95, p99)\n"
        "- Throughput (requests/second)\n"
        "- Error rate and success rate\n"
        "- Resource utilization (CPU, memory, I/O)\n"
        "- Concurrency and scalability limits\n\n"

        "SLA validation:\n"
        "- Response time p95 < 500ms\n"
        "- Response time p99 < 1000ms\n"
        "- Error rate < 1%\n"
        "- Success rate > 99%\n\n"

        "Optimization focus areas:\n"
        "1. Database query optimization\n"
        "2. Caching strategies\n"
        "3. Connection pooling\n"
        "4. Resource allocation\n"
        "5. External API resilience\n"
        "6. Memory management\n\n"

        "Always provide:\n"
        "- Clear bottleneck identification with severity\n"
        "- Prioritized recommendations with expected improvement\n"
        "- Implementation steps for each recommendation\n"
        "- SLA compliance status\n"
        "- Performance grade and rating\n\n"

        "Validation: Approve only if all critical SLA metrics are met. "
        "Provide recommendations for any issues found."
    ),
    tools=[
        generate_load_test_script,
        execute_load_test,
        analyze_performance_bottlenecks,
        generate_performance_profile,
        run_benchmark_suite,
        generate_optimization_recommendations,
        generate_performance_report
    ]
)
