# src/graph/builder.py
"""Graph construction, compilation, and the public ask_agent() entry point."""

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END

from config.logger import logger
from src.graph.state import AgentState
from src.nodes.agent_nodes import agent_node, tool_node, should_continue


def build_graph():
    """Wire up nodes and edges, then compile the graph with an in-memory checkpointer."""
    logger.info("Building LangGraph agent graph...")

    builder = StateGraph(AgentState)

    builder.add_node("agent", agent_node)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "agent")

    builder.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END,
        },
    )

    builder.add_edge("tools", "agent")

    memory = InMemorySaver()
    compiled_graph = builder.compile(checkpointer=memory)

    logger.info("Graph compiled successfully")
    return compiled_graph

graph = build_graph()

def ask_agent(question: str, session_id: str = "default") -> str:
    """Run a single question through the graph and return the final answer text."""
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