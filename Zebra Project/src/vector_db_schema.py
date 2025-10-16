"""
Vector Database Schema for Printer Specifications
Designed for RAG-based printer recommendations
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json


@dataclass
class PrinterDocument:
    """
    Structured document for vector database storage.
    Each printer is stored as multiple chunked documents for better retrieval.
    """

    # Identifiers
    doc_id: str  # Unique document ID (e.g., "zd220_overview")
    printer_model: str  # Model number (e.g., "ZD220")
    chunk_type: str  # Type of chunk: overview, specs, features, use_cases, etc.

    # Content for embedding
    content: str  # Main text content to be embedded

    # Metadata for filtering and ranking
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PrinterDocument':
        """Create from dictionary."""
        return cls(**data)


class PrinterVectorSchema:
    """
    Schema design for printer specifications in vector DB.

    Strategy:
    - Each printer is split into multiple semantic chunks
    - Each chunk is embedded separately for granular retrieval
    - Metadata enables filtering by specs before semantic search
    """

    CHUNK_TYPES = [
        "overview",           # Product description and key selling points
        "specifications",     # Technical specifications
        "features",          # Standard and optional features
        "use_cases",         # Applications and industries
        "connectivity",      # Connectivity options
        "media_ribbon",      # Media and ribbon specifications
        "compliance",        # Regulatory and certifications
        "performance",       # Speed, resolution, duty cycle
    ]

    @staticmethod
    def create_metadata_schema() -> Dict[str, str]:
        """
        Define metadata fields for filtering and hybrid search.
        These are NOT embedded but used for filtering.
        """
        return {
            # Identifiers
            "model": "str",
            "series": "str",
            "category": "str",  # desktop, mobile, industrial

            # Key specifications (for filtering)
            "print_method": "str",  # thermal_transfer, direct_thermal, both
            "resolution_dpi": "int",
            "max_print_width_inches": "float",
            "print_speed_ips": "float",

            # Physical characteristics
            "form_factor": "str",  # desktop, mobile, industrial
            "weight_lbs": "float",

            # Connectivity (for filtering)
            "has_usb": "bool",
            "has_ethernet": "bool",
            "has_wifi": "bool",
            "has_bluetooth": "bool",

            # Media capabilities
            "max_label_length_inches": "float",
            "min_media_width_inches": "float",
            "max_media_width_inches": "float",

            # Operating conditions
            "min_operating_temp_f": "int",
            "max_operating_temp_f": "int",

            # Compliance
            "energy_star": "bool",

            # Source
            "source_file": "str",
            "extraction_date": "str",
        }

    @staticmethod
    def extract_chunks_from_json(json_data: Dict[str, Any]) -> List[PrinterDocument]:
        """
        Convert a printer JSON file into multiple vector-ready documents.

        Args:
            json_data: Parsed JSON from pdf_processor.py output

        Returns:
            List of PrinterDocument objects ready for embedding
        """
        model = json_data.get("product_info", {}).get("model", "UNKNOWN")
        chunks = []

        # Extract common metadata
        base_metadata = PrinterVectorSchema._extract_metadata(json_data)

        # CHUNK 1: Overview
        overview_content = PrinterVectorSchema._create_overview_chunk(json_data)
        if overview_content:
            chunks.append(PrinterDocument(
                doc_id=f"{model}_overview",
                printer_model=model,
                chunk_type="overview",
                content=overview_content,
                metadata={**base_metadata, "chunk_type": "overview"}
            ))

        # CHUNK 2: Specifications
        specs_content = PrinterVectorSchema._create_specs_chunk(json_data)
        if specs_content:
            chunks.append(PrinterDocument(
                doc_id=f"{model}_specifications",
                printer_model=model,
                chunk_type="specifications",
                content=specs_content,
                metadata={**base_metadata, "chunk_type": "specifications"}
            ))

        # CHUNK 3: Features
        features_content = PrinterVectorSchema._create_features_chunk(json_data)
        if features_content:
            chunks.append(PrinterDocument(
                doc_id=f"{model}_features",
                printer_model=model,
                chunk_type="features",
                content=features_content,
                metadata={**base_metadata, "chunk_type": "features"}
            ))

        # CHUNK 4: Use Cases
        use_cases_content = PrinterVectorSchema._create_use_cases_chunk(json_data)
        if use_cases_content:
            chunks.append(PrinterDocument(
                doc_id=f"{model}_use_cases",
                printer_model=model,
                chunk_type="use_cases",
                content=use_cases_content,
                metadata={**base_metadata, "chunk_type": "use_cases"}
            ))

        # CHUNK 5: Media & Ribbon
        media_content = PrinterVectorSchema._create_media_ribbon_chunk(json_data)
        if media_content:
            chunks.append(PrinterDocument(
                doc_id=f"{model}_media_ribbon",
                printer_model=model,
                chunk_type="media_ribbon",
                content=media_content,
                metadata={**base_metadata, "chunk_type": "media_ribbon"}
            ))

        # CHUNK 6: Performance
        performance_content = PrinterVectorSchema._create_performance_chunk(json_data)
        if performance_content:
            chunks.append(PrinterDocument(
                doc_id=f"{model}_performance",
                printer_model=model,
                chunk_type="performance",
                content=performance_content,
                metadata={**base_metadata, "chunk_type": "performance"}
            ))

        return chunks

    @staticmethod
    def _extract_metadata(json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract filterable metadata from JSON."""
        product_info = json_data.get("product_info", {})
        specs = json_data.get("specifications", {})
        printer_specs = specs.get("printer", {})
        physical = specs.get("physical", {})
        media = specs.get("media", {})
        operating = specs.get("operating_conditions", {})
        connectivity = json_data.get("connectivity", [])
        compliance = json_data.get("compliance", {})

        # Helper function to safely get nested values
        def safe_get(data, key, default=0):
            """Safely extract value from dict or return default."""
            if isinstance(data, dict):
                return data.get(key, default)
            return default

        # Extract media width safely
        media_width_data = media.get("media_width", {})
        if isinstance(media_width_data, dict):
            max_width = media_width_data.get("max_inches", 0)
        else:
            max_width = 0

        # Extract resolution safely
        resolution_data = printer_specs.get("resolution", {})
        if isinstance(resolution_data, dict):
            resolution_dpi = resolution_data.get("dpi", 0)
        else:
            resolution_dpi = 0

        # Extract print speed safely
        speed_data = printer_specs.get("print_speed", {})
        if isinstance(speed_data, dict):
            print_speed = speed_data.get("inches_per_second", 0)
        else:
            print_speed = 0

        metadata = {
            "model": product_info.get("model", ""),
            "series": product_info.get("series", ""),
            "category": PrinterVectorSchema._infer_category(product_info.get("title", "")),

            # Specs
            "resolution_dpi": resolution_dpi,
            "print_speed_ips": print_speed,

            # Connectivity
            "has_usb": "USB" in connectivity,
            "has_ethernet": "Ethernet" in connectivity,
            "has_wifi": "Wi-Fi" in connectivity,
            "has_bluetooth": "Bluetooth" in connectivity,

            # Media
            "max_media_width_inches": max_width,

            # Compliance
            "energy_star": compliance.get("energy_star", False),

            # Source
            "source_file": json_data.get("metadata", {}).get("source_file", ""),
            "extraction_date": json_data.get("metadata", {}).get("extraction_date", ""),
        }

        return metadata

    @staticmethod
    def _infer_category(title: str) -> str:
        """Infer printer category from title."""
        title_lower = title.lower()
        if "desktop" in title_lower:
            return "desktop"
        elif "mobile" in title_lower:
            return "mobile"
        elif "industrial" in title_lower:
            return "industrial"
        return "unknown"

    @staticmethod
    def _create_overview_chunk(json_data: Dict[str, Any]) -> str:
        """Create overview chunk with key information."""
        product_info = json_data.get("product_info", {})

        parts = []

        # Title and model
        if product_info.get("title"):
            parts.append(f"Product: {product_info['title']}")

        if product_info.get("model"):
            parts.append(f"Model: {product_info['model']}")

        # Tagline
        if product_info.get("tagline"):
            parts.append(f"Description: {product_info['tagline']}")

        # Full description
        if product_info.get("description"):
            desc = product_info['description']
            # Extract just the meaningful part, not the full raw text
            if "---" not in desc:
                parts.append(desc)
            else:
                # Get first paragraph before page markers
                first_para = desc.split("---")[0].strip()
                if len(first_para) > 100:
                    parts.append(first_para)

        return "\n\n".join(parts)

    @staticmethod
    def _create_specs_chunk(json_data: Dict[str, Any]) -> str:
        """Create specifications chunk."""
        specs = json_data.get("specifications", {})
        printer_specs = specs.get("printer", {})
        physical = specs.get("physical", {})
        operating = specs.get("operating_conditions", {})

        parts = []

        # Printer specifications
        if printer_specs.get("resolution"):
            res = printer_specs["resolution"]
            if isinstance(res, dict):
                parts.append(f"Resolution: {res.get('raw', res)}")
            else:
                parts.append(f"Resolution: {res}")

        if printer_specs.get("print_speed"):
            speed = printer_specs["print_speed"]
            if isinstance(speed, dict):
                parts.append(f"Print Speed: {speed.get('raw', speed)}")
            else:
                parts.append(f"Print Speed: {speed}")

        if printer_specs.get("memory"):
            parts.append(f"Memory: {printer_specs['memory']}")

        if printer_specs.get("maximum_print_width"):
            parts.append(f"Maximum Print Width: {printer_specs['maximum_print_width']}")

        # Physical specs
        if physical.get("dimensions"):
            parts.append(f"Dimensions: {physical['dimensions']}")

        if physical.get("weight"):
            parts.append(f"Weight: {physical['weight']}")

        # Operating conditions
        if operating.get("operating_temperature"):
            temp = operating["operating_temperature"]
            if isinstance(temp, dict):
                parts.append(f"Operating Temperature: {temp.get('raw', temp)}")
            else:
                parts.append(f"Operating Temperature: {temp}")

        if operating.get("operating_humidity"):
            humid = operating["operating_humidity"]
            if isinstance(humid, dict):
                parts.append(f"Operating Humidity: {humid.get('raw', humid)}")
            else:
                parts.append(f"Operating Humidity: {humid}")

        return "\n".join(parts)

    @staticmethod
    def _create_features_chunk(json_data: Dict[str, Any]) -> str:
        """Create features chunk."""
        features = json_data.get("features", {})
        fonts_barcodes = json_data.get("fonts_and_barcodes", {})

        parts = []

        # Standard features
        if features.get("standard"):
            parts.append("Standard Features:")
            for feature in features["standard"]:
                parts.append(f"  - {feature}")

        # Optional features
        if features.get("optional"):
            parts.append("\nOptional Features:")
            for feature in features["optional"]:
                parts.append(f"  - {feature}")

        # Fonts and barcodes
        if fonts_barcodes:
            if fonts_barcodes.get("barcodes_1d"):
                parts.append(f"\n1D Barcodes: {', '.join(fonts_barcodes['barcodes_1d'])}")

            if fonts_barcodes.get("barcodes_2d"):
                parts.append(f"2D Barcodes: {', '.join(fonts_barcodes['barcodes_2d'])}")

        return "\n".join(parts)

    @staticmethod
    def _create_use_cases_chunk(json_data: Dict[str, Any]) -> str:
        """Create use cases chunk from description."""
        product_info = json_data.get("product_info", {})

        parts = []

        # Extract use case info from description
        description = product_info.get("description", "")

        # Look for industry/application mentions
        industries = []
        if "transportation" in description.lower():
            industries.append("Transportation and Logistics")
        if "manufacturing" in description.lower():
            industries.append("Manufacturing")
        if "retail" in description.lower():
            industries.append("Retail")
        if "healthcare" in description.lower():
            industries.append("Healthcare")

        if industries:
            parts.append(f"Ideal for: {', '.join(industries)}")

        # Look for application mentions
        if "label" in description.lower():
            parts.append("Applications: Labels, tags, receipts, passes, tickets")

        return "\n".join(parts)

    @staticmethod
    def _create_media_ribbon_chunk(json_data: Dict[str, Any]) -> str:
        """Create media and ribbon specifications chunk."""
        specs = json_data.get("specifications", {})
        media = specs.get("media", {})
        ribbon = specs.get("ribbon", {})

        parts = []

        # Media specs
        if media.get("media_width"):
            width = media["media_width"]
            if isinstance(width, dict):
                parts.append(f"Media Width: {width.get('raw', width)}")
            else:
                parts.append(f"Media Width: {width}")

        if media.get("maximum_label_length"):
            parts.append(f"Maximum Label Length: {media['maximum_label_length']}")

        if media.get("media_types"):
            parts.append(f"Media Types: {', '.join(media['media_types'])}")

        if media.get("thickness"):
            parts.append(f"Media Thickness: {media['thickness']}")

        # Ribbon specs
        if ribbon.get("maximum_ribbon_length"):
            parts.append(f"Maximum Ribbon Length: {ribbon['maximum_ribbon_length']}")

        if ribbon.get("ribbon_width"):
            parts.append(f"Ribbon Width: {ribbon['ribbon_width']}")

        return "\n".join(parts)

    @staticmethod
    def _create_performance_chunk(json_data: Dict[str, Any]) -> str:
        """Create performance-focused chunk."""
        specs = json_data.get("specifications", {})
        printer_specs = specs.get("printer", {})

        parts = []

        if printer_specs.get("print_speed"):
            speed = printer_specs["print_speed"]
            if isinstance(speed, dict):
                parts.append(f"Print Speed: {speed.get('inches_per_second', 'N/A')} inches per second")
            else:
                parts.append(f"Print Speed: {speed}")

        if printer_specs.get("resolution"):
            res = printer_specs["resolution"]
            if isinstance(res, dict):
                parts.append(f"Resolution: {res.get('dpi', 'N/A')} DPI for high-quality output")
            else:
                parts.append(f"Resolution: {res}")

        # Add any performance-related info from description
        product_info = json_data.get("product_info", {})
        desc = product_info.get("description", "")

        if "fast" in desc.lower() or "speed" in desc.lower():
            parts.append("Optimized for high-speed printing workflows")

        if "duty cycle" in desc.lower():
            parts.append("Designed for demanding duty cycles")

        return "\n".join(parts)


# Example usage and testing
if __name__ == "__main__":
    # Example: Load a JSON file and convert to chunks
    import sys

    if len(sys.argv) > 1:
        json_file = sys.argv[1]

        with open(json_file, 'r') as f:
            data = json.load(f)

        chunks = PrinterVectorSchema.extract_chunks_from_json(data)

        print(f"Generated {len(chunks)} chunks for {data.get('product_info', {}).get('model', 'UNKNOWN')}")
        print("\nChunks:")
        for chunk in chunks:
            print(f"\n{'='*80}")
            print(f"Chunk Type: {chunk.chunk_type}")
            print(f"Doc ID: {chunk.doc_id}")
            print(f"Content Preview: {chunk.content[:200]}...")
            print(f"Metadata: {chunk.metadata}")
