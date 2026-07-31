import proxy_patch  # noqa: F401
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv(override=True)

embeddings = OpenAIEmbeddings()
