import random as rand
import copy
from operator import itemgetter
import time as time


def readfile(filename):
    num_vertices = 0
    num_connections = 0
    vertices = {}

    fp = open(filename, 'r')
    for line in fp:
        if line[0] == 'c':
            continue
        elif line[0] == 'p':
            splits = line.split(' ')
            num_vertices = splits[2]
            num_connections = splits[3]
        elif line[0] == 'e':
            splits = line.replace('\n', '').split(' ')
            vertex1 = int(splits[1])
            vertex2 = int(splits[2])
            if vertex1 not in vertices:
                vertices[vertex1] = []
            if vertex2 not in vertices:
                vertices[vertex2] = []

            vertices[vertex1].append(vertex2)
            vertices[vertex2].append(vertex1)
    fp.close()

    return vertices


def checksolution(solution, vertices):
    num_of_errors = 0

    for key in vertices:
        for neighbor in vertices[key]:
            if solution["vertex_color"][key] == solution["vertex_color"][neighbor]:
                num_of_errors += 1
    return num_of_errors/2


def get_two_vertex_cost(solution, vertex1, vertex2):
    num_of_errors = 0
    for neighbor in vertices[vertex1]:
        if solution["vertex_color"][neighbor] == solution["vertex_color"][vertex1]:
            num_of_errors += 1
    for neighbor in vertices[vertex2]:
        if solution["vertex_color"][neighbor] == solution["vertex_color"][vertex2]:
            num_of_errors += 1
    return num_of_errors


def swapcolors(solution, vertex1, vertex2):
    total_cost = solution["cost"]

    color1 = solution["vertex_color"][vertex1]
    color2 = solution["vertex_color"][vertex2]

    vertex_cost_before = get_two_vertex_cost(solution, vertex1, vertex2)

    solution["vertex_color"][vertex1] = color2
    solution["vertex_color"][vertex2] = color1

    solution["elements"][color1].remove(vertex1)
    solution["elements"][color1].append(vertex2)
    solution["elements"][color2].remove(vertex2)
    solution["elements"][color2].append(vertex1)

    vertex_cost_after = get_two_vertex_cost(solution, vertex1, vertex2)  # swapped colors
    solution["cost"] = total_cost - vertex_cost_before + vertex_cost_after


# unused at the moment
def swapcolors_groups(solution, vertex1, vertex2, group1, group2):
    total_cost = solution["cost"]
    vertex_cost_before = get_two_vertex_cost(solution, vertex1, vertex2)
    solution["elements"][group1].remove(vertex1)
    solution["elements"][group1].append(vertex2)
    solution["elements"][group2].remove(vertex2)
    solution["elements"][group2].append(vertex1)
    vertex_cost_after = get_two_vertex_cost(solution, vertex1, vertex2)  # swapped colors
    solution["cost"] = total_cost - vertex_cost_before + vertex_cost_after



def vdls(solution, vertices):
    max_iterations = 100
    current_iteration = 0
    elapsed = 0
    while True:
        #print(current_iteration, "/", max_iterations)
        start = time.time()
        #print("Iteration:", current_iteration, "out of", max_iterations, "with best cost", solution["cost"], "in time", elapsed)
        changed = False

        keys = list(vertices.keys())
        rand.shuffle(keys)
        for key in keys:  # 50ms per run
            best_swap = [0] * 3  # score vertex1 vertex2
            best_swap[0] = solution["cost"]
            swapped = False
            for neighbor in vertices[key]:
                swapcolors(solution, key, neighbor)
                num_of_errors = solution["cost"]  # checksolution(solution, vertices)
                if num_of_errors < best_swap[0]:
                    best_swap[0] = num_of_errors
                    best_swap[1] = key
                    best_swap[2] = neighbor
                    swapped = True
                    changed = True
                swapcolors(solution, key, neighbor)
            if swapped:
                swapcolors(solution, best_swap[1], best_swap[2])

        if not changed:
            current_iteration += 1
        else:
            current_iteration = 0
        if current_iteration == max_iterations:
            break
        elapsed = (time.time() - start)
        #print(elapsed)


