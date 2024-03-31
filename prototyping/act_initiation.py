from grass import AssociativeGraph

from src.knowledge_base.in_memory_kb import InMemoryKB
from src.world_model.instance import Instance


def main():
    # we have a current action
    # the next action will be automatic??
    # incoming stimuli will steer the agent to a different action
    # planning influences on the next action
    # actions are hierarchical
    # high-level planning requires active thinking to convert the plan into actions
    
    kb = InMemoryKB([], [])
    actions_graph = AssociativeGraph([], bidirectional=False)
    actions_graph.set_weight("Alexandra", "Telegram", 1.0)
    actions_graph.set_weight("Telegram", "func::make_telegram_call", 1.0)
    actions_graph.set_weight("CallAct", "func::make_telegram_call", 1.0)
    actions_graph.set_weight("CallAct", "func::make_facebook_call", 1.0)
    actions_graph.set_weight("CallAct", "func::make_phone_call", 1.0)
    actions_graph.set_weight("Action", "func::make_telegram_call", 1.0)
    actions_graph.set_weight("Action", "func::make_facebook_call", 1.0)
    actions_graph.set_weight("Action", "func::make_phone_call", 1.0)
    
    next_action_graph = AssociativeGraph([], bidirectional=False)
    next_action_graph.set_weight("func::make_telegram_call", "func::take_mobile_phone", 1.0)
    next_action_graph.set_weight("func::take_mobile_phone", "func::find_mobile_phone", 1.0)
    
    task = Instance("ActOnEntity", {
        "act": Instance("CallAct"),
        "entity": Instance("Alexandra"),
    })
    
    actions = actions_graph.lookup("Action", "CallAct", "Alexandra", "ActOnEntity", depth=3)
    print(actions)
    # immediately you imagine Alexandra
    # since you have done this before you associate calling Alexandra with the Telegram call
    # now that Telegram has been activated you will find a correct task to call Alexandra
    
    pass


if __name__ == "__main__":
    main()
