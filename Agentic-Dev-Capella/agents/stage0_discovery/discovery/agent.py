"""
agents/stage0_discovery/discovery/agent.py

Discovery agent that performs comprehensive asset inventory of legacy systems.
Identifies all components including code, configs, schemas, and infrastructure.
"""

from typing import Dict, List, Any, Set
from google.adk.agents import Agent
import os
from pathlib import Path
import re
from collections import defaultdict
from datetime import datetime


def scan_repository(
    repo_path: str,
    include_patterns: List[str] = None
) -> Dict[str, Any]:
    """Scans repository for all assets including code and non-code files.

    Args:
        repo_path: Path to the legacy repository
        include_patterns: File patterns to include (e.g., ['*.py', '*.sql'])

    Returns:
        dict: Complete asset inventory with categorization
    """
    if include_patterns is None:
        include_patterns = [
            "*.py", "*.java", "*.cobol", "*.cbl", "*.c", "*.cpp", "*.cs", "*.js", "*.ts",  # Source code
            "*.sql", "*.ddl", "*.dml",  # Database
            "*.yaml", "*.yml", "*.json", "*.xml", "*.conf", "*.properties", "*.ini",  # Config
            "*.tf", "*.tfvars",  # Infrastructure as Code
            "*.md", "*.txt", "*.doc", "*.docx", "*.pdf"  # Documentation
        ]

    path = Path(repo_path)

    # Initialize asset inventory
    asset_inventory = {
        "source_code": [],
        "database_schemas": [],
        "configuration_files": [],
        "infrastructure_code": [],
        "documentation": [],
        "api_contracts": []
    }

    if not path.exists():
        # Return empty inventory for non-existent paths (testing scenario)
        return {
            "status": "success",
            "repo_path": repo_path,
            "total_assets": 0,
            "inventory": asset_inventory,
            "scan_summary": {
                "source_files": 0,
                "db_schemas": 0,
                "configs": 0,
                "infrastructure_files": 0,
                "documentation_files": 0
            },
            "scan_status": "path_not_found"
        }

    # Scan directory recursively
    scanned_files = []
    total_size = 0

    try:
        if path.is_file():
            # Single file provided
            scanned_files = [path]
        else:
            # Scan directory
            scanned_files = _scan_directory(path, include_patterns)

        # Categorize each file
        for file_path in scanned_files:
            try:
                file_size = file_path.stat().st_size
                total_size += file_size

                file_info = {
                    "path": str(file_path),
                    "name": file_path.name,
                    "size_bytes": file_size,
                    "extension": file_path.suffix
                }

                # Categorize based on file type
                category = _categorize_file(file_path)
                if category:
                    asset_inventory[category].append(file_info)

            except Exception as e:
                # Skip files that can't be read
                continue

        # Calculate summary statistics
        scan_summary = {
            "source_files": len(asset_inventory["source_code"]),
            "db_schemas": len(asset_inventory["database_schemas"]),
            "configs": len(asset_inventory["configuration_files"]),
            "infrastructure_files": len(asset_inventory["infrastructure_code"]),
            "documentation_files": len(asset_inventory["documentation"]),
            "api_contracts": len(asset_inventory["api_contracts"]),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }

        return {
            "status": "success",
            "repo_path": repo_path,
            "total_assets": sum(len(v) for v in asset_inventory.values()),
            "inventory": asset_inventory,
            "scan_summary": scan_summary,
            "scan_status": "completed",
            "scanned_at": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "status": "error",
            "repo_path": repo_path,
            "error": str(e),
            "inventory": asset_inventory,
            "scan_status": "failed"
        }


def _scan_directory(directory: Path, include_patterns: List[str]) -> List[Path]:
    """Recursively scan directory for files matching patterns."""
    files = []

    # Convert glob patterns to set for faster matching
    extensions = set()
    for pattern in include_patterns:
        if pattern.startswith("*."):
            extensions.add(pattern[1:])  # Remove *

    try:
        for item in directory.rglob("*"):
            # Skip hidden files and directories
            if any(part.startswith('.') for part in item.parts):
                continue

            # Skip common build/dependency directories
            skip_dirs = {'node_modules', '__pycache__', 'venv', 'env', 'target', 'build', 'dist', '.git'}
            if any(skip_dir in item.parts for skip_dir in skip_dirs):
                continue

            if item.is_file():
                # Check if file matches any pattern
                if item.suffix in extensions or not extensions:
                    files.append(item)

    except PermissionError:
        # Skip directories we don't have permission to read
        pass

    return files


