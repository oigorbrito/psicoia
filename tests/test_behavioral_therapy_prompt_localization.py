import re
from pathlib import Path

from src.sample.prompt_manager import PsychAgentPromptManager


ROOT = Path(__file__).resolve().parents[1]
COMPATIBILITY_TEXT = (
    "表达理解与共情；询问精神科就诊经历",
    "人际关系",
    "婚姻关系",
    "家庭关系",
    "情绪管理",
    "个人成长",
    "社会事件",
    "职业发展",
    "自我探索",
    "学业压力",
    "完全达成",
    "部分达成",
    "未达成",
    "目标调整",
    "问题概念化与目标设定",
    "核心认知与行为干预",
    "巩固与复发预防",
    "待解决",
    "已解决",
    "死亡",
    "自由",
    "孤独",
    "无意义",
    "内摄",
    "回摄",
    "融合",
    "偏转",
    "投射",
    "自我监控",
    "压抑",
    "去敏化",
    "否认",
    "分裂",
    "退行",
    "幻想",
    "投射性认同",
    "情感隔离",
    "理智化",
    "合理化",
    "反向形成",
    "转移",
    "抵消",
    "转向自身",
    "摄入/内向投射",
    "仿同/认同",
    "升华",
    "利他",
    "幽默",
    "预期",
)
MODALITIES = ("bt", "cbt", "het", "pdt", "pmt")


def test_psychagent_prompt_text_is_english_except_fixed_compatibility_values():
    prompt_root = ROOT / "prompts" / "psychagent"
    allowed = re.compile(
        "|".join(re.escape(value) for value in sorted(COMPATIBILITY_TEXT, key=len, reverse=True))
    )
    for modality in MODALITIES:
        for path in (prompt_root / modality).rglob("*.jinja2"):
            for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                remainder = allowed.sub("", line)
                assert not re.search(r"[\u3400-\u9fff]", remainder), f"Unexpected Chinese in {path}:{line_no}"


def test_behavior_therapy_templates_render_and_preserve_output_schemas():
    for modality in MODALITIES:
        manager = PsychAgentPromptManager(ROOT / "prompts" / "psychagent", modality)
        context = {
            "client_info": {},
            "history": [],
            "session_stage": "Assessment",
            "session_focus": ["Understand the current concern"],
            "homework_assigned_from_last_session": [],
            "suggested_skills": [],
            "current_session_dialogue": "Counselor: What would you like to focus on?",
        }
        counselor = manager.render(
            "counselor_system", **context, output_language="Português (Brasil)"
        )
        summary_user = manager.render("summary_user", **context)
        profile_user = manager.render("profile_user", **context)

        assert "Respond in Português (Brasil)" in counselor
        assert "Focus for this session" in summary_user
        assert "Complete counseling conversation" in profile_user
        assert "{{ output_language }}" not in manager.prompts["summary_system"]
        for key in (
            '"session_summary_abstract"',
            '"goal_assessment"',
            '"client_state_analysis"',
            '"next_session_plan"',
            '"homework"',
        ):
            assert key in manager.prompts["summary_system"]

        profile_keys = {
            "bt": ('"target_behavior"',),
            "cbt": ('"special_situations"',),
            "het": ('"existentialism_topic"', '"contact_model"'),
            "pdt": ('"core_conflict"', '"object_relations"', '"behavioral_response_patterns"'),
            "pmt": ('"exception_events"', '"force_field"'),
        }[modality]
        assert all(key in manager.prompts["profile_system"] for key in profile_keys)
