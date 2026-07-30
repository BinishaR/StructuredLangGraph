# # api.py
# import re

# from fastapi import FastAPI, HTTPException
# from fastapi.responses import PlainTextResponse

# from config.logger import logger
# from config.settings import settings
# from schemas import UserQuery, BotResponse, ErrorResponse
# from src.graph.builder import ask_agent, graph
# from src.nodes.agent_nodes import MODEL_NAME
# from src.tools.faq_tools import tools

# app = FastAPI(title=settings.api_title)


# @app.post(
#     "/ask",
#     response_model=BotResponse,
#     tags=["Assistant"],
#     responses={
#         200: {"description": "Successful answer", "model": BotResponse},
#         422: {"description": "Validation error — check input"},
#         429: {"description": "OpenAI rate limit exceeded"},
#         500: {"description": "Internal error", "model": ErrorResponse},
#     },
# )
# def ask_question(query: UserQuery):
#     clean_question = re.sub(r"[?.!,;:'\"]", "", query.question).strip()
#     session_id = query.session_id or "default-session"

#     logger.info(f"POST /ask | session_id={session_id} | question='{query.question}'")

#     try:
#         answer = ask_agent(
#             question=clean_question,
#             session_id=session_id,
#         )

#         return BotResponse(
#             status="success",
#             question=query.question,
#             answer=answer,
#             session_id=query.session_id,
#         )

#     except Exception as e:
#         error_str = str(e)
#         logger.error(f"/ask failed | session_id={session_id} | error={error_str}")

#         if "429" in error_str or "rate_limit" in error_str.lower():
#             raise HTTPException(
#                 status_code=429,
#                 detail="OpenAI rate limit. Please wait and try again.",
#             )

#         raise HTTPException(
#             status_code=500,
#             detail=f"Agent error: {error_str}",
#         )


# @app.get(
#     "/graph/mermaid",
#     tags=["Debug"],
#     response_class=PlainTextResponse,
# )
# def get_graph_mermaid():
#     try:
#         actual_graph = graph.get_graph()
#         return actual_graph.draw_mermaid()
#     except Exception as e:
#         logger.error(f"/graph/mermaid failed | error={str(e)}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"Could not read graph structure: {str(e)}",
#         )
        
import re
import secrets

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import PlainTextResponse

from config.logger import logger
from config.settings import settings
from schemas import (
    UserQuery,
    BotResponse,
    ErrorResponse,
    UpdateVectorstoreResponse,
)
from src.graph.builder import ask_agent, graph
from src.nodes.agent_nodes import MODEL_NAME
from src.rag.retriever import retriever_manager
from src.tools.faq_tools import tools

app = FastAPI(title=settings.api_title)


@app.post(
    "/ask",
    response_model=BotResponse,
    tags=["Assistant"],
    responses={
        200: {"description": "Successful answer", "model": BotResponse},
        422: {"description": "Validation error — check input"},
        429: {"description": "OpenAI rate limit exceeded"},
        500: {"description": "Internal error", "model": ErrorResponse},
    },
)
def ask_question(query: UserQuery):
    clean_question = re.sub(r"[?.!,;:'\"]", "", query.question).strip()
    session_id = query.session_id or "default-session"

    logger.info(f"POST /ask | session_id={session_id} | question='{query.question}'")

    try:
        answer = ask_agent(
            question=clean_question,
            session_id=session_id,
        )

        return BotResponse(
            status="success",
            question=query.question,
            answer=answer,
            session_id=query.session_id,
        )

    except Exception as e:
        error_str = str(e)
        logger.error(f"/ask failed | session_id={session_id} | error={error_str}")

        if "429" in error_str or "rate_limit" in error_str.lower():
            raise HTTPException(
                status_code=429,
                detail="OpenAI rate limit. Please wait and try again.",
            )

        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {error_str}",
        )


@app.get(
    "/graph/mermaid",
    tags=["Debug"],
    response_class=PlainTextResponse,
)
def get_graph_mermaid():
    try:
        actual_graph = graph.get_graph()
        return actual_graph.draw_mermaid()
    except Exception as e:
        logger.error(f"/graph/mermaid failed | error={str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Could not read graph structure: {str(e)}",
        )


@app.post(
    "/update-vectorstore",
    tags=["Admin"],
    response_model=UpdateVectorstoreResponse,
    responses={
        200: {"description": "Vectorstore rebuilt", "model": UpdateVectorstoreResponse},
        401: {"description": "Missing or invalid update key"},
        500: {"description": "Rebuild failed", "model": ErrorResponse},
    },
)
def update_vectorstore(
    x_update_key: str = Header(..., alias="X-Update-Key"),
):
    """
    Rebuild the Chroma vectorstore from the CSVs in data/, replacing whatever
    is currently persisted. Requires the X-Update-Key header to match
    UPDATE_API_KEY from .env.

    Use this instead of committing chroma_db/ to git: run this once after
    each deploy, or whenever the source CSVs change.
    """
    if not secrets.compare_digest(x_update_key, settings.update_api_key):
        logger.warning("POST /update-vectorstore | rejected: invalid update key")
        raise HTTPException(status_code=401, detail="Invalid update key")

    logger.info("POST /update-vectorstore | authorized, starting rebuild")

    try:
        vector_count = retriever_manager.rebuild()
        return UpdateVectorstoreResponse(
            status="success",
            message="Vectorstore rebuilt successfully from source CSVs.",
            vector_count=vector_count,
        )
    except Exception as e:
        logger.error(f"/update-vectorstore failed | error={str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to rebuild vectorstore: {str(e)}",
        )