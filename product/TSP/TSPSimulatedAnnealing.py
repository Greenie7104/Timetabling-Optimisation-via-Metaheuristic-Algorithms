import math
import random
import time


def euclidean_distance(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)


def total_distance(route, dist_matrix):
    return sum(
        dist_matrix[route[i]][route[(i + 1) % len(route)]]
        for i in range(len(route))
    )

def two_opt_swap(route):
    n = len(route)
    i, j = sorted(random.sample(range(n), 2))
    new_route = route[:i] + route[i:j][::-1] + route[j:]
    return new_route


def simulated_annealing(coords, T_start=1.0, alpha=0.995, max_iter=50000):
    n = len(coords)

    # Precompute distances
    dist_matrix = [
        [euclidean_distance(coords[i], coords[j]) for j in range(n)]
        for i in range(n)
    ]

    # Initial route
    current = list(range(n))
    random.shuffle(current)

    current_cost = total_distance(current, dist_matrix)
    best_route = current[:]
    best_cost = current_cost

    T = T_start

    for _ in range(max_iter):
        new_route = two_opt_swap(current)
        new_cost = total_distance(new_route, dist_matrix)
        delta = new_cost - current_cost

        # Acceptance
        if delta < 0 or random.random() < math.exp(-delta / T):
            current = new_route
            current_cost = new_cost

            if current_cost < best_cost:
                best_cost = current_cost
                best_route = current[:]

        # Cooling
        T *= alpha
        if T < 1e-6:
            break

    return best_route, best_cost

def run_sa_benchmarks():
    print("\n--- Simulated Annealing (SA) TSP Benchmark ---\n")

    for n in [20, 50, 100, 200]:
        # Generates random coordinates
        coords = [(random.random(), random.random()) for _ in range(n)]

        start = time.time()
        best_route, best_distance = simulated_annealing(
            coords,
            T_start=5.0,
            alpha=0.9992,
            max_iter=100000
        )
        end = time.time()

        print(f"{n} cities:")
        print(f"  SA distance:  {best_distance:.4f}")
        print(f"  Runtime:      {end - start:.4f} seconds\n")

if __name__ == "__main__":
    run_sa_benchmarks()

