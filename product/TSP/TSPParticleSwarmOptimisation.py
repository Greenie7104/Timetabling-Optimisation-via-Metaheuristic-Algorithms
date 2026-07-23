import random
import math
import time


def euclidean_distance(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def total_distance(route, dist_matrix):
    return sum(
        dist_matrix[route[i]][route[(i + 1) % len(route)]]
        for i in range(len(route))
    )

def generate_swaps(route_a, route_b):
    #Generates swaps required to turn route_a into route_b
    a = route_a[:]
    swaps = []
    pos = {city: i for i, city in enumerate(a)}
    for i in range(len(a)):
        if a[i] != route_b[i]:
            j = pos[route_b[i]]
            swaps.append((i, j))
            a[i], a[j] = a[j], a[i]
            pos[a[j]] = j
            pos[a[i]] = i
    return swaps

def apply_swaps(route, swaps):
    #Applies a list of swap operations to a route
    r = route[:]
    for i, j in swaps:
        r[i], r[j] = r[j], r[i]
    return r

def pso_tsp(coords, swarm_size=30, iterations=500):
    n = len(coords)

    dist_matrix = [
        [euclidean_distance(coords[i], coords[j]) for j in range(n)]
        for i in range(n)
    ]

    # Initialises swarm with random permutations
    swarm = []
    for _ in range(swarm_size):
        route = list(range(n))
        random.shuffle(route)
        cost = total_distance(route, dist_matrix)
        swarm.append({
            "position": route,
            "pbest": route[:],
            "pbest_cost": cost,
            "velocity": []
        })

    # Determines global best
    gbest = min(swarm, key=lambda p: p["pbest_cost"])["pbest"]
    gbest_cost = min(p["pbest_cost"] for p in swarm)

    for _ in range(iterations):
        for particle in swarm:
            # Generate swap sequences
            swaps_pbest = generate_swaps(particle["position"], particle["pbest"])
            swaps_gbest = generate_swaps(particle["position"], gbest)
            # Random portions
            vel_pbest = swaps_pbest[: int(0.1 * len(swaps_pbest))]
            vel_gbest = swaps_gbest[: int(0.1 * len(swaps_gbest))]
            # Update velocity and apply moves
            velocity = vel_pbest + vel_gbest
            particle["position"] = apply_swaps(particle["position"], velocity)
            # Evaluate
            cost = total_distance(particle["position"], dist_matrix)
            # Personal best update
            if cost < particle["pbest_cost"]:
                particle["pbest"] = particle["position"][:]
                particle["pbest_cost"] = cost
                # Global best update
                if cost < gbest_cost:
                    gbest = particle["position"][:]
                    gbest_cost = cost

    return gbest, gbest_cost

def run_pso_benchmarks():
    print("\n--- PSO TSP Benchmark ---\n")

    for n in [20, 50, 100, 200]:
        coords = [(random.random(), random.random()) for _ in range(n)]
        start = time.time()
        best_route, best_cost = pso_tsp(coords, swarm_size=30, iterations=500)
        end = time.time()
        print(f"{n} cities:")
        print(f"  PSO distance: {best_cost:.4f}")
        print(f"  Runtime:      {end - start:.4f} seconds\n")

if __name__ == "__main__":
    run_pso_benchmarks()