def _categorize_file(file_path: Path) -> str:
    """Categorize file based on extension and content."""
    ext = file_path.suffix.lower()
    name = file_path.name.lower()

    # Source code files
    source_extensions = {'.py', '.java', '.cobol', '.cbl', '.c', '.cpp', '.cs',
                        '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.rb', '.php'}
    if ext in source_extensions:
        return "source_code"

    # Database files
    db_extensions = {'.sql', '.ddl', '.dml'}
    if ext in db_extensions:
        return "database_schemas"

    # Configuration files
    config_extensions = {'.yaml', '.yml', '.json', '.xml', '.conf', '.properties',
                        '.ini', '.toml', '.env'}
    if ext in config_extensions or name in {'dockerfile', 'makefile'}:
        return "configuration_files"

    # Infrastructure as Code
    iac_extensions = {'.tf', '.tfvars'}
    if ext in iac_extensions or 'cloudformation' in name:
        return "infrastructure_code"

    # API contracts
    if 'swagger' in name or 'openapi' in name or ext == '.wsdl':
        return "api_contracts"

    # Documentation
    doc_extensions = {'.md', '.txt', '.doc', '.docx', '.pdf', '.rst'}
    if ext in doc_extensions or name in {'readme', 'changelog', 'license'}:
        return "documentation"

    return None


def identify_technology_stack(
    asset_inventory: Dict[str, List[str]]
) -> Dict[str, Any]:
    """Analyzes assets to identify the technology stack.

    Args:
        asset_inventory: Inventory from scan_repository

    Returns:
        dict: Identified technologies, languages, frameworks, and databases
    """
    tech_stack = {
        "languages": [],
        "frameworks": [],
        "databases": [],
        "infrastructure": [],
        "build_tools": [],
        "testing_frameworks": []
    }

    # Extract file information from inventory
    source_files = asset_inventory.get("source_code", [])
    config_files = asset_inventory.get("configuration_files", [])
    db_files = asset_inventory.get("database_schemas", [])
    iac_files = asset_inventory.get("infrastructure_code", [])

    # Language detection from source files
    languages_detected = _detect_languages(source_files)
    tech_stack["languages"] = languages_detected

    # Framework detection from config and source
    frameworks_detected = _detect_frameworks(source_files, config_files)
    tech_stack["frameworks"] = frameworks_detected

    # Database detection
    databases_detected = _detect_databases(db_files, config_files, source_files)
    tech_stack["databases"] = databases_detected

    # Infrastructure detection
    infrastructure_detected = _detect_infrastructure(iac_files, config_files)
    tech_stack["infrastructure"] = infrastructure_detected

    # Build tool detection
    build_tools_detected = _detect_build_tools(config_files)
    tech_stack["build_tools"] = build_tools_detected

    # Testing framework detection
    testing_frameworks_detected = _detect_testing_frameworks(source_files, config_files)
    tech_stack["testing_frameworks"] = testing_frameworks_detected

    # Assess modernization complexity
    complexity = _assess_complexity(tech_stack)

    # Generate modernization recommendations
    recommendations = _generate_modernization_recommendations(tech_stack)

    return {
        "status": "success",
        "technology_stack": tech_stack,
        "modernization_complexity": complexity,
        "modernization_recommendations": recommendations,
        "total_technologies": sum(len(v) for v in tech_stack.values())
    }


def _detect_languages(source_files: List[Dict[str, Any]]) -> List[str]:
    """Detect programming languages from source files."""
    languages = set()

    for file_info in source_files:
        if isinstance(file_info, dict):
            ext = file_info.get("extension", "")
        else:
            # Handle case where it's just a string path
            ext = Path(str(file_info)).suffix

        ext = ext.lower()

        # Map extensions to languages
        lang_map = {
            '.py': 'Python',
            '.java': 'Java',
            '.cobol': 'COBOL',
            '.cbl': 'COBOL',
            '.c': 'C',
            '.cpp': 'C++',
            '.cs': 'C#',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React',
            '.tsx': 'React/TypeScript',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.scala': 'Scala',
            '.kt': 'Kotlin'
        }

        if ext in lang_map:
            languages.add(lang_map[ext])

    return sorted(list(languages))


