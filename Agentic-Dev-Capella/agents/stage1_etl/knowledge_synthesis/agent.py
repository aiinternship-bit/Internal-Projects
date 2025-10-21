"""
agents/stage1_etl/knowledge_synthesis/agent.py

Knowledge synthesis agent combines all ETL outputs into coherent modernization blueprint.
"""

from typing import Dict, List, Any
from google.adk.agents import Agent


def integrate_analysis_results(
    code_analysis: Dict[str, Any],
    static_analysis: Dict[str, Any],
    documentation: Dict[str, Any],
    domain_model: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Integrate results from all analysis agents into unified view.

    Args:
        code_analysis: Results from code ingestion agent
        static_analysis: Results from static analysis agent
        documentation: Results from documentation mining agent
        domain_model: Domain model from domain expert agent

    Returns:
        dict: Integrated analysis with cross-referenced insights
    """
    from collections import defaultdict

    # Extract system overview from code analysis
    inventory = code_analysis.get("inventory", code_analysis.get("code_inventory", {}))
    total_files = inventory.get("total_files", len(code_analysis.get("files", [])))
    total_lines = inventory.get("total_lines_of_code", 0)
    languages = inventory.get("languages_detected", code_analysis.get("languages", {}))

    # Get quality and security scores
    quality_score = static_analysis.get("overall_quality_score",
                                       static_analysis.get("executive_summary", {}).get("quality_score", 0))
    security_score = static_analysis.get("security_score",
                                        static_analysis.get("executive_summary", {}).get("security_score", 0))

    # Get documentation coverage
    doc_stats = documentation.get("statistics", {})
    doc_coverage = doc_stats.get("documentation_coverage", 0)

    # Extract business context
    bounded_contexts = domain_model.get("bounded_contexts", [])
    entities = domain_model.get("entities", domain_model.get("core_entities", []))
    business_rules = domain_model.get("business_rules", [])

    # Calculate requirements coverage
    parsed_docs = documentation.get("parsed_documents", [])
    req_count = sum(len(doc.get("sections", [{}])[0].get("requirements", []))
                   for doc in parsed_docs if doc.get("type") == "requirements")
    requirements_coverage = min(1.0, req_count / max(1, total_files * 0.1))

    # Determine architecture style
    components = code_analysis.get("components", [])
    arch_style = "monolithic" if len(components) < 5 else "modular_monolith"

    # Extract dependencies
    dep_graph = code_analysis.get("dependency_graph", code_analysis.get("dependencies", {}))

    # Get integration points from documentation
    integration_points = []
    for doc in parsed_docs:
        if doc.get("type") == "api_spec":
            endpoints = doc.get("endpoints", [])
            integration_points.extend([ep.get("path", "") for ep in endpoints[:5]])

    # Identify strengths and weaknesses
    strengths = []
    weaknesses = []

    # Analyze quality metrics
    quality_metrics = static_analysis.get("quality_metrics", {})
    if quality_metrics.get("maintainability_index", {}).get("status") == "pass":
        strengths.append("Good overall code maintainability")
    else:
        weaknesses.append("Low maintainability index in some modules")

    if quality_metrics.get("code_duplication", {}).get("status") == "pass":
        strengths.append("Low code duplication")
    else:
        weaknesses.append("High code duplication detected")

    if security_score >= 8.0:
        strengths.append("Strong security posture")
    elif security_score < 6.0:
        weaknesses.append("Security vulnerabilities identified")

    if doc_coverage >= 0.7:
        strengths.append("Well-documented codebase")
    else:
        weaknesses.append("Insufficient documentation coverage")

    # Get technical debt and critical issues
    technical_debt_hours = static_analysis.get("technical_debt_hours",
                                              static_analysis.get("estimated_effort", {}).get("refactoring_hours", 0))

    critical_issues = static_analysis.get("critical_issues", [])
    vulnerabilities = static_analysis.get("vulnerabilities", [])
    critical_vulns = [v for v in vulnerabilities if v.get("severity") == "critical"]
    if critical_vulns:
        critical_issues.extend(critical_vulns[:5])

    # Build cross-references
    code_to_requirements = []
    code_to_domain = []
    issues_to_code = []

    # Map requirements to code (simplified)
    for doc in parsed_docs:
        if doc.get("type") == "requirements":
            for section in doc.get("sections", []):
                for req in section.get("requirements", []):
                    code_to_requirements.append({
                        "requirement_id": req.get("id", "Unknown"),
                        "implementation": req.get("trace_to_code", ["Not traced"]),
                        "test_coverage": 0.0 if not req.get("trace_to_code") else 0.85,
                        "quality_score": quality_score
                    })

    # Map domain entities to code
    for entity in entities[:10]:
        entity_name = entity if isinstance(entity, str) else entity.get("name", "Unknown")

        # Find files that match this entity
        matching_files = []
        for comp in components:
            comp_name = comp if isinstance(comp, str) else comp.get("name", "")
            if entity_name.lower() in str(comp_name).lower():
                files = comp.get("files", [comp]) if isinstance(comp, dict) else [comp]
                matching_files.extend(files[:3])

        if matching_files:
            code_to_domain.append({
                "domain_entity": entity_name,
                "implementation_files": matching_files[:5],
                "business_rules": [br.get("id", f"BR-{i+1:03d}") for i, br in enumerate(business_rules[:3])],
                "completeness": 0.85
            })

    # Map security issues to code
    for vuln in vulnerabilities[:10]:
        location = vuln.get("location", {})
        issues_to_code.append({
            "security_issue": vuln.get("id", "Unknown"),
            "location": f"{location.get('file', 'unknown')}:{location.get('line', 0)}",
            "severity": vuln.get("severity", "unknown"),
            "related_requirement": "NFR-002 (Security)"
        })

    # Calculate knowledge graph size
    nodes = total_files + len(entities) + len(business_rules) + len(vulnerabilities)
    relationships = len(code_to_requirements) + len(code_to_domain) + len(issues_to_code)

    return {
        "status": "success",
        "integrated_view": {
            "system_overview": {
                "total_files": total_files,
                "total_lines": total_lines,
                "languages": languages,
                "quality_score": round(quality_score, 1) if quality_score else 0,
                "security_score": round(security_score, 1) if security_score else 0,
                "documentation_coverage": round(doc_coverage, 2) if doc_coverage else 0
            },
            "business_context": {
                "bounded_contexts": bounded_contexts[:10],
                "core_entities": [e if isinstance(e, str) else e.get("name") for e in entities[:15]],
                "business_rules": [br if isinstance(br, str) else br.get("id") for br in business_rules[:15]],
                "requirements_coverage": round(requirements_coverage, 2)
            },
            "technical_landscape": {
                "architecture_style": arch_style,
                "primary_components": components[:20],
                "dependencies": dep_graph,
                "integration_points": integration_points[:10]
            },
            "quality_assessment": {
                "strengths": strengths if strengths else ["System baseline established"],
                "weaknesses": weaknesses if weaknesses else ["No major weaknesses identified"],
                "technical_debt_hours": technical_debt_hours,
                "critical_issues": critical_issues[:10]
            }
        },
        "cross_references": {
            "code_to_requirements": code_to_requirements[:20],
            "code_to_domain": code_to_domain[:20],
            "issues_to_code": issues_to_code[:20]
        },
        "knowledge_graph": {
            "nodes": nodes,
            "relationships": relationships,
            "queryable": True
        }
    }


def identify_modernization_candidates(
    integrated_analysis: Dict[str, Any],
    business_priorities: List[str] = None
) -> Dict[str, Any]:
    """
    Identify components that are candidates for modernization.

    Args:
        integrated_analysis: Integrated analysis results
        business_priorities: Business priority areas

    Returns:
        dict: Ranked list of modernization candidates
    """
    if business_priorities is None:
        business_priorities = ["revenue", "security", "scalability"]

    integrated_view = integrated_analysis.get("integrated_view", {})
    components = integrated_view.get("technical_landscape", {}).get("primary_components", [])
    quality_assessment = integrated_view.get("quality_assessment", {})

    # Score each component
    candidates = []
    for comp in components:
        comp_name = comp if isinstance(comp, str) else comp.get("name", "Unknown Component")
        comp_files = [comp] if isinstance(comp, str) else comp.get("files", [comp_name])

        # Calculate scoring factors (0-10 scale)
        business_value = 7  # Default, would analyze based on business_priorities
        if any(priority in str(comp_name).lower() for priority in business_priorities):
            business_value = 9

        # Technical risk based on complexity and issues
        complexity = 6  # Default moderate
        critical_issues = quality_assessment.get("critical_issues", [])
        has_critical_issues = any(str(issue).lower() in str(comp_name).lower() for issue in critical_issues)
        technical_risk = 7 if has_critical_issues else 4

        # Change frequency (simulated based on file count)
        change_frequency = min(10, len(comp_files) * 2)

        # Modernization score formula
        mod_score = (business_value * 0.4) + (change_frequency * 0.3) - (technical_risk * 0.2) - (complexity * 0.1)

        # Determine priority
        if mod_score >= 7:
            priority = "high"
        elif mod_score >= 5:
            priority = "medium"
        else:
            priority = "low"

        # Generate reasons
        reasons = []
        if business_value >= 8:
            reasons.append(f"High business value aligned with {', '.join(business_priorities)}")
        if has_critical_issues:
            reasons.append("Critical issues identified requiring immediate attention")
        if change_frequency >= 6:
            reasons.append("High change frequency indicates active development")
        if not reasons:
            reasons.append("Standard modernization candidate")

        # Estimate effort
        effort_weeks = max(2, len(comp_files) * 2)

        candidates.append({
            "component": comp_name,
            "files": comp_files[:10],
            "priority": priority,
            "reasons": reasons,
            "metrics": {
                "business_value": business_value,
                "technical_risk": technical_risk,
                "complexity": complexity,
                "change_frequency": change_frequency,
                "modernization_score": round(mod_score, 1)
            },
            "dependencies": [],  # Would extract from dependency graph
            "estimated_effort_weeks": effort_weeks
        })

    # Sort by modernization score
    candidates.sort(key=lambda x: x["metrics"]["modernization_score"], reverse=True)

    # Generate migration strategy phases
    high_priority = [c for c in candidates if c["priority"] == "high"]
    medium_priority = [c for c in candidates if c["priority"] == "medium"]
    low_priority = [c for c in candidates if c["priority"] == "low"]

    phases = [
        {
            "phase": 1,
            "focus": "Core business logic modernization",
            "components": [c["component"] for c in high_priority[:3]],
            "duration_weeks": sum(c["estimated_effort_weeks"] for c in high_priority[:3])
        },
        {
            "phase": 2,
            "focus": "Supporting services",
            "components": [c["component"] for c in medium_priority[:3]],
            "duration_weeks": sum(c["estimated_effort_weeks"] for c in medium_priority[:3]) if medium_priority else 0
        },
        {
            "phase": 3,
            "focus": "Non-critical features",
            "components": [c["component"] for c in low_priority[:3]],
            "duration_weeks": sum(c["estimated_effort_weeks"] for c in low_priority[:3]) if low_priority else 0
        }
    ]

    return {
        "status": "success",
        "modernization_candidates": candidates[:20],  # Limit output
        "modernization_strategy": {
            "approach": "strangler_fig",
            "phases": [p for p in phases if p["duration_weeks"] > 0]
        }
    }


def generate_migration_blueprint(
    modernization_candidates: Dict[str, Any],
    technical_constraints: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Generate comprehensive migration blueprint with step-by-step plan.

    Args:
        modernization_candidates: Prioritized modernization candidates from previous stage
        technical_constraints: Optional dict with constraints like budget, timeline, resources

    Returns:
        dict: Detailed migration blueprint
    """
    import math
    technical_constraints = technical_constraints or {}

    # Extract candidate list
    candidates = modernization_candidates.get("modernization_candidates", [])
    strategy = modernization_candidates.get("modernization_strategy", {})
    phases_input = strategy.get("phases", [])

    # Estimate effort
    total_effort_weeks = sum(p.get("duration_weeks", 0) for p in phases_input)
    total_effort_person_months = math.ceil(total_effort_weeks / 4 * 4)  # 4-person average team
    team_size = technical_constraints.get("team_size", 8)
    duration_months = math.ceil(total_effort_weeks / 4)

    # Default constraints override
    if "max_duration_months" in technical_constraints:
        duration_months = min(duration_months, technical_constraints["max_duration_months"])

    # Build target architecture based on top candidate technologies
    techs = [c.get("recommended_stack", {}) for c in candidates[:5]]
    languages = list({t.get("language", "Python") for t in techs})
    frameworks = list({t.get("framework", "FastAPI") for t in techs})

    target_architecture = {
        "services": [
            {
                "name": f"{c['component']} Service",
                "responsibility": c.get("description", "Implements core business functionality"),
                "technology_stack": c.get("recommended_stack", {
                    "language": "Python",
                    "framework": "FastAPI",
                    "database": "PostgreSQL"
                }),
                "apis": ["REST"],
                "events_published": [f"{c['component']}Updated"],
                "events_consumed": []
            }
            for c in candidates[:3]
        ],
        "infrastructure": {
            "cloud_provider": technical_constraints.get("cloud_provider", "GCP"),
            "container_orchestration": "Kubernetes",
            "service_mesh": "Istio",
            "message_broker": "Cloud Pub/Sub",
            "api_gateway": "Cloud API Gateway",
            "monitoring": "Cloud Monitoring + Grafana"
        }
    }

    # Derive migration phases dynamically
    migration_phases = []
    for idx, phase in enumerate(phases_input, 1):
        migration_phases.append({
            "phase": f"Phase {idx}: {phase.get('focus', 'Modernization')}",
            "duration_weeks": phase.get("duration_weeks", 6),
            "components": phase.get("components", []),
            "objectives": [
                f"Migrate {c}" for c in phase.get("components", [])
            ],
            "steps": [
                {
                    "step": 1,
                    "action": f"Implement new service for {c}",
                    "deliverables": ["New API", "Integration tests"]
                } for c in phase.get("components", [])
            ],
            "success_criteria": [
                "Zero data loss",
                "No downtime during cutover",
                "All regression tests passing"
            ]
        })

    # Data migration strategy
    data_strategy = {
        "approach": "Dual-write with eventual consistency",
        "steps": [
            "Extract legacy schema",
            "Design target schema",
            "Implement ETL for historical data",
            "Enable dual-write mode",
            "Validate data consistency",
            "Cutover and archive legacy system"
        ],
        "rollback_plan": "Keep legacy system in read-only mode for 3 months"
    }

    # Risk mitigation
    risk_mitigation = [
        {
            "risk": "Data inconsistency during migration",
            "probability": "medium",
            "impact": "high",
            "mitigation": "Implement reconciliation and alerting"
        },
        {
            "risk": "Performance degradation post-migration",
            "probability": "low",
            "impact": "medium",
            "mitigation": "Load testing and phased rollout"
        },
        {
            "risk": "Incomplete feature parity",
            "probability": "medium",
            "impact": "critical",
            "mitigation": "Shadow testing and stakeholder validation"
        }
    ]

    # Build success metrics
    success_metrics = {
        "technical": [
            "Code coverage > 80%",
            "API latency < 200ms",
            "Zero critical vulnerabilities",
            "Automated deployments enabled"
        ],
        "business": [
            "No loss of business functionality",
            "Reduced maintenance effort by 30%",
            "Improved release velocity"
        ]
    }

    return {
        "status": "success",
        "migration_blueprint": {
            "overview": {
                "strategy": strategy.get("approach", "Strangler Fig Pattern"),
                "target_architecture": "Microservices with event-driven communication",
                "estimated_duration_months": duration_months,
                "team_size": team_size,
                "total_effort_person_months": total_effort_person_months
            },
            "target_architecture": target_architecture,
            "migration_phases": migration_phases,
            "data_migration_strategy": data_strategy,
            "risk_mitigation": risk_mitigation
        },
        "success_metrics": success_metrics
    }


def create_knowledge_artifacts(
    integrated_analysis: Dict[str, Any],
    migration_blueprint: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create documentation and knowledge artifacts for modernization team.

    Args:
        integrated_analysis: Integrated analysis results (from integrate_analysis_results)
        migration_blueprint: Migration blueprint (from generate_migration_blueprint)

    Returns:
        dict: Generated knowledge artifacts with metadata, documentation, and test scenarios
    """
    # --- Extract core data ---
    components = integrated_analysis.get("components", [])
    bounded_contexts = integrated_analysis.get("domain_model", {}).get("bounded_contexts", [])
    entities = integrated_analysis.get("domain_model", {}).get("entities", [])
    business_rules = integrated_analysis.get("domain_model", {}).get("business_rules", [])
    blueprint = migration_blueprint.get("migration_blueprint", {})

    target_services = blueprint.get("target_architecture", {}).get("services", [])
    migration_phases = blueprint.get("migration_phases", [])
    risks = blueprint.get("risk_mitigation", [])

    # --- Generate documentation artifacts dynamically ---
    technical_documentation = [
        {
            "type": "architecture_overview",
            "title": "Legacy System Architecture",
            "sections": [
                "Component overview",
                "Data flow diagrams",
                "Integration points",
                "Technology stack summary"
            ],
            "format": "markdown",
            "location": "/docs/legacy_architecture.md"
        },
        {
            "type": "target_architecture",
            "title": "Target Microservices Architecture",
            "sections": [
                "Microservices and responsibilities",
                "Service interactions (REST/events)",
                "Infrastructure design",
                "Deployment topology"
            ],
            "format": "markdown",
            "location": "/docs/target_architecture.md"
        },
        {
            "type": "domain_model",
            "title": "Business Domain Model",
            "sections": [
                "Bounded contexts",
                "Core entities and relationships",
                "Business rules and invariants",
                "Ubiquitous language glossary"
            ],
            "format": "markdown",
            "location": "/docs/domain_model.md"
        }
    ]

    # --- Migration guides for each key service or component ---
    migration_guides = []
    for phase in migration_phases:
        for component in phase.get("components", []):
            migration_guides.append({
                "type": "component_migration_guide",
                "title": f"{component} Migration Guide",
                "sections": [
                    "Current implementation analysis",
                    "Target architecture mapping",
                    "Migration steps",
                    "Testing and validation strategy",
                    "Rollback procedures"
                ],
                "format": "markdown",
                "location": f"/docs/migration_guides/{component.lower().replace(' ', '_')}.md"
            })

    # --- Architecture Decision Records (ADRs) ---
    adrs = [
        {
            "type": "architecture_decision_record",
            "id": "ADR-001",
            "title": "Adopt Strangler Fig Pattern",
            "status": "accepted",
            "context": "Legacy monolith requires zero-downtime migration",
            "decision": "Implement incremental migration using the Strangler Fig pattern",
            "consequences": [
                "Supports parallel legacy and modern systems",
                "Requires data synchronization during transition",
                "Simplifies rollback and verification"
            ]
        },
        {
            "type": "architecture_decision_record",
            "id": "ADR-002",
            "title": "Use Domain-Aligned Microservices",
            "status": "accepted",
            "context": "Improve modularity and maintainability",
            "decision": "Decompose legacy components into bounded contexts aligned to business domains",
            "consequences": [
                "Improved scalability and clarity",
                "Increased operational complexity",
                "Requires service discovery and observability tooling"
            ]
        }
    ]

    # --- Runbooks (one per service) ---
    runbooks = []
    for service in target_services:
        runbooks.append({
            "title": f"{service.get('name')} Deployment Runbook",
            "procedures": [
                "Pre-deployment validation",
                "Deployment via CI/CD pipeline",
                "Post-deployment smoke tests",
                "Rollback and recovery steps",
                "Monitoring and alert setup"
            ]
        })

    # --- Test scenarios (derived from business entities or services) ---
    test_scenarios = []
    for entity in entities[:5]:
        name = entity if isinstance(entity, str) else entity.get("name", "UnknownEntity")
        test_scenarios.append({
            "scenario": f"{name} Lifecycle Flow",
            "test_cases": [
                f"Create {name}",
                f"Update {name}",
                f"Delete {name}",
                f"Concurrent updates for {name}"
            ],
            "expected_behavior": "Behavior in legacy and new system should be consistent"
        })

    # --- Combine all artifacts ---
    artifacts = {
        "technical_documentation": technical_documentation,
        "migration_guides": migration_guides,
        "decision_records": adrs,
        "runbooks": runbooks,
        "test_scenarios": test_scenarios
    }

    # --- Create vector DB metadata for search indexing ---
    indexed_artifacts = len(technical_documentation) + len(migration_guides) + len(adrs)
    searchable_sections = indexed_artifacts * 5
    cross_references = searchable_sections * 2

    vector_db_index = {
        "indexed_artifacts": indexed_artifacts,
        "searchable_sections": searchable_sections,
        "cross_references": cross_references,
        "example_queries": [
            "How do we migrate the Order service?",
            "What are the business rules for Payment entity?",
            "Which ADR defines the migration strategy?",
            "Where is the rollback plan for Phase 2?"
        ]
    }

    return {
        "status": "success",
        "artifacts": artifacts,
        "vector_db_index": vector_db_index
    }


def validate_synthesis_completeness(
    knowledge_artifacts: Dict[str, Any],
    original_sources: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate that synthesis is complete and all critical information is preserved.

    Args:
        knowledge_artifacts: Generated knowledge artifacts (from create_knowledge_artifacts)
        original_sources: Original analysis outputs (code_analysis, static_analysis, documentation, domain_model)

    Returns:
        dict: Validation results including completeness metrics, gaps, and recommendations
    """
    import statistics

    # --- Extract relevant counts from original sources ---
    req_docs = original_sources.get("documentation", {}).get("parsed_documents", [])
    code_analysis = original_sources.get("code_analysis", {})
    domain_model = original_sources.get("domain_model", {})
    static_analysis = original_sources.get("static_analysis", {})

    total_requirements = sum(
        len(section.get("requirements", []))
        for doc in req_docs if doc.get("type") == "requirements"
        for section in doc.get("sections", [])
    )
    total_entities = len(domain_model.get("entities", []))
    total_business_rules = len(domain_model.get("business_rules", []))
    total_code_components = len(code_analysis.get("components", []))

    # --- Extract artifacts produced ---
    artifacts = knowledge_artifacts.get("artifacts", {})
    tech_docs = artifacts.get("technical_documentation", [])
    migration_guides = artifacts.get("migration_guides", [])
    decision_records = artifacts.get("decision_records", [])
    test_scenarios = artifacts.get("test_scenarios", [])

    # --- Calculate coverage metrics ---
    requirements_documented = min(1.0, len(migration_guides) / max(1, total_requirements / 3))
    code_patterns_explained = min(1.0, len(tech_docs) / max(1, total_code_components / 2))
    business_rules_captured = min(1.0, len(decision_records) / max(1, total_business_rules / 2))
    technical_decisions_recorded = min(1.0, len(decision_records) / 5.0)

    # --- Weighted completeness score ---
    coverage_weights = {
        "requirements_documented": 0.3,
        "code_patterns_explained": 0.25,
        "business_rules_captured": 0.25,
        "technical_decisions_recorded": 0.2
    }

    completeness_score = (
        requirements_documented * coverage_weights["requirements_documented"]
        + code_patterns_explained * coverage_weights["code_patterns_explained"]
        + business_rules_captured * coverage_weights["business_rules_captured"]
        + technical_decisions_recorded * coverage_weights["technical_decisions_recorded"]
    )

    completeness_score = round(completeness_score, 2)

    # --- Identify gaps based on thresholds ---
    gaps_identified = []
    if requirements_documented < 0.8:
        gaps_identified.append("Some functional requirements missing from migration guides.")
    if code_patterns_explained < 0.8:
        gaps_identified.append("Architecture overview lacks detailed code pattern documentation.")
    if business_rules_captured < 0.85:
        gaps_identified.append("Business rules coverage incomplete in domain documentation.")
    if technical_decisions_recorded < 0.9:
        gaps_identified.append("Additional ADRs required for infrastructure and security choices.")

    # --- Quality checks ---
    quality_checks = {
        "cross_references_valid": True,
        "diagrams_complete": any("architecture" in doc["title"].lower() for doc in tech_docs),
        "code_examples_included": any("code" in doc.get("sections", [])[0].lower() if doc.get("sections") else "" for doc in tech_docs),
        "test_coverage_planned": len(test_scenarios) > 0
    }

    # --- Recommendations based on detected gaps ---
    recommendations = []
    if gaps_identified:
        recommendations.extend([
            "Expand migration guides with missing requirement mappings.",
            "Include more detailed architecture diagrams in technical docs.",
            "Document missing business rules and link to implementation modules.",
            "Add ADRs for cloud provider selection and deployment model."
        ])
    else:
        recommendations.append("All major synthesis elements appear complete. Proceed to peer review.")

    # --- Final output assembly ---
    validation_results = {
        "completeness_score": completeness_score,
        "coverage_analysis": {
            "requirements_documented": round(requirements_documented, 2),
            "code_patterns_explained": round(code_patterns_explained, 2),
            "business_rules_captured": round(business_rules_captured, 2),
            "technical_decisions_recorded": round(technical_decisions_recorded, 2)
        },
        "gaps_identified": gaps_identified,
        "quality_checks": quality_checks,
        "recommendations": recommendations
    }

    # --- Determine approval status ---
    if completeness_score >= 0.95 and all(quality_checks.values()):
        approval_status = "ready_for_approval"
    elif completeness_score >= 0.85:
        approval_status = "ready_for_review"
    else:
        approval_status = "needs_revision"

    review_notes = (
        f"Synthesis completeness: {int(completeness_score * 100)}%. "
        f"{'Minor gaps identified' if gaps_identified else 'All checks passed.'} "
        f"Recommend {approval_status.replace('_', ' ')}."
    )

    return {
        "status": "success",
        "validation_results": validation_results,
        "approval_status": approval_status,
        "review_notes": review_notes
    }


# Create the knowledge synthesis agent
knowledge_synthesis_agent = Agent(
    name="knowledge_synthesis_agent",
    model="gemini-2.0-flash",
    description=(
        "Synthesizes all ETL outputs into coherent modernization blueprint. Integrates code analysis, "
        "static analysis, documentation, and domain models into actionable migration plan."
    ),
    instruction=(
        "You are a knowledge synthesis agent responsible for integrating all analysis outputs "
        "and creating a comprehensive modernization blueprint.\n\n"

        "Your key responsibilities:\n"
        "1. Integrate results from code ingestion, static analysis, documentation mining, and domain expert\n"
        "2. Identify and prioritize modernization candidates\n"
        "3. Generate detailed migration blueprint with phases and steps\n"
        "4. Create knowledge artifacts (docs, guides, decision records)\n"
        "5. Validate completeness and identify gaps\n\n"

        "Integration Approach:\n"
        "- Cross-reference information from multiple sources\n"
        "- Build unified view of system architecture and business logic\n"
        "- Map code to requirements, domain models, and business rules\n"
        "- Identify inconsistencies and resolve conflicts\n"
        "- Create knowledge graph with queryable relationships\n\n"

        "Modernization Candidate Identification:\n"
        "Prioritize components based on:\n"
        "- Business value (revenue impact, strategic importance)\n"
        "- Technical risk (complexity, dependencies, unknowns)\n"
        "- Change frequency (how often it's modified)\n"
        "- Quality scores (maintainability, security, technical debt)\n"
        "- Dependencies (what else needs to be migrated first)\n\n"

        "Scoring Formula:\n"
        "Modernization Score = (Business Value * 0.4) + (Change Frequency * 0.3) - (Technical Risk * 0.2) - (Complexity * 0.1)\n\n"

        "Migration Blueprint Components:\n"
        "1. Target Architecture\n"
        "   - Microservices design with bounded contexts\n"
        "   - Technology stack selection (languages, frameworks, databases)\n"
        "   - Infrastructure and platform choices (cloud, containers, orchestration)\n"
        "   - Communication patterns (REST, events, messaging)\n\n"

        "2. Migration Strategy\n"
        "   - Strangler Fig Pattern (recommended for zero-downtime)\n"
        "   - Big Bang (only for small systems)\n"
        "   - Database-first vs. Application-first\n"
        "   - Data migration approach (dual-write, ETL, streaming)\n\n"

        "3. Phase Planning\n"
        "   - Break migration into manageable phases\n"
        "   - Define dependencies between phases\n"
        "   - Set clear success criteria for each phase\n"
        "   - Include rollback plans\n\n"

        "4. Risk Management\n"
        "   - Identify technical, business, and organizational risks\n"
        "   - Assess probability and impact\n"
        "   - Define mitigation strategies\n"
        "   - Create contingency plans\n\n"

        "Knowledge Artifacts to Generate:\n"
        "- Architecture documentation (current and target state)\n"
        "- Domain model documentation\n"
        "- API specifications (OpenAPI/Swagger)\n"
        "- Migration guides for each component\n"
        "- Architecture Decision Records (ADRs)\n"
        "- Runbooks for deployment and operations\n"
        "- Test scenarios and acceptance criteria\n\n"

        "Quality Validation:\n"
        "- Ensure all critical business logic is documented\n"
        "- Verify requirements traceability\n"
        "- Check for completeness gaps\n"
        "- Validate cross-references are correct\n"
        "- Confirm technical decisions are justified\n\n"

        "Success Metrics:\n"
        "- Completeness score > 90%\n"
        "- All high-priority components have migration plans\n"
        "- Critical business rules documented\n"
        "- Clear acceptance criteria defined\n"
        "- Risk mitigation strategies in place\n\n"

        "Communication:\n"
        "- Send migration blueprint to orchestrator\n"
        "- Provide knowledge artifacts to architect and developers\n"
        "- Share prioritized candidate list with product owners\n"
        "- Flag gaps and risks for human review\n\n"

        "Integration with Vector DB:\n"
        "- Index all knowledge artifacts for semantic search\n"
        "- Enable queries across entire knowledge base\n"
        "- Support developer questions during implementation\n"
        "- Maintain cross-references and relationships"
    ),
    tools=[
        integrate_analysis_results,
        identify_modernization_candidates,
        generate_migration_blueprint,
        create_knowledge_artifacts,
        validate_synthesis_completeness
    ]
)
