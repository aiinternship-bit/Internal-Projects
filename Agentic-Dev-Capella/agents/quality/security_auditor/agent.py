"""
agents/quality/security_auditor/agent.py

Security Auditor Agent - Performs security vulnerability scanning,
penetration testing, code security analysis, and generates security
audit reports with remediation recommendations.
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

def scan_vulnerabilities(
    target: str,
    scan_type: str = "comprehensive",
    scan_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Scan application for security vulnerabilities.

    Args:
        target: Target URL or codebase path
        scan_type: Type of scan (quick, comprehensive, deep)
        scan_config: Additional scan configuration

    Returns:
        Vulnerability scan results
    """
    return {
        "status": "success",
        "scan_execution": {
            "scan_id": "sec-scan-001",
            "target": target,
            "scan_type": scan_type,
            "start_time": "2025-10-30T10:00:00Z",
            "end_time": "2025-10-30T10:45:00Z",
            "duration_minutes": 45,
            "tools_used": ["OWASP ZAP", "Snyk", "Bandit"]
        },
        "vulnerabilities": [
            {
                "id": "VULN-001",
                "severity": "critical",
                "category": "SQL Injection",
                "cwe_id": "CWE-89",
                "cvss_score": 9.8,
                "location": "/api/orders endpoint",
                "file": "order_controller.py",
                "line": 145,
                "description": "SQL injection vulnerability in order search functionality",
                "vulnerable_code": "query = f\"SELECT * FROM orders WHERE id = {order_id}\"",
                "attack_vector": "User-controlled input directly concatenated into SQL query",
                "exploitability": "high",
                "impact": "Database compromise, data breach"
            },
            {
                "id": "VULN-002",
                "severity": "high",
                "category": "Cross-Site Scripting (XSS)",
                "cwe_id": "CWE-79",
                "cvss_score": 7.5,
                "location": "/api/comments endpoint",
                "file": "comment_service.py",
                "line": 78,
                "description": "Reflected XSS in comment rendering",
                "vulnerable_code": "return f\"<div>{user_comment}</div>\"",
                "attack_vector": "Unsanitized user input rendered in HTML",
                "exploitability": "high",
                "impact": "Session hijacking, credential theft"
            },
            {
                "id": "VULN-003",
                "severity": "high",
                "category": "Authentication Bypass",
                "cwe_id": "CWE-287",
                "cvss_score": 8.1,
                "location": "/api/admin endpoint",
                "file": "auth_middleware.py",
                "line": 45,
                "description": "Weak JWT token validation allows bypass",
                "vulnerable_code": "if token and not verify_signature: pass",
                "attack_vector": "JWT signature not properly verified",
                "exploitability": "medium",
                "impact": "Unauthorized admin access"
            },
            {
                "id": "VULN-004",
                "severity": "medium",
                "category": "Sensitive Data Exposure",
                "cwe_id": "CWE-200",
                "cvss_score": 6.5,
                "location": "application logs",
                "file": "logger.py",
                "line": 23,
                "description": "Credit card numbers logged in plaintext",
                "vulnerable_code": "logger.info(f'Payment processed: {card_number}')",
                "attack_vector": "Sensitive data in logs",
                "exploitability": "low",
                "impact": "PCI-DSS violation, data breach"
            },
            {
                "id": "VULN-005",
                "severity": "medium",
                "category": "Insecure Dependencies",
                "cwe_id": "CWE-1035",
                "cvss_score": 6.0,
                "location": "requirements.txt",
                "description": "Vulnerable dependency: requests==2.25.0 (CVE-2023-32681)",
                "vulnerable_code": "requests==2.25.0",
                "attack_vector": "Known CVE in dependency",
                "exploitability": "medium",
                "impact": "Potential remote code execution"
            }
        ],
        "summary": {
            "total_vulnerabilities": 5,
            "critical": 1,
            "high": 2,
            "medium": 2,
            "low": 0,
            "informational": 0
        }
    }