def _detect_frameworks(source_files: List[Dict], config_files: List[Dict]) -> List[str]:
    """Detect frameworks from source and config files."""
    frameworks = set()

    # Check config file names for framework indicators
    for file_info in config_files:
        if isinstance(file_info, dict):
            name = file_info.get("name", "").lower()
            path = file_info.get("path", "").lower()
        else:
            name = Path(str(file_info)).name.lower()
            path = str(file_info).lower()

        # Framework detection patterns
        if 'package.json' in name:
            frameworks.add('Node.js/NPM')
        elif 'pom.xml' in name:
            frameworks.add('Maven')
        elif 'build.gradle' in name:
            frameworks.add('Gradle')
        elif 'requirements.txt' in name or 'pipfile' in name:
            frameworks.add('Python/Pip')
        elif 'go.mod' in name:
            frameworks.add('Go Modules')
        elif 'cargo.toml' in name:
            frameworks.add('Rust/Cargo')
        elif 'gemfile' in name:
            frameworks.add('Ruby/Bundler')
        elif 'composer.json' in name:
            frameworks.add('PHP/Composer')
        elif 'spring' in path:
            frameworks.add('Spring Framework')
        elif 'django' in path:
            frameworks.add('Django')
        elif 'flask' in path:
            frameworks.add('Flask')
        elif 'express' in path:
            frameworks.add('Express.js')
        elif 'react' in path:
            frameworks.add('React')
        elif 'angular' in path:
            frameworks.add('Angular')
        elif 'vue' in path:
            frameworks.add('Vue.js')

    return sorted(list(frameworks))


def _detect_databases(db_files: List[Dict], config_files: List[Dict],
                      source_files: List[Dict]) -> List[str]:
    """Detect databases from schema files and configurations."""
    databases = set()

    # Check if there are database schema files
    if db_files:
        databases.add('SQL Database (Generic)')

    # Scan config and source files for database indicators
    all_files = config_files + source_files

    for file_info in all_files:
        if isinstance(file_info, dict):
            path = file_info.get("path", "").lower()
            name = file_info.get("name", "").lower()
        else:
            path = str(file_info).lower()
            name = Path(str(file_info)).name.lower()

        content_to_check = path + " " + name

        # Database detection patterns
        if any(db in content_to_check for db in ['oracle', 'orcl']):
            databases.add('Oracle')
        if any(db in content_to_check for db in ['postgres', 'postgresql', 'psql']):
            databases.add('PostgreSQL')
        if 'mysql' in content_to_check:
            databases.add('MySQL')
        if any(db in content_to_check for db in ['mongodb', 'mongo']):
            databases.add('MongoDB')
        if 'redis' in content_to_check:
            databases.add('Redis')
        if any(db in content_to_check for db in ['cassandra', 'cql']):
            databases.add('Cassandra')
        if 'dynamodb' in content_to_check:
            databases.add('DynamoDB')
        if any(db in content_to_check for db in ['sqlserver', 'mssql']):
            databases.add('SQL Server')
        if 'db2' in content_to_check:
            databases.add('DB2')

    # Remove generic if we found specific databases
    if len(databases) > 1 and 'SQL Database (Generic)' in databases:
        databases.remove('SQL Database (Generic)')

    return sorted(list(databases))


def _detect_infrastructure(iac_files: List[Dict], config_files: List[Dict]) -> List[str]:
    """Detect infrastructure technologies."""
    infrastructure = set()

    all_files = iac_files + config_files

    for file_info in all_files:
        if isinstance(file_info, dict):
            name = file_info.get("name", "").lower()
            ext = file_info.get("extension", "").lower()
            path = file_info.get("path", "").lower()
        else:
            name = Path(str(file_info)).name.lower()
            ext = Path(str(file_info)).suffix.lower()
            path = str(file_info).lower()

        content_to_check = name + " " + path

        # Infrastructure detection
        if ext in ['.tf', '.tfvars'] or 'terraform' in content_to_check:
            infrastructure.add('Terraform')
        if 'cloudformation' in content_to_check or ext == '.template':
            infrastructure.add('AWS CloudFormation')
        if 'kubernetes' in content_to_check or 'k8s' in content_to_check:
            infrastructure.add('Kubernetes')
        if 'docker' in content_to_check:
            infrastructure.add('Docker')
        if 'ansible' in content_to_check:
            infrastructure.add('Ansible')
        if 'puppet' in content_to_check:
            infrastructure.add('Puppet')
        if 'chef' in content_to_check:
            infrastructure.add('Chef')
        if 'helm' in content_to_check:
            infrastructure.add('Helm')

    return sorted(list(infrastructure))


