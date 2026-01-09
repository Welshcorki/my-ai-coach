from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app import models
from datetime import date, timedelta
from typing import List, Dict, Any

router = APIRouter()

@router.get("/heatmap")
async def get_heatmap_data(db: Session = Depends(get_db)):
    """
    최근 1년 간의 활동량(미션 완료 + 채팅 메시지 수)을 날짜별로 집계하여 반환합니다.
    """
    # 1년 전 날짜 계산
    one_year_ago = date.today() - timedelta(days=365)

    # 1. 일별 채팅 수 집계
    chat_stats = db.query(
        func.date(models.ChatHistory.created_at).label("date"),
        func.count(models.ChatHistory.id).label("count")
    ).filter(
        models.ChatHistory.created_at >= one_year_ago,
        models.ChatHistory.role == "user"
    ).group_by(
        func.date(models.ChatHistory.created_at)
    ).all()

    # 2. 일별 미션 완료 수 집계
    mission_stats = db.query(
        func.date(models.Mission.completed_at).label("date"),
        func.count(models.Mission.id).label("count")
    ).filter(
        models.Mission.completed_at >= one_year_ago,
        models.Mission.is_completed == True
    ).group_by(
        func.date(models.Mission.completed_at)
    ).all()

    # 3. 데이터 병합
    heatmap_map = {}

    for stat in chat_stats:
        d = str(stat.date) # YYYY-MM-DD string
        heatmap_map[d] = heatmap_map.get(d, 0) + stat.count

    for stat in mission_stats:
        d = str(stat.date)
        # 미션 완료는 더 큰 활동으로 간주하여 가중치를 줌 (예: 미션 1개당 3점)
        heatmap_map[d] = heatmap_map.get(d, 0) + (stat.count * 3)

    # 리스트 변환 (프론트엔드 react-calendar-heatmap 형식에 맞춤)
    heatmap_data = [{"date": k, "count": v} for k, v in heatmap_map.items()]

    return heatmap_data

@router.get("/progress/{roadmap_id}")
async def get_roadmap_progress(roadmap_id: int, db: Session = Depends(get_db)):
    """
    특정 로드맵의 진행률(완료된 미션 수 / 전체 미션 수)을 반환합니다.
    """
    total_missions = db.query(models.Mission).filter(models.Mission.roadmap_id == roadmap_id).count()
    completed_missions = db.query(models.Mission).filter(
        models.Mission.roadmap_id == roadmap_id,
        models.Mission.is_completed == True
    ).count()

    if total_missions == 0:
        return {"progress": 0, "total": 0, "completed": 0}

    progress_percentage = round((completed_missions / total_missions) * 100, 1)

    return {
        "progress": progress_percentage,
        "total": total_missions,
        "completed": completed_missions
    }