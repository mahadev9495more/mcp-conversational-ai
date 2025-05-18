# Conversational AI Assignment: MCP Server & Gradio Frontend

A modular Conversational AI assignment solution with a FastAPI backend (supporting Google Gemini, OpenAI, Anthropic, etc.) and a modern Gradio chat frontend with real-time streaming.

## Features

- Easy switching between LLM providers (Google Gemini, OpenAI, Anthropic, etc.)
- FastAPI backend with both standard and streaming endpoints
- Gradio frontend with streaming chat and chat history
- Works locally on Ubuntu (or any OS with Python 3.12.3+)

---

## Setup

```bash
### 1. Clone the Repository
git https://github.com/mahadev9495more/mcp-conversational-ai.git

cd mcp-conversational-ai

## 2. Create Python Virtual Environment
python3 -m venv myenv

source myenv/bin/activate

## 3. Install Dependencies
pip install -r requirements.txt

## 4. Set Your LLM API Keys
export GEMINI_API_KEY=your-gemini-api-key

export OPENAI_API_KEY=your-openai-api-key

export ANTHROPIC_API_KEY=your-anthropic-api-key

## 4. Start FastAPI Backend
python mcp_server.py

## 5. Start Gradio Frontend
python app.py
```

---

## LLM Switching Guide
#### How to Switch Models (LLMs)
- The backend and frontend are designed to let you switch between LLM providers (Gemini, OpenAI, Anthropic, etc.).
- In the Gradio UI, use the dropdown to select your model.

---

## Deployment Steps

- Production Backend
```bash
## For robustness, use a process manager like systemd
uvicorn mcp_server:app --host 0.0.0.0 --port 9999 --workers 2
```

- Production Frontend:
```Gradio runs on port 7860. For external access, use --share or run behind an NGINX reverse proxy.```

- systemd
```bash 
[Unit]
Description=MCP FastAPI Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/var/www/html/ConversationalAIAssignment
ExecStart=/var/www/html/ConversationalAIAssignment/myenv/bin/uvicorn mcp_server:app --host 0.0.0.0 --port 9999
Restart=always

[Install]
WantedBy=multi-user.target
```

- Enable and start
```bash
sudo systemctl daemon-reload
sudo systemctl enable mcp-backend
sudo systemctl start mcp-backend
```
