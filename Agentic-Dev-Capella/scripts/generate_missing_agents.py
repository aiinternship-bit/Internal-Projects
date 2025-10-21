"""
scripts/generate_missing_agents.py

Script to generate all missing agent implementations with A2A communication support.
"""

import os
from pathlib import Path

# Agent templates
AGENT_TEMPLATES = {
    "stage0_discovery/domain_expert": {
        "tools": [
            ("infer_business_domain", "Infer business domain from code patterns and structure"),
            ("identify_business_rules", "Identify business rules embedded in legacy code"),
            ("extract_domain_terminology", "Extract domain-specific terminology"),
            ("map_business_workflows", "Map business workflows from code flow"),
        ],
        "description": "Domain expert agent that infers business context from legacy code",
        "instruction": """You are a domain expert agent that analyzes legacy code to understand business context.

Your key responsibilities:
1. Infer business domain from code patterns (finance, healthcare, retail, etc.)
2. Identify business rules embedded in the code
3. Extract domain-specific terminology and concepts
4. Map business workflows and processes
5. Provide business context to other agents

Use pattern matching, code analysis, and documentation mining to build domain knowledge."""
    },

    "stage1_etl/code_ingestion": {
        "tools": [
            ("scan_codebase", "Scan legacy codebase and catalog files"),
            ("parse_source_files", "Parse source files by language"),
            ("extract_metadata", "Extract metadata (LOC, complexity, dependencies)"),
            ("batch_upload_to_storage", "Upload code artifacts to GCS"),
        ],
        "description": "Code ingestion agent that scans and catalogs legacy codebase",
        "instruction": """You are a code ingestion agent that processes legacy codebases.

Your key responsibilities:
1. Recursively scan legacy codebase
2. Identify all source files by language
3. Parse and extract metadata (lines of code, complexity, dependencies)
4. Batch upload to cloud storage for processing
5. Track ingestion progress and handle errors

Support multiple languages: COBOL, Java, C++, Python, SQL, etc."""
    },

    "stage1_etl/static_analysis": {
        "tools": [
            ("analyze_code_complexity", "Analyze cyclomatic complexity"),
            ("detect_code_smells", "Detect code smells and anti-patterns"),
            ("analyze_dependencies", "Analyze code dependencies"),
            ("identify_security_issues", "Identify security vulnerabilities"),
        ],
        "description": "Static analysis agent that analyzes code quality and structure",
        "instruction": """You are a static analysis agent that performs deep code analysis.

Your key responsibilities:
1. Analyze code complexity (cyclomatic, cognitive)
2. Detect code smells and anti-patterns
3. Analyze dependencies and coupling
4. Identify security vulnerabilities
5. Generate analysis reports

Provide detailed insights for modernization planning."""
    },

    "stage1_etl/documentation_mining": {
        "tools": [
            ("extract_inline_comments", "Extract inline comments and annotations"),
            ("parse_documentation_files", "Parse README, design docs, wikis"),
            ("extract_api_documentation", "Extract API documentation"),
            ("mine_commit_messages", "Mine git commit messages for context"),
        ],
        "description": "Documentation mining agent that extracts knowledge from docs",
        "instruction": """You are a documentation mining agent that extracts knowledge from documentation.

Your key responsibilities:
1. Extract inline comments and docstrings
2. Parse documentation files (README, wikis, design docs)
3. Extract API documentation
4. Mine version control history for context
5. Synthesize documentation into structured knowledge

Extract business logic, design decisions, and architectural context."""
    },

    "stage1_etl/knowledge_synthesis": {
        "tools": [
            ("generate_embeddings", "Generate embeddings for code and docs"),
            ("store_in_vector_db", "Store embeddings in Vector Search"),
            ("create_knowledge_graph", "Create knowledge graph of components"),
            ("synthesize_component_docs", "Synthesize component documentation"),
        ],
        "description": "Knowledge synthesis agent that creates searchable knowledge base",
        "instruction": """You are a knowledge synthesis agent that creates a searchable knowledge base.

Your key responsibilities:
1. Generate embeddings for code and documentation
2. Store embeddings in Vertex AI Vector Search
3. Create knowledge graph of component relationships
4. Synthesize comprehensive component documentation
5. Enable semantic search for context retrieval

Build a rich, queryable knowledge base for modernization."""
    },

    "stage1_etl/delta_monitoring": {
        "tools": [
            ("monitor_source_changes", "Monitor legacy codebase for changes"),
            ("detect_version_drift", "Detect drift from baseline"),
            ("trigger_incremental_sync", "Trigger incremental knowledge sync"),
            ("alert_on_critical_changes", "Alert on critical changes"),
        ],
        "description": "Delta monitoring agent that tracks changes in legacy codebase",
        "instruction": """You are a delta monitoring agent that tracks changes in the legacy codebase.

Your key responsibilities:
1. Continuously monitor legacy codebase for changes
2. Detect version drift from baseline
3. Trigger incremental knowledge synchronization
4. Alert on critical changes that impact modernization
5. Maintain change history

Ensure knowledge base stays synchronized with legacy system."""
    },

    # Stage 2 agents would continue here...
}

def generate_agent_file(stage_path: str, agent_data: dict) -> str:
    """Generate agent implementation file content."""

    # Generate tool functions
    tools_code = []
    tool_names = []

    for tool_name, tool_desc in agent_data["tools"]:
        tool_names.append(tool_name)
        tools_code.append(f'''
def {tool_name}(**kwargs) -> Dict[str, Any]:
    """
    {tool_desc}

    Returns:
        dict: Operation result
    """
    # Implementation would go here
    return {{"status": "success", "message": "{tool_desc}"}}
''')

    # Generate agent code
    agent_name = stage_path.split('/')[-1] + "_agent"

    content = f'''"""
agents/{stage_path}/agent.py

{agent_data["description"]}
"""

from typing import Dict, List, Any
from google.adk.agents import Agent

{chr(10).join(tools_code)}

# Create the {agent_name}
{agent_name} = Agent(
    name="{agent_name}",
    model="gemini-2.0-flash",
    description="{agent_data["description"]}",
    instruction="""{agent_data["instruction"]}""",
    tools=[
        {", ".join(tool_names)}
    ]
)
'''

    return content


def main():
    """Generate all missing agent files."""
    base_path = Path(__file__).parent.parent / "agents"

    for stage_path, agent_data in AGENT_TEMPLATES.items():
        full_path = base_path / stage_path
        full_path.mkdir(parents=True, exist_ok=True)

        # Create __init__.py
        init_file = full_path / "__init__.py"
        if not init_file.exists():
            init_file.write_text(f'"""{''.join(stage_path.split('/')[-1:])} agent module."""\n')

        # Create agent.py
        agent_file = full_path / "agent.py"
        if not agent_file.exists():
            content = generate_agent_file(stage_path, agent_data)
            agent_file.write_text(content)
            print(f"✓ Created {stage_path}/agent.py")
        else:
            print(f"  Skipped {stage_path}/agent.py (already exists)")


if __name__ == "__main__":
    main()
    print("\n✓ Agent generation complete!")
