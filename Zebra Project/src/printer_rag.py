"""
RAG-based Printer Recommendation System
Answers questions like "Given these requirements, what printer should I choose?"
"""

import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import re
import os
import anthropic
import ollama
import time
from dotenv import load_dotenv

load_dotenv()

class PrinterRAG:
    """
    RAG system for printer recommendations.
    Combines semantic search with requirement filtering.
    """

    def __init__(
        self,
        db_path: str = "./chroma_db",
        collection_name: str = "printer_specs",
        use_llm: bool = True,
        llm_provider: str = "claude",
        anthropic_api_key: Optional[str] = None,
        ollama_model: str = "llama3.2:1b"
    ):
        """
        Initialize RAG system.

        Args:
            db_path: Path to ChromaDB storage directory
            collection_name: Name of the collection to query
            use_llm: Whether to use LLM for enhanced responses (default: True)
            llm_provider: LLM provider to use - 'claude' or 'ollama' (default: 'claude')
            anthropic_api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            ollama_model: Ollama model name (default: 'llama3.2:1b')
        """
        self.db_path = db_path
        self.collection_name = collection_name
        self.use_llm = use_llm
        self.llm_provider = llm_provider.lower()
        self.ollama_model = ollama_model

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=db_path)

        # Use same embedding function as ingestion
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        # Get collection
        try:
            self.collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            print(f"Connected to collection '{collection_name}' ({self.collection.count()} documents)")
        except Exception as e:
            print(f"Error: Collection '{collection_name}' not found. Please run ingestion first.")
            raise

        # Initialize LLM client based on provider
        self.anthropic_client = None
        self.ollama_client = None

        if self.use_llm:
            if self.llm_provider == "claude":
                api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
                if api_key:
                    self.anthropic_client = anthropic.Anthropic(api_key=api_key)
                    print("LLM-enhanced responses enabled (Claude)")
                else:
                    print("Warning: ANTHROPIC_API_KEY not found. Falling back to basic responses.")
                    self.use_llm = False
            elif self.llm_provider == "ollama":
                # Ollama client doesn't require initialization, just verify it's accessible
                try:
                    # Test if Ollama is available
                    ollama.list()
                    print(f"LLM-enhanced responses enabled (Ollama - {self.ollama_model})")
                except Exception as e:
                    print(f"Warning: Ollama not accessible. Falling back to basic responses. Error: {e}")
                    self.use_llm = False
            else:
                print(f"Warning: Unknown LLM provider '{self.llm_provider}'. Falling back to basic responses.")
                self.use_llm = False

    def recommend_printer(
        self,
        requirements: str,
        filters: Optional[Dict[str, Any]] = None,
        n_results: int = 10
    ) -> Dict[str, Any]:
        """
        Recommend printers based on natural language requirements.

        Args:
            requirements: Natural language description of needs
                         e.g., "I need a desktop printer for retail that prints fast"
            filters: Optional metadata filters
                    e.g., {"has_usb": True, "energy_star": True}
            n_results: Number of results to return

        Returns:
            Dictionary with recommendations and reasoning
        """
        print(f"\nAnalyzing requirements: '{requirements}'")

        # Extract structured requirements from natural language
        auto_filters = self._extract_filters_from_query(requirements)

        # Merge with provided filters
        if filters:
            auto_filters.update(filters)

        print(f"Detected filters: {auto_filters}")

        # Build where clause for ChromaDB
        where_clause = None
        if auto_filters:
            where_clause = self._build_where_clause(auto_filters)

        #Time Vector Search
        start = time.perf_counter()
        # Query vector database
        results = self.collection.query(
            query_texts=[requirements],
            n_results=n_results * 2,  # Get more results to account for filtering
            where=where_clause
        )

        # Process and rank results
        recommendations = self._process_results(results, requirements, 20)
        end = time.perf_counter()
        print(f"Vector search and processing took {end - start:.2f} seconds")

        response = {
            "query": requirements,
            "detected_filters": auto_filters,
            "recommendations": recommendations
        }

        LLM_start = time.perf_counter()
        # Generate LLM-enhanced response if enabled
        if self.use_llm and recommendations:
            response["llm_response"] = self._generate_llm_response(requirements, recommendations)
        LLM_end = time.perf_counter()
        print(f"LLM response generation took {LLM_end - LLM_start:.2f} seconds")
        return response

    def _extract_filters_from_query(self, query: str) -> Dict[str, Any]:
        """
        Extract structured filters from natural language query.

        Args:
            query: Natural language query

        Returns:
            Dictionary of filters
        """
        filters = {}
        query_lower = query.lower()

        # Category detection
        if any(word in query_lower for word in ["desktop", "desk", "office"]):
            filters["category"] = "desktop"
        elif any(word in query_lower for word in ["mobile", "portable", "handheld"]):
            filters["category"] = "mobile"
        elif any(word in query_lower for word in ["industrial", "warehouse", "rugged"]):
            filters["category"] = "industrial"

        # Connectivity detection
        if "usb" in query_lower:
            filters["has_usb"] = True
        if any(word in query_lower for word in ["ethernet", "wired network", "lan"]):
            filters["has_ethernet"] = True
        if any(word in query_lower for word in ["wifi", "wi-fi", "wireless"]):
            filters["has_wifi"] = True
        if "bluetooth" in query_lower:
            filters["has_bluetooth"] = True

        # Energy Star
        if any(word in query_lower for word in ["energy star", "energy efficient", "energy-efficient"]):
            filters["energy_star"] = True

        return filters

    def _build_where_clause(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build ChromaDB where clause from filters.

        Args:
            filters: Filter dictionary

        Returns:
            ChromaDB where clause
        """
        if not filters:
            return None

        # For multiple conditions, use $and
        conditions = []

        for key, value in filters.items():
            conditions.append({key: value})

        if len(conditions) == 1:
            return conditions[0]
        else:
            return {"$and": conditions}

    def _process_results(
        self,
        results: Dict[str, Any],
        query: str,
        n_results: int
    ) -> List[Dict[str, Any]]:
        """
        Process and deduplicate results by printer model.

        Args:
            results: Raw results from ChromaDB
            query: Original query
            n_results: Number of final results to return

        Returns:
            List of processed recommendations
        """
        if not results or not results.get('documents'):
            return []

        # Group results by printer model
        model_results = {}

        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            model = metadata.get('model', 'UNKNOWN')

            if model not in model_results:
                model_results[model] = {
                    "model": model,
                    "category": metadata.get('category', 'unknown'),
                    "relevance_score": 1.0 - distance,  # Convert distance to similarity
                    "matching_chunks": [],
                    "key_specs": {},
                    "metadata": metadata
                }

            # Add chunk information
            model_results[model]["matching_chunks"].append({
                "chunk_type": metadata.get('chunk_type', 'unknown'),
                "content": doc,
                "distance": distance
            })

            # Extract key specs from metadata
            if metadata.get('resolution_dpi'):
                model_results[model]["key_specs"]["resolution_dpi"] = metadata['resolution_dpi']
            if metadata.get('print_speed_ips'):
                model_results[model]["key_specs"]["print_speed_ips"] = metadata['print_speed_ips']
            if metadata.get('has_usb'):
                model_results[model]["key_specs"]["connectivity"] = model_results[model]["key_specs"].get("connectivity", [])
                if "USB" not in model_results[model]["key_specs"]["connectivity"]:
                    model_results[model]["key_specs"]["connectivity"].append("USB")
            if metadata.get('has_ethernet'):
                model_results[model]["key_specs"]["connectivity"] = model_results[model]["key_specs"].get("connectivity", [])
                if "Ethernet" not in model_results[model]["key_specs"]["connectivity"]:
                    model_results[model]["key_specs"]["connectivity"].append("Ethernet")

        # Sort by relevance score (highest first)
        sorted_models = sorted(
            model_results.values(),
            key=lambda x: x['relevance_score'],
            reverse=True
        )

        # Return top N results
        return sorted_models[:n_results]

    def explain_recommendation(self, recommendation: Dict[str, Any]) -> str:
        """
        Generate human-readable explanation for a recommendation.

        Args:
            recommendation: Recommendation dictionary

        Returns:
            Explanation string
        """
        model = recommendation['model']
        score = recommendation['relevance_score']
        chunks = recommendation['matching_chunks']
        specs = recommendation['key_specs']

        explanation = [
            f"Model: {model}",
            f"Relevance Score: {score:.2%}",
            f"Category: {recommendation['category']}",
        ]

        # Add key specs
        if specs:
            explanation.append("\nKey Specifications:")
            if 'resolution_dpi' in specs:
                explanation.append(f"  - Resolution: {specs['resolution_dpi']} DPI")
            if 'print_speed_ips' in specs:
                explanation.append(f"  - Speed: {specs['print_speed_ips']} inches/second")
            if 'connectivity' in specs:
                explanation.append(f"  - Connectivity: {', '.join(specs['connectivity'])}")

        # Add matching information
        explanation.append(f"\nMatching Sections ({len(chunks)}):")
        for chunk in chunks[:3]:  # Show top 3 matching chunks
            chunk_type = chunk['chunk_type'].replace('_', ' ').title()
            explanation.append(f"  - {chunk_type} (score: {1.0 - chunk['distance']:.2%})")

        return "\n".join(explanation)

    def compare_printers(self, models: List[str]) -> Dict[str, Any]:
        """
        Compare specific printer models.

        Args:
            models: List of model numbers to compare

        Returns:
            Comparison data
        """
        comparison = {}

        for model in models:
            # Query for this specific model
            results = self.collection.query(
                query_texts=[model],
                n_results=10,
                where={"model": model}
            )

            if results and results['documents']:
                # Aggregate information
                model_info = {
                    "model": model,
                    "specs": {},
                    "features": [],
                    "description": ""
                }

                for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
                    chunk_type = metadata.get('chunk_type')

                    if chunk_type == 'overview':
                        model_info['description'] = doc[:300]  # First 300 chars
                    elif chunk_type == 'specifications':
                        # Parse specs from content
                        model_info['specs'] = self._parse_specs_from_text(doc)

                comparison[model] = model_info

        return comparison

    def _parse_specs_from_text(self, text: str) -> Dict[str, str]:
        """Parse specifications from text content."""
        specs = {}

        # Simple regex-based parsing
        lines = text.split('\n')
        for line in lines:
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    specs[key] = value

        return specs

    def _generate_llm_response(
        self,
        user_query: str,
        recommendations: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a natural language response using LLM (Claude or Ollama) based on RAG results.

        Args:
            user_query: Original user query
            recommendations: List of printer recommendations from vector DB

        Returns:
            Natural language response from the configured LLM
        """
        # Build comprehensive context from ALL search results
        context_parts = []

        for i, rec in enumerate(recommendations[:3], 1):  # Top 3 recommendations
            model = rec['model']
            category = rec['category']
            score = rec['relevance_score']
            specs = rec['key_specs']
            metadata = rec.get('metadata', {})

            context = f"\n{'='*80}\n"
            context += f"PRINTER {i}: {model}\n"
            context += f"{'='*80}\n\n"

            # Basic info
            context += f"Category: {category}\n"
            context += f"Relevance Score: {score:.2%}\n"
            context += f"Source File: {metadata.get('source_file', 'N/A')}\n\n"

            # All metadata/specs
            context += "=== METADATA & SPECIFICATIONS ===\n"
            if metadata:
                # Extract all useful metadata
                if metadata.get('resolution_dpi'):
                    context += f"Resolution: {metadata['resolution_dpi']} DPI\n"
                if metadata.get('print_speed_ips'):
                    context += f"Print Speed: {metadata['print_speed_ips']} inches/second\n"
                if metadata.get('max_media_width_inches'):
                    context += f"Max Media Width: {metadata['max_media_width_inches']} inches\n"
                if metadata.get('energy_star'):
                    context += f"Energy Star: Yes\n"

                # Connectivity
                conn = []
                if metadata.get('has_usb'):
                    conn.append('USB')
                if metadata.get('has_ethernet'):
                    conn.append('Ethernet')
                if metadata.get('has_wifi'):
                    conn.append('Wi-Fi')
                if metadata.get('has_bluetooth'):
                    conn.append('Bluetooth')
                if conn:
                    context += f"Connectivity: {', '.join(conn)}\n"

                # URLs
                if metadata.get('product_url'):
                    context += f"\nProduct Page URL: {metadata['product_url']}\n"
                if metadata.get('warranty_url'):
                    context += f"Warranty Information URL: {metadata['warranty_url']}\n"

            if specs:
                context += f"\nAdditional Specs:\n"
                for key, value in specs.items():
                    if isinstance(value, list):
                        context += f"  {key}: {', '.join(value)}\n"
                    else:
                        context += f"  {key}: {value}\n"

            # ALL matching chunks (not limited to 2)
            context += f"\n=== COMPLETE INFORMATION FROM ALL MATCHING SECTIONS ===\n"
            for j, chunk in enumerate(rec['matching_chunks'], 1):
                chunk_type = chunk['chunk_type'].replace('_', ' ').title()
                content = chunk['content']  # No truncation - send full content
                match_score = 1.0 - chunk['distance']

                context += f"\n--- Section {j}: {chunk_type} (Match: {match_score:.1%}) ---\n"
                context += f"{content}\n"

            context_parts.append(context)

        full_context = "\n".join(context_parts)

        # Create comprehensive prompt for Claude
        prompt = f"""You are an expert Zebra printer specialist helping customers choose the right printer for their needs.

USER'S QUESTION:
{user_query}

COMPLETE PRINTER INFORMATION:
{full_context}

INSTRUCTIONS:
1. Analyze ALL the provided information thoroughly
2. Provide a detailed, comprehensive recommendation based on the user's specific requirements
3. Explain WHY each printer is suitable, referencing specific features and specifications from the data
4. Compare printers if multiple are recommended - highlight key differences in capabilities, use cases, and features
5. Reference specific technical details from the provided sections (specifications, features, performance, etc.)
6. If the user asked about specific features or requirements, directly address them with evidence from the data
7. Be thorough but well-organized - use markdown headers (###) and bullet points to structure your response
8. Maintain a professional, knowledgeable, and helpful tone
9. Include relevant technical specifications to support your recommendations
10. If there are trade-offs between options, explain them clearly

CRITICAL - URL EMBEDDING:
11. For each printer you recommend, you MUST include clickable markdown links to:
    - Product Page URL (if provided)
    - Warranty Information URL (if provided)
12. Format links as markdown: [Link Text](https://url)
13. Add "https://" prefix to URLs that don't already have it (e.g., "www.zebra.com/zd200" becomes "https://www.zebra.com/zd200")
14. Place the product page link prominently near the printer name/model in your recommendation
15. Include the warranty link in a relevant section about warranty or support

IMPORTANT: Use the COMPLETE information provided above. Reference specific details from the matching sections to give authoritative, detailed answers. Use Markdown formatting (###, -, **bold**) in your response for clarity.

Your comprehensive recommendation:"""

        try:
            if self.llm_provider == "claude" and self.anthropic_client:
                # Call Claude API with increased token limit for detailed responses
                message = self.anthropic_client.messages.create(
                    model="claude-3-5-haiku-20241022",
                    max_tokens=4000,  # Increased from 1500 to allow detailed responses
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return message.content[0].text

            elif self.llm_provider == "ollama":
                # Call Ollama API
                response = ollama.chat(
                    model=self.ollama_model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response['message']['content']

            else:
                return "Error: No LLM client configured."

        except Exception as e:
            print(f"Error generating LLM response: {e}")
            import traceback
            traceback.print_exc()
            return f"Error: Unable to generate enhanced response. {str(e)}"


def main():
    """Example usage of the RAG system."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Query printer recommendations using RAG"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Natural language query (e.g., 'I need a fast desktop printer for retail')"
    )
    parser.add_argument(
        "--db-path",
        default="./chroma_db",
        help="Path to ChromaDB storage directory"
    )
    parser.add_argument(
        "--collection",
        default="printer_specs",
        help="Collection name"
    )
    parser.add_argument(
        "--n-results",
        type=int,
        default=3,
        help="Number of recommendations to return"
    )
    parser.add_argument(
        "--compare",
        nargs="+",
        help="Compare specific printer models"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM-enhanced responses (use basic vector search only)"
    )
    parser.add_argument(
        "--llm",
        choices=["claude", "ollama"],
        default="claude",
        help="LLM provider to use: 'claude' (default) or 'ollama'"
    )
    parser.add_argument(
        "--api-key",
        help="Anthropic API key (or set ANTHROPIC_API_KEY environment variable)"
    )
    parser.add_argument(
        "--ollama-model",
        default="llama3.2:1b",
        help="Ollama model name (default: llama3.2:1b)"
    )

    args = parser.parse_args()

    # Initialize RAG system
    try:
        rag = PrinterRAG(
            db_path=args.db_path,
            collection_name=args.collection,
            use_llm=not args.no_llm,
            llm_provider=args.llm,
            anthropic_api_key=args.api_key,
            ollama_model=args.ollama_model
        )
    except Exception as e:
        print(f"Error initializing RAG system: {e}")
        return 1

    # Compare mode
    if args.compare:
        print("\nComparing printers...")
        comparison = rag.compare_printers(args.compare)
        print(json.dumps(comparison, indent=2))
        return 0

    # Interactive mode
    if args.interactive:
        print("\nInteractive Printer Recommendation System")
        print("="*80)
        print("Enter your requirements (or 'quit' to exit)")
        print("Example: 'I need a desktop printer for healthcare that supports USB'")
        print("="*80)

        while True:
            query = input("\nYour requirements: ").strip()

            if query.lower() in ['quit', 'exit', 'q']:
                break

            if not query:
                continue

            result = rag.recommend_printer(query, n_results=args.n_results)

            print(f"\n{'='*80}")

            # Show LLM response if available
            if 'llm_response' in result:
                print("AI RECOMMENDATION")
                print(f"{'='*80}")
                print(f"\n{result['llm_response']}\n")
                print(f"\n{'='*80}")
                print("DETAILED BREAKDOWN")
            else:
                print("RECOMMENDATIONS")

            print(f"{'='*80}")

            if result['recommendations']:
                for i, rec in enumerate(result['recommendations'], 1):
                    print(f"\n{i}. {rag.explain_recommendation(rec)}")
                    print(f"\n{'-'*80}")
            else:
                print("No matching printers found. Try adjusting your requirements.")

        return 0

    # Single query mode
    if args.query:
        result = rag.recommend_printer(args.query, n_results=args.n_results)

        print(f"\n{'='*80}")

        # Show LLM response if available
        if 'llm_response' in result:
            print("AI RECOMMENDATION")
            print(f"{'='*80}")
            print(f"\n{result['llm_response']}\n")
            print(f"\n{'='*80}")
            print("DETAILED BREAKDOWN")
        else:
            print("RECOMMENDATIONS")

        print(f"{'='*80}")

        if result['recommendations']:
            for i, rec in enumerate(result['recommendations'], 1):
                print(f"\n{i}. {rag.explain_recommendation(rec)}")
                print(f"\n{'-'*80}")
        else:
            print("No matching printers found. Try adjusting your requirements.")

        return 0

    # No query provided
    print("Please provide a query or use --interactive mode")
    return 1


if __name__ == "__main__":
    exit(main())
