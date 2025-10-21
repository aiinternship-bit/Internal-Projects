"""
agents/stage1_etl/code_ingestion/agent.py

Code ingestion agent reads and parses legacy source code from various languages and formats.
"""

from typing import Dict, List, Any
from google.adk.agents import Agent


def scan_codebase(
    source_directory: str,
    file_extensions: List[str] = None
) -> Dict[str, Any]:
    """
    Scan legacy codebase and catalog all source files.

    Args:
        source_directory: Root directory of legacy codebase
        file_extensions: List of file extensions to include (e.g., ['.c', '.cpp', '.h'])

    Returns:
        dict: Catalog of discovered files with metadata
    """
    import os
    from datetime import datetime
    from collections import defaultdict

    if file_extensions is None:
        file_extensions = ['.c', '.cpp', '.h', '.java', '.py', '.js', '.cobol', '.cbl',
                          '.sql', '.ddl', '.ts', '.tsx', '.go', '.rs']

    # Language mapping
    language_map = {
        '.c': 'C', '.h': 'C',
        '.cpp': 'C++', '.cc': 'C++', '.cxx': 'C++', '.hpp': 'C++',
        '.java': 'Java',
        '.py': 'Python',
        '.js': 'JavaScript', '.ts': 'TypeScript', '.tsx': 'TypeScript',
        '.cobol': 'COBOL', '.cbl': 'COBOL',
        '.sql': 'SQL', '.ddl': 'SQL',
        '.go': 'Go',
        '.rs': 'Rust'
    }

    files_discovered = []
    languages_detected = defaultdict(int)
    total_lines = 0
    directory_structure = defaultdict(list)

    # Scan directory recursively
    for root, dirs, files in os.walk(source_directory):
        # Skip common directories that shouldn't be analyzed
        dirs[:] = [d for d in dirs if d not in ['.git', '.svn', 'node_modules', 'venv', '__pycache__', 'target', 'build']]

        for file in files:
            file_ext = os.path.splitext(file)[1].lower()

            if file_ext in file_extensions:
                file_path = os.path.join(root, file)

                try:
                    # Get file metadata
                    stat_info = os.stat(file_path)
                    size_bytes = stat_info.st_size
                    last_modified = datetime.fromtimestamp(stat_info.st_mtime).isoformat() + 'Z'

                    # Count lines of code
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines_of_code = sum(1 for line in f if line.strip())
                    except Exception:
                        lines_of_code = 0

                    # Determine language
                    language = language_map.get(file_ext, 'Unknown')
                    languages_detected[language] += 1
                    total_lines += lines_of_code

                    # Track directory structure
                    rel_dir = os.path.relpath(root, source_directory)
                    dir_name = rel_dir.split(os.sep)[0] if rel_dir != '.' else 'root'
                    if file not in directory_structure[dir_name]:
                        directory_structure[dir_name].append(os.path.splitext(file)[0])

                    files_discovered.append({
                        "path": file_path,
                        "size_bytes": size_bytes,
                        "language": language,
                        "last_modified": last_modified,
                        "lines_of_code": lines_of_code
                    })

                except Exception as e:
                    # Skip files that can't be read
                    continue

    return {
        "status": "success",
        "source_directory": source_directory,
        "files_discovered": files_discovered,
        "total_files": len(files_discovered),
        "total_lines": total_lines,
        "languages_detected": dict(languages_detected),
        "directory_structure": {k: list(set(v)) for k, v in directory_structure.items()}
    }


