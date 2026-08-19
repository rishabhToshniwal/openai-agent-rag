# import proxy_patch  # uncomment if behind corp proxy (disables SSL verify)
from dotenv import load_dotenv
from agents import Agent,Runner,function_tool,trace,ModelSettings
import os
from openai_embeddings import OpenAIEmbeddings
from chroma import get_chroma_instance
from pydantic import BaseModel, Field
from helpers import Helpers

load_dotenv(override=True)
model_settings = ModelSettings(tool_choice="auto")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# embeddings = OpenAIEmbeddings()
chroma_db = get_chroma_instance()
similarity_search_result_count=3

system_prompt = """
You are a helpful chat assistant that can answer questions using ingested documents via the doc_search tool.
You have access to the following tools:
- doc_search: Use it for questions about facts, content, or details that may be in the documents.
You should use the doc_search tool to search the document for the answer to the query.
Do not make up information, only use the information from the document.
If you don't know the answer, say "I don't know".
Keep answers clear and concise.
"""

class DocSearchResult(BaseModel):
    document_name: str = Field(description="The name of the document")
    score: float = Field(description="The score of the document")
    content: str = Field(description="The content of the document")


@function_tool
def doc_search(query: str) -> list[DocSearchResult]:
    """Search the document for the answer to the query
       Returns list of documents with their name, score and content
       Return empty list if no relevant documents are found
    """
    # Since chroma instance already had embeddings, we can use similarity_search_with_score directly
    # query_embedding = embeddings.embed_query(query)
    # results = chroma_db.similarity_search_by_vector_with_relevance_scores(query_embedding, k=similarity_search_result_count)
    search_results = chroma_db.similarity_search_with_score(query, k=similarity_search_result_count)
    results = []
    if not search_results:
        return results
    for i, (doc, score) in enumerate(search_results, start=1):
        doc_search_result = DocSearchResult(document_name=doc.metadata["source"], score=score, content=doc.page_content)
        results.append(doc_search_result)
    return results

rag_agent = Agent(name="rag_agent",instructions=system_prompt,tools=[doc_search],model_settings=model_settings)

async def chat_response(message,history):
    messages = []
    for msg in history:
        messages.append({
            "role": msg["role"],
            "content": Helpers.to_text(msg["content"]),
        })
    messages.append({"role": "user", "content": Helpers.to_text(message)})

    with trace("Rag Agent Chat"):
        response = await Runner.run(rag_agent, messages)
    return response.final_output


    
