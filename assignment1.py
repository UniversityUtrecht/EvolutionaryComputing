import random as rand
from operator import itemgetter


def cross(parent1, parent2):
    return cross_2x(parent1, parent2)
    #doCrossover2(parent1, parent2, offspring1, offspring2)


def fit(element):
    return fit_count_ones(element)
    #return calcFintess2(element)
    #return calcFintess3(element)


# two-point crossover
def cross_2x(parent1, parent2):
    point1 = rand.randint(0, len(parent1))
    point2 = rand.randint(point1, len(parent1))

    offspring1 = [0] * len(parent1)
    offspring2 = [0] * len(parent2)
    for i in range(point1):
        offspring1[i] = parent1[i]
        offspring2[i] = parent2[i]

    for i in range(point2 - point1):
        offspring1[point1 + i] = parent2[point1 + i]
        offspring2[point1 + i] = parent1[point1 + i]

    for i in range(len(parent1) - point2):
        offspring1[point2 + i] = parent1[point2 + i]
        offspring2[point2 + i] = parent2[point2 + i]

    return offspring1, offspring2


# uniform crossover
def cross_ux(parent1, parent2):
    offspring1 = [0] * len(parent1)
    offspring2 = [0] * len(parent2)
    for i in range(len(parent1)):
        if rand.random() < 0.5:
            offspring1[i] = parent1[i]
            offspring2[i] = parent2[i]
        else:
            offspring1[i] = parent2[i]
            offspring2[i] = parent1[i]

    return offspring1, offspring2


# Counting Ones function
def fit_count_ones(element):
    score = 0
    for i in range(len(element)):
        if element[i] == 1:
            score += 1
    return score


# tightly linked Deceptive Trap function
def fit_tight_deceptive_trap(element):
    score = 0
    i = 0
    scores = [3, 2, 1, 0, 4]
    while i < len(element):
        one_count = element[i] + element[i + 1] + element[i + 2] + element[i + 3]
        score += scores[one_count]
        i += 4
    return score


# tightly linked Non-deceptive Trap function
def fit_tight_non_trap(element):
    score = 0
    i = 0
    scores = [1.5, 1, 0.5, 0, 4]
    while i < len(element):
        one_count = element[i] + element[i + 1] + element[i + 2] + element[i + 3]
        score += scores[one_count]
        i += 4
    return score


# randomly linked Deceptive Trap function
def fit_rand_deceptive_trap(element):
    # TODO: randomly linked
    return 0


# randomly linked Non-Deceptive Trap function
def fit_rand_non_trap(element):
    # TODO: randomly linked
    return 0


def select_best(parent1, parent2, offspring1, offspring2):
    lis = [(offspring1, fit(offspring1), True),
           (offspring2, fit(offspring2), True),
           (parent1, fit(parent1), False),
           (parent2, fit(parent2), False)
           ]

    lis = sorted(lis, key=itemgetter(1), reverse=True)
    new_gen = True
    if (lis[0][2] == False or (lis[0][2] == True and (lis[0][0] == parent1 or lis[0][0] == parent2))) and \
            (lis[1][2] == False or (lis[1][2] == True and (lis[1][0] == parent1 or lis[1][0] == parent2))):
        new_gen = False

    #print(newGeneration,"|",lis[0][1], lis[0][2], "|", lis[1][1], lis[1][2], "|", lis[2][1], lis[2][2], "|", lis[3][1], lis[3][2])

    return lis[0][0], lis[1][0], new_gen, max(lis[0][1], lis[1][1])


if __name__ == "__main__":
    str_len = 100
    last_pop_size = 0
    pop_size = 10
    max_score = 100

    while pop_size < 1280:
        good_runs = 0

        # do 25 runs
        for k in range(25):
            # generate population
            pop = []
            for i in range(pop_size):
                el = [0] * str_len
                for j in range(str_len):
                    el[j] = 1 if rand.random() > 0.5 else 0
                pop.append(el)

            # do GA
            max_runs = 1000
            diff_gen = False
            best_score_found = False
            while True:
                # shuffle parents
                for el in pop:
                    rand.shuffle(el)

                i = 0
                while i < pop_size:
                    offspring1, offspring2 = cross(pop[i], pop[i + 1])
                    best1, best2, child_chosen, score = select_best(pop[i], pop[i + 1], offspring1, offspring2)
                    if child_chosen:
                        diff_gen = True
                    if score == max_score:
                        best_score_found = True
                    pop[i] = best1
                    pop[i + 1] = best2
                    i += 2

                max_runs -= 1
                if max_runs <= 0 or not diff_gen or best_score_found:
                    break

            if best_score_found:
                good_runs += 1

        print(pop_size, last_pop_size, good_runs)
        if good_runs >= 24:
            if abs(pop_size - last_pop_size) == 10:  # best found
                break
            else:
                tmp = pop_size
                pop_size = int(pop_size - (pop_size - last_pop_size) / 2)
                last_pop_size = tmp
        else:
            last_pop_size = pop_size
            pop_size *= 2

    print(pop_size)
