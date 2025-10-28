"""
agents/multimodal/video_processor/agent.py

Video Processor Agent - Extracts requirements and demonstrations from video content.

Uses Gemini 2.0 Flash Exp for video analysis to:
- Extract product demos and walkthroughs
- Identify UI/UX flows from screen recordings
- Analyze feature demonstrations
- Extract technical requirements from video presentations
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from vertexai.generative_models import GenerativeModel, Part
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration


class VideoProcessorAgent(A2AEnabledAgent):
    """
    Video Processor Agent for analyzing video content.

    Uses Gemini 2.0 Flash Exp for video analysis.
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        model_name: str = "gemini-2.0-flash-exp"
    ):
        """Initialize Video Processor Agent."""
        super().__init__(context, message_bus)

        self.context = context
        self.orchestrator_id = orchestrator_id
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
        self.processing_history: List[Dict[str, Any]] = []

    @A2AIntegration.with_task_tracking
    def process_video(
        self,
        video_path: str,
        analysis_type: str = "product_demo",
        context: Dict[str, Any] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a video and extract relevant information.

        Args:
            video_path: Path to video file
            analysis_type: Type of analysis (product_demo, ui_flow, tutorial, etc.)
            context: Additional context
            task_id: Optional task ID

        Returns:
            Video analysis results
        """
        context = context or {}
        start_time = datetime.utcnow()

        print(f"[Video Processor] Analyzing {analysis_type}: {video_path}")

        # Read video file
        video_bytes = self._read_video(video_path)

        # Generate analysis prompt
        prompt = self._get_analysis_prompt(analysis_type, context)

        # Analyze with model
        analysis = self._analyze_with_model(video_bytes, video_path, prompt)

        duration = (datetime.utcnow() - start_time).total_seconds()

        result = {
            "analysis_type": analysis_type,
            "video_path": video_path,
            "duration_seconds": duration,
            "timestamp": datetime.utcnow().isoformat(),
            "features_demonstrated": [],
            "ui_flows": [],
            "user_interactions": [],
            "technical_requirements": {},
            "raw_analysis": analysis
        }

        self._parse_analysis(analysis, result)

        self.processing_history.append({
            "task_id": task_id,
            "timestamp": result["timestamp"],
            "analysis_type": analysis_type
        })

        return result

    def _read_video(self, video_path: str) -> bytes:
        """Read video file as bytes."""
        path = Path(video_path)
        if not path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        with open(video_path, "rb") as f:
            return f.read()

    def _get_analysis_prompt(self, analysis_type: str, context: Dict[str, Any]) -> str:
        """Generate analysis prompt."""
        return f"""
Analyze this video ({analysis_type}) and extract:

1. **Features Demonstrated** - What features are shown?
2. **UI Flow** - How does the user navigate?
3. **User Interactions** - What actions does the user take?
4. **Technical Requirements** - What technologies are needed?
5. **Key Screens/Pages** - Main screens shown
6. **Data Displayed** - What data is shown?

Context: {context}

Return as JSON with keys: features_demonstrated, ui_flows, user_interactions, technical_requirements, key_screens
"""

    def _analyze_with_model(self, video_bytes: bytes, video_path: str, prompt: str) -> str:
        """Analyze video with Gemini model."""
        try:
            # Determine MIME type
            mime_type = "video/mp4"  # Default
            if video_path.endswith(".mov"):
                mime_type = "video/quicktime"
            elif video_path.endswith(".avi"):
                mime_type = "video/x-msvideo"

            video_part = Part.from_data(data=video_bytes, mime_type=mime_type)

            response = self.model.generate_content([prompt, video_part])

            return response.text

        except Exception as e:
            raise RuntimeError(f"Video analysis failed: {str(e)}")

    def _parse_analysis(self, analysis_text: str, result: Dict[str, Any]) -> None:
        """Parse analysis and update result."""
        import json
        import re

        json_match = re.search(r'```json\s*(\{.*?\})\s*```', analysis_text, re.DOTALL)
        if not json_match:
            json_match = re.search(r'(\{.*\})', analysis_text, re.DOTALL)

        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                result.update(parsed)
            except json.JSONDecodeError:
                pass


# Tool function
def process_video_tool(
    video_path: str,
    analysis_type: str = "product_demo",
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Tool function: Process a video."""
    agent = VideoProcessorAgent(
        context={},
        message_bus=None,
        orchestrator_id=""
    )

    return agent.process_video(
        video_path=video_path,
        analysis_type=analysis_type,
        context=context
    )
