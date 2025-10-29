"""
agents/frontend/css_specialist/agent.py

CSS/Styling Specialist Agent - Expert in modern CSS and styling solutions.

Specializes in:
- Modern CSS (Grid, Flexbox, Container Queries)
- CSS-in-JS solutions
- Tailwind CSS
- Responsive design
- Animations and transitions
- Design systems
- Performance optimization
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration
from shared.utils.kb_integration_mixin import DynamicKnowledgeBaseIntegration


class CSSSpecialistAgent(A2AEnabledAgent, DynamicKnowledgeBaseIntegration):
    """CSS/Styling Specialist Agent."""

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        vector_db_client=None,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize CSS Specialist Agent."""
        A2AEnabledAgent.__init__(self, context, message_bus)

        self.context = context
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

    @A2AIntegration.with_task_tracking
    def create_responsive_layout(
        self,
        layout_spec: Dict[str, Any],
        approach: str = "css_grid",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create responsive layout.

        Args:
            layout_spec: Layout specification
            approach: css_grid, flexbox, or hybrid
            task_id: Optional task ID

        Returns:
            CSS/styling implementation
        """
        print(f"[CSS Specialist] Creating {approach} responsive layout")

        prompt = f"""
Create a responsive layout using {approach}:

**Layout Spec:**
{layout_spec}

Requirements:
1. Mobile-first approach
2. Breakpoints: mobile (< 640px), tablet (640-1024px), desktop (> 1024px)
3. Modern CSS features (Grid, Flexbox, Container Queries)
4. No media query hacks
5. Performant (no layout shifts)
6. Accessibility-friendly

Provide:
1. CSS/SCSS code
2. HTML structure (semantic)
3. Tailwind classes (if applicable)
4. Usage examples

Use {approach} as primary layout method.
"""

        response = self.model.generate_content(prompt)

        return {
            "css_code": response.text,
            "approach": approach,
            "breakpoints": ["mobile", "tablet", "desktop"]
        }

    @A2AIntegration.with_task_tracking
    def create_design_system(
        self,
        design_tokens: Dict[str, Any],
        output_format: str = "css_custom_properties",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create design system from design tokens.

        Args:
            design_tokens: Colors, typography, spacing, etc.
            output_format: css_custom_properties, scss_variables, tailwind_config
            task_id: Optional task ID

        Returns:
            Design system implementation
        """
        print(f"[CSS Specialist] Creating design system ({output_format})")

        prompt = f"""
Create a design system from these tokens:

**Design Tokens:**
{design_tokens}

Output format: {output_format}

Include:
1. Color palette (primary, secondary, neutrals, semantic)
2. Typography scale
3. Spacing system
4. Border radius
5. Shadows
6. Z-index layers
7. Transitions/animations

For CSS Custom Properties:
- Organize in :root
- Use semantic naming
- Include dark mode support

For Tailwind:
- Complete tailwind.config.js
- Extended theme
- Custom utilities

Provide complete, production-ready design system.
"""

        response = self.model.generate_content(prompt)

        return {
            "design_system_code": response.text,
            "output_format": output_format,
            "tokens": design_tokens
        }

    @A2AIntegration.with_task_tracking
    def optimize_css(
        self,
        css_code: str,
        optimization_goals: List[str] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Optimize CSS for performance."""
        optimization_goals = optimization_goals or ["file_size", "render_performance"]
        print(f"[CSS Specialist] Optimizing CSS: {optimization_goals}")

        kb_results = []
        if self.has_kb_access():
            kb_results = self.query_kb(query="CSS performance optimization best practices", top_k=3)

        prompt = f"""Optimize this CSS:

```css
{css_code[:2000]}
```

Goals: {', '.join(optimization_goals)}

Apply: 1. Remove unused styles 2. Reduce specificity 3. Consolidate rules 4. Use shorthand 5. Minimize repaints 6. Critical CSS 7. Remove redundancy

{self._format_kb_results(kb_results) if kb_results else ""}

Provide optimized CSS."""

        response = self.model.generate_content(prompt)

        return {"status": "success", "optimized_css": response.text, "optimization_goals": optimization_goals, "timestamp": datetime.now().isoformat()}

    def handle_task_assignment(self, message: Dict[str, Any]) -> None:
        """Handle incoming task assignments."""
        task_type = message.get("task_type")
        task_data = message.get("task_data", {})
        task_id = message.get("task_id")

        if task_type == "create_responsive_layout":
            result = self.create_responsive_layout(layout_spec=task_data.get("layout_spec", {}), approach=task_data.get("approach", "css_grid"), task_id=task_id)
        elif task_type == "create_design_system":
            result = self.create_design_system(design_tokens=task_data.get("design_tokens", {}), output_format=task_data.get("output_format", "css_custom_properties"), task_id=task_id)
        elif task_type == "optimize_css":
            result = self.optimize_css(css_code=task_data.get("css_code", ""), optimization_goals=task_data.get("optimization_goals", ["performance"]), task_id=task_id)
        elif task_type == "create_animations":
            result = self.create_animations(animation_spec=task_data.get("animation_spec", {}), task_id=task_id)
        elif task_type == "implement_dark_mode":
            result = self.implement_dark_mode(theme_spec=task_data.get("theme_spec", {}), task_id=task_id)
        else:
            result = {"error": f"Unknown task type: {task_type}"}

        self.a2a.report_completion(orchestrator_id=self.orchestrator_id, task_id=task_id, result=result)

    @A2AIntegration.with_task_tracking
    def create_animations(self, animation_spec: Dict[str, Any], task_id: Optional[str] = None) -> Dict[str, Any]:
        """Create CSS animations and transitions."""
        print(f"[CSS Specialist] Creating animations: {animation_spec.get('type')}")

        kb_results = []
        if self.has_kb_access():
            kb_results = self.query_kb(query="CSS animations performance 60fps", top_k=3)

        prompt = f"""Create CSS animations:

**Type:** {animation_spec.get('type', 'fade')}
**Duration:** {animation_spec.get('duration', '300ms')}
**Easing:** {animation_spec.get('easing', 'ease-in-out')}

**Requirements:**
{self._format_dict(animation_spec)}

Create: 1. @keyframes definitions 2. Animation utilities 3. Transition helpers 4. Transform animations 5. 60fps animations (transform/opacity only) 6. Reduced motion support

{self._format_kb_results(kb_results) if kb_results else ""}"""

        response = self.model.generate_content(prompt)
        return {"status": "success", "animation_code": self._extract_code(response.text), "timestamp": datetime.now().isoformat()}

    @A2AIntegration.with_task_tracking
    def implement_dark_mode(self, theme_spec: Dict[str, Any], task_id: Optional[str] = None) -> Dict[str, Any]:
        """Implement dark mode theming."""
        print("[CSS Specialist] Implementing dark mode")

        kb_results = []
        if self.has_kb_access():
            kb_results = self.query_kb(query="dark mode CSS implementation best practices", top_k=3)

        prompt = f"""Implement dark mode theming:

**Theme Spec:**
{self._format_dict(theme_spec)}

Implement: 1. Light/dark color schemes 2. CSS custom properties 3. prefers-color-scheme media query 4. Manual toggle support 5. Smooth transitions 6. Contrast ratios (WCAG AA) 7. Storage persistence

{self._format_kb_results(kb_results) if kb_results else ""}

Provide complete dark mode implementation."""

        response = self.model.generate_content(prompt)
        return {"status": "success", "dark_mode_code": self._extract_code(response.text), "timestamp": datetime.now().isoformat()}

    def _extract_code(self, response: str) -> str:
        """Extract code from LLM response."""
        import re
        code = response
        if "```" in code:
            parts = code.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 1:
                    lines = part.split("\n")
                    if lines and lines[0].strip() in ["css", "scss", "sass", "javascript", "js", "typescript", "ts"]:
                        lines = lines[1:]
                    code = "\n".join(lines)
                    break
        return code.strip()

    def _format_dict(self, data: Dict[str, Any]) -> str:
        """Format dictionary for prompt."""
        if not data:
            return "- None"
        return "\n".join(f"- {k}: {v}" for k, v in data.items())

    def _format_kb_results(self, results: List[Dict[str, Any]]) -> str:
        """Format KB results for prompt."""
        if not results:
            return ""
        formatted = ["KB Patterns:"]
        for i, result in enumerate(results, 1):
            formatted.append(f"{i}. {result.get('content', '')[:150]}...")
        return "\n".join(formatted)


# Tool functions
def create_responsive_layout_tool(layout_spec: Dict[str, Any], approach: str = "css_grid") -> Dict[str, Any]:
    """Tool function: Create responsive layout."""
    class MockMessageBus:
        def publish(self, *args, **kwargs):
            pass

    agent = CSSSpecialistAgent(context={"project_id": "test", "location": "us-central1"}, message_bus=MockMessageBus(), orchestrator_id="orchestrator")
    return agent.create_responsive_layout(layout_spec=layout_spec, approach=approach)


def create_css_specialist_agent(project_id: str, location: str, orchestrator_id: str = None) -> CSSSpecialistAgent:
    """Factory function to create CSS Specialist Agent."""
    context = {"project_id": project_id, "location": location}

    class MockMessageBus:
        def publish(self, *args, **kwargs):
            pass

    return CSSSpecialistAgent(context=context, message_bus=MockMessageBus(), orchestrator_id=orchestrator_id or "orchestrator")
