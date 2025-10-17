"""
LLM Integration Layer
Handles LLM-based answer generation from retrieved context
"""
import time
from typing import Dict, Any, Optional
from . import config

# Import tracer (will be None if not enabled)
try:
    from .langsmith_integration import get_tracer
    _tracer_available = True
except ImportError:
    _tracer_available = False
    def get_tracer():
        return None


class LLMLayer:
    """
    Interface for LLM-based answer generation
    Supports multiple LLM backends (OpenAI, local models, etc.)
    Includes LangSmith tracing for diagnostics
    """

    def __init__(
        self,
        model_name: str = config.LLM_MODEL,
        temperature: float = config.TEMPERATURE,
        max_tokens: int = config.MAX_TOKENS,
        enable_tracing: bool = True
    ):
        """
        Initialize LLM layer

        Args:
            model_name: Name of the LLM model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            enable_tracing: Enable LangSmith tracing
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.backend = self._detect_backend()
        self.enable_tracing = enable_tracing and _tracer_available
        self.tracer = get_tracer() if self.enable_tracing else None

    def _detect_backend(self) -> str:
        """
        Detect which LLM backend to use based on model name

        Priority: ollama → openai → anthropic → mock

        Returns:
            Backend type: 'ollama', 'openai', 'anthropic', 'local', or 'mock'
        """
        model_lower = self.model_name.lower()

        # Check for Ollama first (highest priority)
        if model_lower == "ollama" or config.is_ollama_configured():
            if model_lower == "ollama" or config.is_ollama_configured():
                return "ollama"

        # Then check specific model types
        if "gpt" in model_lower:
            return "openai"
        elif "claude" in model_lower:
            return "anthropic"
        elif "mock" in model_lower:
            return "mock"
        else:
            return "local"

    def generate_answer(
        self,
        context: str,
        query: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate answer from context and query

        Args:
            context: Retrieved context from query engine
            query: User's original question
            system_prompt: Optional custom system prompt

        Returns:
            Dictionary with 'answer', 'model', and 'token_usage'
        """
        start_time = time.time()

        # Default system prompt
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt()

        # Build prompt
        full_prompt = self._build_prompt(system_prompt, context, query)

        # Route to appropriate backend
        try:
            if self.backend == "ollama":
                result = self._generate_ollama(full_prompt, system_prompt)
            elif self.backend == "openai":
                result = self._generate_openai(full_prompt, system_prompt)
            elif self.backend == "anthropic":
                result = self._generate_anthropic(full_prompt, system_prompt)
            elif self.backend == "mock":
                result = self._generate_mock(full_prompt, context, query)
            else:
                result = self._generate_local(full_prompt)

            # Trace LLM call if enabled
            if self.enable_tracing and self.tracer:
                execution_time = time.time() - start_time
                self.tracer.trace_llm_call(
                    prompt=full_prompt,
                    response=result.get("answer", ""),
                    model=result.get("model", self.model_name),
                    token_usage=result.get("token_usage", 0),
                    execution_time=execution_time
                )

            return result

        except Exception as e:
            # Log error if tracing enabled
            if self.enable_tracing and self.tracer:
                self.tracer.log_error("llm_generation", e, {"query": query})
            raise

    def _get_default_system_prompt(self) -> str:
        """Get default system prompt for Excel analyst"""
        return """You are an expert data analyst with access to an Excel database.

Your task is to answer user questions based ONLY on the provided context from the Excel data.

Guidelines:
1. Answer concisely and accurately based on the retrieved data
2. If the context doesn't contain enough information, say so explicitly
3. Cite specific sheets or data points when possible
4. If you see relevant patterns or insights, mention them
5. Format your answer in a clear, human-readable way

Do not make up information not present in the context."""

    def _build_prompt(self, system_prompt: str, context: str, query: str) -> str:
        """Build complete prompt from components"""
        return f"""{system_prompt}

{context}

Please answer the following question based on the information above:
{query}

Answer:"""

    def _generate_ollama(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        """
        Generate answer using Ollama (local LLM server)

        Note: Requires Ollama to be running: ollama serve
        """
        try:
            import requests

            # Use configured model from .env
            model = config.OLLAMA_MODEL
            base_url = config.OLLAMA_BASE_URL

            if not base_url:
                return {
                    "answer": "Ollama not configured. Set OLLAMA_BASE_URL in .env file",
                    "model": "ollama",
                    "token_usage": 0,
                    "backend": "error"
                }

            # Ollama API endpoint
            url = f"{base_url}/api/generate"

            # Combine system prompt and user prompt
            full_prompt = f"{system_prompt}\n\n{prompt}"

            payload = {
                "model": model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            }

            # Make request with timeout
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()

            result = response.json()

            # Extract answer and approximate token count
            answer = result.get("response", "")
            # Ollama doesn't return token count, estimate it
            token_count = len(answer.split()) + len(full_prompt.split())

            return {
                "answer": answer,
                "model": f"ollama/{model}",
                "token_usage": token_count,
                "backend": "ollama"
            }

        except requests.exceptions.ConnectionError:
            return {
                "answer": f"Cannot connect to Ollama at {config.OLLAMA_BASE_URL}. Is Ollama running? (ollama serve)",
                "model": "ollama",
                "token_usage": 0,
                "backend": "error"
            }
        except requests.exceptions.Timeout:
            return {
                "answer": "Ollama request timed out. Try a smaller query or increase timeout.",
                "model": "ollama",
                "token_usage": 0,
                "backend": "error"
            }
        except Exception as e:
            return {
                "answer": f"Error calling Ollama API: {str(e)}",
                "model": "ollama",
                "token_usage": 0,
                "backend": "error"
            }

    def _generate_openai(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        """
        Generate answer using OpenAI API (openai>=1.0.0)

        Note: Requires openai package and API key to be installed
        """
        try:
            from openai import OpenAI

            if not config.OPENAI_API_KEY:
                return {
                    "answer": "OpenAI API key not set. Please set OPENAI_API_KEY in .env file",
                    "model": self.model_name,
                    "token_usage": 0,
                    "backend": "error"
                }

            # Initialize client with API key
            client = OpenAI(api_key=config.OPENAI_API_KEY)

            # Make API call using new SDK
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            return {
                "answer": response.choices[0].message.content,
                "model": self.model_name,
                "token_usage": response.usage.total_tokens,
                "backend": "openai"
            }

        except ImportError:
            return {
                "answer": "OpenAI package not installed. Please: pip install openai",
                "model": self.model_name,
                "token_usage": 0,
                "backend": "error"
            }
        except Exception as e:
            return {
                "answer": f"Error calling OpenAI API: {str(e)}",
                "model": self.model_name,
                "token_usage": 0,
                "backend": "error"
            }

    def _generate_anthropic(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        """
        Generate answer using Anthropic Claude API

        Note: Requires anthropic package and API key to be installed
        """
        try:
            import anthropic

            if not config.ANTHROPIC_API_KEY:
                return {
                    "answer": "Anthropic API key not set. Please set ANTHROPIC_API_KEY in .env file",
                    "model": self.model_name,
                    "token_usage": 0,
                    "backend": "error"
                }

            client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

            response = client.messages.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return {
                "answer": response.content[0].text,
                "model": self.model_name,
                "token_usage": response.usage.input_tokens + response.usage.output_tokens,
                "backend": "anthropic"
            }

        except ImportError:
            return {
                "answer": "Anthropic package not installed. Please: pip install anthropic",
                "model": self.model_name,
                "token_usage": 0,
                "backend": "error"
            }
        except Exception as e:
            return {
                "answer": f"Error calling Anthropic API: {str(e)}",
                "model": self.model_name,
                "token_usage": 0,
                "backend": "error"
            }

    def _generate_local(self, prompt: str) -> Dict[str, Any]:
        """
        Generate answer using local model (placeholder for future implementation)
        """
        return {
            "answer": "Local model support not yet implemented. Use 'mock' model for testing.",
            "model": self.model_name,
            "token_usage": 0,
            "backend": "local"
        }

    def _generate_mock(self, prompt: str, context: str, query: str) -> Dict[str, Any]:
        """
        Generate mock answer for testing without LLM API

        This creates a structured response based on the retrieved context
        """
        # Simple mock: just format the context nicely
        answer_parts = [
            f"Based on the retrieved Excel data, here's what I found regarding: '{query}'\n"
        ]

        # Count structure and content results
        structure_count = context.count("Sheet:")
        content_count = context.count("Relevance:")

        answer_parts.append(f"Retrieved {structure_count} relevant sheets and {content_count} data rows.\n")
        answer_parts.append("The most relevant information is shown above in the context.")
        answer_parts.append("\n[Note: This is a mock response. Configure a real LLM for detailed answers.]")

        return {
            "answer": "\n".join(answer_parts),
            "model": "mock",
            "token_usage": len(prompt.split()) + len(" ".join(answer_parts).split()),
            "backend": "mock"
        }

    def estimate_tokens(self, text: str) -> int:
        """
        Rough token count estimation (1 token ≈ 0.75 words)

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        words = len(text.split())
        return int(words / 0.75)
