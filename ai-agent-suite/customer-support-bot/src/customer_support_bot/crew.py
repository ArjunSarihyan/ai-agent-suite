from crewai_tools import ScrapeWebsiteTool, SerperDevTool  # You may include more tools as needed.
from pydantic import BaseModel
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


class ChatResponse(BaseModel):
    response_text: str
    follow_up_actions: str


@CrewBase
class CustomerSupportCrew:
    """Customer support crew that handles customer issues, suggests solutions, and crafts responses"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def customer_support_researcher(self) -> Agent:
        """Agent that gathers detailed information about the customer's issue, specifically focusing on package tracking."""
        return Agent(
            config=self.agents_config["customer_support_researcher"],
            tools=[ScrapeWebsiteTool(), SerperDevTool()],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def package_tracker(self) -> Agent:
        """Agent that focuses specifically on tracking packages and resolving related issues."""
        return Agent(
            config=self.agents_config["package_tracker"],
            tools=[],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def solution_suggester(self) -> Agent:
        """Agent that suggests solutions based on the customer's problem, focusing on package-related solutions."""
        return Agent(
            config=self.agents_config["solution_suggester"],
            tools=[],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def chat_copywriter(self) -> Agent:
        """Agent that crafts clear and empathetic responses for the customer."""
        return Agent(
            config=self.agents_config["chat_copywriter"],
            tools=[],
            allow_delegation=False,
            verbose=True,
        )

    @task
    def customer_support_research_task(self) -> Task:
        """Task that gathers necessary information about the customer’s issue"""
        return Task(
            config=self.tasks_config["customer_support_research_task"],
            agent=self.customer_support_researcher(),
        )

    @task
    def package_tracking_task(self) -> Task:
        """Task focused on resolving package tracking issues, e.g., tracking number, delivery status, etc."""
        return Task(
            config=self.tasks_config["package_tracking_task"],
            agent=self.package_tracker(),
        )

    @task
    def solution_suggestion_task(self) -> Task:
        """Task that analyzes the details and suggests a solution"""
        return Task(
            config=self.tasks_config["solution_suggestion_task"],
            agent=self.solution_suggester(),
        )

    @task
    def craft_chat_response_task(self) -> Task:
        """Task that crafts a clear, polite, and helpful response for the customer"""
        return Task(
            config=self.tasks_config["craft_chat_response_task"],
            agent=self.chat_copywriter(),
            output_json=ChatResponse,
            output_file="chat_response.md",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the CustomerSupportCrew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,  # Define the process flow
            verbose=True,
        )