from src.instance import Instance


def main():
    goal = Instance("GoalAct", {
        "act": Instance("ActOnEntity", {
            "action": Instance("RemoveAct", {
            }),
            "entity": Instance("EntityReferencedByName", {
                "concept": Instance("Concept", {
                    "value": "File"
                }),
                "name": Instance("String", {
                    "value": "main.txt"
                })
            })
        })
    })
    
    goal = Instance("GoalChangeField", {
        "entity": ...,
        "field": Instance("String", {
            "value": "exists"
        }),
        "value": Instance("Boolean", {
            "value": False
        })
    })


if __name__ == '__main__':
    main()
