"""
agents/frontend/mobile_developer/agent.py

Mobile Developer Agent - Cross-platform mobile development specialist.

Specializes in:
- React Native development
- Flutter development
- Native features integration
- Mobile UI patterns
- Performance optimization for mobile
- App store deployment
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration
from shared.utils.kb_integration_mixin import DynamicKnowledgeBaseIntegration


class MobileDeveloperAgent(A2AEnabledAgent, DynamicKnowledgeBaseIntegration):
    """Mobile Developer Agent for React Native and Flutter."""

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        vector_db_client=None,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize Mobile Developer Agent."""
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
    def implement_mobile_screen(
        self,
        screen_spec: Dict[str, Any],
        platform: str = "react-native",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Implement mobile screen.

        Args:
            screen_spec: Screen specification
            platform: react-native, flutter, or both
            task_id: Optional task ID

        Returns:
            Screen implementation with navigation
        """
        print(f"[Mobile Developer] Implementing {screen_spec.get('name')} for {platform}")

        prompts = {
            "react-native": f"""
Implement a React Native screen:

**Screen:** {screen_spec}

Include:
1. Screen component with TypeScript
2. React Navigation integration
3. Platform-specific code (iOS/Android)
4. Responsive design (phone/tablet)
5. Accessibility features
6. Performance optimizations (FlatList, memoization)
7. Native module integration if needed
8. Styling with StyleSheet

Provide complete implementation.
""",
            "flutter": f"""
Implement a Flutter screen:

**Screen:** {screen_spec}

Include:
1. StatelessWidget or StatefulWidget
2. Material Design / Cupertino widgets
3. Navigation routes
4. Responsive layout (mobile/tablet)
5. Platform-specific widgets
6. State management (Provider/Riverpod)
7. Accessibility
8. Performance optimizations

Provide complete Dart code.
"""
        }

        prompt = prompts.get(platform, prompts["react-native"])
        response = self.model.generate_content(prompt)

        return {
            "screen_code": response.text,
            "platform": platform,
            "screen_name": screen_spec.get("name")
        }

    def setup_navigation(
        self,
        nav_structure: Dict[str, Any],
        platform: str = "react-native"
    ) -> Dict[str, Any]:
        """Set up mobile navigation structure."""
        print(f"[Mobile Developer] Setting up {platform} navigation")

        prompt = f"""
Set up {platform} navigation:

**Navigation Structure:**
{nav_structure}

For React Native:
- Use React Navigation 6+
- Stack, Tab, Drawer navigators
- Deep linking
- Authentication flow

For Flutter:
- Navigator 2.0 or go_router
- Route definitions
- Transitions
- Guards

Provide complete navigation setup.
"""

        response = self.model.generate_content(prompt)

        return {
            "navigation_code": response.text,
            "platform": platform
        }


# Tool function
def implement_mobile_screen_tool(
    screen_spec: Dict[str, Any],
    platform: str = "react-native"
) -> Dict[str, Any]:
    """Tool function: Implement mobile screen."""
    agent = MobileDeveloperAgent(
        context={},
        message_bus=None,
        orchestrator_id=""
    )

    return agent.implement_mobile_screen(
        screen_spec=screen_spec,
        platform=platform
    )
