import random

from environments.circuits.world import CircuitWorld
from scenarios.human_subjects.base_scenario import Scenario

    
class Scenario1(Scenario):
    def setup(self):
        self.btns = [
            self.api.create("Button")
            for _ in range(4)
        ]
        self.led = self.api.create("LED")
        self.corrent_btn = random.choice(self.btns)
        self.api.connect(
            self.corrent_btn.output_pin_id,
            self.led.input_pin_id,
        )
        
        self.say("Turn on the LED")
        
    def check(self):
        if self.api.probe_pin(self.led.input_pin_id) == 1:
            self.say("Success!")
            return True
        
        for btn in self.btns:
            if btn is self.corrent_btn:
                continue
            if self.api.probe_pin(btn.output_pin_id) == 1:
                self.say("Failure: wrong button pressed")
                return True


def main():
    world = CircuitWorld()
    sce = Scenario1(world)
    sce.run()


if __name__ == "__main__":
    main()
