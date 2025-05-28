from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from adalchemy.tools.custom_tool import URLIngestTool
import os
import pandas as pd

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class Adalchemy():
    """Adalchemy crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools

        # Load the taxonomy files as DataFrames once when the crew is created
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'knowledge')

        audience_tsv_path = os.path.join(base_path, 'Audience Taxonomy 1.1.tsv')
        content_tsv_path = os.path.join(base_path, 'Content Taxonomy 3.1.tsv')

        # Read the TSV files into pandas DataFrames
        self.audience_taxonomy_df = pd.read_csv(audience_tsv_path, sep='\t')
        self.content_taxonomy_df = pd.read_csv(content_tsv_path, sep='\t')

        # Print the dataframes
        print("Audience Taxonomy DataFrame:")
        print(self.audience_taxonomy_df)
        print("\nContent Taxonomy DataFrame:")
        print(self.content_taxonomy_df)

        # Read the taxonomy.csv file and create DF taxonomy_mapping_df
        taxonomy_csv_path = os.path.join(base_path, 'taxonomy.csv')
        if os.path.exists(taxonomy_csv_path):
            self.taxonomy_mapping_df = pd.read_csv(taxonomy_csv_path)
        else:
            self.taxonomy_mapping_df = pd.DataFrame()


    @agent
    def taxonomy_mapper(self) -> Agent:
        return Agent(
            config=self.agents_config['taxonomy_mapper'],  # type: ignore[index]
            verbose=True
        )

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            tools=[URLIngestTool()],
            verbose=True
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'], # type: ignore[index]
            verbose=True
        )
    
    @agent
    def ad_relevance_scorer(self) -> Agent:
        return Agent(
            config=self.agents_config['ad_relevance_scorer'],
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task

    @task
    def taxonomy_mapping_task(self) -> Task:
        # Prepare inputs as CSV strings for passing to the agent
        audience_csv = self.audience_taxonomy_df.to_csv(index=False)
        content_csv = self.content_taxonomy_df.to_csv(index=False)

        # The inputs dictionary keys must match what the agent expects
        inputs = {
            "audience_taxonomy_csv": audience_csv,
            "content_taxonomy_csv": content_csv,
        }

        # This assumes the underlying framework lets you pass inputs to the task
        return Task(
            config=self.tasks_config['taxonomy_mapping_task'],  # type: ignore[index]
            inputs=inputs,
            output_file="taxonomy.csv",
        )

    @task
    def research_task(self) -> Task:
        taxonomy_mapping_csv = self.taxonomy_mapping_df.to_csv(index=False)
        return Task(
            config=self.tasks_config['research_task'],  # type: ignore[index]
            inputs={
                "taxonomy_mapping_csv": taxonomy_mapping_csv
            }
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'], # type: ignore[index]
            output_file='report.md'
        )
    
    @task
    def ad_relevance_scoring_task(self) -> Task:
        # This task depends on the reporting task's output (report.md)
        # We read the report.md and pass it as input context to the scoring agent
        # Then write the full scoring result + best case conclusion to result.md

        report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report.md')
        report_content = ""
        if os.path.exists(report_path):
            with open(report_path, 'r', encoding='utf-8') as f:
                report_content = f.read()

        inputs = {
            "report_content": report_content,
            # You can also pass other campaign criteria or URLs as needed
        }

        return Task(
            config=self.tasks_config['ad_relevance_scoring_task'],
            inputs=inputs,
            output_file='result.md',
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Adalchemy crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
