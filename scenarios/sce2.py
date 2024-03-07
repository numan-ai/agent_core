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
    agent.world_model.add(Instance("CircuitLED", {
        "id": rw_led.id,
    }))
    
    world.api.connect(rw_btn.output_pin, rw_led.input_pin)
    agent.world_model.add(Instance("CircuitWire", {
        "pin_a": rw_btn.output_pin,
        "pin_b": rw_led.input_pin,
    }))
    
    # User: "turn on the led"
    agent.input_processor.send_event(Instance("UserSaidEvent", {
        "sentence": Instance("ActOnReferencedEntityStatement", {
            "reference": Instance("DefiniteEntityReference", {
                "concept": Instance("CircuitLEDClass"),
            }),
            "act": Instance("PutIntoStateAct", {
                "state": Instance("TurnedOnState"),
            }),
        }),
    }))
    
    agent.run(world=world)
    
    # assert world.api.probe_pin(rw_led.input_pin) == 1, "LED is not turned on"


if __name__ == "__main__":
    main()
