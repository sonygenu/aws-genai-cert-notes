"""
Bedrock Converse API — Interactive Chatbot

Demonstrates:
- Converse API (model-agnostic chat)
- Multi-turn conversation (message history)
- System prompts
- Temperature control
- Token usage tracking

Run:
    python3 chatbot.py
    python3 chatbot.py --model us.anthropic.claude-sonnet-4-20250514-v1:0
"""
import boto3
import json
import sys

# --- Configuration ---
DEFAULT_MODEL = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
REGION = "us-east-1"

SYSTEM_PROMPT = """You are a helpful AI study assistant for the AWS Generative AI certification exam. 
You explain concepts clearly with examples. When asked about AWS services, 
relate them back to how they're used in generative AI applications."""


def create_client():
    """Create Bedrock Runtime client."""
    return boto3.client("bedrock-runtime", region_name=REGION)


def converse(client, model_id, messages, system_prompt=None, temperature=0.7, max_tokens=1000):
    """
    Call Bedrock Converse API.
    
    This is the key function — same format works for ANY model on Bedrock.
    """
    # Build the request
    kwargs = {
        "modelId": model_id,
        "messages": messages,
        "inferenceConfig": {
            "temperature": temperature,
            "maxTokens": max_tokens,
        },
    }

    # Add system prompt if provided
    if system_prompt:
        kwargs["system"] = [{"text": system_prompt}]

    # Call the API
    response = client.converse(**kwargs)

    # Extract the response
    output_message = response["output"]["message"]
    assistant_text = output_message["content"][0]["text"]

    # Token usage
    usage = response.get("usage", {})
    input_tokens = usage.get("inputTokens", 0)
    output_tokens = usage.get("outputTokens", 0)

    return assistant_text, input_tokens, output_tokens


def main():
    # Parse model from args
    model_id = DEFAULT_MODEL
    if "--model" in sys.argv:
        idx = sys.argv.index("--model") + 1
        if idx < len(sys.argv):
            model_id = sys.argv[idx]

    print(f"\n{'='*60}")
    print(f"🤖 Bedrock Converse API Chatbot")
    print(f"   Model: {model_id}")
    print(f"   System: AWS GenAI Cert Study Assistant")
    print(f"   Type 'quit' to exit, 'clear' to reset history")
    print(f"{'='*60}\n")

    client = create_client()
    messages = []  # Conversation history
    total_input_tokens = 0
    total_output_tokens = 0

    while True:
        # Get user input
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            break
        if user_input.lower() == "clear":
            messages = []
            print("  [History cleared]\n")
            continue

        # Add user message to history
        messages.append({
            "role": "user",
            "content": [{"text": user_input}]
        })

        # Call Converse API
        try:
            response_text, input_tokens, output_tokens = converse(
                client=client,
                model_id=model_id,
                messages=messages,
                system_prompt=SYSTEM_PROMPT,
                temperature=0.7,
                max_tokens=1000,
            )

            # Add assistant response to history (for multi-turn)
            messages.append({
                "role": "assistant",
                "content": [{"text": response_text}]
            })

            # Track tokens
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens

            # Print response
            print(f"\nAssistant: {response_text}")
            print(f"  [{input_tokens} in / {output_tokens} out tokens]\n")

        except Exception as e:
            print(f"\n  ❌ Error: {e}\n")
            # Remove the failed user message from history
            messages.pop()

    # Summary
    print(f"\n{'='*60}")
    print(f"Session summary:")
    print(f"  Total input tokens:  {total_input_tokens}")
    print(f"  Total output tokens: {total_output_tokens}")
    print(f"  Messages exchanged:  {len(messages)}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
