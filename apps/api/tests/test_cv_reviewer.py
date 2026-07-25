import unittest

from app.services.cv_reviewer import review_cv


class CvReviewerTest(unittest.TestCase):
    def test_grounded_passes(self):
        baseline = "Built Python FastAPI SQL services and production APIs. " * 5
        content = (
            "# Tailored CV\n\n## Role focus (from JD)\nNeed Python FastAPI\n\n"
            "## Experience & skills (from your baseline resume — edit, do not invent)\n"
            f"{baseline}\n"
        )
        result = review_cv(baseline, content, "Need Python FastAPI in Tel Aviv")
        self.assertTrue(result.ok)
        self.assertEqual(result.issues, [])

    def test_invented_rewritten(self):
        baseline = "Python developer with FastAPI experience. " * 4
        invented = (
            "# Tailored CV\n\n## Role focus (from JD)\nNeed backend\n\n"
            "## Experience & skills (from your baseline resume — edit, do not invent)\n"
            "Led Quantum Blockchain Kubernetes Terraform Ansible "
            "Salesforce Databricks Snowflake Snowflake Snowflake "
            "orchestration platforms worldwide.\n"
        )
        result = review_cv(baseline, invented, "Need backend engineer")
        self.assertFalse(result.ok)
        self.assertTrue(any("invented" in i.lower() or "rewrote" in i.lower() for i in result.issues))
        self.assertIn("baseline resume", result.content_md.lower())
        self.assertNotIn("Quantum", result.content_md)


if __name__ == "__main__":
    unittest.main()
