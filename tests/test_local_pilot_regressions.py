import unittest
from unittest.mock import AsyncMock, patch

from src.sample.skill_manager import SkillManager

from src.sample.backends.ollama_local import is_loopback_url
from src.sample.core.schemas import ConfigValidationError, RuntimeConfig
from src.sample.utils import extract_public_response


class LocalPilotRegressions(unittest.TestCase):
    def test_public_output_never_includes_reasoning(self):
        self.assertEqual(extract_public_response('<think>private</think><response>hello', '</end>'), ('hello', False))
        self.assertEqual(extract_public_response('<think>private'), ('', False))
        self.assertEqual(extract_public_response('<response>hello<skill'), ('', False))
        self.assertEqual(extract_public_response('<response>hello<skill>private'), ('hello', False))
        self.assertEqual(extract_public_response('<response>done</response></end>', '</end>'), ('done', True))

    def test_unauthenticated_endpoint_only_loopback(self):
        self.assertTrue(is_loopback_url('http://127.0.0.1:11434/v1'))
        for url in ('http://example.com/v1', 'http://127.0.0.1.example.com/v1', 'https://127.0.0.1/v1', 'http://user@127.0.0.1/v1'):
            self.assertFalse(is_loopback_url(url))
        with self.assertRaises(ConfigValidationError):
            RuntimeConfig.from_dict({'psychagent_embedding_api_key_env': '', 'psychagent_embedding_base_url': 'http://example.com/v1'})


class RetrievalRegressions(unittest.IsolatedAsyncioTestCase):
    # Provider calls are mocked here only to isolate invalid vector handling.
    async def test_dimension_mismatch_is_not_scored(self):
        runtime = RuntimeConfig(output_language='Português (Brasil)')
        manager = SkillManager(backend=None, runtime_config=runtime)
        candidate = {'skill_id': 'synthetic', 'embedding_to_merge': [1.0], 'embedding_to_retrive': [1.0, 2.0]}
        with patch.object(manager, '_embed_by_api', new=AsyncMock(return_value=[[1.0]])):
            with self.assertRaisesRegex(RuntimeError, 'dimension mismatch'):
                await manager.retrive('bt', 'synthetic', 1, {}, [], candidate_skills=[candidate])

    async def test_nonfinite_query_is_rejected(self):
        runtime = RuntimeConfig(output_language='Português (Brasil)')
        manager = SkillManager(backend=None, runtime_config=runtime)
        with patch.object(manager, '_embed_by_api', new=AsyncMock(return_value=[[float('nan')]])):
            with self.assertRaisesRegex(RuntimeError, 'non-finite'):
                await manager.retrive('bt', 'synthetic', 1, {}, [], candidate_skills=[{'skill_id': 'synthetic'}])


if __name__ == '__main__':
    unittest.main()
