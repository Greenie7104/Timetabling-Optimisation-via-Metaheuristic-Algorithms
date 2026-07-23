import math
import random
import time


def euclidean_distance(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)


def nearest_neighbour_tsp(coords, start=0):
    n = len(coords)
    visited = [False] * n
    visited[start] = True
    route = [start]

    # Precompute distances
    dist_matrix = [
        [euclidean_distance(coords[i], coords[j]) for j in range(n)]
        for i in range(n)
    ]

    current = start

    for _ in range(n - 1):
        nearest = None
        nearest_dist = float("inf")

        for city in range(n):
            if not visited[city]:
                d = dist_matrix[current][city]
                if d < nearest_dist:
                    nearest = city
                    nearest_dist = d

        route.append(nearest)
        visited[nearest] = True
        current = nearest

    return route, total_route_length(route, dist_matrix)


def total_route_length(route, dist_matrix):
    d = sum(dist_matrix[route[i]][route[(i + 1) % len(route)]] for i in range(len(route)))
    return d


def run_nn_benchmarks():
    print("\n--- Nearest Neighbour (NN) TSP Benchmark ---\n")

    for n in [20, 50, 100, 200]:
        coords = [(random.random(), random.random()) for _ in range(n)]

        start = time.time()
        route, dist = nearest_neighbour_tsp(coords)
        end = time.time()

        print(f"{n} cities:")
        print(f"  NN distance:   {dist:.4f}")
        print(f"  Runtime:       {end - start:.4f} seconds\n")

if __name__ == "__main__":
    run_nn_benchmarks()

