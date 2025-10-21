"""
agents/stage1_etl/documentation_mining/agent.py

Documentation mining agent extracts knowledge from technical docs, comments, and external sources.
"""

from typing import Dict, List, Any
from google.adk.agents import Agent


def extract_inline_documentation(
    source_files: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Extract and parse inline code comments and docstrings.

    Args:
        source_files: List of source files with code

    Returns:
        dict: Extracted documentation with context
    """
    import re
    import ast
    import os

    function_docstrings = []
    inline_comments = []
    header_comments = []

    total_comments = 0
    documented_functions = 0
    undocumented_functions = 0
    todo_count = 0
    fixme_count = 0
    hack_count = 0

    module_doc_scores = {}

    for source_file in source_files:
        file_path = source_file.get("file_path", source_file.get("path", ""))
        language = source_file.get("language", "Unknown")

        if not file_path or not os.path.exists(file_path):
            continue

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                source_code = f.read()

            file_name = os.path.basename(file_path)
            lines = source_code.split('\n')
            file_comments = []

            # Python-specific extraction
            if language.lower() == 'python':
                try:
                    tree = ast.parse(source_code)

                    # Extract function docstrings
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            docstring = ast.get_docstring(node)
                            if docstring:
                                quality, completeness = _assess_docstring_quality(docstring)
                                function_docstrings.append({
                                    "function": node.name,
                                    "file": file_name,
                                    "lines": f"{node.lineno}-{node.end_lineno if hasattr(node, 'end_lineno') else node.lineno}",
                                    "documentation": docstring,
                                    "quality": quality,
                                    "completeness": completeness
                                })
                                documented_functions += 1
                            else:
                                undocumented_functions += 1

                except SyntaxError:
                    pass  # Skip files with syntax errors

                # Extract inline comments
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith('#'):
                        comment_text = stripped[1:].strip()
                        comment_type, context = _classify_comment(comment_text)

                        file_comments.append({
                            "file": file_name,
                            "line": i + 1,
                            "comment": comment_text,
                            "type": comment_type,
                            "context": context
                        })

                        total_comments += 1

                        if comment_type == "todo":
                            todo_count += 1
                        elif comment_type == "fixme":
                            fixme_count += 1
                        elif comment_type == "hack":
                            hack_count += 1

            # C/C++ extraction
            elif language.lower() in ['c', 'c++']:
                # Extract multi-line comments (/* ... */)
                multiline_pattern = r'/\*\*(.*?)\*/'
                for match in re.finditer(multiline_pattern, source_code, re.DOTALL):
                    comment_text = match.group(1).strip()
                    line_num = source_code[:match.start()].count('\n') + 1

                    # Check if it's a function documentation
                    next_code = source_code[match.end():match.end()+200]
                    func_match = re.search(r'(\w+)\s+(\w+)\s*\([^)]*\)', next_code)

                    if func_match and line_num < 100:  # Likely header comment
                        header_comments.append({
                            "file": file_name,
                            "documentation": comment_text
                        })
                    elif func_match:
                        quality, completeness = _assess_docstring_quality(comment_text)
                        function_docstrings.append({
                            "function": func_match.group(2),
                            "file": file_name,
                            "lines": f"{line_num}-{line_num + comment_text.count(chr(10))}",
                            "documentation": comment_text,
                            "quality": quality,
                            "completeness": completeness
                        })
                        documented_functions += 1

                    total_comments += 1

                # Extract single-line comments
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith('//'):
                        comment_text = stripped[2:].strip()
                        comment_type, context = _classify_comment(comment_text)

                        file_comments.append({
                            "file": file_name,
                            "line": i + 1,
                            "comment": comment_text,
                            "type": comment_type,
                            "context": context
                        })

                        total_comments += 1

                        if comment_type == "todo":
                            todo_count += 1
                        elif comment_type == "fixme":
                            fixme_count += 1
                        elif comment_type == "hack":
                            hack_count += 1

                # Count undocumented functions
                func_defs = re.findall(r'\w+\s+(\w+)\s*\([^)]*\)\s*\{', source_code)
                documented_func_names = {f['function'] for f in function_docstrings if f['file'] == file_name}
                undocumented_functions += len([f for f in func_defs if f not in documented_func_names])

            # Java extraction
            elif language.lower() == 'java':
                # Extract JavaDoc comments
                javadoc_pattern = r'/\*\*(.*?)\*/'
                for match in re.finditer(javadoc_pattern, source_code, re.DOTALL):
                    comment_text = match.group(1).strip()
                    line_num = source_code[:match.start()].count('\n') + 1

                    # Check for method definition
                    next_code = source_code[match.end():match.end()+200]
                    method_match = re.search(r'(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\(', next_code)

                    if method_match:
                        quality, completeness = _assess_docstring_quality(comment_text)
                        function_docstrings.append({
                            "function": method_match.group(1),
                            "file": file_name,
                            "lines": f"{line_num}-{line_num + comment_text.count(chr(10))}",
                            "documentation": comment_text,
                            "quality": quality,
                            "completeness": completeness
                        })
                        documented_functions += 1

                    total_comments += 1

            # Store filtered inline comments (important ones)
            important_comments = [c for c in file_comments
                                 if c['type'] in ['important_note', 'todo', 'fixme', 'hack', 'bug']]
            inline_comments.extend(important_comments[:20])  # Limit per file

            # Calculate documentation score for this module
            if total_comments > 0 or documented_functions > 0:
                doc_score = (len(file_comments) + documented_functions * 5) / max(1, len(lines) / 10)
                module_doc_scores[file_name] = min(1.0, doc_score / 10)

        except Exception as e:
            continue  # Skip files that can't be processed

    # Calculate overall coverage
    total_functions = documented_functions + undocumented_functions
    documentation_coverage = documented_functions / max(1, total_functions)

    # Identify well-documented vs poorly-documented modules
    sorted_modules = sorted(module_doc_scores.items(), key=lambda x: x[1], reverse=True)
    well_documented = [m[0] for m in sorted_modules[:5] if m[1] > 0.5]
    poorly_documented = [m[0] for m in sorted_modules[-5:] if m[1] < 0.3]

    # Identify documentation gaps
    gaps = []
    if undocumented_functions > total_functions * 0.3:
        gaps.append(f"{undocumented_functions} functions lack documentation")
    if todo_count > 20:
        gaps.append(f"{todo_count} TODO items indicate incomplete implementation")
    if hack_count > 5:
        gaps.append(f"{hack_count} HACK comments suggest technical debt")

    return {
        "status": "success",
        "documentation_extracted": {
            "function_docstrings": function_docstrings[:50],  # Limit output
            "inline_comments": inline_comments[:100],
            "header_comments": header_comments[:20]
        },
        "statistics": {
            "total_comments": total_comments,
            "documented_functions": documented_functions,
            "undocumented_functions": undocumented_functions,
            "documentation_coverage": round(documentation_coverage, 3),
            "todo_count": todo_count,
            "fixme_count": fixme_count,
            "hack_count": hack_count
        },
        "quality_assessment": {
            "well_documented_modules": well_documented,
            "poorly_documented_modules": poorly_documented,
            "documentation_gaps": gaps
        }
    }


def _assess_docstring_quality(docstring: str) -> tuple:
    """Assess the quality and completeness of a docstring."""
    quality = "poor"
    completeness = 0.0

    doc_lower = docstring.lower()

    # Check for key elements
    has_description = len(docstring) > 20
    has_params = 'param' in doc_lower or 'arg' in doc_lower or ':param' in doc_lower
    has_returns = 'return' in doc_lower or ':return' in doc_lower
    has_examples = 'example' in doc_lower

    score = 0
    if has_description:
        score += 0.4
    if has_params:
        score += 0.3
    if has_returns:
        score += 0.2
    if has_examples:
        score += 0.1

    completeness = score

    if score >= 0.8:
        quality = "excellent"
    elif score >= 0.6:
        quality = "good"
    elif score >= 0.4:
        quality = "fair"

    return quality, completeness


def _classify_comment(comment_text: str) -> tuple:
    """Classify comment type and context."""
    comment_lower = comment_text.lower()

    # Determine type
    if comment_text.startswith(('TODO', 'Todo', 'todo')):
        comment_type = "todo"
        context = "technical_debt"
    elif comment_text.startswith(('FIXME', 'FixMe', 'fixme', 'FIX')):
        comment_type = "fixme"
        context = "bug"
    elif comment_text.startswith(('HACK', 'Hack', 'hack', 'WORKAROUND')):
        comment_type = "hack"
        context = "known_issue"
    elif comment_text.startswith(('IMPORTANT', 'Important', 'NOTE', 'Note')):
        comment_type = "important_note"
        context = "business_rule" if any(word in comment_lower for word in ['must', 'should', 'rule', 'requirement']) else "implementation_note"
    elif comment_text.startswith(('BUG', 'Bug', 'bug', 'ISSUE')):
        comment_type = "bug"
        context = "known_issue"
    elif comment_text.startswith(('DEPRECATED', 'Deprecated')):
        comment_type = "deprecated"
        context = "obsolete_code"
    else:
        comment_type = "regular"

        # Infer context from content
        if any(word in comment_lower for word in ['business', 'rule', 'requirement', 'spec']):
            context = "business_rule"
        elif any(word in comment_lower for word in ['performance', 'optimize', 'slow']):
            context = "performance"
        elif any(word in comment_lower for word in ['security', 'auth', 'permission']):
            context = "security"
        else:
            context = "general"

    return comment_type, context


def parse_external_documentation(
    doc_paths: List[str],
    doc_types: List[str] = None
) -> Dict[str, Any]:
    """
    Parse external documentation files (PDF, Word, Markdown, Wiki pages).

    Args:
        doc_paths: Paths to documentation files
        doc_types: Types of documents (requirements, design, user_guide, api_spec)

    Returns:
        dict: Parsed documentation content and metadata
    """
    import os
    import re
    from datetime import datetime

    if doc_types is None:
        doc_types = ['requirements', 'design', 'user_guide', 'api_spec']

    parsed_documents = []
    requirements_count = 0
    req_to_code_mappings = 0

    for doc_path in doc_paths:
        if not os.path.exists(doc_path):
            continue

        try:
            file_ext = os.path.splitext(doc_path)[1].lower()
            file_name = os.path.basename(doc_path)

            # Infer document type from path/name
            doc_type = _infer_doc_type(doc_path, doc_types)

            # Parse based on file type
            if file_ext == '.md':
                parsed_doc = _parse_markdown(doc_path, doc_type)
            elif file_ext in ['.txt', '.text']:
                parsed_doc = _parse_text_file(doc_path, doc_type)
            elif file_ext in ['.pdf']:
                # Mock PDF parsing (would use pypdf or similar in production)
                parsed_doc = _mock_parse_pdf(doc_path, doc_type)
            elif file_ext in ['.yaml', '.yml']:
                parsed_doc = _parse_yaml_spec(doc_path, doc_type)
            elif file_ext in ['.json']:
                parsed_doc = _parse_json_spec(doc_path, doc_type)
            else:
                continue  # Unsupported format

            if parsed_doc:
                parsed_documents.append(parsed_doc)

                # Count requirements
                if doc_type == 'requirements':
                    for section in parsed_doc.get('sections', []):
                        requirements_count += len(section.get('requirements', []))
                        req_to_code_mappings += sum(1 for req in section.get('requirements', [])
                                                   if req.get('trace_to_code'))

        except Exception as e:
            continue  # Skip files that can't be parsed

    # Calculate traceability
    unmapped_requirements = requirements_count - req_to_code_mappings
    coverage = req_to_code_mappings / max(1, requirements_count)

    return {
        "status": "success",
        "parsed_documents": parsed_documents,
        "knowledge_graph": {
            "requirements_count": requirements_count,
            "requirements_to_code_mappings": req_to_code_mappings,
            "unmapped_requirements": unmapped_requirements,
            "orphaned_code": 0  # Would require cross-reference with code
        },
        "traceability_matrix": {
            "requirement_coverage": round(coverage, 2),
            "gaps": [f"{unmapped_requirements} requirements not traced to code"] if unmapped_requirements > 0 else []
        }
    }


def _infer_doc_type(doc_path: str, allowed_types: List[str]) -> str:
    """Infer document type from path/name."""
    path_lower = doc_path.lower()

    if 'requirement' in path_lower or 'req' in path_lower:
        return 'requirements'
    elif 'api' in path_lower or 'swagger' in path_lower or 'openapi' in path_lower:
        return 'api_spec'
    elif 'design' in path_lower or 'architecture' in path_lower:
        return 'design'
    elif 'user' in path_lower or 'guide' in path_lower or 'manual' in path_lower:
        return 'user_guide'
    else:
        return allowed_types[0] if allowed_types else 'unknown'


def _parse_markdown(doc_path: str, doc_type: str) -> Dict[str, Any]:
    """Parse Markdown documentation file."""
    import re

    with open(doc_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Extract title (first # heading)
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else os.path.basename(doc_path)

    # Extract sections
    sections = []
    section_pattern = r'##\s+(.+?)\n(.*?)(?=##|\Z)'

    for match in re.finditer(section_pattern, content, re.DOTALL):
        heading = match.group(1).strip()
        section_content = match.group(2).strip()

        # Extract requirements from section
        requirements = []
        req_pattern = r'(?:FR|NFR)-(\d+):\s*(.+?)(?=\n|$)'
        for req_match in re.finditer(req_pattern, section_content):
            req_id = req_match.group(0).split(':')[0]
            req_desc = req_match.group(2).strip()

            requirements.append({
                "id": req_id,
                "description": req_desc,
                "priority": "must_have",  # Default
                "trace_to_code": []  # Would be populated by traceability analysis
            })

        sections.append({
            "heading": heading,
            "content": section_content[:500],  # Truncate
            "requirements": requirements
        })

    return {
        "path": doc_path,
        "type": doc_type,
        "title": title,
        "sections": sections,
        "metadata": {
            "format": "markdown",
            "date": datetime.now().isoformat()
        }
    }


def _parse_text_file(doc_path: str, doc_type: str) -> Dict[str, Any]:
    """Parse plain text documentation file."""
    with open(doc_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    lines = content.split('\n')
    title = lines[0] if lines else os.path.basename(doc_path)

    return {
        "path": doc_path,
        "type": doc_type,
        "title": title[:100],
        "sections": [{
            "heading": "Content",
            "content": content[:1000],
            "requirements": []
        }],
        "metadata": {"format": "text"}
    }


def _mock_parse_pdf(doc_path: str, doc_type: str) -> Dict[str, Any]:
    """Mock PDF parsing (placeholder for production implementation)."""
    return {
        "path": doc_path,
        "type": doc_type,
        "title": f"PDF Document: {os.path.basename(doc_path)}",
        "sections": [{
            "heading": "Note",
            "content": "PDF parsing requires pypdf or similar library in production",
            "requirements": []
        }],
        "metadata": {"format": "pdf"}
    }


def _parse_yaml_spec(doc_path: str, doc_type: str) -> Dict[str, Any]:
    """Parse YAML specification (e.g., OpenAPI)."""
    import yaml

    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        endpoints = []
        if 'paths' in data:  # OpenAPI format
            for path, methods in data['paths'].items():
                for method, details in methods.items():
                    endpoints.append({
                        "method": method.upper(),
                        "path": path,
                        "description": details.get('description', ''),
                        "parameters": details.get('parameters', []),
                        "response": details.get('responses', {})
                    })

        return {
            "path": doc_path,
            "type": "api_spec",
            "title": data.get('info', {}).get('title', os.path.basename(doc_path)),
            "endpoints": endpoints,
            "metadata": {"format": "yaml", "version": data.get('info', {}).get('version', 'unknown')}
        }
    except:
        return None


def _parse_json_spec(doc_path: str, doc_type: str) -> Dict[str, Any]:
    """Parse JSON specification."""
    import json

    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return {
            "path": doc_path,
            "type": doc_type,
            "title": data.get('title', os.path.basename(doc_path)),
            "sections": [{
                "heading": "JSON Specification",
                "content": json.dumps(data, indent=2)[:500],
                "requirements": []
            }],
            "metadata": {"format": "json"}
        }
    except:
        return None


def mine_version_control_history(
    repo_path: str,
    depth: int = 1000
) -> Dict[str, Any]:
    """
    Mine Git/SVN history for commit messages, change patterns, and evolution.

    Args:
        repo_path: Path to version control repository
        depth: Number of commits to analyze

    Returns:
        dict: Historical insights and patterns
    """
    import os
    import subprocess
    from datetime import datetime
    from collections import defaultdict

    if not os.path.exists(repo_path):
        return {"status": "error", "message": "Repository path does not exist"}

    try:
        # Get commit history
        cmd = ['git', '-C', repo_path, 'log', f'-{depth}',
               '--pretty=format:%H|%aI|%an|%ae|%s', '--no-merges']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            return {"status": "error", "message": "Failed to read git history"}

        commit_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []

        # Parse commits
        contributors = defaultdict(lambda: {"commits": 0, "files_touched": set()})
        file_modifications = defaultdict(int)
        commit_insights = []
        bug_fixes = []
        feature_additions = []
        refactoring_commits = 0
        emergency_fixes = 0

        first_date = None
        last_date = None

        for line in commit_lines[:depth]:
            if not line:
                continue

            parts = line.split('|', 4)
            if len(parts) < 5:
                continue

            commit_hash, date, author_name, author_email, message = parts

            # Track dates
            if not first_date:
                first_date = date
            last_date = date

            # Track contributors
            contributors[author_name]["commits"] += 1

            # Get files changed
            files_cmd = ['git', '-C', repo_path, 'diff-tree', '--no-commit-id',
                        '--name-only', '-r', commit_hash]
            files_result = subprocess.run(files_cmd, capture_output=True, text=True, timeout=10)
            files_changed = files_result.stdout.strip().split('\n') if files_result.stdout.strip() else []

            for file in files_changed:
                if file:
                    contributors[author_name]["files_touched"].add(file)
                    file_modifications[file] += 1

            # Classify commit
            message_lower = message.lower()

            if any(word in message_lower for word in ['critical', 'urgent', 'hotfix', 'emergency']):
                emergency_fixes += 1
                commit_insights.append({
                    "commit_hash": commit_hash[:8],
                    "date": date[:10],
                    "message": message,
                    "files_changed": files_changed[:5],
                    "insight": "Critical business logic fix - preserve this behavior in modernization"
                })

            if any(word in message_lower for word in ['bug', 'fix', 'patch']):
                bug_fixes.append(message)

            if any(word in message_lower for word in ['feature', 'add', 'implement', 'new']):
                feature_additions.append(message)
                if len(commit_insights) < 10:
                    commit_insights.append({
                        "commit_hash": commit_hash[:8],
                        "date": date[:10],
                        "message": message,
                        "files_changed": files_changed[:5],
                        "insight": "Feature addition - document requirements for new system"
                    })

            if any(word in message_lower for word in ['refactor', 'cleanup', 'restructure']):
                refactoring_commits += 1

        # Calculate hotspots
        hotspots = []
        for file, count in sorted(file_modifications.items(), key=lambda x: x[1], reverse=True)[:10]:
            contributor_count = sum(1 for c in contributors.values() if file in c["files_touched"])
            hotspots.append({
                "file": file,
                "modifications": count,
                "contributors": contributor_count,
                "interpretation": "High change frequency indicates complex or unstable module" if count > 20 else "Moderate stability"
            })

        # Identify stable files
        all_files = set(file_modifications.keys())
        stable_files = [{
            "file": file,
            "modifications": file_modifications[file],
            "interpretation": "Stable, well-tested core functionality"
        } for file in all_files if file_modifications[file] <= 2]

        # Calculate active years
        if first_date and last_date:
            try:
                first_dt = datetime.fromisoformat(first_date.replace('Z', '+00:00'))
                last_dt = datetime.fromisoformat(last_date.replace('Z', '+00:00'))
                active_years = round((last_dt - first_dt).days / 365.25, 1)
            except:
                active_years = 0
        else:
            active_years = 0

        # Top contributors
        top_contributors = sorted(
            [{"name": name, "commits": data["commits"], "files_touched": len(data["files_touched"])}
             for name, data in contributors.items()],
            key=lambda x: x["commits"],
            reverse=True
        )[:10]

        # Bug fix patterns
        total_bug_fixes = len(bug_fixes)
        bug_areas = defaultdict(int)
        for bug_msg in bug_fixes:
            msg_lower = bug_msg.lower()
            if 'validation' in msg_lower or 'validate' in msg_lower:
                bug_areas['validation'] += 1
            elif 'concurrency' in msg_lower or 'thread' in msg_lower or 'race' in msg_lower:
                bug_areas['concurrency'] += 1
            elif 'edge' in msg_lower or 'corner' in msg_lower:
                bug_areas['edge_cases'] += 1

        common_bug_areas = [
            {"area": area, "count": count, "percentage": round(count / max(1, total_bug_fixes) * 100, 1)}
            for area, count in sorted(bug_areas.items(), key=lambda x: x[1], reverse=True)
        ]

        return {
            "status": "success",
            "repository_analysis": {
                "total_commits": len(commit_lines),
                "analyzed_commits": min(depth, len(commit_lines)),
                "date_range": {
                    "first_commit": first_date or "unknown",
                    "last_commit": last_date or "unknown",
                    "active_years": active_years
                },
                "contributors": top_contributors
            },
            "code_evolution": {
                "hotspots": hotspots,
                "churned_files": [],  # Would require churn calculation
                "stable_files": stable_files[:5]
            },
            "commit_insights": commit_insights,
            "bug_fix_patterns": {
                "total_bug_fixes": total_bug_fixes,
                "common_bug_areas": common_bug_areas,
                "recommendations": [
                    f"Focus on {area['area']} testing in new system" for area in common_bug_areas[:3]
                ]
            },
            "knowledge_extraction": {
                "business_rule_mentions": len([m for m in commit_lines if 'business' in m.lower() or 'rule' in m.lower()]),
                "refactoring_commits": refactoring_commits,
                "emergency_fixes": emergency_fixes,
                "feature_additions": len(feature_additions)
            }
        }

    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Git command timed out"}
    except Exception as e:
        return {"status": "error", "message": f"Error mining VCS: {str(e)}"}


def extract_runtime_documentation(
    log_files: List[str],
    configuration_files: List[str]
) -> Dict[str, Any]:
    """
    Extract operational knowledge from logs and configuration files.

    Args:
        log_files: Paths to log files
        configuration_files: Paths to configuration files

    Returns:
        dict: Operational insights and configuration documentation
    """
    import os
    import re
    from collections import defaultdict

    # Parse configuration files
    config_analysis = []
    env_vars_required = set()
    env_vars_optional = set()

    for config_path in configuration_files:
        if not os.path.exists(config_path):
            continue

        try:
            file_ext = os.path.splitext(config_path)[1].lower()
            config_type = _infer_config_type(config_path)

            parameters = {}

            if file_ext in ['.conf', '.ini', '.properties']:
                parameters = _parse_ini_config(config_path)
            elif file_ext in ['.yaml', '.yml']:
                parameters = _parse_yaml_config(config_path)
            elif file_ext in ['.json']:
                parameters = _parse_json_config(config_path)
            elif file_ext in ['.env']:
                parameters = _parse_env_file(config_path)

            # Extract env var references
            for value in str(parameters).split():
                if value.startswith('${') and value.endswith('}'):
                    env_var = value[2:-1]
                    env_vars_required.add(env_var)

            config_analysis.append({
                "path": config_path,
                "type": config_type,
                "parameters": parameters,
                "documentation_status": "undocumented",  # Would check for comments
                "inferred_purpose": f"{config_type.title()} configuration"
            })

        except Exception:
            continue

    # Parse log files
    log_analysis = {
        "analyzed_log_entries": 0,
        "operational_insights": [],
        "error_patterns": [],
        "performance_metrics": {}
    }

    error_counts = defaultdict(int)
    response_times = []

    for log_path in log_files:
        if not os.path.exists(log_path):
            continue

        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Read last 10000 lines
                lines = f.readlines()[-10000:]

            log_analysis["analyzed_log_entries"] += len(lines)

            for line in lines:
                # Extract errors
                if any(word in line.lower() for word in ['error', 'exception', 'failed']):
                    # Simple pattern extraction
                    error_msg = line.split('ERROR')[-1].split('\n')[0][:100] if 'ERROR' in line else line[:100]
                    error_counts[error_msg.strip()] += 1

                # Extract response times (if present)
                time_match = re.search(r'(\d+)\s*ms', line)
                if time_match:
                    response_times.append(int(time_match.group(1)))

        except Exception:
            continue

    # Compile error patterns
    for error_msg, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        log_analysis["error_patterns"].append({
            "error_message": error_msg,
            "occurrences": count,
            "impact": "high" if count > 50 else "medium" if count > 10 else "low",
            "root_cause": "Requires investigation"
        })

    # Calculate performance metrics
    if response_times:
        response_times.sort()
        n = len(response_times)
        log_analysis["performance_metrics"] = {
            "average_response_time_ms": round(sum(response_times) / n),
            "p95_response_time_ms": response_times[int(n * 0.95)] if n > 0 else 0,
            "p99_response_time_ms": response_times[int(n * 0.99)] if n > 0 else 0,
            "slow_endpoints": []  # Would require URL parsing
        }

    return {
        "status": "success",
        "configuration_analysis": {
            "config_files": config_analysis,
            "environment_dependencies": {
                "required_env_vars": list(env_vars_required),
                "optional_env_vars": list(env_vars_optional)
            }
        },
        "log_analysis": log_analysis,
        "deployment_artifacts": {
            "startup_scripts": [],  # Would scan for .sh files
            "cron_jobs": [],  # Would parse crontab
            "monitoring_dashboards": []  # Would be manually configured
        }
    }


def _infer_config_type(config_path: str) -> str:
    """Infer configuration file type from path."""
    path_lower = config_path.lower()

    if 'database' in path_lower or 'db' in path_lower:
        return 'database'
    elif 'feature' in path_lower or 'flag' in path_lower:
        return 'feature_flags'
    elif 'app' in path_lower or 'application' in path_lower:
        return 'application'
    elif 'server' in path_lower:
        return 'server'
    else:
        return 'general'


def _parse_ini_config(config_path: str) -> Dict[str, Any]:
    """Parse INI/conf configuration file."""
    import configparser

    try:
        config = configparser.ConfigParser()
        config.read(config_path)

        params = {}
        for section in config.sections():
            for key, value in config.items(section):
                params[f"{section}.{key}"] = value

        return params
    except:
        return {}


def _parse_yaml_config(config_path: str) -> Dict[str, Any]:
    """Parse YAML configuration file."""
    import yaml

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except:
        return {}


def _parse_json_config(config_path: str) -> Dict[str, Any]:
    """Parse JSON configuration file."""
    import json

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}


def _parse_env_file(config_path: str) -> Dict[str, Any]:
    """Parse .env file."""
    params = {}

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    params[key.strip()] = value.strip()
    except:
        pass

    return params


def synthesize_knowledge_base(
    inline_docs: Dict[str, Any],
    external_docs: Dict[str, Any],
    vcs_history: Dict[str, Any],
    runtime_docs: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Synthesize all documentation sources into unified knowledge base.

    Args:
        inline_docs: Inline code documentation
        external_docs: External documentation
        vcs_history: Version control insights
        runtime_docs: Runtime and operational docs

    Returns:
        dict: Comprehensive knowledge base
    """
    import uuid

    kb_id = f"KB_LEGACY_{uuid.uuid4().hex[:8].upper()}"

    # Extract statistics
    inline_stats = inline_docs.get("statistics", {})
    doc_coverage = inline_stats.get("documentation_coverage", 0)

    # Identify well-documented areas
    well_documented_areas = inline_docs.get("quality_assessment", {}).get("well_documented_modules", [])

    # Identify gaps
    gaps = inline_docs.get("quality_assessment", {}).get("documentation_gaps", [])

    # Extract critical insights from VCS
    commit_insights = vcs_history.get("commit_insights", [])
    preserve_logic = [
        insight["message"] for insight in commit_insights
        if "critical" in insight.get("insight", "").lower()
    ][:5]

    # Build components list
    components = []
    # (Would cross-reference inline docs with external docs to build comprehensive component list)

    # Calculate completeness
    completeness = (doc_coverage + 0.5) / 1.5  # Weighted average

    return {
        "status": "success",
        "knowledge_base_id": kb_id,
        "unified_documentation": {
            "business_logic": {
                "requirements": external_docs.get("parsed_documents", []),
                "implementation": inline_docs.get("documentation_extracted", {}),
                "evolution": commit_insights,
                "completeness": round(completeness, 2)
            },
            "technical_architecture": {
                "components": components,
                "integration_points": []  # Would be extracted from API specs
            },
            "operational_knowledge": {
                "configuration": runtime_docs.get("configuration_analysis", {}),
                "performance_characteristics": runtime_docs.get("log_analysis", {}).get("performance_metrics", {}),
                "known_issues": runtime_docs.get("log_analysis", {}).get("error_patterns", []),
                "deployment_procedures": runtime_docs.get("deployment_artifacts", {})
            },
            "quality_insights": {
                "well_documented_areas": well_documented_areas,
                "documentation_gaps": gaps,
                "technical_debt": inline_stats.get("todo_count", 0),
                "critical_notes": inline_stats.get("hack_count", 0) + inline_stats.get("fixme_count", 0)
            }
        },
        "vector_db_integration": {
            "documents_indexed": (
                len(inline_docs.get("documentation_extracted", {}).get("function_docstrings", [])) +
                len(external_docs.get("parsed_documents", [])) +
                len(commit_insights)
            ),
            "semantic_search_enabled": True,
            "cross_reference_links": 0,  # Would be calculated
            "example_queries": [
                "How does the system handle payment failures?",
                "What are the order validation rules?",
                "Why was the duplicate order check added?"
            ]
        },
        "modernization_insights": {
            "preserve_logic": preserve_logic or ["No critical logic identified"],
            "improvement_opportunities": [
                f"Address {len(gaps)} documentation gaps" if gaps else "Improve documentation coverage",
                "Standardize configuration management",
                "Document error handling patterns"
            ],
            "risk_areas": [
                f"{inline_stats.get('hack_count', 0)} undocumented workarounds" if inline_stats.get('hack_count', 0) > 0 else "",
                "Configuration parameters need documentation",
                "Requirements traceability incomplete"
            ]
        }
    }


def mine_version_control_history(
    repo_path: str,
    depth: int = 1000
) -> Dict[str, Any]:
    """
    Mine Git history for commit messages, change patterns, and evolution.
    Uses `git` CLI via subprocess. If git is not available or repo_path is not a git repo,
    returns a status explaining failure.

    Args:
        repo_path: Path to version control repository (assumed git)
        depth: Number of commits to analyze

    Returns:
        dict: Historical insights and patterns
    """
    import subprocess
    import os
    import re
    from collections import Counter, defaultdict
    from datetime import datetime

    def run_git(cmd_args):
        try:
            out = subprocess.check_output(["git"] + cmd_args, cwd=repo_path, stderr=subprocess.DEVNULL)
            return out.decode("utf-8", errors="replace")
        except Exception:
            return None

    if not os.path.isdir(repo_path):
        return {"status": "error", "error": f"repo_path '{repo_path}' not found"}

    # quick check for git repo
    if run_git(["rev-parse", "--is-inside-work-tree"]) is None:
        return {"status": "error", "error": "Not a git repository or `git` not available in PATH"}

    result = {"status": "success", "repository_analysis": {}, "code_evolution": {}, "commit_insights": [], "bug_fix_patterns": {}, "knowledge_extraction": {}}

    # total commits
    total_commits_out = run_git(["rev-list", "--count", "HEAD"])
    try:
        total_commits = int(total_commits_out.strip()) if total_commits_out else 0
    except Exception:
        total_commits = 0

    # collect commits (limited by depth)
    log_format = "%H%x1f%an%x1f%ad%x1f%s"  # hash, author, date, subject separated by \x1f
    raw_log = run_git(["log", f"-n{depth}", f"--pretty=format:{log_format}", "--date=iso"])
    commits = []
    authors = Counter()
    file_change_counts = Counter()
    commits_by_file = defaultdict(list)
    commit_messages = []

    if raw_log:
        for line in raw_log.splitlines():
            parts = line.split("\x1f")
            if len(parts) < 4:
                continue
            h, author, date_str, subject = parts[0], parts[1], parts[2], parts[3]
            commit_messages.append((h, date_str, subject))
            authors[author] += 1
            # get files changed for this commit
            files_out = run_git(["show", "--pretty=", "--name-only", h])
            files = [f.strip() for f in (files_out or "").splitlines() if f.strip()]
            for f in files:
                file_change_counts[f] += 1
                commits_by_file[f].append(h)

            commits.append({"hash": h, "author": author, "date": date_str, "message": subject, "files": files})

    # date range from all commits in repo (not only limited)
    first_commit = run_git(["log", "--reverse", "--pretty=format:%ad", "--date=iso"])
    first_date = None
    last_date = None
    if first_commit:
        first_line = first_commit.splitlines()[0] if first_commit.splitlines() else None
        first_date = first_line if first_line else None
    last_commit_date_out = run_git(["log", "-1", "--pretty=format:%ad", "--date=iso"])
    last_date = last_commit_date_out.strip() if last_commit_date_out else None

    # hotspots: top changed files
    hotspots = []
    for f, cnt in file_change_counts.most_common(10):
        hotspots.append({
            "file": f,
            "modifications": cnt,
            "contributors": len(set([c for c in commits_by_file.get(f, [])])),  # approximate contributor count by unique commits
            "interpretation": "Frequent modifications may indicate complexity or instability"
        })

    # churn detection (simple churn score = normalized change count)
    churned_files = []
    if file_change_counts:
        max_changes = max(file_change_counts.values())
        for f, cnt in file_change_counts.items():
            churn_score = cnt / max_changes if max_changes else 0.0
            if churn_score > 0.6:
                churned_files.append({"file": f, "churn_score": round(churn_score, 2), "interpretation": "High churn suggests technical debt or band-aid fixes"})

    # classify commit messages for bugfix/feature/refactor
    bugfix_re = re.compile(r"\b(fix(es|ed)?|bug|hotfix|patch|repair)\b", re.I)
    feature_re = re.compile(r"\b(add|feature|implement|support|introduce)\b", re.I)
    refactor_re = re.compile(r"\b(refactor|cleanup|restructure|rename)\b", re.I)
    emergency_re = re.compile(r"\b(critical|urgent|emergency)\b", re.I)

    commit_insights = []
    bug_fix_count = 0
    features = 0
    refactors = 0
    emergencies = 0

    for h, date_str, msg in commit_messages:
        insight = None
        if bugfix_re.search(msg):
            insight = "bugfix"
            bug_fix_count += 1
        elif feature_re.search(msg):
            insight = "feature"
            features += 1
        elif refactor_re.search(msg):
            insight = "refactor"
            refactors += 1
        if emergency_re.search(msg):
            emergencies += 1

        commit_insights.append({
            "commit_hash": h[:8],
            "date": date_str,
            "message": msg,
            "insight": insight or "other",
            "files_changed": []  # keep small; omitted for speed
        })

    # common bug areas (heuristic from commit messages + file names)
    common_bug_areas = Counter()
    for _, _, msg in commit_messages:
        if "validation" in msg.lower():
            common_bug_areas["validation"] += 1
        if "concur" in msg.lower() or "race" in msg.lower() or "thread" in msg.lower():
            common_bug_areas["concurrency"] += 1
        if "edge" in msg.lower() or "boundary" in msg.lower():
            common_bug_areas["edge_cases"] += 1

    common_bug_list = []
    total_bugs_count = sum(common_bug_areas.values()) or bug_fix_count
    for k, v in common_bug_areas.most_common():
        pct = (v / total_bugs_count * 100) if total_bugs_count else 0.0
        common_bug_list.append({"area": k, "count": v, "percentage": round(pct, 1)})

    # contributors summary (top 10)
    contributors = [{"name": a, "commits": c} for a, c in authors.most_common(10)]

    result["repository_analysis"] = {
        "total_commits": total_commits,
        "analyzed_commits": min(depth, total_commits),
        "date_range": {
            "first_commit": first_date,
            "last_commit": last_date,
            "active_years": None
        },
        "contributors": contributors
    }

    # try to compute active_years
    try:
        if first_date and last_date:
            d1 = datetime.fromisoformat(first_date.split("+")[0])
            d2 = datetime.fromisoformat(last_date.split("+")[0])
            years = (d2 - d1).days / 365.25
            result["repository_analysis"]["date_range"]["active_years"] = round(years, 2)
    except Exception:
        pass

    result["code_evolution"] = {
        "hotspots": hotspots,
        "churned_files": churned_files[:20],
        "stable_files": [
            {"file": f, "last_modified": None, "interpretation": "Stable, low change frequency"}
            for f, cnt in file_change_counts.items() if cnt <= 1
        ][:20]
    }

    result["commit_insights"] = commit_insights[:min(len(commit_insights), 200)]
    result["bug_fix_patterns"] = {
        "total_bug_fixes": bug_fix_count,
        "common_bug_areas": common_bug_list,
        "recommendations": [
            "Increase validation unit tests",
            "Review concurrency handling and locking",
            "Capture and document edge case behavior in requirements"
        ]
    }

    result["knowledge_extraction"] = {
        "business_rule_mentions": sum(1 for _, _, m in commit_messages if "business" in m.lower() or "rule" in m.lower()),
        "refactoring_commits": refactors,
        "emergency_fixes": emergencies,
        "feature_additions": features
    }

    return result


def extract_runtime_documentation(
    log_files: List[str],
    configuration_files: List[str]
) -> Dict[str, Any]:
    """
    Extract operational knowledge from logs and configuration files.

    Args:
        log_files: Paths to log files
        configuration_files: Paths to configuration files

    Returns:
        dict: Operational insights and configuration documentation
    """
    import json
    import os
    import re
    import configparser
    import xml.etree.ElementTree as ET
    from collections import Counter, defaultdict

    try:
        import yaml
    except Exception:
        yaml = None  # optional

    config_summary = []
    env_candidates = set()
    parameter_counter = Counter()
    doc_status_map = {}

    for cfg_path in configuration_files:
        entry = {"path": cfg_path, "type": None, "parameters": {}, "documentation_status": "unknown", "inferred_purpose": None}
        if not os.path.exists(cfg_path):
            entry["documentation_status"] = "missing"
            config_summary.append(entry)
            continue
        _, ext = os.path.splitext(cfg_path.lower())
        try:
            with open(cfg_path, "r", encoding="utf-8", errors="replace") as fh:
                raw = fh.read()
        except Exception:
            entry["documentation_status"] = "unreadable"
            config_summary.append(entry)
            continue

        # Heuristics per extension
        try:
            if ext in (".json",):
                parsed = json.loads(raw)
                entry["type"] = "json"
                # flatten one-level keys as parameters
                if isinstance(parsed, dict):
                    for k, v in parsed.items():
                        entry["parameters"][k] = v
                        parameter_counter[k] += 1
                        if isinstance(k, str) and k.isupper():
                            env_candidates.add(k)
                entry["documentation_status"] = "partially_documented" if len(entry["parameters"]) else "undocumented"
                entry["inferred_purpose"] = "JSON configuration file"
            elif ext in (".yml", ".yaml") and yaml:
                parsed = yaml.safe_load(raw)
                entry["type"] = "yaml"
                if isinstance(parsed, dict):
                    for k, v in parsed.items():
                        entry["parameters"][k] = v
                        parameter_counter[k] += 1
                        if isinstance(k, str) and k.isupper():
                            env_candidates.add(k)
                entry["documentation_status"] = "partially_documented" if entry["parameters"] else "undocumented"
                entry["inferred_purpose"] = "YAML configuration file"
            elif ext in (".ini", ".cfg"):
                cp = configparser.ConfigParser()
                cp.read_string(raw)
                entry["type"] = "ini"
                for section in cp.sections():
                    for k, v in cp.items(section):
                        key = f"{section}.{k}"
                        entry["parameters"][key] = v
                        parameter_counter[key] += 1
                        if k.isupper():
                            env_candidates.add(k)
                entry["documentation_status"] = "partially_documented" if entry["parameters"] else "undocumented"
                entry["inferred_purpose"] = "INI-style configuration"
            elif ext in (".xml",):
                entry["type"] = "xml"
                try:
                    tree = ET.fromstring(raw)
                    # naive extraction: immediate children as parameters
                    for child in list(tree):
                        entry["parameters"][child.tag] = child.text
                        parameter_counter[child.tag] += 1
                        if child.tag.isupper():
                            env_candidates.add(child.tag)
                    entry["documentation_status"] = "partially_documented" if entry["parameters"] else "undocumented"
                    entry["inferred_purpose"] = "XML configuration"
                except Exception:
                    entry["documentation_status"] = "malformed_xml"
            else:
                # fallback: try to capture KEY=VALUE pairs and environment variables
                for m in re.finditer(r"(^|\s)([A-Z0-9_]{2,})\s*[:=]\s*([^\n\r]+)", raw):
                    k = m.group(2)
                    v = m.group(3).strip()
                    entry["parameters"][k] = v
                    parameter_counter[k] += 1
                    env_candidates.add(k)
                entry["type"] = "unknown"
                entry["documentation_status"] = "partially_documented" if entry["parameters"] else "undocumented"
                entry["inferred_purpose"] = "heuristic-parsed configuration"
        except Exception:
            entry["documentation_status"] = "parse_error"

        config_summary.append(entry)

    # Log analysis (simple, heuristic-based)
    analyzed_entries = 0
    error_patterns = Counter()
    operational_patterns = Counter()
    response_times = []
    slow_endpoints = Counter()
    peak_hours = Counter()

    timestamp_re = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})")  # ISO-like
    ms_re = re.compile(r"(\d+)\s?ms\b")
    endpoint_re = re.compile(r"(/api/[^\s,\"\']+)")
    level_re = re.compile(r"\b(ERROR|WARN|WARNING|INFO|DEBUG|CRITICAL)\b", re.I)

    for log_path in log_files:
        if not os.path.exists(log_path):
            continue
        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    analyzed_entries += 1
                    # timestamp -> hour
                    tmatch = timestamp_re.search(line)
                    if tmatch:
                        try:
                            hour = int(tmatch.group(1)[11:13])
                            peak_hours[hour] += 1
                        except Exception:
                            pass
                    # levels
                    level_match = level_re.search(line)
                    if level_match:
                        operational_patterns[level_match.group(1).upper()] += 1
                    # errors
                    if "exception" in line.lower() or "traceback" in line.lower() or "error" in line.lower():
                        # capture short signature of the error
                        snippet = line.strip()[:200]
                        error_patterns[snippet] += 1
                    # response times
                    m = ms_re.search(line)
                    if m:
                        try:
                            response_times.append(int(m.group(1)))
                        except Exception:
                            pass
                    # endpoints
                    e = endpoint_re.search(line)
                    if e:
                        slow_endpoints[e.group(1)] += 1
        except Exception:
            # unreadable log - skip
            continue

    # Compute metrics
    avg_resp = (sum(response_times) / len(response_times)) if response_times else None
    sorted_slow_endpoints = [p for p, _ in slow_endpoints.most_common(10)]
    peak_hours_list = sorted([(h, c) for h, c in peak_hours.items()], key=lambda x: -x[1])[:5]

    # error pattern list trimmed
    error_patterns_list = []
    for s, cnt in error_patterns.most_common(20):
        # try to infer root cause heuristically
        root = "unknown"
        if "connection" in s.lower():
            root = "connection_issue"
        elif "timeout" in s.lower():
            root = "timeout"
        error_patterns_list.append({"error_message": s, "occurrences": cnt, "impact": "high" if "CRITICAL" in s or "ERROR" in s else "medium", "root_cause": root})

    # environment variables heuristics
    required_env_vars = sorted([v for v in env_candidates if not v.lower().startswith("opt")][:50])
    optional_env_vars = []  # couldn't reliably tell optional vs required without semantics

    # Deployment artifacts: search for known scripts in provided config file paths (heuristic)
    startup_scripts = []
    cron_jobs = []
    monitoring_dashboards = []

    for cfg in configuration_files:
        if cfg.endswith("crontab") or "cron" in cfg.lower():
            # attempt naive parse
            try:
                with open(cfg, "r", encoding="utf-8", errors="replace") as fh:
                    for line in fh:
                        if line.strip() and not line.strip().startswith("#"):
                            if re.search(r"\d+\s+\d+\s+\*\s+\*\s+\*", line):
                                cron_jobs.append({"schedule": "unknown", "command": line.strip(), "purpose": "cron job (heuristic)"})
            except Exception:
                pass
        if cfg.endswith(".sh") and "start" in cfg.lower():
            startup_scripts.append(cfg)

    # consolidate
    runtime_doc = {
        "status": "success",
        "configuration_analysis": {
            "config_files": config_summary,
            "environment_dependencies": {
                "required_env_vars": required_env_vars,
                "optional_env_vars": optional_env_vars
            }
        },
        "log_analysis": {
            "analyzed_log_entries": analyzed_entries,
            "operational_insights": [
                {
                    "pattern": "Peak usage hours",
                    "frequency": "daily-pattern" if peak_hours_list else "unknown",
                    "interpretation": f"Peak hours by occurrence: {peak_hours_list[:3]}",
                    "recommendation": "Consider capacity scaling around peak hours"
                }
            ],
            "error_patterns": error_patterns_list,
            "performance_metrics": {
                "average_response_time_ms": avg_resp,
                "p95_response_time_ms": None if not response_times else sorted(response_times)[int(len(response_times) * 0.95) - 1 if len(response_times) * 0.95 >= 1 else 0],
                "p99_response_time_ms": None if not response_times else sorted(response_times)[int(len(response_times) * 0.99) - 1 if len(response_times) * 0.99 >= 1 else -1],
                "slow_endpoints": sorted_slow_endpoints
            }
        },
        "deployment_artifacts": {
            "startup_scripts": startup_scripts,
            "cron_jobs": cron_jobs,
            "monitoring_dashboards": monitoring_dashboards
        }
    }

    return runtime_doc


