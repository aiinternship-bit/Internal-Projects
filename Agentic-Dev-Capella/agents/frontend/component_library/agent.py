"""
agents/frontend/component_library/agent.py

Component Library Agent - Creates and maintains reusable component libraries.

Specializes in:
- Design system components
- Component library architecture
- Storybook documentation
- Component variants and theming
- Accessibility standards
- Cross-framework components
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration
from shared.utils.kb_integration_mixin import DynamicKnowledgeBaseIntegration


class ComponentLibraryAgent(A2AEnabledAgent, DynamicKnowledgeBaseIntegration):
    """
    Component Library Agent for creating design system component libraries.
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        vector_db_client=None,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize Component Library Agent."""
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

        if task_type == "create_component_library":
            result = self.create_component_library(
                library_spec=task_data.get("library_spec"),
                task_id=task_id
            )
        elif task_type == "generate_component":
            result = self.generate_component(
                component_spec=task_data.get("component_spec"),
                task_id=task_id
            )
        elif task_type == "create_storybook_stories":
            result = self.create_storybook_stories(
                component_name=task_data.get("component_name"),
                variants=task_data.get("variants", []),
                task_id=task_id
            )
        elif task_type == "generate_design_tokens":
            result = self.generate_design_tokens(
                design_system=task_data.get("design_system"),
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
    def create_component_library(
        self,
        library_spec: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create complete component library with structure and build setup.

        Args:
            library_spec: Library specification
            task_id: Optional task ID

        Returns:
            Component library structure and setup files
        """
        print(f"[Component Library] Creating library: {library_spec.get('name')}")

        # Query KB for library patterns
        kb_results = []
        if self.has_kb_access():
            kb_results = self.query_kb(
                query=f"component library structure {library_spec.get('framework', 'react')}",
                top_k=3
            )

        prompt = f"""Create a component library with the following specification:

Library Name: {library_spec.get('name')}
Framework: {library_spec.get('framework', 'react')}
Build Tool: {library_spec.get('build_tool', 'vite')}
Package Manager: {library_spec.get('package_manager', 'npm')}

Features:
{self._format_list(library_spec.get('features', []))}

Components to include:
{self._format_list(library_spec.get('components', ['Button', 'Input', 'Card', 'Modal']))}

Requirements:
- TypeScript support
- Tree-shaking for optimal bundle size
- CSS-in-JS or CSS modules
- Storybook for documentation
- Unit tests with Vitest/Jest
- Build for ESM and CJS
- Accessibility (WCAG AA)
- Dark mode support

Generate:
1. package.json with dependencies and scripts
2. tsconfig.json for TypeScript
3. vite.config.ts for build
4. .storybook/main.ts for Storybook
5. README.md with usage instructions
6. Project structure

{"Similar libraries:\n" + self._format_kb_results(kb_results) if kb_results else ""}
"""

        response = self.model.generate_content(prompt)
        library_structure = response.text

        result = self._parse_library_structure(library_structure, library_spec)

        return {
            "status": "success",
            "library": result,
            "timestamp": datetime.now().isoformat()
        }

    @A2AIntegration.with_task_tracking
    def generate_component(
        self,
        component_spec: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate reusable component with variants.

        Args:
            component_spec: Component specification
            task_id: Optional task ID

        Returns:
            Component with variants and documentation
        """
        print(f"[Component Library] Generating component: {component_spec.get('name')}")

        # Query KB for similar components
        kb_results = []
        if self.has_kb_access():
            kb_results = self.query_kb(
                query=f"{component_spec.get('name')} component pattern",
                top_k=3
            )

        prompt = f"""Create a reusable library component:

Component: {component_spec.get('name')}
Type: {component_spec.get('type', 'presentational')}
Description: {component_spec.get('description', '')}

Props:
{self._format_dict(component_spec.get('props', {}))}

Variants:
{self._format_list(component_spec.get('variants', []))}

States:
{self._format_list(component_spec.get('states', ['default', 'hover', 'active', 'disabled']))}

Requirements:
- TypeScript with strict types
- Compound component pattern if complex
- Accessible (ARIA attributes, keyboard navigation)
- Customizable via props and CSS variables
- Support for as prop (polymorphic)
- Forward refs
- Export named component and types

Example structure:
```typescript
export interface {component_spec.get('name')}Props {{
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  // ... other props
}}

export const {component_spec.get('name')} = forwardRef<HTMLElement, {component_spec.get('name')}Props>(
  ({{ variant = 'primary', size = 'md', ...props }}, ref) => {{
    // Implementation
  }}
);

{component_spec.get('name')}.displayName = '{component_spec.get('name')}';
```

{"Similar patterns:\n" + self._format_kb_results(kb_results) if kb_results else ""}
"""

        response = self.model.generate_content(prompt)
        component_code = response.text

        result = self._parse_component(component_code, component_spec)

        return {
            "status": "success",
            "component": result,
            "timestamp": datetime.now().isoformat()
        }

    @A2AIntegration.with_task_tracking
    def create_storybook_stories(
        self,
        component_name: str,
        variants: List[Dict[str, Any]],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create Storybook stories for component.

        Args:
            component_name: Component name
            variants: Component variants to document
            task_id: Optional task ID

        Returns:
            Storybook story file
        """
        print(f"[Component Library] Creating stories for: {component_name}")

        prompt = f"""Create Storybook 7 stories for component:

Component: {component_name}

Variants to document:
{self._format_list([v.get('name', '') for v in variants])}

Create stories with:
1. Meta configuration with args table
2. Default story
3. Story for each variant
4. Interactive controls
5. Accessibility checks
6. Dark mode toggle

Use CSF3 format (Component Story Format 3):
```typescript
import type {{ Meta, StoryObj }} from '@storybook/react';
import {{ {component_name} }} from './{component_name}';

const meta: Meta<typeof {component_name}> = {{
  title: 'Components/{component_name}',
  component: {component_name},
  tags: ['autodocs'],
  argTypes: {{
    // Control definitions
  }},
}};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {{
  args: {{
    // Default props
  }},
}};

// Add stories for each variant
```
"""

        response = self.model.generate_content(prompt)
        stories_code = response.text

        return {
            "status": "success",
            "stories": {
                "component": component_name,
                "code": self._extract_code(stories_code),
                "file_path": f"src/components/{component_name}/{component_name}.stories.tsx"
            },
            "timestamp": datetime.now().isoformat()
        }

    @A2AIntegration.with_task_tracking
    def generate_design_tokens(
        self,
        design_system: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate design tokens from design system spec.

        Args:
            design_system: Design system specification
            task_id: Optional task ID

        Returns:
            Design tokens in multiple formats
        """
        print("[Component Library] Generating design tokens")

        prompt = f"""Generate design tokens from this design system specification:

Colors:
{self._format_dict(design_system.get('colors', {}))}

Typography:
{self._format_dict(design_system.get('typography', {}))}

Spacing:
{self._format_dict(design_system.get('spacing', {}))}

Breakpoints:
{self._format_dict(design_system.get('breakpoints', {}))}

Shadows:
{self._format_dict(design_system.get('shadows', {}))}

Generate:
1. CSS variables (tokens.css)
2. TypeScript theme object (theme.ts)
3. Tailwind config (tailwind.config.ts)
4. Style Dictionary format (tokens.json)

Example CSS variables:
```css
:root {{
  /* Colors */
  --color-primary-50: #...;
  --color-primary-500: #...;

  /* Spacing */
  --spacing-1: 0.25rem;
  --spacing-4: 1rem;

  /* Typography */
  --font-sans: 'Inter', sans-serif;
  --text-sm: 0.875rem;
}}
```
"""

        response = self.model.generate_content(prompt)
        tokens = response.text

        result = self._parse_design_tokens(tokens, design_system)

        return {
            "status": "success",
            "tokens": result,
            "timestamp": datetime.now().isoformat()
        }

    def _parse_library_structure(
        self,
        structure: str,
        spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse library structure."""
        return {
            "name": spec.get('name'),
            "framework": spec.get('framework', 'react'),
            "structure": self._extract_code(structure),
            "setup_complete": True
        }

    def _parse_component(
        self,
        code: str,
        spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse generated component."""
        return {
            "name": spec.get('name'),
            "code": self._extract_code(code),
            "file_path": f"src/components/{spec.get('name')}/{spec.get('name')}.tsx",
            "variants": spec.get('variants', [])
        }

    def _parse_design_tokens(
        self,
        tokens: str,
        spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse design tokens."""
        return {
            "tokens": self._extract_code(tokens),
            "formats": ["css", "typescript", "tailwind", "json"],
            "source": spec
        }

    def _extract_code(self, response: str) -> str:
        """Extract code from LLM response."""
        code = response
        if "```" in code:
            parts = code.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 1:
                    lines = part.split("\n")
                    if lines and lines[0].strip() in [
                        "typescript", "ts", "javascript", "js", "tsx", "jsx",
                        "css", "json", "bash", "shell"
                    ]:
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
def create_component_library_standalone(
    library_spec: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """Standalone function for library creation."""
    return {
        "status": "success",
        "library": {
            "name": library_spec.get('name'),
            "structure": "Component library structure generated",
            "setup_complete": True
        }
    }


def generate_component_standalone(
    component_spec: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """Standalone function for component generation."""
    return {
        "status": "success",
        "component": {
            "name": component_spec.get('name'),
            "code": f"// {component_spec.get('name')} component",
            "file_path": f"src/components/{component_spec.get('name')}.tsx"
        }
    }


def create_component_library_agent(
    project_id: str,
    location: str,
    orchestrator_id: str = None
) -> ComponentLibraryAgent:
    """Factory function to create Component Library Agent."""
    context = {
        "project_id": project_id,
        "location": location
    }

    class MockMessageBus:
        def publish(self, *args, **kwargs):
            pass

    return ComponentLibraryAgent(
        context=context,
        message_bus=MockMessageBus(),
        orchestrator_id=orchestrator_id or "orchestrator"
    )
