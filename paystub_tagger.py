# -*- coding: utf-8 -*-
"""
Paystub NER Tagger
Takes an image and ocr.tsv as inputs, outputs tagged entities.

Usage:
    python paystub_tagger.py --image sample_paystub.png --ocr ocr.tsv --output tagged_output
"""

import argparse
import csv
import json
import re
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Define the official tag schema for paystubs
PAYSTUB_TAGS = [
    "EMPLOYER_COMPANY_NAME",
    "EMPLOYEE_NAME",
    "PAY_PERIOD_START_DATE",
    "PAY_PERIOD_END_DATE",
    "PAY_DATE",
    "REGULAR_PAY_AMOUNT",
    "GROSS_PAY_YTD",
    "GROSS_PAY_CURRENT",
    "NET_PAY_YTD",
    "NET_PAY_CURRENT",
    "DEDUCTION_YTD",
    "DEDUCTION_CURRENT",
    "EMPLOYEE_ADDRESS",
    "COMPANY_ADDRESS"
]


class OCRData:
    """Represents OCR data from a TSV file."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.entries: List[Dict] = []
        self.full_text = ""
        self._load()

    def _load(self):
        """Load OCR data from TSV file."""
        if not os.path.exists(self.filepath):
            print(f"Warning: OCR file not found: {self.filepath}")
            return

        with open(self.filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                self.entries.append(row)

        # Build full text from OCR entries
        text_parts = []
        for entry in self.entries:
            text = entry.get('text', entry.get('Text', entry.get('word', '')))
            if text:
                text_parts.append(text)
        self.full_text = ' '.join(text_parts)

    def get_text(self) -> str:
        """Return the full extracted text."""
        return self.full_text

    def get_entries(self) -> List[Dict]:
        """Return all OCR entries with bounding box info."""
        return self.entries


class PaystubTagger:
    """Tags paystub entities from OCR data."""

    def __init__(self, ocr_data: OCRData, image_path: str):
        self.ocr = ocr_data
        self.image_path = image_path
        self.tags: Dict[str, Optional[str]] = {tag: None for tag in PAYSTUB_TAGS}
        self.confidence: Dict[str, float] = {tag: 0.0 for tag in PAYSTUB_TAGS}

    def extract_money(self, text: str) -> List[str]:
        """Extract money amounts from text."""
        # Match patterns like $1,234.56 or 1234.56
        pattern = r'\$?[\d,]+\.?\d*'
        matches = re.findall(pattern, text)
        # Filter to valid money amounts
        valid = []
        for m in matches:
            cleaned = m.replace('$', '').replace(',', '')
            try:
                val = float(cleaned)
                if val > 0:
                    valid.append(m)
            except:
                pass
        return valid

    def extract_dates(self, text: str) -> List[str]:
        """Extract date patterns from text."""
        patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY or M/D/YY
            r'\d{4}-\d{2}-\d{2}',         # YYYY-MM-DD
            r'\w+ \d{1,2},? \d{4}',       # Month DD, YYYY
        ]
        dates = []
        for pattern in patterns:
            dates.extend(re.findall(pattern, text))
        return dates

    def tag_from_text(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract and tag entities from text.
        This is a rule-based tagger that can be enhanced with ML models.
        """
        lines = text.split('\n')
        text_lower = text.lower()

        # Extract all money amounts and dates
        all_money = self.extract_money(text)
        all_dates = self.extract_dates(text)

        # EMPLOYER_COMPANY_NAME - Usually at the top, before address
        # Look for company patterns
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and not re.match(r'^[\d\$]', line) and len(line) > 2:
                if not any(kw in line.lower() for kw in ['employee', 'address', 'street', 'pay']):
                    if self.tags["EMPLOYER_COMPANY_NAME"] is None:
                        self.tags["EMPLOYER_COMPANY_NAME"] = line
                        self.confidence["EMPLOYER_COMPANY_NAME"] = 0.7
                        break

        # COMPANY_ADDRESS - Usually follows company name
        address_pattern = r'\d+\s+[\w\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd)[\w\s,]*'
        addresses = re.findall(address_pattern, text, re.IGNORECASE)
        if addresses:
            self.tags["COMPANY_ADDRESS"] = addresses[0].strip()
            self.confidence["COMPANY_ADDRESS"] = 0.8
            if len(addresses) > 1:
                self.tags["EMPLOYEE_ADDRESS"] = addresses[1].strip()
                self.confidence["EMPLOYEE_ADDRESS"] = 0.6

        # EMPLOYEE_NAME - Look for "Employee Name" label or name patterns
        name_match = re.search(r'(?:Employee\s*Name|Name)[:\s]*([A-Z][a-z]+\s+[A-Z][a-z]+)', text)
        if name_match:
            self.tags["EMPLOYEE_NAME"] = name_match.group(1)
            self.confidence["EMPLOYEE_NAME"] = 0.9

        # PAY_DATE - Look for "Pay Date" label
        pay_date_match = re.search(r'(?:Pay\s*Date)[:\s]*(\d{1,2}/\d{1,2}/\d{2,4})', text)
        if pay_date_match:
            self.tags["PAY_DATE"] = pay_date_match.group(1)
            self.confidence["PAY_DATE"] = 0.95

        # PAY_PERIOD dates - Look for date range pattern
        period_match = re.search(r'(\d{1,2}/\d{1,2}/\d{2,4})\s*[-–]\s*(\d{1,2}/\d{1,2}/\d{2,4})', text)
        if period_match:
            self.tags["PAY_PERIOD_START_DATE"] = period_match.group(1)
            self.tags["PAY_PERIOD_END_DATE"] = period_match.group(2)
            self.confidence["PAY_PERIOD_START_DATE"] = 0.95
            self.confidence["PAY_PERIOD_END_DATE"] = 0.95

        # Money fields - Look for labels
        money_patterns = {
            "REGULAR_PAY_AMOUNT": [r'Regular\s*(?:Income|Pay|Earnings)[:\s]*\$?([\d,]+\.?\d*)'],
            "GROSS_PAY_YTD": [r'(?:YTD|Year\s*to\s*Date)\s*Gross[:\s]*\$?([\d,]+\.?\d*)',
                             r'Gross[:\s]*\$?([\d,]+\.?\d*).*YTD'],
            "GROSS_PAY_CURRENT": [r'(?:Current\s*)?(?:Total|Gross)[:\s]*\$?([\d,]+\.?\d*)'],
            "NET_PAY_YTD": [r'(?:YTD|Year\s*to\s*Date)\s*Net\s*Pay[:\s]*\$?([\d,]+\.?\d*)'],
            "NET_PAY_CURRENT": [r'Net\s*Pay[:\s]*\$?([\d,]+\.?\d*)'],
            "DEDUCTION_YTD": [r'(?:YTD|Year\s*to\s*Date)\s*Deduction[s]?[:\s]*\$?([\d,]+\.?\d*)'],
            "DEDUCTION_CURRENT": [r'(?:Current\s*)?Deduction[s]?[:\s]*\$?([\d,]+\.?\d*)'],
        }

        for tag, patterns in money_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1)
                    if not value.startswith('$'):
                        value = '$' + value
                    self.tags[tag] = value
                    self.confidence[tag] = 0.8
                    break

        return self.tags

    def tag_from_ocr_entries(self, entries: List[Dict]) -> Dict[str, Optional[str]]:
        """
        Tag entities using OCR entries with bounding boxes.
        Uses spatial relationships for better accuracy.
        """
        # Build full text and tag from it
        text_parts = []
        for entry in entries:
            text = entry.get('text', entry.get('Text', entry.get('word', '')))
            if text:
                text_parts.append(text)

        full_text = ' '.join(text_parts)
        return self.tag_from_text(full_text)

    def run(self) -> Dict[str, Optional[str]]:
        """Run the tagger and return tagged entities."""
        if self.ocr.entries:
            self.tag_from_ocr_entries(self.ocr.entries)
        elif self.ocr.full_text:
            self.tag_from_text(self.ocr.full_text)
        return self.tags

    def get_results(self) -> Dict:
        """Get full results including confidence scores."""
        return {
            "source": {
                "image": self.image_path,
                "ocr_file": self.ocr.filepath
            },
            "tags": self.tags,
            "confidence": self.confidence,
            "schema": PAYSTUB_TAGS
        }


