def simple_planning_strategy():
    world_copy = make_virtual_world_model_copy()
    goal = get_goal()
    
    goal_closeness = get_goal_closeness(world_copy, goal)
    
    run("how close am I to the goal, given the goal variable and world_copy variable")
    
    goal_closeness = run_instance(
        Instance("HowClose_Question", {
            "????": Instance(""),
            "world": world_copy,
            "goal": goal,
        })
    )
    
    while not is_the_goal_reached(world_copy):
        next_action = find_the_next_action_using_associations_only(world_copy, goal)
        new_world_copy = apply_action(world_copy, next_action)
        
        new_goal_closeness = run_instance(
            Instance("HowClose_Question", {
                "????": Instance(""),
                "world": new_world_copy,
                "goal": goal,
            })
        )
        if is_closer_to_the_goal(goal_closeness, new_goal_closeness):
            goal_closeness = new_goal_closeness
            world_copy = new_world_copy # or undo the action if it's not good
