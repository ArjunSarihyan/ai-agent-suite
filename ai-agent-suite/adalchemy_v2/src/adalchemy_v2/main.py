#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from adalchemy_v2.crew import Adalchemy_v2

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    url = "https://sports.yahoo.com/nba/breaking-news/live/pacers-vs-thunder-score-okc-dominates-nba-finals-game-2-behind-big-game-from-shai-gilgeous-alexander-as-tyrese-haliburton-fades-223020825.html"
    topic =  "Achieve a 20% growth in unique audience reach during Q2 by strategically targeting and optimizing content across diverse, high-intent audience segments — including key purchase intent categories."
    inputs = {
        "url": url,
        "topic": topic,
        "current_year": str(datetime.now().year)
    }
    try:
        Adalchemy_v2().crew().kickoff(inputs=inputs)
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
        Adalchemy_v2().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Adalchemy_v2().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    
    try:
        Adalchemy_v2().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")