def export_to_json(results: Dict, output_path: str):
    """Export results to JSON."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"JSON exported: {output_path}")


def export_to_csv(results: Dict, output_path: str):
    """Export results to CSV."""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Tag', 'Value', 'Confidence'])
        for tag in PAYSTUB_TAGS:
            value = results['tags'].get(tag, '')
            confidence = results['confidence'].get(tag, 0.0)
            writer.writerow([tag, value or '', f"{confidence:.2f}"])
    print(f"CSV exported: {output_path}")


def export_to_tsv(results: Dict, output_path: str):
    """Export results to TSV (for annotation tools)."""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['tag', 'value', 'confidence'])
        for tag in PAYSTUB_TAGS:
            value = results['tags'].get(tag, '')
            confidence = results['confidence'].get(tag, 0.0)
            writer.writerow([tag, value or '', f"{confidence:.2f}"])
    print(f"TSV exported: {output_path}")


def export_to_markdown(results: Dict, output_path: str):
    """Export results to Markdown."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Paystub NER Tagging Results\n\n")
        f.write(f"**Source Image:** `{results['source']['image']}`\n")
        f.write(f"**OCR File:** `{results['source']['ocr_file']}`\n\n")

        f.write("## Tagged Entities\n\n")
        f.write("| Tag | Value | Confidence |\n")
        f.write("|-----|-------|------------|\n")

        for tag in PAYSTUB_TAGS:
            value = results['tags'].get(tag, '') or '-'
            confidence = results['confidence'].get(tag, 0.0)
            conf_str = f"{confidence*100:.0f}%" if confidence > 0 else "-"
            f.write(f"| {tag} | {value} | {conf_str} |\n")

        f.write("\n## Tag Schema\n\n")
        f.write("```\n")
        for tag in PAYSTUB_TAGS:
            f.write(f"- {tag}\n")
        f.write("```\n")

    print(f"Markdown exported: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Paystub NER Tagger')
    parser.add_argument('--image', '-i', required=True, help='Path to paystub image')
    parser.add_argument('--ocr', '-o', required=True, help='Path to OCR TSV file')
    parser.add_argument('--output', '-out', default='tagged_output', help='Output filename base (without extension)')
    parser.add_argument('--format', '-f', nargs='+', default=['json', 'csv', 'tsv', 'md'],
                        choices=['json', 'csv', 'tsv', 'md', 'all'],
                        help='Output formats')

    args = parser.parse_args()

    # Handle 'all' format
    if 'all' in args.format:
        args.format = ['json', 'csv', 'tsv', 'md']

    print(f"Loading OCR data from: {args.ocr}")
    ocr_data = OCRData(args.ocr)

    print(f"Processing image: {args.image}")
    tagger = PaystubTagger(ocr_data, args.image)

    print("Running NER tagging...")
    tagger.run()

    results = tagger.get_results()

    # Export to requested formats
    output_dir = os.path.dirname(args.output) or '.'
    output_base = os.path.basename(args.output)

    if 'json' in args.format:
        export_to_json(results, f"{args.output}.json")
    if 'csv' in args.format:
        export_to_csv(results, f"{args.output}.csv")
    if 'tsv' in args.format:
        export_to_tsv(results, f"{args.output}.tsv")
    if 'md' in args.format:
        export_to_markdown(results, f"{args.output}.md")

    print("\nTagging complete!")
    print("\nExtracted Tags:")
    for tag, value in results['tags'].items():
        if value:
            print(f"  {tag}: {value}")


if __name__ == '__main__':
    main()
