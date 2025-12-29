"""Chat API router for ChatKit endpoint"""
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import Response, StreamingResponse
from sqlmodel import Session

from src.database import get_session
from src.auth.dependencies import get_current_user
from src.models.user import User
from src.todo_chatkit.server import TodoChatKitServer
from src.todo_chatkit.store import PostgreSQLStore, ChatContext

router = APIRouter(prefix="/chatkit", tags=["chat"])

# Initialize store and server (singleton pattern)
store = PostgreSQLStore()
chatkit_server = TodoChatKitServer(store)


@router.post("")
async def chatkit_endpoint(
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """ChatKit endpoint for AI chat interface

    This endpoint processes ChatKit protocol messages and returns
    streaming responses from the AI agent.

    Authentication:
    - Requires valid JWT token via get_current_user dependency
    - User ID is extracted from JWT and used for data isolation

    Args:
        request: FastAPI request with ChatKit protocol body
        session: Database session
        current_user: Authenticated user from JWT

    Returns:
        StreamingResponse or Response based on ChatKit protocol
    """
    # Create context with user ID and session
    context = ChatContext(
        user_id=str(current_user.id),
        session=session
    )

    # Process request with ChatKit server
    result = await chatkit_server.process(await request.body(), context)

    # Return appropriate response type
    if hasattr(result, '__aiter__'):  # Streaming result
        return StreamingResponse(
            result,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no"
            }
        )
    else:  # Non-streaming result
        return Response(
            content=result.json,
            media_type="application/json"
        )


@router.get("/health")
async def chat_health():
    """Health check for chat service"""
    return {
        "status": "healthy",
        "service": "chatkit",
        "provider": "groq"
    }
