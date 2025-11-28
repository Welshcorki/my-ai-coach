from fastapi import APIRouter
from app.schemas.chat import ChatMessage
from app.agents.chatbot import chatbot_agent

router = APIRouter()

@router.post("/chat", response_model=ChatMessage)
async def post_chat(message: ChatMessage):
    """
    Receives a chat message, gets a response from the chatbot agent,
    and returns it.
    """
    response_content = chatbot_agent.get_response(message.content)
    
    ai_response = ChatMessage(
        content=response_content,
        sender="ai"
    )
    return ai_response
