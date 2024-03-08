""" Agent Core
Modules:
- input_processor
    Takes in raw input and processes it into a format that the agent can understand.
    Processed data is then sent to the decision maker.
- decision_maker
    Takes in processed data and builds a plan of action.
    The plan is then sent to the action manager.
- action_manager
    Takes in a plan of action and executes it.
- world_model
    Stores the agent's knowledge of the world.
    Knowledge is a graph of instances and their fields
- knowledge_base
    Stores the agent's conceptual knowledge of the world.
    Conceptual knowledge is a graph of concepts and their fields
- unified_graph
    Provides a unified graph interface to the world model,
        knowledge base and the Agent Code graphs.
"""