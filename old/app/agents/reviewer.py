from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate


from app.core.config import settings

class ReviewerAgent:
    def __init__(self):
        """
        Initializes the ReviewerAgent for image analysis.
        """
        self.llm = None
        if settings.GOOGLE_API_KEY:
            try:
                # Vision-capable model
                self.llm = ChatGoogleGenerativeAI(model="gemini-pro-vision", google_api_key=settings.GOOGLE_API_KEY)
            except Exception as e:
                print(f"Error initializing Google Generative AI for Vision: {e}")
        else:
            print("⚠️ ReviewerAgent: GOOGLE_API_KEY not found. The reviewer will not be functional.")

    def get_review(self, base64_image: str, mime_type: str, prompt: str) -> str:
        """
        Analyzes an image with a given prompt and returns constructive feedback.
        """
        if not self.llm:
            return "리뷰 에이전트가 API 키 문제로 인해 현재 설정되지 않았습니다. .env 파일을 확인해주세요."

        try:
            image_message = {
                "type": "image_url",
                "image_url": f"data:{mime_type};base64,{base64_image}",
            }
            
            text_message = {
                "type": "text",
                "text": f"""
                당신은 'Grow'라는 AI 학습 코치입니다. 사용자가 자신의 작업 증명으로 이미지를 제출했습니다.
                이미지를 분석하고 사용자의 프롬프트에 기반하여 건설적이고 격려적인 피드백을 제공하세요.
                
                **사용자 프롬프트:** "{prompt}"
                
                잘한 점을 지적하고 개선할 점 한두 가지를 제안하세요.
                이미지가 불분명하거나 관련이 없는 경우, 정중하게 더 나은 이미지를 요청하세요.
                """,
            }

            message = HumanMessage(content=[text_message, image_message])
            
            ai_response = self.llm.invoke([message])
            return ai_response.content
        except Exception as e:
            print(f"Error during Vision model invocation: {e}")
            return "죄송합니다, 이미지를 분석하는 동안 오류가 발생했습니다."

reviewer_agent = ReviewerAgent()
