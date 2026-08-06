# src/graph/state.py
"""Shared state schema that flows through every node in the graph."""

from langgraph.graph import MessagesState

class AgentState(MessagesState):
    """
    Extends LangGraph's built-in MessagesState (which already provides
    a `messages` field with add_messages reducer) with any extra fields
    the graph needs to track.
    """

    