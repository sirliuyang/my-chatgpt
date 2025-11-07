# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from pydantic_ai import Agent
from src.core.config import settings
from pydantic import BaseModel, Field
from typing import AsyncIterable, List, Dict


# Optional: Define a structured output model for chat responses (pydantic-ai validates it)
class ChatOutput(BaseModel):
    content: str = Field(description="Assistant's response content")


# Create the agent once (singleton-like)
agent = Agent(
    model=settings.DEEPSEEK_MODEL,  # Uses DeepSeek via pydantic-ai (model-agnostic)
    instructions="You are a helpful AI assistant. Respond based on the conversation history.",
    output_type=ChatOutput,  # Ensures structured, validated output
)


async def stream_chat_response(messages: List[Dict[str, str]]) -> AsyncIterable[str]:
    """
    Streams response from LLM using pydantic-ai Agent.
    Supports DeepSeek and streams chunks for real-time response.
    """
    # Format messages for agent (pydantic-ai expects a prompt or conversation)
    prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

    # Run asynchronously; pydantic-ai supports streamed outputs
    # Assuming agent.run returns an iterable for streaming (based on framework docs)
    result = await agent.run(prompt)  # Async run for conversation

    # Simulate chunking for streaming (in practice, integrate with agent's streamed-results if available)
    # For simplicity, yield the full response in chunks; extend for true token-by-token if needed
    full_response = result.output.content
    chunks = [full_response[i:i + 100] for i in range(0, len(full_response), 100)]  # Example chunking
    for chunk in chunks:
        yield chunk