def movetooffspring(solution1, solution2, offspring):
    max_len = -1
    max_len_id = -1
    for j in range(len(solution1["elements"])):
        if len(solution1["elements"][j]) > max_len:
            max_len = len(solution1["elements"][j])
            max_len_id = j

    if max_len <= 0:
        offspring["elements"].append([])
        return

    num_of_offspring_groups = len(offspring["elements"])
    offspring["elements"].append(solution1["elements"][max_len_id])
    for key in solution1["elements"][max_len_id]:
        solution1["vertex_color"][key] = -1
        offspring["vertex_color"][key] = num_of_offspring_groups

        solution2["elements"][solution2["vertex_color"][key]].remove(key)
        solution2["vertex_color"][key] = -1

    solution1["elements"][max_len_id] = []


def gpx(parent1, parent2, K):
    solution1 = copy.deepcopy(parent1)
    solution2 = copy.deepcopy(parent2)
    offspring = {"cost": 0, "elements": [], "vertex_color": {}}

    for i in range(K):
        if i % 2 == 0:
            movetooffspring(solution1, solution2, offspring)
        else:
            movetooffspring(solution2, solution1, offspring)

    for group in solution1["elements"]:
        for j in group:
            color_group = rand.randint(0, K - 1)
            offspring["vertex_color"][j] = color_group
            offspring["elements"][color_group].append(j)

    offspring["cost"] = checksolution(offspring, vertices)

    return offspring


def select_best(parent1, parent2, offspring):
    lis = [(offspring, offspring["cost"], True),
           (parent1, parent1["cost"], False),
           (parent2, parent2["cost"], False)
           ]
    lis = sorted(lis, key=itemgetter(1), reverse=False)  # must be False as we are minimizing

    return lis[0][0], lis[1][0], (lis[0][2] or lis[1][2]), min(lis[0][1], lis[1][1])


# estimations
# simple.txt 10s per 10 pop size -> 100s per 100 pop size
# 12s per 10 pop size -> 120s per generation
# 300 generations max -> 36000s = 10h

print("Parsing file")
#vertices = readfile('test.txt')
#vertices = readfile('graph1.txt')
vertices = readfile('simple.txt')

K = 8
pop_size = 100  #100

print("Generating population")
population = []
for i in range(pop_size):
    element = {"elements": [[] for _ in range(K)], "vertex_color": {}}  # elements - color groups, vertex_color - color per vertex
    for key in vertices:
        color_group = rand.randint(0, K - 1)
        element["elements"][color_group].append(key)
        element["vertex_color"][key] = color_group
    element["cost"] = checksolution(element, vertices)
    start = time.time()
    vdls(element, vertices)
    elapsed = (time.time() - start)
    print(i, element["cost"], elapsed)
    population.append(element)


print("Running GA")
run_number = 0
max_non_diff_gen = 50
optimal_coloring_found = False
best_score = 9999
best_solution1 = None
best_solution2 = None
best1 = None
best2 = None
max_runs = 300
while True:
    time_start_loop = time.time()
    diff_gen = False
    i = 0
    num_child_chosen = 0
    while i < pop_size:
        #print(i, "/", pop_size)

        rand.shuffle(population)
        offspring = gpx(population[i], population[i + 1], K)
        vdls(offspring, vertices)
        best1, best2, child_chosen, score = select_best(population[i], population[i + 1], offspring)

        #print(child_chosen)
        if child_chosen:
            num_child_chosen += 1
            diff_gen = True

        if score < best_score:
            best_score = score
        if best_score == 0:
            best_solution1 = best1
            best_solution2 = best2
            optimal_coloring_found = True
            break

        population[i] = best1
        population[i + 1] = best2
        i += 2

    max_runs -= 1

    if optimal_coloring_found:
        break

    if not diff_gen:
        max_non_diff_gen -= 1

    if max_non_diff_gen == 0 or max_runs == 0:
        break

    elapsed_time_loop = time.time() - time_start_loop
    print(best_score, max_non_diff_gen, num_child_chosen, max_runs, elapsed_time_loop)

if optimal_coloring_found:
    print("Found optimal solution.", best1, best2)
else:
    print("Solution not found.")
