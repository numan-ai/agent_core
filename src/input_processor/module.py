from src.base_module import AgentModule
from src.world_model import Instance


class InputProcessor(AgentModule):
    started = False
    
    def step(self):
        if self.started == 2:
            return
        self.started += 1
        
        parsed_sentence = Instance("UserSaidImperative", {
            "act": Instance("ActOnEntity", {
                "act": Instance("PrintAct"),
                "entity": Instance("BinaryMathExpression", {
                    "left": Instance("Number", {"value": self.started}),
                    "op": Instance("PlusSign"),
                    "right": Instance("Number", {"value": 2}),
                })
            })
        })
        
        event = Instance("UserSaidEvent", {
            "sentence": parsed_sentence
        })
        
        self.core.decision_maker.on_event(event)
