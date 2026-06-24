# Project 1: Bedrock Converse API Chatbot

An interactive CLI chatbot using the Bedrock Converse API.

## What This Demonstrates

- **Converse API** — model-agnostic chat (same code works with any model)
- **Multi-turn conversation** — full message history maintained
- **System prompts** — sets the AI's persona and behavior
- **Token tracking** — shows cost per message
- **Model swapping** — change model with one flag

## How to Run

On the bastion:
```bash
cd ~/aws-genai-cert-notes/projects/01-converse-api-chatbot
python3 chatbot.py
```

To use a different model:
```bash
python3 chatbot.py --model us.anthropic.claude-sonnet-4-20250514-v1:0
```

## Key Learning Points

1. **Converse API format is model-agnostic:**
```python
response = client.converse(
    modelId="any-model-id",
    messages=[{"role": "user", "content": [{"text": "Hello"}]}],
    system=[{"text": "You are a helpful assistant"}],
)
```

2. **Multi-turn = pass full message history every call:**
```python
messages = [
    {"role": "user", "content": [{"text": "What is RAG?"}]},
    {"role": "assistant", "content": [{"text": "RAG is..."}]},
    {"role": "user", "content": [{"text": "How does it use embeddings?"}]},
]
```

3. **Switch models by changing ONE string:**
```python
model_id = "us.anthropic.claude-haiku-4-5-20251001-v1:0"  # Fast, cheap
model_id = "us.anthropic.claude-sonnet-4-20250514-v1:0"   # Smarter, pricier
```
