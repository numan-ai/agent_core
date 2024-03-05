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
    
    rw_btn = world.api.create("Switch")
    agent.world_model.add(Instance("CircuitSwitch", {
        "id": rw_btn.id,
    }))
    
    rw_led = world.api.create("LED")
    agent.world_model.add(Instance("LED", {
        "id": rw_led.id,
    }))
    
    # User: "turn on the led"
    agent.input_processor.send_event(Instance("UserSaidEvent", {
        "sentence": Instance("ActOnReferencedEntityStatement", {
            "reference": Instance("DefiniteEntityReference", {
                "concept": Instance("LEDClass"),
            }),
            "act": Instance("TurnOnAct"),
        }),
    }))
    
    agent.run(world=world)
    
    assert world.api.probe_pin(rw_led.input_pin) == 1, "LED is not turned on"


if __name__ == "__main__":
    main()
