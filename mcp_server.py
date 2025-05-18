import os
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import uvicorn

from google import genai
from google.genai import types


# Load Gemini API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set")

# Initialize Gen AI client for Gemini Developer API
client = genai.Client(api_key=GEMINI_API_KEY)


# FastAPI app instance
app = FastAPI(title="MCP Server - FastAPI + Gemini 2.0 Flash")

# Pydantic models for request/response
class ChatMessage(BaseModel):
    role: str = "user"  # Default to user role
    content: str

class ChatRequest(BaseModel):
    model: str = "gemini-2.0-flash-001" # Default model
    messages: List[ChatMessage] = [
        ChatMessage(role="system", content="Conversational AI Assignment."),
        ChatMessage(role="user", content="")
    ]

    def __init__(self, **data):
        super().__init__(**data)
        # Ensure first message is system message
        self.messages[0] = ChatMessage(role="system", content="Conversational AI Assignment.")
        # Set user content from request
        if len(self.messages) > 1:
            user_content = self.messages[1].content
            self.messages[1] = ChatMessage(role="user", content=user_content)

class ChatResponse(BaseModel):
    content: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Non-streaming chat: starts a session and sends messages sequentially.
    """
    try:
        # Create a chat session for the requested model
        chat_session = client.chats.create(model=request.model)
        response = None
        # Send each message in order
        for msg in request.messages:
            response = chat_session.send_message(msg.content)
        return ChatResponse(content=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint using Server-Sent Events (SSE).
    """
    try:
        chat_session = client.chats.create(model=request.model)
        def event_generator():
            # Send each user message and stream chunks
            for msg in request.messages:
                for chunk in chat_session.send_message_stream(msg.content):
                    # Yield each text chunk as SSE
                    yield f"data: {chunk.text}\n\n"
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    # Run with: python mcp_server.py
    uvicorn.run("mcp_server:app", host="127.0.0.1", port=9999, reload=True)
