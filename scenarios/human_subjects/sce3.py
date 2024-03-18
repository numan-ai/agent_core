import random
from environments.circuits.world import CircuitWorld
from scenarios.human_subjects.base_scenario import Scenario


def _get_random_gate(api):
    gate_names = [
        "AndGate",
        "OrGate",
        "NotGate",
        "XorGate",
    ]
    
    return api.create(random.choice(gate_names))


def _create_layer(api, previous_layer):
    layer = []
    for _ in range(len(previous_layer) // 2):
        gate = _get_random_gate(api)
        layer.append(gate)
        
    return layer


class Scenario3(Scenario):
    def setup(self):
        layers_count = 2
        switches_count = 2 ** (layers_count + 1)
        
        while True:
            self.led_ok = self.api.create("LED")
            self.led_err = self.api.create("LED")
            
            layers = [
                [
                    self.api.create("Switch")
                    for _ in range(switches_count)
                ],
            ]
            
            for _ in range(layers_count):
                layers.append(_create_layer(self.api, layers[-1]))
            
            layers.append([
                self.led_ok,
                self.led_err,
            ])

            for layer_idx in range(len(layers) - 1):
                layer_start = layers[layer_idx]
                layer_end = layers[layer_idx + 1]
                output_pins = [
                    comp.output_pin_id
                    for comp in layer_start
                ]
                input_pins = [
                    pin_id
                    for comp in layer_end
                    for pin_id in comp.input_pin_ids
                ]
                random.shuffle(output_pins)
                random.shuffle(input_pins)
                
                for start, end in zip(output_pins, input_pins):
                    self.api.connect(start, end)
                    
                random_start = random.choice(output_pins)
                random_end = random.choice(input_pins)
                self.api.connect(random_start, random_end)
                
            for _ in range(5):
                self.world.step()
                if self.api.probe_pin(self.led_ok.input_pin_id) == 1:
                    break
                if self.api.probe_pin(self.led_err.input_pin_id) == 1:
                    break
            else:
                break
            
            self.world.reset()
            continue

        self.say(f"Light up the LED with id: {self.led_ok.id}")
        self.say(f"Do not light up the LED with id: {self.led_err.id}")
        
    def check(self):
        if self.api.probe_pin(self.led_ok.input_pin_id) == 1:
            self.say("Success!")
            return True
        
        if self.api.probe_pin(self.led_err.input_pin_id) == 1:
            self.say("Failure: wrong LED lit up")
            return True


def main():
    world = CircuitWorld()
    sce = Scenario3(world)
    sce.run()


if __name__ == "__main__":
    main()