def _detect_build_tools(config_files: List[Dict]) -> List[str]:
    """Detect build tools from config files."""
    build_tools = set()

    for file_info in config_files:
        if isinstance(file_info, dict):
            name = file_info.get("name", "").lower()
        else:
            name = Path(str(file_info)).name.lower()

        if 'makefile' in name:
            build_tools.add('Make')
        elif 'pom.xml' in name:
            build_tools.add('Maven')
        elif 'build.gradle' in name:
            build_tools.add('Gradle')
        elif 'package.json' in name:
            build_tools.add('NPM/Yarn')
        elif 'setup.py' in name:
            build_tools.add('Python setuptools')
        elif 'cargo.toml' in name:
            build_tools.add('Cargo')
        elif 'go.mod' in name:
            build_tools.add('Go build')

    return sorted(list(build_tools))


def _detect_testing_frameworks(source_files: List[Dict], config_files: List[Dict]) -> List[str]:
    """Detect testing frameworks."""
    testing = set()

    all_files = source_files + config_files

    for file_info in all_files:
        if isinstance(file_info, dict):
            name = file_info.get("name", "").lower()
            path = file_info.get("path", "").lower()
        else:
            name = Path(str(file_info)).name.lower()
            path = str(file_info).lower()

        content = name + " " + path

        # Testing framework detection
        if 'pytest' in content or 'test_' in name:
            testing.add('pytest')
        elif 'unittest' in content:
            testing.add('unittest')
        elif 'junit' in content:
            testing.add('JUnit')
        elif 'jest' in content:
            testing.add('Jest')
        elif 'mocha' in content:
            testing.add('Mocha')
        elif 'jasmine' in content:
            testing.add('Jasmine')
        elif 'rspec' in content:
            testing.add('RSpec')
        elif 'testng' in content:
            testing.add('TestNG')

    return sorted(list(testing))


def _assess_complexity(tech_stack: Dict[str, List[str]]) -> str:
    """Assess modernization complexity based on technology stack."""
    num_languages = len(tech_stack.get("languages", []))
    num_databases = len(tech_stack.get("databases", []))
    num_frameworks = len(tech_stack.get("frameworks", []))

    has_legacy_tech = any(
        legacy in tech_stack.get("languages", [])
        for legacy in ['COBOL', 'C', 'C++']
    )

    has_legacy_db = any(
        db in tech_stack.get("databases", [])
        for db in ['Oracle', 'DB2', 'SQL Server']
    )

    # Calculate complexity score
    complexity_score = 0
    complexity_score += num_languages * 2
    complexity_score += num_databases * 3
    complexity_score += num_frameworks * 1
    if has_legacy_tech:
        complexity_score += 5
    if has_legacy_db:
        complexity_score += 3

    if complexity_score >= 15:
        return "very_high"
    elif complexity_score >= 10:
        return "high"
    elif complexity_score >= 5:
        return "medium"
    else:
        return "low"


def _generate_modernization_recommendations(tech_stack: Dict[str, List[str]]) -> List[str]:
    """Generate modernization recommendations based on tech stack."""
    recommendations = []

    languages = tech_stack.get("languages", [])
    databases = tech_stack.get("databases", [])
    frameworks = tech_stack.get("frameworks", [])

    # Legacy language recommendations
    if 'COBOL' in languages:
        recommendations.append("Consider migrating COBOL to Java or Python for better maintainability")

    # Database recommendations
    if 'Oracle' in databases:
        recommendations.append("Consider PostgreSQL or cloud-native databases to reduce licensing costs")
    if 'DB2' in databases:
        recommendations.append("Evaluate migration to PostgreSQL or cloud database services")

    # Multiple language recommendation
    if len(languages) > 3:
        recommendations.append("High language diversity detected - consider standardizing on 1-2 primary languages")

    # No infrastructure as code
    if not tech_stack.get("infrastructure", []):
        recommendations.append("Implement Infrastructure as Code using Terraform or CloudFormation")

    # No testing frameworks
    if not tech_stack.get("testing_frameworks", []):
        recommendations.append("Implement automated testing framework for quality assurance")

    # Containerization
    if 'Docker' not in tech_stack.get("infrastructure", []):
        recommendations.append("Consider containerization with Docker for improved portability")

    # Orchestration
    if 'Kubernetes' not in tech_stack.get("infrastructure", []) and len(languages) > 1:
        recommendations.append("Consider Kubernetes for microservices orchestration")

    return recommendations


