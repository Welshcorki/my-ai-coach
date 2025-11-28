from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.reviewer import reviewer_agent

router = APIRouter()

class ReviewRequest(BaseModel):
    """Image review request model"""
    base64_image: str
    mime_type: str
    prompt: str

class ReviewResponse(BaseModel):
    """Image review response model"""
    feedback: str

@router.post("/review", response_model=ReviewResponse, tags=["Reviewer Agent"])
async def review_image(request: ReviewRequest):
    """
    Receives an image and a prompt, gets feedback from the Reviewer Agent,
    and returns it.
    """
    feedback_content = reviewer_agent.get_review(
        base64_image=request.base64_image,
        mime_type=request.mime_type,
        prompt=request.prompt
    )
    
    return ReviewResponse(feedback=feedback_content)
