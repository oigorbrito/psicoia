from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import HTTPException
from pydantic import BaseModel


class StageInfo(BaseModel):
    key: str
    label: str
    desc: str
    range: List[int]
    color: Optional[str] = None


class SchoolInfo(BaseModel):
    id: str
    name: str
    color: str
    desc: str
    style: str


STAGES: Dict[str, Dict[str, object]] = {
    "assessment": {
        "label": "Problem conceptualization and goal setting",
        "range": [1, 2],
        "desc": "Focus on defining concerns, gathering information, building rapport, and setting actionable goals.",
        "color": "text-blue-600 bg-blue-50",
    },
    "intervention": {
        "label": "Core cognitive and behavioral interventions",
        "range": [3, 8],
        "desc": "Use structured interventions and practice focused on key cognitive and behavioral patterns.",
        "color": "text-purple-600 bg-purple-50",
    },
    "consolidation": {
        "label": "Consolidation and relapse prevention",
        "range": [9, 10],
        "desc": "Consolidate progress, support application, address relapse prevention, and prepare for an orderly ending.",
        "color": "text-green-600 bg-green-50",
    },
}


SCHOOLS: List[SchoolInfo] = [
    SchoolInfo(
        id="behavioral",
        name="Behavior Therapy (BT)",
        color="bg-amber-500",
        desc="Changes specific behavior patterns through reinforcement, desensitization, and modeling, emphasizing observable, practiceable, and trackable change.",
        style="Direct, practical, and skills-oriented",
    ),
    SchoolInfo(
        id="cbt",
        name="Cognitive Behavioral Therapy (CBT)",
        color="bg-blue-500",
        desc="Focuses on relationships among thoughts, emotions, and behaviors, and on identifying and reframing distressing automatic thoughts.",
        style="Rational, structured, and problem-solving oriented",
    ),
    SchoolInfo(
        id="humanistic",
        name="Humanistic-Existential Therapy (HET)",
        color="bg-rose-500",
        desc="Emphasizes an authentic relationship, acceptance, and exploration of meaning to help clients understand present experience and make autonomous choices.",
        style="Warm, accepting, and person-centered",
    ),
    SchoolInfo(
        id="psychodynamic",
        name="Psychodynamic Therapy (PDT)",
        color="bg-indigo-600",
        desc="Explores how unconscious conflicts and early experiences may affect current relationships and emotional patterns, supporting self-understanding.",
        style="In-depth exploration of inner conflicts and relationship patterns",
    ),
    SchoolInfo(
        id="postmodern",
        name="Postmodern Therapy (PMT)",
        color="bg-teal-500",
        desc="Uses externalization, narrative re-authoring, and discovery of exceptions to help clients develop a more empowering life story.",
        style="Collaborative, empowering, and open to multiple perspectives",
    ),
]

SCHOOL_TO_PSYCHAGENT_SECT: Dict[str, str] = {
    "behavioral": "bt",
    "cbt": "cbt",
    "humanistic": "het",
    "psychodynamic": "pdt",
    "postmodern": "pmt",
}

STAGE_KEY_TO_SKILL_STAGE: Dict[str, int] = {
    "assessment": 1,
    "intervention": 2,
    "consolidation": 3,
}

SUMMARY_STAGE_TO_STAGE_KEY: Dict[str, str] = {
    "assessment": "assessment",
    "intervention": "intervention",
    "consolidation": "consolidation",
    "问题概念化与目标设定": "assessment",
    "核心认知与行为干预": "intervention",
    "巩固与复发预防": "consolidation",
    # Backward-compatible aliases from older UI copy.
    "评估性会谈": "assessment",
    "咨询性会谈": "intervention",
    "巩固性会谈": "consolidation",
}


def stage_from_key(key: str) -> StageInfo:
    value = STAGES[key]
    return StageInfo(
        key=key,
        label=value["label"],
        desc=value["desc"],
        range=value["range"],
        color=value.get("color"),
    )


def get_stage_by_visit_no(visit_no: int) -> StageInfo:
    for key, value in STAGES.items():
        start, end = value["range"]
        if start <= visit_no <= end:
            return stage_from_key(key)
    last_key = list(STAGES.keys())[-1]
    return stage_from_key(last_key)


def pick_school(school_id: str) -> SchoolInfo:
    for school in SCHOOLS:
        if school.id == school_id:
            return school
    raise HTTPException(status_code=404, detail="School not found")


def school_to_psychagent_sect(school_id: str) -> str:
    sect = SCHOOL_TO_PSYCHAGENT_SECT.get(school_id)
    if not sect:
        raise HTTPException(status_code=404, detail="Unsupported school for PsychAgent prompts")
    return sect


def stage_key_to_skill_stage(stage_key: str) -> int:
    return STAGE_KEY_TO_SKILL_STAGE.get(stage_key, 1)


def summary_stage_to_stage_key(raw_stage: str) -> Optional[str]:
    text = str(raw_stage or "").strip()
    if not text:
        return None
    return SUMMARY_STAGE_TO_STAGE_KEY.get(text)
