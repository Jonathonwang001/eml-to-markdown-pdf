#!/usr/bin/env python3
"""
EML to Markdown/PDF Converter
从EML邮件文件中提取邮件正文HTML，转换为Markdown和优化排版的PDF

使用方法:
    python eml_to_markdown_pdf.py <eml_file> [output_dir]
"""

import sys
import email
import re
from pathlib import Path
from bs4 import BeautifulSoup
from html import unescape
from weasyprint import HTML, CSS
import io

def extract_html_from_eml(eml_path):
    """从EML文件中提取邮件正文HTML"""
    with open(eml_path, 'rb') as f:
        msg = email.message_from_binary_file(f)
    
    html_content = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                charset = part.get_content_charset() or 'utf-8'
                html_content = part.get_payload(decode=True).decode(charset, errors='ignore')
                break
    
    if not html_content:
        raise ValueError("未找到HTML内容")
    
    return html_content

def optimize_html_for_pdf(html_content):
    """优化HTML以改进PDF排版"""
    
    # 添加优化的CSS样式
    optimization_css = """
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            line-height: 1.6;
            color: #1a1a1a;
        }
        
        /* 避免不合理的分页 */
        h1, h2, h3, h4, h5, h6 {
            page-break-after: avoid;
            page-break-inside: avoid;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }
        
        p {
            page-break-inside: avoid;
            margin: 0.5em 0;
        }
        
        table {
            page-break-inside: avoid;
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        
        th {
            background-color: #f5f5f5;
            font-weight: bold;
        }
        
        ul, ol {
            page-break-inside: avoid;
            margin: 0.5em 0;
            padding-left: 2em;
        }
        
        li {
            margin: 0.25em 0;
        }
        
        /* 避免孤立的行 */
        div {
            page-break-inside: avoid;
        }
        
        /* 分隔符样式 */
        hr {
            page-break-after: avoid;
            border: none;
            border-top: 2px solid #1a1a1a;
            margin: 1.5em 0;
        }
    </style>
    """
    
    # 在head中插入优化CSS
    if '<head>' in html_content:
        html_content = html_content.replace('<head>', '<head>' + optimization_css)
    elif '<html>' in html_content:
        html_content = html_content.replace('<html>', '<html><head>' + optimization_css + '</head>')
    else:
        html_content = optimization_css + html_content
    
    return html_content

def html_to_markdown(html_content):
    """将HTML转换为Markdown"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 移除style和script
    for tag in soup(['style', 'script']):
        tag.decompose()
    
    body = soup.find('body')
    if not body:
        body = soup
    
    markdown_lines = []
    
    def process_element(elem):
        for child in elem.children:
            if isinstance(child, str):
                text = child.strip()
                if text:
                    text = unescape(text)
                    markdown_lines.append(text)
            else:
                tag_name = child.name
                
                if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    level = int(tag_name[1])
                    text = child.get_text().strip()
                    if text:
                        text = unescape(text)
                        markdown_lines.append(f"\n{'#' * level} {text}\n")
                        
                elif tag_name == 'p':
                    text = child.get_text().strip()
                    if text:
                        text = unescape(text)
                        markdown_lines.append(f"\n{text}\n")
                        
                elif tag_name == 'table':
                    rows = child.find_all('tr')
                    if rows:
                        markdown_lines.append('\n')
                        for i, row in enumerate(rows):
                            cells = row.find_all(['td', 'th'])
                            cell_texts = [unescape(cell.get_text().strip()) for cell in cells]
                            if cell_texts:
                                markdown_lines.append('| ' + ' | '.join(cell_texts) + ' |')
                                if i == 0:
                                    markdown_lines.append('|' + '|'.join(['---'] * len(cell_texts)) + '|')
                        markdown_lines.append('\n')
                        
                elif tag_name == 'ul':
                    items = child.find_all('li', recursive=False)
                    if items:
                        markdown_lines.append('\n')
                        for item in items:
                            text = item.get_text().strip()
                            if text:
                                text = unescape(text)
                                markdown_lines.append(f'- {text}')
                        markdown_lines.append('\n')
                        
                elif tag_name == 'ol':
                    items = child.find_all('li', recursive=False)
                    if items:
                        markdown_lines.append('\n')
                        for j, item in enumerate(items, 1):
                            text = item.get_text().strip()
                            if text:
                                text = unescape(text)
                                markdown_lines.append(f'{j}. {text}')
                        markdown_lines.append('\n')
                        
                elif tag_name == 'br':
                    markdown_lines.append('\n')
                    
                elif tag_name in ['strong', 'b']:
                    text = child.get_text().strip()
                    if text:
                        text = unescape(text)
                        markdown_lines.append(f'**{text}**')
                        
                elif tag_name in ['em', 'i']:
                    text = child.get_text().strip()
                    if text:
                        text = unescape(text)
                        markdown_lines.append(f'*{text}*')
                        
                elif tag_name == 'a':
                    text = child.get_text().strip()
                    href = child.get('href', '#')
                    if text:
                        text = unescape(text)
                        markdown_lines.append(f'[{text}]({href})')
                        
                elif tag_name in ['span', 'section', 'article', 'main', 'div']:
                    process_element(child)
                else:
                    process_element(child)
    
    process_element(body)
    markdown = '\n'.join(markdown_lines)
    
    # 清理多余空行
    markdown = re.sub(r'\n\n\n+', '\n\n', markdown)
    return markdown.strip()

def convert_eml_to_files(eml_path, output_dir=None):
    """主转换函数"""
    
    eml_path = Path(eml_path)
    if not eml_path.exists():
        raise FileNotFoundError(f"EML文件不存在: {eml_path}")
    
    if output_dir is None:
        output_dir = eml_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成输出文件名
    base_name = eml_path.stem
    md_path = output_dir / f"{base_name}.md"
    pdf_path = output_dir / f"{base_name}.pdf"
    html_path = output_dir / f"{base_name}_optimized.html"
    
    print(f"📧 正在处理: {eml_path.name}")
    
    # 提取HTML
    print("  ✓ 提取邮件HTML...")
    html_content = extract_html_from_eml(eml_path)
    
    # 优化HTML排版
    print("  ✓ 优化HTML排版...")
    optimized_html = optimize_html_for_pdf(html_content)
    
    # 保存优化后的HTML
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(optimized_html)
    
    # 转换为Markdown
    print("  ✓ 转换为Markdown...")
    markdown = html_to_markdown(optimized_html)
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    # 转换为PDF
    print("  ✓ 转换为PDF...")
    try:
        HTML(string=optimized_html, base_url='/').write_pdf(pdf_path)
    except Exception as e:
        print(f"  ⚠ PDF生成警告: {e}")
    
    print(f"\n✅ 转换完成!")
    print(f"  📄 Markdown: {md_path}")
    print(f"  📕 PDF: {pdf_path}")
    print(f"  🔧 优化HTML: {html_path}")
    
    return {
        'markdown': str(md_path),
        'pdf': str(pdf_path),
        'html': str(html_path)
    }

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python eml_to_markdown_pdf.py <eml_file> [output_dir]")
        sys.exit(1)
    
    eml_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result = convert_eml_to_files(eml_file, output_dir)
        print(f"\n结果: {result}")
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

