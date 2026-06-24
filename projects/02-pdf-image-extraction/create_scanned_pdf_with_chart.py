"""
Generate a SCANNED PDF that contains a chart image.

This simulates what a scanner produces — the chart and text are
all rendered as images (no selectable text, needs OCR to read).

Run:
    python3 create_scanned_pdf_with_chart.py
    open scanned_report_with_chart.pdf
"""
from PIL import Image, ImageDraw


def create_scanned_pdf_with_chart(output_path: str):
    """Create a scanned PDF with a chart (everything is an image)."""
    pages = []

    # --- Page 1: Title + text + bar chart (all as one image) ---
    img1 = Image.new("RGB", (612, 792), "white")
    draw1 = ImageDraw.Draw(img1)

    # Title
    draw1.text((72, 40), "QUARTERLY REVENUE REPORT - Q2 2026", fill="black")
    draw1.text((72, 70), "=" * 50, fill="black")

    # Body text
    lines = [
        "Executive Summary:",
        "",
        "Total revenue for Q2 2026 reached $450K across all regions,",
        "representing a 15% increase over Q1.",
        "",
        "Regional Performance:",
        "- US: $180K (20% growth, driven by enterprise deals)",
        "- EU: $120K (stabilized after Q1 headwinds)",
        "- APAC: $90K (strongest growth rate: 35% QoQ)",
        "- LATAM: $60K (expanding into 3 new countries)",
        "",
        "Revenue by Region (Bar Chart):",
    ]

    y = 100
    for line in lines:
        draw1.text((72, y), line, fill="black")
        y += 22

    # Draw a bar chart
    chart_y = y + 10
    bars = [
        ("US", 150, "steelblue"),
        ("EU", 100, "coral"),
        ("APAC", 75, "seagreen"),
        ("LATAM", 50, "goldenrod"),
    ]

    # Chart background
    draw1.rectangle([72, chart_y, 540, chart_y + 220], outline="gray")

    # Bars
    x = 110
    for label, height, color in bars:
        bar_bottom = chart_y + 200
        bar_top = bar_bottom - height
        draw1.rectangle([x, bar_top, x + 70, bar_bottom], fill=color)
        draw1.text((x + 20, bar_bottom + 5), label, fill="black")
        draw1.text((x + 15, bar_top - 20), f"${height}K", fill="black")
        x += 110

    # Axes
    draw1.line([(90, chart_y + 10), (90, chart_y + 200)], fill="black", width=2)
    draw1.line([(90, chart_y + 200), (530, chart_y + 200)], fill="black", width=2)

    # Y-axis labels
    draw1.text((60, chart_y + 10), "$200K", fill="gray")
    draw1.text((60, chart_y + 100), "$100K", fill="gray")
    draw1.text((60, chart_y + 190), "$0", fill="gray")

    pages.append(img1)

    # --- Page 2: Pie chart + recommendations (all as image) ---
    img2 = Image.new("RGB", (612, 792), "white")
    draw2 = ImageDraw.Draw(img2)

    draw2.text((72, 40), "MARKET SHARE BREAKDOWN", fill="black")
    draw2.text((72, 70), "=" * 40, fill="black")

    # Simple pie chart representation (draw colored circles/arcs)
    center_x, center_y = 300, 250
    radius = 120

    # Draw pie segments as colored wedges
    draw2.pieslice([center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius],
                   start=0, end=144, fill="steelblue")      # US 40%
    draw2.pieslice([center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius],
                   start=144, end=240, fill="coral")         # EU 27%
    draw2.pieslice([center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius],
                   start=240, end=312, fill="seagreen")      # APAC 20%
    draw2.pieslice([center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius],
                   start=312, end=360, fill="goldenrod")     # LATAM 13%

    # Legend
    legend_y = 400
    legend_items = [
        ("US - 40%", "steelblue"),
        ("EU - 27%", "coral"),
        ("APAC - 20%", "seagreen"),
        ("LATAM - 13%", "goldenrod"),
    ]
    for label, color in legend_items:
        draw2.rectangle([200, legend_y, 220, legend_y + 15], fill=color)
        draw2.text((230, legend_y), label, fill="black")
        legend_y += 25

    # Recommendations text below
    rec_y = 520
    recommendations = [
        "Recommendations:",
        "",
        "1. Increase APAC investment (highest growth potential)",
        "2. Launch localized marketing for LATAM",
        "3. Maintain US enterprise focus",
        "4. Monitor EU regulatory changes",
        "",
        "Next review: September 15, 2026",
        "Prepared by: Finance Team",
    ]
    for line in recommendations:
        draw2.text((72, rec_y), line, fill="black")
        rec_y += 22

    pages.append(img2)

    # Save as PDF (images only — no text layer = scanned)
    pages[0].save(
        output_path,
        "PDF",
        save_all=True,
        append_images=pages[1:],
        resolution=150.0,
    )

    print(f"✓ Created scanned PDF with charts: {output_path}")
    print(f"  Page 1: Bar chart (revenue by region)")
    print(f"  Page 2: Pie chart (market share) + recommendations")
    print(f"  Note: All content is IMAGE — no selectable text (simulates scanner)")


if __name__ == "__main__":
    print("\n📄 Generating scanned PDF with chart images...\n")
    create_scanned_pdf_with_chart("scanned_report_with_chart.pdf")
    print("\n✅ Done! Open with: open scanned_report_with_chart.pdf")
