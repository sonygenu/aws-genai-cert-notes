# Project 2: PDF Image Extraction + Multimodal Summarization

Extract images from a PDF with bounding box coordinates, then send the image bytes to Bedrock Claude for AI-powered summarization.

## What This Demonstrates

- **PDF image extraction** — PyMuPDF extracts embedded images with position data
- **Bounding box detection** — know exactly where each image sits on the page
- **Multimodal AI** — Converse API accepts images + text in the same message
- **Vision model capabilities** — Claude analyzes charts, diagrams, screenshots

## How to Run

On the bastion:
```bash
cd ~/aws-genai-cert-notes/projects/02-pdf-image-extraction

# Step 1: Create a test PDF with an embedded chart
python3 create_pdf_with_image.py

# Step 2 & 3: Extract image + summarize with Bedrock
python3 extract_and_summarize.py report_with_chart.pdf
```

## Pipeline

```
PDF with images
    ↓ PyMuPDF
Extract images + bounding boxes (x0, y0, x1, y1)
    ↓ raw image bytes
Send to Bedrock Converse API (multimodal: image + text prompt)
    ↓ Claude vision
AI-generated summary of what the image shows
```

## Key Code Patterns

### Extracting images from PDF:
```python
doc = fitz.open("report.pdf")
for page in doc:
    for img_info in page.get_images(full=True):
        xref = img_info[0]
        image_data = doc.extract_image(xref)
        image_bytes = image_data["image"]      # Raw bytes
        bbox = page.get_image_rects(xref)[0]   # Position on page
```

### Sending image to Bedrock (Converse API multimodal):
```python
messages = [{
    "role": "user",
    "content": [
        {"image": {"format": "png", "source": {"bytes": image_bytes}}},
        {"text": "Describe this image"}
    ]
}]
response = client.converse(modelId=MODEL_ID, messages=messages)
```
