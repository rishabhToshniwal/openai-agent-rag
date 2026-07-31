import gradio as gr
from agent import chat_response  
from dotenv import load_dotenv
import os

load_dotenv(override=True)
GRADIO_SERVER_PORT = os.getenv("GRADIO_SERVER_PORT", 7860)

def main():
    gr.ChatInterface(
        chat_response,
        title="Ask Queries to RAG Agent",
        description=(
            "Ask queries to the RAG Agent to get the answer from the documents."
        ),
    ).launch(
        server_port=GRADIO_SERVER_PORT,
        inbrowser=True,
    )


if __name__ == "__main__":
    main()