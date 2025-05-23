#!/usr/bin/env python
# src/project/main.py

import sys
import warnings
from datetime import datetime
from publisher.crew import Publisher

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Function to run the crew
def run():
    """
    Run the crew.
    """
    inputs = {
        'topic': 'Duke Energy',  # Define your topic here
        'current_year': str(datetime.now().year)  # Get the current year dynamically
    }
    
    try:
        Publisher(topic=inputs['topic']).crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

# Function to train the crew for a given number of iterations
def train():
    """
    Train the crew for 3 iterations using summaries.md.
    """
    inputs = {
        "topic": "Duke Energy"  # Define your topic here
    }
    try:
        # Use 3 iterations and summaries.md explicitly as the training file
        Publisher(topic=inputs['topic']).crew().train(n_iterations=3, filename='summaries.md', inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

# Function to replay a specific task in the crew
def replay():
    """
    Replay the crew execution from a specific task.
    """
    inputs = {
        "topic": "Duke Energy"
    }
    try:
        Publisher(topic=inputs['topic']).crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

# Function to test the crew execution
def test():
    """
    Test the crew execution for 3 iterations using summaries.md.
    """
    inputs = {
        "topic": "Duke Energy",
        "current_year": str(datetime.now().year)  # Get the current year dynamically
    }
    try:
        # Use 3 iterations and the openai_model_name passed from command line, and summaries.md implicitly
        Publisher(topic=inputs['topic']).crew().test(n_iterations=3, openai_model_name=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")