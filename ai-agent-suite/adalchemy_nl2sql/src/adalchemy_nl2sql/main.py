#!/usr/bin/env python
import sys
import warnings
from datetime import datetime

from adalchemy_nl2sql.crew import AdalchemyNl2Sql  # ✅ updated path

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the crew.
    """
    inputs = {
        'topic': 'Target users aged between 18-24, 25-34, and 35-44 who are interested in Basketball and College Basketball, have shown purchase intent for Basketball Equipment, and engage in Sports Betting or Virtual Betting, to increase sales of basketball-related sporting goods.',
        'current_year': str(datetime.now().year)
    }

    try:
        AdalchemyNl2Sql().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        AdalchemyNl2Sql().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        AdalchemyNl2Sql().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and return the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }

    try:
        AdalchemyNl2Sql().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")