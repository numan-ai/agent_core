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
    api.connect(
        btn.output_pin_id,
        led.input_pin_id
    )

    btn.interact("Press")
    
    world.step()

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
    api.connect(
        btn.output_pin_id,
        led.input_pin_id
    )

    btn.interact("Press")
    world.step()

    assert api.probe_pin(led.input_pin_id) == 1

    api.disconnect(
        btn.output_pin_id,
        led.input_pin_id
    )
    world.step()

    assert api.probe_pin(led.input_pin_id) == 0


def test_btn_press_down(world):
    api = world.api
    btn = api.create("Button")
    btn.interact("PressDown")

    assert api.probe_pin(btn.output_pin_id) == 1

    world.step()

    assert api.probe_pin(btn.output_pin_id) == 1


def test_circuits_clock(world): # Clock's output_pin should start in 0 and oscilate between 0 | 1 every step
    api = world.api
    clock = api.create("Clock")

    for i in range(10):
        assert api.probe_pin(clock.output_pin_id) == i % 2
        world.step()


def test_circuits_switch(world):
    api = world.api
    switch = api.create("Switch")

    assert api.probe_pin(switch.output_pin_id) == 0

    switch.interact("Press")

    assert api.probe_pin(switch.output_pin_id) == 1


def test_circuits_and_gate(world):
    api = world.api
    switch_1 = api.create("Switch")
    switch_2 = api.create("Switch")
    and_gate = api.create("AndGate")

    api.connect(
        switch_1.output_pin_id,
        and_gate.input_pin_ids[0]
    )
    api.connect(
        switch_2.output_pin_id,
        and_gate.input_pin_ids[1]
    )
    
    switch_1.interact("Press")
    switch_2.interact("Press")
    
    world.step()

    assert api.probe_pin(and_gate.output_pin_id) == 1


def test_circuits_not_gate(world):
    api = world.api
    switch = api.create("Switch")
    switch.interact("Press")
    not_gate = api.create("NotGate")

    api.connect(
        switch.output_pin_id,
        not_gate.input_pin_id
    )

    assert api.probe_pin(not_gate.output_pin_id) == 1


def test_circuit_wire_junction(world):
    api = world.api
    button_1 = api.create("Switch")
    button_2 = api.create("Switch")
    
    gate = api.create("NotGate")

    api.connect(
        button_1.output_pin_id,
        gate.input_pin_id
    )
    api.connect(
        button_2.output_pin_id,
        gate.input_pin_id
    )

    assert api.probe_pin(gate.output_pin_id) == 1

    button_1.interact("Press")
    world.step()
    
    assert api.probe_pin(gate.output_pin_id) == 0

    button_2.interact("Press")
    world.step()
    
    assert api.probe_pin(gate.output_pin_id) == 0