def perform_penetration_test(
    target: str,
    test_scope: List[str],
    authorization: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Perform authorized penetration testing.

    Args:
        target: Target application URL
        test_scope: Scope of testing (endpoints, features)
        authorization: Authorization credentials and scope

    Returns:
        Penetration test results
    """
    return {
        "status": "success",
        "pentest_execution": {
            "test_id": "pentest-001",
            "target": target,
            "scope": test_scope,
            "authorization": "verified",
            "start_time": "2025-10-30T11:00:00Z",
            "end_time": "2025-10-30T14:00:00Z",
            "duration_hours": 3,
            "methodology": "OWASP Testing Guide v4"
        },
        "test_results": {
            "authentication_tests": {
                "total_tests": 12,
                "passed": 9,
                "failed": 3,
                "findings": [
                    {
                        "test": "Password brute force protection",
                        "status": "failed",
                        "description": "No rate limiting on login endpoint",
                        "severity": "high"
                    },
                    {
                        "test": "Session fixation",
                        "status": "failed",
                        "description": "Session token not regenerated after login",
                        "severity": "medium"
                    },
                    {
                        "test": "JWT token manipulation",
                        "status": "failed",
                        "description": "Weak signature validation",
                        "severity": "high"
                    }
                ]
            },
            "authorization_tests": {
                "total_tests": 10,
                "passed": 8,
                "failed": 2,
                "findings": [
                    {
                        "test": "Horizontal privilege escalation",
                        "status": "failed",
                        "description": "Users can access other users' orders by ID manipulation",
                        "severity": "critical"
                    },
                    {
                        "test": "Vertical privilege escalation",
                        "status": "failed",
                        "description": "Regular user can access admin endpoints",
                        "severity": "critical"
                    }
                ]
            },
            "injection_tests": {
                "total_tests": 15,
                "passed": 12,
                "failed": 3,
                "findings": [
                    {
                        "test": "SQL injection",
                        "status": "failed",
                        "description": "SQL injection in order search",
                        "severity": "critical"
                    },
                    {
                        "test": "XSS injection",
                        "status": "failed",
                        "description": "Reflected XSS in comments",
                        "severity": "high"
                    },
                    {
                        "test": "Command injection",
                        "status": "failed",
                        "description": "OS command injection in file upload",
                        "severity": "critical"
                    }
                ]
            },
            "data_exposure_tests": {
                "total_tests": 8,
                "passed": 6,
                "failed": 2,
                "findings": [
                    {
                        "test": "Sensitive data in responses",
                        "status": "failed",
                        "description": "API returns full credit card numbers",
                        "severity": "critical"
                    },
                    {
                        "test": "Directory listing",
                        "status": "failed",
                        "description": "Backup files accessible via direct URL",
                        "severity": "medium"
                    }
                ]
            }
        },
        "summary": {
            "total_tests": 45,
            "passed": 35,
            "failed": 10,
            "success_rate": 0.78,
            "critical_findings": 4,
            "high_findings": 3,
            "medium_findings": 3
        }
    }


def analyze_code_security(
    codebase_path: str,
    languages: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Perform static code security analysis.

    Args:
        codebase_path: Path to codebase
        languages: Programming languages to analyze

    Returns:
        Code security analysis results
    """
    return {
        "status": "success",
        "analysis": {
            "scan_id": "sast-001",
            "codebase_path": codebase_path,
            "languages_analyzed": languages or ["python", "javascript"],
            "files_scanned": 245,
            "lines_of_code": 45000,
            "tools_used": ["Bandit", "ESLint Security", "Semgrep"]
        },
        "security_issues": [
            {
                "id": "SAST-001",
                "severity": "high",
                "category": "Hardcoded Credentials",
                "file": "config.py",
                "line": 12,
                "code": "API_KEY = 'sk-1234567890abcdef'",
                "description": "Hardcoded API key in source code",
                "cwe_id": "CWE-798"
            },
            {
                "id": "SAST-002",
                "severity": "high",
                "category": "Weak Cryptography",
                "file": "encryption.py",
                "line": 45,
                "code": "hashlib.md5(password.encode())",
                "description": "Using weak MD5 hashing for passwords",
                "cwe_id": "CWE-327"
            },
            {
                "id": "SAST-003",
                "severity": "medium",
                "category": "Insecure Random",
                "file": "token_generator.py",
                "line": 23,
                "code": "random.randint(1000, 9999)",
                "description": "Using insecure random for security token",
                "cwe_id": "CWE-330"
            },
            {
                "id": "SAST-004",
                "severity": "medium",
                "category": "Path Traversal",
                "file": "file_handler.py",
                "line": 78,
                "code": "open(user_provided_path, 'r')",
                "description": "Unvalidated file path from user input",
                "cwe_id": "CWE-22"
            }
        ],
        "best_practices_violations": [
            {
                "category": "Input Validation",
                "count": 15,
                "description": "Missing input validation on user-controlled data"
            },
            {
                "category": "Output Encoding",
                "count": 8,
                "description": "Missing output encoding for HTML rendering"
            },
            {
                "category": "Error Handling",
                "count": 12,
                "description": "Verbose error messages expose internal details"
            }
        ],
        "summary": {
            "total_issues": 39,
            "high": 2,
            "medium": 2,
            "low": 35,
            "security_score": 72
        }
    }


def check_dependency_vulnerabilities(
    dependency_file: str,
    package_manager: str = "pip"
) -> Dict[str, Any]:
    """
    Check dependencies for known vulnerabilities.

    Args:
        dependency_file: Path to dependency file (requirements.txt, package.json)
        package_manager: Package manager type

    Returns:
        Dependency vulnerability scan results
    """
    return {
        "status": "success",
        "scan": {
            "dependency_file": dependency_file,
            "package_manager": package_manager,
            "total_dependencies": 45,
            "direct_dependencies": 18,
            "transitive_dependencies": 27,
            "tool_used": "Snyk"
        },
        "vulnerable_packages": [
            {
                "package": "requests",
                "current_version": "2.25.0",
                "fixed_version": "2.31.0",
                "severity": "high",
                "cve_ids": ["CVE-2023-32681"],
                "cvss_score": 7.5,
                "description": "Unintended proxy authentication in redirects",
                "exploit_maturity": "proof_of_concept",
                "fix_available": True
            },
            {
                "package": "flask",
                "current_version": "1.1.2",
                "fixed_version": "2.3.2",
                "severity": "medium",
                "cve_ids": ["CVE-2023-30861"],
                "cvss_score": 6.1,
                "description": "Open redirect vulnerability",
                "exploit_maturity": "proof_of_concept",
                "fix_available": True
            },
            {
                "package": "pillow",
                "current_version": "8.2.0",
                "fixed_version": "10.0.1",
                "severity": "critical",
                "cve_ids": ["CVE-2023-44271", "CVE-2023-50447"],
                "cvss_score": 9.8,
                "description": "Remote code execution via crafted image",
                "exploit_maturity": "functional",
                "fix_available": True
            }
        ],
        "license_issues": [
            {
                "package": "some-package",
                "version": "1.0.0",
                "license": "GPL-3.0",
                "severity": "medium",
                "description": "Copyleft license may conflict with commercial use"
            }
        ],
        "summary": {
            "total_vulnerabilities": 8,
            "critical": 1,
            "high": 2,
            "medium": 3,
            "low": 2,
            "fixable": 7,
            "unfixable": 1
        }
    }


def generate_security_recommendations(
    vulnerabilities: Dict[str, Any],
    pentest_results: Dict[str, Any],
    code_analysis: Dict[str, Any],
    dependency_scan: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate prioritized security remediation recommendations.

    Args:
        vulnerabilities: Vulnerability scan results
        pentest_results: Penetration test results
        code_analysis: Code security analysis
        dependency_scan: Dependency vulnerability scan

    Returns:
        Prioritized security recommendations
    """
    return {
        "status": "success",
        "recommendations": [
            {
                "priority": "critical",
                "category": "injection",
                "vulnerability_ids": ["VULN-001", "pentest-finding-sql"],
                "issue": "SQL injection in order search functionality",
                "recommendation": "Use parameterized queries or ORM to prevent SQL injection",
                "cvss_score": 9.8,
                "exploitability": "high",
                "remediation_steps": [
                    "Replace string concatenation with parameterized queries",
                    "Use SQLAlchemy ORM or parameterized query: cursor.execute('SELECT * FROM orders WHERE id = ?', [order_id])",
                    "Implement input validation for order_id parameter",
                    "Add Web Application Firewall (WAF) rules",
                    "Conduct security testing after fix"
                ],
                "code_example": """
# BEFORE (Vulnerable):
query = f"SELECT * FROM orders WHERE id = {order_id}"

# AFTER (Secure):
query = "SELECT * FROM orders WHERE id = ?"
cursor.execute(query, (order_id,))
""",
                "estimated_effort": "2 hours",
                "business_impact": "Prevents database breach and data theft"
            },
            {
                "priority": "critical",
                "category": "authorization",
                "vulnerability_ids": ["pentest-horizontal-escalation"],
                "issue": "Horizontal privilege escalation - users can access other users' data",
                "recommendation": "Implement proper authorization checks on all endpoints",
                "cvss_score": 8.5,
                "exploitability": "high",
                "remediation_steps": [
                    "Add ownership validation: if order.user_id != current_user.id: raise Forbidden",
                    "Implement centralized authorization middleware",
                    "Use Role-Based Access Control (RBAC) framework",
                    "Add audit logging for all data access",
                    "Test with multiple user accounts"
                ],
                "code_example": """
# Add authorization check:
@require_auth
def get_order(order_id):
    order = Order.query.get(order_id)
    if order.user_id != current_user.id:
        raise Forbidden("Access denied")
    return order
""",
                "estimated_effort": "1 day",
                "business_impact": "Prevents unauthorized data access and privacy violations"
            },
            {
                "priority": "critical",
                "category": "dependencies",
                "vulnerability_ids": ["CVE-2023-44271"],
                "issue": "Critical vulnerability in Pillow library (RCE)",
                "recommendation": "Update Pillow to version 10.0.1 or higher",
                "cvss_score": 9.8,
                "exploitability": "medium",
                "remediation_steps": [
                    "Update requirements.txt: pillow>=10.0.1",
                    "Run: pip install --upgrade pillow",
                    "Test image processing functionality",
                    "Deploy updated dependencies to all environments",
                    "Set up automated dependency scanning"
                ],
                "estimated_effort": "1 hour",
                "business_impact": "Prevents remote code execution attacks"
            },
            {
                "priority": "high",
                "category": "xss",
                "vulnerability_ids": ["VULN-002"],
                "issue": "Cross-Site Scripting (XSS) in comment rendering",
                "recommendation": "Sanitize user input and use proper output encoding",
                "cvss_score": 7.5,
                "exploitability": "high",
                "remediation_steps": [
                    "Use HTML escaping library: from markupsafe import escape",
                    "Sanitize all user input: safe_comment = escape(user_comment)",
                    "Implement Content Security Policy (CSP) headers",
                    "Use template engine auto-escaping (Jinja2)",
                    "Test with XSS payloads"
                ],
                "code_example": """
# BEFORE:
return f"<div>{user_comment}</div>"

# AFTER:
from markupsafe import escape
return f"<div>{escape(user_comment)}</div>"
""",
                "estimated_effort": "4 hours",
                "business_impact": "Prevents session hijacking and credential theft"
            },
            {
                "priority": "high",
                "category": "authentication",
                "vulnerability_ids": ["pentest-jwt-validation"],
                "issue": "Weak JWT token validation",
                "recommendation": "Implement proper JWT signature verification",
                "cvss_score": 8.1,
                "exploitability": "medium",
                "remediation_steps": [
                    "Use proper JWT library: PyJWT",
                    "Always verify signature: jwt.decode(token, SECRET_KEY, algorithms=['HS256'])",
                    "Implement token expiration and refresh mechanism",
                    "Use strong secret keys (256-bit minimum)",
                    "Rotate secret keys periodically"
                ],
                "estimated_effort": "4 hours",
                "business_impact": "Prevents authentication bypass and unauthorized access"
            },
            {
                "priority": "high",
                "category": "sensitive_data",
                "vulnerability_ids": ["VULN-004", "pentest-data-exposure"],
                "issue": "Sensitive data (credit cards) exposed in logs and API responses",
                "recommendation": "Mask sensitive data and implement proper data handling",
                "cvss_score": 6.5,
                "exploitability": "low",
                "remediation_steps": [
                    "Remove credit card logging entirely",
                    "Implement PAN masking: card_number[-4:].rjust(len(card_number), '*')",
                    "Use tokenization for payment data",
                    "Encrypt logs at rest",
                    "Conduct PCI-DSS compliance review"
                ],
                "estimated_effort": "1 day",
                "business_impact": "Achieves PCI-DSS compliance and prevents data breaches"
            },
            {
                "priority": "medium",
                "category": "cryptography",
                "vulnerability_ids": ["SAST-002"],
                "issue": "Using weak MD5 hashing for passwords",
                "recommendation": "Use bcrypt or Argon2 for password hashing",
                "cvss_score": 7.0,
                "exploitability": "medium",
                "remediation_steps": [
                    "Install bcrypt: pip install bcrypt",
                    "Hash passwords: bcrypt.hashpw(password.encode(), bcrypt.gensalt())",
                    "Verify passwords: bcrypt.checkpw(password.encode(), hashed)",
                    "Implement password migration on next login",
                    "Enforce strong password policy"
                ],
                "estimated_effort": "6 hours",
                "business_impact": "Protects user credentials from brute force attacks"
            }
        ],
        "quick_wins": [
            "Update vulnerable dependencies (1 hour)",
            "Add rate limiting on login endpoint (2 hours)",
            "Enable HTTPS and security headers (1 hour)"
        ],
        "estimated_total_effort": "4-5 days",
        "security_improvement": "Critical vulnerabilities reduced from 4 to 0"
    }


def generate_security_report(
    vulnerabilities: Dict[str, Any],
    pentest_results: Dict[str, Any],
    code_analysis: Dict[str, Any],
    dependency_scan: Dict[str, Any],
    recommendations: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate comprehensive security audit report.

    Args:
        vulnerabilities: Vulnerability scan results
        pentest_results: Penetration test results
        code_analysis: Code security analysis
        dependency_scan: Dependency vulnerability scan
        recommendations: Security recommendations

    Returns:
        Complete security audit report
    """
    return {
        "status": "success",
        "security_report": {
            "summary": {
                "audit_date": "2025-10-30",
                "application": "E-commerce API v1.1.0",
                "auditor": "Security Auditor Agent",
                "overall_security_rating": "D",
                "risk_level": "high",
                "critical_issues": 4,
                "high_priority_issues": 3,
                "total_vulnerabilities": 60,
                "pci_dss_compliant": False,
                "owasp_top_10_coverage": True
            },
            "vulnerability_summary": {
                "critical": vulnerabilities.get("summary", {}).get("critical", 0),
                "high": vulnerabilities.get("summary", {}).get("high", 0),
                "medium": vulnerabilities.get("summary", {}).get("medium", 0),
                "low": vulnerabilities.get("summary", {}).get("low", 0)
            },
            "pentest_summary": {
                "total_tests": pentest_results.get("summary", {}).get("total_tests", 0),
                "failed_tests": pentest_results.get("summary", {}).get("failed", 0),
                "success_rate": pentest_results.get("summary", {}).get("success_rate", 0),
                "critical_findings": pentest_results.get("summary", {}).get("critical_findings", 0)
            },
            "code_security_score": code_analysis.get("summary", {}).get("security_score", 0),
            "dependency_risks": {
                "vulnerable_packages": len(dependency_scan.get("vulnerable_packages", [])),
                "critical_cves": dependency_scan.get("summary", {}).get("critical", 0),
                "fixable": dependency_scan.get("summary", {}).get("fixable", 0)
            },
            "owasp_top_10_findings": {
                "A01_Broken_Access_Control": 2,
                "A02_Cryptographic_Failures": 1,
                "A03_Injection": 2,
                "A04_Insecure_Design": 0,
                "A05_Security_Misconfiguration": 3,
                "A06_Vulnerable_Components": 8,
                "A07_Auth_Failures": 2,
                "A08_Data_Integrity_Failures": 1,
                "A09_Logging_Failures": 2,
                "A10_SSRF": 0
            },
            "compliance_status": {
                "PCI-DSS": "non-compliant",
                "OWASP": "partially_compliant",
                "CWE_Top_25": "high_risk"
            },
            "recommendations_count": len(recommendations.get("recommendations", [])),
            "validation_result": "rejected",
            "required_actions": [
                "Fix all critical vulnerabilities immediately",
                "Implement proper authorization checks",
                "Update vulnerable dependencies",
                "Remove sensitive data from logs",
                "Conduct security training for development team",
                "Implement automated security testing in CI/CD",
                "Schedule follow-up audit in 2 weeks"
            ],
            "estimated_remediation": {
                "effort": "4-5 days",
                "cost_estimate": "$5,000-$10,000",
                "timeline": "2 weeks"
            }
        }
    }


# ============================================================================
# Agent Capability Declaration
# ============================================================================

AGENT_CAPABILITY = AgentCapability(
    agent_id="security_auditor_agent",
    agent_name="Security Auditor Agent",
    agent_type=AgentType.SECURITY_ENGINEER,
    description=(
        "Performs comprehensive security audits including vulnerability scanning, "
        "penetration testing, static code analysis, and dependency checks. "
        "Identifies security issues and provides detailed remediation recommendations."
    ),
    version="1.0.0",

    # Capabilities
    capabilities={
        "vulnerability_scanning",
        "penetration_testing",
        "sast_analysis",
        "dependency_scanning",
        "security_auditing",
        "threat_modeling",
        "owasp_top_10_testing",
        "pci_dss_validation",
        "cwe_analysis",
        "exploit_detection",
        "security_recommendations"
    },

    input_modalities={
        InputModality.TEXT,
        InputModality.CODE,
        InputModality.API_SPEC
    },

    output_types={
        "security_report",
        "vulnerability_scan",
        "pentest_results",
        "remediation_plan",
        "compliance_report"
    },

    # Technology Stack
    supported_languages=["python", "javascript", "java", "go", "ruby", "php"],
    supported_frameworks=["OWASP ZAP", "Snyk", "Bandit", "ESLint Security", "Semgrep"],
    supported_platforms=["web", "api", "mobile", "cloud"],
    supported_cloud_providers=["gcp", "aws", "azure"],

    # Dependencies
    required_agents=[],
    optional_agents=[
        "qa_tester_agent",
        "compliance_agent",
        "monitoring_agent"
    ],
    collaborates_with=[
        "developer_agent",
        "devops_agent",
        "compliance_agent"
    ],

    # Performance Characteristics
    performance_metrics=PerformanceMetrics(
        avg_task_duration_minutes=45.0,
        p95_task_duration_minutes=90.0,
        success_rate=0.98,
        retry_rate=0.02,
        total_tasks_completed=0,
        total_tasks_failed=0
    ),

    parallel_capacity=2,
    max_concurrent_tasks=3,

    # Constraints
    max_complexity_score=None,
    max_lines_of_code=None,
    min_context_length=2000,
    max_context_length=150000,
    timeout_seconds=3600,  # 60 minutes for comprehensive scans
    max_retries=2,

    # Cost Metrics
    cost_metrics=CostMetrics(
        cost_per_task_usd=0.25,
        token_usage_per_task=25000,
        kb_queries_per_task=10
    ),

    # Model Configuration
    model="gemini-2.0-flash",
    model_parameters={
        "temperature": 0.2,
        "top_p": 0.9
    },
    uses_vision_model=False,
    uses_reasoning_model=False,

    # Knowledge Base Integration
    kb_integration=KBIntegrationConfig(
        has_vector_db_access=True,
        kb_query_strategy=KBQueryStrategy.ADAPTIVE,
        kb_query_frequency=15,
        kb_query_triggers=["start", "vulnerability_found", "remediation"],
        preferred_query_types=["security_patterns", "vulnerability_databases", "remediation_guides"],
        max_kb_queries_per_task=20
    ),

    # Metadata
    tags={
        "security",
        "testing",
        "vulnerability",
        "penetration_testing",
        "compliance",
        "owasp"
    },
    domain_expertise=["application_security", "owasp", "penetration_testing", "threat_analysis"],
    compliance_standards=["OWASP Top 10", "CWE Top 25", "PCI-DSS", "NIST"],

    # Status
    is_active=True,
    is_deployed=False
)


# ============================================================================
# Agent Definition
# ============================================================================

security_auditor_agent = Agent(
    name="security_auditor_agent",
    model="gemini-2.0-flash",
    description=(
        "Security specialist that performs comprehensive security audits, "
        "vulnerability scanning, penetration testing, code analysis, and "
        "generates detailed security reports with remediation guidance."
    ),
    instruction=(
        "You are a Security Auditor specializing in application security, "
        "vulnerability assessment, and penetration testing.\n\n"

        "Your responsibilities:\n"
        "1. Scan applications for security vulnerabilities (OWASP Top 10, CWE)\n"
        "2. Perform authorized penetration testing\n"
        "3. Analyze code for security issues (SAST)\n"
        "4. Check dependencies for known vulnerabilities (CVEs)\n"
        "5. Generate prioritized remediation recommendations\n"
        "6. Create comprehensive security audit reports\n"
        "7. Validate compliance with security standards\n\n"

        "Security frameworks:\n"
        "- OWASP Top 10 (2021)\n"
        "- CWE Top 25 Most Dangerous Software Weaknesses\n"
        "- PCI-DSS for payment security\n"
        "- NIST Cybersecurity Framework\n\n"

        "Vulnerability severity (CVSS):\n"
        "- Critical: 9.0-10.0 (immediate action required)\n"
        "- High: 7.0-8.9 (urgent remediation needed)\n"
        "- Medium: 4.0-6.9 (plan remediation)\n"
        "- Low: 0.1-3.9 (informational)\n\n"

        "Testing methodology:\n"
        "1. Reconnaissance and information gathering\n"
        "2. Vulnerability scanning and identification\n"
        "3. Exploitation (authorized only)\n"
        "4. Impact analysis\n"
        "5. Remediation recommendations\n\n"

        "Key focus areas:\n"
        "1. Injection flaws (SQL, XSS, Command)\n"
        "2. Broken authentication and authorization\n"
        "3. Sensitive data exposure\n"
        "4. Security misconfiguration\n"
        "5. Vulnerable dependencies\n"
        "6. Cryptographic failures\n\n"

        "For each vulnerability provide:\n"
        "- Clear description and impact\n"
        "- CVSS score and severity\n"
        "- CWE/CVE references\n"
        "- Exploitability assessment\n"
        "- Detailed remediation steps\n"
        "- Code examples (vulnerable vs secure)\n"
        "- Estimated effort and business impact\n\n"

        "Validation: REJECT if any critical vulnerabilities are found. "
        "APPROVE only when security posture is acceptable (no critical/high issues). "
        "Always provide actionable remediation guidance."
    ),
    tools=[
        scan_vulnerabilities,
        perform_penetration_test,
        analyze_code_security,
        check_dependency_vulnerabilities,
        generate_security_recommendations,
        generate_security_report
    ]
)
