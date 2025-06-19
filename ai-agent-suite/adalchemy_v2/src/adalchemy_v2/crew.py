# crew.py

import sys
import os
import logging
import pandas as pd
from typing import List, Dict
from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

# Visualization
try:
    from tabulate import tabulate
except ImportError:
    def tabulate(df, headers='keys', tablefmt='github'):
        return df.to_markdown()

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from knowledge.audience_segment import SegmentKnowledgeSource
from knowledge.content_segment import ContentSegmentKnowledgeSource
from knowledge.adproduct_segment import AdProductSegmentKnowledgeSource
from adalchemy_v2.tools.custom_tool import URLIngestTool

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TSV_DIR = r"C:\Users\User\OneDrive\Desktop\HyperMindz\ai-agent-suite\ai-agent-suite\adalchemy_v2"
AUDIENCE_TSV = os.path.join(TSV_DIR, "Audience Taxonomy 1.1.tsv")
CONTENT_TSV = os.path.join(TSV_DIR, "Content Taxonomy 3.1.tsv")
ADPRODUCT_TSV = os.path.join(TSV_DIR, "Ad Product Taxonomy 2.0.tsv")

def load_tsv_as_dict_list(tsv_path: str) -> List[Dict]:
    try:
        df = pd.read_csv(tsv_path, sep="\t", dtype=str).fillna("")
        return df.to_dict(orient="records")
    except Exception as e:
        logging.error(f"Error loading TSV {tsv_path}: {e}")
        return []

def filter_exact_matches(row, audience_tsv_df, content_tsv_df, adproduct_tsv_df) -> bool:
    unique_id = str(row['Unique ID']).strip()
    name = str(row['Name']).strip()

    if row['Taxonomy Type'] == 'Audience':
        df = audience_tsv_df
    elif row['Taxonomy Type'] == 'Content':
        df = content_tsv_df
    elif row['Taxonomy Type'] == 'Ad Product':
        df = adproduct_tsv_df
    else:
        return False

    match = df[(df['Unique ID'].astype(str).str.strip() == unique_id) &
               (df['Name'].astype(str).str.strip() == name)]

    return not match.empty

@CrewBase
class Adalchemy_v2():
    agents: List[BaseAgent]
    tasks: List[Task]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        logging.info("[CREW INIT] Loading taxonomy knowledge sources and TSVs...")
        self.audience_segment_knowledge = SegmentKnowledgeSource()
        self.content_segment_knowledge = ContentSegmentKnowledgeSource()
        self.adproduct_segment_knowledge = AdProductSegmentKnowledgeSource()

        self.audience_segment_knowledge.load_content()
        self.content_segment_knowledge.load_content()
        self.adproduct_segment_knowledge.load_content()

        self.audience_tsv_data = load_tsv_as_dict_list(AUDIENCE_TSV)
        self.content_tsv_data = load_tsv_as_dict_list(CONTENT_TSV)
        self.adproduct_tsv_data = load_tsv_as_dict_list(ADPRODUCT_TSV)

        self.audience_df = pd.DataFrame()
        self.content_df = pd.DataFrame()
        self.adproduct_df = pd.DataFrame()

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
            agent=self.researcher()
        )

    @task
    def audience_taxonomy_task(self) -> Task:
        def run_task():
            result = self.audience_taxonomy_agent().run(self.research_task().output)
            new_df = pd.DataFrame(result)
            if not new_df.empty:
                new_df['Taxonomy Type'] = 'Audience'
                self.audience_df = pd.concat([self.audience_df, new_df], ignore_index=True)
                self.audience_df.drop_duplicates(subset=["Unique ID", "Taxonomy Type"], inplace=True)
            return result
        return Task(
            config=self.tasks_config['audience_taxonomy_task'],
            agent=self.audience_taxonomy_agent(),
            input=lambda: self.research_task().output,
            run=run_task
        )

    @task
    def content_taxonomy_task(self) -> Task:
        def run_task():
            result = self.content_taxonomy_agent().run(self.research_task().output)
            new_df = pd.DataFrame(result)
            if not new_df.empty:
                new_df['Taxonomy Type'] = 'Content'
                self.content_df = pd.concat([self.content_df, new_df], ignore_index=True)
                self.content_df.drop_duplicates(subset=["Unique ID", "Taxonomy Type"], inplace=True)
            return result
        return Task(
            config=self.tasks_config['content_taxonomy_task'],
            agent=self.content_taxonomy_agent(),
            input=lambda: self.research_task().output,
            run=run_task
        )

    @task
    def adproduct_taxonomy_task(self) -> Task:
        def run_task():
            result = self.adproduct_taxonomy_agent().run(self.research_task().output)
            new_df = pd.DataFrame(result)
            if not new_df.empty:
                new_df['Taxonomy Type'] = 'Ad Product'
                self.adproduct_df = pd.concat([self.adproduct_df, new_df], ignore_index=True)
                self.adproduct_df.drop_duplicates(subset=["Unique ID", "Taxonomy Type"], inplace=True)
            return result
        return Task(
            config=self.tasks_config['adproduct_taxonomy_task'],
            agent=self.adproduct_taxonomy_agent(),
            input=lambda: self.research_task().output,
            run=run_task
        )

    @task
    def scoring_task(self) -> Task:
        def combined_input():
            combined_df = pd.concat(
                [self.audience_df, self.content_df, self.adproduct_df],
                ignore_index=True
            )
            combined_df.drop_duplicates(subset=["Unique ID", "Taxonomy Type"], inplace=True)

            audience_tsv_df = pd.DataFrame(self.audience_tsv_data)
            content_tsv_df = pd.DataFrame(self.content_tsv_data)
            adproduct_tsv_df = pd.DataFrame(self.adproduct_tsv_data)

            filtered_df = combined_df[combined_df.apply(
                lambda row: filter_exact_matches(row, audience_tsv_df, content_tsv_df, adproduct_tsv_df),
                axis=1
            )].copy()

            return filtered_df.to_dict(orient="records")

        return Task(
            config=self.tasks_config['scoring_task'],
            agent=self.scoring_agent(),
            input=combined_input
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

    # ✅ New method for Streamlit
    def run_and_return_results(self, inputs: Dict) -> pd.DataFrame:
        self.crew().kickoff(inputs=inputs)

        combined_df = pd.concat(
            [self.audience_df, self.content_df, self.adproduct_df],
            ignore_index=True
        )
        combined_df.drop_duplicates(subset=["Unique ID", "Taxonomy Type"], inplace=True)

        audience_tsv_df = pd.DataFrame(self.audience_tsv_data)
        content_tsv_df = pd.DataFrame(self.content_tsv_data)
        adproduct_tsv_df = pd.DataFrame(self.adproduct_tsv_data)

        filtered_df = combined_df[combined_df.apply(
            lambda row: filter_exact_matches(row, audience_tsv_df, content_tsv_df, adproduct_tsv_df),
            axis=1
        )].copy()

        return filtered_df
