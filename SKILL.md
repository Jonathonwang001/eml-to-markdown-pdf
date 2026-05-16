---
name: eml-to-markdown-pdf
description: Convert EML email files to Markdown and optimized PDF. Extracts email body HTML content, removes email client UI/CSS, and generates clean documents with proper pagination. Use when converting email reports, newsletters, or formatted email content to portable document formats.
---

# EML to Markdown & PDF Converter

This skill converts RFC 822 email files (.eml) to clean Markdown and properly formatted PDF documents. It extracts only the email body content (removing email client UI and styling), optimizes the layout to avoid awkward pagination, and produces both human-readable and portable formats.

## When to Use

- Converting email reports (investment reports, newsletters, etc.) to shareable documents
- Extracting email content for archival or documentation
- Converting formatted HTML emails to Markdown for editing
- Creating PDF versions of emails with optimized page breaks and layout

## Key Features

- **Extracts email body HTML** - Removes email client UI, headers, and CSS framework code
- **Optimizes PDF layout** - Prevents empty pages, orphaned lines, and awkward breaks
- **Generates Markdown** - Creates editable text format preserving structure (headings, tables, lists)
- **Preserves formatting** - Maintains tables, bold/italic text, links, and document hierarchy

## Usage

### Command Line

```bash
python /home/ubuntu/skills/eml-to-markdown-pdf/scripts/eml_to_markdown_pdf.py <eml_file> [output_dir]
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
python eml_to_markdown_pdf.py report.eml ./output/
```

### Python API

```python
from eml_to_markdown_pdf import convert_eml_to_files

result = convert_eml_to_files(
    eml_path="/path/to/email.eml",
    output_dir="/path/to/output"
)

print(result['markdown'])  # Path to .md file
print(result['pdf'])       # Path to .pdf file
print(result['html'])      # Path to optimized .html file
```

## How It Works

1. **Extract HTML from EML** - Reads the email file and extracts the HTML body content
2. **Optimize for PDF** - Adds CSS rules to prevent:
   - Orphaned headings at page bottom
   - Tables split across pages
   - Awkward page breaks within content blocks
3. **Generate Markdown** - Parses HTML and converts to clean Markdown with proper formatting
4. **Generate PDF** - Uses WeasyPrint to render optimized HTML to PDF with proper pagination

## Technical Details

### Pagination Optimization

The skill adds CSS rules that:
- Mark headings, tables, lists as `page-break-inside: avoid`
- Ensure proper spacing between sections
- Prevent single lines at page boundaries
- Maintain readable content flow across pages

### HTML Extraction

The script:
- Reads RFC 822 format email files
- Finds the `text/html` MIME part
- Handles character encoding automatically
- Removes script and style tags before conversion

### Markdown Conversion

Supports:
- Headings (h1-h6)
- Paragraphs with proper spacing
- Tables with headers
- Unordered and ordered lists
- Bold, italic, and links
- Line breaks

## Limitations

- Only processes the HTML part of multipart emails (ignores plain text alternatives)
- Complex CSS styling may not fully transfer to PDF
- Embedded images are preserved if they have valid URLs
- Very large emails (>50MB) may take time to process

## Troubleshooting

**"未找到HTML内容" (No HTML content found)**
- The email file may only contain plain text. Check if it has an HTML part.

**PDF has unexpected layout**
- Try adjusting the CSS in `optimize_html_for_pdf()` function
- Increase margins or adjust `page-break-inside` rules

**Markdown has formatting issues**
- Complex nested HTML may not convert perfectly
- Edit the .md file manually for fine-tuning

## Files

- `scripts/eml_to_markdown_pdf.py` - Main conversion script (executable)
