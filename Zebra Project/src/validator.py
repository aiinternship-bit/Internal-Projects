"""
JSON Validation Script for Zebra Printer Specifications
Validates completeness and quality of extracted JSON data.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime


class ValidationReport:
    """Container for validation results."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.errors = []
        self.warnings = []
        self.info = []
        self.stats = {}

    def add_error(self, message: str):
        self.errors.append(message)

    def add_warning(self, message: str):
        self.warnings.append(message)

    def add_info(self, message: str):
        self.info.append(message)

    def is_valid(self) -> bool:
        """Check if validation passed (no errors)."""
        return len(self.errors) == 0

    def summary(self) -> str:
        """Get summary of validation results."""
        status = "PASS" if self.is_valid() else "FAIL"
        summary = [
            f"\n{'='*80}",
            f"Validation Report: {Path(self.file_path).name}",
            f"Status: {status}",
            f"{'='*80}",
            f"Errors: {len(self.errors)}",
            f"Warnings: {len(self.warnings)}",
            f"Info: {len(self.info)}",
        ]

        if self.stats:
            summary.append(f"\nStatistics:")
            for key, value in self.stats.items():
                summary.append(f"  {key}: {value}")

        if self.errors:
            summary.append(f"\nERRORS:")
            for error in self.errors:
                summary.append(f"  ❌ {error}")

        if self.warnings:
            summary.append(f"\nWARNINGS:")
            for warning in self.warnings:
                summary.append(f"  ⚠️  {warning}")

        if self.info:
            summary.append(f"\nINFO:")
            for info in self.info:
                summary.append(f"  ℹ️  {info}")

        summary.append(f"{'='*80}\n")
        return "\n".join(summary)


