from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class MatchCrew:
    """Rank Israel-scoped jobs against seeker Memory/resume."""

    agents: list[BaseAgent]
    tasks: list[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def matcher(self) -> Agent:
        return Agent(config=self.agents_config["matcher"])  # type: ignore[index]

    @agent
    def critic(self) -> Agent:
        return Agent(config=self.agents_config["critic"])  # type: ignore[index]

    @task
    def match_task(self) -> Task:
        return Task(config=self.tasks_config["match_task"])  # type: ignore[index]

    @task
    def critique_task(self) -> Task:
        return Task(config=self.tasks_config["critique_task"])  # type: ignore[index]

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
