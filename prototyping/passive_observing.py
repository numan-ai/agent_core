"""
This will require building 2d pyramid of pattern matching in order to detect
  objects. 
We can cheat by skipping the algo and coming up with how the answer
  will look like directly.
The result is a pyramidally segmented 2d plane. Each segment is a detected object.
Interestingly not everything catches our attention, somehow people only see 
higher level objects, omitting what they are composed of.
What about the boundaries for the objects? Do we want to be precise?
We can make every layer as a square, and the shape will be the outer part of 
  all the lowest level layers.
"""
from typing import Self
from dataclasses import dataclass, field


@dataclass
class Segment:
    concept: str
    # rect: Rect
    sub_segments: list[Self] = field(default_factory=list)


segments = [
    Segment("CircuitLED", [
        Segment("CircuitLEDBulb"),
        Segment("CircuitInputPin"),
    ]),
]
