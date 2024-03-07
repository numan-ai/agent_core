import abc


class Component(abc.ABC):    
    def __init__(self, world, component_id) -> None:
        self.world = world
        self.id = component_id
        self.input_pins: list[int] = []
        self.output_pins: list[int] = []
    
    @property
    def input_pin(self):
        if len(self.input_pins) != 1:
            raise ValueError("Component must have exactly one input pin")
        return self.input_pins[0]
    
    @property
    def output_pin(self):
        if len(self.output_pins) != 1:
            raise ValueError("Component must have exactly one output pin")
        return self.output_pins[0]
    
    @abc.abstractmethod
    def interact(self, action: str = "Press"):
        pass
    
    def step(self):
        pass
    

class Button(Component):
    def __init__(self, world, component_id) -> None:
        super().__init__(world, component_id)
        self.power = 0
        self.output_pins.append(self.world.get_next_pin_id())
        world.pin_values[self.output_pin] = 0
        
    def interact(self, action: str = "Press"):
        if action == "Press":
            self.power = 1
            self.world.pin_values[self.output_pin] = 1
        elif action == "PressDown":
            self.power = -1
            self.world.pin_values[self.output_pin] = 1
        elif action == "PressUp":
            self.power = 0
        else:
            raise ValueError(f"Unknown action: {action}")
        
    def step(self):
        self.world.pin_values[self.output_pin] = min(max(self.power, 0), 1)
        if self.power > 0:
            self.power -= 1
            
            
            
class Switch(Component):
    def __init__(self, world, component_id) -> None:
        super().__init__(world, component_id)
        self.power = 0
        self.output_pins.append(self.world.get_next_pin_id())
        world.pin_values[self.output_pin] = 0
        
    def interact(self, action: str = "Press"):
        if action == "Press":
            self.power = 1 - self.power
            self.world.pin_values[self.output_pin] = self.power
        else:
            raise ValueError(f"Unknown action: {action}")
        
    def step(self):
        self.world.pin_values[self.output_pin] = min(max(self.power, 0), 1)


class LED(Component):
    def __init__(self, world, component_id) -> None:
        super().__init__(world, component_id)
        self.input_pins.append(self.world.get_next_pin_id())
        world.pin_values[self.input_pin] = 0
        
    def interact(self, action: str = "Press"):
        raise ValueError("LED cannot be interacted with")


class CircuitWorld:
    last_id = 0
    last_pin_id = 0
    
    def __init__(self) -> None:
        self.components = {}
        self.wires = []
        self.pin_values = {}
        self.api = CircuitAPI(self)
        
    @classmethod
    def get_next_id(cls):
        cls.last_id += 1
        return cls.last_id
            
    @classmethod
    def get_next_pin_id(cls):
        cls.last_pin_id += 1
        return cls.last_pin_id
    
    def step(self):
        for comp in self.components.values():
            comp.step()
    
    
class CircuitAPI:
    def __init__(self, world: CircuitWorld) -> None:
        self.__world = world
    
    def list(self):
        return list(self.__world.components.values())
    
    def create(self, label: str):
        component_classes = {
            "Button": Button,
            "LED": LED,
            "Switch": Switch,
        }
        comp = component_classes[label](self.__world, self.__world.get_next_id())
        self.__world.components[comp.id] = comp
        return comp
    
    def connect(self, pin_a: int, pin_b: int):
        self.__world.wires.append((pin_a, pin_b))
    
    def interact(self, component_id: int, action: str):
        try:
            comp = self.__world.components[component_id]
        except IndexError:
            raise ValueError(f"Component with id {component_id} does not exist")
        comp.interact(action)
    
    def probe_pin(self, pin_id: int):
        try:
            return self.__world.pin_values[pin_id]
        except KeyError:
            raise ValueError(f"Pin with id {pin_id} does not exist")
