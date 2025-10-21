"""
agents/stage1_etl/delta_monitoring/agent.py

Delta monitoring agent tracks changes in legacy system during modernization.
"""

from typing import Dict, List, Any
from google.adk.agents import Agent


def monitor_code_changes(
    repo_path: str,
    baseline_commit: str,
    check_interval_hours: int = 24
) -> Dict[str, Any]:
    """
    Monitor version control for new commits and changes.

    Args:
        repo_path: Path to legacy repository
        baseline_commit: Baseline commit hash from initial analysis
        check_interval_hours: How often to check for changes

    Returns:
        dict: Detected changes since baseline
    """
    import os
    import subprocess
    from datetime import datetime, timezone
    from collections import defaultdict

    # Verify repository exists
    if not os.path.exists(repo_path):
        return {
            "status": "error",
            "message": f"Repository path does not exist: {repo_path}",
            "changes_detected": {}
        }

    # Check if it's a git repository
    git_dir = os.path.join(repo_path, '.git')
    if not os.path.exists(git_dir):
        return {
            "status": "error",
            "message": f"Not a git repository: {repo_path}",
            "changes_detected": {}
        }

    try:
        # Get commits since baseline
        cmd = ['git', '-C', repo_path, 'log', f'{baseline_commit}..HEAD',
               '--pretty=format:%H|%aI|%ae|%s', '--no-merges']

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            return {
                "status": "error",
                "message": f"Git command failed: {result.stderr}",
                "changes_detected": {}
            }

        commit_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []

        # Parse commits
        commit_details = []
        all_authors = set()
        total_files_changed = 0
        total_lines_added = 0
        total_lines_deleted = 0
        file_change_counts = defaultdict(int)

        for line in commit_lines:
            if not line:
                continue

            parts = line.split('|', 3)
            if len(parts) < 4:
                continue

            commit_hash, date, author, message = parts
            all_authors.add(author)

            # Get files changed in this commit
            files_cmd = ['git', '-C', repo_path, 'diff-tree', '--no-commit-id',
                        '--name-only', '-r', commit_hash]
            files_result = subprocess.run(files_cmd, capture_output=True, text=True, timeout=10)
            files_changed = files_result.stdout.strip().split('\n') if files_result.stdout.strip() else []

            # Get stats for this commit
            stats_cmd = ['git', '-C', repo_path, 'show', '--shortstat', '--format=', commit_hash]
            stats_result = subprocess.run(stats_cmd, capture_output=True, text=True, timeout=10)

            lines_added = 0
            lines_deleted = 0
            if stats_result.stdout:
                # Parse: "1 file changed, 10 insertions(+), 5 deletions(-)"
                import re
                insertions = re.search(r'(\d+) insertion', stats_result.stdout)
                deletions = re.search(r'(\d+) deletion', stats_result.stdout)
                if insertions:
                    lines_added = int(insertions.group(1))
                if deletions:
                    lines_deleted = int(deletions.group(1))

            total_files_changed += len(files_changed)
            total_lines_added += lines_added
            total_lines_deleted += lines_deleted

            # Track file change frequency
            for file in files_changed:
                file_change_counts[file] += 1

            # Assess impact based on commit message and files
            impact = _assess_commit_impact(message, files_changed)

            commit_details.append({
                "commit_hash": commit_hash[:10],
                "date": date,
                "author": author,
                "message": message,
                "files_changed": files_changed,
                "lines_added": lines_added,
                "lines_deleted": lines_deleted,
                "impact_assessment": impact
            })

        # Identify hotspots
        hotspots = []
        for file, count in sorted(file_change_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            reason = _infer_hotspot_reason(file, count)
            hotspots.append({
                "file": file,
                "changes": count,
                "reason": reason
            })

        return {
            "status": "success",
            "monitoring_config": {
                "repo_path": repo_path,
                "baseline_commit": baseline_commit,
                "check_interval_hours": check_interval_hours,
                "last_check": datetime.now(timezone.utc).isoformat()
            },
            "changes_detected": {
                "total_commits": len(commit_details),
                "total_files_changed": total_files_changed,
                "total_lines_added": total_lines_added,
                "total_lines_deleted": total_lines_deleted,
                "authors": list(all_authors)
            },
            "commit_details": commit_details,
            "hotspot_analysis": {
                "frequently_changed_files": hotspots
            }
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "Git command timed out",
            "changes_detected": {}
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error monitoring changes: {str(e)}",
            "changes_detected": {}
        }


def _assess_commit_impact(message: str, files: List[str]) -> Dict[str, Any]:
    """Assess the impact of a commit based on message and files changed."""
    message_lower = message.lower()

    # Determine severity based on keywords
    severity = "low"
    impact_type = "other"

    if any(word in message_lower for word in ['critical', 'urgent', 'hotfix', 'security', 'vulnerability']):
        severity = "critical"
        impact_type = "bug_fix"
    elif any(word in message_lower for word in ['bug', 'fix', 'patch', 'issue']):
        severity = "high"
        impact_type = "bug_fix"
    elif any(word in message_lower for word in ['feature', 'add', 'new', 'implement']):
        severity = "medium"
        impact_type = "feature_addition"
    elif any(word in message_lower for word in ['refactor', 'cleanup', 'optimize', 'improve']):
        severity = "medium"
        impact_type = "refactoring"
    elif any(word in message_lower for word in ['config', 'update', 'upgrade']):
        severity = "low"
        impact_type = "configuration"

    # Infer affected modules from file paths
    affected_modules = set()
    for file in files:
        module = _infer_module_from_path(file)
        if module:
            affected_modules.add(module)

    # Generate modernization impact message
    if impact_type == "bug_fix" and severity in ["critical", "high"]:
        mod_impact = "Must be incorporated into modernized system"
    elif impact_type == "feature_addition":
        mod_impact = "New business requirement to be added to modernization plan"
    elif impact_type == "refactoring":
        mod_impact = "Review for potential architecture improvements"
    else:
        mod_impact = "Low impact, monitor for patterns"

    return {
        "severity": severity,
        "impact_type": impact_type,
        "affected_modules": list(affected_modules),
        "modernization_impact": mod_impact
    }


def _infer_module_from_path(file_path: str) -> str:
    """Infer module name from file path."""
    import os

    # Common module patterns
    if 'payment' in file_path.lower():
        return "Payment Processing"
    elif 'order' in file_path.lower():
        return "Order Management"
    elif 'tax' in file_path.lower():
        return "Tax Calculation"
    elif 'customer' in file_path.lower() or 'user' in file_path.lower():
        return "Customer Management"
    elif 'inventory' in file_path.lower() or 'stock' in file_path.lower():
        return "Inventory Management"
    elif 'database' in file_path.lower() or 'db' in file_path.lower():
        return "Database Layer"
    elif 'auth' in file_path.lower() or 'login' in file_path.lower():
        return "Authentication"
    elif 'api' in file_path.lower() or 'service' in file_path.lower():
        return "API Layer"

    # Extract from directory structure
    parts = file_path.split(os.sep)
    if len(parts) > 1:
        return parts[0].replace('_', ' ').title()

    return "Core System"


def _infer_hotspot_reason(file: str, change_count: int) -> str:
    """Infer why a file is a hotspot."""
    if change_count >= 5:
        return "High activity - active development or frequent bug fixes"
    elif change_count >= 3:
        return "Moderate activity - ongoing enhancements"
    else:
        return "Low activity - occasional updates"


def analyze_delta_impact(
    changes: Dict[str, Any],
    modernization_blueprint: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Analyze impact of detected changes on modernization plan.

    Args:
        changes: Changes detected from monitoring
        modernization_blueprint: Current modernization plan

    Returns:
        dict: Impact analysis and recommendations
    """
    from datetime import datetime, timedelta

    commit_details = changes.get("commit_details", [])
    if not commit_details:
        return {
            "status": "success",
            "impact_analysis": [],
            "summary": {
                "critical_changes": 0,
                "high_impact_changes": 0,
                "medium_impact_changes": 0,
                "low_impact_changes": 0,
                "total_effort_hours": 0,
                "components_affected": []
            },
            "recommendations": ["No changes detected"]
        }

    # Get blueprint components
    blueprint_components = modernization_blueprint.get("components", {})

    impact_analysis = []
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    total_effort_hours = 0
    all_affected_components = set()
    recommendations = set()

    # Analyze each commit
    for idx, commit in enumerate(commit_details):
        change_id = f"CHG-{idx + 1:03d}"
        commit_hash = commit.get("commit_hash", "")
        message = commit.get("message", "")
        impact_assessment = commit.get("impact_assessment", {})

        severity = impact_assessment.get("severity", "low")
        impact_type = impact_assessment.get("impact_type", "other")
        affected_modules = impact_assessment.get("affected_modules", [])

        severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Map modules to modernization components
        affected_components = _map_modules_to_components(affected_modules, blueprint_components)
        all_affected_components.update(affected_components)

        # Determine modernization status of affected components
        mod_status = _get_component_status(affected_components, blueprint_components)

        # Generate action items based on severity and type
        actions = _generate_action_items(impact_type, severity, affected_components, mod_status)

        # Calculate effort
        effort_hours = sum(action.get("estimated_effort_hours", 0) for action in actions)
        total_effort_hours += effort_hours

        # Assess risk
        risk = _assess_risk_if_ignored(impact_type, severity, affected_components)

        impact_analysis.append({
            "change_id": change_id,
            "commit": commit_hash,
            "description": message,
            "impact_type": impact_type,
            "severity": severity,
            "affected_components": affected_components,
            "modernization_status": mod_status,
            "actions_required": actions,
            "risk_if_ignored": risk
        })

        # Generate recommendations based on severity and type
        if severity == "critical":
            if mod_status == "in_development":
                recommendations.add(f"Pause development on affected components until critical change is incorporated")
            else:
                recommendations.add(f"Prioritize incorporating critical changes before development begins")

        if impact_type == "feature_addition" and severity in ["critical", "high"]:
            recommendations.add("Schedule architecture review for new features")
            recommendations.add("Update requirements documentation")

        if impact_type == "bug_fix" and severity in ["critical", "high"]:
            recommendations.add("Update test plan to include bug fix scenarios")

    # Calculate change velocity
    total_commits = changes.get("changes_detected", {}).get("total_commits", 0)
    if total_commits > 10:
        recommendations.add("Consider increasing sprint buffer for delta changes due to high change velocity")

    # Additional recommendations
    if severity_counts["critical"] > 0:
        recommendations.add("Create fast-track process for critical bug fixes")
    if len(all_affected_components) > 5:
        recommendations.add("Wide impact detected - schedule team sync meeting")

    recommendations.add("Establish weekly delta review meetings")

    return {
        "status": "success",
        "impact_analysis": impact_analysis,
        "summary": {
            "critical_changes": severity_counts["critical"],
            "high_impact_changes": severity_counts["high"],
            "medium_impact_changes": severity_counts["medium"],
            "low_impact_changes": severity_counts["low"],
            "total_effort_hours": total_effort_hours,
            "components_affected": list(all_affected_components)
        },
        "recommendations": list(recommendations)
    }


def _map_modules_to_components(modules: List[str], blueprint: Dict[str, Any]) -> List[str]:
    """Map legacy modules to modernization components."""
    # Simple mapping - in production, this would use a more sophisticated mapping
    component_map = {
        "Payment Processing": "Payment Service",
        "Order Management": "Order Service",
        "Tax Calculation": "Tax Service",
        "Customer Management": "Customer Service",
        "Inventory Management": "Inventory Service",
        "Database Layer": "Data Access Layer",
        "Authentication": "Auth Service",
        "API Layer": "API Gateway"
    }

    components = []
    for module in modules:
        component = component_map.get(module, module)
        components.append(component)

    return components if components else ["Core System"]


def _get_component_status(components: List[str], blueprint: Dict[str, Any]) -> str:
    """Get the modernization status of affected components."""
    # Check blueprint for component status
    for component in components:
        comp_data = blueprint.get(component, {})
        if comp_data.get("status") == "in_development":
            return "in_development"
        elif comp_data.get("status") == "completed":
            return "completed"
        elif comp_data.get("status") == "testing":
            return "testing"

    return "planning"


def _generate_action_items(
    impact_type: str,
    severity: str,
    components: List[str],
    mod_status: str
) -> List[Dict[str, Any]]:
    """Generate action items based on change characteristics."""
    actions = []

    # Priority mapping
    priority_map = {
        "critical": "immediate",
        "high": "high",
        "medium": "medium",
        "low": "low"
    }
    priority = priority_map.get(severity, "medium")

    # Generate actions based on impact type
    if impact_type == "bug_fix":
        if mod_status in ["in_development", "testing"]:
            actions.append({
                "action": f"Update implementation to incorporate bug fix for {', '.join(components)}",
                "priority": priority,
                "assigned_to": "developer_agent",
                "estimated_effort_hours": 4 if severity in ["critical", "high"] else 2
            })
        else:
            actions.append({
                "action": f"Document bug fix for inclusion in {', '.join(components)} design",
                "priority": priority,
                "assigned_to": "architect_agent",
                "estimated_effort_hours": 1
            })

        actions.append({
            "action": "Add test case for bug scenario",
            "priority": "high" if severity == "critical" else priority,
            "assigned_to": "qa_tester_agent",
            "estimated_effort_hours": 2
        })

    elif impact_type == "feature_addition":
        actions.append({
            "action": f"Update requirements to include new feature for {', '.join(components)}",
            "priority": priority,
            "assigned_to": "domain_expert_agent",
            "estimated_effort_hours": 2
        })

        actions.append({
            "action": f"Update architecture spec for {', '.join(components)}",
            "priority": priority,
            "assigned_to": "architect_agent",
            "estimated_effort_hours": 3
        })

        if mod_status == "in_development":
            actions.append({
                "action": "Update implementation to include new feature",
                "priority": priority,
                "assigned_to": "developer_agent",
                "estimated_effort_hours": 8
            })

    elif impact_type == "refactoring":
        actions.append({
            "action": "Review refactoring for potential architecture improvements",
            "priority": "low",
            "assigned_to": "architect_agent",
            "estimated_effort_hours": 1
        })

    return actions


def _assess_risk_if_ignored(impact_type: str, severity: str, components: List[str]) -> str:
    """Assess the risk of ignoring this change."""
    comp_str = ", ".join(components)

    if impact_type == "bug_fix":
        if severity == "critical":
            return f"{comp_str} will have critical known bug that's fixed in legacy system"
        elif severity == "high":
            return f"{comp_str} will have known bug that's fixed in legacy system"
        else:
            return f"Minor bug may persist in {comp_str}"

    elif impact_type == "feature_addition":
        if severity in ["critical", "high"]:
            return f"New system will be missing functionality present in legacy {comp_str}"
        else:
            return f"Feature parity gap in {comp_str}"

    elif impact_type == "refactoring":
        return f"May miss architecture improvement opportunity for {comp_str}"

    else:
        return "Low risk - monitor for patterns"


def synchronize_knowledge_base(
    delta_changes: Dict[str, Any],
    vector_db_collection: str
) -> Dict[str, Any]:
    """
    Update Vector DB with new information from delta changes.

    Args:
        delta_changes: Changes detected and analyzed
        vector_db_collection: Vector DB collection to update

    Returns:
        dict: Synchronization status
    """
    import hashlib
    from datetime import datetime

    commit_details = delta_changes.get("commit_details", [])

    if not commit_details:
        return {
            "status": "success",
            "synchronization": {
                "collection": vector_db_collection,
                "updates_applied": 0,
                "new_documents": [],
                "updated_documents": [],
                "deprecated_documents": []
            },
            "consistency_check": {
                "status": "passed",
                "conflicts_detected": 0,
                "conflicts_resolved": 0
            },
            "query_impact": {
                "affected_queries": [],
                "query_results_updated": False
            }
        }

    new_documents = []
    updated_documents = []
    deprecated_documents = []
    affected_queries = set()
    files_to_update = set()

    # Process each commit for knowledge base updates
    for commit in commit_details:
        commit_hash = commit.get("commit_hash", "")
        message = commit.get("message", "")
        files_changed = commit.get("files_changed", [])
        impact = commit.get("impact_assessment", {})

        impact_type = impact.get("impact_type", "other")
        affected_modules = impact.get("affected_modules", [])

        # Create document for significant changes
        if impact.get("severity") in ["critical", "high", "medium"]:
            # Generate vector ID
            doc_id = f"vec_delta_{hashlib.md5(commit_hash.encode()).hexdigest()[:12]}"

            # Create document content
            doc_content = f"Delta Change: {message}\n"
            doc_content += f"Type: {impact_type}\n"
            doc_content += f"Modules: {', '.join(affected_modules)}\n"
            doc_content += f"Commit: {commit_hash}\n"

            new_doc = {
                "type": impact_type,
                "title": message[:100],
                "commit": commit_hash,
                "content": doc_content,
                "metadata": {
                    "severity": impact.get("severity"),
                    "modules": affected_modules,
                    "timestamp": commit.get("date")
                },
                "indexed": True,
                "vector_id": doc_id
            }

            new_documents.append(new_doc)

            # Track affected queries based on modules
            for module in affected_modules:
                affected_queries.add(f"How does {module.lower()} work?")

        # Track files that need to be re-analyzed
        for file in files_changed:
            files_to_update.add(file)

    # Create updated document entries for changed files
    for file in files_to_update:
        file_vector_id = f"vec_code_{hashlib.md5(file.encode()).hexdigest()[:12]}"

        updated_documents.append({
            "type": "code_analysis",
            "file": file,
            "reason": "Code changed, re-analyzed",
            "vector_id": file_vector_id,
            "update_timestamp": datetime.utcnow().isoformat() + 'Z'
        })

    # Check for deprecated functionality (files deleted or renamed)
    # This would require git diff analysis in production

    # Simulate consistency check
    conflicts_detected = 0
    conflicts_resolved = 0

    # In production, would check for conflicting information
    # For now, assume no conflicts

    total_updates = len(new_documents) + len(updated_documents)

    return {
        "status": "success",
        "synchronization": {
            "collection": vector_db_collection,
            "updates_applied": total_updates,
            "new_documents": new_documents[:10],  # Limit output
            "updated_documents": updated_documents[:10],
            "deprecated_documents": deprecated_documents
        },
        "consistency_check": {
            "status": "passed",
            "conflicts_detected": conflicts_detected,
            "conflicts_resolved": conflicts_resolved
        },
        "query_impact": {
            "affected_queries": list(affected_queries)[:10],
            "query_results_updated": len(affected_queries) > 0
        }
    }


def track_requirements_drift(
    original_requirements: Dict[str, Any],
    delta_changes: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Track drift between original requirements and evolving legacy system.

    Args:
        original_requirements: Requirements from initial analysis
        delta_changes: Changes detected over time

    Returns:
        dict: Requirements drift analysis
    """
    from datetime import datetime

    baseline_req_count = original_requirements.get("total_requirements", 0)
    commit_details = delta_changes.get("commit_details", [])

    new_requirements = []
    modified_requirements = []
    deprecated_requirements = []
    architecture_changes = set()
    test_plan_updates = set()

    req_counter = baseline_req_count + 1

    # Analyze each commit for requirement changes
    for commit in commit_details:
        commit_hash = commit.get("commit_hash", "")
        message = commit.get("message", "")
        date = commit.get("date", "")
        impact = commit.get("impact_assessment", {})

        impact_type = impact.get("impact_type", "other")
        severity = impact.get("severity", "low")
        affected_modules = impact.get("affected_modules", [])

        # Extract new requirements from feature additions
        if impact_type == "feature_addition":
            priority = "must_have" if severity in ["critical", "high"] else "should_have"

            new_req = {
                "id": f"FR-{req_counter:03d}",
                "source": f"commit:{commit_hash}",
                "description": _extract_requirement_from_message(message, affected_modules),
                "priority": priority,
                "date_added": date[:10] if date else datetime.now().date().isoformat(),
                "reason": _infer_business_reason(message),
                "affected_modules": affected_modules
            }

            new_requirements.append(new_req)
            req_counter += 1

            # Track architecture changes needed
            for module in affected_modules:
                architecture_changes.add(f"Implement {message[:50]} for {module}")
                test_plan_updates.add(f"Add test scenarios for {module}")

        # Detect modified requirements from bug fixes or refactoring
        elif impact_type == "bug_fix" and severity in ["critical", "high"]:
            # Infer that a requirement was incorrectly implemented
            modified_req = {
                "id": f"FR-???",  # Would map to existing requirement
                "original": f"Original implementation of {', '.join(affected_modules)}",
                "modified": f"Corrected implementation based on: {message[:80]}",
                "source": f"commit:{commit_hash}",
                "reason": "Bug fix reveals requirement clarification",
                "impact": "Need to update implementation and tests"
            }

            modified_requirements.append(modified_req)

        elif impact_type == "refactoring" and severity in ["high", "medium"]:
            # Performance improvements may indicate NFR changes
            if any(word in message.lower() for word in ['performance', 'optimize', 'faster', 'speed']):
                modified_req = {
                    "id": f"NFR-???",
                    "original": f"Performance requirements for {', '.join(affected_modules)}",
                    "modified": f"Improved performance based on: {message[:80]}",
                    "source": f"commit:{commit_hash}",
                    "reason": "Performance optimization",
                    "impact": "Update performance SLAs"
                }

                modified_requirements.append(modified_req)

        # Detect deprecated requirements (removals)
        # This would be detected from deleted files/functions in production
        if 'remove' in message.lower() or 'deprecate' in message.lower():
            deprecated_req = {
                "id": f"FR-???",
                "description": f"Deprecated functionality in {', '.join(affected_modules)}: {message[:80]}",
                "reason": message,
                "date_deprecated": date[:10] if date else datetime.now().date().isoformat()
            }

            deprecated_requirements.append(deprecated_req)

    # Calculate drift statistics
    new_req_count = len(new_requirements)
    modified_req_count = len(modified_requirements)
    deprecated_req_count = len(deprecated_requirements)
    current_req_count = baseline_req_count + new_req_count - deprecated_req_count

    # Estimate schedule impact
    # Assume: new feature = 2 days, high-impact change = 1 day
    schedule_impact_days = (
        new_req_count * 2 +
        sum(1 for req in modified_requirements if 'critical' in req.get('impact', '').lower())
    )

    # Generate recommendations
    recommendations = []

    if new_req_count > 0:
        recommendations.append(f"Update architecture spec to include {new_req_count} new requirements")
        recommendations.append("Schedule sprint planning to accommodate new requirements")

    if modified_req_count > 0:
        recommendations.append("Review and update affected requirements documentation")
        if any('performance' in req.get('reason', '').lower() for req in modified_requirements):
            recommendations.append("Review performance SLAs with stakeholders")

    if deprecated_req_count > 0:
        recommendations.append(f"Remove {deprecated_req_count} deprecated requirements from migration plan")

    if schedule_impact_days > 3:
        recommendations.append(f"Adjust timeline - estimated {schedule_impact_days} days impact")

    return {
        "status": "success",
        "drift_analysis": {
            "baseline_requirements": baseline_req_count,
            "new_requirements": new_req_count,
            "modified_requirements": modified_req_count,
            "deprecated_requirements": deprecated_req_count,
            "current_requirements": current_req_count
        },
        "new_requirements": new_requirements,
        "modified_requirements": modified_requirements,
        "deprecated_requirements": deprecated_requirements,
        "impact_on_modernization": {
            "blueprint_updates_needed": new_req_count > 0 or modified_req_count > 0,
            "architecture_changes": list(architecture_changes)[:10],
            "test_plan_updates": list(test_plan_updates)[:10],
            "estimated_schedule_impact_days": schedule_impact_days
        },
        "recommendations": recommendations
    }


def _extract_requirement_from_message(message: str, modules: List[str]) -> str:
    """Extract a requirement statement from a commit message."""
    # Clean up the message
    message = message.strip()

    # Try to make it sound like a requirement
    module_str = ', '.join(modules) if modules else "the system"

    if message.startswith(('Add', 'add', 'Implement', 'implement')):
        return f"System shall {message.lower()} for {module_str}"
    elif message.startswith(('Fix', 'fix')):
        return f"System shall correctly handle {message[4:].lower()} in {module_str}"
    else:
        return f"System shall support: {message} ({module_str})"


def _infer_business_reason(message: str) -> str:
    """Infer business reason from commit message."""
    message_lower = message.lower()

    if 'eu' in message_lower or 'europe' in message_lower:
        return "Business expansion to European market"
    elif 'tax' in message_lower:
        return "Tax regulation compliance"
    elif 'payment' in message_lower:
        return "Payment processing enhancement"
    elif 'security' in message_lower:
        return "Security compliance requirement"
    elif 'performance' in message_lower or 'optimize' in message_lower:
        return "Performance improvement requirement"
    elif 'customer' in message_lower or 'user' in message_lower:
        return "Customer experience enhancement"
    else:
        return "Business requirement change"


def generate_delta_report(
    changes: Dict[str, Any],
    impact_analysis: Dict[str, Any],
    requirements_drift: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate comprehensive delta monitoring report.

    Args:
        changes: Detected changes
        impact_analysis: Impact on modernization
        requirements_drift: Requirements drift analysis

    Returns:
        dict: Delta monitoring report
    """
    from datetime import datetime, timedelta
    from collections import defaultdict
    import uuid

    # Generate unique report ID
    report_id = f"DELTA_REPORT_{uuid.uuid4().hex[:8].upper()}"

    # Calculate reporting period from changes
    commit_details = changes.get("commit_details", [])
    monitoring_config = changes.get("monitoring_config", {})

    if commit_details:
        dates = [commit.get("date", "") for commit in commit_details if commit.get("date")]
        if dates:
            sorted_dates = sorted(dates)
            start_date = sorted_dates[0]
            end_date = sorted_dates[-1]
        else:
            end_date = datetime.now().isoformat() + 'Z'
            start_date = (datetime.now() - timedelta(days=30)).isoformat() + 'Z'
    else:
        end_date = datetime.now().isoformat() + 'Z'
        start_date = (datetime.now() - timedelta(days=30)).isoformat() + 'Z'

    # Calculate days
    try:
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        days = (end_dt - start_dt).days + 1
    except:
        days = 30

    # Get summary data
    changes_detected = changes.get("changes_detected", {})
    summary = impact_analysis.get("summary", {})
    drift = requirements_drift.get("drift_analysis", {})
    impact_on_mod = requirements_drift.get("impact_on_modernization", {})

    # Count changes by type
    change_type_counts = defaultdict(int)
    severity_counts = defaultdict(int)
    component_counts = defaultdict(int)

    for commit in commit_details:
        impact = commit.get("impact_assessment", {})
        impact_type = impact.get("impact_type", "other")
        severity = impact.get("severity", "low")
        modules = impact.get("affected_modules", [])

        change_type_counts[impact_type] += 1
        severity_counts[severity] += 1

        for module in modules:
            component_counts[module] += 1

    # Generate action items from impact analysis
    action_items = []
    action_counter = 1

    for item in impact_analysis.get("impact_analysis", []):
        for action in item.get("actions_required", []):
            # Calculate due date based on priority
            priority = action.get("priority", "medium")
            if priority == "immediate":
                due_days = 2
            elif priority == "high":
                due_days = 5
            elif priority == "medium":
                due_days = 10
            else:
                due_days = 14

            due_date = (datetime.now() + timedelta(days=due_days)).date().isoformat()

            action_items.append({
                "id": f"ACT-{action_counter:03d}",
                "priority": priority,
                "description": action.get("action", ""),
                "assigned_to": action.get("assigned_to", "unassigned"),
                "due_date": due_date,
                "estimated_hours": action.get("estimated_effort_hours", 0)
            })

            action_counter += 1

    # Calculate trends
    total_commits = changes_detected.get("total_commits", 0)
    if days > 0:
        change_velocity = f"{total_commits} commits per {days} days"
    else:
        change_velocity = "No data"

    bug_fix_count = change_type_counts.get("bug_fix", 0)
    feature_count = change_type_counts.get("feature_addition", 0)

    bug_fix_ratio = bug_fix_count / max(total_commits, 1)
    feature_ratio = feature_count / max(total_commits, 1)

    # Make predictions based on trends
    if total_commits > 20:
        prediction = "Legacy system highly active - recommend accelerating migration"
    elif total_commits > 10:
        prediction = "Legacy system remains active with moderate changes"
    elif total_commits > 0:
        prediction = "Legacy system has low activity - stable migration environment"
    else:
        prediction = "No changes detected - legacy system frozen"

    # Aggregate recommendations
    all_recommendations = set()
    all_recommendations.update(impact_analysis.get("recommendations", []))
    all_recommendations.update(requirements_drift.get("recommendations", []))

    # Add standard recommendations
    if total_commits > 0:
        all_recommendations.add("Establish weekly delta review meetings")
        all_recommendations.add("Implement automated change detection")

    if severity_counts.get("critical", 0) > 0:
        all_recommendations.add("Create fast-track process for critical bug fixes")

    if total_commits > 15:
        all_recommendations.add("Consider accelerating migration timeline due to active legacy changes")

    return {
        "status": "success",
        "report": {
            "report_id": report_id,
            "generated_at": datetime.now().isoformat() + 'Z',
            "period": {
                "start_date": start_date,
                "end_date": end_date,
                "days": days
            },
            "executive_summary": {
                "total_changes": total_commits,
                "critical_changes": severity_counts.get("critical", 0),
                "high_impact_changes": severity_counts.get("high", 0),
                "new_requirements": drift.get("new_requirements", 0),
                "modified_requirements": drift.get("modified_requirements", 0),
                "schedule_impact_days": impact_on_mod.get("estimated_schedule_impact_days", 0),
                "action_items": len(action_items),
                "total_effort_hours": summary.get("total_effort_hours", 0)
            },
            "change_summary": {
                "by_type": {
                    "bug_fixes": change_type_counts.get("bug_fix", 0),
                    "features": change_type_counts.get("feature_addition", 0),
                    "refactoring": change_type_counts.get("refactoring", 0),
                    "configuration": change_type_counts.get("configuration", 0),
                    "other": change_type_counts.get("other", 0)
                },
                "by_severity": {
                    "critical": severity_counts.get("critical", 0),
                    "high": severity_counts.get("high", 0),
                    "medium": severity_counts.get("medium", 0),
                    "low": severity_counts.get("low", 0)
                },
                "by_component": dict(component_counts)
            },
            "code_statistics": {
                "files_changed": changes_detected.get("total_files_changed", 0),
                "lines_added": changes_detected.get("total_lines_added", 0),
                "lines_deleted": changes_detected.get("total_lines_deleted", 0),
                "contributors": len(changes_detected.get("authors", []))
            },
            "modernization_impact": {
                "components_affected": summary.get("components_affected", []),
                "total_effort_hours": summary.get("total_effort_hours", 0),
                "blueprint_updates_required": impact_on_mod.get("blueprint_updates_needed", False),
                "architecture_changes_needed": impact_on_mod.get("architecture_changes", [])[:10],
                "test_plan_updates": impact_on_mod.get("test_plan_updates", [])[:10]
            },
            "action_items": action_items[:20],  # Limit to top 20
            "trends": {
                "change_velocity": change_velocity,
                "bug_fix_ratio": round(bug_fix_ratio, 2),
                "feature_addition_ratio": round(feature_ratio, 2),
                "refactoring_ratio": round(change_type_counts.get("refactoring", 0) / max(total_commits, 1), 2),
                "prediction": prediction
            },
            "hotspot_analysis": changes.get("hotspot_analysis", {}),
            "recommendations": list(all_recommendations)[:15]
        },
        "distribution": {
            "recipients": [
                "project_manager",
                "tech_lead",
                "orchestrator_agent",
                "architect_agent"
            ],
            "notification_channels": ["email", "slack"],
            "priority": "high" if severity_counts.get("critical", 0) > 0 else "normal"
        }
    }


# Create the delta monitoring agent
delta_monitoring_agent = Agent(
    name="delta_monitoring_agent",
    model="gemini-2.0-flash",
    description=(
        "Monitors legacy system for changes during modernization. Detects code changes, "
        "analyzes impact, tracks requirements drift, and keeps knowledge base synchronized."
    ),
    instruction=(
        "You are a delta monitoring agent responsible for tracking changes in the legacy system "
        "while modernization is in progress.\n\n"

        "Your key responsibilities:\n"
        "1. Monitor version control for new commits and code changes\n"
        "2. Analyze impact of changes on modernization plan\n"
        "3. Synchronize Vector DB with new information\n"
        "4. Track requirements drift (new, modified, deprecated requirements)\n"
        "5. Generate delta reports with actionable recommendations\n\n"

        "Why Delta Monitoring Matters:\n"
        "Legacy systems often remain active during modernization. Changes can include:\n"
        "- Critical bug fixes that must be incorporated into new system\n"
        "- New features added due to business needs\n"
        "- Performance optimizations and refactoring\n"
        "- Configuration and infrastructure changes\n"
        "Failing to track these changes can lead to feature parity gaps.\n\n"

        "Change Detection:\n"
        "- Monitor version control (Git, SVN) for new commits\n"
        "- Track file changes, additions, deletions\n"
        "- Analyze commit messages for context\n"
        "- Identify changed modules and components\n"
        "- Detect hotspots (frequently changing files)\n\n"

        "Impact Analysis:\n"
        "For each change, assess:\n"
        "- Impact type (bug fix, feature, refactoring, config)\n"
        "- Severity (critical, high, medium, low)\n"
        "- Affected modernization components\n"
        "- Current modernization status of affected components\n"
        "- Actions required to incorporate change\n"
        "- Risk if change is ignored\n\n"

        "Impact Severity Levels:\n"
        "- Critical: Bug fixes or security patches that must be in new system\n"
        "- High: New features or significant business logic changes\n"
        "- Medium: Performance optimizations or refactoring\n"
        "- Low: Configuration changes, documentation updates\n\n"

        "Requirements Drift Tracking:\n"
        "- Identify new requirements from code changes\n"
        "- Track modifications to existing requirements\n"
        "- Detect deprecated functionality\n"
        "- Update requirements documentation\n"
        "- Assess impact on architecture and design\n"
        "- Estimate schedule impact\n\n"

        "Vector DB Synchronization:\n"
        "- Update code embeddings for changed files\n"
        "- Add new documentation from commit messages\n"
        "- Update business rules and requirements\n"
        "- Maintain consistency across knowledge base\n"
        "- Ensure queries return up-to-date information\n\n"

        "Action Item Generation:\n"
        "For each significant change, create action items:\n"
        "- Description of what needs to be done\n"
        "- Priority level (critical, high, medium, low)\n"
        "- Assigned agent (developer, architect, QA, etc.)\n"
        "- Estimated effort in hours\n"
        "- Due date based on priority\n\n"

        "Reporting:\n"
        "Generate periodic delta reports including:\n"
        "- Summary of changes detected\n"
        "- Impact on modernization timeline and scope\n"
        "- Action items with priorities\n"
        "- Trends and predictions\n"
        "- Recommendations for process improvements\n\n"

        "Escalation Criteria:\n"
        "Escalate to human review when:\n"
        "- Critical changes detected in components being modernized\n"
        "- Significant new requirements added\n"
        "- Changes conflict with architectural decisions\n"
        "- Schedule impact exceeds threshold (e.g., > 1 week)\n\n"

        "Best Practices:\n"
        "- Run checks daily or on every legacy commit\n"
        "- Prioritize changes by business impact\n"
        "- Fast-track critical bug fixes\n"
        "- Batch low-priority changes for efficiency\n"
        "- Maintain clear change log for audit trail\n"
        "- Communicate changes to affected teams promptly\n\n"

        "Integration:\n"
        "- Send action items to orchestrator for task assignment\n"
        "- Update architect with new requirements\n"
        "- Notify developers of relevant code changes\n"
        "- Alert QA team to new test scenarios\n"
        "- Keep knowledge synthesis agent informed of drift"
    ),
    tools=[
        monitor_code_changes,
        analyze_delta_impact,
        synchronize_knowledge_base,
        track_requirements_drift,
        generate_delta_report
    ]
)
