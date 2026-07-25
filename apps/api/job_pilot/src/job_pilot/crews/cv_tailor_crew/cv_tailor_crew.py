from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class CvTailorCrew:
    """Tailor baseline resume to a job description."""

    agents: list[BaseAgent]
    tasks: list[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def tailor(self) -> Agent:
        return Agent(config=self.agents_config["tailor"])  # type: ignore[index]

    @agent
    def editor(self) -> Agent:
        return Agent(config=self.agents_config["editor"])  # type: ignore[index]

    @task
    def tailor_task(self) -> Task:
        return Task(config=self.tasks_config["tailor_task"])  # type: ignore[index]

    @task
    def edit_task(self) -> Task:
        return Task(config=self.tasks_config["edit_task"])  # type: ignore[index]

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
