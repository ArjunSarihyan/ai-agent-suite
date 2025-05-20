# src/publisher/crew.py

import datetime
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import yaml

@CrewBase
class Publisher():
    """Publisher crew"""

    agents_config_path = 'src/publisher/config/agents.yaml'
    tasks_config_path = 'src/publisher/config/tasks.yaml'

    def __init__(self, topic: str):
        self.topic = topic
        self.current_year = datetime.datetime.now().year

        # Load and format YAML config files
        with open(self.agents_config_path, 'r') as f:
            raw_agents = yaml.safe_load(f)
            self.agents_config = {
                k: {kk: vv.format(topic=topic) for kk, vv in v.items()}
                for k, v in raw_agents.items()
            }

        with open(self.tasks_config_path, 'r') as f:
            raw_tasks = yaml.safe_load(f)
            self.tasks_config = {
                k: {kk: vv.format(topic=topic, current_year=self.current_year) for kk, vv in v.items()}
                for k, v in raw_tasks.items()
            }

    # Agents
    @agent
    def crawler_agent(self) -> Agent:
        return Agent(config=self.agents_config['crawler_agent'], verbose=True)

    @agent
    def role_generator(self) -> Agent:
        return Agent(config=self.agents_config['role_generator'], verbose=True)

    @agent
    def simulation_agent(self) -> Agent:
        return Agent(config=self.agents_config['simulation_agent'], verbose=True)

    @agent
    def summarization_agent(self) -> Agent:
        return Agent(config=self.agents_config['summarization_agent'], verbose=True)

    # Tasks
    @task
    def crawler_task(self) -> Task:
        return Task(config=self.tasks_config['crawler_task'])

    @task
    def role_generation_task(self) -> Task:
        return Task(config=self.tasks_config['role_generation_task'])

    @task
    def simulation_task(self) -> Task:
        return Task(config=self.tasks_config['simulation_task'])

    @task
    def summarization_task(self) -> Task:
        return Task(config=self.tasks_config['summarization_task'], output_file='summaries.md')

    # Crew definition
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
