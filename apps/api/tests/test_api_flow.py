import os
import tempfile
import unittest
from pathlib import Path


class ApiFlowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        root = Path(cls.temp.name)
        os.environ["DATABASE_URL"] = f"sqlite:///{(root / 'test.sqlite').as_posix()}"
        os.environ["MEMORY_PATH"] = str(root / "memory")

        from fastapi.testclient import TestClient
        from app.main import app

        cls.client_context = TestClient(app)
        cls.client = cls.client_context.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client_context.__exit__(None, None, None)
        from app.db.session import engine

        engine.dispose()
        cls.temp.cleanup()

    def test_complete_mvp_flow(self):
        status = self.client.get("/api/onboarding/status")
        self.assertEqual(status.status_code, 200)
        self.assertFalse(status.json()["onboarding_complete"])

        gated = self.client.get("/api/jobs/feed")
        self.assertEqual(gated.status_code, 403)

        profile = self.client.put(
            "/api/onboarding/profile",
            json={
                "name": "Test Developer",
                "title": "Backend Engineer",
                "skills_notes": "Python, FastAPI, SQL",
            },
        )
        self.assertEqual(profile.status_code, 200)

        resume_text = (
            "Test Developer\nBackend Engineer\n"
            + "Python FastAPI SQL APIs testing distributed systems. " * 12
        )
        upload = self.client.post(
            "/api/onboarding/resume",
            files={"file": ("resume.txt", resume_text, "text/plain")},
        )
        self.assertEqual(upload.status_code, 200)
        self.assertTrue(upload.json()["ok"])
        self.assertNotIn("preview", upload.json())

        complete = self.client.post("/api/onboarding/complete", json={})
        self.assertEqual(complete.status_code, 200)
        self.assertTrue(complete.json()["onboarding_complete"])

        feed = self.client.get("/api/jobs/feed")
        self.assertEqual(feed.status_code, 200)
        self.assertEqual(feed.json()["mode"], "ranked")
        self.assertGreaterEqual(len(feed.json()["jobs"]), 3)

        description = (
            "Backend developer needed for Python FastAPI APIs and SQL systems "
            "in Tel Aviv. Build tested production services."
        )
        added = self.client.post("/api/jobs", json={"description": description})
        self.assertEqual(added.status_code, 200)
        self.assertTrue(added.json()["title"])

        tailored = self.client.post(
            "/api/tailor",
            json={"job_description": description, "run_crew": False},
        )
        self.assertEqual(tailored.status_code, 200)
        body = tailored.json()
        self.assertIn("Test Developer", body["content_md"])
        self.assertIn("Python", body["content_md"])

        exported = self.client.get(f"/api/tailor/{body['id']}/docx")
        self.assertEqual(exported.status_code, 200)
        self.assertTrue(exported.content.startswith(b"PK"))

        alert = self.client.post("/api/alerts/demo", json={})
        self.assertEqual(alert.status_code, 200)
        marked = self.client.post(f"/api/alerts/{alert.json()['id']}/read", json={})
        self.assertEqual(marked.status_code, 200)
        self.assertTrue(marked.json()["read"])


if __name__ == "__main__":
    unittest.main()
