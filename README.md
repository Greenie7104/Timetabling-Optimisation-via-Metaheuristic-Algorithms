Timetabling Optimisation via Metaheuristic Algorithms

This repository contains the source code developed for my final-year project investigating the application of metaheuristic optimisation techniques to combinatorial optimisation problems focusing on university timetabling.

The project explores the behaviour of several metaheuristic algorithms on the Travelling Salesman Problem (TSP) as a benchmarking task, before adapting and applying Simulated Annealing to a constrained university timetabling problem using a penalty-based cost function.


## Repository Structure
PROJECT/
│
├── README.md
│
├── documents/
│   └── Project_Final_Report.pdf
│
├── product/
│   ├── Timetabling/
│   │   ├── __init__.py
│   │   ├── benchmarks.py
│   │   ├── benchmarks_constraints_suite.py
│   │   ├── constraints.py
│   │   ├── cost_function.py
│   │   ├── models.py
│   │   ├── neighbourhoods.py
│   │   └── simulated_annealing.py
│   │
│   └── TSP/
│       ├── TSPBruteForce.py
│       ├── TSPNearestNeighbour.py
│       ├── TSPSimulatedAnnealing.py
│       ├── TSPParticleSwarmOptimisation.py
│       └── TSPGeneticAlgorithm.py




The report provides:
- theoretical background
- problem formulation
- algorithmic design decisions
- experimental results
- discussion, limitations and future work

All experiments described in the report can be reproduced using the code in the `product/` directory.

---

## Requirements

### Software Requirements
- Python **3.9 or later**
- NumPy

### Tested Environment
- Python 3.13
- macOS
- NumPy (latest version)

The code should run on any modern operating system that supports Python.

---

## Installation

1. Clone or download the repository:
```bash
git clone https://gitlab.cim.rhul.ac.uk/zlac262/PROJECT.git
cd PROJECT

2. Install the required dependency
pip install numpy

3. Runnning the files
From the root directory of the repository, run:
python -m product.Timetabling.benchmarks

4. Travelling Salesman Benchmarks
each can be run independently from their own file
for example:
python product/TSP/TSPNearestNeighbour.py


## Installation

A short demonstration video showing the execution of the timetabling benchmarks is available at:

https://www.youtube.com/watch?v=TSVt5sy5Jy8
