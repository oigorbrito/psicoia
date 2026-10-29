import asyncio

import pytest

from src.sample.core.schemas import RuntimeConfig
from src.sample.skill_manager import SkillManager


@pytest.mark.parametrize(
    ("language", "suffix"),
    [("English", "en"), ("Português (Brasil)", "pt-BR")],
)
def test_localized_retrieval_embeds_original_query_without_chinese_rewrite(language, suffix):
    async def run():
        manager = SkillManager(backend=None, runtime_config=RuntimeConfig(output_language=language))
        embedded_texts = []

        async def embed(texts):
            embedded_texts.extend(texts)
            return [[1.0, 0.0] for _ in texts]

        async def unexpected_rewrite(**_kwargs):
            raise AssertionError("localized catalog must not use the Chinese-only query rewriter")

        manager._embed_by_api = embed
        manager.rewrite = unexpected_rewrite
        candidates = [
            {"skill_id": "10", "skill_name": "target", "embedding_to_retrive": [1.0, 0.0], "embedding_to_merge": [1.0, 0.0]},
            {"skill_id": "11", "skill_name": "other", "embedding_to_retrive": [0.0, 1.0], "embedding_to_merge": [0.0, 1.0]},
        ]
        query = "synthetic query in the selected locale"
        retrieved, trace = await manager.retrive(
            sect="cbt",
            query=query,
            session_stage=1,
            session_goals={},
            diag_hist=[],
            candidate_skills=candidates,
        )
        assert manager._skill_locale_suffix() == suffix
        assert embedded_texts == [query]
        assert [item["skill_id"] for item in retrieved] == ["10", "11"]
        assert trace["rewrite_skipped"] == "localized_query_language_preserved"

    asyncio.run(run())


def test_retrieval_rejects_index_query_dimension_mismatch():
    async def run():
        manager = SkillManager(backend=None, runtime_config=RuntimeConfig(output_language="English"))

        async def embed(_texts):
            return [[1.0, 0.0]]

        manager._embed_by_api = embed
        with pytest.raises(RuntimeError, match="dimension mismatch"):
            await manager.retrive(
                sect="cbt",
                query="dimension probe",
                session_stage=1,
                session_goals={},
                diag_hist=[],
                candidate_skills=[
                    {
                        "skill_id": "1",
                        "embedding_to_retrive": [1.0, 0.0, 0.0],
                        "embedding_to_merge": [1.0, 0.0, 0.0],
                    }
                ],
            )

    asyncio.run(run())


def test_skill_manager_passes_call_specific_model_kwargs():
    class Backend:
        async def chat_text(self, *, messages, **kwargs):
            assert [message["role"] for message in messages] == ["system", "user"]
            return kwargs

    async def run():
        manager = SkillManager(backend=Backend(), runtime_config=RuntimeConfig(output_language="English"))
        result = await manager.llm_response("system", "user", model_kwgs={"max_tokens": 256})
        assert result == {"max_tokens": 256}

    asyncio.run(run())


def test_locale_cache_paths_are_separate(tmp_path):
    english = SkillManager(backend=None, runtime_config=RuntimeConfig(output_language="English"))
    portuguese = SkillManager(backend=None, runtime_config=RuntimeConfig(output_language="Português (Brasil)"))
    (tmp_path / "micro_skills.en.json").write_text("{}", encoding="utf-8")
    (tmp_path / "micro_skills.pt-BR.json").write_text("{}", encoding="utf-8")

    en_path = english._micro_skills_cache_path(tmp_path)
    pt_path = portuguese._micro_skills_cache_path(tmp_path)
    assert en_path.name == "micro_skills.en.pt"
    assert pt_path.name == "micro_skills.pt-BR.pt"
    assert en_path != pt_path
