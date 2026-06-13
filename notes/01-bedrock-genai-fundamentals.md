# Section 1: Bedrock + Gen AI Fundamentals

## Foundation Models

- Foundation models are giant pre-trained transformer models
- Examples:
  1. **GPT-n (OpenAI)** — Generative Pre-trained Transformer. Series of autoregressive language models (GPT-3, GPT-4). Trained on massive internet text data. Used for text generation, reasoning, code, and multi-modal tasks.
  2. **Claude (Anthropic)** — Constitutional AI approach. Focused on being helpful, harmless, and honest. Available on AWS Bedrock. Strong at long-context tasks (200K token window), analysis, and coding.
  3. **DALL-E (OpenAI)** — For images. Text-to-image generation model. Creates and edits images from natural language descriptions.
  4. **LLaMA (Meta)** — Large Language Model Meta AI. Open-source foundation model. Available in various sizes (7B, 13B, 70B parameters). Can be fine-tuned and self-hosted. Available on Bedrock via Meta's partnership.
  5. **DeepSeek (DeepSeek AI)** — Chinese open-source LLM. Known for strong reasoning and coding capabilities at lower training cost. Uses Mixture of Experts (MoE) architecture. Competitive with GPT-4 on benchmarks at fraction of the cost.
  6. **Nova (Amazon)** — Amazon's own foundation model family on Bedrock. Includes Nova Micro (text), Nova Lite (multimodal), Nova Pro (complex tasks). Optimized for speed, cost, and AWS integration. Built for enterprise use cases.
  7. **Jurassic-1 (AI21 Labs)** — Multilingual LLMs for text generation. Available on Bedrock. Strong at summarization, paraphrasing, and multilingual content.
  8. **Stable Diffusion (Stability AI)** — Image, art, logo, and design generation. Open-source text-to-image model. Available on Bedrock. Used for creative content, marketing assets, and visual design.
  9. **Amazon Titan** — Text summarization, text generation, Q&A, and embeddings (personalization, search). Amazon's first-party model family on Bedrock.
  10. **Amazon Nova Reels** — Video generation. Creates short video clips from text prompts.

## Amazon Bedrock

- **What it is:** A single API that acts as the layer between you and foundation models. You can swap models without changing your application code.
- **Completely serverless** — no infrastructure to manage, maintain, patch, or scale. You just call the API.

### What Bedrock Provides (Beyond Inference)

| Capability | What it does |
|-----------|-------------|
| **Model inference** | Call any supported FM via a single API (InvokeModel) |
| **Fine-tuning** | Customize models with your own data (without managing training infra) |
| **Knowledge Bases** | Built-in RAG — connect your data sources for grounded answers |
| **Agents** | Build autonomous agents with tool use and multi-step reasoning |
| **Guardrails** | Content filtering, PII redaction, topic blocking |
| **Model evaluation** | Compare model outputs, benchmark quality |
| **Provisioned throughput** | Reserve capacity for predictable performance |
| **Batch inference** | Process large datasets asynchronously at lower cost |

### Two APIs: Bedrock vs Bedrock Runtime

| API | Purpose | Example actions |
|-----|---------|----------------|
| **Bedrock API** | Manage, deploy, and train | List models, create fine-tuning jobs, manage knowledge bases, configure guardrails |
| **Bedrock Runtime API** | Run inference (call models) | InvokeModel, InvokeModelWithResponseStream, Converse |

Think of it as: **Bedrock API = control plane** (setup/config), **Bedrock Runtime = data plane** (actual model calls).

### Cost Structure

| Pricing model | How it works | Best for |
|--------------|-------------|----------|
| **On-demand** | Pay per token (input + output) | Variable workloads, experimentation |
| **Provisioned throughput** | Reserve model units (hourly) | Predictable high-volume workloads |
| **Batch inference** | Lower per-token cost, async processing | Large offline jobs (not real-time) |

- You pay **only for what you use** — no idle cost with on-demand
- Each foundation model has its own per-token price (Claude is more expensive than Titan)
- Fine-tuning has separate costs (training time + storage)

### Integration with SageMaker

| Integration | What it enables |
|------------|----------------|
| **SageMaker → Bedrock** | Use Bedrock models inside SageMaker pipelines and notebooks |
| **Bedrock → SageMaker** | Deploy custom models trained in SageMaker, serve via Bedrock |
| **Model Registry** | Track model versions across both services |
| **SageMaker Canvas** | No-code interface that can call Bedrock models |
| **MLOps** | SageMaker Pipelines can orchestrate Bedrock fine-tuning jobs |

**Key difference:** Bedrock = fully managed, no infra. SageMaker = full control, you manage compute. Use Bedrock when a supported FM works. Use SageMaker when you need custom training or unsupported models.

### 4 Main Entry Points for Bedrock Runtime

| API | What it does | Response | Use case |
|-----|-------------|----------|----------|
| **Converse** | Unified chat API — works the same across all models. Handles message history, tool use, and system prompts in a model-agnostic format. | Full response at once | Chat applications, agents, tool calling. Recommended default — no model-specific formatting needed |
| **ConverseStream** | Same as Converse, but returns tokens as they're generated (streaming). | Token-by-token stream | Real-time chat UIs where you want to show responses as they type |
| **InvokeModel** | Low-level model call — you format the request body per model's specific schema (each model has a different format). | Full response at once | Direct model access, embedding calls, image generation, non-chat models |
| **InvokeModelWithResponseStream** | Same as InvokeModel, but streams the response. | Token-by-token stream | Streaming for model-specific payloads (e.g., streaming image generation progress) |

