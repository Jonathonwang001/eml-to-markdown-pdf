# EML to Markdown & PDF Converter

Convert EML email files to clean Markdown and optimized PDF documents.

## Description

This tool converts RFC 822 email files (.eml) to clean Markdown and properly formatted PDF documents. It extracts only the email body content (removing email client UI and styling), optimizes the layout to avoid awkward pagination, and produces both human-readable and portable formats.

## Features

- **Extracts email body HTML** - Removes email client UI, headers, and CSS framework code
- **Optimizes PDF layout** - Prevents empty pages, orphaned lines, and awkward breaks
- **Generates Markdown** - Creates editable text format preserving structure (headings, tables, lists)
- **Preserves formatting** - Maintains tables, bold/italic text, links, and document hierarchy

## Installation

```bash
# Clone the repository
git clone https://github.com/Jonathonwang001/eml-to-markdown-pdf.git
cd eml-to-markdown-pdf

# Install dependencies
pip install beautifulsoup4 weasyprint
```

## Usage

### Command Line

```bash
python scripts/eml_to_markdown_pdf.py <eml_file> [output_dir]
```

**Parameters:**
- `eml_file` (required): Path to the .eml file
- `output_dir` (optional): Output directory. Defaults to same directory as input file

**Output:**
- `{filename}.md` - Markdown version
- `{filename}.pdf` - Optimized PDF
- `{filename}_optimized.html` - Intermediate HTML with pagination CSS

### Example

```bash
python scripts/eml_to_markdown_pdf.py report.eml ./output/
```

### Python API

```python
from scripts.eml_to_markdown_pdf import convert_eml_to_files

result = convert_eml_to_files(
    eml_path="/path/to/email.eml",
    output_dir="/path/to/output"
)

print(result['markdown'])  # Path to .md file
print(result['pdf'])       # Path to .pdf file
print(result['html'])      # Path to optimized .html file
```

## Requirements

- Python 3.7+
- beautifulsoup4
- weasyprint

## License

MIT License

## Author

Jonathonwang001
