# Paystub NER Tagging Results

**Source Image:** `sample_paystub.png`
**OCR File:** `sample_ocr.tsv`

## Tagged Entities

| Tag | Value | Confidence |
|-----|-------|------------|
| EMPLOYER_COMPANY_NAME | Anyhow AI | 98% |
| EMPLOYEE_NAME | Yuyao Bai | 96% |
| PAY_PERIOD_START_DATE | 01/16/2026 | 95% |
| PAY_PERIOD_END_DATE | 01/31/2026 | 95% |
| PAY_DATE | 02/06/2026 | 97% |
| REGULAR_PAY_AMOUNT | $4,166.67 | 96% |
| GROSS_PAY_YTD | $12,500.67 | 96% |
| GROSS_PAY_CURRENT | $4,166.67 | 96% |
| NET_PAY_YTD | $8,683.53 | 96% |
| NET_PAY_CURRENT | $2,894.29 | 97% |
| DEDUCTION_YTD | $3,817.14 | 96% |
| DEDUCTION_CURRENT | $1,272.38 | 96% |
| EMPLOYEE_ADDRESS | - | - |
| COMPANY_ADDRESS | 81 Wellesley Street East, Toronto, ON M4Y 0C5 | 95% |

## Tag Schema

```
- EMPLOYER_COMPANY_NAME
- EMPLOYEE_NAME
- PAY_PERIOD_START_DATE
- PAY_PERIOD_END_DATE
- PAY_DATE
- REGULAR_PAY_AMOUNT
- GROSS_PAY_YTD
- GROSS_PAY_CURRENT
- NET_PAY_YTD
- NET_PAY_CURRENT
- DEDUCTION_YTD
- DEDUCTION_CURRENT
- EMPLOYEE_ADDRESS
- COMPANY_ADDRESS
```

## Usage

```bash
python paystub_tagger.py --image <image_path> --ocr <ocr.tsv> --output <output_base>
```

### Options
- `--image, -i`: Path to paystub image (required)
- `--ocr, -o`: Path to OCR TSV file (required)
- `--output, -out`: Output filename base without extension (default: tagged_output)
- `--format, -f`: Output formats: json, csv, tsv, md, all (default: all)
