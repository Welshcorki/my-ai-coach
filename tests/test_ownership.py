"""소유권 격리(user_id 필터) 회귀 테스트.

모든 roadmap/mission 접근은 current_user 본인 것으로 제한되어야 한다.
"""
from tests.conftest import make_user, make_roadmap
from app import models


def test_roadmaps_list_returns_only_own(client, db_session):
    alice = make_user(db_session, "alice@example.com")
    bob = make_user(db_session, "bob@example.com")
    make_roadmap(db_session, alice, "Alice Plan")
    make_roadmap(db_session, bob, "Bob Plan")

    client.login_as(alice)
    resp = client.get("/api/v2/roadmaps")

    assert resp.status_code == 200
    titles = [r["project_title"] for r in resp.json()]
    assert titles == ["Alice Plan"]


def test_cannot_read_others_roadmap_detail(client, db_session):
    alice = make_user(db_session, "alice@example.com")
    bob = make_user(db_session, "bob@example.com")
    bob_roadmap = make_roadmap(db_session, bob, "Bob Plan")

    client.login_as(alice)
    resp = client.get(f"/api/v2/roadmap/{bob_roadmap.id}")

    assert resp.status_code == 404


def test_cannot_complete_others_mission(client, db_session):
    alice = make_user(db_session, "alice@example.com")
    bob = make_user(db_session, "bob@example.com")
    bob_roadmap = make_roadmap(db_session, bob, "Bob Plan")
    mission = models.Mission(
        roadmap_id=bob_roadmap.id,
        week=1,
        theme="주제",
        mission_key="w1_m1",
        title="미션",
        is_completed=False,
    )
    db_session.add(mission)
    db_session.commit()

    client.login_as(alice)
    resp = client.put(f"/api/v2/roadmap/{bob_roadmap.id}/mission/w1_m1/complete")

    assert resp.status_code == 404
    db_session.refresh(mission)
    assert mission.is_completed is False


def test_unauthenticated_request_is_rejected(client, db_session):
    # login_as 호출 전 → 인증 사용자 없음
    resp = client.get("/api/v2/roadmaps")
    assert resp.status_code == 401
