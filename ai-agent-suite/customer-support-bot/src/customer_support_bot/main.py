#!/usr/bin/env python
import sys
from customer_support_bot.crew import CustomerSupportCrew

def run():
    """
    Run the customer support crew, processing a customer query with user-defined input.
    Focus on package tracking if specified by the user.
    """
    # Prompt user for input
    customer_issue = input("Enter the customer's issue: ").strip()
    order_number = input("Enter the order number: ").strip()
    tracking_number = input("Enter the package tracking number: ").strip()
    customer_account = input("Enter the customer account ID: ").strip()
    additional_details = input("Enter any additional details: ").strip()

    # Create the input dictionary
    inputs = {
        "customer_issue": customer_issue,
        "order_number": order_number,
        "tracking_number": tracking_number,  # Track package-related issues
        "customer_account": customer_account,
        "additional_details": additional_details,
    }

    # Initialize and start the CustomerSupportCrew process
    CustomerSupportCrew().crew().kickoff(inputs=inputs)

def train():
    """
    Train the crew for a given number of iterations to improve task handling.
    """
    inputs = {"topic": "Customer Support AI"}
    try:
        CustomerSupportCrew().crew().train(
            n_iterations=int(sys.argv[2]), filename=sys.argv[3], inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task for debugging or review.
    """
    try:
        CustomerSupportCrew().crew().replay(task_id=sys.argv[2])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and return the results for evaluation.
    """
    inputs = {"topic": "Customer Support AI"}
    try:
        CustomerSupportCrew().crew().test(
            n_iterations=int(sys.argv[2]), openai_model_name=sys.argv[3], inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a command: 'run', 'train', 'replay', or 'test'")
        sys.exit(1)

    command = sys.argv[1]
    if command == "run":
        run()
    elif command == "train":
        if len(sys.argv) < 4:
            print("Please provide the number of iterations and filename for training.")
            sys.exit(1)
        train()
    elif command == "replay":
        if len(sys.argv) < 3:
            print("Please provide a task ID for replaying.")
            sys.exit(1)
        replay()
    elif command == "test":
        if len(sys.argv) < 4:
            print("Please provide the number of iterations and model name for testing.")
            sys.exit(1)
        test()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)