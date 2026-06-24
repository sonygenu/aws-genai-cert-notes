"""
Step 1: Generate a digital PDF that contains an embedded image (a chart).

Creates a PDF with:
- Text content (report title, paragraphs)
- An embedded bar chart image (generated with Pillow)

Run:
    python3 create_pdf_with_image.py
"""
from PIL import Image, ImageDraw, ImageFont
import fitz  # pymupdf


def create_chart_image(output_path: str):
    """Create a simple bar chart image."""
    img = Image.new("RGB", (500, 300), "white")
    draw = ImageDraw.Draw(img)

    # Title
    draw.text((150, 10), "Q2 Revenue by Region", fill="black")

    # Bars
    bars = [
        ("US", 180, "steelblue"),
        ("EU", 120, "coral"),
        ("APAC", 90, "seagreen"),
        ("LATAM", 60, "goldenrod"),
    ]

    x = 80
    for label, height, color in bars:
        # Bar
        draw.rectangle([x, 280 - height, x + 60, 280], fill=color)
        # Label
        draw.text((x + 15, 285), label, fill="black")
        # Value
        draw.text((x + 15, 280 - height - 20), f"${height}K", fill="black")
        x += 100

    # Axes
    draw.line([(60, 30), (60, 280)], fill="black", width=2)
    draw.line([(60, 280), (480, 280)], fill="black", width=2)

    img.save(output_path)
    print(f"  ✓ Chart image created: {output_path}")
    return img


def create_pdf_with_image(output_path: str, image_path: str):
    """Create a PDF with text and an embedded image."""
    doc = fitz.open()

    # Page 1: Title + intro text
    page = doc.new_page()

    title = "QUARTERLY REVENUE REPORT - Q2 2026"
    body = """Executive Summary:

Total revenue for Q2 2026 reached $450K across all regions, representing a 15% 
increase over Q1. The US market continues to lead with $180K, followed by EU ($120K), 
APAC ($90K), and LATAM ($60K).

Key highlights:
- US grew 20% driven by enterprise deals
- EU stabilized after Q1 regulatory headwinds
- APAC showed strongest growth rate (35% QoQ)
- LATAM expanding into 3 new countries

See the chart below for regional breakdown:"""

    page.insert_text((72, 72), title, fontsize=14)
    page.insert_text((72, 100), body, fontsize=11)

    # Insert the chart image into the PDF
    img_rect = fitz.Rect(72, 350, 500, 600)  # x0, y0, x1, y1
    page.insert_image(img_rect, filename=image_path)

    # Page 2: Additional text
    page2 = doc.new_page()
    page2_text = """Recommendations:

1. Increase investment in APAC sales team (highest growth potential)
2. Launch localized marketing for LATAM expansion
3. Maintain US enterprise focus with dedicated account managers
4. Monitor EU regulatory changes for compliance impact

Next review: September 15, 2026
Prepared by: Finance Team"""

    page2.insert_text((72, 72), page2_text, fontsize=11)

    doc.save(output_path)
    doc.close()
    print(f"  ✓ PDF with image created: {output_path}")


if __name__ == "__main__":
    print("\n📄 Creating PDF with embedded chart image...\n")
    create_chart_image("chart.png")
    create_pdf_with_image("report_with_chart.pdf", "chart.png")
    print("\n✅ Done! Files created: chart.png, report_with_chart.pdf")
