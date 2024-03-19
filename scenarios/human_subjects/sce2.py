import random

from environments.circuits.world import CircuitWorld
from scenarios.human_subjects.base_scenario import Scenario

    
class Scenario1(Scenario):
    def setup(self):
        self.switches = [
            self.api.create("Switch")
            for _ in range(2)
        ]
        self.led = self.api.create("LED")
        self.not_gate = self.api.create("NotGate")
        self.or_gate = self.api.create("OrGate")
        self.not_gate_2 = self.api.create("NotGate")

        self.api.connect(self.switches[0].output_pin_id, self.or_gate.input_pin_ids[0],)
        self.api.connect(self.switches[1].output_pin_id, self.not_gate.input_pin_id,)
        self.api.connect(self.not_gate.output_pin_id, self.or_gate.input_pin_ids[1])
        self.api.connect(self.or_gate.output_pin_id, self.not_gate_2.input_pin_id)

        self.api.connect(self.not_gate_2.output_pin_id, self.led.input_pin_id)
        

        print(self.api.list())
        print(self.api.wires())

        self.say("Guess the password!")
        
    def check(self):
        print("I am going to check wether", self.api.probe_pin(self.led.input_pin_id), "is equal to", 1)
        print(" - Result is:", self.api.probe_pin(self.led.input_pin_id) == 1)
        if self.api.probe_pin(self.led.input_pin_id) == 1:
            self.say("Success!")
            return True
        
        #for btn in self.switches:
        #    if btn is self.correct_btn:
        #        continue
        #    if self.api.probe_pin(btn.output_pin_id) == 1:
        #        self.say("Failure: wrong button pressed")
        #        return True


def main():
    world = CircuitWorld()
    sce = Scenario1(world)
    sce.run()


if __name__ == "__main__":
    main()