def detect_dependencies(
    source_files: List[str],
    config_files: List[str]
) -> Dict[str, Any]:
    """Identifies external dependencies and third-party libraries.

    Args:
        source_files: List of source code files
        config_files: List of configuration files

    Returns:
        dict: Dependency graph and external library list
    """
    dependencies = {
        "external_libraries": [],
        "internal_modules": [],
        "system_dependencies": []
    }

    # Parse dependency configuration files
    for config_file in config_files:
        if isinstance(config_file, dict):
            path = Path(config_file.get("path", ""))
            name = config_file.get("name", "").lower()
        else:
            path = Path(str(config_file))
            name = path.name.lower()

        try:
            if not path.exists():
                continue

            # Python dependencies
            if name == "requirements.txt":
                deps = _parse_requirements_txt(path)
                dependencies["external_libraries"].extend(deps)

            # Node.js dependencies
            elif name == "package.json":
                deps = _parse_package_json(path)
                dependencies["external_libraries"].extend(deps)

            # Java dependencies (Maven)
            elif name == "pom.xml":
                deps = _parse_pom_xml(path)
                dependencies["external_libraries"].extend(deps)

            # Java dependencies (Gradle)
            elif "build.gradle" in name:
                deps = _parse_gradle(path)
                dependencies["external_libraries"].extend(deps)

        except Exception:
            continue

    # Scan source files for import statements to find internal modules
    internal_modules = _scan_imports(source_files)
    dependencies["internal_modules"] = internal_modules

    # Deduplicate
    dependencies["external_libraries"] = list(set(dependencies["external_libraries"]))
    dependencies["internal_modules"] = list(set(dependencies["internal_modules"]))

    return {
        "status": "success",
        "dependencies": dependencies,
        "dependency_count": sum(len(v) for v in dependencies.values()),
        "external_count": len(dependencies["external_libraries"]),
        "internal_count": len(dependencies["internal_modules"])
    }


def _parse_requirements_txt(path: Path) -> List[str]:
    """Parse Python requirements.txt file."""
    deps = []
    try:
        content = path.read_text()
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                # Remove version specifiers
                dep = re.split(r'[>=<!\[]', line)[0].strip()
                if dep:
                    deps.append(dep)
    except:
        pass
    return deps


def _parse_package_json(path: Path) -> List[str]:
    """Parse Node.js package.json file."""
    deps = []
    try:
        import json
        content = json.loads(path.read_text())
        if 'dependencies' in content:
            deps.extend(content['dependencies'].keys())
        if 'devDependencies' in content:
            deps.extend(content['devDependencies'].keys())
    except:
        pass
    return deps


def _parse_pom_xml(path: Path) -> List[str]:
    """Parse Maven pom.xml file."""
    deps = []
    try:
        content = path.read_text()
        # Simple regex to extract artifactId
        matches = re.findall(r'<artifactId>([^<]+)</artifactId>', content)
        deps.extend(matches)
    except:
        pass
    return deps


def _parse_gradle(path: Path) -> List[str]:
    """Parse Gradle build file."""
    deps = []
    try:
        content = path.read_text()
        # Find dependency declarations
        matches = re.findall(r"implementation\s+['\"]([^:'\"]+)", content)
        deps.extend(matches)
        matches = re.findall(r"compile\s+['\"]([^:'\"]+)", content)
        deps.extend(matches)
    except:
        pass
    return deps


def _scan_imports(source_files: List) -> List[str]:
    """Scan source files for internal module imports."""
    modules = set()

    for file_info in source_files[:50]:  # Limit to first 50 files for performance
        if isinstance(file_info, dict):
            path = Path(file_info.get("path", ""))
        else:
            path = Path(str(file_info))

        try:
            if not path.exists():
                continue

            content = path.read_text(errors='ignore')

            # Python imports
            if path.suffix == '.py':
                imports = re.findall(r'^import\s+(\w+)', content, re.MULTILINE)
                from_imports = re.findall(r'^from\s+(\w+)', content, re.MULTILINE)
                modules.update(imports)
                modules.update(from_imports)

            # Java imports
            elif path.suffix == '.java':
                imports = re.findall(r'^import\s+([^;]+);', content, re.MULTILINE)
                # Extract package name (first part)
                for imp in imports:
                    parts = imp.strip().split('.')
                    if parts:
                        modules.add(parts[0])

            # JavaScript/TypeScript imports
            elif path.suffix in ['.js', '.ts', '.jsx', '.tsx']:
                imports = re.findall(r"from\s+['\"]([^'\"]+)['\"]", content)
                # Only internal modules (relative paths)
                for imp in imports:
                    if imp.startswith('.'):
                        modules.add(imp.split('/')[0])

        except:
            continue

    return list(modules)


