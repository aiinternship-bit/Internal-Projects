"""
agents/multimodal/pdf_parser/agent.py

PDF Parser Agent - Extracts requirements, specifications, and documentation from PDFs.

This agent uses Gemini 2.0 Flash Exp to:
- Extract text and structure from PDFs
- Identify requirements and specifications
- Parse technical documentation
- Extract diagrams and tables
- Identify dependencies and constraints
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from vertexai.generative_models import GenerativeModel, Part
from google.cloud import aiplatform

from shared.utils.agent_base import A2AEnabledAgent
from shared.utils.a2a_integration import A2AIntegration
from shared.models.agent_capability import InputModality


class PDFParserAgent(A2AEnabledAgent):
    """
    PDF Parser Agent for extracting requirements and specifications from documents.

    Uses Gemini 2.0 Flash Exp for PDF processing and information extraction.
    """

    def __init__(
        self,
        context: Dict[str, Any],
        message_bus,
        orchestrator_id: str,
        model_name: str = "gemini-2.0-flash-exp"
    ):
        """
        Initialize PDF Parser Agent.

        Args:
            context: Agent context
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

        # Parsing history
        self.parsing_history: List[Dict[str, Any]] = []

    def handle_task_assignment(self, message: Dict[str, Any]) -> None:
        """Handle TASK_ASSIGNMENT message from orchestrator."""
        payload = message.get("payload", {})
        task_id = payload.get("task_id")

        try:
            result = self.parse_pdf(
                pdf_path=payload.get("pdf_path"),
                document_type=payload.get("document_type", "requirements"),
                extraction_focus=payload.get("extraction_focus", []),
                task_id=task_id
            )

            self.a2a.send_completion(
                task_id=task_id,
                artifacts=result,
                metrics={
                    "parsing_duration_seconds": result.get("duration_seconds", 0),
                    "pages_processed": result.get("pages_processed", 0)
                }
            )

        except Exception as e:
            self.a2a.send_error_report(
                task_id=task_id,
                error_type="PDF_PARSING_FAILED",
                error_message=str(e),
                stack_trace=""
            )

    @A2AIntegration.with_task_tracking
    def parse_pdf(
        self,
        pdf_path: str,
        document_type: str = "requirements",
        extraction_focus: List[str] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Parse a PDF document and extract relevant information.

        Args:
            pdf_path: Path to PDF file
            document_type: Type of document (requirements, specification, documentation, etc.)
            extraction_focus: What to focus on (requirements, apis, nfrs, etc.)
            task_id: Optional task ID

        Returns:
            {
                "document_type": str,
                "pages_processed": int,
                "requirements": List[Dict],
                "technical_specs": Dict,
                "apis": List[Dict],
                "nfrs": List[Dict],
                "diagrams_mentioned": List[str],
                "dependencies": List[str],
                "constraints": List[str],
                "metadata": Dict,
                "raw_text": str
            }
        """
        extraction_focus = extraction_focus or ["requirements", "technical_specs"]
        start_time = datetime.utcnow()

        print(f"[PDF Parser] Parsing {document_type}: {pdf_path}")

        # Read PDF file
        pdf_bytes = self._read_pdf(pdf_path)

        # Generate parsing prompt
        prompt = self._get_parsing_prompt(document_type, extraction_focus)

        # Parse with model
        parsed_content = self._parse_with_model(pdf_bytes, pdf_path, prompt)

        # Structure the results
        structured_result = self._structure_results(parsed_content, document_type)

        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()

        result = {
            "document_type": document_type,
            "pdf_path": pdf_path,
            "duration_seconds": duration,
            "timestamp": datetime.utcnow().isoformat(),
            **structured_result
        }

        # Store in history
        self.parsing_history.append({
            "task_id": task_id,
            "timestamp": result["timestamp"],
            "document_type": document_type,
            "pdf_path": pdf_path
        })

        return result

    def _read_pdf(self, pdf_path: str) -> bytes:
        """Read PDF file as bytes."""
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        with open(pdf_path, "rb") as f:
            return f.read()

    def _get_parsing_prompt(self, document_type: str, extraction_focus: List[str]) -> str:
        """Generate parsing prompt based on document type."""
        focus_str = ", ".join(extraction_focus)

        prompts = {
            "requirements": f"""
Analyze this requirements document and extract:

1. **Functional Requirements** - What the system must do
   - Feature descriptions
   - User stories
   - Acceptance criteria

2. **Non-Functional Requirements (NFRs)**
   - Performance requirements (response times, throughput)
   - Security requirements (authentication, authorization, encryption)
   - Scalability requirements
   - Reliability/availability requirements
   - Compliance requirements

3. **Technical Specifications**
   - Preferred technologies
   - Integration requirements
   - Data requirements

4. **Constraints**
   - Budget constraints
   - Timeline constraints
   - Technical constraints
   - Resource constraints

5. **Dependencies**
   - External systems
   - Third-party services
   - Prerequisites

6. **Success Criteria**
   - Measurable goals
   - KPIs

Focus on: {focus_str}

Return as structured JSON with keys: functional_requirements, nfrs, technical_specs, constraints, dependencies, success_criteria
""",

            "specification": f"""
Analyze this technical specification document and extract:

1. **System Architecture**
   - Components and their responsibilities
   - Communication patterns
   - Data flow

2. **API Specifications**
   - Endpoints
   - Request/response formats
   - Authentication methods

3. **Data Models**
   - Entities and relationships
   - Database schema
   - Data validation rules

4. **Technology Stack**
   - Languages and frameworks
   - Libraries and tools
   - Infrastructure requirements

5. **Security Specifications**
   - Authentication mechanisms
   - Authorization rules
   - Encryption standards

6. **Performance Specifications**
   - Response time requirements
   - Throughput requirements
   - Scalability targets

Focus on: {focus_str}

Return as structured JSON.
""",

            "documentation": f"""
Analyze this documentation and extract:

1. **Overview**
   - System purpose
   - Key features
   - Architecture summary

2. **Setup Instructions**
   - Prerequisites
   - Installation steps
   - Configuration

3. **API Documentation**
   - Available endpoints
   - Parameters
   - Examples

4. **Usage Examples**
   - Common use cases
   - Code snippets

5. **Troubleshooting**
   - Common issues
   - Solutions

6. **Technical Details**
   - Implementation notes
   - Best practices
   - Limitations

Focus on: {focus_str}

Return as structured JSON.
""",

            "design_doc": f"""
Analyze this design document and extract:

1. **Design Goals**
   - Objectives
   - Success metrics

2. **Design Decisions**
   - Choices made
   - Rationale
   - Alternatives considered

3. **System Design**
   - Components
   - Interfaces
   - Data flow

4. **UI/UX Design**
   - User flows
   - Screen layouts
   - Interaction patterns

5. **Implementation Plan**
   - Phases
   - Milestones
   - Timeline

6. **Risks and Mitigations**
   - Identified risks
   - Mitigation strategies

Focus on: {focus_str}

Return as structured JSON.
"""
        }

        return prompts.get(document_type, prompts["requirements"])

    def _parse_with_model(self, pdf_bytes: bytes, pdf_path: str, prompt: str) -> str:
        """Parse PDF with Gemini model."""
        try:
            # Create PDF part
            pdf_part = Part.from_data(data=pdf_bytes, mime_type="application/pdf")

            # Generate analysis
            response = self.model.generate_content([prompt, pdf_part])

            return response.text

        except Exception as e:
            raise RuntimeError(f"PDF parsing failed: {str(e)}")

    def _structure_results(self, parsed_content: str, document_type: str) -> Dict[str, Any]:
        """Structure the parsed content into standard format."""
        import json
        import re

        result = {
            "pages_processed": 0,  # TODO: Extract page count
            "requirements": [],
            "technical_specs": {},
            "apis": [],
            "nfrs": [],
            "diagrams_mentioned": [],
            "dependencies": [],
            "constraints": [],
            "metadata": {},
            "raw_text": parsed_content
        }

        # Try to extract JSON
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', parsed_content, re.DOTALL)
        if not json_match:
            json_match = re.search(r'(\{.*\})', parsed_content, re.DOTALL)

        if json_match:
            try:
                parsed = json.loads(json_match.group(1))

                # Map parsed fields to standard structure
                if "functional_requirements" in parsed:
                    result["requirements"] = parsed["functional_requirements"]

                if "nfrs" in parsed:
                    result["nfrs"] = parsed["nfrs"]

                if "technical_specs" in parsed:
                    result["technical_specs"] = parsed["technical_specs"]

                if "dependencies" in parsed:
                    result["dependencies"] = parsed["dependencies"]

                if "constraints" in parsed:
                    result["constraints"] = parsed["constraints"]

                if "apis" in parsed or "api_specifications" in parsed:
                    result["apis"] = parsed.get("apis", parsed.get("api_specifications", []))

            except json.JSONDecodeError:
                pass

        return result

    def extract_requirements_only(
        self,
        pdf_path: str
    ) -> List[Dict[str, Any]]:
        """
        Quick extraction of just the requirements.

        Args:
            pdf_path: Path to PDF

        Returns:
            List of requirements with metadata
        """
        result = self.parse_pdf(
            pdf_path=pdf_path,
            document_type="requirements",
            extraction_focus=["functional_requirements"]
        )

        return result.get("requirements", [])

    def extract_apis(
        self,
        pdf_path: str
    ) -> List[Dict[str, Any]]:
        """
        Extract API specifications from document.

        Args:
            pdf_path: Path to PDF

        Returns:
            List of API specifications
        """
        result = self.parse_pdf(
            pdf_path=pdf_path,
            document_type="specification",
            extraction_focus=["apis"]
        )

        return result.get("apis", [])

    def get_parsing_stats(self) -> Dict[str, Any]:
        """Get PDF parser statistics."""
        if not self.parsing_history:
            return {"total_parses": 0}

        doc_types = {}
        for record in self.parsing_history:
            dtype = record.get("document_type", "unknown")
            doc_types[dtype] = doc_types.get(dtype, 0) + 1

        return {
            "total_parses": len(self.parsing_history),
            "document_types": doc_types,
            "model_used": self.model_name
        }


# Tool functions
def parse_pdf_tool(
    pdf_path: str,
    document_type: str = "requirements",
    extraction_focus: List[str] = None
) -> Dict[str, Any]:
    """
    Tool function: Parse a PDF document.
    """
    agent = PDFParserAgent(
        context={},
        message_bus=None,
        orchestrator_id=""
    )

    return agent.parse_pdf(
        pdf_path=pdf_path,
        document_type=document_type,
        extraction_focus=extraction_focus
    )


def extract_requirements_tool(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Tool function: Extract requirements from PDF.
    """
    agent = PDFParserAgent(
        context={},
        message_bus=None,
        orchestrator_id=""
    )

    return agent.extract_requirements_only(pdf_path)