**Key insight:** 
- Use **Converse/ConverseStream** for text/chat (model-agnostic, easier to swap models)
- Use **InvokeModel/InvokeModelWithResponseStream** for embeddings, images, or when you need model-specific parameters

### Bedrock Agents

- **What it is:** Autonomous AI agents that can reason, plan, and take actions across multiple steps. They can call APIs, query databases, and use tools to complete complex tasks.
- Can orchestrate **multiple models running in parallel** — e.g., one model for reasoning, another for code generation, another for summarization.

**What agents can do:**
- Break down a complex user request into sub-tasks
- Decide which tools/APIs to call and in what order
- Maintain conversation memory across turns
- Access Knowledge Bases for grounded retrieval
- Execute Lambda functions as tools
- Handle multi-step workflows autonomously

**Architecture:**
```
User query → Agent (LLM reasons) → Decides action
    → Call tool A (Lambda/API)
    → Observe result
    → Call tool B (Knowledge Base)
    → Observe result
    → Generate final answer
```

**Key features:**
- Fully managed — no orchestration code to write
- Built-in ReAct (Reason + Act) loop
- Session memory (short-term and long-term)
- Guardrails integration for safety
- Trace/debug mode to see agent's reasoning steps

### Bedrock Agent Runtime

The runtime API for executing agents and knowledge base queries.

| API | What it does | When to use |
|-----|-------------|-------------|
| **InvokeAgent** | Sends a user message to a Bedrock Agent. The agent reasons, calls tools, and returns a response. Handles the full multi-step loop. | When you want the agent to autonomously figure out what to do (tool calling, reasoning, multi-step) |
| **Retrieve** | Queries a Knowledge Base and returns raw matching chunks — no LLM involved. Just vector search results. | When you want to do your own processing on the retrieved documents (custom ranking, filtering, or using your own LLM) |
| **RetrieveAndGenerate** | Queries a Knowledge Base AND feeds results to an LLM to generate a grounded answer — full RAG in one call. | When you want a one-call RAG solution: question in → answer out (with citations) |

**Key difference:**
```
Retrieve:             Question → Vector search → Return chunks (you handle the rest)
RetrieveAndGenerate:  Question → Vector search → LLM generates answer → Return answer + citations
InvokeAgent:          Question → Agent reasons → May call tools + KB → Multi-step → Return answer
```

**Simplicity spectrum:**
- `Retrieve` = most control, least magic
- `RetrieveAndGenerate` = one-call RAG, no agent
- `InvokeAgent` = most autonomous, agent decides everything

### Bedrock Permissions

- **Must use IAM user/role — NOT root account**
  - Why? Root has unrestricted access — violates least privilege principle. Cannot be scoped, audited, or revoked granularly. AWS best practice: never use root for daily operations.

| Managed Policy | What it grants |
|---------------|----------------|
| **AmazonBedrockFullAccess** | Full access to all Bedrock actions (invoke, fine-tune, manage KBs, agents, guardrails) |
| **AmazonBedrockReadOnly** | Read-only — list models, view configurations, but cannot invoke or modify |

**Custom policies for fine-grained control:**
```json
{
    "Action": "bedrock:InvokeModel",
    "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude*"
}
```
This restricts a user to only invoke Claude models — not Titan, not Stable Diffusion.

### Amazon Bedrock: Model Access

- **Models are NOT available by default** — you must explicitly request access in the Bedrock console
- Go to Bedrock → Model access → Request access for each model/provider
- Some models require accepting an End User License Agreement (EULA)
- Access is per-region — enabling Claude in us-east-1 doesn't enable it in eu-west-1
- Once approved, models appear in your API calls
- Access can be revoked or restricted via IAM policies

### Bedrock Pricing

**Three pricing models:**

| Model | How you pay | Best for |
|-------|------------|----------|
| **On-demand** | Per token (input tokens + output tokens charged separately) | Unpredictable workloads, experimentation, low volume |
| **Provisioned Throughput** | Reserve Model Units (hourly or with commitment) | High-volume, predictable workloads needing guaranteed performance |
| **Batch Inference** | Per token (discounted, ~50% cheaper than on-demand) | Large offline jobs — not real-time, results returned asynchronously |

**On-demand pricing breakdown:**
- **Input tokens** — what you send to the model (prompt, context)
- **Output tokens** — what the model generates (response)
- Output tokens are typically 3-5x more expensive than input tokens
- No minimum fees, no upfront commitment

**Additional costs:**
| Feature | Pricing |
|---------|---------|
| Fine-tuning | Training hours + model storage (per GB/month) |
| Knowledge Bases | Storage + embedding generation + retrieval calls |
| Guardrails | Per 1K text units assessed |
| Model evaluation | Per model call during evaluation |

**Key exam point:** You are charged for BOTH input AND output tokens separately. A long prompt with a short answer costs more on input. A short prompt with a long response costs more on output.
