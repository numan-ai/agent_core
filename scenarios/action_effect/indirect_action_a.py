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
    
    # User: "set the switch to on"
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
