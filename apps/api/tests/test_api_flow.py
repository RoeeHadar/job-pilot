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
        top = feed.json()["jobs"][0]
        self.assertIn("keyword_gaps", top)
        self.assertIsInstance(top["keyword_gaps"], list)
        self.assertIsNotNone(top.get("rubric"))
        self.assertEqual(len(top["rubric"]), 5)
        self.assertEqual(top["rubric_mode"], "heuristic")
        dim_ids = {d["id"] for d in top["rubric"]}
        self.assertEqual(
            dim_ids,
            {
                "hard_requirements",
                "skills_evidence",
                "role_alignment",
                "israel_location",
                "risks_gaps",
            },
        )

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
        self.assertTrue(body.get("review_ok", True))
        self.assertIsInstance(body.get("review_issues", []), list)

        exported = self.client.get(f"/api/tailor/{body['id']}/docx")
        self.assertEqual(exported.status_code, 200)
        self.assertTrue(exported.content.startswith(b"PK"))

        alert = self.client.post("/api/alerts/demo", json={})
        self.assertEqual(alert.status_code, 200)
        marked = self.client.post(f"/api/alerts/{alert.json()['id']}/read", json={})
        self.assertEqual(marked.status_code, 200)
        self.assertTrue(marked.json()["read"])

        job_id = feed.json()["jobs"][0]["id"]
        liked = self.client.post(
            f"/api/jobs/{job_id}/feedback",
            json={"action": "like"},
        )
        self.assertEqual(liked.status_code, 200)
        self.assertEqual(liked.json()["feedback"], "like")
        from app.settings import get_settings

        fits = get_settings().memory_dir / "rag" / "fits"
        self.assertTrue(fits.exists())
        self.assertTrue(any(fits.iterdir()))

        pack = self.client.post(f"/api/jobs/{job_id}/outreach-pack", json={})
        self.assertEqual(pack.status_code, 200)
        self.assertIn("short_pitch", pack.json())
        self.assertIn("never auto-sends", pack.json()["disclaimer"].lower())

        ready = self.client.post(
            f"/api/jobs/{job_id}/status",
            json={"status": "ready"},
        )
        self.assertEqual(ready.status_code, 200)
        self.assertEqual(ready.json()["status"], "ready")

        dismiss_id = feed.json()["jobs"][1]["id"]
        dismissed = self.client.post(
            f"/api/jobs/{dismiss_id}/feedback",
            json={"action": "dismiss"},
        )
        self.assertEqual(dismissed.status_code, 200)
        after = self.client.get("/api/jobs/feed")
        ids = {j["id"] for j in after.json()["jobs"]}
        self.assertNotIn(dismiss_id, ids)


if __name__ == "__main__":
    unittest.main()
