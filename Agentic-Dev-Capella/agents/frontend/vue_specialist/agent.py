"""
agents/frontend/vue_specialist/agent.py

Vue Specialist Agent - Expert in Vue.js ecosystem and Nuxt.js.

Specializes in:
- Vue 3 Composition API
- Nuxt 3 applications
- Pinia state management
- Vue Router
- Component architecture
- Performance optimization
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration
from shared.utils.kb_integration_mixin import DynamicKnowledgeBaseIntegration


class VueSpecialistAgent(A2AEnabledAgent, DynamicKnowledgeBaseIntegration):
    """
    Vue Specialist Agent for Vue 3 and Nuxt 3 development.
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        vector_db_client=None,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize Vue Specialist Agent."""
        A2AEnabledAgent.__init__(self, context, message_bus)

        self.context = context
        self.orchestrator_id = orchestrator_id
        self.model_name = model_name

        self.a2a = A2AIntegration(
            context=context,
            message_bus=message_bus,
            orchestrator_id=orchestrator_id
        )

        if vector_db_client:
            self.initialize_kb_integration(
                vector_db_client=vector_db_client,
                kb_query_strategy="adaptive"
            )

        aiplatform.init(
            project=context.get("project_id"),
            location=context.get("location", "us-central1")
        )

        self.model = GenerativeModel(model_name)

    def handle_task_assignment(self, message: Dict[str, Any]) -> None:
        """Handle incoming task assignments."""
        task_type = message.get("task_type")
        task_data = message.get("task_data", {})
        task_id = message.get("task_id")

        if task_type == "implement_vue_component":
            result = self.implement_vue_component(
                component_spec=task_data.get("component_spec"),
                task_id=task_id
            )
        elif task_type == "create_nuxt_page":
            result = self.create_nuxt_page(
                page_spec=task_data.get("page_spec"),
                task_id=task_id
            )
        elif task_type == "implement_composable":
            result = self.implement_composable(
                composable_spec=task_data.get("composable_spec"),
                task_id=task_id
            )
        elif task_type == "setup_pinia_store":
            result = self.setup_pinia_store(
                store_spec=task_data.get("store_spec"),
                task_id=task_id
            )
        else:
            result = {"error": f"Unknown task type: {task_type}"}

        # Send completion message
        self.a2a.report_completion(
            orchestrator_id=self.orchestrator_id,
            task_id=task_id,
            result=result
        )

    @A2AIntegration.with_task_tracking
    def implement_vue_component(
        self,
        component_spec: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Implement Vue 3 component with Composition API.

        Args:
            component_spec: Component specification with props, emits, slots
            task_id: Optional task ID

        Returns:
            Vue component code with TypeScript
        """
        print(f"[Vue Specialist] Implementing component: {component_spec.get('name')}")

        # Query KB for similar components
        kb_results = []
        if self.has_kb_access():
            kb_results = self.query_kb(
                query=f"Vue 3 component {component_spec.get('name')} {component_spec.get('type', '')}",
                top_k=3
            )

        # Build prompt
        prompt = self._build_component_prompt(component_spec, kb_results)

        # Generate with LLM
        response = self.model.generate_content(prompt)
        component_code = response.text

        # Parse and structure
        result = self._parse_component_code(component_code, component_spec)

        return {
            "status": "success",
            "component": result,
            "timestamp": datetime.now().isoformat()
        }

    @A2AIntegration.with_task_tracking
    def create_nuxt_page(
        self,
        page_spec: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create Nuxt 3 page with server routes and SEO.

        Args:
            page_spec: Page specification
            task_id: Optional task ID

        Returns:
            Nuxt page with layouts and middleware
        """
        print(f"[Vue Specialist] Creating Nuxt page: {page_spec.get('route')}")

        # Query KB for page patterns
        kb_results = []
        if self.has_kb_access():
            kb_results = self.query_kb(
                query=f"Nuxt 3 page {page_spec.get('route')} {page_spec.get('type', 'standard')}",
                top_k=3
            )

        prompt = f"""Create a Nuxt 3 page with the following specification:

Route: {page_spec.get('route')}
Type: {page_spec.get('type', 'standard')}
Data Fetching: {page_spec.get('data_fetching', 'useAsyncData')}
Layout: {page_spec.get('layout', 'default')}
Meta/SEO: {page_spec.get('meta', {{}})}

Features needed:
{self._format_list(page_spec.get('features', []))}

{"Knowledge Base patterns:\n" + self._format_kb_results(kb_results) if kb_results else ""}

Generate:
1. Page component (pages/{page_spec.get('route')}.vue)
2. Server route if needed (server/api/...)
3. Composables for data fetching
4. TypeScript interfaces

Use Vue 3 Composition API with <script setup>.
Include proper TypeScript types.
Add SEO meta tags using useHead().
"""

        response = self.model.generate_content(prompt)
        page_code = response.text

        result = self._parse_nuxt_page(page_code, page_spec)

        return {
            "status": "success",
            "page": result,
            "timestamp": datetime.now().isoformat()
        }

    @A2AIntegration.with_task_tracking
    def implement_composable(
        self,
        composable_spec: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Implement Vue composable (reusable composition function).

        Args:
            composable_spec: Composable specification
            task_id: Optional task ID

        Returns:
            Composable implementation
        """
        print(f"[Vue Specialist] Creating composable: {composable_spec.get('name')}")

        prompt = f"""Create a Vue 3 composable with the following specification:

Name: {composable_spec.get('name')}
Purpose: {composable_spec.get('purpose')}
Returns: {composable_spec.get('returns', [])}

Features:
{self._format_list(composable_spec.get('features', []))}

Requirements:
- Use TypeScript with proper types
- Follow Vue 3 composition patterns
- Include reactivity (ref, computed, watch as needed)
- Handle cleanup in onUnmounted if needed
- Export named function

Example usage:
{composable_spec.get('example_usage', '')}
"""

        response = self.model.generate_content(prompt)
        composable_code = response.text

        return {
            "status": "success",
            "composable": {
                "name": composable_spec.get('name'),
                "code": self._extract_code(composable_code),
                "file_path": f"composables/{composable_spec.get('name')}.ts"
            },
            "timestamp": datetime.now().isoformat()
        }

    @A2AIntegration.with_task_tracking
    def setup_pinia_store(
        self,
        store_spec: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Setup Pinia store for state management.

        Args:
            store_spec: Store specification
            task_id: Optional task ID

        Returns:
            Pinia store implementation
        """
        print(f"[Vue Specialist] Setting up Pinia store: {store_spec.get('name')}")

        prompt = f"""Create a Pinia store with the following specification:

Store Name: {store_spec.get('name')}
Purpose: {store_spec.get('purpose')}

State:
{self._format_dict(store_spec.get('state', {}))}

Getters:
{self._format_list(store_spec.get('getters', []))}

Actions:
{self._format_list(store_spec.get('actions', []))}

Requirements:
- Use Pinia setup store pattern (recommended)
- TypeScript with proper types
- Include async actions for API calls if needed
- Use computed for getters
- Export store with defineStore

Example:
```typescript
export const use{store_spec.get('name').title()}Store = defineStore('{store_spec.get('name')}', () => {{
  // State
  const items = ref<Item[]>([])

  // Getters
  const itemCount = computed(() => items.value.length)

  // Actions
  async function fetchItems() {{
    // Implementation
  }}

  return {{ items, itemCount, fetchItems }}
}})
```
"""

        response = self.model.generate_content(prompt)
        store_code = response.text

        return {
            "status": "success",
            "store": {
                "name": store_spec.get('name'),
                "code": self._extract_code(store_code),
                "file_path": f"stores/{store_spec.get('name')}.ts"
            },
            "timestamp": datetime.now().isoformat()
        }

    def _build_component_prompt(
        self,
        component_spec: Dict[str, Any],
        kb_results: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for component generation."""
        prompt = f"""Create a Vue 3 component with Composition API:

Component Name: {component_spec.get('name')}
Type: {component_spec.get('type', 'standard')}
Description: {component_spec.get('description', '')}

Props:
{self._format_dict(component_spec.get('props', {}))}

Emits:
{self._format_list(component_spec.get('emits', []))}

Slots:
{self._format_list(component_spec.get('slots', []))}

Features needed:
{self._format_list(component_spec.get('features', []))}

{"Similar patterns from knowledge base:\n" + self._format_kb_results(kb_results) if kb_results else ""}

Requirements:
- Use <script setup lang="ts">
- Define props with defineProps<Props>()
- Define emits with defineEmits<Emits>()
- Use Composition API patterns
- Include proper TypeScript interfaces
- Add template with proper v-bind and v-on
- Include scoped styles if needed

Generate complete component code.
"""
        return prompt

    def _parse_component_code(
        self,
        code: str,
        spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse generated component code."""
        return {
            "name": spec.get('name'),
            "code": self._extract_code(code),
            "file_path": f"components/{spec.get('name')}.vue",
            "type": spec.get('type', 'standard')
        }

    def _parse_nuxt_page(
        self,
        code: str,
        spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse generated Nuxt page."""
        return {
            "route": spec.get('route'),
            "code": self._extract_code(code),
            "file_path": f"pages/{spec.get('route')}.vue",
            "layout": spec.get('layout', 'default')
        }

    def _extract_code(self, response: str) -> str:
        """Extract code from LLM response."""
        # Remove markdown code blocks
        code = response
        if "```" in code:
            parts = code.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 1:  # Odd indices are code blocks
                    # Remove language identifier
                    lines = part.split("\n")
                    if lines and (lines[0].strip() in ["vue", "typescript", "ts", "javascript", "js"]):
                        lines = lines[1:]
                    code = "\n".join(lines)
                    break
        return code.strip()

    def _format_list(self, items: List[str]) -> str:
        """Format list for prompt."""
        return "\n".join(f"- {item}" for item in items) if items else "- None"

    def _format_dict(self, data: Dict[str, Any]) -> str:
        """Format dictionary for prompt."""
        return "\n".join(f"- {k}: {v}" for k, v in data.items()) if data else "- None"

    def _format_kb_results(self, results: List[Dict[str, Any]]) -> str:
        """Format KB results for prompt."""
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(f"{i}. {result.get('content', '')[:200]}...")
        return "\n".join(formatted)


# Standalone tool functions for testing
def implement_vue_component_standalone(
    component_spec: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """Standalone function for component implementation."""
    # Mock implementation for testing
    return {
        "status": "success",
        "component": {
            "name": component_spec.get('name'),
            "code": f"<template>\n  <div class='{component_spec.get('name').lower()}'></div>\n</template>",
            "file_path": f"components/{component_spec.get('name')}.vue"
        }
    }


def create_nuxt_page_standalone(
    page_spec: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """Standalone function for Nuxt page creation."""
    return {
        "status": "success",
        "page": {
            "route": page_spec.get('route'),
            "code": "<template>\n  <div>Page</div>\n</template>",
            "file_path": f"pages/{page_spec.get('route')}.vue"
        }
    }


def create_vue_specialist_agent(
    project_id: str,
    location: str,
    orchestrator_id: str = None
) -> VueSpecialistAgent:
    """Factory function to create Vue Specialist Agent."""
    context = {
        "project_id": project_id,
        "location": location
    }

    # Mock message bus for local testing
    class MockMessageBus:
        def publish(self, *args, **kwargs):
            pass

    return VueSpecialistAgent(
        context=context,
        message_bus=MockMessageBus(),
        orchestrator_id=orchestrator_id or "orchestrator"
    )
