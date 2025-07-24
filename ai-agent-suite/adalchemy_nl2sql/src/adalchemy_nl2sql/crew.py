from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent  # for v0.148
from typing import List

from adalchemy_nl2sql.tools.custom_tool import nl2sql_tool  # ✅ updated import


@CrewBase
class AdalchemyNl2Sql():
    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def nl2sql_agent(self) -> BaseAgent:
        # Create the agent with the nl2sql_tool attached
        return Agent(
            config=self.agents_config['nl2sql_agent'],  # type: ignore[index]
            tools=[nl2sql_tool],
            verbose=True
        )

    @task
    def sql_query_task(self) -> Task:
        return Task(
            config=self.tasks_config['sql_query_task'],  # type: ignore[index]
            run=self._run_sql_query_task,
            expected_output="A set of syntactically correct SQL SELECT queries for each of the three taxonomy tables: adproduct, audience, and content."
        )

    def _run_sql_query_task(self, input_text: str) -> str:
        agent = self.nl2sql_agent()
        sql_query = agent.run(input_text)
        tool_result = nl2sql_tool.run(sql_query)
        return tool_result

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )