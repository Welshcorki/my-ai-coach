from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app import models
from app.schemas.roadmap import RoadmapWithHistory, ChatMessage, RoadmapSummary
from app.schemas.plan import WeekPlan, Mission as MissionSchema

router = APIRouter()

@router.get("/roadmaps", response_model=List[RoadmapSummary])
async def get_all_roadmaps(db: Session = Depends(get_db)):
    """
    저장된 모든 로드맵의 목록과 진행률을 반환합니다.
    """
    roadmaps = db.query(models.Roadmap).order_by(models.Roadmap.created_at.desc()).all()
    result = []
    for r in roadmaps:
        total = len(r.missions)
        completed = len([m for m in r.missions if m.is_completed])
        result.append(RoadmapSummary(
            id=r.id,
            project_title=r.project_title,
            goal=r.goal,
            level=r.level,
            created_at=r.created_at,
            total_missions=total,
            completed_missions=completed
        ))
    return result

@router.get("/roadmap/{roadmap_id}", response_model=RoadmapWithHistory)
async def get_roadmap_detail(roadmap_id: int, db: Session = Depends(get_db)):
    """
    특정 로드맵의 상세 커리큘럼과 채팅 내역을 반환합니다.
    """
    roadmap = db.query(models.Roadmap).filter(models.Roadmap.id == roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    # 미션 데이터를 주차(Week)별로 그룹화
    missions_by_week = {}
    # id 순 정렬 (생성 순서 유지)
    sorted_missions = sorted(roadmap.missions, key=lambda x: x.id)
    
    for m in sorted_missions:
        if m.week not in missions_by_week:
            missions_by_week[m.week] = {"theme": m.theme, "missions": []}
        
        missions_by_week[m.week]["missions"].append(
            MissionSchema(id=m.mission_key, title=m.title, is_completed=m.is_completed)
        )
    
    # WeekPlan 리스트 생성
    curriculum = []
    for week_num in sorted(missions_by_week.keys()):
        data = missions_by_week[week_num]
        curriculum.append(WeekPlan(
            week=week_num,
            theme=data["theme"],
            missions=data["missions"]
        ))

    # 채팅 내역 변환
    chat_history = []
    sorted_chats = sorted(roadmap.chats, key=lambda x: x.id)
    
    for chat in sorted_chats:
        chat_history.append(ChatMessage(
            id=str(chat.id),
            role=chat.role,
            text=chat.text,
            image=chat.image,
            modelImage=chat.model_image,
            created_at=chat.created_at
        ))

    return RoadmapWithHistory(
        id=roadmap.id,
        project_title=roadmap.project_title,
        curriculum=curriculum,
        chat_history=chat_history
    )

@router.put("/roadmap/{roadmap_id}/mission/{mission_key}/complete")
async def complete_mission(roadmap_id: int, mission_key: str, db: Session = Depends(get_db)):
    """
    특정 로드맵의 특정 미션을 완료 처리합니다.
    """
    mission = db.query(models.Mission).filter(
        models.Mission.roadmap_id == roadmap_id,
        models.Mission.mission_key == mission_key
    ).first()
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
        
    mission.is_completed = True
    db.commit()
    return {"status": "success", "roadmap_id": roadmap_id, "mission_key": mission_key}