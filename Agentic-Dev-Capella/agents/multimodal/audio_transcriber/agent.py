"""
agents/multimodal/audio_transcriber/agent.py

Audio Transcriber Agent - Transcribes and analyzes audio content.

Uses Gemini 2.0 Flash Exp for audio transcription and analysis to:
- Transcribe meetings and discussions
- Extract requirements from verbal descriptions
- Identify action items and decisions
- Analyze technical discussions
- Speaker diarization (identify different speakers)
- Sentiment and tone analysis
- Extract technical specifications
- Generate meeting summaries
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


class AudioTranscriberAgent(A2AEnabledAgent, DynamicKnowledgeBaseIntegration):
    """
    Audio Transcriber Agent for transcribing and analyzing audio.

    Uses Gemini 2.0 Flash Exp for audio processing.
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        vector_db_client=None,
        model_name: str = "gemini-2.0-flash-exp"
    ):
        """Initialize Audio Transcriber Agent."""
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
        self.transcription_history: List[Dict[str, Any]] = []

    @A2AIntegration.with_task_tracking
    def transcribe_audio(
        self,
        audio_path: str,
        audio_type: str = "meeting",
        extract_items: List[str] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio and extract relevant information.

        Args:
            audio_path: Path to audio file
            audio_type: Type of audio (meeting, interview, discussion, etc.)
            extract_items: What to extract (requirements, action_items, decisions, etc.)
            task_id: Optional task ID

        Returns:
            Transcription and analysis results
        """
        extract_items = extract_items or ["requirements", "action_items"]
        start_time = datetime.utcnow()

        print(f"[Audio Transcriber] Transcribing {audio_type}: {audio_path}")

        # Read audio file
        audio_bytes = self._read_audio(audio_path)

        # Generate prompt
        prompt = self._get_transcription_prompt(audio_type, extract_items)

        # Transcribe with model
        transcription = self._transcribe_with_model(audio_bytes, audio_path, prompt)

        duration = (datetime.utcnow() - start_time).total_seconds()

        result = {
            "audio_type": audio_type,
            "audio_path": audio_path,
            "duration_seconds": duration,
            "timestamp": datetime.utcnow().isoformat(),
            "transcript": "",
            "requirements": [],
            "action_items": [],
            "decisions": [],
            "speakers": [],
            "key_topics": [],
            "raw_transcription": transcription
        }

        self._parse_transcription(transcription, result)

        self.transcription_history.append({
            "task_id": task_id,
            "timestamp": result["timestamp"],
            "audio_type": audio_type
        })

        return result

    def _read_audio(self, audio_path: str) -> bytes:
        """Read audio file as bytes."""
        path = Path(audio_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio not found: {audio_path}")

        with open(audio_path, "rb") as f:
            return f.read()

    def _get_transcription_prompt(self, audio_type: str, extract_items: List[str]) -> str:
        """Generate transcription prompt."""
        items_str = ", ".join(extract_items)

        return f"""
Transcribe this audio ({audio_type}) and extract:

1. **Full Transcript** - Complete text transcription
2. **Requirements** - Any requirements mentioned
3. **Action Items** - Tasks and assignments
4. **Decisions** - Key decisions made
5. **Speakers** - Who is speaking (if identifiable)
6. **Key Topics** - Main topics discussed

Focus on extracting: {items_str}

Return as JSON with keys: transcript, requirements, action_items, decisions, speakers, key_topics
"""

    def _transcribe_with_model(self, audio_bytes: bytes, audio_path: str, prompt: str) -> str:
        """Transcribe audio with Gemini model."""
        try:
            # Determine MIME type
            mime_type = "audio/mpeg"  # Default
            if audio_path.endswith(".wav"):
                mime_type = "audio/wav"
            elif audio_path.endswith(".m4a"):
                mime_type = "audio/mp4"
            elif audio_path.endswith(".ogg"):
                mime_type = "audio/ogg"

            audio_part = Part.from_data(data=audio_bytes, mime_type=mime_type)

            response = self.model.generate_content([prompt, audio_part])

            return response.text

        except Exception as e:
            raise RuntimeError(f"Audio transcription failed: {str(e)}")

    def _parse_transcription(self, transcription_text: str, result: Dict[str, Any]) -> None:
        """Parse transcription and update result."""
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', transcription_text, re.DOTALL)
        if not json_match:
            json_match = re.search(r'(\{.*\})', transcription_text, re.DOTALL)

        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                result.update(parsed)
            except json.JSONDecodeError:
                # Fallback: use raw text as transcript
                result["transcript"] = transcription_text

    def handle_task_assignment(self, message: Dict[str, Any]) -> None:
        """Handle incoming task assignments."""
        task_type = message.get("task_type")
        task_data = message.get("task_data", {})
        task_id = message.get("task_id")

        if task_type == "transcribe_audio":
            result = self.transcribe_audio(
                audio_path=task_data.get("audio_path"),
                audio_type=task_data.get("audio_type", "meeting"),
                extract_items=task_data.get("extract_items", ["requirements", "action_items"]),
                task_id=task_id
            )
        elif task_type == "analyze_meeting":
            result = self.analyze_meeting(
                audio_path=task_data.get("audio_path"),
                task_id=task_id
            )
        elif task_type == "extract_technical_specs":
            result = self.extract_technical_specs(
                audio_path=task_data.get("audio_path"),
                task_id=task_id
            )
        elif task_type == "identify_speakers":
            result = self.identify_speakers(
                audio_path=task_data.get("audio_path"),
                task_id=task_id
            )
        elif task_type == "analyze_sentiment":
            result = self.analyze_sentiment(
                audio_path=task_data.get("audio_path"),
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
    def analyze_meeting(
        self,
        audio_path: str,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive meeting analysis with summary, action items, and decisions.

        Args:
            audio_path: Path to meeting audio file
            task_id: Optional task ID

        Returns:
            Meeting analysis with summary, attendees, decisions, action items
        """
        print(f"[Audio Transcriber] Analyzing meeting: {audio_path}")

        # Query KB for meeting analysis patterns
        kb_results = []
        if self.has_kb_access():
            kb_results = self.query_kb(
                query="meeting analysis requirements extraction",
                top_k=3
            )

        audio_bytes = self._read_audio(audio_path)

        prompt = f"""Analyze this meeting recording and provide comprehensive analysis:

1. **Meeting Summary** - High-level overview of discussion
   - Main topics covered
   - Overall purpose/goal
   - Key outcomes

2. **Attendees/Speakers** - Who participated
   - Speaker identifiers (Speaker 1, Speaker 2, etc.)
   - Estimated roles based on content
   - Participation level

3. **Decisions Made** - Key decisions reached
   - Decision description
   - Who made the decision
   - Rationale/reasoning
   - Impact/implications

4. **Action Items** - Tasks assigned
   - Task description
   - Assignee (if mentioned)
   - Deadline (if mentioned)
   - Priority (high/medium/low)
   - Dependencies

5. **Requirements Discussed** - Technical/business requirements
   - Requirement description
   - Type (functional/non-functional/technical)
   - Priority
   - Owner

6. **Open Questions** - Unresolved items
   - Question
   - Who asked
   - Why important

7. **Follow-ups Needed** - What needs to happen next
   - Follow-up action
   - Why needed
   - Who should handle

8. **Key Timestamps** - Important moments
   - Timestamp
   - What happened
   - Why significant

Return as JSON with keys: meeting_summary, attendees, decisions, action_items, requirements, open_questions, follow_ups, key_timestamps

{self._format_kb_results(kb_results) if kb_results else ""}"""

        mime_type = self._get_mime_type(audio_path)
        audio_part = Part.from_data(data=audio_bytes, mime_type=mime_type)

        response = self.model.generate_content([prompt, audio_part])
        analysis_text = response.text

        # Parse analysis
        analysis = self._parse_json_response(analysis_text)

        return {
            "status": "success",
            "audio_path": audio_path,
            "meeting_analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }

    @A2AIntegration.with_task_tracking
    def extract_technical_specs(
        self,
        audio_path: str,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract technical specifications from audio discussion.

        Args:
            audio_path: Path to audio file
            task_id: Optional task ID

        Returns:
            Technical specifications with details
        """
        print(f"[Audio Transcriber] Extracting technical specs from: {audio_path}")

        # Query KB for technical patterns
        kb_results = []
        if self.has_kb_access():
            kb_results = self.query_kb(
                query="technical specifications system requirements",
                top_k=3
            )

        audio_bytes = self._read_audio(audio_path)

        prompt = f"""Extract technical specifications from this audio discussion:

1. **System Requirements** - Overall system needs
   - Performance requirements
   - Scalability requirements
   - Availability requirements
   - Security requirements

2. **Technical Architecture** - Architecture decisions
   - Architecture style (microservices, monolith, etc.)
   - Components mentioned
   - Integration patterns
   - Technology stack

3. **APIs and Interfaces** - API specifications
   - API endpoints mentioned
   - Data formats
   - Authentication/authorization
   - Rate limits

4. **Data Requirements** - Data specifications
   - Data models/entities
   - Data storage requirements
   - Data flow
   - Data validation rules

5. **Infrastructure Requirements** - Infrastructure needs
   - Compute resources
   - Storage requirements
   - Network requirements
   - Cloud services mentioned

6. **Security Specifications** - Security requirements
   - Authentication methods
   - Authorization rules
   - Encryption requirements
   - Compliance requirements

7. **Integration Points** - External integrations
   - Third-party services
   - Integration methods
   - Data exchange formats

8. **Technical Constraints** - Limitations and constraints
   - Technology constraints
   - Resource constraints
   - Compliance constraints
   - Timeline constraints

Return as JSON with keys: system_requirements, technical_architecture, apis_interfaces, data_requirements, infrastructure_requirements, security_specifications, integration_points, technical_constraints

{self._format_kb_results(kb_results) if kb_results else ""}"""

        mime_type = self._get_mime_type(audio_path)
        audio_part = Part.from_data(data=audio_bytes, mime_type=mime_type)

        response = self.model.generate_content([prompt, audio_part])
        analysis_text = response.text

        # Parse specs
        specs = self._parse_json_response(analysis_text)

        return {
            "status": "success",
            "audio_path": audio_path,
            "technical_specs": specs,
            "timestamp": datetime.now().isoformat()
        }

    @A2AIntegration.with_task_tracking
    def identify_speakers(
        self,
        audio_path: str,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Identify and analyze different speakers (speaker diarization).

        Args:
            audio_path: Path to audio file
            task_id: Optional task ID

        Returns:
            Speaker analysis with segments and characteristics
        """
        print(f"[Audio Transcriber] Identifying speakers in: {audio_path}")

        audio_bytes = self._read_audio(audio_path)

        prompt = """Analyze the speakers in this audio and provide speaker diarization:

1. **Number of Speakers** - How many distinct speakers?

2. **Speaker Segments** - Who speaks when
   - Speaker ID (Speaker 1, Speaker 2, etc.)
   - Start time
   - End time
   - Text spoken
   - Topic discussed

3. **Speaker Characteristics** - What can you infer about each speaker?
   - Role/expertise (based on content)
   - Communication style
   - Key topics they focus on
   - Level of participation

4. **Speaker Interactions** - How speakers interact
   - Who responds to whom
   - Agreement/disagreement patterns
   - Questions asked and answered
   - Dominant/passive speakers

5. **Turn-Taking Analysis** - Conversation dynamics
   - Average turn length per speaker
   - Interruptions
   - Who initiates topics
   - Who concludes topics

Return as JSON with keys: num_speakers, speaker_segments, speaker_characteristics, speaker_interactions, turn_taking_analysis"""

        mime_type = self._get_mime_type(audio_path)
        audio_part = Part.from_data(data=audio_bytes, mime_type=mime_type)

        response = self.model.generate_content([prompt, audio_part])
        analysis_text = response.text

        # Parse speaker analysis
        speaker_analysis = self._parse_json_response(analysis_text)

        return {
            "status": "success",
            "audio_path": audio_path,
            "speaker_analysis": speaker_analysis,
            "timestamp": datetime.now().isoformat()
        }

    @A2AIntegration.with_task_tracking
    def analyze_sentiment(
        self,
        audio_path: str,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze sentiment and emotional tone of audio.

        Args:
            audio_path: Path to audio file
            task_id: Optional task ID

        Returns:
            Sentiment analysis with emotional patterns
        """
        print(f"[Audio Transcriber] Analyzing sentiment in: {audio_path}")

        audio_bytes = self._read_audio(audio_path)

        prompt = """Analyze the sentiment and emotional tone of this audio:

1. **Overall Sentiment** - General emotional tone
   - Positive/negative/neutral
   - Confidence level
   - Energy level

2. **Sentiment Timeline** - How sentiment changes over time
   - Timestamp
   - Sentiment at that moment
   - What caused the sentiment
   - Intensity (1-10)

3. **Emotional Patterns** - Recurring emotional themes
   - Frustration moments
   - Excitement moments
   - Confusion/uncertainty
   - Agreement/consensus

4. **Tone Analysis** - Communication tone
   - Formal vs informal
   - Collaborative vs confrontational
   - Confident vs uncertain
   - Urgent vs relaxed

5. **Stress Indicators** - Signs of stress or concern
   - Timestamp
   - Indicator (fast speech, hesitation, etc.)
   - Context
   - Speaker

6. **Positive Moments** - Highlights and wins
   - What was positive
   - Why significant
   - Who was involved

7. **Concerns Raised** - Worries or issues mentioned
   - Concern description
   - Who raised it
   - Severity
   - Resolution status

Return as JSON with keys: overall_sentiment, sentiment_timeline, emotional_patterns, tone_analysis, stress_indicators, positive_moments, concerns_raised"""

        mime_type = self._get_mime_type(audio_path)
        audio_part = Part.from_data(data=audio_bytes, mime_type=mime_type)

        response = self.model.generate_content([prompt, audio_part])
        analysis_text = response.text

        # Parse sentiment
        sentiment = self._parse_json_response(analysis_text)

        return {
            "status": "success",
            "audio_path": audio_path,
            "sentiment_analysis": sentiment,
            "timestamp": datetime.now().isoformat()
        }

    def _get_mime_type(self, audio_path: str) -> str:
        """Determine MIME type from file extension."""
        if audio_path.endswith(".wav"):
            return "audio/wav"
        elif audio_path.endswith(".m4a"):
            return "audio/mp4"
        elif audio_path.endswith(".ogg"):
            return "audio/ogg"
        elif audio_path.endswith(".flac"):
            return "audio/flac"
        else:
            return "audio/mpeg"

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
def transcribe_audio_tool(
    audio_path: str,
    audio_type: str = "meeting",
    extract_items: List[str] = None
) -> Dict[str, Any]:
    """Tool function: Transcribe audio."""
    class MockMessageBus:
        def publish(self, *args, **kwargs):
            pass

    agent = AudioTranscriberAgent(
        context={"project_id": "test", "location": "us-central1"},
        message_bus=MockMessageBus(),
        orchestrator_id="orchestrator"
    )

    return agent.transcribe_audio(
        audio_path=audio_path,
        audio_type=audio_type,
        extract_items=extract_items
    )


def analyze_meeting_tool(audio_path: str) -> Dict[str, Any]:
    """Tool function: Analyze meeting."""
    class MockMessageBus:
        def publish(self, *args, **kwargs):
            pass

    agent = AudioTranscriberAgent(
        context={"project_id": "test", "location": "us-central1"},
        message_bus=MockMessageBus(),
        orchestrator_id="orchestrator"
    )

    return agent.analyze_meeting(audio_path=audio_path)


def create_audio_transcriber_agent(
    project_id: str,
    location: str,
    orchestrator_id: str = None
) -> AudioTranscriberAgent:
    """Factory function to create Audio Transcriber Agent."""
    context = {
        "project_id": project_id,
        "location": location
    }

    class MockMessageBus:
        def publish(self, *args, **kwargs):
            pass

    return AudioTranscriberAgent(
        context=context,
        message_bus=MockMessageBus(),
        orchestrator_id=orchestrator_id or "orchestrator"
    )
