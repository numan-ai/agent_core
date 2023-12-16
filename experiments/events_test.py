from threading import Thread
import time
from shpat.hierarchy import DictHierarchyProvider

from src.world_model.world_model import WorldModel


HIERARCHY = DictHierarchyProvider(children={
    "Article": ["DefiniteArticle", "IndefiniteArticle"],
})


def world_model_thread(wm: WorldModel):
    while True:
        wm.clock_tick()
        time.sleep(1)
        
        
def send_event(wm: WorldModel, wait: int, event_cid: str):
    time.sleep(wait)
    wm.new_event(event_cid)


def main():
    wm = WorldModel(None, HIERARCHY)
    
    Thread(target=world_model_thread, args=(wm,), daemon=True).start()
    Thread(target=send_event, args=(wm, 3, "TestEvent"), daemon=True).start()
    
    result = wm.expect_event(
        "TestEvent",
        timeout=3,
    )
    print(result)
    
    time.sleep(10)
    
    
    
if __name__ == '__main__':
    main()