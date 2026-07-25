from pydantic import BaseModel

from crewai.flow import Flow, listen, start

from job_pilot.crews.cv_tailor_crew.cv_tailor_crew import CvTailorCrew
from job_pilot.crews.match_crew.match_crew import MatchCrew


class JobPilotState(BaseModel):
    """Shared Flow state for MVP loops (ADR 0006b / 0008)."""

    mode: str = "match"  # onboard | match | tailor
    resume_text: str = ""
    seeker_profile: str = ""
    job_description: str = ""
    job_title: str = ""
    company: str = ""
    jobs_json: str = "[]"
    match_report: str = ""
    tailored_cv: str = ""
    notes: str = ""


class JobPilotFlow(Flow[JobPilotState]):
    """
    Flow entrypoints:
    - mode=match  → score jobs vs Memory/resume
    - mode=tailor → produce tailored CV from JD + resume
    """

    @start()
    def prepare(self, crewai_trigger_payload: dict | None = None):
        payload = crewai_trigger_payload or {}
        self.state.mode = payload.get("mode", self.state.mode)
        self.state.resume_text = payload.get("resume_text", self.state.resume_text)
        self.state.seeker_profile = payload.get(
            "seeker_profile", self.state.seeker_profile
        )
        self.state.job_description = payload.get(
            "job_description", self.state.job_description
        )
        self.state.job_title = payload.get("job_title", self.state.job_title)
        self.state.company = payload.get("company", self.state.company)
        self.state.jobs_json = payload.get("jobs_json", self.state.jobs_json)
        self.state.notes = payload.get("notes", self.state.notes)

    @listen(prepare)
    def run_pipeline(self):
        if self.state.mode == "tailor":
            result = (
                CvTailorCrew()
                .crew()
                .kickoff(
                    inputs={
                        "resume_text": self.state.resume_text,
                        "seeker_profile": self.state.seeker_profile,
                        "job_description": self.state.job_description,
                        "job_title": self.state.job_title,
                        "company": self.state.company,
                    }
                )
            )
            self.state.tailored_cv = result.raw
            return

        # Default: match / rank
        result = (
            MatchCrew()
            .crew()
            .kickoff(
                inputs={
                    "resume_text": self.state.resume_text,
                    "seeker_profile": self.state.seeker_profile,
                    "jobs_json": self.state.jobs_json,
                }
            )
        )
        self.state.match_report = result.raw


def kickoff():
    JobPilotFlow().kickoff()


def plot():
    JobPilotFlow().plot()


def run_with_trigger():
    import json
    import sys

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided.")
    trigger_payload = json.loads(sys.argv[1])
    flow = JobPilotFlow()
    return flow.kickoff({"crewai_trigger_payload": trigger_payload})


def run_flow(payload: dict) -> JobPilotState:
    """Programmatic entry for FastAPI."""
    flow = JobPilotFlow()
    flow.kickoff({"crewai_trigger_payload": payload})
    return flow.state


if __name__ == "__main__":
    kickoff()
