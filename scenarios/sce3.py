from src.agent_core import AgentCore
from src.world_model.instance import Instance
from src.world_model.wm_entities import InstanceReference


def main():
    core = AgentCore()
    
    btn = core.world_model.add(Instance("Button", {
        "output_pin": Instance("Number", {"value": 0}),
    }, instance_id="btn-1"))
    
    core.input_processor.send_event(Instance("ActOnEntityEvent", {
        "entity": InstanceReference("btn-1"),
        "act": Instance("PressAct"),
    }))
    
    core.run()
    
    assert btn.fields.output_pin.fields.value == 1


if __name__ == "__main__":
    main()
