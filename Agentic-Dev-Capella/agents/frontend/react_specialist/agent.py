"""
agents/frontend/react_specialist/agent.py

React Specialist Agent - Expert in React ecosystem and best practices.

Specializes in:
- Advanced React patterns (HOCs, render props, compound components)
- Performance optimization (memoization, lazy loading, code splitting)
- State management (Redux, Zustand, Context API)
- React Server Components (Next.js)
- Testing strategies
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration
from shared.utils.kb_integration_mixin import DynamicKnowledgeBaseIntegration


class ReactSpecialistAgent(A2AEnabledAgent, DynamicKnowledgeBaseIntegration):
    """
    React Specialist Agent for advanced React development.
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        vector_db_client=None,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize React Specialist Agent."""
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
                kb_query_strategy="aggressive"  # Query KB frequently for best practices
            )

        aiplatform.init(
            project=context.get("project_id"),
            location=context.get("location", "us-central1")
        )

        self.model = GenerativeModel(model_name)
        self.optimization_history: List[Dict[str, Any]] = []

    @A2AIntegration.with_task_tracking
    def optimize_react_component(
        self,
        component_code: str,
        optimization_goals: List[str] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Optimize React component for performance.

        Args:
            component_code: Current component code
            optimization_goals: performance, bundle_size, accessibility, etc.
            task_id: Optional task ID

        Returns:
            Optimized component with explanations
        """
        optimization_goals = optimization_goals or ["performance", "bundle_size"]

        print(f"[React Specialist] Optimizing component: {optimization_goals}")

        # Query KB for optimization patterns
        kb_context = ""
        if hasattr(self, 'should_query_kb') and self.should_query_kb({"goals": optimization_goals}):
            kb_results = self.execute_dynamic_query(
                query_type="best_practices",
                context={"technology": "react", "focus": "performance"},
                task_id=task_id
            )
            if kb_results:
                kb_context = f"\n\nBest practices from KB:\n{kb_results}"

        prompt = f"""
Optimize this React component for: {', '.join(optimization_goals)}

**Current Component:**
```tsx
{component_code}
```

Apply optimizations:
1. **Performance:**
   - Use React.memo for expensive components
   - useMemo for expensive calculations
   - useCallback for event handlers
   - Lazy loading for code splitting

2. **Bundle Size:**
   - Tree shaking
   - Dynamic imports
   - Remove unused dependencies

3. **Rendering:**
   - Prevent unnecessary re-renders
   - Optimize list rendering with keys
   - Virtualization for long lists

4. **State Management:**
   - Minimize state
   - Lift state appropriately
   - Use context wisely

{kb_context}

Provide:
1. Optimized component code
2. Explanation of optimizations made
3. Performance impact estimates
4. Before/after comparison
"""

        response = self.model.generate_content(prompt)

        result = {
            "optimized_code": response.text,
            "optimization_goals": optimization_goals,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.optimization_history.append(result)

        return result

    @A2AIntegration.with_task_tracking
    def implement_advanced_pattern(
        self,
        pattern_type: str,
        use_case: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Implement advanced React patterns.

        Args:
            pattern_type: compound_components, render_props, hoc, custom_hooks, etc.
            use_case: Specific use case description
            task_id: Optional task ID

        Returns:
            Pattern implementation with examples
        """
        print(f"[React Specialist] Implementing {pattern_type} pattern")

        pattern_prompts = {
            "compound_components": """
Implement a Compound Component pattern for this use case:

{use_case}

The pattern should:
1. Use React.Children and cloneElement
2. Share implicit state between components
3. Provide flexible composition
4. Include proper TypeScript types

Example: <Tabs><Tab>One</Tab><Tab>Two</Tab><TabPanel>Content</TabPanel></Tabs>
""",
            "render_props": """
Implement a Render Props pattern:

{use_case}

Include:
1. Component with render prop
2. Flexible rendering logic
3. State management within render prop
4. TypeScript types
""",
            "custom_hooks": """
Create custom React hooks for this use case:

{use_case}

The hooks should:
1. Follow hooks rules
2. Be composable
3. Handle cleanup properly
4. Include TypeScript types
5. Handle edge cases
"""
        }

        prompt = pattern_prompts.get(pattern_type, pattern_prompts["custom_hooks"])
        prompt = prompt.format(use_case=use_case)

        response = self.model.generate_content(prompt)

        return {
            "pattern_code": response.text,
            "pattern_type": pattern_type,
            "use_case": use_case
        }

    def setup_nextjs_app(
        self,
        app_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Set up Next.js application with app router.

        Args:
            app_spec: App specification with pages, API routes, etc.

        Returns:
            Next.js project structure and configuration
        """
        print("[React Specialist] Setting up Next.js app")

        prompt = f"""
Set up a Next.js 14+ application with App Router:

**App Specification:**
{app_spec}

Include:
1. App directory structure
2. Page components with metadata
3. API routes
4. Server Components vs Client Components
5. Data fetching strategies
6. Middleware configuration
7. next.config.js
8. TypeScript configuration

Provide complete file structure with all necessary files.
"""

        response = self.model.generate_content(prompt)

        return {
            "project_structure": response.text,
            "app_name": app_spec.get("name", "NextJS App")
        }


# Tool functions
def optimize_react_component_tool(
    component_code: str,
    optimization_goals: List[str] = None
) -> Dict[str, Any]:
    """Tool function: Optimize React component."""
    agent = ReactSpecialistAgent(
        context={},
        message_bus=None,
        orchestrator_id=""
    )

    return agent.optimize_react_component(
        component_code=component_code,
        optimization_goals=optimization_goals
    )
