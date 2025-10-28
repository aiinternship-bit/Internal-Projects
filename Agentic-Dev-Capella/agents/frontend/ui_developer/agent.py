"""
agents/frontend/ui_developer/agent.py

UI Developer Agent - General frontend development agent.

Implements UI components, layouts, and interactions based on design specifications.
Supports multiple frameworks and styling approaches.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration
from shared.utils.kb_integration_mixin import DynamicKnowledgeBaseIntegration


class UIDevAgent(A2AEnabledAgent, DynamicKnowledgeBaseIntegration):
    """
    UI Developer Agent for general frontend development.

    Capabilities:
    - Implement UI components from designs
    - Create responsive layouts
    - Add interactivity and state management
    - Integrate with backend APIs
    - Follow accessibility best practices
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        vector_db_client=None,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize UI Developer Agent."""
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

        # Initialize KB integration if vector_db_client provided
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

        try:
            result = self.implement_ui_component(
                component_spec=payload.get("component_spec"),
                framework=payload.get("framework", "react"),
                styling_approach=payload.get("styling_approach", "css_modules"),
                task_id=task_id
            )

            self.a2a.send_completion(
                task_id=task_id,
                artifacts=result,
                metrics={
                    "implementation_duration_minutes": result.get("duration_minutes", 0),
                    "lines_of_code": result.get("lines_of_code", 0)
                }
            )

        except Exception as e:
            self.a2a.send_error_report(
                task_id=task_id,
                error_type="UI_IMPLEMENTATION_FAILED",
                error_message=str(e),
                stack_trace=""
            )

    @A2AIntegration.with_task_tracking
    def implement_ui_component(
        self,
        component_spec: Dict[str, Any],
        framework: str = "react",
        styling_approach: str = "css_modules",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Implement a UI component based on specifications.

        Args:
            component_spec: Component specification
                {
                    "name": str,
                    "type": str,  # button, form, card, modal, etc.
                    "props": Dict,
                    "state": Dict,
                    "interactions": List,
                    "styling": Dict,
                    "accessibility": Dict
                }
            framework: Frontend framework (react, vue, angular, vanilla)
            styling_approach: css_modules, tailwind, styled_components, css
            task_id: Optional task ID

        Returns:
            {
                "component_code": str,
                "styles": str,
                "tests": str,
                "documentation": str,
                "lines_of_code": int
            }
        """
        start_time = datetime.utcnow()

        print(f"[UI Developer] Implementing {component_spec.get('name')} component")

        # Query KB for similar implementations (if enabled)
        kb_context = ""
        if hasattr(self, 'should_query_kb') and self.should_query_kb(component_spec):
            kb_results = self.execute_dynamic_query(
                query_type="similar_implementations",
                context={
                    "component_type": component_spec.get("type"),
                    "framework": framework
                },
                task_id=task_id
            )
            if kb_results:
                kb_context = f"\n\nSimilar implementations from KB:\n{kb_results}"

        # Generate implementation prompt
        prompt = self._build_implementation_prompt(
            component_spec=component_spec,
            framework=framework,
            styling_approach=styling_approach,
            kb_context=kb_context
        )

        # Generate code with LLM
        response = self.model.generate_content(prompt)
        implementation = response.text

        # Parse implementation
        result = self._parse_implementation(implementation, framework, styling_approach)

        # Add metadata
        duration = (datetime.utcnow() - start_time).total_seconds() / 60
        result.update({
            "component_name": component_spec.get("name"),
            "framework": framework,
            "styling_approach": styling_approach,
            "duration_minutes": duration,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Store in history
        self.dev_history.append({
            "task_id": task_id,
            "component_name": result["component_name"],
            "framework": framework,
            "timestamp": result["timestamp"]
        })

        return result

    def _build_implementation_prompt(
        self,
        component_spec: Dict[str, Any],
        framework: str,
        styling_approach: str,
        kb_context: str = ""
    ) -> str:
        """Build implementation prompt for LLM."""

        component_name = component_spec.get("name", "Component")
        component_type = component_spec.get("type", "general")
        props = component_spec.get("props", {})
        state = component_spec.get("state", {})
        interactions = component_spec.get("interactions", [])
        styling = component_spec.get("styling", {})
        accessibility = component_spec.get("accessibility", {})

        framework_templates = {
            "react": """
Implement a React component with the following specifications:

**Component Name:** {name}
**Component Type:** {type}
**Props:** {props}
**State:** {state}
**Interactions:** {interactions}
**Styling:** {styling}
**Accessibility:** {accessibility}

Requirements:
1. Use functional components with hooks
2. Implement proper TypeScript types
3. Use {styling_approach} for styling
4. Follow React best practices
5. Add prop validation
6. Implement accessibility features (ARIA labels, keyboard navigation)
7. Add error handling
8. Write JSDoc comments

Provide:
1. Component code (TypeScript)
2. Styles ({styling_approach})
3. Unit tests (Jest + React Testing Library)
4. Usage documentation

{kb_context}

Return as structured sections with clear markers.
""",
            "vue": """
Implement a Vue 3 component with Composition API:

**Component Name:** {name}
**Component Type:** {type}
**Props:** {props}
**State:** {state}
**Interactions:** {interactions}
**Styling:** {styling}
**Accessibility:** {accessibility}

Requirements:
1. Use Composition API with <script setup>
2. TypeScript with proper types
3. {styling_approach} for styling
4. Vue 3 best practices
5. Reactive state management
6. Accessibility features
7. Error handling

Provide:
1. Vue component (SFC)
2. Styles (scoped)
3. Unit tests (Vitest)
4. Documentation

{kb_context}
""",
            "vanilla": """
Implement a vanilla JavaScript component (Web Components):

**Component Name:** {name}
**Component Type:** {type}
**Attributes:** {props}
**Internal State:** {state}
**Events:** {interactions}
**Styling:** {styling}
**Accessibility:** {accessibility}

Requirements:
1. Use Custom Elements API
2. Shadow DOM for encapsulation
3. Modern ES6+ JavaScript
4. CSS for styling
5. Accessibility built-in
6. Browser compatibility

Provide:
1. Web Component class
2. CSS styles
3. Usage examples
4. Documentation

{kb_context}
"""
        }

        template = framework_templates.get(framework, framework_templates["react"])

        return template.format(
            name=component_name,
            type=component_type,
            props=props,
            state=state,
            interactions=interactions,
            styling=styling,
            accessibility=accessibility,
            styling_approach=styling_approach,
            kb_context=kb_context
        )

    def _parse_implementation(
        self,
        implementation: str,
        framework: str,
        styling_approach: str
    ) -> Dict[str, Any]:
        """Parse LLM implementation into structured format."""
        import re

        result = {
            "component_code": "",
            "styles": "",
            "tests": "",
            "documentation": "",
            "lines_of_code": 0
        }

        # Extract code blocks
        code_blocks = re.findall(r'```(\w+)?\n(.*?)```', implementation, re.DOTALL)

        for lang, code in code_blocks:
            lang = lang.lower() if lang else ""

            if any(x in lang for x in ["typescript", "tsx", "jsx", "javascript", "vue"]):
                if "test" in code.lower() or "describe" in code:
                    result["tests"] = code.strip()
                else:
                    result["component_code"] = code.strip()

            elif any(x in lang for x in ["css", "scss", "less"]):
                result["styles"] = code.strip()

            elif lang == "markdown" or lang == "":
                if not result["documentation"]:
                    result["documentation"] = code.strip()

        # If no structured extraction, use raw
        if not result["component_code"]:
            result["component_code"] = implementation

        # Count lines of code
        result["lines_of_code"] = (
            len(result["component_code"].split("\n")) +
            len(result["styles"].split("\n")) +
            len(result["tests"].split("\n"))
        )

        return result

    def implement_page_layout(
        self,
        layout_spec: Dict[str, Any],
        framework: str = "react"
    ) -> Dict[str, Any]:
        """
        Implement a complete page layout.

        Args:
            layout_spec: Layout specification with sections, components
            framework: Frontend framework

        Returns:
            Page implementation with routing
        """
        print(f"[UI Developer] Implementing page layout: {layout_spec.get('name')}")

        prompt = f"""
Implement a page layout in {framework}:

**Layout Specification:**
{layout_spec}

Include:
1. Page component with all sections
2. Routing configuration
3. Layout components (Header, Footer, Sidebar, etc.)
4. Responsive design
5. Loading states
6. Error boundaries

Return complete implementation with all necessary files.
"""

        response = self.model.generate_content(prompt)

        return {
            "page_code": response.text,
            "layout_name": layout_spec.get("name"),
            "framework": framework
        }

    def add_state_management(
        self,
        component_code: str,
        state_requirements: Dict[str, Any],
        framework: str = "react",
        state_library: str = "redux"
    ) -> Dict[str, Any]:
        """
        Add state management to existing component.

        Args:
            component_code: Existing component code
            state_requirements: State structure and actions
            framework: Frontend framework
            state_library: redux, zustand, pinia, vuex, etc.

        Returns:
            Updated component with state management
        """
        print(f"[UI Developer] Adding {state_library} state management")

        prompt = f"""
Add {state_library} state management to this {framework} component:

**Current Component:**
```
{component_code}
```

**State Requirements:**
{state_requirements}

Provide:
1. Updated component with state hooks/connectors
2. State slice/store/module definition
3. Action creators
4. Selectors (if applicable)
5. Usage examples

Follow {state_library} best practices.
"""

        response = self.model.generate_content(prompt)

        return {
            "updated_component": response.text,
            "state_library": state_library
        }

    def get_dev_stats(self) -> Dict[str, Any]:
        """Get UI developer statistics."""
        if not self.dev_history:
            return {"total_components": 0}

        frameworks = {}
        for record in self.dev_history:
            framework = record.get("framework", "unknown")
            frameworks[framework] = frameworks.get(framework, 0) + 1

        return {
            "total_components": len(self.dev_history),
            "frameworks_used": frameworks,
            "model_used": self.model_name
        }


# Tool functions
def implement_ui_component_tool(
    component_spec: Dict[str, Any],
    framework: str = "react",
    styling_approach: str = "css_modules"
) -> Dict[str, Any]:
    """
    Tool function: Implement a UI component.
    """
    agent = UIDevAgent(
        context={},
        message_bus=None,
        orchestrator_id=""
    )

    return agent.implement_ui_component(
        component_spec=component_spec,
        framework=framework,
        styling_approach=styling_approach
    )


def implement_page_layout_tool(
    layout_spec: Dict[str, Any],
    framework: str = "react"
) -> Dict[str, Any]:
    """
    Tool function: Implement a page layout.
    """
    agent = UIDevAgent(
        context={},
        message_bus=None,
        orchestrator_id=""
    )

    return agent.implement_page_layout(
        layout_spec=layout_spec,
        framework=framework
    )
