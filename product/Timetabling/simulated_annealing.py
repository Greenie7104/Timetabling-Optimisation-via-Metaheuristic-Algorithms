from __future__ import annotations
import math
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from .models import Timetable
from .cost_function import CostWeights, timetable_cost
from .neighbourhoods import MoveWeights, random_neighbour


@dataclass(frozen=True)
class SAParams:
    # Temperature schedule
    initial_temperature: float = 10_000.0
    cooling_rate: float = 0.995          # geometric cooling
    min_temperature: float = 1e-6
    # Iteration budget
    max_iterations: int = 50_000
    # Neighbourhood behaviour
    move_weights: MoveWeights = MoveWeights()
    prefer_feasible_rooms: bool = True
    # Reproducibility
    seed: Optional[int] = None
    # Logging
    log_every: int = 1_000              # set 0 to disable


def accept_probability(delta: float, temperature: float) -> float:
    """
    standard SA acceptance probability
    if delta <= 0 accept deterministically, else accept with exp(-delta / T)
    """
    if delta <= 0:
        return 1.0
    if temperature <= 0:
        return 0.0
    # guard against overflow when delta is huge
    x = -delta / temperature
    if x < -700:  # exp(-700) ~ 5e-305
        return 0.0
    return math.exp(x)


def simulated_annealing_timetabling(
    initial: Timetable,
    cost_weights: Optional[CostWeights] = None,
    params: SAParams = SAParams()
) -> Tuple[Timetable, Dict[str, List[float]]]:
    """
    Returns:
      best_timetable and history
    history contains:
      - "current_cost"
      - "best_cost"
      - "temperature"
      - "accepted"
    """
    rng = random.Random(params.seed)
    w = cost_weights or CostWeights()

    current = initial.copy()
    current_cost = timetable_cost(current, weights=w)
    best = current.copy()
    best_cost = current_cost

    T = params.initial_temperature

    history: Dict[str, List[float]] = {
        "current_cost": [],
        "best_cost": [],
        "temperature": [],
        "accepted": [],
    }

    for it in range(1, params.max_iterations + 1):
        neighbour = random_neighbour(
            current,
            rng=rng,
            weights=params.move_weights,
            prefer_feasible_rooms=params.prefer_feasible_rooms
        )
        neighbour_cost = timetable_cost(neighbour, weights=w)
        delta = neighbour_cost - current_cost

        p = accept_probability(delta, T)
        accepted = 1.0 if rng.random() < p else 0.0

        if accepted == 1.0:
            current = neighbour
            current_cost = neighbour_cost

            if current_cost < best_cost:
                best = current.copy()
                best_cost = current_cost

        # log
        if params.log_every and (it % params.log_every == 0 or it == 1):
            history["current_cost"].append(float(current_cost))
            history["best_cost"].append(float(best_cost))
            history["temperature"].append(float(T))
            history["accepted"].append(float(accepted))

        # cooling
        T *= params.cooling_rate
        if T < params.min_temperature:
            break

    return best, history
