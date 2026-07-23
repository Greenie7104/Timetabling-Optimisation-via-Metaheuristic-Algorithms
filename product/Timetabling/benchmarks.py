from __future__ import annotations
from typing import Dict, Any
from .models import Timetable
from .constraints import hard_constraint_report, is_feasible
from .cost_function import CostWeights, timetable_cost
from .simulated_annealing import SAParams, simulated_annealing_timetabling
from .benchmarks_constraints_suite import (
    base_instance,
    case_all_feasible_with_soft,
    case_room_clash,
    case_lecturer_clash,
    case_cohort_clash,
    case_capacity_violation,
    case_feature_violation,
    case_unassigned_event,
)

#printing helpers
def _print_breakdown(breakdown: Dict[str, Any]) -> None:
    print("Cost breakdown:")
    for k, v in breakdown.items():
        print(f"  {k}: {v}")


def print_case(title: str, tt: Timetable, weights: CostWeights) -> Dict[str, Any]:
    print(f"\n=== {title} ===")
    rep = hard_constraint_report(tt)
    breakdown = timetable_cost(tt, weights=weights, return_breakdown=True)
    print("Feasible?:", is_feasible(tt))
    print("Assignments:", tt.assignment)
    print("Hard report:", rep)
    _print_breakdown(breakdown)
    return breakdown


def print_sa_history_summary(history: Dict[str, list]) -> None:
    """
    Your SA returns history as dict-of-lists:
      history["best_cost"], history["temperature"], etc.
    """
    n = len(history.get("best_cost", []))
    print("\n--- SA HISTORY SUMMARY ---")
    print("Logged points:", n)
    if n == 0:
        return
    print("First best_cost:", history["best_cost"][0])
    print("Last  best_cost:", history["best_cost"][-1])
    print("First temperature:", history["temperature"][0])
    print("Last  temperature:", history["temperature"][-1])



#static validation on Constraint Suite
def run_constraint_suite() -> None:
    print("\n================ CONSTRAINT SUITE (A-G) ================\n")

    events, rooms, timeslots = base_instance()
    weights = CostWeights(
        slots_per_day=6,
        late_slot_threshold=5,
        hard_violation_penalty=1_000_000,
        gap_penalty=5,
        late_slot_penalty=2,
    )

    tt = Timetable.empty(events, rooms, timeslots)
    case_all_feasible_with_soft(tt)
    print_case("CASE A: Feasible timetable (soft penalties only)", tt, weights)

    tt = Timetable.empty(events, rooms, timeslots)
    case_room_clash(tt)
    print_case("CASE B: Room clash", tt, weights)

    tt = Timetable.empty(events, rooms, timeslots)
    case_lecturer_clash(tt)
    print_case("CASE C: Lecturer clash", tt, weights)

    tt = Timetable.empty(events, rooms, timeslots)
    case_cohort_clash(tt)
    print_case("CASE D: Cohort clash", tt, weights)

    tt = Timetable.empty(events, rooms, timeslots)
    case_capacity_violation(tt)
    print_case("CASE E: Capacity violation", tt, weights)

    tt = Timetable.empty(events, rooms, timeslots)
    case_feature_violation(tt)
    print_case("CASE F: Feature violation", tt, weights)

    tt = Timetable.empty(events, rooms, timeslots)
    case_unassigned_event(tt)
    print_case("CASE G: Unassigned event", tt, weights)



#SA on feasible timetable (reduces soft penalties)

def run_sa_soft_only() -> None:
    print("\n================ SA: SOFT OPTIMISATION ================\n")

    events, rooms, timeslots = base_instance()
    weights = CostWeights(
        slots_per_day=6,
        late_slot_threshold=5,
        hard_violation_penalty=1_000_000,
        gap_penalty=5,
        late_slot_penalty=2,
    )

    #starts feasible but with soft penalties
    tt = Timetable.empty(events, rooms, timeslots)
    case_all_feasible_with_soft(tt)

    print_case("--- INITIAL TIMETABLE ---", tt, weights)

    params = SAParams(
        initial_temperature=10_000.0,
        cooling_rate=0.995,
        min_temperature=1e-5,
        max_iterations=5_000,   
        seed=42
    )

    best_tt, history = simulated_annealing_timetabling(tt, cost_weights=weights, params=params)

    print_case("--- AFTER SIMULATED ANNEALING ---", best_tt, weights)
    print_sa_history_summary(history)



#SA repairing hard constraints (starts infeasible)

def run_sa_hard_repair() -> None:
    print("\n================ SA: HARD CONSTRAINT REPAIR ================\n")

    events, rooms, timeslots = base_instance()
    weights = CostWeights(
        slots_per_day=6,
        late_slot_threshold=5,
        hard_violation_penalty=1_000_000,
        gap_penalty=5,
        late_slot_penalty=2,
    )

    #Start infeasible 
    tt = Timetable.empty(events, rooms, timeslots)
    case_room_clash(tt)

    before = print_case("--- BEFORE SA (INFEASIBLE) ---", tt, weights)

    params = SAParams(
        initial_temperature=20_000.0,
        cooling_rate=0.995,
        min_temperature=1e-5,
        max_iterations=10_000,  
        seed=123
    )

    best_tt, history = simulated_annealing_timetabling(tt, cost_weights=weights, params=params)

    after = print_case("--- AFTER SA (POST-REPAIR) ---", best_tt, weights)

    print("\n--- REPAIR SUMMARY ---")
    print("Hard violations before:", before["hard_violations"])
    print("Hard violations after: ", after["hard_violations"])
    print("Hard cost before:", before["hard_cost"])
    print("Hard cost after: ", after["hard_cost"])
    print_sa_history_summary(history)

#main
def main() -> None:
    run_constraint_suite()
    run_sa_soft_only()
    run_sa_hard_repair()


if __name__ == "__main__":
    main()
