from __future__ import annotations
import random
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple
from .models import Timetable, EventID, RoomID, TimeslotID


@dataclass(frozen=True)
class MoveWeights:
    """probabilities for selecting each move type"""
    move_timeslot: float = 0.50
    move_room: float = 0.30
    swap_timeslots: float = 0.20


def choose_weighted(rng: random.Random, weights: MoveWeights) -> str:
    r = rng.random()
    if r < weights.move_timeslot:
        return "move_timeslot"
    r -= weights.move_timeslot
    if r < weights.move_room:
        return "move_room"
    return "swap_timeslots"


def random_event_id(rng: random.Random, tt: Timetable) -> EventID:
    return rng.choice(list(tt.assignment.keys()))


def random_room_id(
    rng: random.Random,
    tt: Timetable,
    event_id: EventID,
    prefer_feasible: bool = True
) -> RoomID:
    room_ids = list(tt.rooms.keys())
    if prefer_feasible:
        feasible = [rid for rid in room_ids if tt.room_feasible_for_event(event_id, rid)]
        if feasible:
            return rng.choice(feasible)
    return rng.choice(room_ids)


def random_timeslot_id(rng: random.Random, tt: Timetable) -> TimeslotID:
    return rng.choice(tt.timeslots)



# Neighbourhood moves

def move_event_timeslot(
    tt: Timetable,
    event_id: EventID,
    new_timeslot: TimeslotID
) -> Timetable:
    """return a neighbour timetable where one event is moved to a new timeslot"""
    neighbour = tt.copy()
    old_t, old_r = neighbour.assignment[event_id]
    if new_timeslot == old_t:
        return neighbour
    neighbour.place_event(event_id, new_timeslot, old_r)
    return neighbour


def move_event_room(
    tt: Timetable,
    event_id: EventID,
    new_room: RoomID
) -> Timetable:
    """return a neighbour timetable where one event is moved to a new room"""
    neighbour = tt.copy()
    old_t, old_r = neighbour.assignment[event_id]
    if new_room == old_r:
        return neighbour
    neighbour.place_event(event_id, old_t, new_room)
    return neighbour


def swap_event_timeslots(
    tt: Timetable,
    event_a: EventID,
    event_b: EventID
) -> Timetable:
    """return a neighbour timetable where two events swap timeslots"""
    if event_a == event_b:
        return tt.copy()

    neighbour = tt.copy()

    t_a, r_a = neighbour.assignment[event_a]
    t_b, r_b = neighbour.assignment[event_b]

    if t_a == t_b:
        return neighbour

    #use place_event which will remove/re-add safely
    neighbour.place_event(event_a, t_b, r_a)
    neighbour.place_event(event_b, t_a, r_b)
    return neighbour


def random_neighbour(
    tt: Timetable,
    rng: Optional[random.Random] = None,
    weights: MoveWeights = MoveWeights(),
    prefer_feasible_rooms: bool = True
) -> Timetable:

    if rng is None:
        rng = random.Random()

    #need at least 1 assigned event to move and at least 2 to swap
    if not tt.assignment:
        return tt.copy()

    move_type = choose_weighted(rng, weights)

    if move_type == "move_timeslot":
        e = random_event_id(rng, tt)
        new_t = random_timeslot_id(rng, tt)
        return move_event_timeslot(tt, e, new_t)

    if move_type == "move_room":
        e = random_event_id(rng, tt)
        new_r = random_room_id(rng, tt, e, prefer_feasible=prefer_feasible_rooms)
        return move_event_room(tt, e, new_r)

    if len(tt.assignment) < 2:
        #fall back to a single event move
        e = random_event_id(rng, tt)
        new_t = random_timeslot_id(rng, tt)
        return move_event_timeslot(tt, e, new_t)

    e1, e2 = rng.sample(list(tt.assignment.keys()), 2)
    return swap_event_timeslots(tt, e1, e2)
