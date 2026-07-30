# src/nodes/agent_nodes.py
"""All node functions used to build the graph, plus the LLM setup they rely on."""

from typing import Literal

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph import END
from langgraph.prebuilt import ToolNode

from config.logger import logger
from config.settings import settings
from src.graph.state import AgentState
from src.tools.faq_tools import tools

# --- LLM setup ---
model = ChatOpenAI(
    model_name=settings.openai_model,
    temperature=0,
    api_key=settings.openai_api_key,
)

MODEL_NAME = model.model_name

model_with_tools = model.bind_tools(tools)

SYSTEM_PROMPT = """You are a helpful customer service assistant
for Laxmi Sunrise Bank Nepal.

You have access to a FAQ database containing information about:
- General banking (accounts, deposits, interest, ATM)
- Mobile Money app (registration, transfers, limits)
- Wonder Woman Savings account (eligibility, benefits)

Instructions:
1. ALWAYS use search_bank_faq tool before answering any bank question
2. Base your answers ONLY on the retrieved FAQ data
3. Give warm, professional, helpful responses
4. If nothing relevant is found, say sorry honestly
5. Do not make up bank policies or interest rates"""


# --- Nodes ---
def agent_node(state: AgentState) -> dict:
    """Main reasoning node: decides whether to call a tool or answer directly."""
    messages = state["messages"]
    system = SystemMessage(content=SYSTEM_PROMPT)

    logger.info(f"agent_node invoked | history_length={len(messages)}")

    response = model_with_tools.invoke([system] + messages)

    if getattr(response, "tool_calls", None):
        logger.info(f"agent_node requested tool call(s): {response.tool_calls}")
    else:
        logger.info(f"agent_node produced final answer: {str(response.content)[:200]}")

    return {"messages": [response]}


tool_node = ToolNode(tools)


def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    """Router: go to 'tools' if the last message requested a tool call, else end."""
    messages = state["messages"]
    last_message = messages[-1]

    if last_message.tool_calls:
        logger.info("should_continue -> routing to 'tools'")
        return "tools"

    logger.info("should_continue -> routing to END")
    return END