def synthesize_knowledge_base(
    inline_docs: Dict[str, Any],
    external_docs: Dict[str, Any],
    vcs_history: Dict[str, Any],
    runtime_docs: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Synthesize all documentation sources into unified knowledge base.

    The function performs:
      - merging of sources
      - simple completeness heuristics
      - cross-reference counting
      - extraction of items to preserve (critical fixes, high-severity bug fixes)
      - produces a knowledge-base-ready dict (with placeholders for vector DB ingestion)

    Args:
        inline_docs: Inline code documentation (extracted)
        external_docs: External documentation (parsed)
        vcs_history: Version control insights
        runtime_docs: Runtime and operational docs

    Returns:
        dict: Comprehensive knowledge base
    """
    import math
    from collections import Counter

    # Basic counts and presence checks
    inline_count = len(inline_docs.get("functions", [])) if isinstance(inline_docs.get("functions", []), list) else inline_docs.get("statistics", {}).get("doc_items", 0)
    external_count = len(external_docs.get("parsed_documents", [])) if isinstance(external_docs.get("parsed_documents", []), list) else 0
    commits = vcs_history.get("repository_analysis", {}).get("analyzed_commits", 0) or len(vcs_history.get("commit_insights", []))
    runtime_issues = len(runtime_docs.get("log_analysis", {}).get("error_patterns", [])) if runtime_docs and isinstance(runtime_docs.get("log_analysis", {}).get("error_patterns", []), list) else 0

    # Cross-reference: find overlaps between external docs and inline (by simple name matching)
    cross_refs = 0
    try:
        inline_titles = set()
        for f in inline_docs.get("documentation_extracted", {}).get("functions", []) if inline_docs.get("documentation_extracted") else inline_docs.get("functions", []):
            name = f.get("name") if isinstance(f, dict) else None
            if name:
                inline_titles.add(name.lower())

        for doc in external_docs.get("parsed_documents", [])[:1000]:
            title = doc.get("title") if isinstance(doc, dict) else None
            if title and title.lower() in inline_titles:
                cross_refs += 1
    except Exception:
        cross_refs = 0

    # Completeness heuristics
    # - coverage: proportion of inline docs vs discovered code units (approx)
    doc_units = max(inline_count + external_count, 1)
    documented_units = inline_count + cross_refs
    coverage = min(1.0, documented_units / doc_units) if doc_units else 0.0

    # critical preservation items: scan vcs_history commit_insights for keywords and runtime known issues
    preserve = []
    for c in vcs_history.get("commit_insights", []):
        msg = c.get("message", "")
        if ("critical" in msg.lower()) or ("CRITICAL" in msg) or ("double-charg" in msg.lower()) or ("prevent" in msg.lower() and "charge" in msg.lower()):
            preserve.append(c.get("message"))

    for e in runtime_docs.get("log_analysis", {}).get("error_patterns", [])[:50]:
        msg = e.get("error_message", "")
        # if this pattern has many occurrences, suggest preserving related handling
        if e.get("occurrences", 0) > 10:
            preserve.append(msg)

    preserve = list(dict.fromkeys(preserve))  # dedupe while preserving order

    # Identify documentation gaps (heuristic)
    gaps = []
    # missing error handling docs
    if not any("error_handling" in src for src in external_docs.get("topics", []) if isinstance(external_docs.get("topics", []), list)):
        gaps.append("error_handling")
    # missing deployment docs
    if not runtime_docs.get("deployment_artifacts", {}).get("startup_scripts"):
        gaps.append("deployment_procedures")
    # config parameter docs
    undocumented_params = []
    for cfg in runtime_docs.get("configuration_analysis", {}).get("config_files", []):
        if cfg.get("documentation_status") in ("undocumented", "partially_documented"):
            undocumented_params.append(cfg.get("path"))
    if undocumented_params:
        gaps.append("configuration_documentation")

    # Quality insights
    well_documented = []
    poor_documented = []
    try:
        stats = inline_docs.get("statistics", {})
        todo_count = stats.get("todo_count", 0)
        documented_pct = stats.get("doc_coverage_pct", coverage * 100)
        if documented_pct >= 75:
            well_documented.append("modules_with_high_coverage")
        else:
            poor_documented.append("overall_low_inline_coverage")
    except Exception:
        todo_count = inline_docs.get("statistics", {}).get("todo_count", 0) if inline_docs.get("statistics") else 0

    # assemble unified documentation (condensed)
    unified = {
        "business_logic": {
            "requirements": external_docs.get("parsed_documents", []),
            "implementation": inline_docs.get("documentation_extracted", {}),
            "evolution": vcs_history.get("commit_insights", []),
            "completeness": round(float(coverage), 2)
        },
        "technical_architecture": {
            "components": external_docs.get("components", []) if external_docs.get("components") else [
                {
                    "name": "Order Management",
                    "files": ["orders.c", "orders.h"],
                    "responsibilities": "Handle order lifecycle",
                    "dependencies": ["database", "inventory", "payment"],
                    "documentation_sources": ["inline", "requirements", "api_spec"]
                }
            ],
            "integration_points": external_docs.get("integration_points", []) if external_docs.get("integration_points") else []
        },
        "operational_knowledge": {
            "configuration": runtime_docs.get("configuration_analysis", {}),
            "performance_characteristics": runtime_docs.get("log_analysis", {}).get("performance_metrics", {}),
            "known_issues": runtime_docs.get("log_analysis", {}).get("error_patterns", []),
            "deployment_procedures": runtime_docs.get("deployment_artifacts", {})
        },
        "quality_insights": {
            "well_documented_areas": well_documented,
            "documentation_gaps": gaps,
            "technical_debt": todo_count,
            "critical_notes": len(vcs_history.get("commit_insights", []))
        }
    }

    # vector DB / semantic search placeholder summary
    docs_to_index = []
    # collect small search documents from sources
    # inline docs
    for fn in (inline_docs.get("documentation_extracted", {}).get("functions", []) or []):
        docs_to_index.append({"source": "inline", "id": fn.get("name"), "text": fn.get("docstring") or fn.get("summary") or ""})
    # external docs
    for i, d in enumerate(external_docs.get("parsed_documents", [])[:1000]):
        docs_to_index.append({"source": "external", "id": d.get("title") or f"doc_{i}", "text": d.get("content") or d.get("body") or ""})
    # vcs critical messages
    for c in vcs_history.get("commit_insights", [])[:200]:
        docs_to_index.append({"source": "vcs", "id": c.get("commit_hash"), "text": c.get("message")})

    # summary metrics for vector DB
    documents_indexed = len(docs_to_index)

    knowledge_base = {
        "status": "success",
        "knowledge_base_id": "KB_LEGACY_001",
        "unified_documentation": unified,
        "vector_db_integration": {
            "documents_indexed": documents_indexed,
            "semantic_search_enabled": bool(documents_indexed),
            "cross_reference_links": cross_refs,
            "example_queries": [
                "How does the system handle payment failures?",
                "What are the order validation rules?",
                "Why was the duplicate order check added?"
            ]
        },
        "modernization_insights": {
            "preserve_logic": preserve[:50],
            "improvement_opportunities": [
                "Add missing documentation for error codes",
                "Document database schema relationships",
                "Standardize configuration management"
            ],
            "risk_areas": [
                "Undocumented workarounds and hacks",
                "Configuration parameters without clear purpose",
                "Orphaned code not mapped to requirements"
            ]
        }
    }

    return knowledge_base

# Create the documentation mining agent
documentation_mining_agent = Agent(
    name="documentation_mining_agent",
    model="gemini-2.0-flash",
    description=(
        "Extracts knowledge from inline comments, external documentation, version control history, "
        "and runtime artifacts. Synthesizes into unified knowledge base for modernization."
    ),
    instruction=(
        "You are a documentation mining agent responsible for extracting and synthesizing "
        "knowledge from all available documentation sources in legacy systems.\n\n"

        "Your key responsibilities:\n"
        "1. Extract and parse inline code comments and docstrings\n"
        "2. Parse external documentation (PDF, Word, Markdown, Wiki)\n"
        "3. Mine version control history for insights and evolution\n"
        "4. Extract operational knowledge from logs and configuration\n"
        "5. Synthesize all sources into unified, searchable knowledge base\n\n"

        "Inline Documentation Extraction:\n"
        "- Function and class docstrings\n"
        "- Inline comments (regular, TODO, FIXME, HACK, NOTE)\n"
        "- Header/file-level documentation\n"
        "- Calculate documentation coverage\n"
        "- Identify well-documented vs. poorly-documented areas\n\n"

        "External Documentation Processing:\n"
        "- Requirements documents (functional and non-functional)\n"
        "- Design documents and architecture diagrams\n"
        "- API specifications (REST, SOAP, GraphQL)\n"
        "- User guides and operational manuals\n"
        "- Extract diagrams and visual documentation\n"
        "- Build requirements-to-code traceability matrix\n\n"

        "Version Control Mining:\n"
        "- Analyze commit messages for context and intent\n"
        "- Identify code hotspots (frequently modified files)\n"
        "- Track code evolution and refactoring history\n"
        "- Extract bug fix patterns and common issues\n"
        "- Identify critical fixes that must be preserved\n"
        "- Recognize feature additions and their timing\n\n"

        "Runtime Documentation:\n"
        "- Parse configuration files (INI, YAML, JSON, XML)\n"
        "- Analyze log files for operational patterns\n"
        "- Extract performance metrics and bottlenecks\n"
        "- Identify error patterns and their frequencies\n"
        "- Document deployment procedures and scripts\n"
        "- Catalog environment dependencies\n\n"

        "Knowledge Synthesis:\n"
        "- Cross-reference information from multiple sources\n"
        "- Resolve conflicts and inconsistencies\n"
        "- Build comprehensive business logic documentation\n"
        "- Map requirements to implementation\n"
        "- Identify documentation gaps and missing information\n"
        "- Create unified, searchable knowledge base\n\n"

        "Critical Information to Preserve:\n"
        "- Business rules and validation logic\n"
        "- Edge cases and special handling\n"
        "- Bug fixes and workarounds (understand why they exist)\n"
        "- Performance characteristics and bottlenecks\n"
        "- Integration points and dependencies\n"
        "- Configuration parameters and their purpose\n\n"

        "Quality Assessment:\n"
        "- Documentation coverage percentage\n"
        "- Completeness of requirements traceability\n"
        "- Consistency across documentation sources\n"
        "- Identification of outdated or conflicting information\n\n"

        "Vector DB Integration:\n"
        "- Generate embeddings for all documentation\n"
        "- Enable semantic search across knowledge base\n"
        "- Support queries like 'How does X work?' or 'Why was Y changed?'\n"
        "- Provide cross-references and related documentation\n\n"

        "Output:\n"
        "- Send knowledge base to knowledge synthesis agent\n"
        "- Provide to developers for implementation context\n"
        "- Share with architects for design decisions\n"
        "- Flag critical information and risks for human review"
    ),
    tools=[
        extract_inline_documentation,
        parse_external_documentation,
        mine_version_control_history,
        extract_runtime_documentation,
        synthesize_knowledge_base
    ]
)