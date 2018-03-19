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
    for group in solution["elements"]:
        for key in group:
            for neighbor in vertices[key]:
                if neighbor in group:
                    num_of_errors += 1
    return num_of_errors/2


def get_two_vertex_cost(vertex1, vertex2, group1, group2):
    num_of_errors = 0
    for neighbor in vertices[vertex1]:
        if neighbor in group1:
            num_of_errors += 1
    for neighbor in vertices[vertex2]:
        if neighbor in group2:
            num_of_errors += 1
    return num_of_errors


def swapcolors(solution, vertex1, vertex2):
    total_cost = solution["cost"]

    color1 = -1
    color2 = -1
    for i in range(len(solution["elements"])):
        if vertex1 in solution["elements"][i]:
            color1 = i
        if vertex2 in solution["elements"][i]:
            color2 = i
        if color1 >= 0 and color2 >= 0:
            break

    vertex_cost_before = get_two_vertex_cost(vertex1, vertex2, solution["elements"][color1], solution["elements"][color2])

    solution["elements"][color1].remove(vertex1)
    solution["elements"][color1].append(vertex2)
    solution["elements"][color2].remove(vertex2)
    solution["elements"][color2].append(vertex1)

    vertex_cost_after = get_two_vertex_cost(vertex1, vertex2, solution["elements"][color2], solution["elements"][color1])  # swapped colors
    solution["cost"] = total_cost - vertex_cost_before + vertex_cost_after



def vdls(solution, vertices):
    max_iterations = 100
    current_iteration = 0
    elapsed = 0
    while True:
        #print(current_iteration, "/", max_iterations)
        start = time.time()
        print("Iteration:", current_iteration, "out of", max_iterations, "with best cost", solution["cost"], "in time", elapsed)
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
    offspring["elements"].append(solution1["elements"][max_len_id])

    for j in solution1["elements"][max_len_id]:
        for k in solution2["elements"]:
            if j in k:
                k.remove(j)
                break
    solution1["elements"].pop(max_len_id)


def gpx(parent1, parent2, K):
    solution1 = copy.deepcopy(parent1)
    solution2 = copy.deepcopy(parent2)
    offspring = {"cost": 0, "elements": []}

    for i in range(K):
        if i % 2 == 0:
            movetooffspring(solution1, solution2, offspring)
        else:
            movetooffspring(solution2, solution1, offspring)

    for i in range(len(solution1["elements"])):
        for j in solution1["elements"][i]:
            offspring["elements"][rand.randint(0, K - 1)].append(j)
            for k in solution2["elements"]:
                if j in k:
                    k.remove(j)
                    break
        solution1["elements"][i] = []
    for i in range(len(solution2["elements"])):
        for j in solution2["elements"][i]:
            offspring["elements"][rand.randint(0, K - 1)].append(j)
            for k in solution1["elements"]:
                if j in k:
                    k.remove(j)
                    break
        solution2["elements"][i] = []

    offspring["cost"] = checksolution(offspring, vertices)
    return offspring


def select_best(parent1, parent2, offspring):
    #if offspring == parent1 or offspring == parent2:
    #    return parent1, parent2, False, max(checksolution(parent1, vertices), checksolution(parent2, vertices))

    lis = [(parent1, parent1["cost"], False),
           (parent2, parent2["cost"], False),
           (offspring, offspring["cost"], True)  # todo: move this back to first place and do checking if parent-offspring are different, also there is always some offspring better
           ]
    lis = sorted(lis, key=itemgetter(1), reverse=True)

    return lis[0][0], lis[1][0], (lis[0][2] or lis[1][2]), min(lis[0][1], lis[1][1])

# 150 nodes calc
# generation - 5s per element -> 100*5 = 500s
# GA - 20s per 2 elements -> 10s per element -> estimated runs 150, 100 pop size -> 150000s
# total estimated - 41.8h

print("Parsing file")
#vertices = readfile('graph1.txt')
vertices = readfile('simple.txt')

K = 10
pop_size = 100  #100

print("Generating population")
population = []
for i in range(pop_size):
    element = {"elements": [[] for _ in range(K)]}
    for key in vertices:
        element["elements"][rand.randint(0, K - 1)].append(key)
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
while True:
    diff_gen = False
    i = 0
    num_child_chosen = 0
    while i < pop_size:
        #print(i, "/", pop_size)

        offspring = gpx(population[i], population[i + 1], K)
        vdls(offspring, vertices)
        best1, best2, child_chosen, score = select_best(population[i], population[i + 1], offspring)

        #print(child_chosen)
        if child_chosen:
            num_child_chosen +=1
            diff_gen = True

        if score < best_score:
            best_score = score
        if best_score == 0:
            optimal_coloring_found = True
            break

        population[i] = best1
        population[i + 1] = best2
        i += 2

    if optimal_coloring_found:
        print("Found optimal solution.")
        break

    if not diff_gen:
        max_non_diff_gen -= 1

    if max_non_diff_gen == 0:
        break

    print(best_score, max_non_diff_gen, num_child_chosen)


