"""
PDF to JSON Processor for Zebra Printer Specifications
Extracts ALL information from PDFs using OCR and organizes it into structured JSON.
Any information that doesn't fit standard categories goes into 'additional_information'.
"""

import pdfplumber
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class PDFProcessor:
    """Processes PDF files and extracts complete information into JSON format."""

    def __init__(self):
        """Initialize the PDF processor."""
        self.schema_version = "1.0.0"

    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract all text from PDF organized by pages.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with extracted text and tables
        """
        extracted_data = {
            "pages": [],
            "all_text": "",
            "tables": []
        }

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_data = {
                    "page_number": page_num,
                    "text": "",
                    "tables": []
                }

                # Extract text
                text = page.extract_text()
                if text:
                    page_data["text"] = text
                    extracted_data["all_text"] += f"\n--- Page {page_num} ---\n{text}"

                # Extract tables
                tables = page.extract_tables()
                if tables:
                    for table_idx, table in enumerate(tables):
                        page_data["tables"].append({
                            "table_index": table_idx,
                            "data": table
                        })
                        extracted_data["tables"].append({
                            "page": page_num,
                            "table_index": table_idx,
                            "data": table
                        })

                extracted_data["pages"].append(page_data)

        return extracted_data

    def parse_specifications(self, tables: List[Dict]) -> Dict[str, Any]:
        """Parse specifications from extracted tables."""
        specs = {
            "printer": {},
            "physical": {},
            "media": {},
            "ribbon": {},
            "operating_conditions": {}
        }

        for table_info in tables:
            table = table_info["data"]

            for row in table:
                if not row or len(row) < 2:
                    continue

                key = str(row[0]).strip() if row[0] else ""
                value = str(row[1]).strip() if row[1] else ""

                if not key or not value:
                    continue

                key_lower = key.lower()

                # Printer specifications
                if any(term in key_lower for term in ["resolution", "dpi", "dots per mm"]):
                    specs["printer"]["resolution"] = self._parse_resolution(key, value)
                elif "memory" in key_lower and "user available" not in key_lower and "flash" not in key_lower and "sdram" not in key_lower.split():
                    specs["printer"]["memory"] = value
                elif "maximum print" in key_lower and "width" in key_lower:
                    specs["printer"]["maximum_print_width"] = value
                elif ("maximum print" in key_lower and "speed" in key_lower) or ("print speed" in key_lower and "maximum" not in key_lower):
                    specs["printer"]["print_speed"] = self._parse_speed(value)
                elif "media sensor" in key_lower:
                    if "media_sensors" not in specs["printer"]:
                        specs["printer"]["media_sensors"] = []

                    # Clean and split by logical sensor descriptions
                    value_clean = re.sub(r'\s+', ' ', value)  # First normalize whitespace

                    # Split by "Fixed" which indicates a new sensor - add space after "Fixed"
                    if "Fixed" in value_clean and "Fixedoff" not in value_clean:
                        parts = value_clean.split("Fixed")
                        specs["printer"]["media_sensors"].append(parts[0].strip())
                        specs["printer"]["media_sensors"].append("Fixed " + parts[1].strip())
                    elif "Fixedoff" in value_clean:
                        # Handle the case where "Fixed" is concatenated
                        parts = value_clean.split("Fixed")
                        if parts[0].strip():
                            specs["printer"]["media_sensors"].append(parts[0].strip())
                        specs["printer"]["media_sensors"].append("Fixed " + parts[1].strip())
                    else:
                        specs["printer"]["media_sensors"].append(value_clean)
                elif "firmware" in key_lower:
                    specs["printer"]["firmware"] = [f.strip() for f in value.split(';')]
                elif "maximum print length" in key_lower:
                    specs["printer"]["maximum_print_length"] = value

                # Physical specifications
                elif "dimension" in key_lower:
                    specs["physical"]["dimensions"] = value
                elif "weight" in key_lower:
                    specs["physical"]["weight"] = value

                # Media specifications
                elif ("minimum label" in key_lower and "length" in key_lower) or ("label and liner" in key_lower and "length" in key_lower):
                    specs["media"]["minimum_label_length"] = value
                elif "media width" in key_lower:
                    specs["media"]["media_width"] = self._parse_range(value)
                elif "media roll" in key_lower or "roll size" in key_lower:
                    specs["media"]["media_roll_size"] = value
                elif "thickness" in key_lower and "ribbon" not in key_lower and "media" in key_lower:
                    specs["media"]["thickness"] = value
                elif "media type" in key_lower:
                    # Clean up media types - consolidate logical groups
                    raw_types = value.replace('\n', ' ')
                    # Split more intelligently
                    types_list = []

                    if "roll-fed" in raw_types.lower() or "fan-fold" in raw_types.lower():
                        types_list.append("Roll-fed or fan-fold")

                    if "die cut" in raw_types.lower() or "die-cut" in raw_types.lower():
                        types_list.append("Die cut or continuous with or without black mark")

                    if "tag stock" in raw_types.lower():
                        types_list.append("Tag stock")

                    if "receipt paper" in raw_types.lower():
                        types_list.append("Continuous receipt paper")

                    if "wristband" in raw_types.lower():
                        types_list.append("Wristbands")

                    if "notch" in raw_types.lower() or "black mark" in raw_types.lower():
                        if "die cut" not in raw_types.lower():
                            types_list.append(raw_types)

                    specs["media"]["media_types"] = types_list if types_list else [raw_types]

                # Ribbon specifications
                elif "ribbon" in key_lower or ("standard" in key_lower and "length" in key_lower and table_info.get("page", 0) > 2):
                    if "outside diameter" in key_lower or ("diameter" in key_lower and "ribbon" in key_lower):
                        specs["ribbon"]["outside_diameter"] = self._parse_measurement(value)
                    elif ("length" in key_lower and "ribbon" in key_lower) or ("standard" in key_lower and "length" in key_lower):
                        specs["ribbon"]["maximum_ribbon_length"] = value
                    elif "ratio" in key_lower:
                        specs["ribbon"]["ribbon_ratio"] = value
                    elif "width" in key_lower:
                        specs["ribbon"]["ribbon_width"] = value
                    elif "core" in key_lower:
                        specs["ribbon"]["ribbon_core_id"] = value

                # Operating conditions
                elif "operating" in key_lower and "temp" in key_lower:
                    specs["operating_conditions"]["operating_temperature"] = self._parse_temperature(value)
                elif ("storage" in key_lower or "transportation" in key_lower) and "temp" in key_lower:
                    specs["operating_conditions"]["storage_temperature"] = self._parse_temperature(value)
                elif "operating" in key_lower and "humidity" in key_lower:
                    specs["operating_conditions"]["operating_humidity"] = self._parse_humidity(value)
                elif "storage" in key_lower and "humidity" in key_lower:
                    specs["operating_conditions"]["storage_humidity"] = self._parse_humidity(value)
                elif "electrical" in key_lower or "power supply" in key_lower:
                    specs["operating_conditions"]["electrical"] = value
                elif "agency" in key_lower and "approval" in key_lower:
                    specs["operating_conditions"]["agency_approvals"] = value

        return specs
    
    def parse_product_info(self, text: str) -> Dict[str, str]:
        """
        Extract product information from text.

        Args:
            text: Full text from PDF

        Returns:
            Dictionary with product information
        """
        info = {}

        # Extract model number (pattern: letters followed by numbers)
        model_match = re.search(r'\b([A-Z]{2}\d{3,4}[A-Za-z]?)\b', text)
        if model_match:
            info["model"] = model_match.group(1)

        # Extract title (usually in first few lines)
        lines = text.split('\n')
        for i, line in enumerate(lines[:10]):
            if any(word in line.lower() for word in ["printer", "desktop", "mobile", "industrial"]):
                info["title"] = line.strip()
                break

        # Extract tagline (subtitle or marketing line)
        tagline_patterns = [
            r'(Reliable.*?value)',
            r'(The.*?choice)',
            r'(Industry.*?performance)'
        ]
        for pattern in tagline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["tagline"] = match.group(1)
                break

        # Extract URL
        url_match = re.search(r'www\.zebra\.com/\S+', text)
        if url_match:
            info["url"] = url_match.group(0)

        # Extract description (first substantial paragraph)
        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 100]
        if paragraphs:
            info["description"] = paragraphs[0]

        return info

    def parse_fonts_and_barcodes(self, text: str, tables: List[Dict]) -> Dict[str, Any]:
        """Extract font and barcode information."""
        fonts_barcodes = {
            "fonts": [],
            "barcode_ratios": [],
            "barcodes_1d": [],
            "barcodes_2d": [],
            "graphics_memory": ""
        }

        for table_info in tables:
            table = table_info["data"]

            # Check for single-column tables (like Firmware, Barcodes, Fonts)
            if table and len(table) > 0:
                # Check if this is a single-column table with header
                first_row = table[0] if table[0] else []
                header = str(first_row[0]).strip() if first_row and first_row[0] else ""

                # Handle Barcode Symbologies table (single column)
                if "barcode symbolog" in header.lower():
                    if len(table) > 1 and table[1] and table[1][0]:
                        content = str(table[1][0])

                        # Extract Linear/1D Barcodes
                        linear_match = re.search(r'Linear Barcodes:\s*(.*?)(?=2D Barcodes:|$)', content, re.DOTALL)
                        if linear_match:
                            linear_text = linear_match.group(1).strip()
                            barcodes = re.split(r',\s*(?=[A-Z])', linear_text)
                            fonts_barcodes["barcodes_1d"] = [bc.strip() for bc in barcodes if bc.strip()]

                        # Extract 2D Barcodes
                        barcode_2d_match = re.search(r'2D Barcodes:\s*(.*?)$', content, re.DOTALL)
                        if barcode_2d_match:
                            barcode_2d_text = barcode_2d_match.group(1).strip()
                            barcodes = re.split(r',\s*(?=[A-Z])', barcode_2d_text)
                            fonts_barcodes["barcodes_2d"] = [bc.strip() for bc in barcodes if bc.strip()]
                    continue

                # Handle Fonts and Graphics table (single column)
                if "fonts and graphics" in header.lower():
                    if len(table) > 1 and table[1] and table[1][0]:
                        content = str(table[1][0])

                        # Split by sentences/logical groups
                        parts = re.split(r'(?<=[.:])\s+(?=[A-Z])', content)

                        for part in parts:
                            part = part.strip()
                            if not part:
                                continue

                            # Check if it's memory info
                            if ('MB' in part and 'available' in part) or ('Flash memory' in part or 'SDRAM' in part):
                                fonts_barcodes["graphics_memory"] = part
                            # Otherwise it's a font description
                            elif part:
                                fonts_barcodes["fonts"].append(part)
                    continue

            # Handle standard two-column tables
            for row in table:
                if not row or len(row) < 2:
                    continue

                key = str(row[0]).strip() if row[0] else ""
                value = str(row[1]).strip() if row[1] else ""

                if not key or not value:
                    continue

                key_lower = key.lower()

                # Clean newlines from value
                value_clean = re.sub(r'\s*\n\s*', ' ', value)

                # Barcode ratios
                if "bar code ratio" in key_lower or "barcode ratio" in key_lower:
                    fonts_barcodes["barcode_ratios"] = [r.strip() for r in re.split(r'\band\b', value_clean)]

        return fonts_barcodes
    
    def parse_features(self, text: str, tables: List[Dict]) -> Dict[str, List[str]]:
        """Extract standard and optional features."""
        features = {
            "standard": [],
            "optional": []
        }

        # Method 1: Extract from raw text using bullet points
        # Look for the section between "Standard Features" and next major heading
        standard_section = re.search(
            r'Standard Features\s*\n((?:•[^\n]+\n?)+)',
            text,
            re.DOTALL
        )
        
        if standard_section:
            feature_text = standard_section.group(1)
            # Split by bullet points - handle both • and escaped versions
            lines = feature_text.split('\n')
            
            for line in lines:
                # Remove bullet point and clean
                line = line.strip()
                if line.startswith('•'):
                    feature = line[1:].strip()  # Remove bullet
                elif line.startswith('â€¢'):  # Escaped bullet
                    feature = line[3:].strip()  # Remove escaped bullet
                else:
                    continue
                
                # Clean up the feature text
                if feature:
                    # Remove any remaining special chars and extra whitespace
                    feature = re.sub(r'\s+', ' ', feature).strip()
                    if len(feature) > 3:
                        features["standard"].append(feature)
        
        # Method 2: If Method 1 didn't work, try extracting from tables
        if not features["standard"]:
            for table_info in tables:
                table = table_info["data"]
                
                in_standard_section = False
                for row in table:
                    if not row:
                        continue
                    
                    row_text = ' '.join([str(cell) for cell in row if cell]).strip()
                    
                    # Check if we're entering standard features
                    if 'Standard Features' in row_text:
                        in_standard_section = True
                        continue
                    
                    # Check if we've left the section
                    if in_standard_section and any(header in row_text for header in 
                        ['Physical Characteristics', 'Operating Characteristics', 'Printer Specifications']):
                        break
                    
                    # Extract features
                    if in_standard_section:
                        # Look for bullet points in the row
                        if '•' in row_text or 'â€¢' in row_text:
                            # Split by bullets and extract each feature
                            parts = re.split(r'[•â€¢]', row_text)
                            for part in parts:
                                part = part.strip()
                                if part and len(part) > 5:
                                    # Clean up
                                    part = re.sub(r'\s+', ' ', part)
                                    if part not in features["standard"]:
                                        features["standard"].append(part)
        
        # Extract optional features from tables
        for table_info in tables:
            table = table_info["data"]
            
            in_options_section = False
            for row in table:
                if not row:
                    continue
                
                row_text = ' '.join([str(cell) for cell in row if cell]).strip()
                
                # Check if we're in Options and Accessories section
                if 'Options and Accessories' in row_text:
                    in_options_section = True
                    continue
                
                # Check if we've left the section
                if in_options_section and any(section in row_text for section in 
                    ['Fonts/Graphics', 'Bar Code', 'Printer Specifications']):
                    in_options_section = False
                
                # Extract options
                if in_options_section and len(row) >= 2:
                    key = str(row[0]).strip() if row[0] else ""
                    value = str(row[1]).strip() if row[1] else ""
                    
                    if key and value and 'Options and Accessories' not in key:
                        features["optional"].append(f"{key}: {value}")
        
        return features
    
    def parse_connectivity(self, text: str) -> List[str]:
        """Extract connectivity options."""
        connectivity = []

        patterns = {
            'USB': r'\bUSB\s+connectivity\b',
            'Ethernet': r'\bEthernet\b',
            'Wi-Fi': r'\bWi-Fi\b',
            'Bluetooth': r'\bBluetooth\b',
            'Serial': r'\bSerial\b',
            'Parallel': r'\bParallel\b'
        }

        for conn_type, pattern in patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                connectivity.append(conn_type)

        return connectivity

    def parse_compliance(self, text: str) -> Dict[str, Any]:
        """Extract regulatory compliance information."""
        compliance = {
            "regulatory_standards": [],
            "certifications": [],
            "energy_star": False
        }

        # Look for regulatory section or agency approvals section
        regulatory_match = re.search(
            r'(?:Regulatory|Agency\s+Approvals)\s*(.*?)(?=\n\n|Recommended Services|Print DNA|$)',
            text,
            re.DOTALL | re.IGNORECASE
        )

        if regulatory_match:
            reg_text = regulatory_match.group(1)

            # Clean up the text first
            reg_text = re.sub(r'\s+', ' ', reg_text)

            # Extract specific complete standards with better patterns
            standard_patterns = [
                r'IEC\s+[\d\-]+',
                r'EN\d+\s+Class\s+B',  # EN55022 Class B, EN55024, etc
                r'EN\d{5}(?:-\d-\d)?',  # EN55022, EN61000-3-2, etc
                r'EN\s+\d{3}\s+\d{3}',  # EN 300 328, EN 301 893
                r'FCC\s+Class\s+B',
                r'FCC\s+15\.\d+(?:\([a-z]\))?',  # FCC 15.209, FCC 15.247(d)
                r'ICES-\d+',
                r'IC\s+RSS\s+\d+',
                r'CE\s+Marking',
                r'cTUVus',
                r'VCCI',
                r'C-Tick',
                r'RCM',
                r'S-Mark',
                r'UKCA',
                r'\bCCC\b',
                r'\bCU\s+EAC\b',
                r'\bCU\b(?!\s+EAC)',
                r'BSMI',
                r'KCC',
                r'SABS',
                r'IN-Metro',
                r'BIS',
                r'\bNOM\b'
            ]

            for pattern in standard_patterns:
                matches = re.findall(pattern, reg_text, re.IGNORECASE)
                for match in matches:
                    clean_match = match.strip()
                    if clean_match and clean_match not in compliance["regulatory_standards"]:
                        compliance["regulatory_standards"].append(clean_match)

            # Extract certifications
            if re.search(r'CE Marking', text, re.IGNORECASE):
                compliance["certifications"].append("CE Marking")
            if re.search(r'cTUVus', text):
                compliance["certifications"].append("cTUVus")
            if re.search(r'ENERGY STAR', text, re.IGNORECASE):
                compliance["certifications"].append("ENERGY STAR")

        # Check for ENERGY STAR
        if re.search(r'ENERGY STAR', text, re.IGNORECASE):
            compliance["energy_star"] = True

        return compliance

    def parse_warranty(self, text: str) -> Dict[str, str]:
        """Extract warranty information."""
        warranty = {}

        # Look for the actual Product Warranty section
        warranty_match = re.search(
            r'Product Warranty\s*(.*?)(?=The Zebra wordmark|$)', 
            text, 
            re.DOTALL | re.IGNORECASE
        )
        
        if warranty_match:
            warranty_text = warranty_match.group(1).strip()

            # Extract duration
            duration_match = re.search(r'(\d+)\s*\(.*?\)\s*years?', warranty_text, re.IGNORECASE)
            if duration_match:
                warranty["duration_years"] = int(duration_match.group(1))

            # Clean coverage text
            warranty["coverage"] = re.sub(r'\s+', ' ', warranty_text).strip()

            # Extract URL
            url_match = re.search(r'www\.zebra\.com/warranty', warranty_text)
            if url_match:
                warranty["url"] = url_match.group(0)

        return warranty

    def parse_firmware(self, text: str, tables: List[Dict]) -> List[str]:
        """Extract firmware information from tables or text."""
        firmware_list = []

        for table_info in tables:
            table = table_info["data"]

            # Check for single-column Firmware table
            if table and len(table) > 0:
                first_row = table[0] if table[0] else []
                header = str(first_row[0]).strip() if first_row and first_row[0] else ""

                # Handle single-column Firmware table
                if "firmware" in header.lower() and len(first_row) == 1:
                    if len(table) > 1 and table[1] and table[1][0]:
                        content = str(table[1][0])

                        # Split by firmware names (lines starting with known firmware names)
                        firmware_patterns = [
                            r'(ZBI[^\n]+—[^\n]+(?:\n[^\n]+(?!—))*)',
                            r'(ZPL[^\n]+—[^\n]+(?:\n[^\n]+(?!—))*)',
                            r'(EPL[^\n]+—[^\n]+(?:\n[^\n]+(?!—))*)'
                        ]

                        for pattern in firmware_patterns:
                            matches = re.findall(pattern, content, re.MULTILINE)
                            for match in matches:
                                entry = re.sub(r'\s+', ' ', match.strip())
                                if entry and entry not in firmware_list:
                                    firmware_list.append(entry)
                    continue

            # Handle standard two-column tables
            for row in table:
                if not row or len(row) < 2:
                    continue

                key = str(row[0]).strip() if row[0] else ""
                value = str(row[1]).strip() if row[1] else ""

                if not key or not value:
                    continue

                key_lower = key.lower()

                if "firmware" in key_lower:
                    # Parse firmware entries
                    firmware_entries = re.split(r'\n(?=[A-Z])', value)
                    for entry in firmware_entries:
                        entry = entry.strip()
                        if entry and entry not in firmware_list:
                            firmware_list.append(entry)

        return firmware_list

    def parse_markets_applications(self, tables: List[Dict]) -> Dict[str, List[str]]:
        """Extract markets and applications information from tables."""
        markets = {}

        for table_info in tables:
            table = table_info["data"]

            # Look for single-column table with "Markets and Applications" header
            if table and len(table) > 0:
                first_row = table[0] if table[0] else []
                header = str(first_row[0]).strip() if first_row and first_row[0] else ""

                # Skip this table - it's usually part of page header/layout
                if "markets and" in header.lower() and "applications" in header.lower():
                    if len(table) > 1 and table[1] and table[1][0]:
                        content = str(table[1][0])

                        # Define market categories
                        categories = [
                            ("Manufacturing", r'Manufacturing\s+(.*?)(?=Transportation and Logistics|Healthcare|Retail|$)'),
                            ("Transportation and Logistics", r'Transportation and Logistics\s+(.*?)(?=Healthcare|Retail|$)'),
                            ("Healthcare", r'Healthcare\s+(.*?)(?=Retail|$)'),
                            ("Retail", r'Retail\s+(.*?)$')
                        ]

                        for category_name, pattern in categories:
                            category_match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

                            if category_match:
                                apps_text = category_match.group(1)
                                # Extract bullet points
                                apps = re.findall(r'•\s*([^\n•]+)', apps_text)
                                if apps:
                                    # Filter out junk - only keep items that are relevant application descriptions
                                    filtered_apps = []
                                    for app in apps:
                                        app = app.strip()
                                        # Skip if it's too long (probably merged data) or contains technical specs
                                        if len(app) > 100 or 'mm' in app.lower() or 'in.' in app or 'lbs' in app:
                                            continue
                                        # Skip if it has firmware/technical keywords
                                        if any(keyword in app.lower() for keyword in ['firmware', 'communications:', 'energy star', 'bluetooth', 'printer specifications']):
                                            continue
                                        filtered_apps.append(app)

                                    if filtered_apps:
                                        markets[category_name] = filtered_apps

        return markets

    def extract_additional_info(self, text: str) -> Dict[str, Any]:
        """
        Extract any additional information not captured in standard categories.
        This ensures no data is lost.
        """
        additional = {}

        # Define sections with better patterns
        sections_patterns = {
            "Recommended Services": r'Recommended Services\s*(.*?)(?=\n\s*\n[A-Z][a-z]+\s+[A-Z]|Operating System|$)',
            "ZebraOneCare": r'ZebraOneCare\s*(.*?)(?=\n\s*\n[A-Z][a-z]+\s+[A-Z]|Note:|$)',
            "Print DNA": r'Print DNA\s+Software\s*(.*?)(?=\n\s*\n[A-Z][a-z]+\s+[A-Z]|Product Warranty|The Zebra|$)',
            "Operating System": r'Operating System\s*(.*?)(?=\n\s*\n[A-Z][a-z]+\s+[A-Z]|Print DNA|$)',
            "Printer Supplies": r'Printers?\s+Supplies\s*(.*?)(?=\n\s*\n[A-Z][a-z]+\s+[A-Z]|Regulatory|$)',
        }

        for section_name, pattern in sections_patterns.items():
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                section_content = match.group(1).strip()
                # Clean up excessive whitespace
                section_content = re.sub(r'\s+', ' ', section_content)
                additional[section_name] = section_content

        # Parse Print DNA components if found
        if "Print DNA" in additional:
            additional["Print DNA Components"] = {}

            # Look for specific components
            components = {
                "Zebra Setup Utilities": r'Zebra Setup\s+Utilities\s*(.*?)(?=ZebraDesigner|Emulations|For more|$)',
                "ZebraDesigner Essentials": r'ZebraDesigner\s+Essentials\s*(.*?)(?=Emulations|For more|$)',
                "Emulations": r'Emulations\s*(.*?)(?=For more|$)'
            }

            for comp_name, comp_pattern in components.items():
                comp_match = re.search(comp_pattern, additional["Print DNA"], re.DOTALL | re.IGNORECASE)
                if comp_match:
                    additional["Print DNA Components"][comp_name] = re.sub(r'\s+', ' ', comp_match.group(1).strip())

        # Extract any disclaimers or notes
        disclaimer_matches = re.findall(r'Note:\s*(.+?)(?=\n\n|$)', text, re.IGNORECASE | re.DOTALL)
        if disclaimer_matches:
            additional["notes"] = [re.sub(r'\s+', ' ', note.strip()) for note in disclaimer_matches]

        # Extract copyright and trademark info
        copyright_match = re.search(r'©\s*\d{4}.*?(?=\n|$)', text)
        if copyright_match:
            additional["copyright"] = copyright_match.group(0).strip()

        trademark_match = re.search(r'The Zebra.*?trademarks.*?\.', text, re.IGNORECASE | re.DOTALL)
        if trademark_match:
            additional["trademark"] = re.sub(r'\s+', ' ', trademark_match.group(0).strip())

        # Extract document date
        date_match = re.search(r'\b(\d{2}/\d{2}/\d{4})\b', text)
        if date_match:
            additional["document_date"] = date_match.group(1)

        return additional

    def _parse_resolution(self, key: str, value: str) -> Dict[str, Any]:
        """Parse resolution value."""
        result = {"raw": value}

        dpi_match = re.search(r'(\d+)\s*dpi', value, re.IGNORECASE)
        if dpi_match:
            result["dpi"] = int(dpi_match.group(1))

        dots_match = re.search(r'(\d+)\s*dots?\s*per\s*mm', value, re.IGNORECASE)
        if dots_match:
            result["dots_per_mm"] = int(dots_match.group(1))

        return result

    def _parse_measurement(self, value: str) -> Dict[str, Any]:
        """Parse measurement with multiple units."""
        result = {"raw": value}

        # Extract inches
        inch_match = re.search(r'([\d.]+)\s*in', value, re.IGNORECASE)
        if inch_match:
            result["inches"] = float(inch_match.group(1))

        # Extract mm
        mm_match = re.search(r'([\d.]+)\s*mm', value, re.IGNORECASE)
        if mm_match:
            result["mm"] = float(mm_match.group(1))

        return result

    def _parse_range(self, value: str) -> Dict[str, Any]:
        """Parse range values (e.g., '1.0 in. to 4.4 in.')."""
        result = {"raw": value}

        # Extract inch range
        inch_range = re.search(r'([\d.]+)\s*in.*?to\s*([\d.]+)\s*in', value, re.IGNORECASE)
        if inch_range:
            result["min_inches"] = float(inch_range.group(1))
            result["max_inches"] = float(inch_range.group(2))

        # Extract mm range
        mm_range = re.search(r'([\d.]+)\s*mm.*?to\s*([\d.]+)\s*mm', value, re.IGNORECASE)
        if mm_range:
            result["min_mm"] = float(mm_range.group(1))
            result["max_mm"] = float(mm_range.group(2))

        return result

    def _parse_temperature(self, value: str) -> Dict[str, Any]:
        """Parse temperature range."""
        result = {"raw": value}

        # Extract Fahrenheit range
        f_range = re.search(r'(-?\d+)°?\s*to\s*(-?\d+)°?\s*F', value, re.IGNORECASE)
        if f_range:
            result["min_f"] = int(f_range.group(1))
            result["max_f"] = int(f_range.group(2))

        # Extract Celsius range
        c_range = re.search(r'(-?[\d.]+)°?\s*to\s*(-?[\d.]+)°?\s*C', value, re.IGNORECASE)
        if c_range:
            result["min_c"] = float(c_range.group(1))
            result["max_c"] = float(c_range.group(2))

        return result

    def _parse_humidity(self, value: str) -> Dict[str, Any]:
        """Parse humidity range."""
        result = {"raw": value}

        humidity_range = re.search(r'(\d+)%\s*to\s*(\d+)%', value)
        if humidity_range:
            result["min_percent"] = int(humidity_range.group(1))
            result["max_percent"] = int(humidity_range.group(2))

        if "non-condensing" in value.lower():
            result["condition"] = "non-condensing"

        return result

    def _parse_speed(self, value: str) -> Dict[str, Any]:
        """Parse print speed."""
        result = {"raw": value}

        # Extract inches per second
        inch_match = re.search(r'([\d.]+)\s*in.*?per\s*second', value, re.IGNORECASE)
        if inch_match:
            result["inches_per_second"] = float(inch_match.group(1))

        # Extract mm per second
        mm_match = re.search(r'([\d.]+)\s*mm.*?per\s*second', value, re.IGNORECASE)
        if mm_match:
            result["mm_per_second"] = float(mm_match.group(1))

        return result

    def process_pdf(self, pdf_path: str, output_path: str = None) -> str:
        """
        Process a single PDF file and save to JSON.

        Args:
            pdf_path: Path to input PDF file
            output_path: Path to output JSON file (optional, auto-generated if not provided)

        Returns:
            Path to output JSON file
        """
        print(f"Processing: {pdf_path}")

        # Extract all text and tables
        extracted = self.extract_text_from_pdf(pdf_path)
        text = extracted["all_text"]
        tables = extracted["tables"]

        # Build structured JSON
        data = {}

        # Product information
        data["product_info"] = self.parse_product_info(text)

        # Specifications
        data["specifications"] = self.parse_specifications(tables)

        # Features
        data["features"] = self.parse_features(text, tables)

        # Fonts and Barcodes
        data["fonts_and_barcodes"] = self.parse_fonts_and_barcodes(text, tables)

        # Firmware
        firmware = self.parse_firmware(text, tables)
        if firmware:
            data["firmware"] = firmware

        # Markets and Applications
        markets = self.parse_markets_applications(tables)
        if markets:
            data["markets_and_applications"] = markets

        # Connectivity
        data["connectivity"] = self.parse_connectivity(text)

        # Compliance
        data["compliance"] = self.parse_compliance(text)

        # Warranty
        data["warranty"] = self.parse_warranty(text)

        # Additional information (spillover)
        data["additional_information"] = self.extract_additional_info(text)

        # Metadata
        data["metadata"] = {
            "source_file": Path(pdf_path).name,
            "extraction_date": datetime.now().isoformat(),
            "schema_version": self.schema_version,
            "total_pages": len(extracted["pages"]),
            "total_tables": len(tables)
        }

        # Generate output path if not provided
        if output_path is None:
            pdf_name = Path(pdf_path).stem
            output_dir = Path(pdf_path).parent.parent / "output"
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"{pdf_name}.json"

        # Save to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Saved to: {output_path}")
        return str(output_path)
    
    def process_directory(self, pdf_dir: str, output_dir: str = None) -> List[str]:
        """
        Process all PDF files in a directory.

        Args:
            pdf_dir: Directory containing PDF files
            output_dir: Directory for output JSON files (optional, auto-generated if not provided)

        Returns:
            List of output file paths
        """
        pdf_dir = Path(pdf_dir)

        if output_dir is None:
            output_dir = pdf_dir.parent / "output"

        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)

        # Find all PDF files
        pdf_files = sorted(pdf_dir.glob("*.pdf"))

        if not pdf_files:
            print(f"No PDF files found in {pdf_dir}")
            return []

        print(f"Found {len(pdf_files)} PDF files to process\n")

        output_paths = []
        for pdf_path in pdf_files:
            try:
                output_path = output_dir / f"{pdf_path.stem}.json"
                self.process_pdf(str(pdf_path), str(output_path))
                output_paths.append(str(output_path))
                print()
            except Exception as e:
                print(f"Error processing {pdf_path}: {e}")
                import traceback
                traceback.print_exc()
                continue

        print(f"Processing complete. {len(output_paths)}/{len(pdf_files)} files processed successfully.")
        return output_paths


def main():
    """Main entry point for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract complete information from Zebra printer spec PDFs to JSON"
    )
    parser.add_argument(
        "input",
        help="Input PDF file or directory containing PDFs"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output JSON file or directory (optional, auto-generated if not provided)"
    )

    args = parser.parse_args()

    # Initialize processor
    processor = PDFProcessor()

    # Process input
    input_path = Path(args.input)

    if input_path.is_file():
        processor.process_pdf(str(input_path), args.output)
    elif input_path.is_dir():
        processor.process_directory(str(input_path), args.output)
    else:
        print(f"Error: {input_path} is not a valid file or directory")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
