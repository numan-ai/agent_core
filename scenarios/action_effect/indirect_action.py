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
    wm_btn = agent.world_model.add(Instance("CircuitSwitch", {
        "id": rw_btn.id,
        "output_pin": Instance("CircuitPin", {
            "value": 0,
            "id": Instance("Number", {
                "value": rw_btn.output_pin_id,
            }),
        })
    }))
    
    rw_led = world.api.create("LED")
    wm_led = agent.world_model.add(Instance("CircuitLED", {
        "id": rw_led.id,
        "input_pin": Instance("CircuitPin", {
            "value": 0,
            "id": Instance("Number", {
                "value": rw_led.input_pin_id,
            }),
        })
    }))
    
    world.api.connect(rw_btn.output_pin_id, rw_led.input_pin_id)
    agent.world_model.add(Instance("CircuitWire", {
        "pin_a": wm_btn.fields.output_pin,
        "pin_b": rw_led.fields.input_pin,
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
    
    # assert world.api.probe_pin(rw_led.input_pin_id) == 1, "LED is not turned on"


if __name__ == "__main__":
    main()
