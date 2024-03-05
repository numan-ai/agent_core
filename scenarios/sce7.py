from src.agent_core import AgentCore
from src.world_model.instance import Instance
from src.world_model.wm_entities import InstanceReference


def main():
    core = AgentCore()
    
    core.world_model.add(Instance("Button", {
        "input_pin": Instance("Number", {"value": 0}),
    }, instance_id="btn-1"))
    
    core.input_processor.send_event(Instance("UserSaidEvent", {
        "sentence": Instance("LogicOfActionStatement", {
            "action": Instance("ActOnReferencedEntity", {
                "act": Instance("PressAct"),
                "reference": Instance("IndefiniteEntityReference", {
                    "concept": Instance("ButtonClass"),
                }),
            }),
            "result": Instance("SetEntityReferenceProperty", {
                "reference": Instance("ReferenceFromPronoun", {
                    "pronoun": Instance("PronounIt"),
                }),
                "property": Instance("OutputPin"),
                "value": Instance("Number", {"value": 1}),
            }),
        }),
    }))
    
    core.run()
    
    core.input_processor.send_event(Instance("ActOnEntityEvent", {
        "entity": InstanceReference("btn-1"),
        "act": Instance("PressAct"),
    }))
    
    core.run()


if __name__ == "__main__":
    main()
