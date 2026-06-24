"""
Compare image summarization between Claude Haiku and Nemotron VL.

Extracts an image from a PDF and sends it to BOTH models,
then displays results side-by-side for comparison.

Run:
    python3 create_pdf_with_image.py   # (if not already done)
    python3 compare_models.py report_with_chart.pdf
"""
import sys
import json
import time
import boto3
import fitz  # pymupdf


REGION = "us-east-1"

# Models to compare
MODELS = {
    "Claude Haiku 4.5": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    "Nemotron Nano 12B VL": "nvidia.nemotron-nano-12b-v2",
}

PROMPT = """Analyze this image extracted from a PDF document.
Please provide:
1. A brief description of what the image shows
2. Key data points or information visible
3. Any trends or insights you can identify"""


def extract_first_image(pdf_path: str) -> dict:
    """Extract the first image from a PDF with bounding box."""
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


def summarize_with_model(client, model_id: str, image_bytes: bytes, image_format: str) -> dict:
    """Send image to a model and get summary + timing."""
    # Normalize format
    fmt = image_format if image_format in ["png", "jpeg", "gif", "webp"] else "png"

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "image": {
                        "format": fmt,
                        "source": {"bytes": image_bytes}
                    }
                },
                {"text": PROMPT}
            ]
        }
    ]

    start_time = time.time()

    try:
        response = client.converse(
            modelId=model_id,
            messages=messages,
            inferenceConfig={"temperature": 0.3, "maxTokens": 500},
        )

        elapsed = time.time() - start_time
        output = response["output"]["message"]["content"][0]["text"]
        usage = response.get("usage", {})

        return {
            "success": True,
            "summary": output,
            "latency_ms": round(elapsed * 1000),
            "input_tokens": usage.get("inputTokens", 0),
            "output_tokens": usage.get("outputTokens", 0),
        }

    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "latency_ms": round(elapsed * 1000),
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 compare_models.py <pdf_path>")
        print("  First run: python3 create_pdf_with_image.py")
        sys.exit(1)

    pdf_path = sys.argv[1]

    # Extract image
    print(f"\n🔍 Extracting image from: {pdf_path}")
    img = extract_first_image(pdf_path)
    if not img:
        print("❌ No images found in PDF")
        sys.exit(1)

    print(f"   Image: {img['width']}x{img['height']} ({img['format']})")
    print(f"   Bounding box: {img['bbox']}")
    print(f"   Size: {len(img['image_bytes'])} bytes")

    # Compare models
    client = boto3.client("bedrock-runtime", region_name=REGION)
    results = {}

    print(f"\n{'='*70}")
    print(f"🤖 COMPARING MODELS ON SAME IMAGE")
    print(f"{'='*70}")

    for model_name, model_id in MODELS.items():
        print(f"\n--- {model_name} ({model_id}) ---")
        print(f"    Sending image...")

        result = summarize_with_model(client, model_id, img["image_bytes"], img["format"])
        results[model_name] = result

        if result["success"]:
            print(f"    ✅ Latency: {result['latency_ms']}ms")
            print(f"    Tokens: {result['input_tokens']} in / {result['output_tokens']} out")
            print(f"\n    Summary:")
            for line in result["summary"].split("\n"):
                print(f"      {line}")
        else:
            print(f"    ❌ Error: {result['error']}")

    # Side-by-side comparison
    print(f"\n\n{'='*70}")
    print(f"📊 COMPARISON SUMMARY")
    print(f"{'='*70}")
    print(f"\n{'Model':<25} {'Latency':<12} {'In Tokens':<12} {'Out Tokens':<12} {'Status'}")
    print(f"{'-'*25} {'-'*12} {'-'*12} {'-'*12} {'-'*8}")

    for model_name, result in results.items():
        if result["success"]:
            print(f"{model_name:<25} {result['latency_ms']:<12}ms "
                  f"{result['input_tokens']:<12} {result['output_tokens']:<12} ✅")
        else:
            print(f"{model_name:<25} {result['latency_ms']:<12}ms "
                  f"{'—':<12} {'—':<12} ❌")

    print(f"\n{'='*70}")


if __name__ == "__main__":
    main()
