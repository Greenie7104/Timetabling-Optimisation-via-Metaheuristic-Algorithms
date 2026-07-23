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


# -------- Genetic Operators -------- #

def ordered_crossover(parent1, parent2):
    """OX crossover for permutations."""
    n = len(parent1)
    start, end = sorted(random.sample(range(n), 2))

    child = [None] * n
    child[start:end] = parent1[start:end]

    pointer = end
    for city in parent2:
        if city not in child:
            if pointer == n:
                pointer = 0
            child[pointer] = city
            pointer += 1
    return child


def mutate(route, rate=0.05):
    """Swap mutation."""
    r = route[:]
    for _ in range(int(len(route) * rate)):
        i, j = random.sample(range(len(route)), 2)
        r[i], r[j] = r[j], r[i]
    return r


# -------- Main GA Algorithm -------- #

def ga_tsp(coords, population_size=50, generations=300):
    n = len(coords)

    dist_matrix = [
        [euclidean_distance(coords[i], coords[j]) for j in range(n)]
        for i in range(n)
    ]

    # Initial population: random tours
    population = []
    for _ in range(population_size):
        route = list(range(n))
        random.shuffle(route)
        population.append(route)

    for _ in range(generations):
        # Evaluate fitness
        scored_pop = sorted(
            population, 
            key=lambda r: total_distance(r, dist_matrix)
        )

        # Selection: take top half
        parents = scored_pop[: population_size // 2]

        # Produce children through crossover
        children = []
        while len(children) < population_size:
            p1, p2 = random.sample(parents, 2)
            child = ordered_crossover(p1, p2)
            child = mutate(child, rate=0.02)
            children.append(child)

        population = children

    best = min(population, key=lambda r: total_distance(r, dist_matrix))
    return best, total_distance(best, dist_matrix)


def run_ga_benchmarks():
    print("\n--- GA TSP Benchmark ---\n")

    for n in [20, 50, 100, 200]:
        coords = [(random.random(), random.random()) for _ in range(n)]

        start = time.time()
        best_route, best_cost = ga_tsp(coords, population_size=80, generations=400)
        end = time.time()

        print(f"{n} cities:")
        print(f"  GA distance:  {best_cost:.4f}")
        print(f"  Runtime:      {end - start:.4f} seconds\n")

if __name__ == "__main__":
    run_ga_benchmarks()