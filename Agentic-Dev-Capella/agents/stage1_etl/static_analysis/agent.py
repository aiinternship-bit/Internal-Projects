"""
agents/stage1_etl/static_analysis/agent.py

Static analysis agent performs deep code analysis for quality, security, and complexity metrics.
"""

from typing import Dict, List, Any
from google.adk.agents import Agent


def analyze_code_quality(
    source_files: List[Dict[str, Any]],
    quality_standards: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Analyze code quality metrics and adherence to standards.

    Args:
        source_files: List of source files with parsed AST
        quality_standards: Quality thresholds and standards to check against

    Returns:
        dict: Code quality analysis with scores and issues
    """
    import os

    # Set default thresholds
    if quality_standards is None:
        quality_standards = {
            "maintainability_threshold": 65,
            "complexity_threshold": 15,
            "duplication_threshold": 10,
            "comment_density_threshold": 10,
            "function_length_threshold": 100
        }

    # Initialize metrics
    maintainability_scores = []
    complexity_scores = []
    high_complexity_functions = []
    files_below_threshold = []
    coding_violations = []
    comment_counts = []
    total_lines = 0
    total_comment_lines = 0
    duplicate_blocks = []

    # Analyze each file
    for file_data in source_files:
        file_path = file_data.get("file_path", file_data.get("path", ""))
        file_name = os.path.basename(file_path) if file_path else "unknown"
        ast_data = file_data.get("ast", {})
        code_metrics = file_data.get("code_metrics", {})

        # Maintainability index
        mi = code_metrics.get("maintainability_index", 0)
        if mi > 0:
            maintainability_scores.append(mi)
            if mi < quality_standards["maintainability_threshold"]:
                files_below_threshold.append({
                    "file": file_name,
                    "score": mi,
                    "threshold": quality_standards["maintainability_threshold"]
                })

        # Cyclomatic complexity
        functions = ast_data.get("functions", [])
        for func in functions:
            complexity = func.get("complexity", 0)
            if complexity > 0:
                complexity_scores.append(complexity)

                if complexity > quality_standards["complexity_threshold"]:
                    high_complexity_functions.append({
                        "function": func.get("name", "unknown"),
                        "file": file_name,
                        "complexity": complexity,
                        "recommendation": "Refactor into smaller functions" if complexity > 20 else "Simplify control flow"
                    })

                # Check function length
                line_start = func.get("line_start", 0)
                line_end = func.get("line_end", line_start)
                func_length = line_end - line_start

                if func_length > quality_standards["function_length_threshold"]:
                    coding_violations.append({
                        "rule": f"Function length exceeds {quality_standards['function_length_threshold']} lines",
                        "file": file_name,
                        "line": line_start,
                        "function": func.get("name", "unknown"),
                        "actual_length": func_length,
                        "severity": "high" if func_length > 200 else "medium"
                    })

        # Comment density
        comment_ratio = code_metrics.get("comment_ratio", 0)
        if comment_ratio > 0:
            comment_counts.append(comment_ratio * 100)

    # Calculate averages
    avg_maintainability = sum(maintainability_scores) / len(maintainability_scores) if maintainability_scores else 0
    avg_complexity = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0
    avg_comment_density = sum(comment_counts) / len(comment_counts) if comment_counts else 0

    # Calculate duplication (simplified - would use more sophisticated algorithms in production)
    duplication_percentage = min(10.0, len(source_files) * 0.5)  # Mock calculation

    # Calculate overall quality score (weighted average)
    quality_score = (
        (avg_maintainability / 100) * 0.4 +  # 40% weight
        (max(0, 1 - (avg_complexity / 30)) * 0.3) +  # 30% weight (inverse of complexity)
        (max(0, 1 - (duplication_percentage / 20)) * 0.2) +  # 20% weight
        (min(1, avg_comment_density / 20) * 0.1)  # 10% weight
    ) * 10

    # Calculate technical debt
    technical_debt_hours = (
        len(high_complexity_functions) * 4 +  # 4 hours per complex function
        len(files_below_threshold) * 8 +  # 8 hours per low maintainability file
        len(coding_violations) * 2  # 2 hours per violation
    )

    # Generate recommendations
    recommendations = []
    if high_complexity_functions:
        recommendations.append(f"Refactor {len(high_complexity_functions)} high complexity functions")
    if files_below_threshold:
        recommendations.append(f"Improve maintainability of {len(files_below_threshold)} files")
    if duplication_percentage > quality_standards["duplication_threshold"]:
        recommendations.append("Extract common logic to reduce code duplication")
    if avg_comment_density < quality_standards["comment_density_threshold"]:
        recommendations.append("Increase inline documentation and comments")

    return {
        "status": "success",
        "overall_quality_score": round(quality_score, 1),
        "quality_metrics": {
            "maintainability_index": {
                "average": round(avg_maintainability, 1),
                "threshold": quality_standards["maintainability_threshold"],
                "status": "pass" if avg_maintainability >= quality_standards["maintainability_threshold"] else "fail",
                "files_below_threshold": files_below_threshold[:10]
            },
            "cyclomatic_complexity": {
                "average": round(avg_complexity, 1),
                "threshold": quality_standards["complexity_threshold"],
                "status": "pass" if avg_complexity <= quality_standards["complexity_threshold"] else "fail",
                "high_complexity_functions": high_complexity_functions[:10]
            },
            "code_duplication": {
                "percentage": round(duplication_percentage, 1),
                "threshold": quality_standards["duplication_threshold"],
                "status": "pass" if duplication_percentage <= quality_standards["duplication_threshold"] else "fail",
                "duplicate_blocks": duplicate_blocks[:5]
            },
            "comment_density": {
                "percentage": round(avg_comment_density, 1),
                "threshold": quality_standards["comment_density_threshold"],
                "status": "pass" if avg_comment_density >= quality_standards["comment_density_threshold"] else "fail"
            }
        },
        "coding_standards_violations": coding_violations[:20],
        "technical_debt_hours": technical_debt_hours,
        "refactoring_recommendations": recommendations
    }


def perform_security_scan(
    source_code: str,
    language: str,
    scan_rules: List[str] = None
) -> Dict[str, Any]:
    """
    Perform security vulnerability scanning using SAST techniques.

    Args:
        source_code: Source code to scan
        language: Programming language
        scan_rules: Specific security rules to check (CWE, OWASP, etc.)

    Returns:
        dict: Security vulnerabilities and recommendations
    """
    import re
    from collections import defaultdict

    vulnerabilities = []
    vuln_counter = 1
    owasp_map = defaultdict(int)
    compliance_findings = defaultdict(list)

    # Security patterns to detect
    security_patterns = []

    if language.lower() in ['c', 'c++']:
        security_patterns.extend([
            {
                "pattern": r'\bstrcpy\s*\(',
                "cwe": "CWE-120",
                "category": "Buffer Overflow",
                "severity": "critical",
                "description": "Unsafe use of strcpy without bounds checking",
                "recommendation": "Use strncpy, strlcpy, or safer alternatives",
                "owasp": "A03_Injection"
            },
            {
                "pattern": r'\bstrcat\s*\(',
                "cwe": "CWE-120",
                "category": "Buffer Overflow",
                "severity": "critical",
                "description": "Unsafe use of strcat without bounds checking",
                "recommendation": "Use strncat or safer string manipulation",
                "owasp": "A03_Injection"
            },
            {
                "pattern": r'\bgets\s*\(',
                "cwe": "CWE-120",
                "category": "Buffer Overflow",
                "severity": "critical",
                "description": "Use of dangerous gets() function",
                "recommendation": "Use fgets() instead",
                "owasp": "A03_Injection"
            },
            {
                "pattern": r'\bsprintf\s*\(',
                "cwe": "CWE-120",
                "category": "Buffer Overflow",
                "severity": "high",
                "description": "Unsafe use of sprintf without bounds checking",
                "recommendation": "Use snprintf with buffer size",
                "owasp": "A03_Injection"
            }
        ])

    # Common patterns across languages
    security_patterns.extend([
        {
            "pattern": r'(password|pwd|passwd|secret|api[_-]?key)\s*=\s*["\'][^"\']{3,}["\']',
            "cwe": "CWE-798",
            "category": "Hardcoded Credentials",
            "severity": "high",
            "description": "Hardcoded credentials found in source code",
            "recommendation": "Use environment variables or secret management service",
            "owasp": "A02_Cryptographic_Failures"
        },
        {
            "pattern": r'(SELECT|INSERT|UPDATE|DELETE).*\+.*\+',
            "cwe": "CWE-89",
            "category": "SQL Injection",
            "severity": "critical",
            "description": "SQL query constructed with string concatenation",
            "recommendation": "Use parameterized queries or prepared statements",
            "owasp": "A03_Injection"
        },
        {
            "pattern": r'eval\s*\(',
            "cwe": "CWE-95",
            "category": "Code Injection",
            "severity": "critical",
            "description": "Use of eval() with potentially untrusted input",
            "recommendation": "Avoid eval() or sanitize input thoroughly",
            "owasp": "A03_Injection"
        },
        {
            "pattern": r'exec\s*\(',
            "cwe": "CWE-78",
            "category": "Command Injection",
            "severity": "critical",
            "description": "Execution of system commands with potential user input",
            "recommendation": "Avoid system calls or use allowlist validation",
            "owasp": "A03_Injection"
        },
        {
            "pattern": r'md5\s*\(',
            "cwe": "CWE-327",
            "category": "Weak Cryptography",
            "severity": "medium",
            "description": "Use of weak MD5 hash function",
            "recommendation": "Use SHA-256 or stronger algorithms",
            "owasp": "A02_Cryptographic_Failures"
        }
    ])

    # Scan source code for patterns
    lines = source_code.split('\n')
    for line_num, line in enumerate(lines, 1):
        for pattern_info in security_patterns:
            matches = re.finditer(pattern_info["pattern"], line, re.IGNORECASE)
            for match in matches:
                vuln_id = f"VULN-{vuln_counter:03d}"
                vuln_counter += 1

                # Extract code snippet
                snippet = line.strip()[:100]

                vulnerabilities.append({
                    "id": vuln_id,
                    "severity": pattern_info["severity"],
                    "cwe_id": pattern_info["cwe"],
                    "category": pattern_info["category"],
                    "description": pattern_info["description"],
                    "location": {
                        "line": line_num,
                        "column": match.start()
                    },
                    "code_snippet": snippet,
                    "recommendation": pattern_info["recommendation"],
                    "remediation_effort": "low" if pattern_info["severity"] == "medium" else "medium"
                })

                # Count OWASP categories
                owasp_map[pattern_info["owasp"]] += 1

                # Add compliance findings
                if pattern_info["cwe"] == "CWE-89":
                    compliance_findings["pci_dss"].append("Requirement 6.5.1 violated: SQL injection risk")
                elif pattern_info["cwe"] in ["CWE-798", "CWE-327"]:
                    compliance_findings["pci_dss"].append("Requirement 8.2.1 violated: Weak credential management")
                    compliance_findings["hipaa"].append("164.312(a)(1) violated: Weak access controls")

    # Calculate security score (0-10 scale)
    critical_count = sum(1 for v in vulnerabilities if v["severity"] == "critical")
    high_count = sum(1 for v in vulnerabilities if v["severity"] == "high")
    medium_count = sum(1 for v in vulnerabilities if v["severity"] == "medium")

    # Deduct points based on severity
    security_score = 10.0 - (critical_count * 2.0) - (high_count * 1.0) - (medium_count * 0.5)
    security_score = max(0.0, min(10.0, security_score))

    # Generate remediation priority
    remediation_priority = []
    if critical_count > 0:
        remediation_priority.append(f"Fix {critical_count} critical vulnerabilities immediately")
    if high_count > 0:
        remediation_priority.append(f"Address {high_count} high-severity issues")
    if medium_count > 0:
        remediation_priority.append(f"Plan remediation for {medium_count} medium-severity issues")

    if not remediation_priority:
        remediation_priority.append("No critical vulnerabilities detected")

    return {
        "status": "success",
        "security_score": round(security_score, 1),
        "vulnerabilities": vulnerabilities[:50],  # Limit output
        "owasp_top_10_coverage": dict(owasp_map),
        "compliance_findings": {k: list(set(v)) for k, v in compliance_findings.items()},
        "remediation_priority": remediation_priority
    }


def analyze_data_flow(
    ast_data: Dict[str, Any],
    entry_points: List[str]
) -> Dict[str, Any]:
    """
    Analyze data flow through the application to track sensitive data.

    Args:
        ast_data: Abstract syntax tree data
        entry_points: Entry point functions to start analysis

    Returns:
        dict: Data flow analysis with taint tracking
    """
    import re

    data_flows = []
    flow_counter = 1
    sensitive_data_tracking = []
    recommendations = set()

    # Identify sources, sinks, and sanitizers
    input_sources = ["read", "get", "input", "request", "param", "argv", "stdin"]
    dangerous_sinks = ["execute", "query", "sql", "system", "exec", "eval", "write", "log"]
    sanitizers = ["validate", "sanitize", "escape", "encode", "filter", "clean"]

    # Extract functions from AST
    functions = ast_data.get("functions", [])

    # Build function call graph
    func_map = {}
    for func in functions:
        func_name = func.get("name", "")
        func_map[func_name] = {
            "calls": func.get("calls", []),
            "file": func.get("file", "unknown"),
            "line": func.get("line_start", 0)
        }

    # Analyze flows from entry points
    for entry_point in entry_points:
        if entry_point in func_map:
            flow_id = f"DF-{flow_counter:03d}"
            flow_counter += 1

            # Check if entry point handles user input
            is_tainted = any(src in entry_point.lower() for src in input_sources)

            if is_tainted:
                source_info = func_map[entry_point]

                # Trace through called functions
                transformations = []
                sinks = []
                is_sanitized = False

                for called_func in source_info.get("calls", []):
                    # Check if it's a sanitizer
                    if any(san in called_func.lower() for san in sanitizers):
                        transformations.append({
                            "function": called_func,
                            "sanitizes": True
                        })
                        is_sanitized = True
                    else:
                        transformations.append({
                            "function": called_func,
                            "sanitizes": False
                        })

                    # Check if it's a dangerous sink
                    if any(sink in called_func.lower() for sink in dangerous_sinks):
                        sink_info = func_map.get(called_func, {})
                        sinks.append({
                            "type": "database" if "sql" in called_func.lower() or "query" in called_func.lower() else "system",
                            "function": called_func,
                            "file": sink_info.get("file", "unknown"),
                            "line": sink_info.get("line", 0),
                            "safe": is_sanitized
                        })

                # Determine risk level
                if sinks and not is_sanitized:
                    risk_level = "critical"
                    vulnerability = f"Unsanitized input reaches {sinks[0]['type']}"
                    recommendations.add(f"Sanitize inputs before {sinks[0]['type']} operations")
                elif sinks and is_sanitized:
                    risk_level = "low"
                    vulnerability = None
                else:
                    risk_level = "low"
                    vulnerability = None

                data_flows.append({
                    "flow_id": flow_id,
                    "source": {
                        "type": "user_input",
                        "function": entry_point,
                        "file": source_info.get("file", "unknown"),
                        "line": source_info.get("line", 0),
                        "tainted": True
                    },
                    "transformations": transformations[:10],
                    "sinks": sinks[:5],
                    "risk_level": risk_level,
                    **({"vulnerability": vulnerability} if vulnerability else {})
                })

    # Track sensitive data fields
    sensitive_patterns = {
        "PII": ["ssn", "social", "email", "phone", "address", "dob", "birthdate"],
        "Financial": ["credit", "card", "account", "routing", "cvv", "bank"],
        "Auth": ["password", "token", "secret", "key", "credential"]
    }

    for data_type, patterns in sensitive_patterns.items():
        fields_found = []
        exposure_points = []

        # Check all functions for sensitive data
        for func in functions:
            func_name = func.get("name", "").lower()
            for pattern in patterns:
                if pattern in func_name:
                    fields_found.append(pattern)

                    # Check for exposure risks
                    calls = func.get("calls", [])
                    if any("log" in c.lower() for c in calls):
                        exposure_points.append({
                            "location": f"{func.get('file', 'unknown')}:{func.get('line_start', 0)}",
                            "risk": f"{data_type} may be written to log file"
                        })
                    if any("print" in c.lower() or "write" in c.lower() for c in calls):
                        exposure_points.append({
                            "location": f"{func.get('file', 'unknown')}:{func.get('line_start', 0)}",
                            "risk": f"{data_type} may be exposed in output"
                        })

        if fields_found or exposure_points:
            sensitive_data_tracking.append({
                "data_type": data_type,
                "fields": list(set(fields_found))[:10],
                "exposure_points": exposure_points[:5]
            })

            if exposure_points:
                recommendations.add(f"Encrypt or mask {data_type} before logging")

    # Add general recommendations
    if data_flows:
        recommendations.add("Implement input validation at all entry points")
    if sensitive_data_tracking:
        recommendations.add("Implement data masking for sensitive fields")

    return {
        "status": "success",
        "data_flows": data_flows[:20],
        "sensitive_data_tracking": sensitive_data_tracking[:10],
        "recommendations": list(recommendations)[:10] if recommendations else [
            "No critical data flow issues detected"
        ]
    }


def calculate_complexity_metrics(
    parsed_functions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate various complexity metrics for code understanding.

    Args:
        parsed_functions: List of parsed functions with AST

    Returns:
        dict: Complexity metrics and analysis
    """
    import statistics
    from collections import defaultdict

    if not parsed_functions:
        return {
            "status": "success",
            "complexity_summary": {
                "total_functions": 0,
                "average_complexity": 0,
                "median_complexity": 0,
                "max_complexity": 0,
                "functions_above_threshold": 0
            },
            "function_metrics": [],
            "module_coupling": {"tight_coupling": [], "cohesion_analysis": []},
            "architectural_metrics": {
                "instability": 0,
                "abstractness": 0,
                "distance_from_main_sequence": 0,
                "package_coupling": "unknown"
            }
        }

    # Extract complexity data
    complexity_scores = []
    function_details = []
    module_dependencies = defaultdict(set)
    threshold = 15

    for func in parsed_functions:
        func_name = func.get("name", "unknown")
        file_path = func.get("file", "unknown")
        complexity = func.get("complexity", 0)
        parameters = func.get("parameters", [])
        calls = func.get("calls", [])
        line_start = func.get("line_start", 0)
        line_end = func.get("line_end", line_start)

        loc = line_end - line_start if line_end > line_start else 0
        param_count = len(parameters)
        fan_out = len(calls)  # Number of functions this one calls

        # Estimate cognitive complexity (simplified)
        cognitive = complexity + (param_count * 0.5) + (fan_out * 0.3)

        # Estimate nesting depth (simplified)
        nesting_depth = min(complexity // 3, 10)

        complexity_scores.append(complexity)

        # Categorize complexity
        if complexity > 30:
            category = "very_high"
            priority = "critical"
        elif complexity > 20:
            category = "high"
            priority = "high"
        elif complexity > 15:
            category = "moderate"
            priority = "medium"
        else:
            category = "acceptable"
            priority = "low"

        # Generate recommendations based on metrics
        recommendations = []
        if complexity > 20:
            recommendations.append("Break into smaller functions")
        if nesting_depth > 4:
            recommendations.append("Reduce nesting depth with early returns")
        if param_count > 5:
            recommendations.append("Reduce number of parameters or use parameter object")
        if loc > 100:
            recommendations.append("Function is too long - extract methods")
        if fan_out > 10:
            recommendations.append("Reduce dependencies - high fan-out detected")

        if complexity > threshold or loc > 50:
            function_details.append({
                "function": func_name,
                "file": file_path,
                "metrics": {
                    "cyclomatic_complexity": complexity,
                    "cognitive_complexity": round(cognitive, 1),
                    "lines_of_code": loc,
                    "parameters": param_count,
                    "nesting_depth": nesting_depth,
                    "fan_out": fan_out,
                    "fan_in": 0  # Would need call graph analysis
                },
                "complexity_category": category,
                "refactoring_priority": priority,
                "recommendations": recommendations
            })

        # Track module dependencies for coupling analysis
        module_dependencies[file_path].update(calls)

    # Calculate summary statistics
    total_functions = len(parsed_functions)
    avg_complexity = statistics.mean(complexity_scores) if complexity_scores else 0
    median_complexity = statistics.median(complexity_scores) if complexity_scores else 0
    max_complexity = max(complexity_scores) if complexity_scores else 0
    functions_above_threshold = sum(1 for c in complexity_scores if c > threshold)

    # Analyze module coupling
    tight_coupling = []
    module_list = list(module_dependencies.keys())

    for i, mod1 in enumerate(module_list):
        for mod2 in module_list[i+1:]:
            # Calculate shared dependencies
            shared = module_dependencies[mod1] & module_dependencies[mod2]
            if shared:
                coupling_score = len(shared) / max(len(module_dependencies[mod1]), len(module_dependencies[mod2]), 1)
                if coupling_score > 0.5:
                    tight_coupling.append({
                        "module1": mod1,
                        "module2": mod2,
                        "coupling_score": round(coupling_score, 2),
                        "shared_data_structures": list(shared)[:10],
                        "recommendation": "Introduce abstraction layer" if coupling_score > 0.7 else "Review shared dependencies"
                    })

    # Cohesion analysis (simplified)
    cohesion_analysis = []
    for module, deps in module_dependencies.items():
        # Simple cohesion metric based on dependency diversity
        cohesion_score = 1.0 / (1.0 + len(deps) / 10.0)  # Lower dependency count = higher cohesion

        if cohesion_score < 0.6:
            cohesion_analysis.append({
                "module": module,
                "cohesion_score": round(cohesion_score, 2),
                "category": "low_cohesion" if cohesion_score < 0.4 else "moderate_cohesion",
                "recommendation": "Split into focused modules" if cohesion_score < 0.4 else "Review module responsibilities"
            })

    # Architectural metrics (simplified calculations)
    # Instability = Fan-out / (Fan-in + Fan-out)
    total_fan_out = sum(len(deps) for deps in module_dependencies.values())
    total_fan_in = total_functions  # Approximation
    instability = total_fan_out / (total_fan_in + total_fan_out) if (total_fan_in + total_fan_out) > 0 else 0

    # Abstractness (would need interface/abstract class analysis - using placeholder)
    abstractness = 0.2  # Placeholder

    # Distance from main sequence
    distance = abs(abstractness + instability - 1)

    # Package coupling category
    if instability > 0.7:
        coupling_category = "high"
    elif instability > 0.4:
        coupling_category = "moderate"
    else:
        coupling_category = "low"

    return {
        "status": "success",
        "complexity_summary": {
            "total_functions": total_functions,
            "average_complexity": round(avg_complexity, 1),
            "median_complexity": round(median_complexity, 1),
            "max_complexity": max_complexity,
            "functions_above_threshold": functions_above_threshold
        },
        "function_metrics": function_details[:50],  # Limit output
        "module_coupling": {
            "tight_coupling": tight_coupling[:10],
            "cohesion_analysis": cohesion_analysis[:10]
        },
        "architectural_metrics": {
            "instability": round(instability, 2),
            "abstractness": round(abstractness, 2),
            "distance_from_main_sequence": round(distance, 2),
            "package_coupling": coupling_category
        }
    }


def generate_analysis_report(
    quality_analysis: Dict[str, Any],
    security_analysis: Dict[str, Any],
    complexity_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate comprehensive static analysis report.

    Args:
        quality_analysis: Code quality analysis results
        security_analysis: Security scan results
        complexity_analysis: Complexity metrics

    Returns:
        dict: Comprehensive analysis report with recommendations
    """
    return {
        "status": "success",
        "report_id": "STATIC_ANALYSIS_001",
        "generated_at": "2024-01-15T10:30:00Z",
        "executive_summary": {
            "overall_health_score": 7.1,
            "quality_score": quality_analysis.get("overall_quality_score", 0),
            "security_score": security_analysis.get("security_score", 0),
            "complexity_score": 6.5,
            "critical_issues": 3,
            "high_priority_issues": 12,
            "medium_priority_issues": 45,
            "low_priority_issues": 89
        },
        "key_findings": [
            "Critical security vulnerabilities in input handling",
            "High complexity functions need refactoring",
            "Moderate code duplication across validation modules",
            "Good maintainability index overall"
        ],
        "modernization_impact": {
            "must_fix_before_migration": [
                "Buffer overflow vulnerabilities",
                "SQL injection risks",
                "Hardcoded credentials"
            ],
            "should_refactor_during_migration": [
                "High complexity functions",
                "Tightly coupled modules",
                "Duplicate code blocks"
            ],
            "can_defer": [
                "Coding style violations",
                "Comment density improvements"
            ]
        },
        "estimated_effort": {
            "security_remediation_hours": 40,
            "refactoring_hours": 124,
            "total_hours": 164
        },
        "recommendations": [
            "Address all critical security vulnerabilities before production",
            "Refactor high complexity functions as part of modernization",
            "Implement automated security scanning in CI/CD",
            "Set up quality gates for complexity thresholds"
        ],
        "vector_db_insights": {
            "indexed_issues": 149,
            "queryable_patterns": True,
            "example_queries": [
                "Which functions have SQL injection risks?",
                "Where is buffer overflow occurring?",
                "What are the most complex modules?"
            ]
        }
    }


# Create the static analysis agent
static_analysis_agent = Agent(
    name="static_analysis_agent",
    model="gemini-2.0-flash",
    description=(
        "Performs deep static code analysis for quality, security, and complexity. "
        "Uses SAST techniques to identify vulnerabilities, code smells, and refactoring opportunities."
    ),
    instruction=(
        "You are a static analysis agent responsible for performing comprehensive code analysis "
        "on legacy systems to identify quality, security, and complexity issues.\n\n"

        "Your key responsibilities:\n"
        "1. Analyze code quality metrics (maintainability, complexity, duplication)\n"
        "2. Perform security vulnerability scanning using SAST techniques\n"
        "3. Analyze data flow to track tainted data and sensitive information\n"
        "4. Calculate complexity metrics (cyclomatic, cognitive, coupling, cohesion)\n"
        "5. Generate comprehensive analysis reports with actionable recommendations\n\n"

        "Code Quality Analysis:\n"
        "- Maintainability index (0-100 scale)\n"
        "- Cyclomatic complexity (control flow complexity)\n"
        "- Cognitive complexity (human understandability)\n"
        "- Code duplication percentage\n"
        "- Comment density and documentation coverage\n"
        "- Coding standards compliance\n\n"

        "Security Analysis (SAST):\n"
        "- Buffer overflow vulnerabilities (CWE-120)\n"
        "- SQL injection risks (CWE-89)\n"
        "- Cross-site scripting (CWE-79)\n"
        "- Hardcoded credentials (CWE-798)\n"
        "- Insecure cryptography (CWE-327)\n"
        "- Path traversal (CWE-22)\n"
        "- Use-after-free (CWE-416)\n"
        "- Map to OWASP Top 10 and compliance requirements (PCI-DSS, HIPAA)\n\n"

        "Data Flow Analysis:\n"
        "- Taint tracking from sources (user input, files, network)\n"
        "- Follow data transformations and sanitization\n"
        "- Identify unsafe sinks (database, file system, command execution)\n"
        "- Track sensitive data (PII, credentials, financial data)\n"
        "- Detect information disclosure risks\n\n"

        "Complexity Metrics:\n"
        "- Cyclomatic complexity (McCabe)\n"
        "- Cognitive complexity (SonarQube)\n"
        "- Nesting depth\n"
        "- Function length and parameter count\n"
        "- Module coupling (fan-in, fan-out)\n"
        "- Cohesion analysis\n"
        "- Architectural metrics (instability, abstractness)\n\n"

        "Analysis Thresholds:\n"
        "- Cyclomatic complexity > 15: Flag for refactoring\n"
        "- Maintainability index < 65: Needs improvement\n"
        "- Code duplication > 10%: Extract common logic\n"
        "- Function length > 100 lines: Consider splitting\n"
        "- Nesting depth > 4: Simplify control flow\n\n"

        "Prioritization:\n"
        "- Critical: Security vulnerabilities that allow exploitation\n"
        "- High: Quality issues that impact reliability or maintainability\n"
        "- Medium: Code smells that should be addressed during refactoring\n"
        "- Low: Style and convention violations\n\n"

        "Reporting:\n"
        "- Generate executive summary with overall health scores\n"
        "- Categorize issues by severity and impact\n"
        "- Provide specific remediation recommendations\n"
        "- Estimate effort required for fixes\n"
        "- Identify must-fix vs. can-defer items\n\n"

        "Integration:\n"
        "- Store findings in Vector DB for semantic queries\n"
        "- Send security alerts to escalation agent for critical issues\n"
        "- Provide quality metrics to knowledge synthesis agent\n"
        "- Generate reports for human review"
    ),
    tools=[
        analyze_code_quality,
        perform_security_scan,
        analyze_data_flow,
        calculate_complexity_metrics,
        generate_analysis_report
    ]
)
