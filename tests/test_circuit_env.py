from environments import CircuitWorld
import pytest

@pytest.fixture(scope="function")
def world():
    world = CircuitWorld()
    return world


def test_pressing_button(world):
    api = world.api
    btn = api.create("Button")
    btn.interact("Press")

    assert api.probe_pin(btn.output_pin) == 1


def test_turn_led_on(world):
    api = world.api
    btn = api.create("Button")
    led = api.create("LED")
    api.connect(1,2)

    btn.interact("Press")

    assert api.probe_pin(led.input_pin) == 1


def test_button(world):
    api = world.api
    btn = api.create("Button")

    btn.interact("Press")

    world.step()

    assert api.probe_pin(btn.output_pin) == 0


def test_disconnect(world):  # Not sure if steps should be considered here
    api = world.api
    btn = api.create("Button")
    led = api.create("LED")
    api.connect(1,2)

    btn.interact("Press")

    result_1 = api.probe_pin(led.input_pin) == 1

    api.disconnect(1,2)

    result_2 = api.probe_pin(led.input_pin) == 0

    assert result_1 and result_2


def test_stay_pressed(world):
    api = world.api
    btn = api.create("Button")
    btn.interact("PressDown")

    result_1 = api.probe_pin(btn.output_pin) == 1

    world.step()

    result_2 = api.probe_pin(btn.output_pin) == 1

    assert result_1 and result_2


def test_clock(world): # Clock's output_pin should start in 0 and oscilate between 0 | 1 every step
    api = world.api
    clock = api.create("Clock")

    empty = []
    for i in range(10):
        empty.append(api.probe_pin(clock.output_pin) == i%2)
        world.step()
    
    assert empty


def test_lever(world):
    api = world.api
    switch = api.create("Switch")

    result_1 = api.probe_pin(switch.output_pin) == 0

    switch.interact("Press")

    result_2 = api.probe_pin(switch.output_pin) == 1

    assert result_1 and result_2


def test_AND_gate(world):
    api = world.api
    switch_1 = api.create("Switch")
    switch_1.interact("Press")
    switch_2 = api.create("Switch")
    switch_2.interact("Press")
    gate_AND = api.create("AND_gate")

    api.connect(1,3)
    api.connect(2,3)

    assert api.probe_pin(gate_AND.output_pin) == 1


def test_NOT_gate(world):
    api = world.api
    switch = api.create("Switch")
    switch.interact("Press")
    gate_NOT = api.create("NOT_gate")

    api.connect(1,2)

    assert api.probe_pin(gate_NOT.output_pin) == 1


def test_password(world):
    api = world.api
    button_1 = api.create("Button")
    button_2 = api.create("Button")
    button_3 = api.create("Button")
    
    gate_NOT_1 = api.create("NOT_gate")
    gate_NOT_2 = api.create("NOT_gate")
    gate_NOT_3 = api.create("NOT_gate")

    api.connect(1,6) # b1 -> g3
    api.connect(2,4) # b2 -> g1
    api.connect(3,5) # b3 -> g2

    api.connect(4,6) # g1 -> g3
    api.connect(5,6) # g2 -> g3

    result_1 = api.probe_pin(gate_NOT_3.output_pin) == 0

    button_2.interact("Press")
    result_2 = api.probe_pin(gate_NOT_3.output_pin) == 0

    button_3.interact("Press")
    result_3 = api.probe_pin(gate_NOT_3.output_pin) == 1

    assert result_1 and result_2 and result_3