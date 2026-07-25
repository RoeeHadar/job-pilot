# Job Pilot CrewAI package

CrewAI Flow and crews used by the FastAPI application:

- `MatchCrew`: ranks Israel-market roles against resume-backed Memory.
- `CvTailorCrew`: tailors a CV to a JD without inventing experience.
- `JobPilotFlow`: routes match and tailor runs.

Install from `apps/api`:

```powershell
.\.venv\Scripts\pip install -e .\job_pilot
```

Provider keys are read from the local, ignored `.env` file. See the repository
root `README.md` for full setup and tests.
