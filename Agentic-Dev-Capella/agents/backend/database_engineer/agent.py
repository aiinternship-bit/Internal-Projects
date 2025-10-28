"""
agents/backend/database_engineer/agent.py

Database Engineer Agent - Designs schemas, generates migrations, optimizes queries.

Supports PostgreSQL, MySQL, MongoDB, Redis with best practices for schema design,
migrations, and query optimization.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re

from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration
from shared.utils.kb_integration_mixin import DynamicKnowledgeBaseIntegration


class DatabaseEngineerAgent(A2AEnabledAgent, DynamicKnowledgeBaseIntegration):
    """
    Database Engineer Agent for database design and optimization.

    Capabilities:
    - Schema design (PostgreSQL, MySQL, MongoDB, Redis)
    - Migration script generation
    - Query optimization
    - ER diagram generation
    - Index strategy recommendations
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        vector_db_client=None,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize Database Engineer Agent."""
        A2AEnabledAgent.__init__(self, context, message_bus)

        self.context = context
        self.orchestrator_id = orchestrator_id
        self.model_name = model_name

        # Initialize A2A integration
        self.a2a = A2AIntegration(
            context=context,
            message_bus=message_bus,
            orchestrator_id=orchestrator_id
        )

        # Initialize KB integration
        if vector_db_client:
            self.initialize_kb_integration(
                vector_db_client=vector_db_client,
                kb_query_strategy="adaptive"
            )

        # Initialize Vertex AI
        aiplatform.init(
            project=context.get("project_id"),
            location=context.get("location", "us-central1")
        )

        self.model = GenerativeModel(model_name)
        self.dev_history: List[Dict[str, Any]] = []

    def handle_task_assignment(self, message: Dict[str, Any]) -> None:
        """Handle TASK_ASSIGNMENT message from orchestrator."""
        payload = message.get("payload", {})
        task_id = payload.get("task_id")
        task_type = payload.get("task_type")
        parameters = payload.get("parameters", {})

        try:
            if task_type == "design_database_schema":
                result = self.design_database_schema(task_id=task_id, **parameters)
            elif task_type == "generate_migration_scripts":
                result = self.generate_migration_scripts(task_id=task_id, **parameters)
            elif task_type == "optimize_queries":
                result = self.optimize_queries(task_id=task_id, **parameters)
            elif task_type == "generate_er_diagram":
                result = self.generate_er_diagram(task_id=task_id, **parameters)
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            self.a2a.send_completion(
                task_id=task_id,
                artifacts=result,
                metrics={"kb_queries_used": getattr(self, "_kb_query_count", 0)}
            )

        except Exception as e:
            self.a2a.send_error_report(
                task_id=task_id,
                error_type="DATABASE_DESIGN_FAILED",
                error_message=str(e),
                stack_trace=""
            )

    @A2AIntegration.with_task_tracking
    def design_database_schema(
        self,
        requirements: Dict[str, Any],
        database_type: str,
        constraints: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Design database schema based on requirements.

        Args:
            requirements: Schema requirements (entities, relationships, etc.)
            database_type: Database type (postgresql, mysql, mongodb, redis)
            constraints: Additional constraints (performance, scaling, etc.)
            task_id: Optional task ID

        Returns:
            {
                "schema": str,
                "migrations": str,
                "indexes": List[str],
                "er_diagram": str,
                "documentation": str
            }
        """
        start_time = datetime.utcnow()
        print(f"[DB Engineer] Designing schema for {database_type}")

        # Query KB for similar schemas
        kb_context = ""
        if hasattr(self, 'should_query_kb') and self.should_query_kb(requirements):
            kb_results = self.execute_dynamic_query(
                query_type="schema_patterns",
                context={"database": database_type, "entities": requirements.get("entities", [])},
                task_id=task_id
            )
            if kb_results:
                kb_context = self._format_kb_results(kb_results)

        # Build prompt
        prompt = self._build_schema_design_prompt(
            requirements=requirements,
            database_type=database_type,
            constraints=constraints,
            kb_context=kb_context
        )

        # Generate with LLM
        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        # Parse result
        result = self._parse_schema_design(response.text, database_type)

        # Add metadata
        duration = (datetime.utcnow() - start_time).total_seconds() / 60
        result.update({
            "database_type": database_type,
            "duration_minutes": duration,
            "timestamp": datetime.utcnow().isoformat()
        })

        self.dev_history.append({
            "task_id": task_id,
            "operation": "schema_design",
            "database_type": database_type,
            "timestamp": result["timestamp"]
        })

        return result

    @A2AIntegration.with_task_tracking
    def generate_migration_scripts(
        self,
        from_schema: str,
        to_schema: str,
        database_type: str,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate migration scripts to transform schema.

        Args:
            from_schema: Current schema
            to_schema: Target schema
            database_type: Database type
            task_id: Optional task ID

        Returns:
            {
                "up_migration": str,
                "down_migration": str,
                "migration_notes": str
            }
        """
        print(f"[DB Engineer] Generating migrations for {database_type}")

        prompt = self._build_migration_prompt(from_schema, to_schema, database_type)
        response = self.model.generate_content(prompt, generation_config=self._get_generation_config())

        result = self._parse_migration_scripts(response.text)
        result.update({
            "database_type": database_type,
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    @A2AIntegration.with_task_tracking
    def optimize_queries(
        self,
        queries: List[str],
        database_type: str,
        performance_targets: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Optimize database queries for performance.

        Args:
            queries: List of queries to optimize
            database_type: Database type
            performance_targets: Target metrics (latency, throughput)
            task_id: Optional task ID

        Returns:
            {
                "optimized_queries": List[str],
                "indexes_recommended": List[str],
                "performance_analysis": str
            }
        """
        print(f"[DB Engineer] Optimizing {len(queries)} queries")

        prompt = self._build_optimization_prompt(queries, database_type, performance_targets)
        response = self.model.generate_content(prompt, generation_config=self._get_generation_config())

        result = self._parse_optimization_result(response.text)
        result.update({
            "query_count": len(queries),
            "database_type": database_type,
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    @A2AIntegration.with_task_tracking
    def generate_er_diagram(
        self,
        schema: str,
        format: str = "mermaid",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate ER diagram from schema.

        Args:
            schema: Database schema
            format: Diagram format (mermaid, plantuml)
            task_id: Optional task ID

        Returns:
            {
                "diagram": str,
                "format": str
            }
        """
        print(f"[DB Engineer] Generating ER diagram ({format})")

        prompt = f"""
Generate an ER diagram in {format} format for the following database schema:

{schema}

Requirements:
1. Show all entities and their attributes
2. Show relationships with cardinality
3. Highlight primary and foreign keys
4. Use clear, readable notation

Return the diagram code that can be rendered directly.
"""

        response = self.model.generate_content(prompt, generation_config=self._get_generation_config())

        return {
            "diagram": response.text,
            "format": format,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _build_schema_design_prompt(
        self,
        requirements: Dict[str, Any],
        database_type: str,
        constraints: Optional[Dict[str, Any]],
        kb_context: str
    ) -> str:
        """Build schema design prompt."""

        entities = requirements.get("entities", [])
        relationships = requirements.get("relationships", [])

        if database_type in ["postgresql", "mysql"]:
            prompt = f"""
Design a normalized database schema for {database_type.upper()}:

**Entities:**
{json.dumps(entities, indent=2)}

**Relationships:**
{json.dumps(relationships, indent=2)}

**Constraints:**
{json.dumps(constraints or {}, indent=2)}

Requirements:
1. Follow normalization best practices (at least 3NF)
2. Define proper primary keys and foreign keys
3. Add appropriate indexes for performance
4. Include check constraints and default values
5. Add timestamps (created_at, updated_at)
6. Consider partitioning for large tables
7. Add comments for documentation

Provide:
1. CREATE TABLE statements
2. CREATE INDEX statements
3. Foreign key constraints
4. Initial migration script
5. ER diagram (Mermaid format)
6. Documentation

{kb_context}
"""
        else:  # mongodb, redis
            prompt = f"""
Design a document/key-value schema for {database_type.upper()}:

**Collections/Keys:**
{json.dumps(entities, indent=2)}

**Relationships:**
{json.dumps(relationships, indent=2)}

Requirements:
1. Optimize for query patterns
2. Consider embedding vs referencing
3. Define indexes for performance
4. Handle data consistency
5. Plan for sharding if needed

Provide:
1. Collection/Key schemas
2. Index definitions
3. Data modeling rationale
4. Query patterns
5. Documentation

{kb_context}
"""

        return prompt

    def _build_migration_prompt(self, from_schema: str, to_schema: str, database_type: str) -> str:
        """Build migration prompt."""
        return f"""
Generate migration scripts to transform the database schema from:

**Current Schema:**
```sql
{from_schema}
```

**Target Schema:**
```sql
{to_schema}
```

**Database:** {database_type}

Requirements:
1. Generate UP migration (apply changes)
2. Generate DOWN migration (rollback changes)
3. Preserve existing data
4. Handle column renames safely
5. Add appropriate indexes
6. Consider performance impact

Provide:
1. UP migration script
2. DOWN migration script
3. Migration notes and warnings
4. Estimated execution time
"""

    def _build_optimization_prompt(
        self,
        queries: List[str],
        database_type: str,
        performance_targets: Optional[Dict[str, Any]]
    ) -> str:
        """Build query optimization prompt."""

        queries_formatted = "\n\n".join([f"Query {i+1}:\n```sql\n{q}\n```" for i, q in enumerate(queries)])

        return f"""
Optimize the following {database_type.upper()} queries:

{queries_formatted}

**Performance Targets:**
{json.dumps(performance_targets or {"latency_ms": 100}, indent=2)}

Requirements:
1. Analyze query execution plans
2. Identify performance bottlenecks
3. Recommend index optimizations
4. Rewrite queries for better performance
5. Suggest query hints if applicable
6. Consider caching strategies

Provide:
1. Optimized versions of each query
2. Recommended indexes
3. Performance analysis
4. Expected improvements
5. Trade-offs and considerations
"""

    def _parse_schema_design(self, text: str, database_type: str) -> Dict[str, Any]:
        """Parse schema design result."""
        result = {
            "schema": "",
            "migrations": "",
            "indexes": [],
            "er_diagram": "",
            "documentation": ""
        }

        code_blocks = re.findall(r'```(\w+)?\n(.*?)```', text, re.DOTALL)

        for lang, code in code_blocks:
            lang = lang.lower() if lang else ""

            if lang in ["sql", "postgres", "mysql"]:
                if "create index" in code.lower():
                    result["indexes"].append(code.strip())
                else:
                    result["schema"] += code.strip() + "\n\n"

            elif lang == "mermaid":
                result["er_diagram"] = code.strip()

            elif lang in ["markdown", "md", ""]:
                result["documentation"] += code.strip() + "\n\n"

        if not result["schema"]:
            result["schema"] = text

        return result

    def _parse_migration_scripts(self, text: str) -> Dict[str, Any]:
        """Parse migration scripts."""
        result = {
            "up_migration": "",
            "down_migration": "",
            "migration_notes": ""
        }

        # Extract UP and DOWN migrations
        up_match = re.search(r'(?:UP|Forward|Apply).*?```sql\n(.*?)```', text, re.DOTALL | re.IGNORECASE)
        down_match = re.search(r'(?:DOWN|Rollback|Revert).*?```sql\n(.*?)```', text, re.DOTALL | re.IGNORECASE)

        if up_match:
            result["up_migration"] = up_match.group(1).strip()
        if down_match:
            result["down_migration"] = down_match.group(1).strip()

        result["migration_notes"] = text

        return result

    def _parse_optimization_result(self, text: str) -> Dict[str, Any]:
        """Parse query optimization result."""
        result = {
            "optimized_queries": [],
            "indexes_recommended": [],
            "performance_analysis": text
        }

        code_blocks = re.findall(r'```sql\n(.*?)```', text, re.DOTALL)
        result["optimized_queries"] = [block.strip() for block in code_blocks]

        # Extract index recommendations
        index_matches = re.findall(r'CREATE INDEX.*?;', text, re.DOTALL | re.IGNORECASE)
        result["indexes_recommended"] = [idx.strip() for idx in index_matches]

        return result

    def _get_generation_config(self) -> Dict[str, Any]:
        """Get generation config for LLM."""
        return {
            "temperature": 0.2,
            "max_output_tokens": 8192,
            "top_p": 0.95,
            "top_k": 40
        }

    def _format_kb_results(self, results: List[Dict]) -> str:
        """Format KB query results."""
        if not results:
            return ""
        formatted = "\n\nRelevant schema patterns from knowledge base:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result.get('content', '')}\n\n"
        return formatted


# Standalone tool functions

def design_database_schema(
    requirements: Dict[str, Any],
    database_type: str,
    constraints: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Standalone function for schema design."""
    agent = DatabaseEngineerAgent(context={}, message_bus=None, orchestrator_id="")
    return agent.design_database_schema(requirements, database_type, constraints)


def generate_migration_scripts(
    from_schema: str,
    to_schema: str,
    database_type: str
) -> Dict[str, Any]:
    """Standalone function for migration generation."""
    agent = DatabaseEngineerAgent(context={}, message_bus=None, orchestrator_id="")
    return agent.generate_migration_scripts(from_schema, to_schema, database_type)


def optimize_queries(
    queries: List[str],
    database_type: str,
    performance_targets: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Standalone function for query optimization."""
    agent = DatabaseEngineerAgent(context={}, message_bus=None, orchestrator_id="")
    return agent.optimize_queries(queries, database_type, performance_targets)