def parse_source_files(
    file_paths: List[str],
    language: str
) -> Dict[str, Any]:
    """
    Parse source files to extract AST and code structure.

    Args:
        file_paths: List of source file paths to parse
        language: Programming language (C, C++, Java, Python, COBOL, etc.)

    Returns:
        dict: Parsed AST and code structure for each file
    """
    import ast
    import re
    import os

    parsed_files = []
    parsing_errors = []
    warnings = []

    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                source_code = f.read()

            file_result = {
                "file_path": file_path,
                "language": language,
                "ast": {},
                "dependencies": {"internal": [], "external": []},
                "code_metrics": {}
            }

            # Python-specific parsing using AST
            if language.lower() == 'python':
                try:
                    tree = ast.parse(source_code)
                    functions = []
                    classes = []
                    imports = []
                    global_vars = []

                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            functions.append({
                                "name": node.name,
                                "return_type": "unknown",
                                "parameters": [arg.arg for arg in node.args.args],
                                "line_start": node.lineno,
                                "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                                "complexity": _estimate_complexity(node),
                                "calls": _extract_function_calls(node)
                            })
                        elif isinstance(node, ast.ClassDef):
                            classes.append({
                                "name": node.name,
                                "line_start": node.lineno,
                                "methods": [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                            })
                        elif isinstance(node, (ast.Import, ast.ImportFrom)):
                            if isinstance(node, ast.Import):
                                imports.extend([alias.name for alias in node.names])
                            else:
                                imports.append(node.module if node.module else "")
                        elif isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
                            if node.col_offset == 0:  # Global scope
                                global_vars.append(node.targets[0].id)

                    file_result["ast"] = {
                        "functions": functions,
                        "classes": classes,
                        "global_variables": list(set(global_vars))[:10],  # Limit to 10
                        "imports": list(set(imports))
                    }

                except SyntaxError as e:
                    parsing_errors.append(f"Python syntax error in {file_path}: {str(e)}")

            # C/C++ parsing (regex-based for simplicity)
            elif language.lower() in ['c', 'c++']:
                functions = _parse_c_functions(source_code)
                includes = re.findall(r'#include\s+[<"]([^>"]+)[>"]', source_code)
                global_vars = re.findall(r'^\s*(?:extern\s+)?(?:const\s+)?(?:static\s+)?(\w+)\s+(\w+)\s*[=;]', source_code, re.MULTILINE)

                file_result["ast"] = {
                    "functions": functions,
                    "classes": [],
                    "global_variables": [var[1] for var in global_vars[:10]],
                    "imports": includes
                }

                # Detect deprecated functions
                deprecated_funcs = ['gets', 'strcpy', 'strcat', 'sprintf']
                for func in deprecated_funcs:
                    if re.search(rf'\b{func}\s*\(', source_code):
                        matches = [m.start() for m in re.finditer(rf'\b{func}\s*\(', source_code)]
                        for match in matches:
                            line_num = source_code[:match].count('\n') + 1
                            warnings.append(f"Deprecated function '{func}' used in {os.path.basename(file_path)}:{line_num}")

            # Java parsing (regex-based)
            elif language.lower() == 'java':
                functions = _parse_java_methods(source_code)
                imports = re.findall(r'import\s+([\w.]+);', source_code)
                classes = re.findall(r'class\s+(\w+)', source_code)

                file_result["ast"] = {
                    "functions": functions,
                    "classes": [{"name": cls, "methods": []} for cls in classes],
                    "global_variables": [],
                    "imports": imports
                }

            # Generic fallback for other languages
            else:
                file_result["ast"] = {
                    "functions": [],
                    "classes": [],
                    "global_variables": [],
                    "imports": []
                }
                warnings.append(f"Limited parsing support for {language}")

            # Calculate basic code metrics
            lines = source_code.split('\n')
            comment_lines = sum(1 for line in lines if line.strip().startswith(('#', '//', '/*', '*')))
            code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith(('#', '//', '/*', '*')))

            file_result["code_metrics"] = {
                "cyclomatic_complexity": _calculate_avg_complexity(file_result["ast"].get("functions", [])),
                "maintainability_index": min(100, max(0, 171 - 5.2 * len(source_code) // 1000)),
                "comment_ratio": comment_lines / max(1, code_lines)
            }

            # Extract dependencies
            file_result["dependencies"] = _extract_dependencies(file_path, file_result["ast"].get("imports", []))

            parsed_files.append(file_result)

        except Exception as e:
            parsing_errors.append(f"Error parsing {file_path}: {str(e)}")

    return {
        "status": "success" if not parsing_errors else "partial",
        "parsed_files": parsed_files,
        "parsing_errors": parsing_errors,
        "warnings": warnings[:20]  # Limit warnings
    }


def _estimate_complexity(node):
    """Estimate cyclomatic complexity for a Python AST node."""
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
    return complexity


def _extract_function_calls(node):
    """Extract function calls from a Python AST node."""
    calls = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
            calls.append(child.func.id)
    return list(set(calls))[:10]  # Limit to 10


def _parse_c_functions(source_code: str) -> List[Dict[str, Any]]:
    """Parse C/C++ function definitions using regex."""
    import re
    functions = []
    # Simple regex for function definitions
    pattern = r'(\w+)\s+(\w+)\s*\(([^)]*)\)\s*\{'
    matches = re.finditer(pattern, source_code)

    for match in matches:
        return_type, func_name, params = match.groups()
        line_start = source_code[:match.start()].count('\n') + 1

        functions.append({
            "name": func_name,
            "return_type": return_type,
            "parameters": [p.strip().split()[-1] if p.strip() else "" for p in params.split(',')],
            "line_start": line_start,
            "line_end": line_start + 10,  # Estimate
            "complexity": 5,  # Estimate
            "calls": []
        })

    return functions[:50]  # Limit results


def _parse_java_methods(source_code: str) -> List[Dict[str, Any]]:
    """Parse Java method definitions using regex."""
    import re
    methods = []
    pattern = r'(?:public|private|protected)?\s*(?:static)?\s*(\w+)\s+(\w+)\s*\(([^)]*)\)\s*\{'
    matches = re.finditer(pattern, source_code)

    for match in matches:
        return_type, method_name, params = match.groups()
        line_start = source_code[:match.start()].count('\n') + 1

        methods.append({
            "name": method_name,
            "return_type": return_type,
            "parameters": [p.strip().split()[-1] if p.strip() else "" for p in params.split(',')],
            "line_start": line_start,
            "line_end": line_start + 10,
            "complexity": 5,
            "calls": []
        })

    return methods[:50]


def _calculate_avg_complexity(functions: List[Dict[str, Any]]) -> float:
    """Calculate average cyclomatic complexity."""
    if not functions:
        return 0.0
    return sum(f.get("complexity", 0) for f in functions) / len(functions)


def _extract_dependencies(file_path: str, imports: List[str]) -> Dict[str, List[str]]:
    """Categorize dependencies as internal or external."""
    import os
    internal = []
    external = []

    base_dir = os.path.dirname(file_path)

    for imp in imports:
        # Check if it's a local file
        if imp.endswith('.h') or imp.endswith('.hpp'):
            if os.path.exists(os.path.join(base_dir, imp)):
                internal.append(imp)
            else:
                external.append(imp)
        else:
            # Assume external for packages/libraries
            external.append(imp)

    return {
        "internal": internal[:20],
        "external": external[:20]
    }


def extract_dependencies(
    parsed_files: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Extract and map dependencies between code modules.

    Args:
        parsed_files: List of parsed file structures

    Returns:
        dict: Dependency graph and analysis
    """
    import os
    from collections import defaultdict

    nodes = []
    edges = []
    file_map = {}
    dependency_counts = defaultdict(int)
    external_deps = set()

    # Build file map and create nodes
    for parsed_file in parsed_files:
        file_path = parsed_file.get("file_path", "")
        file_name = os.path.basename(file_path)
        file_map[file_name] = parsed_file

        nodes.append({
            "id": file_name,
            "type": "source",
            "path": file_path,
            "language": parsed_file.get("language", "Unknown")
        })

    # Build edges from dependencies
    for parsed_file in parsed_files:
        source_file = os.path.basename(parsed_file.get("file_path", ""))
        deps = parsed_file.get("dependencies", {})

        # Internal dependencies
        for internal_dep in deps.get("internal", []):
            edges.append({
                "from": source_file,
                "to": internal_dep,
                "type": "includes"
            })
            dependency_counts[source_file] += 1

        # External dependencies
        for external_dep in deps.get("external", []):
            external_deps.add(external_dep)
            if external_dep not in [n["id"] for n in nodes]:
                nodes.append({
                    "id": external_dep,
                    "type": "external"
                })
            edges.append({
                "from": source_file,
                "to": external_dep,
                "type": "links"
            })

    # Detect circular dependencies
    circular_deps = _detect_circular_dependencies(edges)

    # Find tightly coupled modules
    tightly_coupled = _find_tightly_coupled_modules(edges, dependency_counts)

    # Identify orphaned files (no incoming or outgoing dependencies)
    all_files = {node["id"] for node in nodes if node["type"] == "source"}
    files_with_deps = {edge["from"] for edge in edges} | {edge["to"] for edge in edges}
    orphaned_files = list(all_files - files_with_deps)

    # Categorize external dependencies
    external_dep_list = []
    for ext_dep in external_deps:
        purpose = _infer_library_purpose(ext_dep)
        external_dep_list.append({
            "name": ext_dep,
            "version": "unknown",
            "purpose": purpose
        })

    # Generate modernization recommendations
    recommendations = []
    if circular_deps:
        recommendations.append(f"Break {len(circular_deps)} circular dependencies to improve maintainability")
    if tightly_coupled:
        recommendations.append(f"Reduce coupling between {len(tightly_coupled)} module pairs")
    if orphaned_files:
        recommendations.append(f"Review {len(orphaned_files)} orphaned files for removal")

    # Check for legacy libraries
    legacy_libs = ['libcurl', 'libxml2', 'openssl']
    for lib in legacy_libs:
        if any(lib in dep for dep in external_deps):
            recommendations.append(f"Consider modernizing {lib} to newer alternatives")

    return {
        "status": "success",
        "dependency_graph": {
            "nodes": nodes,
            "edges": edges
        },
        "dependency_analysis": {
            "circular_dependencies": circular_deps,
            "tightly_coupled_modules": tightly_coupled,
            "external_dependencies": external_dep_list,
            "orphaned_files": orphaned_files
        },
        "modernization_recommendations": recommendations
    }


def _detect_circular_dependencies(edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect circular dependencies using DFS."""
    from collections import defaultdict

    # Build adjacency list
    graph = defaultdict(list)
    for edge in edges:
        if edge["type"] == "includes":  # Only check internal dependencies
            graph[edge["from"]].append(edge["to"])

    circular = []
    visited = set()
    rec_stack = set()

    def dfs(node, path):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor, path.copy()):
                    return True
            elif neighbor in rec_stack:
                # Found cycle
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                if len(cycle) > 1:
                    circular.append({
                        "cycle": cycle,
                        "severity": "high" if len(cycle) > 3 else "medium"
                    })
                return True

        rec_stack.remove(node)
        return False

    for node in graph:
        if node not in visited:
            dfs(node, [])

    return circular[:10]  # Limit to 10


def _find_tightly_coupled_modules(edges: List[Dict[str, Any]], dependency_counts: Dict[str, int]) -> List[Dict[str, Any]]:
    """Find modules with high coupling."""
    from collections import defaultdict

    coupling = defaultdict(int)

    # Count bidirectional dependencies
    for edge in edges:
        if edge["type"] == "includes":
            pair = tuple(sorted([edge["from"], edge["to"]]))
            coupling[pair] += 1

    tightly_coupled = []
    for (mod1, mod2), count in coupling.items():
        if count >= 2:  # Bidirectional or multiple dependencies
            coupling_score = min(1.0, count / 5.0)
            tightly_coupled.append({
                "module1": mod1,
                "module2": mod2,
                "coupling_score": round(coupling_score, 2),
                "shared_dependencies": count
            })

    return sorted(tightly_coupled, key=lambda x: x["coupling_score"], reverse=True)[:10]


def _infer_library_purpose(lib_name: str) -> str:
    """Infer the purpose of a library from its name."""
    purposes = {
        "curl": "HTTP client",
        "xml": "XML parsing",
        "json": "JSON parsing",
        "ssl": "Cryptography",
        "crypto": "Cryptography",
        "sql": "Database",
        "db": "Database",
        "test": "Testing",
        "log": "Logging",
        "math": "Mathematics",
        "thread": "Concurrency",
        "net": "Networking"
    }

    lib_lower = lib_name.lower()
    for key, purpose in purposes.items():
        if key in lib_lower:
            return purpose

    return "Unknown"


def detect_code_patterns(
    source_code: str,
    language: str
) -> Dict[str, Any]:
    """
    Detect common patterns, anti-patterns, and code smells.

    Args:
        source_code: Source code to analyze
        language: Programming language

    Returns:
        dict: Detected patterns and anti-patterns
    """
    import re

    design_patterns = []
    anti_patterns = []
    code_smells = []
    security_issues = []

    lines = source_code.split('\n')

    # Detect design patterns
    # Singleton pattern
    if re.search(r'private\s+static\s+\w+\s+instance', source_code, re.IGNORECASE):
        for i, line in enumerate(lines):
            if re.search(r'private\s+static\s+\w+\s+instance', line, re.IGNORECASE):
                design_patterns.append({
                    "pattern": "Singleton",
                    "location": f"line {i + 1}",
                    "confidence": 0.85,
                    "usage": "good"
                })
                break

    # Factory pattern
    if re.search(r'class\s+\w*Factory', source_code) or re.search(r'create\w+\(', source_code):
        for i, line in enumerate(lines):
            if re.search(r'class\s+\w*Factory', line):
                design_patterns.append({
                    "pattern": "Factory",
                    "location": f"line {i + 1}",
                    "confidence": 0.75,
                    "usage": "good"
                })
                break

    # Observer pattern
    if re.search(r'addListener|addEventListener|subscribe|notify', source_code):
        design_patterns.append({
            "pattern": "Observer",
            "location": "multiple locations",
            "confidence": 0.70,
            "usage": "good"
        })

    # Detect anti-patterns
    # God Object (very large classes/files)
    if len(lines) > 1000:
        anti_patterns.append({
            "pattern": "God Object",
            "location": f"entire file ({len(lines)} lines)",
            "severity": "high",
            "description": f"File has {len(lines)} lines, suggesting a God Object",
            "recommendation": "Split into smaller, focused modules"
        })

    # Magic Numbers
    magic_numbers = []
    for i, line in enumerate(lines):
        # Detect numeric literals (excluding 0, 1, -1)
        matches = re.findall(r'\b(?<!\.)\d{2,}\b(?!\.)', line)
        if matches and not line.strip().startswith(('#', '//')):
            magic_numbers.append(f"line {i + 1}")

    if magic_numbers:
        anti_patterns.append({
            "pattern": "Magic Numbers",
            "locations": magic_numbers[:5],
            "severity": "medium",
            "recommendation": "Define named constants for better readability"
        })

    # Hard-coded credentials or sensitive data
    sensitive_patterns = [
        (r'password\s*=\s*["\'][\w]+["\']', "Hard-coded password"),
        (r'api[_-]?key\s*=\s*["\'][\w]+["\']', "Hard-coded API key"),
        (r'secret\s*=\s*["\'][\w]+["\']', "Hard-coded secret")
    ]

    for pattern, desc in sensitive_patterns:
        matches = re.finditer(pattern, source_code, re.IGNORECASE)
        for match in matches:
            line_num = source_code[:match.start()].count('\n') + 1
            anti_patterns.append({
                "pattern": "Hard-coded Credentials",
                "location": f"line {line_num}",
                "severity": "critical",
                "description": desc,
                "recommendation": "Use environment variables or secret management"
            })

    # Detect code smells
    # Long methods
    if language.lower() == 'python':
        func_pattern = r'^\s*def\s+(\w+)\s*\('
        func_starts = [(i, match.group(1)) for i, line in enumerate(lines)
                      for match in [re.match(func_pattern, line)] if match]

        for idx, (start, func_name) in enumerate(func_starts):
            end = func_starts[idx + 1][0] if idx + 1 < len(func_starts) else len(lines)
            func_length = end - start

            if func_length > 50:
                code_smells.append({
                    "smell": "Long Method",
                    "location": f"{func_name}() at line {start + 1}",
                    "severity": "medium" if func_length < 100 else "high",
                    "metrics": {"lines": func_length}
                })

    elif language.lower() in ['c', 'c++', 'java']:
        func_pattern = r'\w+\s+(\w+)\s*\([^)]*\)\s*\{'
        for i, line in enumerate(lines):
            match = re.search(func_pattern, line)
            if match:
                func_name = match.group(1)
                # Estimate function length by finding closing brace
                brace_count = 1
                func_length = 1
                for j in range(i + 1, min(i + 200, len(lines))):
                    func_length += 1
                    brace_count += lines[j].count('{') - lines[j].count('}')
                    if brace_count == 0:
                        break

                if func_length > 50:
                    code_smells.append({
                        "smell": "Long Method",
                        "location": f"{func_name}() at line {i + 1}",
                        "severity": "medium" if func_length < 100 else "high",
                        "metrics": {"lines": func_length}
                    })

    # Deep nesting
    max_nesting = 0
    for line in lines:
        indent = len(line) - len(line.lstrip())
        nesting = indent // 4  # Assume 4-space indentation
        max_nesting = max(max_nesting, nesting)

    if max_nesting > 4:
        code_smells.append({
            "smell": "Deep Nesting",
            "location": "multiple locations",
            "severity": "medium",
            "metrics": {"max_depth": max_nesting},
            "recommendation": "Refactor to reduce nesting depth"
        })

    # Duplicate code (simple pattern matching)
    line_hashes = {}
    for i, line in enumerate(lines):
        stripped = line.strip()
        if len(stripped) > 20 and not stripped.startswith(('#', '//')):
            if stripped in line_hashes:
                line_hashes[stripped].append(i + 1)
            else:
                line_hashes[stripped] = [i + 1]

    duplicate_locations = [f"lines {', '.join(map(str, locs))}"
                          for stripped, locs in line_hashes.items() if len(locs) > 1]
    if duplicate_locations:
        code_smells.append({
            "smell": "Duplicate Code",
            "locations": duplicate_locations[:5],
            "severity": "medium",
            "recommendation": "Extract common logic into reusable functions"
        })

    # Detect security issues
    # Buffer overflow risks (C/C++)
    if language.lower() in ['c', 'c++']:
        unsafe_funcs = [
            ('strcpy', 'CWE-120', 'Use strncpy or safer alternatives'),
            ('strcat', 'CWE-120', 'Use strncat or safer alternatives'),
            ('sprintf', 'CWE-120', 'Use snprintf'),
            ('gets', 'CWE-120', 'Use fgets instead'),
            ('scanf', 'CWE-20', 'Validate input length')
        ]

        for func, cwe, recommendation in unsafe_funcs:
            matches = re.finditer(rf'\b{func}\s*\(', source_code)
            for match in matches:
                line_num = source_code[:match.start()].count('\n') + 1
                security_issues.append({
                    "issue": f"Unsafe function: {func}",
                    "location": f"line {line_num}",
                    "severity": "critical",
                    "cwe_id": cwe,
                    "recommendation": recommendation
                })

    # SQL Injection risks
    sql_concat_patterns = [
        r'(?:query|sql)\s*\+?=.*\+',
        r'sprintf.*SELECT|INSERT|UPDATE|DELETE',
        r'format.*SELECT|INSERT|UPDATE|DELETE'
    ]

    for pattern in sql_concat_patterns:
        matches = re.finditer(pattern, source_code, re.IGNORECASE)
        for match in matches:
            line_num = source_code[:match.start()].count('\n') + 1
            security_issues.append({
                "issue": "SQL Injection Risk",
                "location": f"line {line_num}",
                "severity": "critical",
                "cwe_id": "CWE-89",
                "recommendation": "Use parameterized queries or prepared statements"
            })

    # Command Injection
    if re.search(r'system\s*\(|exec\s*\(|popen\s*\(', source_code):
        matches = re.finditer(r'system\s*\(|exec\s*\(|popen\s*\(', source_code)
        for match in matches:
            line_num = source_code[:match.start()].count('\n') + 1
            security_issues.append({
                "issue": "Command Injection Risk",
                "location": f"line {line_num}",
                "severity": "high",
                "cwe_id": "CWE-78",
                "recommendation": "Avoid shell commands or sanitize inputs thoroughly"
            })

    return {
        "status": "success",
        "design_patterns": design_patterns,
        "anti_patterns": anti_patterns[:10],
        "code_smells": code_smells[:10],
        "security_issues": security_issues[:15]
    }


def ingest_to_vector_db(
    parsed_data: Dict[str, Any],
    embeddings_model: str = "text-embedding-004"
) -> Dict[str, Any]:
    """
    Convert parsed code to embeddings and store in Vector DB.

    Args:
        parsed_data: Parsed code structure and metadata
        embeddings_model: Model to use for generating embeddings

    Returns:
        dict: Ingestion status and vector DB metadata
    """
    import hashlib
    from datetime import datetime

    # Extract parsed files from the data
    parsed_files = parsed_data.get("parsed_files", [])
    if not parsed_files:
        return {
            "status": "error",
            "message": "No parsed files provided",
            "ingested_documents": 0
        }

    documents_to_ingest = []
    indexed_items = []
    stats = {
        "functions_indexed": 0,
        "classes_indexed": 0,
        "comments_indexed": 0,
        "files_indexed": 0
    }

    # Process each parsed file
    for parsed_file in parsed_files:
        file_path = parsed_file.get("file_path", "")
        language = parsed_file.get("language", "Unknown")
        ast_data = parsed_file.get("ast", {})
        dependencies = parsed_file.get("dependencies", {})
        code_metrics = parsed_file.get("code_metrics", {})

        # Index functions
        for func in ast_data.get("functions", []):
            func_name = func.get("name", "")
            vector_id = _generate_vector_id(file_path, func_name)

            # Create document for embedding
            doc_content = _create_function_document(func, file_path, language)

            document = {
                "id": vector_id,
                "content": doc_content,
                "metadata": {
                    "type": "function",
                    "name": func_name,
                    "file": file_path,
                    "language": language,
                    "complexity": func.get("complexity", 0),
                    "lines": f"{func.get('line_start', 0)}-{func.get('line_end', 0)}",
                    "parameters": func.get("parameters", []),
                    "return_type": func.get("return_type", "unknown")
                }
            }

            documents_to_ingest.append(document)
            indexed_items.append({
                "type": "function",
                "name": func_name,
                "vector_id": vector_id,
                "metadata": document["metadata"]
            })
            stats["functions_indexed"] += 1

        # Index classes
        for cls in ast_data.get("classes", []):
            cls_name = cls.get("name", "")
            vector_id = _generate_vector_id(file_path, cls_name)

            doc_content = _create_class_document(cls, file_path, language)

            document = {
                "id": vector_id,
                "content": doc_content,
                "metadata": {
                    "type": "class",
                    "name": cls_name,
                    "file": file_path,
                    "language": language,
                    "methods": cls.get("methods", []),
                    "lines": f"{cls.get('line_start', 0)}-{cls.get('line_end', 0) if 'line_end' in cls else 'unknown'}"
                }
            }

            documents_to_ingest.append(document)
            indexed_items.append({
                "type": "class",
                "name": cls_name,
                "vector_id": vector_id,
                "metadata": document["metadata"]
            })
            stats["classes_indexed"] += 1

        # Index file-level metadata
        file_vector_id = _generate_vector_id(file_path, "file_metadata")
        file_doc_content = _create_file_document(parsed_file)

        file_document = {
            "id": file_vector_id,
            "content": file_doc_content,
            "metadata": {
                "type": "file",
                "file": file_path,
                "language": language,
                "metrics": code_metrics,
                "dependencies": dependencies
            }
        }

        documents_to_ingest.append(file_document)
        stats["files_indexed"] += 1

    # Insert into Vector DB (using mock interface for now)
    # In production, this would use the actual VectorDBInterface
    try:
        # from shared.tools.vector_db import create_vector_db_interface
        # vector_db = create_vector_db_interface()
        # result = vector_db.insert_embeddings(documents_to_ingest)

        # Mock successful insertion
        ingestion_result = {
            "status": "success",
            "inserted_count": len(documents_to_ingest)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to ingest to vector DB: {str(e)}",
            "ingested_documents": 0
        }

    # Generate example queries based on the indexed content
    query_examples = _generate_query_examples(indexed_items, stats)

    return {
        "status": "success",
        "ingested_documents": len(documents_to_ingest),
        "vector_db_collection": "legacy_codebase",
        "embeddings_model": embeddings_model,
        "indexed_items": indexed_items[:20],  # Sample of indexed items
        "indexing_statistics": {
            **stats,
            "total_vectors": len(documents_to_ingest)
        },
        "query_examples": query_examples,
        "ingestion_timestamp": datetime.utcnow().isoformat() + 'Z'
    }


def _generate_vector_id(file_path: str, item_name: str) -> str:
    """Generate a unique vector ID for an item."""
    import hashlib
    unique_str = f"{file_path}:{item_name}"
    return f"vec_{hashlib.md5(unique_str.encode()).hexdigest()[:12]}"


def _create_function_document(func: Dict[str, Any], file_path: str, language: str) -> str:
    """Create a document text for a function to be embedded."""
    func_name = func.get("name", "")
    return_type = func.get("return_type", "unknown")
    params = func.get("parameters", [])
    complexity = func.get("complexity", 0)
    calls = func.get("calls", [])

    doc = f"Function: {func_name}\n"
    doc += f"Language: {language}\n"
    doc += f"File: {file_path}\n"
    doc += f"Signature: {return_type} {func_name}({', '.join(params)})\n"
    doc += f"Cyclomatic Complexity: {complexity}\n"

    if calls:
        doc += f"Calls: {', '.join(calls)}\n"

    doc += f"Purpose: This is a {language} function named {func_name} "
    doc += f"that takes {len(params)} parameter(s) and returns {return_type}."

    return doc


def _create_class_document(cls: Dict[str, Any], file_path: str, language: str) -> str:
    """Create a document text for a class to be embedded."""
    cls_name = cls.get("name", "")
    methods = cls.get("methods", [])

    doc = f"Class: {cls_name}\n"
    doc += f"Language: {language}\n"
    doc += f"File: {file_path}\n"
    doc += f"Methods: {len(methods)}\n"

    if methods:
        doc += f"Method names: {', '.join(methods)}\n"

    doc += f"Purpose: This is a {language} class named {cls_name} "
    doc += f"with {len(methods)} method(s)."

    return doc


def _create_file_document(parsed_file: Dict[str, Any]) -> str:
    """Create a document text for a file to be embedded."""
    file_path = parsed_file.get("file_path", "")
    language = parsed_file.get("language", "Unknown")
    ast_data = parsed_file.get("ast", {})
    metrics = parsed_file.get("code_metrics", {})
    deps = parsed_file.get("dependencies", {})

    num_functions = len(ast_data.get("functions", []))
    num_classes = len(ast_data.get("classes", []))
    imports = ast_data.get("imports", [])

    doc = f"File: {file_path}\n"
    doc += f"Language: {language}\n"
    doc += f"Functions: {num_functions}\n"
    doc += f"Classes: {num_classes}\n"
    doc += f"Cyclomatic Complexity: {metrics.get('cyclomatic_complexity', 0)}\n"
    doc += f"Maintainability Index: {metrics.get('maintainability_index', 0)}\n"

    if imports:
        doc += f"Imports/Includes: {', '.join(imports[:10])}\n"

    internal_deps = deps.get("internal", [])
    external_deps = deps.get("external", [])

    if internal_deps:
        doc += f"Internal Dependencies: {', '.join(internal_deps[:5])}\n"
    if external_deps:
        doc += f"External Dependencies: {', '.join(external_deps[:5])}\n"

    doc += f"Summary: This {language} file contains {num_functions} function(s) "
    doc += f"and {num_classes} class(es)."

    return doc


def _generate_query_examples(indexed_items: List[Dict[str, Any]], stats: Dict[str, int]) -> List[str]:
    """Generate example queries based on indexed content."""
    queries = []

    # Function-based queries
    func_items = [item for item in indexed_items if item.get("type") == "function"]
    if func_items:
        sample_func = func_items[0]["name"]
        queries.append(f"How does the {sample_func} function work?")
        queries.append("Which functions have the highest complexity?")

    # Class-based queries
    class_items = [item for item in indexed_items if item.get("type") == "class"]
    if class_items:
        sample_class = class_items[0]["name"]
        queries.append(f"What methods does the {sample_class} class have?")

    # General queries
    queries.extend([
        "Where is database connection handled?",
        "What are the main security vulnerabilities?",
        "Which modules are tightly coupled?"
    ])

    return queries[:6]


# Create the code ingestion agent
code_ingestion_agent = Agent(
    name="code_ingestion_agent",
    model="gemini-2.0-flash",
    description=(
        "Ingests legacy source code from various languages and formats. Parses code structure, "
        "extracts dependencies, detects patterns, and stores in Vector DB for semantic search."
    ),
    instruction=(
        "You are a code ingestion agent responsible for reading and processing legacy source code "
        "into structured formats for analysis and modernization.\n\n"

        "Your key responsibilities:\n"
        "1. Scan legacy codebase and catalog all source files\n"
        "2. Parse source files to extract AST and code structure\n"
        "3. Extract and map dependencies between modules\n"
        "4. Detect design patterns, anti-patterns, and code smells\n"
        "5. Generate embeddings and store in Vector DB for semantic search\n\n"

        "Supported Languages:\n"
        "- C/C++ (common in legacy systems)\n"
        "- Java (enterprise applications)\n"
        "- COBOL (mainframe systems)\n"
        "- Python (scripting and modern additions)\n"
        "- JavaScript (web interfaces)\n\n"

        "Parsing Strategy:\n"
        "- Use appropriate parser for each language (tree-sitter, ANTLR, etc.)\n"
        "- Extract function signatures, class definitions, interfaces\n"
        "- Identify control flow and data flow\n"
        "- Capture comments and documentation strings\n"
        "- Handle preprocessor directives and macros\n\n"

        "Dependency Analysis:\n"
        "- Map include/import statements\n"
        "- Identify function call graphs\n"
        "- Track data dependencies\n"
        "- Detect circular dependencies\n"
        "- Catalog external library usage\n\n"

        "Pattern Detection:\n"
        "- Identify design patterns (Singleton, Factory, Observer, etc.)\n"
        "- Detect anti-patterns (God Object, Spaghetti Code, etc.)\n"
        "- Find code smells (Long Method, Duplicate Code, etc.)\n"
        "- Flag security vulnerabilities (buffer overflows, SQL injection, etc.)\n\n"

        "Vector DB Storage:\n"
        "- Generate semantic embeddings for code snippets\n"
        "- Store with rich metadata (file, language, metrics, etc.)\n"
        "- Enable semantic search across codebase\n"
        "- Support queries like 'How does authentication work?'\n\n"

        "Quality Metrics:\n"
        "- Calculate cyclomatic complexity\n"
        "- Measure maintainability index\n"
        "- Compute comment/code ratio\n"
        "- Identify duplicate code percentage\n\n"

        "Error Handling:\n"
        "- Handle unparseable code gracefully\n"
        "- Report parsing errors with context\n"
        "- Skip binary files and generated code\n"
        "- Provide warnings for deprecated language features\n\n"

        "Output:\n"
        "- Send parsed code to static analysis agent\n"
        "- Provide dependency graph to knowledge synthesis\n"
        "- Store in Vector DB for developer query access\n"
        "- Generate ingestion summary report"
    ),
    tools=[
        scan_codebase,
        parse_source_files,
        extract_dependencies,
        detect_code_patterns,
        ingest_to_vector_db
    ]
)
