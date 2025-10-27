"""
agents/orchestration/dynamic_orchestrator/task_analyzer.py

Task Analysis Agent - Analyzes tasks from multimodal inputs and extracts requirements.

This agent uses Gemini 2.0 Flash Thinking to:
- Extract required/optional capabilities from natural language descriptions
- Process multimodal inputs (images, PDFs, videos, design files)
- Estimate task complexity and duration
- Identify dependencies between tasks
- Extract non-functional requirements (NFRs)
- Determine KB access requirements
"""

from typing import Dict, List, Set, Optional, Any
from datetime import datetime
import json
import base64
import mimetypes

from vertexai.generative_models import GenerativeModel, Part
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration
from shared.models.task_requirements import (
    TaskRequirements,
    TaskComplexity,
    NFRRequirement,
    NFRType
)
from shared.models.agent_capability import InputModality


class TaskAnalyzer(A2AEnabledAgent):
    """
    Task Analysis Agent for dynamic orchestration.

    Uses Gemini 2.0 Flash Thinking for advanced reasoning about task requirements.
    Supports multimodal inputs to extract comprehensive requirements.
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        model_name: str = "gemini-2.0-flash-thinking-exp-1219",
        multimodal_model_name: str = "gemini-2.0-flash-exp"
    ):
        """
        Initialize Task Analyzer.

        Args:
            context: Agent context (project_id, location, etc.)
            message_bus: A2A message bus for communication
            orchestrator_id: ID of dynamic orchestrator
            model_name: LLM model for reasoning (default: thinking model)
            multimodal_model_name: Model for multimodal processing
        """
        super().__init__(context, message_bus)

        self.context = context
        self.orchestrator_id = orchestrator_id
        self.model_name = model_name
        self.multimodal_model_name = multimodal_model_name

        # Initialize A2A integration
        self.a2a = A2AIntegration(
            context=context,
            message_bus=message_bus,
            orchestrator_id=orchestrator_id
        )

        # Initialize Vertex AI models
        aiplatform.init(
            project=context.get("project_id"),
            location=context.get("location", "us-central1")
        )

        self.reasoning_model = GenerativeModel(model_name)
        self.multimodal_model = GenerativeModel(multimodal_model_name)

        # Analysis history
        self.analysis_history: List[Dict[str, Any]] = []

    def handle_task_assignment(self, message: Dict[str, Any]) -> None:
        """
        Handle TASK_ASSIGNMENT message from orchestrator.

        Expected message payload:
        {
            "task_description": str,
            "input_files": List[Dict],  # [{path, type, modality}, ...]
            "context": Dict,
            "constraints": Dict
        }
        """
        payload = message.get("payload", {})
        task_id = payload.get("task_id")

        try:
            # Extract requirements from multimodal inputs
            requirements = self.analyze_task(
                task_description=payload.get("task_description"),
                input_files=payload.get("input_files", []),
                context=payload.get("context", {}),
                constraints=payload.get("constraints", {})
            )

            # Send completion with extracted requirements
            self.a2a.send_completion(
                task_id=task_id,
                artifacts={
                    "task_requirements": requirements.to_dict(),
                    "analysis_metadata": {
                        "analyzer_id": self.context.get("agent_id"),
                        "model_used": self.model_name,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                },
                metrics={
                    "analysis_duration_seconds": 0,  # TODO: track time
                    "input_files_processed": len(payload.get("input_files", [])),
                    "requirements_extracted": len(requirements.required_capabilities)
                }
            )

        except Exception as e:
            self.a2a.send_error_report(
                task_id=task_id,
                error_type="TASK_ANALYSIS_FAILED",
                error_message=str(e),
                stack_trace=""
            )

    @A2AIntegration.with_task_tracking
    def analyze_task(
        self,
        task_description: str,
        input_files: List[Dict[str, Any]] = None,
        context: Dict[str, Any] = None,
        constraints: Dict[str, Any] = None,
        task_id: Optional[str] = None
    ) -> TaskRequirements:
        """
        Analyze task and extract comprehensive requirements.

        Args:
            task_description: Natural language task description
            input_files: List of input files with metadata
            context: Additional context (project, tech stack, etc.)
            constraints: Constraints (budget, timeline, etc.)
            task_id: Optional task ID for tracking

        Returns:
            TaskRequirements object with extracted requirements
        """
        input_files = input_files or []
        context = context or {}
        constraints = constraints or {}

        # Step 1: Process multimodal inputs
        multimodal_insights = self._process_multimodal_inputs(input_files)

        # Step 2: Extract requirements using reasoning model
        requirements_dict = self._extract_requirements_with_llm(
            task_description=task_description,
            multimodal_insights=multimodal_insights,
            context=context,
            constraints=constraints
        )

        # Step 3: Estimate complexity
        complexity_analysis = self._estimate_complexity(
            task_description=task_description,
            requirements=requirements_dict,
            multimodal_insights=multimodal_insights
        )

        # Step 4: Identify dependencies
        dependencies = self._identify_dependencies(
            requirements=requirements_dict,
            context=context
        )

        # Step 5: Extract NFRs
        nfrs = self._extract_nfrs(
            task_description=task_description,
            requirements=requirements_dict,
            constraints=constraints
        )

        # Step 6: Build TaskRequirements object
        task_requirements = TaskRequirements(
            task_id=task_id or f"task_{datetime.utcnow().timestamp()}",
            description=task_description,
            required_capabilities=set(requirements_dict.get("required_capabilities", [])),
            optional_capabilities=set(requirements_dict.get("optional_capabilities", [])),
            input_modalities=self._detect_modalities(input_files),
            output_types=set(requirements_dict.get("output_types", ["code"])),

            # Technical requirements
            required_languages=requirements_dict.get("languages", []),
            required_frameworks=requirements_dict.get("frameworks", []),
            required_tools=requirements_dict.get("tools", []),

            # Complexity
            estimated_complexity=TaskComplexity[complexity_analysis.get("complexity", "MEDIUM")],
            estimated_lines_of_code=complexity_analysis.get("lines_of_code", 500),
            estimated_duration_hours=complexity_analysis.get("duration_hours", 1.0),
            requires_human_review=complexity_analysis.get("requires_human_review", False),

            # Dependencies
            hard_dependencies=dependencies.get("hard", []),
            soft_dependencies=dependencies.get("soft", []),
            parallel_safe=dependencies.get("parallel_safe", True),

            # KB requirements
            requires_kb_access=requirements_dict.get("requires_kb_access", True),
            expected_kb_queries=requirements_dict.get("expected_kb_queries", 5),
            kb_query_types=requirements_dict.get("kb_query_types", ["similar_implementations"]),

            # NFRs
            nfr_requirements=nfrs,
            performance_targets=requirements_dict.get("performance_targets", {}),
            security_requirements=requirements_dict.get("security_requirements", []),
            compliance_requirements=requirements_dict.get("compliance_requirements", []),

            # Metadata
            additional_context=context,
            constraints=constraints
        )

        # Store in history
        self.analysis_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": task_requirements.task_id,
            "requirements": task_requirements.to_dict()
        })

        return task_requirements

    def _process_multimodal_inputs(self, input_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process multimodal inputs (images, PDFs, videos, etc.) to extract insights.

        Args:
            input_files: List of file metadata [{path, type, modality}, ...]

        Returns:
            Dictionary with extracted insights from each modality
        """
        insights = {
            "images": [],
            "pdfs": [],
            "videos": [],
            "design_files": [],
            "diagrams": [],
            "text_summaries": []
        }

        for file_info in input_files:
            file_path = file_info.get("path")
            modality = file_info.get("modality", InputModality.TEXT)

            try:
                if modality in [InputModality.IMAGE, InputModality.DIAGRAM]:
                    insight = self._analyze_image(file_path, file_info)
                    insights["images"].append(insight)

                elif modality == InputModality.PDF:
                    insight = self._analyze_pdf(file_path, file_info)
                    insights["pdfs"].append(insight)

                elif modality == InputModality.VIDEO:
                    insight = self._analyze_video(file_path, file_info)
                    insights["videos"].append(insight)

                elif modality == InputModality.DESIGN_FILE:
                    insight = self._analyze_design_file(file_path, file_info)
                    insights["design_files"].append(insight)

            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")

        return insights

    def _analyze_image(self, file_path: str, file_info: Dict) -> Dict[str, Any]:
        """Analyze image using multimodal model."""
        try:
            with open(file_path, "rb") as f:
                image_bytes = f.read()

            mime_type = file_info.get("mime_type") or mimetypes.guess_type(file_path)[0] or "image/jpeg"

            image_part = Part.from_data(data=image_bytes, mime_type=mime_type)

            prompt = """
            Analyze this image and extract:
            1. UI/UX components visible
            2. Design patterns used
            3. Technical requirements implied
            4. Functionality suggested
            5. Technologies that might be needed

            Return as structured JSON.
            """

            response = self.multimodal_model.generate_content([prompt, image_part])

            return {
                "file_path": file_path,
                "analysis": response.text,
                "type": "image"
            }

        except Exception as e:
            return {"file_path": file_path, "error": str(e)}

    def _analyze_pdf(self, file_path: str, file_info: Dict) -> Dict[str, Any]:
        """Analyze PDF document."""
        try:
            # For PDFs, we can use Gemini's PDF support
            with open(file_path, "rb") as f:
                pdf_bytes = f.read()

            pdf_part = Part.from_data(data=pdf_bytes, mime_type="application/pdf")

            prompt = """
            Analyze this PDF document and extract:
            1. Requirements mentioned
            2. Technical specifications
            3. Dependencies identified
            4. Constraints and NFRs
            5. Success criteria

            Return as structured JSON.
            """

            response = self.multimodal_model.generate_content([prompt, pdf_part])

            return {
                "file_path": file_path,
                "analysis": response.text,
                "type": "pdf"
            }

        except Exception as e:
            return {"file_path": file_path, "error": str(e)}

    def _analyze_video(self, file_path: str, file_info: Dict) -> Dict[str, Any]:
        """Analyze video file."""
        # TODO: Implement video analysis using Gemini 2.0 Flash video support
        return {
            "file_path": file_path,
            "analysis": "Video analysis not yet implemented",
            "type": "video"
        }

    def _analyze_design_file(self, file_path: str, file_info: Dict) -> Dict[str, Any]:
        """Analyze design file (Figma, Sketch, etc.)."""
        # TODO: Implement design file analysis
        return {
            "file_path": file_path,
            "analysis": "Design file analysis not yet implemented",
            "type": "design_file"
        }

    def _extract_requirements_with_llm(
        self,
        task_description: str,
        multimodal_insights: Dict[str, Any],
        context: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use reasoning model to extract comprehensive requirements.
        """
        # Build comprehensive prompt
        prompt = f"""
        Analyze the following software development task and extract detailed requirements.

        TASK DESCRIPTION:
        {task_description}

        MULTIMODAL INSIGHTS:
        {json.dumps(multimodal_insights, indent=2)}

        PROJECT CONTEXT:
        {json.dumps(context, indent=2)}

        CONSTRAINTS:
        {json.dumps(constraints, indent=2)}

        Extract the following information and return as JSON:

        {{
            "required_capabilities": ["capability1", "capability2"],  // MUST-HAVE capabilities
            "optional_capabilities": ["capability3"],  // NICE-TO-HAVE capabilities
            "languages": ["python", "javascript"],
            "frameworks": ["react", "fastapi"],
            "tools": ["docker", "pytest"],
            "output_types": ["code", "documentation", "tests"],
            "requires_kb_access": true,
            "expected_kb_queries": 5,
            "kb_query_types": ["similar_implementations", "best_practices"],
            "performance_targets": {{"response_time_ms": 200}},
            "security_requirements": ["authentication", "input_validation"],
            "compliance_requirements": []
        }}

        Be specific and comprehensive. Consider:
        - What agents/capabilities are needed? (e.g., "react_development", "api_development")
        - What technologies are implied by the task?
        - What KB queries would help? (similar code, best practices, error solutions)
        - What performance/security requirements exist?
        """

        try:
            response = self.reasoning_model.generate_content(prompt)

            # Extract JSON from response
            response_text = response.text

            # Try to find JSON in response
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text.strip()

            requirements = json.loads(json_str)
            return requirements

        except Exception as e:
            print(f"Error extracting requirements with LLM: {str(e)}")
            # Return default structure
            return {
                "required_capabilities": ["development"],
                "optional_capabilities": [],
                "languages": [],
                "frameworks": [],
                "tools": [],
                "output_types": ["code"],
                "requires_kb_access": True,
                "expected_kb_queries": 5,
                "kb_query_types": ["similar_implementations"]
            }

    def _estimate_complexity(
        self,
        task_description: str,
        requirements: Dict[str, Any],
        multimodal_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Estimate task complexity using LLM reasoning.
        """
        prompt = f"""
        Estimate the complexity of this software development task:

        TASK: {task_description}

        REQUIREMENTS: {json.dumps(requirements, indent=2)}

        Return JSON with:
        {{
            "complexity": "TRIVIAL|LOW|MEDIUM|HIGH|VERY_HIGH",
            "lines_of_code": 500,
            "duration_hours": 2.0,
            "requires_human_review": false,
            "reasoning": "Explanation of complexity assessment"
        }}

        Consider:
        - Number of capabilities required
        - Integration points
        - Technical difficulty
        - Testing requirements
        """

        try:
            response = self.reasoning_model.generate_content(prompt)
            response_text = response.text

            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text.strip()

            return json.loads(json_str)

        except Exception as e:
            print(f"Error estimating complexity: {str(e)}")
            return {
                "complexity": "MEDIUM",
                "lines_of_code": 500,
                "duration_hours": 1.0,
                "requires_human_review": False
            }

    def _identify_dependencies(
        self,
        requirements: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Identify task dependencies.
        """
        # TODO: Implement smart dependency detection
        # For now, return empty dependencies
        return {
            "hard": [],  # Must complete before this task
            "soft": [],  # Should complete before, but not required
            "parallel_safe": True
        }

    def _extract_nfrs(
        self,
        task_description: str,
        requirements: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> List[NFRRequirement]:
        """
        Extract non-functional requirements.
        """
        nfrs = []

        # Performance NFRs
        if requirements.get("performance_targets"):
            for metric, target in requirements["performance_targets"].items():
                nfrs.append(NFRRequirement(
                    nfr_type=NFRType.PERFORMANCE,
                    description=f"{metric}: {target}",
                    metric_name=metric,
                    target_value=target,
                    priority="high"
                ))

        # Security NFRs
        for sec_req in requirements.get("security_requirements", []):
            nfrs.append(NFRRequirement(
                nfr_type=NFRType.SECURITY,
                description=sec_req,
                priority="high"
            ))

        # Compliance NFRs
        for comp_req in requirements.get("compliance_requirements", []):
            nfrs.append(NFRRequirement(
                nfr_type=NFRType.COMPLIANCE,
                description=comp_req,
                priority="medium"
            ))

        return nfrs

    def _detect_modalities(self, input_files: List[Dict[str, Any]]) -> Set[InputModality]:
        """Detect input modalities from file list."""
        modalities = {InputModality.TEXT}  # Always includes text (task description)

        for file_info in input_files:
            modality = file_info.get("modality")
            if modality:
                modalities.add(modality)

        return modalities

    def get_analysis_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent analysis history."""
        return self.analysis_history[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """Get analyzer statistics."""
        return {
            "total_analyses": len(self.analysis_history),
            "model_used": self.model_name,
            "multimodal_model": self.multimodal_model_name
        }


# Tool functions for Vertex AI Reasoning Engine deployment
def analyze_task_tool(
    task_description: str,
    input_files: List[Dict[str, Any]] = None,
    context: Dict[str, Any] = None,
    constraints: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Tool function: Analyze task and extract requirements.

    This is the main entry point when deployed as Vertex AI Reasoning Engine.
    """
    # This will be injected with actual context during deployment
    analyzer = TaskAnalyzer(
        context={},  # Filled by deployment script
        message_bus=None,  # Filled by deployment script
        orchestrator_id=""  # Filled by deployment script
    )

    requirements = analyzer.analyze_task(
        task_description=task_description,
        input_files=input_files,
        context=context,
        constraints=constraints
    )

    return {
        "status": "success",
        "task_requirements": requirements.to_dict(),
        "metadata": analyzer.get_stats()
    }
