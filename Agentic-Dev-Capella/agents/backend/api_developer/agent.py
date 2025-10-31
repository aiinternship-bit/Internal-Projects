"""
agents/backend/api_developer/agent.py

API Developer Agent - Generates REST, GraphQL, and gRPC APIs with documentation.

Implements production-ready APIs with validation, error handling, authentication,
and comprehensive documentation.
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


class APIDevAgent(A2AEnabledAgent, DynamicKnowledgeBaseIntegration):
    """
    API Developer Agent for generating production-ready APIs.

    Capabilities:
    - REST API development (Express, FastAPI, Gin, Spring Boot)
    - GraphQL API development (Apollo Server, Strawberry, gqlgen)
    - gRPC service development
    - OpenAPI/Swagger documentation generation
    - API testing and validation
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        vector_db_client=None,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize API Developer Agent."""
        A2AEnabledAgent.__init__(self, context, message_bus)

        self.context = context
        self.orchestrator_id = orchestrator_id
        self.model_name = model_name

        # Initialize A2A integration
        self.a2a = A2AIntegration(
            agent_context=context,
            message_bus=message_bus,
            orchestrator_id=orchestrator_id
        )

        # Initialize KB integration if vector_db_client provided
        self._kb_query_strategy = "never"  # Default
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

        # Development history
        self.dev_history: List[Dict[str, Any]] = []

    def handle_task_assignment(self, message: Dict[str, Any]) -> None:
        """Handle TASK_ASSIGNMENT message from orchestrator."""
        payload = message.get("payload", {})
        task_id = payload.get("task_id")
        task_type = payload.get("task_type")
        parameters = payload.get("parameters", {})

        try:
            # Route to appropriate handler
            if task_type == "generate_rest_api":
                result = self.generate_rest_api(task_id=task_id, **parameters)
            elif task_type == "generate_graphql_api":
                result = self.generate_graphql_api(task_id=task_id, **parameters)
            elif task_type == "generate_grpc_service":
                result = self.generate_grpc_service(task_id=task_id, **parameters)
            elif task_type == "generate_api_documentation":
                result = self.generate_api_documentation(task_id=task_id, **parameters)
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            # Send completion
            self.a2a.send_completion(
                task_id=task_id,
                artifacts=result,
                metrics={
                    "kb_queries_used": getattr(self, "_kb_query_count", 0),
                    "lines_of_code": result.get("lines_of_code", 0)
                }
            )

        except Exception as e:
            self.a2a.send_error_report(
                task_id=task_id,
                error_type="API_GENERATION_FAILED",
                error_message=str(e),
                stack_trace=""
            )

    
    def generate_rest_api(
        self,
        language: str,
        framework: str,
        endpoints: List[Dict[str, Any]],
        auth_type: str = "none",
        database: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate RESTful API implementation.

        Args:
            language: Programming language (typescript, python, go, java)
            framework: Framework (express, fastapi, gin, spring-boot)
            endpoints: List of endpoint specifications
            auth_type: Authentication type (none, jwt, oauth, api_key)
            database: Database type if needed (postgresql, mysql, mongodb)
            task_id: Optional task ID

        Returns:
            {
                "api_code": str,
                "tests": str,
                "documentation": str,
                "openapi_spec": str,
                "lines_of_code": int
            }
        """
        start_time = datetime.utcnow()

        print(f"[API Developer] Generating REST API ({framework})")

        # Query KB for similar API implementations
        kb_context = ""
        if hasattr(self, 'should_query_kb') and self.should_query_kb({"language": language}):
            kb_results = self.execute_dynamic_query(
                query_type="api_patterns",
                context={
                    "framework": framework,
                    "language": language,
                    "auth_type": auth_type
                },
                task_id=task_id
            )
            if kb_results:
                kb_context = self._format_kb_results(kb_results)

        # Build prompt
        prompt = self._build_rest_api_prompt(
            language=language,
            framework=framework,
            endpoints=endpoints,
            auth_type=auth_type,
            database=database,
            kb_context=kb_context
        )

        # Generate with LLM
        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        # Parse and validate result
        result = self._parse_api_implementation(response.text, language)

        # Validate syntax
        validation_result = self._validate_code_syntax(result["api_code"], language)
        if not validation_result["valid"]:
            print(f"[API Developer] Syntax validation failed: {validation_result['errors']}")
            # Could retry with feedback here

        # Add metadata
        duration = (datetime.utcnow() - start_time).total_seconds() / 60
        result.update({
            "status": "success",
            "api_type": "rest",
            "language": language,
            "framework": framework,
            "auth_type": auth_type,
            "duration_minutes": duration,
            "timestamp": datetime.utcnow().isoformat(),
            "syntax_valid": validation_result["valid"]
        })

        # Store in history
        self.dev_history.append({
            "task_id": task_id,
            "api_type": "rest",
            "framework": framework,
            "endpoint_count": len(endpoints),
            "timestamp": result["timestamp"]
        })

        return result

    
    def generate_graphql_api(
        self,
        language: str,
        schema: str,
        resolvers: List[str],
        auth_type: str = "none",
        database: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate GraphQL API implementation.

        Args:
            language: Programming language (typescript, python, go)
            schema: GraphQL schema definition
            resolvers: List of resolver names to implement
            auth_type: Authentication type
            database: Database type if needed
            task_id: Optional task ID

        Returns:
            {
                "api_code": str,
                "schema": str,
                "tests": str,
                "documentation": str,
                "lines_of_code": int
            }
        """
        start_time = datetime.utcnow()

        print(f"[API Developer] Generating GraphQL API ({language})")

        # Query KB for GraphQL patterns
        kb_context = ""
        if hasattr(self, 'should_query_kb') and self.should_query_kb({"language": language}):
            kb_results = self.execute_dynamic_query(
                query_type="graphql_patterns",
                context={"language": language, "resolvers": len(resolvers)},
                task_id=task_id
            )
            if kb_results:
                kb_context = self._format_kb_results(kb_results)

        # Build prompt
        prompt = self._build_graphql_api_prompt(
            language=language,
            schema=schema,
            resolvers=resolvers,
            auth_type=auth_type,
            database=database,
            kb_context=kb_context
        )

        # Generate with LLM
        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        # Parse result
        result = self._parse_api_implementation(response.text, language)

        # Add metadata
        duration = (datetime.utcnow() - start_time).total_seconds() / 60
        result.update({
            "api_type": "graphql",
            "language": language,
            "auth_type": auth_type,
            "duration_minutes": duration,
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    
    def generate_grpc_service(
        self,
        language: str,
        proto_definition: str,
        service_name: str,
        methods: List[str],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate gRPC service implementation.

        Args:
            language: Programming language (typescript, python, go)
            proto_definition: Protocol Buffer definition
            service_name: Service name
            methods: List of RPC methods to implement
            task_id: Optional task ID

        Returns:
            {
                "api_code": str,
                "proto_file": str,
                "tests": str,
                "documentation": str,
                "lines_of_code": int
            }
        """
        start_time = datetime.utcnow()

        print(f"[API Developer] Generating gRPC service ({language})")

        # Query KB for gRPC patterns
        kb_context = ""
        if hasattr(self, 'should_query_kb') and self.should_query_kb({"language": language}):
            kb_results = self.execute_dynamic_query(
                query_type="grpc_patterns",
                context={"language": language, "service": service_name},
                task_id=task_id
            )
            if kb_results:
                kb_context = self._format_kb_results(kb_results)

        # Build prompt
        prompt = self._build_grpc_service_prompt(
            language=language,
            proto_definition=proto_definition,
            service_name=service_name,
            methods=methods,
            kb_context=kb_context
        )

        # Generate with LLM
        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        # Parse result
        result = self._parse_api_implementation(response.text, language)

        # Add metadata
        duration = (datetime.utcnow() - start_time).total_seconds() / 60
        result.update({
            "api_type": "grpc",
            "language": language,
            "service_name": service_name,
            "duration_minutes": duration,
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    
    def generate_api_documentation(
        self,
        api_code: str,
        api_type: str,
        language: str,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive API documentation.

        Args:
            api_code: API implementation code
            api_type: Type of API (rest, graphql, grpc)
            language: Programming language
            task_id: Optional task ID

        Returns:
            {
                "documentation": str,
                "openapi_spec": str (if REST),
                "examples": List[str]
            }
        """
        print(f"[API Developer] Generating API documentation")

        prompt = f"""
Generate comprehensive API documentation for the following {api_type.upper()} API written in {language}:

```{language}
{api_code}
```

Requirements:
1. Overview of the API
2. Authentication details
3. Endpoint/Query documentation
4. Request/Response examples
5. Error handling details
6. Rate limiting information (if applicable)
7. Usage examples in multiple languages
{"8. OpenAPI 3.0 specification (JSON format)" if api_type == "rest" else ""}

Provide clear, well-structured documentation suitable for developers.
"""

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config()
        )

        result = {
            "documentation": response.text,
            "api_type": api_type,
            "language": language,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Extract OpenAPI spec if REST
        if api_type == "rest":
            openapi_match = re.search(r'```json\n(.*?)```', response.text, re.DOTALL)
            if openapi_match:
                result["openapi_spec"] = openapi_match.group(1).strip()

        return result

    def _build_rest_api_prompt(
        self,
        language: str,
        framework: str,
        endpoints: List[Dict[str, Any]],
        auth_type: str,
        database: Optional[str],
        kb_context: str
    ) -> str:
        """Build REST API generation prompt."""

        endpoints_formatted = "\n".join([
            f"- {ep.get('method', 'GET')} {ep.get('path', '/')}: {ep.get('description', '')}"
            for ep in endpoints
        ])

        framework_templates = {
            "express": f"""
Generate a production-ready REST API using Express.js (TypeScript):

**Framework:** Express.js with TypeScript
**Endpoints:**
{endpoints_formatted}

**Authentication:** {auth_type}
**Database:** {database or 'None'}

Requirements:
1. Use Express.js with TypeScript and proper types
2. Implement all endpoints with full CRUD operations
3. Add {auth_type} authentication middleware
4. Include request validation (using Zod or Joi)
5. Add comprehensive error handling
6. Include CORS configuration
7. Add rate limiting
8. Include logging (Winston or similar)
9. Add health check endpoint
10. Include JSDoc comments
{"11. Include database models and migrations" if database else ""}

Provide:
1. Main API code with routes
2. Middleware implementations
3. Unit tests (Jest)
4. API documentation
5. OpenAPI 3.0 specification

{kb_context}

Return structured code with clear section markers.
""",
            "fastapi": f"""
Generate a production-ready REST API using FastAPI (Python):

**Framework:** FastAPI with Python 3.10+
**Endpoints:**
{endpoints_formatted}

**Authentication:** {auth_type}
**Database:** {database or 'None'}

Requirements:
1. Use FastAPI with Pydantic models
2. Implement all endpoints with proper type hints
3. Add {auth_type} authentication dependencies
4. Include request/response validation with Pydantic
5. Add comprehensive error handling
6. Include CORS middleware
7. Add rate limiting
8. Include logging
9. Add health check and docs endpoints
10. Use async/await where appropriate
{"11. Include SQLAlchemy models and Alembic migrations" if database else ""}

Provide:
1. Main API code (main.py, routers, models)
2. Authentication dependencies
3. Unit tests (pytest)
4. API documentation
5. OpenAPI spec (auto-generated, show how to access)

{kb_context}

Return structured code with clear section markers.
""",
            "gin": f"""
Generate a production-ready REST API using Gin (Go):

**Framework:** Gin with Go 1.21+
**Endpoints:**
{endpoints_formatted}

**Authentication:** {auth_type}
**Database:** {database or 'None'}

Requirements:
1. Use Gin framework with proper structure
2. Implement all endpoints with proper error handling
3. Add {auth_type} authentication middleware
4. Include request validation
5. Add comprehensive error handling
6. Include CORS middleware
7. Add rate limiting middleware
8. Include structured logging
9. Add health check endpoint
{"10. Include database models and migrations using GORM" if database else ""}

Provide:
1. Main API code (handlers, middleware, models)
2. Authentication middleware
3. Unit tests
4. API documentation
5. Swagger/OpenAPI configuration

{kb_context}

Return structured code with clear section markers.
""",
            "spring-boot": f"""
Generate a production-ready REST API using Spring Boot (Java):

**Framework:** Spring Boot 3.x with Java 17+
**Endpoints:**
{endpoints_formatted}

**Authentication:** {auth_type}
**Database:** {database or 'None'}

Requirements:
1. Use Spring Boot with proper annotations
2. Implement all endpoints with @RestController
3. Add {auth_type} authentication with Spring Security
4. Include request validation with @Valid
5. Add comprehensive exception handling with @ExceptionHandler
6. Include CORS configuration
7. Add rate limiting
8. Include SLF4J logging
9. Add actuator health checks
{"10. Include JPA entities and Flyway migrations" if database else ""}

Provide:
1. Main application and controllers
2. Security configuration
3. Unit tests (JUnit 5, MockMvc)
4. API documentation
5. OpenAPI 3.0 specification (Springdoc)

{kb_context}

Return structured code with clear section markers.
"""
        }

        return framework_templates.get(framework, framework_templates["express"])

    def _build_graphql_api_prompt(
        self,
        language: str,
        schema: str,
        resolvers: List[str],
        auth_type: str,
        database: Optional[str],
        kb_context: str
    ) -> str:
        """Build GraphQL API generation prompt."""

        resolvers_formatted = "\n".join([f"- {resolver}" for resolver in resolvers])

        if language == "typescript":
            framework = "Apollo Server"
        elif language == "python":
            framework = "Strawberry"
        elif language == "go":
            framework = "gqlgen"
        else:
            framework = "Apollo Server"

        prompt = f"""
Generate a production-ready GraphQL API using {framework} ({language}):

**Schema:**
```graphql
{schema}
```

**Resolvers to implement:**
{resolvers_formatted}

**Authentication:** {auth_type}
**Database:** {database or 'None'}

Requirements:
1. Implement the provided GraphQL schema
2. Create all resolvers with proper type safety
3. Add {auth_type} authentication to protected resolvers
4. Include input validation
5. Add comprehensive error handling
6. Include DataLoader for N+1 prevention
7. Add query complexity limiting
8. Include logging
9. Add introspection controls
{"10. Include database models and queries" if database else ""}

Provide:
1. Schema definition file
2. Resolver implementations
3. Context setup with authentication
4. DataLoader implementations
5. Unit tests
6. API documentation with example queries

{kb_context}

Return structured code with clear section markers.
"""

        return prompt

    def _build_grpc_service_prompt(
        self,
        language: str,
        proto_definition: str,
        service_name: str,
        methods: List[str],
        kb_context: str
    ) -> str:
        """Build gRPC service generation prompt."""

        methods_formatted = "\n".join([f"- {method}" for method in methods])

        prompt = f"""
Generate a production-ready gRPC service ({language}):

**Service Name:** {service_name}

**Protocol Buffer Definition:**
```protobuf
{proto_definition}
```

**Methods to implement:**
{methods_formatted}

Requirements:
1. Implement all RPC methods
2. Add proper error handling with gRPC status codes
3. Include request validation
4. Add interceptors for logging and authentication
5. Include comprehensive error messages
6. Add health check service
7. Include server reflection for debugging
8. Add proper timeout handling
9. Include retry policies on client side

Provide:
1. Protocol Buffer definition (.proto file)
2. Server implementation
3. Client implementation with examples
4. Interceptors
5. Unit tests
6. Documentation

{kb_context}

Return structured code with clear section markers.
"""

        return prompt

    def _parse_api_implementation(
        self,
        implementation: str,
        language: str
    ) -> Dict[str, Any]:
        """Parse LLM API implementation into structured format."""

        result = {
            "api_code": "",
            "tests": "",
            "documentation": "",
            "openapi_spec": "",
            "lines_of_code": 0
        }

        # Extract code blocks
        code_blocks = re.findall(r'```(\w+)?\n(.*?)```', implementation, re.DOTALL)

        for lang, code in code_blocks:
            lang = lang.lower() if lang else ""

            # Determine block type
            if any(x in lang for x in [language, "typescript", "python", "go", "java"]):
                if "test" in code.lower():
                    result["tests"] += code.strip() + "\n\n"
                else:
                    result["api_code"] += code.strip() + "\n\n"

            elif lang == "json":
                # Could be OpenAPI spec
                if "openapi" in code.lower() or "swagger" in code.lower():
                    result["openapi_spec"] = code.strip()

            elif lang in ["yaml", "yml"]:
                # Could be OpenAPI spec in YAML
                if "openapi" in code.lower():
                    result["openapi_spec"] = code.strip()

            elif lang in ["markdown", "md", ""]:
                result["documentation"] += code.strip() + "\n\n"

        # Count lines of code
        if result["api_code"]:
            result["lines_of_code"] = len([
                line for line in result["api_code"].split("\n")
                if line.strip() and not line.strip().startswith("//") and not line.strip().startswith("#")
            ])

        # If no structured extraction, use raw
        if not result["api_code"]:
            result["api_code"] = implementation
            result["lines_of_code"] = len(implementation.split("\n"))

        return result

    def _validate_code_syntax(
        self,
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """Validate code syntax (basic validation)."""

        result = {
            "valid": True,
            "errors": []
        }

        try:
            if language == "python":
                import ast
                ast.parse(code)
            elif language in ["typescript", "javascript"]:
                # Basic brace matching
                if code.count("{") != code.count("}"):
                    result["valid"] = False
                    result["errors"].append("Mismatched braces")
            # Could add more language-specific validation

        except SyntaxError as e:
            result["valid"] = False
            result["errors"].append(f"Syntax error: {str(e)}")
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Validation error: {str(e)}")

        return result

    def _get_generation_config(self) -> Dict[str, Any]:
        """Get generation config for LLM."""
        return {
            "temperature": 0.2,  # Low temperature for consistent, production-ready code
            "max_output_tokens": 8192,
            "top_p": 0.95,
            "top_k": 40
        }

    def _format_kb_results(self, results: List[Dict]) -> str:
        """Format KB query results."""
        if not results:
            return ""

        formatted = "\n\nRelevant patterns from knowledge base:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result.get('content', '')}\n\n"
        return formatted


# Standalone tool functions for testing

def generate_rest_api(
    language: str,
    framework: str,
    endpoints: List[Dict[str, Any]],
    auth_type: str = "none",
    database: Optional[str] = None
) -> Dict[str, Any]:
    """Standalone function for REST API generation."""
    agent = APIDevAgent(
        context={},
        message_bus=None,
        orchestrator_id=""
    )
    return agent.generate_rest_api(
        language=language,
        framework=framework,
        endpoints=endpoints,
        auth_type=auth_type,
        database=database
    )


def generate_graphql_api(
    language: str,
    schema: str,
    resolvers: List[str],
    auth_type: str = "none",
    database: Optional[str] = None
) -> Dict[str, Any]:
    """Standalone function for GraphQL API generation."""
    agent = APIDevAgent(
        context={},
        message_bus=None,
        orchestrator_id=""
    )
    return agent.generate_graphql_api(
        language=language,
        schema=schema,
        resolvers=resolvers,
        auth_type=auth_type,
        database=database
    )


def generate_grpc_service(
    language: str,
    proto_definition: str,
    service_name: str,
    methods: List[str]
) -> Dict[str, Any]:
    """Standalone function for gRPC service generation."""
    agent = APIDevAgent(
        context={},
        message_bus=None,
        orchestrator_id=""
    )
    return agent.generate_grpc_service(
        language=language,
        proto_definition=proto_definition,
        service_name=service_name,
        methods=methods
    )
