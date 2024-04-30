import asyncio
from functools import partial
import json

import hmap
import websockets

from hmap import (
    Match,
    Pattern,
    PatternMap,
    PatternNode,
)

from environments import CircuitWorld
from prototyping.lrd_traversal import traverse_lrd
from src.agent_core import AgentCore
from src.knowledge_base.module import KBEdgeType, KnowledgeBase
from src.knowledge_base.reverse_specialisation import reverse_specialise
from src.world_model.instance import Instance


def get_word_concepts(word, kb: KnowledgeBase):
    word_node = kb.get_word(word)
    if word_node is None:
        return []
    concepts = kb.out(word_node.id, KBEdgeType.ASSOCIATED)
    return [
        concept.data["name"]
        for concept in concepts
    ]


pattern_map = PatternMap.from_list([
    Pattern("ActOnReferencedEntityStatement", [
        PatternNode("Act", "act"),
        PatternNode("EntityReference", id="reference"),
    ]),
    Pattern("IndefiniteEntityReference", [
        PatternNode("POS_IndefiniteArticle"),
        PatternNode("EntityClass", id="ref_class"),
    ]),
    Pattern("IndefinitePluralEntityReference", [
        PatternNode("POS_IndefiniteArticle"),
        PatternNode("PluralEntityClass", id="ref_class"),
    ]),
    Pattern("DefiniteEntityReference", [
        PatternNode("POS_DefiniteArticle"),
        PatternNode("EntityClass", id="ref_class"),
    ]),
    Pattern("GreetingStatement", [
        PatternNode("Word_hello"),
    ]),
    Pattern("GreetingStatement", [
        PatternNode("Word_hi"),
    ]),
    Pattern("PrintMathExpression", [
        PatternNode("Word_print"),
        PatternNode("MathExpression", id="expression"),
    ]),
    Pattern("NegativeNumber", [
        PatternNode("MinusSign"),
        PatternNode("Number", id="number"),
    ]),
    Pattern("TurnOnAct", [
        PatternNode("Word_turn"),
        PatternNode("Word_on"),
    ]),
    Pattern("FloatingPointNumber", [
        PatternNode("Number", id="before_dot"),
        PatternNode("Period"),
        PatternNode("Number", id="after_dot"),
    ]),
    Pattern("BinaryMathExpression", [
        PatternNode("MathExpression", id="left"),
        PatternNode("Sign", id="sign"),
        PatternNode("MathExpression", id="right"),
    ]),
    Pattern("BinaryMathExpression", [
        PatternNode("MathExpression", id="left"),
        PatternNode("Sign", id="sign"),
        PatternNode("MathExpression", id="right"),
    ]),
    Pattern("MathExpressionInParenthesis", [
        PatternNode("LeftParenthesis"),
        PatternNode("MathExpression", id="expression"),
        PatternNode("RightParenthesis"),
    ]),

    Pattern("InOrderTo", [
        PatternNode("Word_in"),
        PatternNode("Word_order"),
        PatternNode("Word_to"),
    ]),
    Pattern("YouNeedTo", [
        PatternNode("Word_you"),
        PatternNode("Word_need"),
        PatternNode("Word_to"),
    ]),
    Pattern("Act_IOT_Act", [
        PatternNode("InOrderTo"),
        PatternNode("ActOnReferencedEntityStatement"),
        PatternNode("YouNeedTo"),
        PatternNode("ActOnReferencedEntityStatement"),
    ]),

    Pattern("ConceptIsConcept", [
        PatternNode("IndefiniteEntityReference"),
        PatternNode("Word_is"),
        PatternNode("IndefiniteEntityReference"),
    ]),

    Pattern("ConceptAreConcept", [
        PatternNode("IndefinitePluralEntityReference"),
        PatternNode("Word_are"),
        PatternNode("IndefinitePluralEntityReference"),
    ]),
])


HIERARCHY = None


def send_server_event(msg: str, queue: asyncio.Queue):
    queue.put_nowait({
        "type": "agent_message",
        "data": str(msg),
        "ref": "on_agent_message",
    })


