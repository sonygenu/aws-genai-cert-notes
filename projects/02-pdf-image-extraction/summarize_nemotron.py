"""
Send extracted PDF image to Nemotron Nano 12B VL for summarization.

Run:
    python3 create_pdf_with_image.py   # (if not already done)
    python3 summarize_nemotron.py report_with_chart.pdf
"""
import sys
import time
import boto3
import fitz  # pymupdf


REGION = "us-east-1"
MODEL_ID = "nvidia.nemotron-nano-12b-v2"

PROMPT = """Analyze this image extracted from a PDF document.
Please provide:
1. A brief description of what the image shows
2. Key data points or information visible
3. Any trends or insights you can identify"""


def extract_first_image(pdf_path: str) -> dict:
    """Extract the first image from a PDF."""
    doc = fitz.open(pdf_path)
    for page_num, page in enumerate(doc, 1):
        image_list = page.get_images(full=True)
        if image_list:
            xref = image_list[0][0]
            base_image = doc.extract_image(xref)
            rects = page.get_image_rects(xref)
            bbox = {"x0": round(rects[0].x0, 2), "y0": round(rects[0].y0, 2),
                    "x1": round(rects[0].x1, 2), "y1": round(rects[0].y1, 2)} if rects else {}
            doc.close()
            return {
                "image_bytes": base_image["image"],
                "format": base_image["ext"],
                "width": base_image["width"],
                "height": base_image["height"],
                "bbox": bbox,
                "page": page_num,
            }
    doc.close()
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 summarize_nemotron.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    # Extract image
    print(f"\n🔍 Extracting image from: {pdf_path}")
    img = extract_first_image(pdf_path)
    if not img:
        print("❌ No images found")
        sys.exit(1)

    print(f"   Image: {img['width']}x{img['height']} ({img['format']})")
    print(f"   Bounding box: {img['bbox']}")
    print(f"   Size: {len(img['image_bytes'])} bytes")

    # Send to Nemotron
    print(f"\n🤖 Sending to Nemotron ({MODEL_ID})...")
    client = boto3.client("bedrock-runtime", region_name=REGION)

    fmt = img["format"] if img["format"] in ["png", "jpeg", "gif", "webp"] else "png"

    messages = [
        {
            "role": "user",
            "content": [
                {"image": {"format": fmt, "source": {"bytes": img["image_bytes"]}}},
                {"text": PROMPT}
            ]
        }
    ]

    start = time.time()
    try:
        response = client.converse(
            modelId=MODEL_ID,
            messages=messages,
            inferenceConfig={"temperature": 0.3, "maxTokens": 500},
        )
        elapsed = time.time() - start

        output = response["output"]["message"]["content"][0]["text"]
        usage = response.get("usage", {})

        print(f"   ✅ Latency: {round(elapsed * 1000)}ms")
        print(f"   Tokens: {usage.get('inputTokens', 0)} in / {usage.get('outputTokens', 0)} out")
        print(f"\n{'='*60}")
        print(f"📝 NEMOTRON SUMMARY:")
        print(f"{'='*60}")
        print(output)
        print(f"{'='*60}")

    except Exception as e:
        elapsed = time.time() - start
        print(f"   ❌ Error ({round(elapsed * 1000)}ms): {e}")
        print(f"\n   Try listing available Nemotron models:")
        print(f"   python3 -c \"import boto3; c=boto3.client('bedrock',region_name='us-east-1'); [print(m['modelId']) for m in c.list_foundation_models()['modelSummaries'] if 'nemotron' in m['modelId'].lower()]\"")


if __name__ == "__main__":
    main()
