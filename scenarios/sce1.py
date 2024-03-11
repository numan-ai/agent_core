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
    
    rw_btn = world.api.create("Button")
    agent.world_model.add(Instance("CircuitButton", {
        "id": rw_btn.id,
    }))
    
    # User: "press the button"
    agent.input_processor.send_event(Instance("UserSaidEvent", {
        "sentence": Instance("ActOnReferencedEntityStatement", {
            "reference": Instance("DefiniteEntityReference", {
                "concept": Instance("CircuitButtonClass"),
            }),
            "act": Instance("PressAct"),
        }),
    }))
    
    # don't pass the world, so that the button does not become unpressed
    agent.run(world=None)
    
    assert world.api.probe_pin(rw_btn.output_pin_id) == 1, "Button was not pressed"


if __name__ == "__main__":
    main()
