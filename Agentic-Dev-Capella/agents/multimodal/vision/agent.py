"""
agents/multimodal/vision/agent.py

Vision Agent - Analyzes images, screenshots, UI mockups, and diagrams.

This agent uses Gemini 2.0 Flash Exp (multimodal) to:
- Extract UI/UX components from mockups
- Identify design patterns and layouts
- Detect technical requirements from screenshots
- Analyze architecture diagrams
- Extract text and annotations from images
- Identify color schemes, fonts, and styling
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import base64
import mimetypes
from pathlib import Path

from vertexai.generative_models import GenerativeModel, Part
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration
from shared.models.agent_capability import InputModality


class VisionAgent(A2AEnabledAgent):
    """
    Vision Agent for analyzing images, screenshots, and visual designs.

    Uses Gemini 2.0 Flash Exp for multimodal vision analysis.
    Extracts UI components, design patterns, and technical requirements.
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        model_name: str = "gemini-2.0-flash-exp"
    ):
        """
        Initialize Vision Agent.

        Args:
            context: Agent context (project_id, location, etc.)
            message_bus: A2A message bus
            orchestrator_id: ID of orchestrator
            model_name: Multimodal model to use
        """
        super().__init__(context, message_bus)

        self.context = context
        self.orchestrator_id = orchestrator_id
        self.model_name = model_name

        # Initialize A2A integration
        self.a2a = A2AIntegration(
            context=context,
            message_bus=message_bus,
            orchestrator_id=orchestrator_id
        )

        # Initialize Vertex AI
        aiplatform.init(
            project=context.get("project_id"),
            location=context.get("location", "us-central1")
        )

        self.model = GenerativeModel(model_name)

        # Analysis history
        self.analysis_history: List[Dict[str, Any]] = []

    def handle_task_assignment(self, message: Dict[str, Any]) -> None:
        """
        Handle TASK_ASSIGNMENT message from orchestrator.

        Expected payload:
        {
            "image_path": str,
            "analysis_type": str,  # ui_mockup, screenshot, diagram, etc.
            "context": Dict
        }
        """
        payload = message.get("payload", {})
        task_id = payload.get("task_id")

        try:
            # Analyze image
            result = self.analyze_image(
                image_path=payload.get("image_path"),
                analysis_type=payload.get("analysis_type", "ui_mockup"),
                context=payload.get("context", {}),
                task_id=task_id
            )

            # Send completion
            self.a2a.send_completion(
                task_id=task_id,
                artifacts=result,
                metrics={
                    "analysis_duration_seconds": result.get("duration_seconds", 0)
                }
            )

        except Exception as e:
            self.a2a.send_error_report(
                task_id=task_id,
                error_type="VISION_ANALYSIS_FAILED",
                error_message=str(e),
                stack_trace=""
            )

    @A2AIntegration.with_task_tracking
    def analyze_image(
        self,
        image_path: str,
        analysis_type: str = "ui_mockup",
        context: Dict[str, Any] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze an image and extract relevant information.

        Args:
            image_path: Path to image file
            analysis_type: Type of analysis (ui_mockup, screenshot, diagram, etc.)
            context: Additional context
            task_id: Optional task ID

        Returns:
            {
                "analysis_type": str,
                "components": List[Dict],
                "design_patterns": List[str],
                "technical_requirements": Dict,
                "color_scheme": Dict,
                "typography": Dict,
                "layout": Dict,
                "extracted_text": str,
                "raw_analysis": str
            }
        """
        context = context or {}
        start_time = datetime.utcnow()

        print(f"[Vision Agent] Analyzing {analysis_type}: {image_path}")

        # Read image file
        image_bytes = self._read_image(image_path)

        # Determine analysis prompt based on type
        prompt = self._get_analysis_prompt(analysis_type, context)

        # Analyze with vision model
        analysis = self._analyze_with_model(image_bytes, image_path, prompt)

        # Parse analysis based on type
        parsed_result = self._parse_analysis(analysis, analysis_type)

        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()

        result = {
            "analysis_type": analysis_type,
            "image_path": image_path,
            "duration_seconds": duration,
            "timestamp": datetime.utcnow().isoformat(),
            **parsed_result
        }

        # Store in history
        self.analysis_history.append({
            "task_id": task_id,
            "timestamp": result["timestamp"],
            "analysis_type": analysis_type,
            "image_path": image_path
        })

        return result

    def _read_image(self, image_path: str) -> bytes:
        """Read image file as bytes."""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        with open(image_path, "rb") as f:
            return f.read()

    def _get_analysis_prompt(self, analysis_type: str, context: Dict[str, Any]) -> str:
        """
        Generate analysis prompt based on type.
        """
        base_context = f"Additional context: {context}" if context else ""

        prompts = {
            "ui_mockup": f"""
Analyze this UI mockup/design and extract:

1. **UI Components** - List all UI elements (buttons, inputs, cards, navigation, etc.)
   - For each component: type, position, styling, functionality

2. **Layout Structure** - Describe the layout system
   - Grid/flexbox structure
   - Responsive breakpoints suggested
   - Spacing and alignment patterns

3. **Design Patterns** - Identify design patterns used
   - Navigation pattern (sidebar, top nav, etc.)
   - Card layouts, modals, forms, tables, etc.

4. **Color Scheme** - Extract colors used
   - Primary, secondary, accent colors
   - Background colors
   - Text colors

5. **Typography** - Font information
   - Font families (or similar)
   - Font sizes and weights
   - Line heights and spacing

6. **Technical Requirements** - What technologies might be needed?
   - Frontend framework (React, Vue, Angular)
   - Component libraries
   - State management needs
   - API endpoints implied

7. **Interactions** - Describe interactive elements
   - Buttons, links, dropdowns
   - Forms and validation
   - Animations suggested

{base_context}

Return as structured JSON with keys: components, layout, design_patterns, color_scheme, typography, technical_requirements, interactions, extracted_text
""",

            "screenshot": f"""
Analyze this application screenshot and extract:

1. **Application Type** - What kind of application is this?
   - Web app, mobile app, desktop app
   - Category (dashboard, e-commerce, social, etc.)

2. **UI Components** - Visible components and their states
   - Component types and hierarchy
   - Current state (selected, disabled, active, etc.)

3. **Functionality** - What can users do?
   - Main features visible
   - Navigation options
   - Data displayed

4. **Technical Stack** - What technologies might be used?
   - Framework indicators (React DevTools, Vue, etc.)
   - UI library (Material-UI, Bootstrap, Tailwind)

5. **Data Requirements** - What data is shown?
   - Data types and structures
   - API endpoints likely needed
   - State management complexity

6. **UX Patterns** - User experience patterns
   - Navigation flow
   - Information architecture
   - Error handling visible

{base_context}

Return as structured JSON.
""",

            "diagram": f"""
Analyze this architecture/design diagram and extract:

1. **Diagram Type** - What kind of diagram?
   - Architecture diagram, flow chart, sequence diagram, etc.

2. **Components** - All components/boxes in the diagram
   - Name, type, responsibilities
   - Technologies mentioned

3. **Connections** - Relationships between components
   - Type of connection (API call, data flow, depends on, etc.)
   - Protocols mentioned (HTTP, gRPC, message queue, etc.)

4. **Data Flow** - How data moves through the system
   - Input sources
   - Processing steps
   - Output destinations

5. **Infrastructure** - Infrastructure elements
   - Databases, caches, queues
   - Cloud services
   - Network components

6. **Technical Requirements** - Implied requirements
   - Scalability needs
   - Security requirements
   - Performance considerations

{base_context}

Return as structured JSON.
""",

            "wireframe": f"""
Analyze this wireframe and extract:

1. **Page Structure** - Overall page layout
   - Header, body, footer, sidebar
   - Content sections

2. **Components** - UI components (low fidelity)
   - Buttons, inputs, placeholders
   - Navigation elements

3. **Content Hierarchy** - Information architecture
   - Primary, secondary, tertiary content
   - Call-to-action elements

4. **User Flow** - Implied user journey
   - Entry points
   - Actions available
   - Next steps

5. **Implementation Notes** - Development considerations
   - Responsive behavior
   - Component reusability
   - State management needs

{base_context}

Return as structured JSON.
""",

            "design_system": f"""
Analyze this design system/style guide and extract:

1. **Color Palette** - All colors defined
   - Primary, secondary, accent colors
   - Semantic colors (success, error, warning, info)
   - Grayscale palette

2. **Typography** - Font system
   - Font families
   - Type scale (sizes)
   - Font weights
   - Line heights

3. **Spacing System** - Spacing scale
   - Base unit
   - Spacing values

4. **Component Variants** - Component variations
   - Button styles (primary, secondary, sizes)
   - Input styles
   - Card variants

5. **Icons** - Icon set information
   - Icon style (outlined, filled, etc.)
   - Icon sizes

6. **Layout Grid** - Grid system
   - Columns
   - Gutters
   - Breakpoints

{base_context}

Return as structured JSON.
"""
        }

        return prompts.get(analysis_type, prompts["ui_mockup"])

    def _analyze_with_model(self, image_bytes: bytes, image_path: str, prompt: str) -> str:
        """
        Analyze image with Gemini vision model.
        """
        try:
            # Detect MIME type
            mime_type = mimetypes.guess_type(image_path)[0] or "image/jpeg"

            # Create image part
            image_part = Part.from_data(data=image_bytes, mime_type=mime_type)

            # Generate analysis
            response = self.model.generate_content([prompt, image_part])

            return response.text

        except Exception as e:
            raise RuntimeError(f"Vision model analysis failed: {str(e)}")

    def _parse_analysis(self, analysis_text: str, analysis_type: str) -> Dict[str, Any]:
        """
        Parse the model's analysis response into structured format.
        """
        # Try to extract JSON from response
        import json
        import re

        result = {
            "components": [],
            "design_patterns": [],
            "technical_requirements": {},
            "color_scheme": {},
            "typography": {},
            "layout": {},
            "extracted_text": "",
            "raw_analysis": analysis_text
        }

        # Try to find JSON in response
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', analysis_text, re.DOTALL)
        if not json_match:
            json_match = re.search(r'(\{.*\})', analysis_text, re.DOTALL)

        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                result.update(parsed)
            except json.JSONDecodeError:
                # Fallback to raw analysis
                pass

        return result

    def analyze_batch(
        self,
        image_paths: List[str],
        analysis_type: str = "ui_mockup",
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple images in batch.

        Args:
            image_paths: List of image paths
            analysis_type: Type of analysis
            context: Additional context

        Returns:
            List of analysis results
        """
        results = []

        for image_path in image_paths:
            try:
                result = self.analyze_image(
                    image_path=image_path,
                    analysis_type=analysis_type,
                    context=context
                )
                results.append(result)
            except Exception as e:
                print(f"Error analyzing {image_path}: {str(e)}")
                results.append({
                    "image_path": image_path,
                    "error": str(e),
                    "status": "failed"
                })

        return results

    def compare_designs(
        self,
        image_path_1: str,
        image_path_2: str,
        comparison_focus: str = "ui_components"
    ) -> Dict[str, Any]:
        """
        Compare two designs/mockups.

        Args:
            image_path_1: First image
            image_path_2: Second image
            comparison_focus: What to compare (ui_components, layout, colors, etc.)

        Returns:
            Comparison result with similarities and differences
        """
        # Analyze both images
        analysis_1 = self.analyze_image(image_path_1, "ui_mockup")
        analysis_2 = self.analyze_image(image_path_2, "ui_mockup")

        # Build comparison prompt
        prompt = f"""
Compare these two UI designs focusing on {comparison_focus}.

Design 1 analysis:
{analysis_1.get('raw_analysis', '')}

Design 2 analysis:
{analysis_2.get('raw_analysis', '')}

Provide:
1. Similarities
2. Differences
3. Recommendations for consistency

Return as JSON with keys: similarities, differences, recommendations
"""

        # Generate comparison (text-only, no images needed)
        try:
            response = self.model.generate_content(prompt)
            comparison_text = response.text

            return {
                "image_1": image_path_1,
                "image_2": image_path_2,
                "comparison_focus": comparison_focus,
                "analysis_1": analysis_1,
                "analysis_2": analysis_2,
                "comparison": comparison_text
            }

        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }

    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get vision agent statistics."""
        if not self.analysis_history:
            return {"total_analyses": 0}

        analysis_types = {}
        for record in self.analysis_history:
            atype = record.get("analysis_type", "unknown")
            analysis_types[atype] = analysis_types.get(atype, 0) + 1

        return {
            "total_analyses": len(self.analysis_history),
            "analysis_types": analysis_types,
            "model_used": self.model_name
        }


# Tool functions for Vertex AI Reasoning Engine deployment
def analyze_image_tool(
    image_path: str,
    analysis_type: str = "ui_mockup",
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Tool function: Analyze an image.

    This is the main entry point when deployed as Vertex AI Reasoning Engine.
    """
    # This will be injected with actual context during deployment
    agent = VisionAgent(
        context={},  # Filled by deployment script
        message_bus=None,  # Filled by deployment script
        orchestrator_id=""  # Filled by deployment script
    )

    result = agent.analyze_image(
        image_path=image_path,
        analysis_type=analysis_type,
        context=context
    )

    return result


def analyze_batch_tool(
    image_paths: List[str],
    analysis_type: str = "ui_mockup",
    context: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """
    Tool function: Analyze multiple images.
    """
    agent = VisionAgent(
        context={},
        message_bus=None,
        orchestrator_id=""
    )

    return agent.analyze_batch(
        image_paths=image_paths,
        analysis_type=analysis_type,
        context=context
    )
