import asyncio
from types import SimpleNamespace

from sample.skill_manager import LoadedSkillStage, SkillManager


class CountingBackend:
    def __init__(self):
        self.calls = 0

    async def chat_text(self, messages, **kwargs):
        self.calls += 1
        return '{"skill_id":["root-1"]}'


def build_manager(root_ids):
    backend = CountingBackend()
    manager = SkillManager(backend=backend, runtime_config=SimpleNamespace())
    manager._select_system_prompt = "select"
    manager._select_user_prompt = "choose"
    meta = {
        root_id: {"skill_id": root_id, "skill_name": root_id, "parent_ids": [root_id]}
        for root_id in root_ids
    }
    micro = {
        f"child-{root_id}": {
            "skill_id": f"child-{root_id}", "skill_name": f"child-{root_id}",
            "parent_ids": [root_id, f"child-{root_id}"],
        }
        for root_id in root_ids
    }
    manager.skill_lib = {
        "cbt": {"stage1": LoadedSkillStage(meta=meta, micro=micro, leaf=meta)}
    }
    return manager, backend


def test_single_category_skips_redundant_coarse_model_call():
    manager, backend = build_manager(["root-1"])

    selected, _, ids, _ = asyncio.run(manager.corse_filter(
        sect="cbt", session_goals={}, stage=1, n=20
    ))

    assert backend.calls == 0
    assert ids == [("cbt", "root-1")]
    assert [item["skill_id"] for item in selected[0]["micro_skills"]] == ["child-root-1"]


def test_multiple_categories_still_use_coarse_model_selection():
    manager, backend = build_manager(["root-1", "root-2"])

    _, _, ids, _ = asyncio.run(manager.corse_filter(
        sect="cbt", session_goals={}, stage=1, n=1
    ))

    assert backend.calls == 1
    assert ids == [("cbt", "root-1")]
