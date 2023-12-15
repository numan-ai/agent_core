from dataclasses import dataclass, field
import enum
from threading import Event
from src.instance import Instance
from src.interfaces import (
    BaseHierarchy, 
    BaseKnowledgeBase,
)
from src.world_model.action_history import ActionHistory


class ExpectedEventStatus(enum.Enum):
    PENDING = enum.auto()
    RECEIVED = enum.auto()
    TIMEOUT = enum.auto()


@dataclass
class ExpectEvent:
    event_cid: str
    timeout: int
    status: ExpectedEventStatus = ExpectedEventStatus.PENDING
    event: Event = field(default_factory=Event)


class WorldModel:
    def __init__(self, kb: BaseKnowledgeBase, hierarchy: BaseHierarchy):
        self.kb = kb
        self.hierarchy = hierarchy
        self.event_stream: list[Instance] = []
        self.expect_events: list[ExpectEvent] = []
        self.action_history = ActionHistory()
        
    def expect_event(self, event_cid: str, timeout: int = 0) -> ExpectedEventStatus:
        exp_event = ExpectEvent(event_cid, timeout)
        print(f'Expecting event {event_cid} in {timeout} ticks')
        self.expect_events.append(exp_event)
        exp_event.event.wait()
        return exp_event.status
        
    def new_event(self, event_cid: str):
        print(f'New event: {event_cid}')
        self.event_stream.append(event_cid)
        
        for expect_event in self.expect_events:
            if expect_event.status != ExpectedEventStatus.PENDING:
                continue
            if expect_event.event_cid == event_cid:
                expect_event.status = ExpectedEventStatus.RECEIVED
                expect_event.event.set()
                print(f'Event {expect_event.event_cid} received')
    
    def clock_tick(self):
        print('tick')
        for expect_event in self.expect_events:
            if expect_event.status != ExpectedEventStatus.PENDING:
                continue
            expect_event.timeout -= 1
            if expect_event.timeout <= 0:
                expect_event.status = ExpectedEventStatus.TIMEOUT
                expect_event.event.set()
                print(f'Event {expect_event.event_cid} timed out')

