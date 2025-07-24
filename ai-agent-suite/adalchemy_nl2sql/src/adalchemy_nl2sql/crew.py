from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

from adalchemy_nl2sql.tools.custom_tool import nl2sql_tool
from adalchemy_nl2sql.tools.semantic_expansion import get_top_k_similar_phrases, log_debug

@CrewBase
class AdalchemyNl2Sql():
    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def researcher_agent(self) -> BaseAgent:
        return Agent(
            config=self.agents_config['researcher_agent'],  # type: ignore
            verbose=True
        )

    @agent
    def semantic_agent(self) -> BaseAgent:
        return Agent(
            config=self.agents_config['semantic_agent'],  # type: ignore
            verbose=True
        )

    @agent
    def nl2sql_agent(self) -> BaseAgent:
        return Agent(
            config=self.agents_config['nl2sql_agent'],  # type: ignore
            tools=[nl2sql_tool],
            verbose=True
        )

    @task
    def researcher_task(self) -> Task:
        return Task(
            config=self.tasks_config['researcher_task'],  # type: ignore
            run=lambda topic: self.researcher_agent().run(topic),
            expected_output="A comma-separated list of core, relevant keywords extracted from the user topic."
        )

    @task
    def semantic_task(self) -> Task:
        return Task(
            config=self.tasks_config['semantic_task'],  # type: ignore
            run=self._run_semantic_task,
            expected_output="A comma-separated list of semantically expanded keywords suitable for taxonomy querying."
        )

    def _run_semantic_task(self, input_keywords: str) -> str:
        keywords = [kw.strip() for kw in input_keywords.split(',') if kw.strip()]
        log_debug(f"🔍 Input Keywords from Researcher Agent: {keywords}")

        results = get_top_k_similar_phrases(keywords, top_k=3)
        log_debug("🔗 Semantic Matches:\n" + "\n".join(
            f"{kw}: {[match['text'] for match in matches]}" for kw, matches in results.items()
        ))

        expanded_keywords = {entry["text"].strip() for matches in results.values() for entry in matches}
        final_keywords = ", ".join(expanded_keywords)
        log_debug(f"✅ Final Expanded Keywords passed to NL2SQL Agent: {final_keywords}")

        return final_keywords

    @task
    def sql_query_task(self) -> Task:
        return Task(
            config=self.tasks_config['sql_query_task'],  # type: ignore
            run=lambda keywords: self.nl2sql_agent().run(keywords),
            expected_output="Syntactically correct SQL SELECT queries for each taxonomy table."
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )