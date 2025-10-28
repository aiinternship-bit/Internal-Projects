"""
agents/multimodal/audio_transcriber/agent.py

Audio Transcriber Agent - Transcribes and analyzes audio content.

Uses Gemini 2.0 Flash Exp for audio transcription and analysis to:
- Transcribe meetings and discussions
- Extract requirements from verbal descriptions
- Identify action items and decisions
- Analyze technical discussions
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from vertexai.generative_models import GenerativeModel, Part
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration


class AudioTranscriberAgent(A2AEnabledAgent):
    """
    Audio Transcriber Agent for transcribing and analyzing audio.

    Uses Gemini 2.0 Flash Exp for audio processing.
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        model_name: str = "gemini-2.0-flash-exp"
    ):
        """Initialize Audio Transcriber Agent."""
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
        import json
        import re

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


# Tool function
def transcribe_audio_tool(
    audio_path: str,
    audio_type: str = "meeting",
    extract_items: List[str] = None
) -> Dict[str, Any]:
    """Tool function: Transcribe audio."""
    agent = AudioTranscriberAgent(
        context={},
        message_bus=None,
        orchestrator_id=""
    )

    return agent.transcribe_audio(
        audio_path=audio_path,
        audio_type=audio_type,
        extract_items=extract_items
    )
