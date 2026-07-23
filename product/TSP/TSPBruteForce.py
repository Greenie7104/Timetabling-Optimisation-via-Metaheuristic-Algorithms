import itertools
import math
import time
import random



# Distance Functions
def euclidean_distance(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)


def total_distance(route, dist_matrix):
    #Returns the total length of the TSP cycle for a given route.
    n = len(route)
    return sum(dist_matrix[route[i]][route[(i + 1) % n]] for i in range(n))



# Brute-Force TSP Solver
def brute_force_tsp(coords):
    #Compute the optimal TSP route using brute-force search.
    #Fixes city 0 to reduce duplicate routes by symmetry.
    
    n = len(coords)

    # Build distance matrix
    dist_matrix = [
        [euclidean_distance(coords[i], coords[j]) for j in range(n)]
        for i in range(n)
    ]

    best_route = None
    best_distance = float("inf")

    # Fix the first city to eliminate rotational symmetry
    for perm in itertools.permutations(range(1, n)):
        route = (0,) + perm
        d = total_distance(route, dist_matrix)

        if d < best_distance:
            best_distance = d
            best_route = route

    return best_route, best_distance


# Benchmarking Function

def run_benchmarks():
    #Benchmark brute-force TSP for n = 6..10 cities.
    print("\n--- Brute-Force TSP Benchmark Results ---\n")

    for n in [6, 7, 8, 9, 10]:
        coords = [(random.random(), random.random()) for _ in range(n)]

        start = time.time()
        best_route, best_distance = brute_force_tsp(coords)
        end = time.time()

        print(f"{n} cities:")
        print(f"  Best route:     {best_route}")
        print(f"  Best distance:  {best_distance:.4f}")
        print(f"  Runtime:        {end - start:.4f} seconds\n")



# Main Execution

if __name__ == "__main__":
    run_benchmarks()
