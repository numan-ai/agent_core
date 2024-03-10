from environments import CircuitWorld
import pytest


@pytest.fixture(scope="function")
def world():
    world = CircuitWorld()
    return world


def test_circuit_btn_press(world):
    api = world.api
    btn = api.create("Button")
    btn.interact("Press")

    assert api.probe_pin(btn.output_pin_id) == 1


def test_circuit_btn_turn_on_led(world):
    api = world.api
    btn = api.create("Button")
    led = api.create("LED")
    api.connect(1,2)

    btn.interact("Press")

    assert api.probe_pin(led.input_pin_id) == 1


def test_circuit_btn_unpress(world):
    api = world.api
    btn = api.create("Button")

    btn.interact("Press")

    world.step()

    assert api.probe_pin(btn.output_pin_id) == 0


def test_circuit_disconnect(world):  # Not sure if steps should be considered here
    api = world.api
    btn = api.create("Button")
    led = api.create("LED")
    api.connect(1, 2)

    btn.interact("Press")

    assert api.probe_pin(led.input_pin_id) == 1

    api.disconnect(1, 2)

    assert api.probe_pin(led.input_pin_id) == 0


def test_btn_press_down(world):
    api = world.api
    btn = api.create("Button")
    btn.interact("PressDown")

    result_1 = api.probe_pin(btn.output_pin_id) == 1

    world.step()

    result_2 = api.probe_pin(btn.output_pin_id) == 1

    assert result_1 and result_2


def test_circuits_clock(world): # Clock's output_pin should start in 0 and oscilate between 0 | 1 every step
    api = world.api
    clock = api.create("Clock")

    empty = []
    for i in range(10):
        empty.append(api.probe_pin(clock.output_pin_id) == i%2)
        world.step()
    
    assert empty


def test_circuits_switch(world):
    api = world.api
    switch = api.create("Switch")

    result_1 = api.probe_pin(switch.output_pin_id) == 0

    switch.interact("Press")

    result_2 = api.probe_pin(switch.output_pin_id) == 1

    assert result_1 and result_2


def test_circuits_and_gate(world):
    api = world.api
    switch_1 = api.create("Switch")
    switch_1.interact("Press")
    switch_2 = api.create("Switch")
    switch_2.interact("Press")
    and_gate = api.create("AndGate")

    api.connect(1, 3)
    api.connect(2, 3)

    assert api.probe_pin(and_gate.output_pin_id) == 1


def test_circuits_not_gate(world):
    api = world.api
    switch = api.create("Switch")
    switch.interact("Press")
    not_gate = api.create("NotGate")

    api.connect(1,2)

    assert api.probe_pin(not_gate.output_pin_id) == 1


def test_password(world):
    api = world.api
    button_1 = api.create("Button")
    button_2 = api.create("Button")
    
    gate_NOT = api.create("NotGate")

    api.connect(1,3)
    api.connect(2,3) 

    result_1 = api.probe_pin(gate_NOT.output_pin_id) == 1

    button_1.interact("Press")
    result_2 = api.probe_pin(gate_NOT.output_pin_id) == 1

    button_2.interact("Press")
    result_3 = api.probe_pin(gate_NOT.output_pin_id) == 0

    assert result_1 and result_2 and result_3