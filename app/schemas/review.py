from pydantic import BaseModel

class ReviewRequest(BaseModel):
    base64Image: str
    mimeType: str
    prompt: str

class ReviewResponse(BaseModel):
    text: str
