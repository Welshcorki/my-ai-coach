from fastapi import APIRouter, HTTPException
import google.generativeai as genai
import base64
from app.core.config import settings
from app.schemas.review import ReviewRequest, ReviewResponse

router = APIRouter()

# Gemini API 설정
genai.configure(api_key=settings.GOOGLE_API_KEY)

@router.post("/review", response_model=ReviewResponse)
async def review_image(request: ReviewRequest):
    """
    사용자가 업로드한 이미지를 AI가 분석하여 피드백을 제공합니다.
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Base64 문자열에서 실제 데이터 부분만 추출 (혹시 헤더가 포함되어 있다면)
        # 예: "data:image/png;base64,iVBOR..." -> "iVBOR..."
        if "," in request.base64Image:
            image_data_str = request.base64Image.split(",")[1]
        else:
            image_data_str = request.base64Image
            
        # Base64 디코딩
        try:
            image_bytes = base64.b64decode(image_data_str)
        except Exception as decode_err:
             raise HTTPException(status_code=400, detail=f"Invalid Base64 image data: {str(decode_err)}")

        # Gemini Vision 모델 호출을 위한 이미지 파트 구성
        image_part = {
            "mime_type": request.mimeType,
            "data": image_bytes
        }
        
        # 프롬프트 구성
        prompt_text = request.prompt if request.prompt else "이 이미지를 분석하고 학습에 도움이 되는 피드백을 주세요."
        
        # 콘텐츠 생성 (멀티모달 요청: [프롬프트, 이미지])
        response = model.generate_content([prompt_text, image_part])
        
        return ReviewResponse(text=response.text)

    except Exception as e:
        print(f"Error in review: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Vision Analysis Error: {str(e)}")