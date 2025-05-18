import gradio as gr
import requests
import sseclient
import logging

MCP_URL = "http://127.0.0.1:9999/chat"
MCP_STREAM_URL = "http://127.0.0.1:9999/chat/stream"

def mcp_chat_api(message, history):
    payload = {
        "model": "gemini-2.0-flash-001",
        "messages": [
            {"role": "system", "content": "Conversational AI Assignment."},
            {"role": "user", "content": message}
        ]
    }
    try:
        response = requests.post(MCP_URL, json=payload)
        response.raise_for_status()
        return response.json()["content"]
    except Exception as e:
        return f"Error: {e}"

def mcp_stream_api(message, history):
    payload = {
        "model": "gemini-2.0-flash-001",
        "messages": [
            {"role": "system", "content": "Conversational AI Assignment."},
            {"role": "user", "content": message}
        ]
    }
    try:
        with requests.post(MCP_STREAM_URL, json=payload, stream=True) as resp:
            resp.raise_for_status()  # Raise an exception for bad status codes
            client = sseclient.SSEClient(resp)
            partial = ""
            
            # Add user message to history first
            new_history = history + [{"role": "user", "content": message}]
            
            # Initial yield to show user message immediately
            yield "", new_history
            
            # Process the streaming response
            for event in client.events():
                if event.data:
                    try:
                        # Clean up any potential whitespace or formatting issues
                        chunk = event.data.strip()
                        if chunk:
                            partial += chunk
                            # Update history with current partial response
                            history_with_stream = new_history + [
                                {"role": "system", "content": partial}
                            ]
                            yield "", history_with_stream
                    except Exception as e:
                        continue

            # Ensure final state is captured
            if partial:
                final_history = new_history + [
                    {"role": "system", "content": partial}
                ]
                yield "", final_history
                
    except requests.RequestException as e:
        error_msg = f"Network error: {str(e)}"
        error_history = history + [
            {"role": "user", "content": message},
            {"role": "system", "content": error_msg}
        ]
        yield "", error_history
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        error_history = history + [
            {"role": "user", "content": message},
            {"role": "system", "content": error_msg}
        ]
        yield "", error_history

with gr.Blocks(title="Conversational AI Assignment") as demo:
    gr.Markdown("## Conversational AI Assignment")
    model = gr.Dropdown(
        choices=["Google Gemini", "ChatGPT", "Anthropic Claude"],
        value="Google Gemini",
        label="Select Model",
        interactive=True,
        container=True,
        scale=2  # Controls the width relative to other elements
    )
    chatbot = gr.Chatbot(type="messages", label="Chat History")
    msg = gr.Textbox(label="Type your message here…", scale=10)
    submit_btn = gr.Button("Send (Standard)")
    stream_btn = gr.Button("Send (Streaming)")

    def on_submit(message, history):
        reply = mcp_chat_api(message, history)
        history = history + [
            {"role": "user", "content": message},
            {"role": "system", "content": reply}
        ]
        return "", history

    def on_stream(message, history):
        try:
            for response in mcp_stream_api(message, history):
                textbox_value, chat_history = response
                yield textbox_value, chat_history
        except Exception as e:
            error_history = history + [
                {"role": "user", "content": message},
                {"role": "system", "content": f"Error during streaming: {str(e)}"}
            ]
            yield "", error_history

    # Setup the interface with proper configurations
    msg.submit(on_submit, [msg, chatbot], [msg, chatbot])  # Re-enable Enter key submission
    submit_btn.click(
        on_submit,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot],
        queue=False
    )
    stream_btn.click(
        on_stream,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot],
        queue=True,
        api_name="stream"  # Enable API access
    )

# Launch with queue enabled and larger queue size for better streaming
demo.queue(max_size=100).launch()
