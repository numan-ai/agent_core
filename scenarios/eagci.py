from environments import CircuitWorld
from src.agent_core import AgentCore
from src.world_model.instance import Instance


def setup(world_type):
    world = world_type()

    agent = AgentCore()
    agent.action_manager.interpreter.global_vars["api"] = world.api
    
    return world, agent


def main():
    world, agent = setup(CircuitWorld)
    
    counter = agent.world_model.add(Instance("CircuitCounter", {
        "value": 0,
    }))
    
    agent.input_processor.send_event(Instance("UserSaidEvent", {
        "sentence": Instance("AchieveGoal", {
            "goal": Instance("GoalMakeLeftEqualToRight", {
                "left": Instance("EntityField", {
                    "entity": counter,
                    "field_name": Instance("String", {
                        "value": "value",
                    }),
                }),
                "right": Instance("Number", {
                    "value": 2,
                }),
            }),
        }),
    }))
    
    agent.run(world=world)


if __name__ == "__main__":
    main()
