from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional
import random


EventID = int
RoomID = int
TimeslotID = int


@dataclass(frozen=True)
class Event:
    """One teaching event that must be scheduled."""
    id: EventID
    cohort_ids: Set[int]          #student groups attending 
    lecturer_id: int
    size: int                     #number of students
    required_features: Set[str]   #for example: lab, projector etc


@dataclass(frozen=True)
class Room:
    id: RoomID
    capacity: int
    features: Set[str]            


@dataclass
class Timetable:
    """
    core representation used by optimisation:
      assignment[event_id] = (timeslot_id, room_id)

    also maintains fast indices for clashes:
      room_occupancy[(timeslot_id, room_id)] = event_id
      lecturer_occupancy[(timeslot_id, lecturer_id)] = event_id
      cohort_occupancy[(timeslot_id, cohort_id)] = set(event_ids)
    """
    events: Dict[EventID, Event]
    rooms: Dict[RoomID, Room]
    timeslots: List[TimeslotID]

    assignment: Dict[EventID, Tuple[TimeslotID, RoomID]]

    room_occupancy: Dict[Tuple[TimeslotID, RoomID], EventID]
    lecturer_occupancy: Dict[Tuple[TimeslotID, int], EventID]
    cohort_occupancy: Dict[Tuple[TimeslotID, int], Set[EventID]]

    @staticmethod
    def empty(events: Dict[EventID, Event],
              rooms: Dict[RoomID, Room],
              timeslots: List[TimeslotID]) -> "Timetable":
        return Timetable(
            events=events,
            rooms=rooms,
            timeslots=timeslots,
            assignment={},
            room_occupancy={},
            lecturer_occupancy={},
            cohort_occupancy={}
        )

    def copy(self) -> "Timetable":
        new_tt = Timetable.empty(self.events, self.rooms, self.timeslots)
        new_tt.assignment = dict(self.assignment)
        new_tt.room_occupancy = dict(self.room_occupancy)
        new_tt.lecturer_occupancy = dict(self.lecturer_occupancy)
        new_tt.cohort_occupancy = {
            k: set(v) for k, v in self.cohort_occupancy.items()
        }
        return new_tt


    def place_event(self, event_id: EventID, timeslot: TimeslotID, room_id: RoomID) -> None:
        """
        assign event and update indices
        if event was already placed, it is removed first
        """
        if event_id in self.assignment:
            self.remove_event(event_id)

        ev = self.events[event_id]
        self.assignment[event_id] = (timeslot, room_id)

        #update room occupancy
        self.room_occupancy[(timeslot, room_id)] = event_id

        #update lecturer occupancy
        self.lecturer_occupancy[(timeslot, ev.lecturer_id)] = event_id

        #update cohort occupancy
        for cohort_id in ev.cohort_ids:
            key = (timeslot, cohort_id)
            if key not in self.cohort_occupancy:
                self.cohort_occupancy[key] = set()
            self.cohort_occupancy[key].add(event_id)

    def remove_event(self, event_id: EventID) -> None:
        """remove event assignment and update indices"""
        timeslot, room_id = self.assignment.pop(event_id)
        ev = self.events[event_id]
        self.room_occupancy.pop((timeslot, room_id), None)
        self.lecturer_occupancy.pop((timeslot, ev.lecturer_id), None)
        for cohort_id in ev.cohort_ids:
            key = (timeslot, cohort_id)
            s = self.cohort_occupancy.get(key)
            if s is not None:
                s.discard(event_id)
                if not s:
                    self.cohort_occupancy.pop(key, None)


    def room_conflict(self, timeslot: TimeslotID, room_id: RoomID) -> bool:
        return (timeslot, room_id) in self.room_occupancy

    def lecturer_conflict(self, timeslot: TimeslotID, lecturer_id: int) -> bool:
        return (timeslot, lecturer_id) in self.lecturer_occupancy

    def cohort_conflict(self, timeslot: TimeslotID, cohort_id: int) -> bool:
        #conflict if there is already more than one event for that cohort in that timeslot
        return (timeslot, cohort_id) in self.cohort_occupancy and len(self.cohort_occupancy[(timeslot, cohort_id)]) > 0

    def room_feasible_for_event(self, event_id: EventID, room_id: RoomID) -> bool:
        ev = self.events[event_id]
        room = self.rooms[room_id]
        if room.capacity < ev.size:
            return False
        if not ev.required_features.issubset(room.features):
            return False
        return True


    #initial solution helpers
    def random_initialise(self, seed: Optional[int] = None) -> None:
        """
        creates an initial timetable by randomly placing all events
        this is fine for SA if your cost function heavily penalises hard constraint violations
        """
        rng = random.Random(seed)
        event_ids = list(self.events.keys())
        rng.shuffle(event_ids)

        room_ids = list(self.rooms.keys())

        for eid in event_ids:
            #picks a feasible room if possible, otherwise any room 
            feasible_rooms = [rid for rid in room_ids if self.room_feasible_for_event(eid, rid)]
            chosen_room = rng.choice(feasible_rooms) if feasible_rooms else rng.choice(room_ids)
            chosen_timeslot = rng.choice(self.timeslots)
            self.place_event(eid, chosen_timeslot, chosen_room)

    def event_assignment(self, event_id: EventID) -> Tuple[TimeslotID, RoomID]:
        return self.assignment[event_id]
    


if __name__ == "__main__":
    events = {
        0: Event(0, cohort_ids={1}, lecturer_id=10, size=40, required_features={"projector"}),
        1: Event(1, cohort_ids={1,2}, lecturer_id=11, size=25, required_features=set()),
        2: Event(2, cohort_ids={2}, lecturer_id=10, size=35, required_features={"lab"}),
    }

    rooms = {
        0: Room(0, capacity=50, features={"projector"}),
        1: Room(1, capacity=30, features=set()),
        2: Room(2, capacity=40, features={"lab"}),
    }

    timeslots = list(range(20)) 

    tt = Timetable.empty(events, rooms, timeslots)
    tt.random_initialise(seed=42)

    for eid, (t, r) in tt.assignment.items():
        print(f"Event {eid} -> timeslot {t}, room {r}")

