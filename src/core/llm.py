from langchain_openai import ChatOpenAI

from config.settings import settings

# --- LLM setup ---
model = ChatOpenAI(
    model_name=settings.openai_model,
    temperature=0,
    api_key=settings.openai_api_key,
)

MODEL_NAME = model.model_name