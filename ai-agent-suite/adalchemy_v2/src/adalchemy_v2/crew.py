# src/adalchemy_v2/crew.py

import sys
import os
import logging
import io
import re
from typing import List, Dict
import pandas as pd

from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, crew, task

# Disable telemetry noise
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from knowledge.audience_segment import SegmentKnowledgeSource
from knowledge.content_segment import ContentSegmentKnowledgeSource
from knowledge.adproduct_segment import AdProductSegmentKnowledgeSource
from adalchemy_v2.tools.custom_tool import URLIngestTool

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@CrewBase
class Adalchemy_v2:
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
            config=self.agents_config["researcher"],
            tools=[URLIngestTool()],
            verbose=True,
        )

    @agent
    def audience_taxonomy_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["audience_taxonomy_agent"],
            knowledge_sources=[self.audience_segment_knowledge],
            verbose=True,
        )

    @agent
    def content_taxonomy_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["content_taxonomy_agent"],
            knowledge_sources=[self.content_segment_knowledge],
            verbose=True,
        )

    @agent
    def adproduct_taxonomy_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["adproduct_taxonomy_agent"],
            knowledge_sources=[self.adproduct_segment_knowledge],
            verbose=True,
        )

    @agent
    def scoring_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["scoring_agent"],
            verbose=True,
        )

    @agent
    def creative_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["creative_agent"],
            verbose=True,
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_task"],
            agent=self.researcher(),
        )

    @task
    def audience_taxonomy_task(self) -> Task:
        return Task(
            config=self.tasks_config["audience_taxonomy_task"],
            agent=self.audience_taxonomy_agent(),
            input=lambda: self.outputs.get("research", ""),
        )

    @task
    def content_taxonomy_task(self) -> Task:
        return Task(
            config=self.tasks_config["content_taxonomy_task"],
            agent=self.content_taxonomy_agent(),
            input=lambda: self.outputs.get("research", ""),
        )

    @task
    def adproduct_taxonomy_task(self) -> Task:
        return Task(
            config=self.tasks_config["adproduct_taxonomy_task"],
            agent=self.adproduct_taxonomy_agent(),
            input=lambda: self.outputs.get("research", ""),
        )

    @task
    def scoring_task(self) -> Task:
        def create_report():
            markdown = "# 🧐 Adalchemy CrewAI Report\n\n"
            markdown += f"**URL**: {self.inputs.get('url')}\n"
            markdown += f"**Topic**: {self.inputs.get('topic')}\n\n"

            if self.outputs.get("research"):
                markdown += "## 🔍 Research Summary\n" + self.outputs["research"] + "\n\n"

            for key in ["audience", "content", "adproduct"]:
                nodes = self.outputs.get(key, [])
                if nodes:
                    markdown += f"## 📂 {key.title()} Taxonomy Suggestions\n```{nodes}\n```\n"

            if self.outputs.get("scoring"):
                markdown += "## 🥮 Taxonomy Scoring & Evaluation\n" + self.outputs["scoring"] + "\n\n"

            if self.outputs.get("creatives"):
                markdown += "## 🌟 Recommended Creatives\n" + self.outputs["creatives"] + "\n\n"

            return markdown

        return Task(
            config=self.tasks_config["scoring_task"],
            agent=self.scoring_agent(),
            input=lambda: {
                "audience": self.outputs.get("audience", []),
                "content": self.outputs.get("content", []),
                "adproduct": self.outputs.get("adproduct", []),
            },
            run=create_report,
            output_file="report.md",
        )

    @task
    def show_creatives_task(self) -> Task:
        def suggest_creatives():
            df = pd.DataFrame(self.outputs.get("scoring_table", []))
            if df.empty:
                return "No taxonomy scoring data available to suggest creatives."

            high_conf = df[df["Confidence Score"] >= 0.8]
            if high_conf.empty:
                return "No high-confidence taxonomy matches available."

            lines = ["### Based on the highest-confidence taxonomy matches:\n"]
            for _, row in high_conf.iterrows():
                tax_type = row.get("Taxonomy Type", "").lower()
                name = row.get("Name", "")
                if tax_type == "audience":
                    lines.append(f"- 🌟 Audience Ad for _{name}_")
                elif tax_type == "content":
                    lines.append(f"- 🖌️ Contextual Ad for _{name}_")
                elif tax_type == "adproduct":
                    lines.append(f"- 💡 Use Ad Product: _{name}_")

            return "\n".join(lines)

        return Task(
            config=self.tasks_config["show_creatives_task"],
            agent=self.creative_agent(),
            input=lambda: self.outputs.get("scoring_table", []),
            run=suggest_creatives,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.researcher(),
                self.audience_taxonomy_agent(),
                self.content_taxonomy_agent(),
                self.adproduct_taxonomy_agent(),
                self.scoring_agent(),
                self.creative_agent(),
            ],
            tasks=[
                self.research_task(),
                self.audience_taxonomy_task(),
                self.content_taxonomy_task(),
                self.adproduct_taxonomy_task(),
                self.scoring_task(),
                self.show_creatives_task(),
            ],
            process=Process.sequential,
            verbose=True,
        )

    def run_and_return_results(self, inputs: Dict) -> Dict[str, str]:
        self.inputs = inputs
        crew = self.crew()
        crew.kickoff(inputs=inputs)

        self.outputs["research"] = self.research_task().output or ""
        self.outputs["audience"] = self.audience_taxonomy_task().output or []
        self.outputs["content"] = self.content_taxonomy_task().output or []
        self.outputs["adproduct"] = self.adproduct_taxonomy_task().output or []
        self.outputs["scoring"] = self.scoring_task().output or ""

        try:
            match = re.search(r"\| Taxonomy Type.+?\|\n((\|.+\n)+)", self.outputs["scoring"])
            if match:
                df = pd.read_csv(io.StringIO(match.group(0)), sep="|", skipinitialspace=True).dropna(axis=1, how='all')
                df.columns = [c.strip() for c in df.columns]
                self.outputs["scoring_table"] = df.to_dict(orient="records")
            else:
                self.outputs["scoring_table"] = []
        except Exception as e:
            logging.warning(f"[SCORING TABLE PARSE FAILED] {e}")
            self.outputs["scoring_table"] = []

        self.outputs["creatives"] = self.show_creatives_task().output or ""

        return {
            "report_path": "report.md",
            "markdown": self.outputs["scoring"],
        }