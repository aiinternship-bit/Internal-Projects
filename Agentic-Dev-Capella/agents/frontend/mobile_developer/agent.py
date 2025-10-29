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

    @A2AIntegration.with_task_tracking
    def setup_navigation(
        self,
        nav_structure: Dict[str, Any],
        platform: str = "react-native",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Set up mobile navigation structure."""
        print(f"[Mobile Developer] Setting up {platform} navigation")

        # Query KB for navigation patterns
        kb_results = []
        if self.has_kb_access():
            kb_results = self.query_kb(
                query=f"{platform} navigation patterns authentication flow",
                top_k=3
            )

        prompt = f"""Set up {platform} navigation:

**Navigation Structure:**
{self._format_dict(nav_structure)}

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

{self._format_kb_results(kb_results) if kb_results else ""}

Provide complete navigation setup."""

        response = self.model.generate_content(prompt)

        return {
            "status": "success",
            "navigation_code": response.text,
            "platform": platform,
            "timestamp": datetime.now().isoformat()
        }

    def handle_task_assignment(self, message: Dict[str, Any]) -> None:
        """Handle incoming task assignments."""
        task_type = message.get("task_type")
        task_data = message.get("task_data", {})
        task_id = message.get("task_id")

        if task_type == "implement_screen":
            result = self.implement_mobile_screen(
                screen_spec=task_data.get("screen_spec", {}),
                platform=task_data.get("platform", "react-native"),
                task_id=task_id
            )
        elif task_type == "setup_navigation":
            result = self.setup_navigation(
                nav_structure=task_data.get("nav_structure", {}),
                platform=task_data.get("platform", "react-native"),
                task_id=task_id
            )
        elif task_type == "implement_native_module":
            result = self.implement_native_module(
                module_spec=task_data.get("module_spec", {}),
                platform=task_data.get("platform", "react-native"),
                task_id=task_id
            )
        elif task_type == "optimize_mobile_performance":
            result = self.optimize_mobile_performance(
                app_code=task_data.get("app_code", ""),
                platform=task_data.get("platform", "react-native"),
                task_id=task_id
            )
        elif task_type == "setup_push_notifications":
            result = self.setup_push_notifications(
                notification_spec=task_data.get("notification_spec", {}),
                platform=task_data.get("platform", "react-native"),
                task_id=task_id
            )
        elif task_type == "implement_offline_support":
            result = self.implement_offline_support(
                offline_spec=task_data.get("offline_spec", {}),
                platform=task_data.get("platform", "react-native"),
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
    def implement_native_module(
        self,
        module_spec: Dict[str, Any],
        platform: str = "react-native",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Implement native module for platform-specific features.

        Args:
            module_spec: Module specification with native features
            platform: react-native or flutter
            task_id: Optional task ID

        Returns:
            Native module implementation for iOS and Android
        """
        print(f"[Mobile Developer] Implementing native module: {module_spec.get('name')}")

        # Query KB for native module patterns
        kb_results = []
        if self.has_kb_access():
            kb_results = self.query_kb(
                query=f"{platform} native module bridge implementation",
                top_k=3
            )

        prompt = f"""Implement native module for {platform}:

**Module Name:** {module_spec.get('name')}
**Purpose:** {module_spec.get('purpose')}

**Features:**
{self._format_list(module_spec.get('features', []))}

**Platform APIs Needed:**
{self._format_list(module_spec.get('platform_apis', []))}

Generate:

1. **JavaScript/Dart Bridge** - Interface layer
   - Method definitions
   - Type safety
   - Error handling
   - Callbacks/Promises

2. **iOS Implementation** (Swift/Objective-C)
   - Native module class
   - Bridge methods
   - iOS API integration
   - Thread handling

3. **Android Implementation** (Kotlin/Java)
   - Native module class
   - React Native bridge
   - Android API integration
   - Lifecycle management

4. **Setup & Configuration**
   - Package linking
   - Permissions (Info.plist, AndroidManifest.xml)
   - Dependencies
   - Build configuration

5. **Usage Examples**
   - JavaScript/Dart usage
   - Error handling
   - Testing

{self._format_kb_results(kb_results) if kb_results else ""}

Provide complete native module implementation for both platforms."""

        response = self.model.generate_content(prompt)

        return {
            "status": "success",
            "module_name": module_spec.get('name'),
            "implementation": self._extract_code(response.text),
            "platform": platform,
            "timestamp": datetime.now().isoformat()
        }

    @A2AIntegration.with_task_tracking
    def optimize_mobile_performance(
        self,
        app_code: str,
        platform: str = "react-native",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Optimize mobile app performance.

        Args:
            app_code: Current app code
            platform: react-native or flutter
            task_id: Optional task ID

        Returns:
            Optimized code with performance improvements
        """
        print(f"[Mobile Developer] Optimizing {platform} app performance")

        # Query KB for performance patterns
        kb_results = []
        if self.has_kb_access():
            kb_results = self.query_kb(
                query=f"{platform} performance optimization best practices",
                top_k=3
            )

        prompt = f"""Optimize {platform} app for mobile performance:

**Current Code:**
```
{app_code[:2000]}  # Truncate for prompt
```

Apply optimizations:

1. **Rendering Performance**
   - React Native: FlatList virtualization, React.memo, useCallback
   - Flutter: const constructors, ListView.builder, RepaintBoundary
   - Reduce re-renders/rebuilds
   - Image optimization and caching

2. **Bundle Size**
   - Code splitting and lazy loading
   - Remove unused dependencies
   - Hermes/dart2js optimization
   - ProGuard/R8 for Android

3. **Memory Management**
   - Proper cleanup in useEffect/dispose
   - Image memory optimization
   - Background task management
   - Memory leak prevention

4. **Network Optimization**
   - Request batching
   - Caching strategies
   - Compression
   - Background sync

5. **Startup Time**
   - Lazy initialization
   - Splash screen optimization
   - Code bundling
   - Native module optimization

6. **Battery Optimization**
   - Background task limits
   - Location services optimization
   - Wake lock management
   - Efficient polling

{self._format_kb_results(kb_results) if kb_results else ""}

Provide optimized code with detailed explanations."""

        response = self.model.generate_content(prompt)

        return {
            "status": "success",
            "optimized_code": self._extract_code(response.text),
            "optimizations_applied": ["rendering", "bundle_size", "memory", "network", "startup", "battery"],
            "platform": platform,
            "timestamp": datetime.now().isoformat()
        }

    @A2AIntegration.with_task_tracking
    def setup_push_notifications(
        self,
        notification_spec: Dict[str, Any],
        platform: str = "react-native",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Set up push notifications (FCM/APNS).

        Args:
            notification_spec: Notification requirements
            platform: react-native or flutter
            task_id: Optional task ID

        Returns:
            Push notification setup for iOS and Android
        """
        print(f"[Mobile Developer] Setting up push notifications for {platform}")

        # Query KB for push notification patterns
        kb_results = []
        if self.has_kb_access():
            kb_results = self.query_kb(
                query=f"{platform} push notifications FCM APNS setup",
                top_k=3
            )

        prompt = f"""Set up push notifications for {platform}:

**Requirements:**
{self._format_dict(notification_spec)}

**Notification Types:**
{self._format_list(notification_spec.get('notification_types', []))}

Implement:

1. **Firebase Cloud Messaging Setup**
   - Firebase project configuration
   - google-services.json / GoogleService-Info.plist
   - Dependencies and plugins

2. **iOS APNS Configuration**
   - Certificates and provisioning
   - Capabilities configuration
   - Push notification entitlements
   - App delegate setup

3. **Android FCM Configuration**
   - Firebase setup
   - AndroidManifest.xml
   - Service workers
   - Channel configuration

4. **Client-Side Implementation**
   - Token registration
   - Permission handling
   - Notification reception
   - Foreground/background handling
   - Action buttons
   - Deep linking

5. **Notification Handling**
   - onMessage, onBackgroundMessage
   - Navigation on tap
   - Badge updates
   - Local notifications

6. **Testing**
   - Test notification sending
   - Debug tools
   - Platform-specific testing

{self._format_kb_results(kb_results) if kb_results else ""}

Provide complete push notification setup."""

        response = self.model.generate_content(prompt)

        return {
            "status": "success",
            "notification_setup": self._extract_code(response.text),
            "platform": platform,
            "timestamp": datetime.now().isoformat()
        }

    @A2AIntegration.with_task_tracking
    def implement_offline_support(
        self,
        offline_spec: Dict[str, Any],
        platform: str = "react-native",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Implement offline support and sync.

        Args:
            offline_spec: Offline requirements
            platform: react-native or flutter
            task_id: Optional task ID

        Returns:
            Offline support implementation
        """
        print(f"[Mobile Developer] Implementing offline support for {platform}")

        # Query KB for offline patterns
        kb_results = []
        if self.has_kb_access():
            kb_results = self.query_kb(
                query=f"{platform} offline first architecture data sync",
                top_k=3
            )

        prompt = f"""Implement offline support for {platform}:

**Requirements:**
{self._format_dict(offline_spec)}

**Data to Cache:**
{self._format_list(offline_spec.get('cached_data', []))}

Implement:

1. **Local Storage Strategy**
   - React Native: AsyncStorage, MMKV, Realm, SQLite
   - Flutter: SharedPreferences, Hive, Sqflite, Isar
   - Storage selection based on data type
   - Encryption for sensitive data

2. **Offline-First Architecture**
   - Data caching layer
   - Request queue for offline actions
   - Optimistic UI updates
   - Conflict resolution

3. **Network Detection**
   - Online/offline detection
   - Network quality monitoring
   - Retry strategies
   - Exponential backoff

4. **Data Synchronization**
   - Background sync
   - Delta sync
   - Conflict resolution strategies
   - Last-write-wins vs merge strategies
   - Sync status UI

5. **API Layer**
   - Interceptors for caching
   - Request queueing
   - Response caching
   - Cache invalidation

6. **User Experience**
   - Offline indicator
   - Sync progress
   - Error handling
   - Retry options

{self._format_kb_results(kb_results) if kb_results else ""}

Provide complete offline support implementation."""

        response = self.model.generate_content(prompt)

        return {
            "status": "success",
            "offline_implementation": self._extract_code(response.text),
            "platform": platform,
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
                        "typescript", "ts", "javascript", "js", "tsx", "jsx",
                        "dart", "swift", "kotlin", "java", "objectivec"
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
def implement_mobile_screen_tool(
    screen_spec: Dict[str, Any],
    platform: str = "react-native"
) -> Dict[str, Any]:
    """Tool function: Implement mobile screen."""
    class MockMessageBus:
        def publish(self, *args, **kwargs):
            pass

    agent = MobileDeveloperAgent(
        context={"project_id": "test", "location": "us-central1"},
        message_bus=MockMessageBus(),
        orchestrator_id="orchestrator"
    )

    return agent.implement_mobile_screen(
        screen_spec=screen_spec,
        platform=platform
    )


def implement_native_module_tool(
    module_spec: Dict[str, Any],
    platform: str = "react-native"
) -> Dict[str, Any]:
    """Tool function: Implement native module."""
    class MockMessageBus:
        def publish(self, *args, **kwargs):
            pass

    agent = MobileDeveloperAgent(
        context={"project_id": "test", "location": "us-central1"},
        message_bus=MockMessageBus(),
        orchestrator_id="orchestrator"
    )

    return agent.implement_native_module(
        module_spec=module_spec,
        platform=platform
    )


def create_mobile_developer_agent(
    project_id: str,
    location: str,
    orchestrator_id: str = None
) -> MobileDeveloperAgent:
    """Factory function to create Mobile Developer Agent."""
    context = {
        "project_id": project_id,
        "location": location
    }

    class MockMessageBus:
        def publish(self, *args, **kwargs):
            pass

    return MobileDeveloperAgent(
        context=context,
        message_bus=MockMessageBus(),
        orchestrator_id=orchestrator_id or "orchestrator"
    )
