"""
Step 2 & 3: Extract image from PDF with bounding box, send to Bedrock for summarization.

Demonstrates:
- PyMuPDF image extraction with bounding box coordinates
- Bedrock Converse API with multimodal input (image + text)
- Vision model summarizing an image

Run:
    python3 extract_and_summarize.py report_with_chart.pdf
"""
import sys
import base64
import json
import boto3
import fitz  # pymupdf


REGION = "us-east-1"
MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"


def extract_images_from_pdf(pdf_path: str) -> list:
    """
    Step 2: Extract all images from a PDF with bounding box details.
    
    Returns a list of dicts, each with:
    - image_bytes: raw PNG bytes of the extracted image
    - bbox: bounding box (x0, y0, x1, y1) on the page
    - page_number: which page the image is on
    - width, height: image dimensions in pixels
    - xref: internal PDF reference ID
    """
    doc = fitz.open(pdf_path)
    extracted_images = []

    print(f"\n🔍 Extracting images from: {pdf_path}")
    print(f"   Total pages: {len(doc)}\n")

    for page_num, page in enumerate(doc, 1):
        # Get list of images on this page
        image_list = page.get_images(full=True)

        if not image_list:
            print(f"   Page {page_num}: No images found")
            continue

        print(f"   Page {page_num}: Found {len(image_list)} image(s)")

        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]  # Image reference ID

            # Extract image bytes
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]  # png, jpeg, etc.
            width = base_image["width"]
            height = base_image["height"]

            # Get bounding box (where the image appears on the page)
            # Find the image's position using get_image_rects
            rects = page.get_image_rects(xref)
            if rects:
                bbox = rects[0]  # First occurrence
                bbox_dict = {
                    "x0": round(bbox.x0, 2),
                    "y0": round(bbox.y0, 2),
                    "x1": round(bbox.x1, 2),
                    "y1": round(bbox.y1, 2),
                }
            else:
                bbox_dict = {"x0": 0, "y0": 0, "x1": width, "y1": height}

            extracted_images.append({
                "image_bytes": image_bytes,
                "image_format": image_ext,
                "bbox": bbox_dict,
                "page_number": page_num,
                "width": width,
                "height": height,
                "xref": xref,
                "img_index": img_index,
            })

            print(f"     Image {img_index + 1}: {width}x{height} ({image_ext})")
            print(f"       Bounding box: {bbox_dict}")
            print(f"       Size: {len(image_bytes)} bytes")

    doc.close()
    return extracted_images


def summarize_image_with_bedrock(image_bytes: bytes, image_format: str, 
                                  bbox: dict, page_number: int) -> str:
    """
    Step 3: Send image bytes to Bedrock Claude for summarization.
    
    Uses the Converse API with multimodal input (image + text prompt).
    """
    client = boto3.client("bedrock-runtime", region_name=REGION)

    # Encode image to base64
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    # Map format to media type
    media_type_map = {"png": "image/png", "jpeg": "image/jpeg", "jpg": "image/jpeg"}
    media_type = media_type_map.get(image_format, "image/png")

    # Build the multimodal message (text + image)
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "image": {
                        "format": image_format if image_format in ["png", "jpeg", "gif", "webp"] else "png",
                        "source": {
                            "bytes": image_bytes
                        }
                    }
                },
                {
                    "text": f"""Analyze this image extracted from a PDF document.

Image location: Page {page_number}, Bounding box: {json.dumps(bbox)}

Please provide:
1. A brief description of what the image shows
2. Key data points or information visible
3. Any trends or insights you can identify
4. How this image relates to a business/technical document"""
                }
            ]
        }
    ]

    print(f"\n🤖 Sending image to Bedrock ({MODEL_ID})...")

    response = client.converse(
        modelId=MODEL_ID,
        messages=messages,
        inferenceConfig={
            "temperature": 0.3,
            "maxTokens": 500,
        }
    )

    # Extract response
    assistant_text = response["output"]["message"]["content"][0]["text"]
    usage = response.get("usage", {})
    input_tokens = usage.get("inputTokens", 0)
    output_tokens = usage.get("outputTokens", 0)

    print(f"   Tokens: {input_tokens} in / {output_tokens} out")

    return assistant_text


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 extract_and_summarize.py <pdf_path>")
        print("  First run: python3 create_pdf_with_image.py")
        sys.exit(1)

    pdf_path = sys.argv[1]

    # Step 2: Extract images with bounding boxes
    images = extract_images_from_pdf(pdf_path)

    if not images:
        print("\n❌ No images found in the PDF")
        sys.exit(1)

    # Step 3: Summarize each image with Bedrock
    print(f"\n{'='*60}")
    print(f"📊 IMAGE SUMMARIES")
    print(f"{'='*60}")

    for img in images:
        print(f"\n--- Image (Page {img['page_number']}, {img['width']}x{img['height']}) ---")
        print(f"    Bounding box: {img['bbox']}")
        print(f"    Format: {img['image_format']}, Size: {len(img['image_bytes'])} bytes")

        # Send to Bedrock for summarization
        summary = summarize_image_with_bedrock(
            image_bytes=img["image_bytes"],
            image_format=img["image_format"],
            bbox=img["bbox"],
            page_number=img["page_number"],
        )

        print(f"\n    📝 AI Summary:")
        for line in summary.split("\n"):
            print(f"       {line}")

    print(f"\n{'='*60}")
    print(f"✅ Done! Processed {len(images)} image(s)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
