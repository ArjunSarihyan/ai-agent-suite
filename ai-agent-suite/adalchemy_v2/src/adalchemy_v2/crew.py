import sys
import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import logging

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# Import segment knowledge sources
from knowledge.audience_segment import SegmentKnowledgeSource
from knowledge.content_segment import ContentSegmentKnowledgeSource
from knowledge.adproduct_segment import AdProductSegmentKnowledgeSource

# Import custom tool
from adalchemy_v2.tools.custom_tool import URLIngestTool

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@CrewBase
class Adalchemy_v2():
    """Adalchemy_v2 crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize and load the segment knowledge sources
        logging.info("[CREW INIT] Chunking audience taxonomy...")
        self.audience_segment_knowledge = SegmentKnowledgeSource()
        self.audience_segment_knowledge.load_content()

        logging.info("[CREW INIT] Chunking content taxonomy...")
        self.content_segment_knowledge = ContentSegmentKnowledgeSource()
        self.content_segment_knowledge.load_content()

        logging.info("[CREW INIT] Chunking ad product taxonomy...")
        self.adproduct_segment_knowledge = AdProductSegmentKnowledgeSource()
        self.adproduct_segment_knowledge.load_content()

    @agent
    def manager(self) -> Agent:
        """Custom manager agent controlling delegation and workflow"""
        return Agent(
            role="Project Manager",
            goal="Efficiently manage the crew and ensure high-quality task completion",
            backstory="Experienced project manager skilled in overseeing complex projects and guiding teams to success.",
            allow_delegation=True,  # Enable task delegation by manager
            verbose=True
        )

    def delegate_work_example(self, delegate_tool):
        coworker = "Audience Taxonomy Specialist"
        task = "Analyze the research output and map it accurately to audience taxonomy nodes."
        context = (
            "The research output includes detailed audience segments, their demographics, "
            "behaviors, and relevance for targeted marketing campaigns."
        )
        delegate_tool(coworker=coworker, task=task, context=context)

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],  # type: ignore[index]
            tools=[URLIngestTool()],
            verbose=True
        )

    @agent
    def audience_taxonomy_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['audience_taxonomy_agent'],  # type: ignore[index]
            knowledge_sources=[self.audience_segment_knowledge],
            verbose=True
        )

    @agent
    def content_taxonomy_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['content_taxonomy_agent'],  # type: ignore[index]
            knowledge_sources=[self.content_segment_knowledge],
            verbose=True
        )

    @agent
    def adproduct_taxonomy_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['adproduct_taxonomy_agent'],  # type: ignore[index]
            knowledge_sources=[self.adproduct_segment_knowledge],
            verbose=True
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],  # type: ignore[index]
            agent=self.researcher()
        )

    @task
    def audience_taxonomy_task(self) -> Task:
        return Task(
            config=self.tasks_config['audience_taxonomy_task'],  # type: ignore[index]
            agent=self.audience_taxonomy_agent(),
            input=lambda: self.research_task().output  # Use research_task output as input
        )

    @task
    def content_taxonomy_task(self) -> Task:
        return Task(
            config=self.tasks_config['content_taxonomy_task'],  # type: ignore[index]
            agent=self.content_taxonomy_agent(),
            input=lambda: self.research_task().output  # Use research_task output as input
        )

    @task
    def adproduct_taxonomy_task(self) -> Task:
        return Task(
            config=self.tasks_config['adproduct_taxonomy_task'],  # type: ignore[index]
            agent=self.adproduct_taxonomy_agent(),
            input=lambda: self.research_task().output  # Use research_task output as input
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Adalchemy_v2 crew with hierarchical process, a manager, and tasks."""

        # List all your agents except the manager here explicitly
        agents_list = [
            self.researcher(),
            self.audience_taxonomy_agent(),
            self.content_taxonomy_agent(),
            self.adproduct_taxonomy_agent()
        ]

        return Crew(
            agents=agents_list,  # manager NOT included here
            tasks=[
                self.research_task(),
                self.audience_taxonomy_task(),
                self.content_taxonomy_task(),
                self.adproduct_taxonomy_task()
            ],
            process=Process.hierarchical,
            manager_agent=self.manager(),  # manager passed separately
            planning=True,
            verbose=True
        )
