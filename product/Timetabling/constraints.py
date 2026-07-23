from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional

from .models import Timetable, EventID, RoomID, TimeslotID


@dataclass
class HardConstraintReport:
    """Counts of hard-constraint violations."""
    room_clashes: int = 0
    lecturer_clashes: int = 0
    cohort_clashes: int = 0
    capacity_violations: int = 0
    feature_violations: int = 0
    unassigned_events: int = 0

    def total(self) -> int:
        return (
            self.room_clashes
            + self.lecturer_clashes
            + self.cohort_clashes
            + self.capacity_violations
            + self.feature_violations
            + self.unassigned_events
        )


def _count_pair_clashes(pairs: List[Tuple[int, int]]) -> int:
    """
    given a list of (key1, key2) pairs (e.g. (timeslot, room)),
    count how many clashes occur

    if a (timeslot, room) appears k times, that contributes (k-1) violations
    """
    counts: Dict[Tuple[int, int], int] = {}
    for p in pairs:
        counts[p] = counts.get(p, 0) + 1
    return sum(max(0, c - 1) for c in counts.values())


def hard_constraint_report(tt: Timetable) -> HardConstraintReport:
    """
    computes hard-constraint violations from the current timetable assignment
    """
    report = HardConstraintReport()

    #unassigned events
    report.unassigned_events = len(tt.events) - len(tt.assignment)

    #if nothing assigned, early return
    if not tt.assignment:
        return report

    #room clashes: two events in the same (timeslot, room)
    room_pairs = [(t, r) for (t, r) in tt.assignment.values()]
    report.room_clashes = _count_pair_clashes(room_pairs)

    #lecturer clashes: same lecturer in same timeslot
    lecturer_pairs: List[Tuple[int, int]] = []
    for eid, (t, _r) in tt.assignment.items():
        lecturer_pairs.append((t, tt.events[eid].lecturer_id))
    report.lecturer_clashes = _count_pair_clashes(lecturer_pairs)

    #cohort clashes: any cohort with 2+ events in the same timeslot
    cohort_pairs: List[Tuple[int, int]] = []
    for eid, (t, _r) in tt.assignment.items():
        ev = tt.events[eid]
        for cohort_id in ev.cohort_ids:
            cohort_pairs.append((t, cohort_id))
    report.cohort_clashes = _count_pair_clashes(cohort_pairs)

    #capacity and feature violations
    for eid, (_t, room_id) in tt.assignment.items():
        ev = tt.events[eid]
        room = tt.rooms[room_id]
        if room.capacity < ev.size:
            report.capacity_violations += 1
        if hasattr(ev, "required_features") and hasattr(room, "features"):
            if not ev.required_features.issubset(room.features):
                report.feature_violations += 1
    return report


def is_feasible(tt: Timetable) -> bool:
    return hard_constraint_report(tt).total() == 0
