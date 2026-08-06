from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langgraph.graph import MessagesState
from config.logger import logger
from src.core.llm import model
from src.core.prompts import SYSTEM_PROMPT
from src.graph.checkpointer import checkpointer
from src.tools.faq_tools import tools

class AgentState(MessagesState):
    """
    Extends LangGraph's built-in MessagesState (which already provides
    a `messages` field with add_messages reducer function. 
    """


def build_graph():
    logger.info("Building agent via create_agent()...")

    compiled_graph = create_agent(
        model=model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        state_schema=AgentState,
        checkpointer=checkpointer,
    )

    logger.info("Agent built successfully")
    return compiled_graph


graph = build_graph()

def ask_agent(question: str, session_id: str = "default") -> str:
    config = {
        "configurable": {"thread_id": session_id},
        "recursion_limit": 10,
    }

    logger.info(f"ask_agent called | session_id={session_id} | question='{question}'")

    result = graph.invoke(
        {"messages": [HumanMessage(content=question)]},
        config=config,
    )

    answer = result["messages"][-1].content
    logger.info(f"ask_agent returning answer | session_id={session_id} | answer='{str(answer)[:200]}'")
    return answer


if __name__ == "__main__":
    logger.info("=== Testing Graph ===")

    answer = ask_agent("What is mobile money?", session_id="test-001")
    logger.info(f"Answer: {answer}")

    answer = ask_agent("How do I register for it?", session_id="test-001")
    logger.info(f"Answer: {answer}")