def setup(world_type, client_event_queue):
    global HIERARCHY
    world: CircuitWorld = world_type()

    agent = AgentCore()
    agent.action_manager.interpreter.global_vars["api"] = world.api
    HIERARCHY = agent.knowledge_base.hierarchy
    
    btn = world.api.create("Switch")
    led = world.api.create("LED")
    world.api.connect(btn.output_pin_id, led.input_pin_id)
    
    wm_btn = Instance("Button", {
        "id": btn.id,
        "output_pin": Instance("Pin", {
            "id": btn.output_pin_id,
        }),
    })
    wm_led = Instance("LED", {
        "id": led.id,
        "input_pin": Instance("Pin", {
            "id": led.input_pin_id,
        }),
    })
    wm_wire = Instance("Wire", {
        "id": "wire",
        "input_pin": wm_btn.fields.output_pin,
        "output_pin": wm_led.fields.input_pin,
    })
    wm_btn.fields.output_pin.fields['wire'] = wm_wire
    wm_led.fields.input_pin.fields['wire'] = wm_wire
    
    agent.world_model.add(wm_btn)
    agent.world_model.add(wm_led)
    agent.world_model.add(wm_wire)
    
    reverse_specialise(wm_btn.fields.output_pin,  agent.knowledge_base)
    reverse_specialise(wm_led.fields.input_pin, agent.knowledge_base)
    
    # sentence = "create a button"
    # client_event_queue.put_nowait({
    #     "type": "user_message",
    #     "data": sentence,
    # })
    
    return world, agent


def _match_to_instance(match: Match, tree) -> Instance:
    value = "".join(
        tree.sentence_map[match.start: match.start + match.size]
    )
    
    extra_fields = {}
    if match.concept == "Number":
        if value.isdigit():
            extra_fields["value"] = int(value)
        else:
            extra_fields["value"] = float(value)
    elif match.concept == "String":
        extra_fields["value"] = value
    
    return Instance(match.concept, {
        **{
            key: _match_to_instance(value, tree)
            for key, value in match.fields.items()
        },
        **extra_fields,
    })


async def process_message(msg: str, agent: AgentCore):
    is_ok, tree = hmap.parse_sentence(
        msg, 
        pattern_map,
        HIERARCHY,
        partial(
            get_word_concepts,
            kb=agent.knowledge_base,
        )
    )
    matches = tree.get_matches()
    
    if not is_ok or len(matches) != 1:
        print("can't parse")
        from pprint import pprint
        pprint(matches)
        return
    
    instance = _match_to_instance(matches[0], tree)
    print(instance)
    
    agent.input_processor.send_event(Instance("UserSaidEvent", {
        "sentence": instance,
    }))


def process_env_click(component_id, world, agent):
    world.api.press(component_id)


async def run_agent(client_event_queue: asyncio.Queue, server_event_queue: asyncio.Queue):
    world, agent = setup(CircuitWorld, client_event_queue)
    agent.action_manager.interpreter.global_vars["_print"] = print
    agent.action_manager.interpreter.global_vars["traverse_lrd"] = traverse_lrd
    agent.action_manager.interpreter.global_vars["print"] = partial(
        send_server_event,
        queue=server_event_queue,
    )
    
    # await process_message("turn on the led", agent)
    
    idx = 0
    while True:
        agent.action_manager.done = False
        for _ in range(100):
            agent.step(world=world)
            if agent.action_manager.done:
                await asyncio.sleep(0.1)
                break
        
        if idx % 10 == 0:
            server_event_queue.put_nowait({
                "type": "world_update",
                "data": world.api.list_json(),
                "ref": "world_update",
            })
            print('led state:', world.api.probe_pin(world.api.list()[1].input_pin_id))
            
        
        idx += 1
            
        # print(world.api.probe_pin(world.api.list()[0].output_pin_id))
        
        
        try:
            evt = client_event_queue.get_nowait()
            if evt['type'] == 'message':
                await process_message(evt['data'], agent)
            elif evt['type'] == 'env_click':
                await process_env_click(evt['data'], world, agent)
        except asyncio.QueueEmpty:
            pass


async def on_message(websocket, path, clients_list: list, client_event_queue: asyncio.Queue, server_event_queue: asyncio.Queue):
    print("Client connected")
    clients_list.append(websocket)
    
    async for data in websocket:
        msg = json.loads(data)
        client_event_queue.put_nowait(msg)
        
        
async def send_server_events(clients_list, server_event_queue: asyncio.Queue):
    while True:
        try:
            msg = server_event_queue.get_nowait()
        except asyncio.QueueEmpty:
            await asyncio.sleep(0.1)
            continue

        data = json.dumps(msg)
        
        await asyncio.sleep(0.15)

        for client in clients_list.copy():
            try:
                await client.send(data)
            except websockets.exceptions.ConnectionClosed:
                clients_list.remove(client)
                print("Client disconnected")


async def main():
    clients_list = []
    client_event_queue = asyncio.Queue()
    server_event_queue = asyncio.Queue()
    
    callback = partial(
        on_message,
        clients_list=clients_list,
        client_event_queue=client_event_queue,
        server_event_queue=server_event_queue,
    )
    async with websockets.serve(callback, "localhost", 8382):
        await asyncio.gather(
            run_agent(client_event_queue, server_event_queue),
            send_server_events(clients_list, server_event_queue),
        )


if __name__ == "__main__":
    asyncio.run(main())
