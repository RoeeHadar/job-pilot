import unittest

from app.services.fit_score import compute_fit, keyword_gaps, local_score


class FitScoreTest(unittest.TestCase):
    def test_local_score_and_gaps(self):
        resume = "Python FastAPI SQL PostgreSQL AWS testing APIs " * 8
        jd = (
            "Need Kubernetes Go engineer for Python FastAPI microservices "
            "in Tel Aviv Israel"
        )
        score = local_score(resume, "Backend Engineer", "Acme", jd)
        self.assertGreater(score, 0)
        gaps = keyword_gaps(resume, jd)
        self.assertTrue(any(g in gaps for g in ("kubernetes", "microservices", "engineer")))

    def test_rubric_five_dims(self):
        resume = "Backend Engineer Python FastAPI SQL Tel Aviv " * 10
        signals = compute_fit(
            resume,
            "Backend Engineer",
            "Example",
            "Tel Aviv",
            "Python FastAPI SQL role in Tel Aviv Israel. Hybrid.",
            has_llm_key=False,
        )
        self.assertEqual(len(signals.rubric), 5)
        self.assertEqual(signals.rubric_mode, "heuristic")
        self.assertIn("compensation", signals.advisory)


if __name__ == "__main__":
    unittest.main()
