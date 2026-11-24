"""Isolated transaction regressions; provider failure is simulated, not an E2E test."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src' / 'web'))
import main


class FailureTransactions(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.original_engine = main.engine
        main.engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
        SQLModel.metadata.create_all(main.engine)
        main.run_sqlite_migrations()
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=main.app), base_url='http://test')
        response = await self.client.post('/auth/register', json={'username': 'synthetic', 'password': 'synthetic'})
        self.headers = {'Authorization': 'Bearer ' + response.json()['token']}

    async def asyncTearDown(self):
        await self.client.aclose()
        main.engine.dispose()
        main.engine = self.original_engine

    async def test_failed_opening_rolls_back_course_and_visit(self):
        with patch.object(main, 'get_psychagent_backend', side_effect=RuntimeError('provider unavailable')):
            response = await self.client.post('/courses', headers=self.headers, json={
                'school_id': 'behavioral', 'title': 'synthetic', 'auto_start_first_visit': True,
            })
        self.assertEqual(response.status_code, 502)
        self.assertEqual((await self.client.get('/courses', headers=self.headers)).json(), [])

    async def test_unstarted_course_can_still_be_created(self):
        response = await self.client.post('/courses', headers=self.headers, json={
            'school_id': 'behavioral', 'title': 'synthetic', 'auto_start_first_visit': False,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len((await self.client.get('/courses', headers=self.headers)).json()), 1)


if __name__ == '__main__':
    unittest.main()
