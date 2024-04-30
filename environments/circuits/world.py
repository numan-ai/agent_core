import abc
import random


class Component(abc.ABC):    
    def __init__(self, world: 'CircuitWorld', component_id) -> None:
        self.world: CircuitWorld = world
        self.id = component_id
        self.input_pin_ids: list[int] = []
        self.output_pin_ids: list[int] = []
    
    @property
    def input_pin_id(self):
        if len(self.input_pin_ids) != 1:
            raise ValueError("Component must have exactly one input pin")
        return self.input_pin_ids[0]
    
    @property
    def output_pin_id(self):
        if len(self.output_pin_ids) != 1:
            raise ValueError("Component must have exactly one output pin")
        return self.output_pin_ids[0]
    
    @abc.abstractmethod
    def interact(self, action: str = "Press"):
        pass
    
    def add_input_pin(self):
        pin_id = self.world.get_next_pin_id()
        self.input_pin_ids.append(pin_id)
        self.world.pin_values[pin_id] = 0
        self.world.input_pin_ids.add(pin_id)
        
        return pin_id
        
    def add_output_pin(self):
        pin_id = self.world.get_next_pin_id()
        self.output_pin_ids.append(pin_id)
        self.world.pin_values[pin_id] = 0
        self.world.output_pin_ids.add(pin_id)
        
        return pin_id
        
    def step(self):
        pass
    
    def inspect(self):
        return f"""<{self.__class__.__name__}
    id      = {self.id}
    inputs  = {self.input_pin_ids}
    outputs = {self.output_pin_ids}>"""
    
    def to_json(self):
        return {
            "type": self.__class__.__name__,
            "id": self.id,
            "in_pins": [
                {
                    "id": pin_in,
                    "value": self.world.pin_values[pin_in],
                }
                for pin_in in self.input_pin_ids
            ],
            "out_pins": [
                {
                    "id": pin_out,
                    "value": self.world.pin_values[pin_out],
                }
                for pin_out in self.output_pin_ids
            ]
        }
    
    def __repr__(self) -> str:
        if self.input_pin_ids:
            in_part = f" in={self.input_pin_ids}"
        else:
            in_part = ""
        if self.output_pin_ids:
            out_part = f" out={self.output_pin_ids}"
        else:
            out_part = ""
        return f"<{self.__class__.__name__} id={self.id}{in_part}{out_part}>"
    

class Button(Component):
    def __init__(self, world, component_id) -> None:
        super().__init__(world, component_id)
        self.power = 0.0
        self.add_output_pin()
        
    def interact(self, action: str = "Press"):
        if action == "Press":
            self.power = 1.0
            self.world.pin_values[self.output_pin_id] = 1
        elif action == "PressDown":
            self.power = float('inf')
            self.world.pin_values[self.output_pin_id] = 1
        elif action == "PressUp":
            self.power = 0.0
        else:
            raise ValueError(f"Unknown action: {action}")
        
    def step(self):
        if self.power > 0:
            self.power -= 1
        self.world.pin_values[self.output_pin_id] = int(min(max(self.power, 0), 1))

            
class NotGate(Component):
    def __init__(self, world, component_id) -> None:
        super().__init__(world, component_id)
        self.add_input_pin()
        self.add_output_pin()
        world.pin_values[self.output_pin_id] = 1
        
    def interact(self, action: str):
        raise ValueError("NotGate cannot be interacted with")
        
    def step(self):
        input_value = min(max(self.world.pin_values[self.input_pin_id], 0), 1)
        value = 1 - input_value
        self.world.pin_values[self.output_pin_id] = value
        
        
class AndGate(Component):
    def __init__(self, world, component_id) -> None:
        super().__init__(world, component_id)
        self.add_input_pin()
        self.add_input_pin()
        self.add_output_pin()
        
    def interact(self, action: str):
        raise ValueError("AndGate cannot be interacted with")
        
    def step(self):
        value = self.world.pin_values[self.input_pin_ids[0]] * \
            self.world.pin_values[self.input_pin_ids[1]]
        self.world.pin_values[self.output_pin_id] = value
        
        
class OrGate(Component):
    def __init__(self, world, component_id) -> None:
        super().__init__(world, component_id)
        self.add_input_pin()
        self.add_input_pin()
        self.add_output_pin()
        
    def interact(self, action: str):
        raise ValueError("OrGate cannot be interacted with")
        
    def step(self):
        value = self.world.pin_values[self.input_pin_ids[0]] + \
            self.world.pin_values[self.input_pin_ids[1]]
        self.world.pin_values[self.output_pin_id] = min(max(value, 0), 1)


