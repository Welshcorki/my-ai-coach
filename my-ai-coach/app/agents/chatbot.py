from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from app.core.config import settings

class ChatbotAgent:
    def __init__(self):
        """
        Initializes the ChatbotAgent, setting up the language model.
        """
        self.llm = None
        if settings.GOOGLE_API_KEY:
            try:
                self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=settings.GOOGLE_API_KEY)
            except Exception as e:
                print(f"Error initializing Google Generative AI: {e}")
        else:
            print("⚠️ ChatbotAgent: GOOGLE_API_KEY not found. The chatbot will not be functional.")

    def get_response(self, message: str) -> str:
        """
        Generates a response to a user message using the configured LLM.
        """
        if not self.llm:
            return "챗봇이 API 키 문제로 인해 현재 설정되지 않았습니다. .env 파일을 확인해주세요."

        try:
            # Wrap the user's message in the format expected by the LLM
            human_message = HumanMessage(content=message)
            ai_response = self.llm.invoke([human_message])
            return ai_response.content
        except Exception as e:
            print(f"Error during LLM invocation: {e}")
            return "죄송합니다, 답변을 생성하는 동안 오류가 발생했습니다."

# A single instance of the agent that can be used across the application
chatbot_agent = ChatbotAgent()