def create_asset_metadata(
    asset_path: str,
    asset_type: str
) -> Dict[str, Any]:
    """Creates metadata for each discovered asset.

    Args:
        asset_path: Path to the asset
        asset_type: Type of asset (code, schema, config, etc.)

    Returns:
        dict: Metadata including size, last modified, and categorization
    """
    path = Path(asset_path)

    metadata = {
        "path": asset_path,
        "type": asset_type,
        "size_bytes": 0,
        "last_modified": None,
        "contains_business_logic": False,
        "complexity_score": 0,
        "lines_of_code": 0
    }

    if path.exists():
        try:
            # Get file stats
            stat = path.stat()
            metadata["size_bytes"] = stat.st_size
            metadata["last_modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()

            # Analyze content for source code files
            if asset_type == "source_code":
                content = path.read_text(errors='ignore')

                # Count lines of code (excluding blank lines and comments)
                lines = content.split('\n')
                code_lines = [l for l in lines if l.strip() and not l.strip().startswith(('#', '//', '/*', '*'))]
                metadata["lines_of_code"] = len(code_lines)

                # Simple complexity heuristic
                complexity = 0
                complexity += content.count('if ') + content.count('if(')
                complexity += content.count('for ') + content.count('for(')
                complexity += content.count('while ') + content.count('while(')
                complexity += content.count('switch ') + content.count('switch(')

                metadata["complexity_score"] = min(complexity, 100)

                # Check for business logic indicators
                business_keywords = ['calculate', 'process', 'validate', 'business',
                                   'order', 'payment', 'transaction', 'account']
                content_lower = content.lower()
                metadata["contains_business_logic"] = any(
                    keyword in content_lower for keyword in business_keywords
                )

        except Exception as e:
            metadata["error"] = str(e)

    return {
        "status": "success",
        "asset_path": asset_path,
        "metadata": metadata
    }


# Create the discovery agent
discovery_agent = Agent(
    name="discovery_agent",
    model="gemini-2.0-flash",
    description=(
        "Performs comprehensive asset inventory of legacy systems. "
        "Scans repositories to identify source code, database schemas, "
        "configuration files, infrastructure code, and documentation."
    ),
    instruction=(
        "You are a discovery agent responsible for comprehensive legacy system inventory. "
        "Your key responsibilities:\n"
        "1. Scan all repository paths to identify every asset\n"
        "2. Categorize assets: source code, DB schemas, configs, IaC, docs, API contracts\n"
        "3. Identify the complete technology stack (languages, frameworks, databases)\n"
        "4. Detect all dependencies (external libraries, internal modules)\n"
        "5. Create metadata for each asset to support downstream processing\n\n"
        "CRITICAL: Do not miss non-code assets. Legacy systems often embed business logic "
        "in database stored procedures, configuration files, and infrastructure definitions. "
        "Incomplete discovery will result in failed modernization.\n\n"
        "When scanning, look for:\n"
        "- Source code in all languages (COBOL, Java, Python, C++, etc.)\n"
        "- Database schemas (.sql, .ddl) and stored procedures\n"
        "- Configuration files (.yaml, .json, .xml, .conf)\n"
        "- Infrastructure as Code (.tf, CloudFormation templates)\n"
        "- API contracts (OpenAPI, WSDL, etc.)\n"
        "- Documentation (README, design docs, comments)\n\n"
        "For each asset, extract metadata:\n"
        "- File size and last modified date\n"
        "- Lines of code for source files\n"
        "- Complexity metrics\n"
        "- Business logic indicators\n\n"
        "Provide actionable modernization recommendations based on discovered technologies."
    ),
    tools=[
        scan_repository,
        identify_technology_stack,
        detect_dependencies,
        create_asset_metadata
    ]
)