class XorGate(Component):
    def __init__(self, world, component_id) -> None:
        super().__init__(world, component_id)
        self.add_input_pin()
        self.add_input_pin()
        self.add_output_pin()
        
    def interact(self, action: str):
        raise ValueError("OrGate cannot be interacted with")
        
    def step(self):
        input_a = self.world.pin_values[self.input_pin_ids[0]]
        input_b = self.world.pin_values[self.input_pin_ids[1]]
        value = input_a + input_b - input_a * input_b
        self.world.pin_values[self.output_pin_id] = min(max(value, 0), 1)


class Switch(Component):
    def __init__(self, world, component_id) -> None:
        super().__init__(world, component_id)
        self.power = 0
        self.add_output_pin()
        
    def interact(self, action: str = "Press"):
        if action == "Press":
            self.power = 1 - self.power
            self.world.pin_values[self.output_pin_id] = self.power
        else:
            raise ValueError(f"Unknown action: {action}")
        
    def step(self):
        self.world.pin_values[self.output_pin_id] = min(max(self.power, 0), 1)


class LED(Component):
    def __init__(self, world, component_id) -> None:
        super().__init__(world, component_id)
        self.add_input_pin()
        
    def interact(self, action: str = "Press"):
        raise ValueError("LED cannot be interacted with")

class Clock(Component):
    def __init__(self, world, component_id) -> None:
        super().__init__(world, component_id)
        self.add_output_pin()
        
    def interact(self, action: str = "Press"):
        raise ValueError("Clock cannot be interacted with")
        
    def step(self):
        value = self.world.pin_values[self.output_pin_id]
        self.world.pin_values[self.output_pin_id] = 1 - value


class CircuitWorld:
    last_id = random.randrange(0, 100)
    last_pin_id = random.randrange(0, 100)
    
    def __init__(self):
        self.components = {}
        self.wires = []
        self.input_pin_ids = set()
        self.output_pin_ids = set()
        self.pin_values = {}
        self.api = CircuitAPI(self)
        
    def reset(self):
        self.components = {}
        self.wires = []
        self.input_pin_ids = set()
        self.output_pin_ids = set()
        self.pin_values = {}
        
    @classmethod
    def get_next_id(cls):
        cls.last_id += 1
        return cls.last_id
            
    @classmethod
    def get_next_pin_id(cls):
        cls.last_pin_id += 1
        return cls.last_pin_id
    
    def step(self):
        self._step_wires()
        
        for comp in self.components.values():
            comp.step()
            
    def _step_wires(self):
        for pin_id in self.input_pin_ids:
            connected_wires = [
                out_id for out_id, in_id in self.wires
                if in_id == pin_id
            ]
            values = [self.pin_values[out_id] for out_id in connected_wires]
            value = max(values, default=0)
            
            self.pin_values[pin_id] = value
        
    
class CircuitAPI:
    def __init__(self, world: CircuitWorld) -> None:
        self.__world = world
    
    def list(self):
        return list(self.__world.components.values())
        
    def list_json(self):
        return [
            x.to_json() for x in self.list()
        ] + [
            {
                "type": "Wire",
                "start_pin": start,
                "end_pin": end,
            }
            for start, end in self.__world.wires
        ]
    
    def wires(self, pin_id=None):
        if pin_id is not None:
            return [
                (out_id, in_id) for out_id, in_id in self.__world.wires
                if out_id == pin_id or in_id == pin_id
            ]
        return self.__world.wires
    
    def create(self, label: str):
        component_classes = {
            "Button": Button,
            "LED": LED,
            "Switch": Switch,
            "NotGate": NotGate,
            "AndGate": AndGate,
            "OrGate": OrGate,
            "XorGate": XorGate,
            "Clock": Clock,
        }
        comp = component_classes[label](self.__world, self.__world.get_next_id())
        self.__world.components[comp.id] = comp
        return comp
    
    def connect(self, pin_out: int, pin_in: int):
        if pin_out not in self.__world.output_pin_ids:
            raise ValueError(f"Pin with id {pin_out} is not an output pin")
        if pin_in not in self.__world.input_pin_ids:
            raise ValueError(f"Pin with id {pin_in} is not an input pin")
        if (pin_out, pin_in) in self.__world.wires:
            return
        self.__world.wires.append((pin_out, pin_in))

    def disconnect(self, pin_a: int, pin_b: int):
        self.__world.wires.remove((pin_a, pin_b))
    
    def interact(self, component_id: int, action: str):
        try:
            comp = self.__world.components[component_id]
        except IndexError:
            raise ValueError(f"Component with id {component_id} does not exist")
        comp.interact(action)
    
    def inspect(self, component_id: int):
        try:
            comp = self.__world.components[component_id]
        except IndexError:
            raise ValueError(f"Component with id {component_id} does not exist")
        return comp.inspect()
    
    def probe_pin(self, pin_id: int):
        try:
            return self.__world.pin_values[pin_id]
        except KeyError:
            raise ValueError(f"Pin with id {pin_id} does not exist")

    def press(self, component_id: int):
        self.interact(component_id, "Press")