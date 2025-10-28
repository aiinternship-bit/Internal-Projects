"""
agents/frontend/accessibility_specialist/agent.py

Accessibility Specialist Agent - Ensures WCAG compliance and inclusive design.

Specializes in:
- WCAG 2.1 AA/AAA compliance
- ARIA attributes and roles
- Keyboard navigation
- Screen reader optimization
- Color contrast
- Focus management
- Accessible forms
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration


class AccessibilitySpecialistAgent(A2AEnabledAgent):
    """Accessibility Specialist Agent for WCAG compliance."""

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        model_name: str = "gemini-2.0-flash"
    ):
        """Initialize Accessibility Specialist Agent."""
        super().__init__(context, message_bus)

        self.context = context
        self.model_name = model_name

        self.a2a = A2AIntegration(
            context=context,
            message_bus=message_bus,
            orchestrator_id=orchestrator_id
        )

        aiplatform.init(
            project=context.get("project_id"),
            location=context.get("location", "us-central1")
        )

        self.model = GenerativeModel(model_name)

    @A2AIntegration.with_task_tracking
    def audit_accessibility(
        self,
        component_code: str,
        target_level: str = "AA",
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Audit component for accessibility issues.

        Args:
            component_code: Component HTML/JSX code
            target_level: A, AA, or AAA
            task_id: Optional task ID

        Returns:
            Audit results with issues and recommendations
        """
        print(f"[Accessibility Specialist] Auditing for WCAG {target_level}")

        prompt = f"""
Audit this component for WCAG 2.1 {target_level} compliance:

```
{component_code}
```

Check for:
1. **Perceivable**
   - Alt text for images
   - Color contrast ratios
   - Text sizing
   - Captions for media

2. **Operable**
   - Keyboard navigation
   - Focus indicators
   - Skip links
   - No keyboard traps

3. **Understandable**
   - Clear labels
   - Error messages
   - Consistent navigation
   - Form validation

4. **Robust**
   - Valid HTML
   - ARIA attributes
   - Semantic markup
   - Screen reader compatibility

Provide:
1. List of issues (severity: critical, major, minor)
2. WCAG criterion violated
3. Specific recommendations
4. Code fixes

Return as structured JSON.
"""

        response = self.model.generate_content(prompt)

        return {
            "audit_report": response.text,
            "target_level": target_level,
            "timestamp": datetime.utcnow().isoformat()
        }

    @A2AIntegration.with_task_tracking
    def fix_accessibility_issues(
        self,
        component_code: str,
        issues: List[Dict[str, Any]],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fix accessibility issues in component.

        Args:
            component_code: Original component code
            issues: List of accessibility issues to fix
            task_id: Optional task ID

        Returns:
            Fixed component code
        """
        print(f"[Accessibility Specialist] Fixing {len(issues)} issues")

        prompt = f"""
Fix these accessibility issues:

**Component:**
```
{component_code}
```

**Issues to fix:**
{issues}

Apply fixes:
1. Add proper ARIA attributes
2. Improve semantic HTML
3. Add keyboard support
4. Fix color contrast
5. Add focus management
6. Improve labels and descriptions

Provide:
1. Fixed component code
2. Explanation of each fix
3. Testing instructions
"""

        response = self.model.generate_content(prompt)

        return {
            "fixed_code": response.text,
            "issues_fixed": len(issues)
        }

    def generate_accessible_component(
        self,
        component_spec: Dict[str, Any],
        target_level: str = "AA"
    ) -> Dict[str, Any]:
        """
        Generate component with accessibility built-in.

        Args:
            component_spec: Component specification
            target_level: WCAG level

        Returns:
            Accessible component implementation
        """
        print(f"[Accessibility Specialist] Generating WCAG {target_level} component")

        prompt = f"""
Create an accessible component from scratch:

**Spec:**
{component_spec}

**Target:** WCAG 2.1 {target_level}

Build with:
1. Semantic HTML5 elements
2. Proper ARIA roles and attributes
3. Keyboard navigation support (Tab, Enter, Esc, arrows)
4. Focus management
5. Screen reader announcements
6. Color contrast compliance
7. Text sizing
8. Error handling
9. Loading states

Provide complete implementation with accessibility features.
"""

        response = self.model.generate_content(prompt)

        return {
            "component_code": response.text,
            "wcag_level": target_level
        }


# Tool functions
def audit_accessibility_tool(
    component_code: str,
    target_level: str = "AA"
) -> Dict[str, Any]:
    """Tool function: Audit accessibility."""
    agent = AccessibilitySpecialistAgent(
        context={},
        message_bus=None,
        orchestrator_id=""
    )

    return agent.audit_accessibility(
        component_code=component_code,
        target_level=target_level
    )


def fix_accessibility_issues_tool(
    component_code: str,
    issues: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Tool function: Fix accessibility issues."""
    agent = AccessibilitySpecialistAgent(
        context={},
        message_bus=None,
        orchestrator_id=""
    )

    return agent.fix_accessibility_issues(
        component_code=component_code,
        issues=issues
    )
