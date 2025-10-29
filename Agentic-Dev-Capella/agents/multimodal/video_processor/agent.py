"""
agents/multimodal/video_processor/agent.py

Video Processor Agent - Extracts requirements and demonstrations from video content.

Uses Gemini 2.0 Flash Exp for video analysis to:
- Extract product demos and walkthroughs
- Identify UI/UX flows from screen recordings
- Analyze feature demonstrations
- Extract technical requirements from video presentations
- Extract frames and key moments
- Generate transcriptions and captions
- Identify scene changes and transitions
- Extract user journey maps
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json
import re

from vertexai.generative_models import GenerativeModel, Part
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration
from shared.utils.kb_integration_mixin import DynamicKnowledgeBaseIntegration


class VideoProcessorAgent(A2AEnabledAgent, DynamicKnowledgeBaseIntegration):
    """
    Video Processor Agent for analyzing video content.

    Uses Gemini 2.0 Flash Exp for video analysis.
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        vector_db_client=None,
        model_name: str = "gemini-2.0-flash-exp"
    ):
        """Initialize Video Processor Agent."""
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
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', analysis_text, re.DOTALL)
        if not json_match:
            json_match = re.search(r'(\{.*\})', analysis_text, re.DOTALL)

        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                result.update(parsed)
            except json.JSONDecodeError:
                pass

    def handle_task_assignment(self, message: Dict[str, Any]) -> None:
        """Handle incoming task assignments."""
        task_type = message.get("task_type")
        task_data = message.get("task_data", {})
        task_id = message.get("task_id")

        if task_type == "process_video":
            result = self.process_video(
                video_path=task_data.get("video_path"),
                analysis_type=task_data.get("analysis_type", "product_demo"),
                context=task_data.get("context", {}),
                task_id=task_id
            )
        elif task_type == "extract_frames":
            result = self.extract_key_frames(
                video_path=task_data.get("video_path"),
                num_frames=task_data.get("num_frames", 10),
                task_id=task_id
            )
        elif task_type == "analyze_ui_flow":
            result = self.analyze_ui_flow(
                video_path=task_data.get("video_path"),
                task_id=task_id
            )
        elif task_type == "extract_user_journey":
            result = self.extract_user_journey(
                video_path=task_data.get("video_path"),
                task_id=task_id
            )
        elif task_type == "generate_transcription":
            result = self.generate_transcription(
                video_path=task_data.get("video_path"),
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
    def extract_key_frames(
        self,
        video_path: str,
        num_frames: int = 10,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract key frames from video at important moments.

        Args:
            video_path: Path to video file
            num_frames: Number of frames to extract
            task_id: Optional task ID

        Returns:
            Key frames with timestamps and descriptions
        """
        print(f"[Video Processor] Extracting {num_frames} key frames from: {video_path}")

        # Query KB for similar video analysis patterns
        kb_results = []
        if self.has_kb_access():
            kb_results = self.query_kb(
                query="video frame extraction UI analysis",
                top_k=3
            )

        video_bytes = self._read_video(video_path)

        prompt = f"""Analyze this video and identify the {num_frames} most important frames/moments.

For each key frame, provide:
1. **Timestamp** - When this moment occurs (e.g., "0:15", "1:23")
2. **Description** - What's happening in this frame
3. **Importance** - Why this frame is significant
4. **UI Elements** - Key UI elements visible
5. **User Action** - What user action is being demonstrated (if any)

Return as JSON array with keys: timestamp, description, importance, ui_elements, user_action

{self._format_kb_results(kb_results) if kb_results else ""}"""

        mime_type = self._get_mime_type(video_path)
        video_part = Part.from_data(data=video_bytes, mime_type=mime_type)

        response = self.model.generate_content([prompt, video_part])
        analysis_text = response.text

        # Parse frames
        frames = self._parse_key_frames(analysis_text)

        return {
            "status": "success",
            "video_path": video_path,
            "num_frames_requested": num_frames,
            "frames_extracted": len(frames),
            "key_frames": frames,
            "timestamp": datetime.now().isoformat()
        }

    @A2AIntegration.with_task_tracking
    def analyze_ui_flow(
        self,
        video_path: str,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze UI/UX flow and navigation patterns from video.

        Args:
            video_path: Path to video file
            task_id: Optional task ID

        Returns:
            UI flow analysis with screens, transitions, and user actions
        """
        print(f"[Video Processor] Analyzing UI flow from: {video_path}")

        # Query KB for UI flow patterns
        kb_results = []
        if self.has_kb_access():
            kb_results = self.query_kb(
                query="UI flow navigation patterns user journey",
                top_k=3
            )

        video_bytes = self._read_video(video_path)

        prompt = f"""Analyze the UI/UX flow in this video and extract:

1. **Screens/Pages** - All unique screens shown
   - Screen name/purpose
   - Key elements on each screen
   - Layout description

2. **Navigation Flow** - How user moves between screens
   - From screen → To screen
   - Navigation method (button click, swipe, etc.)
   - Transition type

3. **User Actions** - Step-by-step actions user takes
   - Action description
   - Screen where action occurs
   - Expected outcome

4. **Data Flow** - How data moves through the app
   - What data is entered/displayed
   - Where data comes from
   - Where data goes

5. **UI Patterns** - Common patterns used
   - Navigation patterns (tabs, sidebar, etc.)
   - Input patterns (forms, search, etc.)
   - Feedback patterns (loading, errors, etc.)

Return as JSON with keys: screens, navigation_flow, user_actions, data_flow, ui_patterns

{self._format_kb_results(kb_results) if kb_results else ""}"""

        mime_type = self._get_mime_type(video_path)
        video_part = Part.from_data(data=video_bytes, mime_type=mime_type)

        response = self.model.generate_content([prompt, video_part])
        analysis_text = response.text

        # Parse UI flow
        ui_flow = self._parse_json_response(analysis_text)

        return {
            "status": "success",
            "video_path": video_path,
            "ui_flow_analysis": ui_flow,
            "timestamp": datetime.now().isoformat()
        }

    @A2AIntegration.with_task_tracking
    def extract_user_journey(
        self,
        video_path: str,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract user journey map from video demonstration.

        Args:
            video_path: Path to video file
            task_id: Optional task ID

        Returns:
            User journey with stages, touchpoints, and emotions
        """
        print(f"[Video Processor] Extracting user journey from: {video_path}")

        video_bytes = self._read_video(video_path)

        prompt = """Create a user journey map from this video demonstration.

Extract:

1. **Journey Stages** - Main phases of the user experience
   - Stage name
   - Goal of this stage
   - Duration in video

2. **Touchpoints** - Points where user interacts with system
   - Interaction type
   - Screen/component
   - User expectation

3. **User Goals** - What user is trying to accomplish
   - Primary goals
   - Secondary goals
   - Success criteria

4. **Pain Points** - Challenges or friction points
   - What makes task difficult
   - Where user might get stuck
   - Suggested improvements

5. **Emotional Journey** - User emotions throughout
   - Frustration points
   - Satisfaction moments
   - Confusion areas

6. **Feature Requirements** - Features needed to support journey
   - Must-have features
   - Nice-to-have features
   - Technical requirements

Return as JSON with keys: journey_stages, touchpoints, user_goals, pain_points, emotional_journey, feature_requirements"""

        mime_type = self._get_mime_type(video_path)
        video_part = Part.from_data(data=video_bytes, mime_type=mime_type)

        response = self.model.generate_content([prompt, video_part])
        analysis_text = response.text

        # Parse journey
        journey = self._parse_json_response(analysis_text)

        return {
            "status": "success",
            "video_path": video_path,
            "user_journey": journey,
            "timestamp": datetime.now().isoformat()
        }

    @A2AIntegration.with_task_tracking
    def generate_transcription(
        self,
        video_path: str,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate transcription and captions from video audio.

        Args:
            video_path: Path to video file
            task_id: Optional task ID

        Returns:
            Transcription with timestamps and key quotes
        """
        print(f"[Video Processor] Generating transcription from: {video_path}")

        video_bytes = self._read_video(video_path)

        prompt = """Transcribe all spoken content in this video.

Provide:

1. **Full Transcription** - Complete text of all spoken words
   - Include speaker labels if multiple speakers
   - Note important tone/emphasis

2. **Timestamped Segments** - Break transcription into segments
   - Segment text
   - Start timestamp
   - End timestamp

3. **Key Quotes** - Most important statements
   - Quote text
   - Speaker
   - Timestamp
   - Why important

4. **Topics Discussed** - Main topics covered
   - Topic name
   - Time range
   - Key points

5. **Technical Terms** - Technical vocabulary used
   - Term
   - Context
   - Explanation (if given in video)

6. **Action Items** - Tasks or requirements mentioned
   - Action description
   - Who should do it
   - Priority/deadline

Return as JSON with keys: full_transcription, timestamped_segments, key_quotes, topics_discussed, technical_terms, action_items"""

        mime_type = self._get_mime_type(video_path)
        video_part = Part.from_data(data=video_bytes, mime_type=mime_type)

        response = self.model.generate_content([prompt, video_part])
        analysis_text = response.text

        # Parse transcription
        transcription = self._parse_json_response(analysis_text)

        return {
            "status": "success",
            "video_path": video_path,
            "transcription": transcription,
            "timestamp": datetime.now().isoformat()
        }

    def _get_mime_type(self, video_path: str) -> str:
        """Determine MIME type from file extension."""
        if video_path.endswith(".mov"):
            return "video/quicktime"
        elif video_path.endswith(".avi"):
            return "video/x-msvideo"
        elif video_path.endswith(".webm"):
            return "video/webm"
        else:
            return "video/mp4"

    def _parse_key_frames(self, analysis_text: str) -> List[Dict[str, Any]]:
        """Parse key frames from analysis text."""
        json_data = self._parse_json_response(analysis_text)

        if isinstance(json_data, list):
            return json_data
        elif isinstance(json_data, dict) and "frames" in json_data:
            return json_data["frames"]
        elif isinstance(json_data, dict) and "key_frames" in json_data:
            return json_data["key_frames"]
        else:
            return []

    def _parse_json_response(self, text: str) -> Any:
        """Parse JSON from LLM response."""
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```json\s*(\{.*?\}|\[.*?\])\s*```', text, re.DOTALL)
        if not json_match:
            json_match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)

        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        return {}

    def _format_kb_results(self, results: List[Dict[str, Any]]) -> str:
        """Format KB results for prompt."""
        if not results:
            return ""

        formatted = ["Knowledge Base Patterns:"]
        for i, result in enumerate(results, 1):
            formatted.append(f"{i}. {result.get('content', '')[:200]}...")
        return "\n".join(formatted)


# Tool functions for testing
def process_video_tool(
    video_path: str,
    analysis_type: str = "product_demo",
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Tool function: Process a video."""
    class MockMessageBus:
        def publish(self, *args, **kwargs):
            pass

    agent = VideoProcessorAgent(
        context={"project_id": "test", "location": "us-central1"},
        message_bus=MockMessageBus(),
        orchestrator_id="orchestrator"
    )

    return agent.process_video(
        video_path=video_path,
        analysis_type=analysis_type,
        context=context
    )


def extract_frames_tool(
    video_path: str,
    num_frames: int = 10
) -> Dict[str, Any]:
    """Tool function: Extract key frames."""
    class MockMessageBus:
        def publish(self, *args, **kwargs):
            pass

    agent = VideoProcessorAgent(
        context={"project_id": "test", "location": "us-central1"},
        message_bus=MockMessageBus(),
        orchestrator_id="orchestrator"
    )

    return agent.extract_key_frames(
        video_path=video_path,
        num_frames=num_frames
    )


def create_video_processor_agent(
    project_id: str,
    location: str,
    orchestrator_id: str = None
) -> VideoProcessorAgent:
    """Factory function to create Video Processor Agent."""
    context = {
        "project_id": project_id,
        "location": location
    }

    class MockMessageBus:
        def publish(self, *args, **kwargs):
            pass

    return VideoProcessorAgent(
        context=context,
        message_bus=MockMessageBus(),
        orchestrator_id=orchestrator_id or "orchestrator"
    )
