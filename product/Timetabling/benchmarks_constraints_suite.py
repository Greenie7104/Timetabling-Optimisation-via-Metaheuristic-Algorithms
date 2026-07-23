from __future__ import annotations

from Timetabling.models import Timetable, Event, Room
from Timetabling.constraints import hard_constraint_report, is_feasible
from Timetabling.cost_function import CostWeights, timetable_cost


def print_case(title: str, tt: Timetable, weights: CostWeights) -> None:
    print(f"\n=== {title} ===")
    rep = hard_constraint_report(tt)
    breakdown = timetable_cost(tt, weights=weights, return_breakdown=True)

    print("Feasible?:", is_feasible(tt))
    print("Assignments:", tt.assignment)
    print("Hard report:", rep)
    print("Cost breakdown:")
    for k, v in breakdown.items():
        print(f"  {k}: {v}")


def base_instance():
    """
    A small instance with:
      - 3 events
      - 2 rooms (one has projector, one doesn't)
      - 12 timeslots (2 days x 6 slots/day)
    """
    events = {
        0: Event(id=0, cohort_ids={1}, lecturer_id=10, size=35, required_features={"projector"}),
        1: Event(id=1, cohort_ids={1, 2}, lecturer_id=11, size=25, required_features=set()),
        2: Event(id=2, cohort_ids={2}, lecturer_id=10, size=45, required_features={"lab"}),  #needs lab and big
    }

    rooms = {
        0: Room(id=0, capacity=40, features={"projector"}),  #projector but only cap 40
        1: Room(id=1, capacity=30, features=set()),          #small, no features
        2: Room(id=2, capacity=60, features={"lab"}),        #lab, large
    }

    timeslots = list(range(12))  #2 days × 6 slots/day
    return events, rooms, timeslots


def case_all_feasible_with_soft(tt: Timetable):
    """
    Feasible timetable but intentionally includes:
        gaps for cohort
        a late slot event 
    """
    tt.place_event(0, 0, 0)   
    tt.place_event(1, 4, 1)   
    tt.place_event(2, 11, 2)  


def case_room_clash(tt: Timetable):
    tt.place_event(0, 0, 0)
    tt.place_event(1, 0, 0)  #clash same room/time
    tt.place_event(2, 6, 2)  


def case_lecturer_clash(tt: Timetable):
    tt.place_event(0, 1, 0)
    tt.place_event(2, 1, 2)  #same timeslot, same lecturer 
    tt.place_event(1, 7, 1)


def case_cohort_clash(tt: Timetable):
    tt.place_event(0, 2, 0)
    tt.place_event(1, 2, 1)  #cohort 1 clash at timeslot 2
    tt.place_event(2, 8, 2)


def case_capacity_violation(tt: Timetable):
    tt.place_event(0, 0, 0)
    tt.place_event(1, 1, 1)
    tt.place_event(2, 2, 0)  #cap violation 


def case_feature_violation(tt: Timetable):
    """
    Put projector-required event in non-projector room 
    """
    tt.place_event(0, 0, 1)  #feature violation
    tt.place_event(1, 1, 1)
    tt.place_event(2, 2, 2)


def case_unassigned_event(tt: Timetable):
    """
    Leave one event unassigned to trigger unassigned_events
    """
    tt.place_event(0, 0, 0)
    tt.place_event(1, 1, 1)
    
def run_suite():
    events, rooms, timeslots = base_instance()
    weights = CostWeights(
        slots_per_day=6,
        late_slot_threshold=5,    
        hard_violation_penalty=1_000_000,
        gap_penalty=5,
        late_slot_penalty=2,
    )

    #case A: feasible but with soft penalties
    tt = Timetable.empty(events, rooms, timeslots)
    case_all_feasible_with_soft(tt)
    print_case("CASE A: Feasible timetable (soft penalties only)", tt, weights)

    #case B: room clash
    tt = Timetable.empty(events, rooms, timeslots)
    case_room_clash(tt)
    print_case("CASE B: Room clash", tt, weights)

    #case C: lecturer clash
    tt = Timetable.empty(events, rooms, timeslots)
    case_lecturer_clash(tt)
    print_case("CASE C: Lecturer clash", tt, weights)

    #case D: cohort clash
    tt = Timetable.empty(events, rooms, timeslots)
    case_cohort_clash(tt)
    print_case("CASE D: Cohort clash", tt, weights)

    #case E: capacity violation
    tt = Timetable.empty(events, rooms, timeslots)
    case_capacity_violation(tt)
    print_case("CASE E: Capacity violation", tt, weights)

    #case F: feature violation
    tt = Timetable.empty(events, rooms, timeslots)
    case_feature_violation(tt)
    print_case("CASE F: Feature violation", tt, weights)

    #case G: unassigned event
    tt = Timetable.empty(events, rooms, timeslots)
    case_unassigned_event(tt)
    print_case("CASE G: Unassigned event", tt, weights)


if __name__ == "__main__":
    run_suite()
