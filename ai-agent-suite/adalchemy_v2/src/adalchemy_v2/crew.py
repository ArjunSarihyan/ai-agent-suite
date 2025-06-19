import sys
import os
import logging
from typing import List, Dict
from pathlib import Path

from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, crew, task

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from knowledge.audience_segment import SegmentKnowledgeSource
from knowledge.content_segment import ContentSegmentKnowledgeSource
from knowledge.adproduct_segment import AdProductSegmentKnowledgeSource
from adalchemy_v2.tools.custom_tool import URLIngestTool

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@CrewBase
class Adalchemy_v2():
    agents: List[Agent]
    tasks: List[Task]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        logging.info("[CREW INIT] Loading taxonomy knowledge sources...")
        self.audience_segment_knowledge = SegmentKnowledgeSource()
        self.content_segment_knowledge = ContentSegmentKnowledgeSource()
        self.adproduct_segment_knowledge = AdProductSegmentKnowledgeSource()

        self.audience_segment_knowledge.load_content()
        self.content_segment_knowledge.load_content()
        self.adproduct_segment_knowledge.load_content()

        self.outputs = {}
        self.inputs = {}

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            tools=[URLIngestTool()],
            verbose=True
        )

    @agent
    def audience_taxonomy_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['audience_taxonomy_agent'],
            knowledge_sources=[self.audience_segment_knowledge],
            verbose=True
        )

    @agent
    def content_taxonomy_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['content_taxonomy_agent'],
            knowledge_sources=[self.content_segment_knowledge],
            verbose=True
        )

    @agent
    def adproduct_taxonomy_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['adproduct_taxonomy_agent'],
            knowledge_sources=[self.adproduct_segment_knowledge],
            verbose=True
        )

    @agent
    def scoring_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['scoring_agent'],
            verbose=True
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
            agent=self.researcher(),
        )

    @task
    def audience_taxonomy_task(self) -> Task:
        return Task(
            config=self.tasks_config['audience_taxonomy_task'],
            agent=self.audience_taxonomy_agent(),
            input=lambda: self.outputs.get("research", "")
        )

    @task
    def content_taxonomy_task(self) -> Task:
        return Task(
            config=self.tasks_config['content_taxonomy_task'],
            agent=self.content_taxonomy_agent(),
            input=lambda: self.outputs.get("research", "")
        )

    @task
    def adproduct_taxonomy_task(self) -> Task:
        return Task(
            config=self.tasks_config['adproduct_taxonomy_task'],
            agent=self.adproduct_taxonomy_agent(),
            input=lambda: self.outputs.get("research", "")
        )

    @task
    def scoring_task(self) -> Task:
        def create_report():
            # Compose the full markdown report here, using previous task outputs
            markdown = "# 🧠 Adalchemy CrewAI Report\n\n"
            markdown += f"**URL**: {self.inputs.get('url')}\n\n"
            markdown += f"**Topic**: {self.inputs.get('topic')}\n\n"

            if self.outputs.get("research"):
                markdown += "## 🔍 Research Summary\n"
                markdown += self.outputs["research"] + "\n\n"

            if self.outputs.get("audience"):
                markdown += "## 🎯 Audience Taxonomy Suggestions\n"
                markdown += self.outputs["audience"] + "\n\n"

            if self.outputs.get("content"):
                markdown += "## 📚 Content Taxonomy Suggestions\n"
                markdown += self.outputs["content"] + "\n\n"

            if self.outputs.get("adproduct"):
                markdown += "## 💼 Ad Product Taxonomy Suggestions\n"
                markdown += self.outputs["adproduct"] + "\n\n"

            # The actual scoring agent output
            if self.outputs.get("scoring"):
                markdown += "## 🧮 Taxonomy Scoring & Evaluation\n"
                markdown += self.outputs["scoring"] + "\n\n"

            return markdown

        # Use this Task to run scoring agent and generate the final report
        return Task(
            config=self.tasks_config['scoring_task'],
            agent=self.scoring_agent(),
            input=lambda: {
                "audience": self.outputs.get("audience", []),
                "content": self.outputs.get("content", []),
                "adproduct": self.outputs.get("adproduct", [])
            },
            run=create_report,
            output_file="report.md"  # This will auto-save the report markdown
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.researcher(),
                self.audience_taxonomy_agent(),
                self.content_taxonomy_agent(),
                self.adproduct_taxonomy_agent(),
                self.scoring_agent()
            ],
            tasks=[
                self.research_task(),
                self.audience_taxonomy_task(),
                self.content_taxonomy_task(),
                self.adproduct_taxonomy_task(),
                self.scoring_task()
            ],
            verbose=True,
            process=Process.sequential
        )

    def run_and_return_results(self, inputs: Dict) -> Dict[str, str]:
        self.inputs = inputs  # Save inputs to use in report generation
        crew = self.crew()
        crew.kickoff(inputs=inputs)

        # Collect outputs
        self.outputs["research"] = self.research_task().output
        self.outputs["audience"] = self.audience_taxonomy_task().output
        self.outputs["content"] = self.content_taxonomy_task().output
        self.outputs["adproduct"] = self.adproduct_taxonomy_task().output
        self.outputs["scoring"] = self.scoring_task().output

        # report.md is auto-generated by scoring_task via output_file param
        return {
            "report_path": "report.md",
            "markdown": self.outputs["scoring"]  # the markdown report string
        }
