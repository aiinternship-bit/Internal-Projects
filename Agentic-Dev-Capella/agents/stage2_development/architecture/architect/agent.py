"""
agents/stage2_development/architecture/architect/agent.py

Technical Architect agent designs target architecture for modernized components using LLM.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re

from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration


class TechnicalArchitectAgent(A2AEnabledAgent):
    """
    Technical Architect Agent for designing system architecture.

    Capabilities:
    - Design component architecture with layers and patterns
    - Define NFR (Non-Functional Requirements) strategies
    - Select appropriate design patterns
    - Create architecture specifications
    - Validate architectural feasibility
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize Technical Architect Agent."""
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

        # Initialize Vertex AI
        aiplatform.init(
            project=context.get("project_id") if hasattr(context, 'get') else getattr(context, 'project_id', None),
            location=context.get("location", "us-central1") if hasattr(context, 'get') else getattr(context, 'location', "us-central1")
        )

        self.model = GenerativeModel(model_name)

        # Architecture history
        self.architecture_history: List[Dict[str, Any]] = []

    def handle_task_assignment(self, message: Dict[str, Any]) -> None:
        """Handle TASK_ASSIGNMENT message from orchestrator."""
        payload = message.get("payload", {})
        task_id = payload.get("task_id")
        task_type = payload.get("task_type")
        parameters = payload.get("parameters", {})

        try:
            if task_type == "design_architecture":
                result = self.design_architecture(task_id=task_id, **parameters)
            elif task_type == "define_nfr_strategy":
                result = self.define_nfr_strategy(task_id=task_id, **parameters)
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            # Send completion
            self.a2a.send_completion(
                task_id=task_id,
                artifacts=result,
                metrics={}
            )

        except Exception as e:
            self.a2a.send_error_report(
                task_id=task_id,
                error_type="ARCHITECTURE_DESIGN_FAILED",
                error_message=str(e),
                stack_trace=""
            )

    def design_architecture(
        self,
        component_spec: Dict[str, Any],
        domain_model: Optional[Dict[str, Any]] = None,
        nfr_requirements: Optional[Dict[str, Any]] = None,
        target_language: str = "python",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Design architecture for a modernized component using LLM.

        Args:
            component_spec: Component specification
            domain_model: Domain model with business entities
            nfr_requirements: Non-functional requirements
            target_language: Target programming language
            task_id: Optional task ID

        Returns:
            Complete architecture design with layers, patterns, and data model
        """
        start_time = datetime.utcnow()

        component_name = component_spec.get("name", "Component")
        print(f"[Technical Architect] Designing architecture for {component_name}")

        # Build comprehensive prompt
        prompt = self._build_architecture_prompt(
            component_spec, domain_model or {}, nfr_requirements or {}, target_language
        )

        # Generate with LLM
        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.4)
        )

        # Parse architecture design
        architecture = self._parse_architecture_response(response.text, component_name)

        duration = (datetime.utcnow() - start_time).total_seconds() / 60

        result = {
            "status": "success",
            "architecture_design": architecture,
            "duration_minutes": duration,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Store in history
        self.architecture_history.append({
            "task_id": task_id,
            "component_name": component_name,
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    def define_nfr_strategy(
        self,
        nfr_requirements: Dict[str, Any],
        component_name: str = "Component",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Define strategies to meet non-functional requirements using LLM.

        Args:
            nfr_requirements: Performance, security, scalability requirements
            component_name: Name of component
            task_id: Optional task ID

        Returns:
            NFR strategies with specific implementation approaches
        """
        start_time = datetime.utcnow()

        print(f"[Technical Architect] Defining NFR strategy for {component_name}")

        prompt = self._build_nfr_strategy_prompt(nfr_requirements, component_name)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.4)
        )

        nfr_strategies = self._parse_nfr_response(response.text)

        duration = (datetime.utcnow() - start_time).total_seconds() / 60

        return {
            "status": "success",
            "nfr_strategies": nfr_strategies,
            "duration_minutes": duration,
            "timestamp": datetime.utcnow().isoformat()
        }

    def choose_design_patterns(
        self,
        component_spec: Dict[str, Any],
        architecture_style: str = "microservice",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Choose appropriate design patterns using LLM."""
        print(f"[Technical Architect] Choosing design patterns")

        prompt = self._build_patterns_prompt(component_spec, architecture_style)

        response = self.model.generate_content(
            prompt,
            generation_config=self._get_generation_config(temperature=0.4)
        )

        patterns = self._parse_patterns_response(response.text)

        return {
            "status": "success",
            "design_patterns": patterns
        }

    # ========================================================================
    # PROMPT BUILDERS
    # ========================================================================

    def _build_architecture_prompt(
        self,
        component_spec: Dict[str, Any],
        domain_model: Dict[str, Any],
        nfr_requirements: Dict[str, Any],
        target_language: str
    ) -> str:
        """Build comprehensive architecture design prompt."""

        component_name = component_spec.get("name", "Component")
        component_desc = component_spec.get("description", "No description")

        spec_text = json.dumps(component_spec, indent=2)
        domain_text = json.dumps(domain_model, indent=2) if domain_model else "No domain model provided"
        nfr_text = json.dumps(nfr_requirements, indent=2) if nfr_requirements else "No specific NFRs"

        prompt = f"""You are an expert software architect specializing in {target_language} and modern cloud-native architectures.

Design a comprehensive, production-ready architecture for the following component:

**Component Name:** {component_name}
**Description:** {component_desc}
**Target Language:** {target_language}

**Component Specification:**
{spec_text}

**Domain Model:**
{domain_text}

**Non-Functional Requirements:**
{nfr_text}

**Architecture Requirements:**
1. Choose appropriate architecture style (microservice, modular monolith, serverless, etc.)
2. Define clear architectural layers with responsibilities
3. Select technologies appropriate for {target_language} ecosystem
4. Identify key components and their relationships
5. Choose design patterns that solve specific problems
6. Design data model with entities and relationships
7. Address all NFRs (performance, security, scalability)
8. Ensure testability and maintainability

**Response Format:**

**Architecture Style:** [microservice/monolith/serverless/layered/etc.]

**Layers:**
1. **[Layer Name]**
   - Responsibility: [What this layer does]
   - Technologies: [Specific tech stack]
   - Components: [Key components in this layer]

2. **[Next Layer]**
   - ...

**Design Patterns:**
1. **[Pattern Name]**
   - Purpose: [Why use this pattern]
   - Implementation: [How to implement]
   - Components: [Which components use it]

**Data Model:**
- Entities: [List main entities]
- Aggregates: [Domain aggregates]
- Value Objects: [Value objects]
- Relationships: [Key relationships]

**Technology Stack:**
- Language: {target_language}
- Framework: [Recommended framework]
- Database: [Database choice with reasoning]
- Caching: [Caching strategy]
- Message Queue: [If needed]

**Key Design Decisions:**
- Decision 1: [Decision and reasoning]
- Decision 2: [Decision and reasoning]

Provide specific, actionable architecture that can be directly implemented.
"""

        return prompt

    def _build_nfr_strategy_prompt(
        self,
        nfr_requirements: Dict[str, Any],
        component_name: str
    ) -> str:
        """Build NFR strategy prompt."""

        nfr_text = json.dumps(nfr_requirements, indent=2)

        prompt = f"""You are an expert in non-functional requirements and system performance.

Define specific strategies to meet the following NFRs for **{component_name}**:

**Requirements:**
{nfr_text}

**NFR Categories to Address:**
1. **Performance** (response time, throughput, latency)
2. **Scalability** (horizontal scaling, load handling)
3. **Security** (authentication, authorization, encryption)
4. **Availability** (uptime, fault tolerance, disaster recovery)
5. **Maintainability** (code quality, observability, debugging)
6. **Reliability** (error handling, data consistency)

**For Each Category, Provide:**

**Performance:**
- Target Metrics: [Specific numbers]
- Strategies: [List 3-5 concrete strategies]
- Implementation: [How to implement each]
- Expected Impact: [Quantify improvements]

**Scalability:**
- [Same format]

**Security:**
- [Same format]

(Continue for all relevant categories)

**Monitoring & Observability:**
- Key Metrics: [What to monitor]
- Tools: [Specific tools/services]
- Alerts: [What to alert on]

Provide specific, measurable strategies with implementation details.
"""

        return prompt

    def _build_patterns_prompt(
        self,
        component_spec: Dict[str, Any],
        architecture_style: str
    ) -> str:
        """Build design patterns selection prompt."""

        spec_text = json.dumps(component_spec, indent=2)

        prompt = f"""You are an expert in software design patterns.

Choose appropriate design patterns for a **{architecture_style}** architecture:

**Component Specification:**
{spec_text}

**Pattern Categories:**
1. **Creational Patterns** (Factory, Builder, Singleton, etc.)
2. **Structural Patterns** (Adapter, Facade, Proxy, etc.)
3. **Behavioral Patterns** (Strategy, Observer, Command, etc.)
4. **Enterprise Patterns** (Repository, Unit of Work, Service Layer, etc.)
5. **Distributed Patterns** (Circuit Breaker, Saga, CQRS, etc.)

**For Each Recommended Pattern:**

**Pattern Name:** [Name]
**Category:** [Creational/Structural/Behavioral/etc.]
**Problem It Solves:** [Specific problem in this component]
**Implementation:** [How to implement it]
**Components Using It:** [Which components]
**Alternatives Considered:** [Why this over alternatives]

Recommend 5-7 patterns that work well together. Focus on practical, proven patterns.
"""

        return prompt

    # ========================================================================
    # RESPONSE PARSERS
    # ========================================================================

    def _parse_architecture_response(self, response_text: str, component_name: str) -> Dict[str, Any]:
        """Parse LLM response for architecture design."""

        # Extract architecture style
        style = "microservice"  # Default
        style_match = re.search(r"Architecture Style:?\s*\*?\*?([^\n]+)", response_text, re.IGNORECASE)
        if style_match:
            style = style_match.group(1).strip().strip("*").lower()

        # Extract layers
        layers = self._extract_layers(response_text)

        # Extract design patterns
        patterns = self._extract_patterns(response_text)

        # Extract data model
        data_model = self._extract_data_model(response_text)

        # Extract technology stack
        tech_stack = self._extract_tech_stack(response_text)

        # Extract key decisions
        decisions = self._extract_decisions(response_text)

        return {
            "component_name": component_name,
            "architecture_style": style,
            "layers": layers if layers else self._default_layers(),
            "design_patterns": patterns if patterns else self._default_patterns(),
            "data_model": data_model if data_model else {},
            "technology_stack": tech_stack,
            "key_decisions": decisions
        }

    def _extract_layers(self, text: str) -> List[Dict[str, Any]]:
        """Extract architectural layers from response."""
        layers = []

        # Find Layers section
        layers_match = re.search(r"Layers:?\s*\n(.*?)(?=\n\n\*\*|$)", text, re.DOTALL | re.IGNORECASE)
        if layers_match:
            layers_text = layers_match.group(1)

            # Extract individual layers
            layer_pattern = r"\*\*([^\*]+)\*\*\s*\n\s*-\s*Responsibility:\s*([^\n]+)\n\s*-\s*Technologies:\s*([^\n]+)"
            for match in re.finditer(layer_pattern, layers_text):
                layers.append({
                    "name": match.group(1).strip(),
                    "responsibility": match.group(2).strip(),
                    "technologies": [t.strip() for t in match.group(3).split(",")]
                })

        return layers

    def _extract_patterns(self, text: str) -> List[Dict[str, Any]]:
        """Extract design patterns from response."""
        patterns = []

        patterns_match = re.search(r"Design Patterns:?\s*\n(.*?)(?=\n\n\*\*|$)", text, re.DOTALL | re.IGNORECASE)
        if patterns_match:
            patterns_text = patterns_match.group(1)

            pattern_pattern = r"\*\*([^\*]+)\*\*\s*\n\s*-\s*Purpose:\s*([^\n]+)"
            for match in re.finditer(pattern_pattern, patterns_text):
                patterns.append({
                    "pattern": match.group(1).strip(),
                    "purpose": match.group(2).strip()
                })

        return patterns

    def _extract_data_model(self, text: str) -> Dict[str, Any]:
        """Extract data model from response."""
        data_model = {}

        # Extract entities
        entities_match = re.search(r"Entities:\s*\[([^\]]+)\]", text, re.IGNORECASE)
        if entities_match:
            data_model["entities"] = [e.strip() for e in entities_match.group(1).split(",")]

        return data_model

    def _extract_tech_stack(self, text: str) -> Dict[str, Any]:
        """Extract technology stack from response."""
        tech_stack = {}

        # Extract framework
        framework_match = re.search(r"Framework:\s*([^\n]+)", text, re.IGNORECASE)
        if framework_match:
            tech_stack["framework"] = framework_match.group(1).strip()

        # Extract database
        db_match = re.search(r"Database:\s*([^\n]+)", text, re.IGNORECASE)
        if db_match:
            tech_stack["database"] = db_match.group(1).strip()

        return tech_stack

    def _extract_decisions(self, text: str) -> List[str]:
        """Extract key design decisions."""
        decisions = []

        decisions_match = re.search(r"Key Design Decisions:?\s*\n(.*?)(?=\n\n\*\*|$)", text, re.DOTALL | re.IGNORECASE)
        if decisions_match:
            decisions_text = decisions_match.group(1)
            for line in decisions_text.split("\n"):
                line = line.strip()
                if line.startswith("-") or line.startswith("*"):
                    decisions.append(line[1:].strip())

        return decisions[:10]

    def _parse_nfr_response(self, response_text: str) -> Dict[str, Any]:
        """Parse NFR strategy response."""

        nfr_strategies = {
            "performance": {"strategies": []},
            "scalability": {"strategies": []},
            "security": {"strategies": []},
            "availability": {"strategies": []},
            "maintainability": {"strategies": []}
        }

        # Extract performance strategies
        perf_match = re.search(r"Performance:?\s*\n(.*?)(?=\n\n\*\*|$)", response_text, re.DOTALL | re.IGNORECASE)
        if perf_match:
            strategies = self._extract_strategies(perf_match.group(1))
            nfr_strategies["performance"]["strategies"] = strategies

        # Extract scalability strategies
        scale_match = re.search(r"Scalability:?\s*\n(.*?)(?=\n\n\*\*|$)", response_text, re.DOTALL | re.IGNORECASE)
        if scale_match:
            strategies = self._extract_strategies(scale_match.group(1))
            nfr_strategies["scalability"]["strategies"] = strategies

        # Extract security strategies
        sec_match = re.search(r"Security:?\s*\n(.*?)(?=\n\n\*\*|$)", response_text, re.DOTALL | re.IGNORECASE)
        if sec_match:
            strategies = self._extract_strategies(sec_match.group(1))
            nfr_strategies["security"]["strategies"] = strategies

        return nfr_strategies

    def _extract_strategies(self, text: str) -> List[Dict[str, str]]:
        """Extract individual strategies from text."""
        strategies = []
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        for line in lines[:5]:  # Limit to 5 strategies
            if line.startswith("-") or line.startswith("*"):
                strategies.append({"description": line[1:].strip()})

        return strategies

    def _parse_patterns_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse design patterns response."""
        return self._extract_patterns(response_text)

    def _default_layers(self) -> List[Dict[str, Any]]:
        """Default architectural layers if parsing fails."""
        return [
            {
                "name": "API Layer",
                "responsibility": "HTTP endpoints and request handling",
                "technologies": ["FastAPI", "REST"]
            },
            {
                "name": "Business Logic Layer",
                "responsibility": "Domain logic and business rules",
                "technologies": ["Python"]
            },
            {
                "name": "Data Access Layer",
                "responsibility": "Database operations",
                "technologies": ["SQLAlchemy", "PostgreSQL"]
            }
        ]

    def _default_patterns(self) -> List[Dict[str, Any]]:
        """Default design patterns if parsing fails."""
        return [
            {"pattern": "Repository Pattern", "purpose": "Abstract data access"},
            {"pattern": "Service Layer", "purpose": "Encapsulate business logic"}
        ]

    def _get_generation_config(self, temperature: float = 0.4) -> Dict[str, Any]:
        """Get LLM generation configuration."""
        return {
            "temperature": temperature,
            "max_output_tokens": 8192,
            "top_p": 0.95,
            "top_k": 40
        }


# Factory function
def create_architect_agent(context: Dict[str, Any], message_bus, orchestrator_id: str):
    """Factory function to create architect agent."""
    return TechnicalArchitectAgent(
        context=context,
        message_bus=message_bus,
        orchestrator_id=orchestrator_id
    )

# Export for backward compatibility
architect_agent = None  # Will be instantiated when needed
