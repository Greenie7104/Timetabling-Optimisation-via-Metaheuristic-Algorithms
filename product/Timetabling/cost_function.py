from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

from .models import Timetable, TimeslotID
from .constraints import hard_constraint_report, HardConstraintReport


@dataclass(frozen=True)
class CostWeights:
    #hard constraints
    hard_violation_penalty: int = 1_000_000  

    #soft constraints
    gap_penalty: int = 5            #per gap slot per cohort per day
    late_slot_penalty: int = 2      #per late event per cohort occurrence
    early_slot_penalty: int = 0     

    #timeslot structure 
    slots_per_day: int = 6          
    late_slot_threshold: int = 5    
    early_slot_threshold: int = 0   


def day_and_slot(timeslot: TimeslotID, slots_per_day: int) -> Tuple[int, int]:
    day = timeslot // slots_per_day
    slot = timeslot % slots_per_day
    return day, slot


def soft_penalty_gaps(tt: Timetable, w: CostWeights) -> int:
    cohort_day_slots: Dict[Tuple[int, int], List[int]] = {}
    for eid, (t, _r) in tt.assignment.items():
        ev = tt.events[eid]
        day, slot = day_and_slot(t, w.slots_per_day)
        for cohort_id in ev.cohort_ids:
            key = (cohort_id, day)
            cohort_day_slots.setdefault(key, []).append(slot)
    gaps = 0
    for key, slots in cohort_day_slots.items():
        if len(slots) <= 1:
            continue
        slots_sorted = sorted(set(slots))  #if duplicates exist, ignore
        #count missing integers between min and max
        min_s, max_s = slots_sorted[0], slots_sorted[-1]
        occupied = set(slots_sorted)
        for s in range(min_s, max_s + 1):
            if s not in occupied:
                gaps += 1
    return gaps * w.gap_penalty


def soft_penalty_early_late(tt: Timetable, w: CostWeights) -> int:
    """
    penalises events scheduled in early or late slots
    applied per cohort occurrence 
    """
    penalty = 0
    for eid, (t, _r) in tt.assignment.items():
        ev = tt.events[eid]
        _day, slot = day_and_slot(t, w.slots_per_day)
        cohort_multiplier = len(ev.cohort_ids) if ev.cohort_ids else 1
        if w.early_slot_penalty > 0 and slot < w.early_slot_threshold:
            penalty += w.early_slot_penalty * cohort_multiplier
        if w.late_slot_penalty > 0 and slot >= w.late_slot_threshold:
            penalty += w.late_slot_penalty * cohort_multiplier
    return penalty


def timetable_cost(
    tt: Timetable,
    weights: Optional[CostWeights] = None,
    return_breakdown: bool = False
):
    """
    total cost = (hard violations * huge penalty) + soft penalties.
    """
    w = weights or CostWeights()
    hard: HardConstraintReport = hard_constraint_report(tt)
    hard_cost = hard.total() * w.hard_violation_penalty
    soft_gaps = soft_penalty_gaps(tt, w)
    soft_early_late = soft_penalty_early_late(tt, w)
    total = hard_cost + soft_gaps + soft_early_late
    if return_breakdown:
        return {
            "total": total,
            "hard_cost": hard_cost,
            "hard_violations": hard.total(),
            "room_clashes": hard.room_clashes,
            "lecturer_clashes": hard.lecturer_clashes,
            "cohort_clashes": hard.cohort_clashes,
            "capacity_violations": hard.capacity_violations,
            "feature_violations": hard.feature_violations,
            "unassigned_events": hard.unassigned_events,
            "soft_gaps_cost": soft_gaps,
            "soft_early_late_cost": soft_early_late,
        }
    return total
