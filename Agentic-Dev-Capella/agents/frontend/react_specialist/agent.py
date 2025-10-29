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

    @A2AIntegration.with_task_tracking
    def setup_nextjs_app(
        self,
        app_spec: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Set up Next.js application with app router.

        Args:
            app_spec: App specification with pages, API routes, etc.
            task_id: Optional task ID

        Returns:
            Next.js project structure and configuration
        """
        print("[React Specialist] Setting up Next.js app")

        # Query KB for Next.js patterns
        kb_results = []
        if self.has_kb_access():
            kb_results = self.query_kb(
                query="Next.js app router server components best practices",
                top_k=3
            )

        prompt = f"""Set up a Next.js 14+ application with App Router:

**App Specification:**
{self._format_dict(app_spec)}

Include:
1. App directory structure
2. Page components with metadata
3. API routes
4. Server Components vs Client Components
5. Data fetching strategies
6. Middleware configuration
7. next.config.js
8. TypeScript configuration

{self._format_kb_results(kb_results) if kb_results else ""}

Provide complete file structure with all necessary files."""

        response = self.model.generate_content(prompt)

        return {
            "status": "success",
            "project_structure": response.text,
            "app_name": app_spec.get("name", "NextJS App"),
            "timestamp": datetime.now().isoformat()
        }

    def handle_task_assignment(self, message: Dict[str, Any]) -> None:
        """Handle incoming task assignments."""
        task_type = message.get("task_type")
        task_data = message.get("task_data", {})
        task_id = message.get("task_id")

        if task_type == "optimize_component":
            result = self.optimize_react_component(
                component_code=task_data.get("component_code"),
                optimization_goals=task_data.get("optimization_goals", ["performance"]),
                task_id=task_id
            )
        elif task_type == "implement_pattern":
            result = self.implement_advanced_pattern(
                pattern_type=task_data.get("pattern_type"),
                use_case=task_data.get("use_case", {}),
                task_id=task_id
            )
        elif task_type == "setup_nextjs":
            result = self.setup_nextjs_app(
                app_spec=task_data.get("app_spec", {}),
                task_id=task_id
            )
        elif task_type == "setup_state_management":
            result = self.setup_state_management(
                state_solution=task_data.get("state_solution", "zustand"),
                requirements=task_data.get("requirements", {}),
                task_id=task_id
            )
        elif task_type == "implement_server_components":
            result = self.implement_server_components(
                component_spec=task_data.get("component_spec", {}),
                task_id=task_id
            )
        elif task_type == "create_custom_hooks":
            result = self.create_custom_hooks(
                hook_requirements=task_data.get("hook_requirements", {}),
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
    def setup_state_management(
        self,
        state_solution: str,
        requirements: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Set up state management solution (Redux, Zustand, Context API, Jotai).

        Args:
            state_solution: redux, zustand, context, jotai, recoil
            requirements: State management requirements
            task_id: Optional task ID

        Returns:
            State management setup with store, actions, and hooks
        """
        print(f"[React Specialist] Setting up {state_solution} state management")

        # Query KB for state management patterns
        kb_results = []
        if self.has_kb_access():
            kb_results = self.query_kb(
                query=f"{state_solution} state management patterns React",
                top_k=3
            )

        prompt = f"""Set up {state_solution} state management for React application:

**Requirements:**
{self._format_dict(requirements)}

**State Entities:**
{self._format_list(requirements.get('entities', []))}

**Actions/Operations:**
{self._format_list(requirements.get('actions', []))}

Generate:

1. **Store Setup** - Complete store configuration
   - Initial state
   - Store creation
   - Middleware (if applicable)
   - DevTools integration

2. **State Slices/Stores** - For each entity
   - State interface
   - Actions/reducers
   - Selectors
   - Async actions (if needed)

3. **Custom Hooks** - For accessing state
   - useEntity hooks
   - Typed hooks
   - Compound selectors

4. **Provider Setup** - App-level setup
   - Provider component
   - Store persistence (if needed)
   - Initial data loading

5. **TypeScript Types** - Full type safety
   - State types
   - Action types
   - Selector types

6. **Best Practices**
   - Normalized state structure
   - Optimistic updates
   - Error handling
   - Loading states

{self._format_kb_results(kb_results) if kb_results else ""}

Provide complete implementation with all files."""

        response = self.model.generate_content(prompt)

        return {
            "status": "success",
            "state_solution": state_solution,
            "implementation": self._extract_code(response.text),
            "timestamp": datetime.now().isoformat()
        }

    @A2AIntegration.with_task_tracking
    def implement_server_components(
        self,
        component_spec: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Implement React Server Components (Next.js 13+).

        Args:
            component_spec: Component specification
            task_id: Optional task ID

        Returns:
            Server and client component implementation
        """
        print(f"[React Specialist] Implementing Server Components: {component_spec.get('name')}")

        # Query KB for RSC patterns
        kb_results = []
        if self.has_kb_access():
            kb_results = self.query_kb(
                query="React Server Components data fetching patterns",
                top_k=3
            )

        prompt = f"""Implement React Server Components for:

**Component:** {component_spec.get('name')}
**Type:** {component_spec.get('type', 'page')}

**Features:**
{self._format_list(component_spec.get('features', []))}

**Data Requirements:**
{self._format_dict(component_spec.get('data_requirements', {}))}

Create:

1. **Server Component** (default)
   - Async data fetching
   - Direct database/API access
   - SEO-optimized
   - No client-side JS

2. **Client Components** (if needed)
   - 'use client' directive
   - Interactive elements
   - Event handlers
   - State management

3. **Data Fetching**
   - Parallel data fetching
   - Streaming with Suspense
   - Error boundaries
   - Loading states

4. **Optimization**
   - Cache strategies
   - Revalidation
   - Static vs Dynamic rendering
   - Partial Prerendering

5. **Composition**
   - Server wraps Client
   - Props passing
   - Context usage
   - Shared layouts

{self._format_kb_results(kb_results) if kb_results else ""}

Generate complete implementation with both server and client components."""

        response = self.model.generate_content(prompt)

        return {
            "status": "success",
            "component_name": component_spec.get('name'),
            "implementation": self._extract_code(response.text),
            "timestamp": datetime.now().isoformat()
        }

    @A2AIntegration.with_task_tracking
    def create_custom_hooks(
        self,
        hook_requirements: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create custom React hooks for reusable logic.

        Args:
            hook_requirements: Hook requirements and specifications
            task_id: Optional task ID

        Returns:
            Custom hooks implementation
        """
        print(f"[React Specialist] Creating custom hooks: {hook_requirements.get('purpose')}")

        # Query KB for hook patterns
        kb_results = []
        if self.has_kb_access():
            kb_results = self.query_kb(
                query="React custom hooks patterns best practices",
                top_k=3
            )

        prompt = f"""Create custom React hooks for:

**Purpose:** {hook_requirements.get('purpose')}

**Requirements:**
{self._format_dict(hook_requirements)}

**Features Needed:**
{self._format_list(hook_requirements.get('features', []))}

Create hooks for:

1. **Data Fetching Hooks**
   - useFetch, useQuery, useMutation
   - Loading, error, data states
   - Caching and revalidation
   - Retry logic

2. **Form Hooks**
   - useForm with validation
   - Field management
   - Submission handling
   - Error display

3. **State Hooks**
   - useLocalStorage
   - useSessionStorage
   - usePrevious
   - useToggle, useBoolean

4. **Effect Hooks**
   - useDebounce, useThrottle
   - useInterval, useTimeout
   - useEventListener
   - useOnClickOutside

5. **Utility Hooks**
   - useMediaQuery
   - useWindowSize
   - useCopyToClipboard
   - useAsync

For each hook provide:
- TypeScript interface
- Implementation with proper cleanup
- Usage examples
- Edge case handling
- Tests examples

{self._format_kb_results(kb_results) if kb_results else ""}

Generate complete hooks library."""

        response = self.model.generate_content(prompt)

        return {
            "status": "success",
            "hooks_purpose": hook_requirements.get('purpose'),
            "implementation": self._extract_code(response.text),
            "timestamp": datetime.now().isoformat()
        }

    def _extract_code(self, response: str) -> str:
        """Extract code from LLM response."""
        import re
        code = response
        if "```" in code:
            parts = code.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 1:
                    lines = part.split("\n")
                    if lines and lines[0].strip() in [
                        "typescript", "ts", "javascript", "js", "tsx", "jsx"
                    ]:
                        lines = lines[1:]
                    code = "\n".join(lines)
                    break
        return code.strip()

    def _format_dict(self, data: Dict[str, Any]) -> str:
        """Format dictionary for prompt."""
        if not data:
            return "- None"
        return "\n".join(f"- {k}: {v}" for k, v in data.items())

    def _format_list(self, items: List[str]) -> str:
        """Format list for prompt."""
        if not items:
            return "- None"
        return "\n".join(f"- {item}" for item in items)

    def _format_kb_results(self, results: List[Dict[str, Any]]) -> str:
        """Format KB results for prompt."""
        if not results:
            return ""
        formatted = ["Knowledge Base Patterns:"]
        for i, result in enumerate(results, 1):
            formatted.append(f"{i}. {result.get('content', '')[:200]}...")
        return "\n".join(formatted)


# Tool functions
def optimize_react_component_tool(
    component_code: str,
    optimization_goals: List[str] = None
) -> Dict[str, Any]:
    """Tool function: Optimize React component."""
    class MockMessageBus:
        def publish(self, *args, **kwargs):
            pass

    agent = ReactSpecialistAgent(
        context={"project_id": "test", "location": "us-central1"},
        message_bus=MockMessageBus(),
        orchestrator_id="orchestrator"
    )

    return agent.optimize_react_component(
        component_code=component_code,
        optimization_goals=optimization_goals
    )


def implement_pattern_tool(
    pattern_type: str,
    use_case: Dict[str, Any]
) -> Dict[str, Any]:
    """Tool function: Implement advanced React pattern."""
    class MockMessageBus:
        def publish(self, *args, **kwargs):
            pass

    agent = ReactSpecialistAgent(
        context={"project_id": "test", "location": "us-central1"},
        message_bus=MockMessageBus(),
        orchestrator_id="orchestrator"
    )

    return agent.implement_advanced_pattern(
        pattern_type=pattern_type,
        use_case=use_case
    )


def create_react_specialist_agent(
    project_id: str,
    location: str,
    orchestrator_id: str = None
) -> ReactSpecialistAgent:
    """Factory function to create React Specialist Agent."""
    context = {
        "project_id": project_id,
        "location": location
    }

    class MockMessageBus:
        def publish(self, *args, **kwargs):
            pass

    return ReactSpecialistAgent(
        context=context,
        message_bus=MockMessageBus(),
        orchestrator_id=orchestrator_id or "orchestrator"
    )
