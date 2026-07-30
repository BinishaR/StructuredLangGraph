# src/tools/faq_tools.py
"""All @tool-decorated functions the agent can call."""

from langchain.tools import tool
from src.rag.retriever import retriever_manager
from config.logger import logger
# from src.rag.retriever import retriever


@tool
def search_bank_faq(query: str) -> str:
    """
    Search Laxmi Sunrise Bank FAQ database using semantic search.
    Use this to answer any customer question about:
    - Bank accounts, deposits, interest rates (general)
    - Mobile Money app registration and features (mobile)
    - Wonder Woman Savings account (wonder)
    query: the customer's question or topic to search for
    """
    logger.info(f"search_bank_faq called | query='{query}'")

    # docs = retriever.invoke(query)
    docs = retriever_manager.get().invoke(query)

    if not docs:
        logger.warning(f"No FAQ results found for query: '{query}'")
        return "No relevant FAQ found for this query."

    results = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        results.append(f"[Source: {source}]\n{doc.page_content}")

    logger.info(f"search_bank_faq returned {len(docs)} result(s) for query: '{query}'")
    return "\n".join(results)


@tool
def get_faq_topics() -> str:
    """
    Get an overview of available FAQ topics in the bank database.
    Use this when customer asks what topics are available
    or what the assistant can help with.
    """
    logger.info("get_faq_topics called")
    return """Available FAQ Topics at Laxmi Sunrise Bank:

1. General Banking (general):
   - Account types and opening
   - Deposits and interest rates
   - ATM cards and cheque books
   - Transaction limits
   - Required documents

2. Mobile Money App (mobile):
   - App registration and activation
   - Password reset and recovery
   - Transaction limits and features
   - Cardless ATM withdrawal
   - International banking

3. Wonder Woman Savings (wonder):
   - Eligibility requirements
   - Account benefits and features
   - Interest rates
   - Special offers for women

Ask me anything about these topics!"""


tools = [search_bank_faq, get_faq_topics]