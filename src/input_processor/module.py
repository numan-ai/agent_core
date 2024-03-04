from src.base_module import AgentModule
from src.world_model import Instance


class InputProcessor(AgentModule):
    started = False
    
    def __init__(self, core) -> None:
        super().__init__(core)

    def send_event(self, event: Instance):
        self.core.decision_maker.on_event(event)
    
    def step(self):
        if self.started == 1:
            return
        self.started += 1
        
        # parsed_sentence = Instance("UserSaidImperative", {
        #     "act": Instance("ActOnEntity", {
        #         "act": Instance("PrintAct"),
        #         "entity": Instance("BinaryMathExpression", {
        #             "left": Instance("Number", {"value": self.started}),
        #             "op": Instance("PlusSign"),
        #             "right": Instance("Number", {"value": 2}),
        #         })
        #     })
        # })
        
        # parsed_sentence = Instance("IsAStatement", {
        #     "left": Instance("LED"),
        #     "right": Instance("LightSource"),
        # })
        
        # parsed_sentence = Instance("IsQuestionStatement", {
        #     "expression": Instance("BinaryMathExpression", {
        #         "left": Instance("Number", {"value": 12}),
        #         "op": Instance("LessThan"),
        #         "right": Instance("Number", {"value": 3}),
        #     }),
        # })
        
        # parsed_sentence = Instance("IsQuestionStatement", {
        #     "expression": Instance("BinaryMathExpression", {
        #         "left": Instance("Number", {"value": 12}),
        #         "op": Instance("GreaterThan"),
        #         "right": Instance("Number", {"value": 3}),
        #     }),
        # })
        
        # parsed_sentence = Instance("IsEntityInStateStatement", {
        #     "entity": Instance("LED", {
        #         "input_pin": Instance("Number", {"value": 1}),
        #     }),
        #     "state": Instance("StateTurnedOn"),
        # })
        
        # event = Instance("UserSaidEvent", {
        #     "sentence": parsed_sentence
        # })
        
        # self.core.decision_maker.on_event(event)
