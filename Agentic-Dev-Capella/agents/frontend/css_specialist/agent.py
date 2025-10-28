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

    def optimize_css(
        self,
        css_code: str,
        optimization_goals: List[str] = None
    ) -> Dict[str, Any]:
        """
        Optimize CSS for performance.

        Args:
            css_code: Current CSS
            optimization_goals: file_size, render_performance, specificity

        Returns:
            Optimized CSS
        """
        optimization_goals = optimization_goals or ["file_size", "render_performance"]

        print(f"[CSS Specialist] Optimizing CSS: {optimization_goals}")

        prompt = f"""
Optimize this CSS:

```css
{css_code}
```

Goals: {', '.join(optimization_goals)}

Apply:
1. Remove unused styles
2. Reduce specificity
3. Consolidate rules
4. Use shorthand properties
5. Minimize repaints/reflows
6. Critical CSS separation
7. Remove redundancy

Provide optimized CSS with explanations.
"""

        response = self.model.generate_content(prompt)

        return {
            "optimized_css": response.text,
            "optimization_goals": optimization_goals
        }


# Tool function
def create_responsive_layout_tool(
    layout_spec: Dict[str, Any],
    approach: str = "css_grid"
) -> Dict[str, Any]:
    """Tool function: Create responsive layout."""
    agent = CSSSpecialistAgent(
        context={},
        message_bus=None,
        orchestrator_id=""
    )

    return agent.create_responsive_layout(
        layout_spec=layout_spec,
        approach=approach
    )
