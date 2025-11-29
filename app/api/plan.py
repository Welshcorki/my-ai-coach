from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import google.generativeai as genai
import json
import re
from app.core.config import settings
from app.schemas.plan import PlanRequest, RoadmapResponse
from app.core.database import get_db
from app import models

router = APIRouter()

# Gemini API 설정
genai.configure(api_key=settings.GOOGLE_API_KEY)

@router.post("/plan", response_model=RoadmapResponse)
async def generate_plan(request: PlanRequest, db: Session = Depends(get_db)):
    """
    사용자의 목표, 수준, 기간을 받아 AI를 통해 학습 로드맵을 생성하고 DB에 저장합니다.
    """
    try:
        # 모델 변경: gemini-2.5-flash
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = f"""
        You are an expert study coach. Create a structured study roadmap based on the user's request.
        
        [User Information]
        - Goal: {request.goal}
        - Level: {request.level}
        - Duration: {request.duration} weeks
        - Frequency: {request.frequency}

        [Instructions]
        1. Create a week-by-week plan for exactly {request.duration} weeks.
        2. Each week should have a 'theme' and specific 'missions'.
        3. The number and difficulty of missions MUST be adjusted based on the 'Frequency' ({request.frequency}).
           - If frequency is high (e.g., "Everyday"), provide more detailed and numerous missions (3-5 missions/week).
           - If frequency is low (e.g., "Weekends only"), provide fewer, focused missions (1-2 missions/week).
        4. Mission 'id' format: 'w{{week}}_m{{number}}' (e.g., w1_m1).
        5. Response MUST be valid JSON only. No markdown blocks.

        [JSON Structure Example]
        {{
          "project_title": "Mastering Python in 4 Weeks",
          "curriculum": [
            {{
              "week": 1,
              "theme": "Python Basics",
              "missions": [
                {{ "id": "w1_m1", "title": "Install Python & IDE", "is_completed": false }},
                {{ "id": "w1_m2", "title": "Variables & Data Types", "is_completed": false }}
              ]
            }}
          ]
        }}
        """

        response = model.generate_content(prompt)
        response_text = response.text

        # 안전한 파싱을 위한 정제 (Markdown 코드 블록 제거)
        cleaned_text = re.sub(r"```json\s*|\s*```", "", response_text).strip()
        
        # 가끔 시작/끝에 이상한 문자가 붙을 경우를 대비해 첫 '{'와 마지막 '}' 사이만 추출
        match = re.search(r"\{.*\}", cleaned_text, re.DOTALL)
        if match:
            cleaned_text = match.group(0)

        roadmap_data = json.loads(cleaned_text)

        # DB 저장 로직
        db_roadmap = models.Roadmap(
            project_title=roadmap_data["project_title"],
            goal=request.goal,
            level=request.level,
            duration=request.duration,
            frequency=request.frequency
        )
        db.add(db_roadmap)
        db.commit()
        db.refresh(db_roadmap)

        # ID를 응답 데이터에 추가
        roadmap_data['id'] = db_roadmap.id

        for week_plan in roadmap_data["curriculum"]:
            for mission in week_plan["missions"]:
                db_mission = models.Mission(
                    roadmap_id=db_roadmap.id,
                    week=week_plan["week"],
                    theme=week_plan["theme"],
                    mission_key=mission["id"],
                    title=mission["title"],
                    is_completed=mission["is_completed"]
                )
                db.add(db_mission)
        
        db.commit()

        return roadmap_data

    except json.JSONDecodeError:
        print(f"JSON Parse Error. Raw response: {response_text}")
        raise HTTPException(status_code=500, detail="Failed to parse AI response.")
    except Exception as e:
        print(f"Error generating plan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI Service Error: {str(e)}")