class JSONValidator:
    """Validates extracted JSON data for completeness and quality."""

    def __init__(self):
        self.required_top_level_keys = [
            "product_info",
            "specifications",
            "metadata"
        ]
        self.required_product_info_keys = [
            "model",
            "title"
        ]
        self.required_metadata_keys = [
            "source_file",
            "extraction_date",
            "schema_version"
        ]

    def validate_file(self, json_path: str) -> ValidationReport:
        """
        Validate a single JSON file.

        Args:
            json_path: Path to JSON file

        Returns:
            ValidationReport object
        """
        report = ValidationReport(json_path)

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            report.add_error(f"Invalid JSON format: {e}")
            return report
        except FileNotFoundError:
            report.add_error(f"File not found: {json_path}")
            return report

        # Validate structure
        self._validate_structure(data, report)

        # Validate product info
        self._validate_product_info(data.get("product_info", {}), report)

        # Validate specifications
        self._validate_specifications(data.get("specifications", {}), report)

        # Validate metadata
        self._validate_metadata(data.get("metadata", {}), report)

        # Check for completeness
        self._check_completeness(data, report)

        # Calculate statistics
        self._calculate_statistics(data, report)

        return report

    def _validate_structure(self, data: Dict, report: ValidationReport):
        """Validate top-level structure."""
        for key in self.required_top_level_keys:
            if key not in data:
                report.add_error(f"Missing required top-level key: '{key}'")
            elif not isinstance(data[key], dict):
                report.add_error(f"'{key}' must be a dictionary")

    def _validate_product_info(self, product_info: Dict, report: ValidationReport):
        """Validate product_info section."""
        for key in self.required_product_info_keys:
            if key not in product_info:
                report.add_error(f"Missing required product_info key: '{key}'")
            elif not product_info[key]:
                report.add_warning(f"Product info '{key}' is empty")

        # Check for common optional fields
        optional_fields = ["series", "category", "description", "url"]
        for field in optional_fields:
            if field not in product_info or not product_info[field]:
                report.add_info(f"Product info missing optional field: '{field}'")

    def _validate_specifications(self, specs: Dict, report: ValidationReport):
        """Validate specifications section."""
        expected_spec_categories = [
            "printer",
            "physical",
            "media",
            "operating_conditions"
        ]

        for category in expected_spec_categories:
            if category not in specs:
                report.add_warning(f"Missing specification category: '{category}'")
            elif not isinstance(specs[category], dict):
                report.add_error(f"Specification '{category}' must be a dictionary")
            elif not specs[category]:
                report.add_warning(f"Specification category '{category}' is empty")

        # Validate printer specs
        if "printer" in specs and specs["printer"]:
            printer = specs["printer"]
            important_fields = ["resolution", "memory", "print_speed"]
            for field in important_fields:
                if field not in printer:
                    report.add_warning(f"Printer specs missing '{field}'")

        # Validate physical specs
        if "physical" in specs and specs["physical"]:
            physical = specs["physical"]
            if "dimensions" not in physical and "weight" not in physical:
                report.add_warning("Physical specs missing both dimensions and weight")

    def _validate_metadata(self, metadata: Dict, report: ValidationReport):
        """Validate metadata section."""
        for key in self.required_metadata_keys:
            if key not in metadata:
                report.add_error(f"Missing required metadata key: '{key}'")
            elif not metadata[key]:
                report.add_error(f"Metadata '{key}' is empty")

        # Validate extraction date format
        if "extraction_date" in metadata:
            try:
                datetime.fromisoformat(metadata["extraction_date"])
            except (ValueError, TypeError):
                report.add_warning(f"Invalid extraction_date format: {metadata['extraction_date']}")

    def _check_completeness(self, data: Dict, report: ValidationReport):
        """Check for data completeness and richness."""
        # Check if additional_information is used
        if "additional_information" in data:
            if data["additional_information"]:
                report.add_info(f"Additional information captured: {len(data['additional_information'])} items")
            else:
                report.add_info("Additional information section exists but is empty")

        # Check for empty sections
        self._check_empty_sections(data, report, prefix="")

        # Check for common optional sections
        optional_sections = [
            "features",
            "fonts_graphics_symbologies",
            "connectivity",
            "software",
            "compliance",
            "warranty",
            "support_services",
            "supplies"
        ]

        for section in optional_sections:
            if section not in data:
                report.add_info(f"Optional section not present: '{section}'")
            elif not data[section]:
                report.add_warning(f"Optional section '{section}' is present but empty")

    def _check_empty_sections(self, data: Any, report: ValidationReport, prefix: str):
        """Recursively check for empty sections."""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{prefix}.{key}" if prefix else key

                if value is None:
                    report.add_warning(f"Null value at: {current_path}")
                elif isinstance(value, (dict, list)) and not value:
                    report.add_info(f"Empty collection at: {current_path}")
                elif isinstance(value, str) and not value.strip():
                    report.add_warning(f"Empty string at: {current_path}")
                elif isinstance(value, dict):
                    self._check_empty_sections(value, report, current_path)

    def _calculate_statistics(self, data: Dict, report: ValidationReport):
        """Calculate statistics about the extracted data."""
        stats = {}

        # Count total keys
        stats["total_top_level_keys"] = len(data.keys())

        # Count specifications
        if "specifications" in data:
            stats["specification_categories"] = len(data["specifications"].keys())

        # Count features
        if "features" in data:
            features = data["features"]
            if isinstance(features, dict):
                stats["standard_features"] = len(features.get("standard", []))
                stats["optional_features"] = len(features.get("optional", []))

        # Count connectivity options
        if "connectivity" in data and isinstance(data["connectivity"], list):
            stats["connectivity_options"] = len(data["connectivity"])

        # Check for fonts/symbologies
        if "fonts_graphics_symbologies" in data:
            fgs = data["fonts_graphics_symbologies"]
            if isinstance(fgs, dict):
                stats["1d_barcodes"] = len(fgs.get("one_d_bar_codes", []))
                stats["2d_barcodes"] = len(fgs.get("two_d_bar_codes", []))

        # Count support services
        if "support_services" in data and isinstance(data["support_services"], list):
            stats["support_services"] = len(data["support_services"])

        # Count additional information items
        if "additional_information" in data and isinstance(data["additional_information"], dict):
            stats["additional_info_items"] = len(data["additional_information"])

        # Calculate data richness score (0-100)
        score = 0
        if data.get("product_info", {}).get("description"):
            score += 10
        if data.get("specifications", {}).get("printer"):
            score += 15
        if data.get("specifications", {}).get("physical"):
            score += 10
        if data.get("specifications", {}).get("media"):
            score += 10
        if data.get("features"):
            score += 10
        if data.get("fonts_graphics_symbologies"):
            score += 10
        if data.get("connectivity"):
            score += 5
        if data.get("software"):
            score += 10
        if data.get("compliance"):
            score += 10
        if data.get("warranty"):
            score += 5
        if data.get("support_services"):
            score += 5

        stats["data_richness_score"] = score

        report.stats = stats

    def validate_directory(self, json_dir: str, output_report: str = None) -> List[ValidationReport]:
        json_dir = Path(json_dir)
        json_files = sorted(json_dir.glob("*.json"))

        if not json_files:
            print(f"No JSON files found in {json_dir}")
            return []

        print(f"Validating {len(json_files)} JSON files...\n")

        reports = []
        for json_file in json_files:
            report = self.validate_file(str(json_file))
            reports.append(report)
            print(report.summary())

        # Generate summary
        total_files = len(reports)
        passed_files = sum(1 for r in reports if r.is_valid())
        failed_files = total_files - passed_files

        summary = [
            f"\n{'='*80}",
            f"OVERALL VALIDATION SUMMARY",
            f"{'='*80}",
            f"Total files: {total_files}",
            f"Passed: {passed_files}",
            f"Failed: {failed_files}",
            f"Success rate: {(passed_files/total_files*100):.1f}%",
            f"{'='*80}\n"
        ]

        summary_text = "\n".join(summary)
        print(summary_text)

        # Save report if requested
        if output_report:
            with open(output_report, 'w', encoding='utf-8') as f:
                f.write(summary_text)
                f.write("\n\nDETAILED REPORTS:\n")
                for report in reports:
                    f.write(report.summary())
            print(f"Detailed report saved to: {output_report}")

        return reports


def main():
    """Main entry point for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate extracted JSON files for completeness and quality"
    )
    parser.add_argument(
        "input",
        help="Input JSON file or directory containing JSON files"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output validation report file (for directory validation)"
    )

    args = parser.parse_args()

    validator = JSONValidator()
    input_path = Path(args.input)

    if input_path.is_file():
        report = validator.validate_file(str(input_path))
        print(report.summary())
        exit(0 if report.is_valid() else 1)

    elif input_path.is_dir():
        reports = validator.validate_directory(str(input_path), args.output)
        all_valid = all(r.is_valid() for r in reports)
        exit(0 if all_valid else 1)

    else:
        print(f"Error: {input_path} is not a valid file or directory")
        exit(1)


if __name__ == "__main__":
    main()
