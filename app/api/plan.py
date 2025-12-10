from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from sqlalchemy.orm import Session
import google.generativeai as genai
import json
import re
import os
import shutil
import logging
from typing import Optional
from app.core.config import settings
from app.schemas.plan import RoadmapResponse
from app.core.database import get_db
from app import models

# 로거 설정
logger = logging.getLogger(__name__)

router = APIRouter()

# Gemini API 설정
genai.configure(api_key=settings.GOOGLE_API_KEY)

@router.post("/plan", response_model=RoadmapResponse)
async def generate_plan(
    goal: str = Form(...),
    level: str = Form(...),
    duration: int = Form(...),
    frequency: str = Form(...),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    사용자의 목표, 수준, 기간 및 선택적 학습 자료(PDF 등)를 받아 AI를 통해 학습 로드맵을 생성하고 DB에 저장합니다.
    """
    temp_filename = None
    uploaded_file = None

    try:
        logger.info(f"Generating plan for Goal: {goal}, Level: {level}, Duration: {duration} weeks")
        
        # 모델 설정: gemini-2.5-flash (멀티모달 지원)
        model = genai.GenerativeModel('gemini-2.5-flash')

        # 기본 프롬프트 구성
        base_instruction = f"""
        You are an expert study coach. Create a structured study roadmap based on the user's request.
        
        [User Information]
        - Goal: {goal}
        - Level: {level}
        - Duration: {duration} weeks
        - Frequency: {frequency}
        """

        file_instruction = ""
        request_content = []

        # 파일 처리 로직
        if file:
            # 1. 파일명 안전하게 추출 (path traversal 공격 방지)
            # os.path.basename()을 사용하여 파일명만 추출하고 경로 제거
            safe_filename = os.path.basename(file.filename) if file.filename else "uploaded_file"
            # 추가 보안: 특수 문자 제거 및 유효한 파일명으로 변환
            safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', safe_filename)
            # 파일명이 비어있거나 너무 긴 경우 처리
            if not safe_filename or len(safe_filename) > 255:
                safe_filename = "uploaded_file"
            
            # 2. 로컬에 임시 저장 (안전한 파일명 사용)
            temp_filename = f"temp_{safe_filename}"
            with open(temp_filename, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # 3. Gemini에 파일 업로드
            logger.info(f"Uploading file to Gemini: {temp_filename}")
            uploaded_file = genai.upload_file(temp_filename)
            
            # 4. 프롬프트에 파일 참조 지시 추가
            file_instruction = """
            [Reference Material]
            - A file has been uploaded by the user. 
            - **CRITICAL:** You MUST analyze the uploaded file (Table of Contents, key concepts) and strictly base the curriculum on this material.
            - Ensure the roadmap covers the key topics found in the file within the given duration.
            """
            
            # 5. 요청 콘텐츠 구성 (프롬프트 + 파일)
            request_content = [base_instruction + file_instruction, uploaded_file]
        else:
            # 파일이 없으면 텍스트 프롬프트만 사용
            request_content = [base_instruction]

        # 공통 프롬프트 (출력 형식 등)
        common_instruction = f"""
        [Instructions]
        1. Create a week-by-week plan for exactly {duration} weeks.
        2. Each week should have a 'theme' and specific 'missions'.
        3. The number and difficulty of missions MUST be adjusted based on the 'Frequency' ({frequency}).
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
        
        # 최종 요청 생성 (리스트의 첫 번째 요소인 텍스트 프롬프트에 공통 지시사항 추가)
        if isinstance(request_content[0], str):
            request_content[0] += common_instruction

        # 콘텐츠 생성 요청
        logger.info("Requesting content generation from Gemini...")
        response = model.generate_content(request_content)
        response_text = response.text

        # 안전한 파싱을 위한 정제 (Markdown 코드 블록 제거)
        cleaned_text = re.sub(r"```json\s*|\s*```", "", response_text).strip()
        
        # 가끔 시작/끝에 이상한 문자가 붙을 경우를 대비해 첫 '{'와 마지막 '}' 사이만 추출
        match = re.search(r"\{.*\}", cleaned_text, re.DOTALL)
        if match:
            cleaned_text = match.group(0)

        roadmap_data = json.loads(cleaned_text)
        logger.info(f"Roadmap generated successfully: {roadmap_data.get('project_title')}")

        # DB 저장 로직
        db_roadmap = models.Roadmap(
            project_title=roadmap_data["project_title"],
            goal=goal,
            level=level,
            duration=duration,
            frequency=frequency
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
        logger.error(f"JSON Parse Error. Raw response: {response_text}")
        raise HTTPException(status_code=500, detail="Failed to parse AI response.")
    except Exception as e:
        logger.error(f"Error generating plan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI Service Error: {str(e)}")
    finally:
        # 리소스 정리
        if temp_filename and os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
                logger.info(f"Deleted temp file: {temp_filename}")
            except Exception as e:
                logger.error(f"Failed to delete temp file: {e}")
        
        if uploaded_file:
            try:
                uploaded_file.delete()
                logger.info("Deleted file from Gemini.")
            except Exception as e:
                logger.error(f"Failed to delete file from Gemini: {e}")
