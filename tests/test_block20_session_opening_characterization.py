"""Characterize the synthetic opening flow before any prompt localization."""
from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path

import pytest

sqlmodel = pytest.importorskip("sqlmodel", reason="web integration dependencies are not installed")
from sqlalchemy.pool import StaticPool  # noqa: E402
from sqlmodel import Session, SQLModel, create_engine  # noqa: E402

from src.web.backend.domain import get_stage_by_visit_no, stage_from_key  # noqa: E402
from src.web.backend.models import TherapyCourseRecord  # noqa: E402
from src.web.backend.services.visit_service import (  # noqa: E402
    build_visit_prompt,
    create_visit,
    get_visit_state_for_user,
)

ROOT = Path(__file__).resolve().parents[1]
BASELINE = json.loads(
    (ROOT / "tests/fixtures/block20/session_opening_baseline.json").read_text(encoding="utf-8")
)


def _new_database():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


def test_synthetic_opening_flow_matches_frozen_original_baseline():
    from src.web.backend.domain import pick_school

    engine = _new_database()
    captured = {}
    async def synthetic_reply(history, course, visit, visit_state, psych_context, output_language):
        captured.update(
            history=history,
            output_language=output_language,
            stage_key=visit.stage_key_snapshot,
            visit_no=visit.visit_no,
            planned_visit_count=course.planned_visit_count,
            focus_count=len(psych_context.session_focus),
            retrieved_document_ids=[],
        )
        return {"text": BASELINE["synthetic_assistant_response"], "end": BASELINE["model_end_flag"]}

    with Session(engine) as db:
        course = TherapyCourseRecord(
            course_id="course-synthetic-block20",
            user_id="user-synthetic-block20",
            school_id="cbt",
            title="Percurso sintético",
            planned_visit_count=BASELINE["planned_visit_count"],
            goal_summary="Objetivo sintético",
        )
        db.add(course)
        db.commit()

        state = asyncio.run(create_visit(
            db,
            course.user_id,
            course.course_id,
            opening_note="foco sintético",
            call_llm=synthetic_reply,
            output_language=BASELINE["output_language"],
        ))
        persisted = get_visit_state_for_user(db, course.user_id, state.visit_id)

        baseline_prompt = build_visit_prompt(
            pick_school(course.school_id),
            stage_from_key(BASELINE["stage_key"]),
            BASELINE["visit_no"],
            BASELINE["planned_visit_count"],
        )
        prompt_digest = hashlib.sha256(baseline_prompt.encode("utf-8")).hexdigest()
        stage_digest = hashlib.sha256(
            f"{state.stage.label}\0{state.stage.desc}".encode("utf-8")
        ).hexdigest()
        marker_count = baseline_prompt.count("{{") + baseline_prompt.count("{%")
        assert prompt_digest == BASELINE["prompt_sha256_utf8"]
        assert stage_digest == BASELINE["stage_metadata_sha256_utf8"]
        assert marker_count == BASELINE["unrendered_template_marker_count"]
        assert captured["history"][0]["content"] == baseline_prompt
        assert captured["history"][1]["content"] == BASELINE["seed_user_text"]
        assert captured["stage_key"] == state.stage.key == BASELINE["stage_key"]
        assert captured["visit_no"] == state.visit_no == BASELINE["visit_no"]
        assert captured["planned_visit_count"] == BASELINE["planned_visit_count"]
        assert captured["output_language"] == BASELINE["output_language"]
        assert captured["retrieved_document_ids"] == BASELINE["retrieved_document_ids"]
        assert captured["focus_count"] == BASELINE["context_session_focus_count"]
        assert state.messages[-1].text == persisted.messages[-1].text == BASELINE["synthetic_assistant_response"]
        assert persisted.status == BASELINE["persisted_status"]
        assert persisted.message_count == BASELINE["persisted_message_count"]

    engine.dispose()


def test_stage_selection_for_visit_boundaries_is_stable():
    assert get_stage_by_visit_no(1).key == "assessment"
    assert get_stage_by_visit_no(3).key == "intervention"
    assert get_stage_by_visit_no(9).key == "consolidation"
    assert get_stage_by_visit_no(10).key == "consolidation"


def test_synthetic_opening_failure_uses_existing_ptbr_fallback():
    engine = _new_database()

    async def failing_reply(*_args, **_kwargs):
        raise RuntimeError("synthetic model failure")

    with Session(engine) as db:
        course = TherapyCourseRecord(
            course_id="course-synthetic-failure-block20",
            user_id="user-synthetic-failure-block20",
            school_id="cbt",
            title="Percurso sintético",
            planned_visit_count=BASELINE["planned_visit_count"],
        )
        db.add(course)
        db.commit()
        state = asyncio.run(create_visit(
            db,
            course.user_id,
            course.course_id,
            call_llm=failing_reply,
            output_language=BASELINE["output_language"],
        ))
        persisted = get_visit_state_for_user(db, course.user_id, state.visit_id)

    assert state.messages[-1].text == BASELINE["failure_fallback_text"]
    assert persisted.messages[-1].text == BASELINE["failure_fallback_text"]
    assert persisted.status == BASELINE["persisted_status"]
    engine.dispose()
