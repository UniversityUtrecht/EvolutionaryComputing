import random as rand
from operator import itemgetter
import time
import statistics


class GA:

    def cross(self, parent1, parent2):
        if self.cross_type == 1:
            return self.cross_2x(parent1, parent2)
        else:
            return self.cross_ux(parent1, parent2)


    def fit(self, element):
        self.avg_fitness_evaluations += 1

        if self.fitness_type == 1:
            return self.fit_count_ones(element)
        elif self.fitness_type == 2:
            return self.fit_tight_deceptive_trap(element)
        elif self.fitness_type == 3:
            return self.fit_tight_non_trap(element)
        elif self.fitness_type == 4:
            return self.fit_rand_deceptive_trap(element, self.links)
        elif self.fitness_type == 5:
            return self.fit_rand_non_trap(element, self.links)

    # two-point crossover
    def cross_2x(self, parent1, parent2):
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
    def cross_ux(self, parent1, parent2):
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
    def fit_count_ones(self, element):
        score = 0
        for i in range(len(element)):
            if element[i] == 1:
                score += 1
        return score


    # tightly linked Deceptive Trap function
    def fit_tight_deceptive_trap(self, element):
        score = 0
        i = 0
        scores = [3, 2, 1, 0, 4]
        while i < len(element):
            one_count = element[i] + element[i + 1] + element[i + 2] + element[i + 3]
            score += scores[one_count]
            i += 4
        return score


    # tightly linked Non-deceptive Trap function
    def fit_tight_non_trap(self, element):
        score = 0
        i = 0
        scores = [1.5, 1, 0.5, 0, 4]
        while i < len(element):
            one_count = element[i] + element[i + 1] + element[i + 2] + element[i + 3]
            score += scores[one_count]
            i += 4
        return score


    # randomly linked Deceptive Trap function
    def fit_rand_deceptive_trap(self, element, links):
        score = 0
        scores = [3, 2, 1, 0, 4]
        for i in range(len(links)):
            one_count = sum([element[links[i][j]] for j in range(3)])
            score += scores[one_count]
        return score


    # randomly linked Non-Deceptive Trap function
    def fit_rand_non_trap(self, element, links):
        score = 0
        scores = [1.5, 1, 0.5, 0, 4]
        for i in range(len(links)):
            one_count = sum([element[links[i][j]] for j in range(3)])
            score += scores[one_count]
        return score


    # generate random links
    def rand_links(self, str_len=100):
        order = list(range(str_len))
        rand.shuffle(order)
        links = [order[i:i + 4] for i in range(0, str_len, 4)]
        return links


    def select_best(self, parent1, parent2, offspring1, offspring2):
        lis = [(offspring1, self.fit(offspring1), True),
               (offspring2, self.fit(offspring2), True),
               (parent1, self.fit(parent1), False),
               (parent2, self.fit(parent2), False)
               ]

        lis = sorted(lis, key=itemgetter(1), reverse=True)
        new_gen = True
        if (not lis[0][2] or (lis[0][2] and (lis[0][0] == parent1 or lis[0][0] == parent2))) and \
                (not lis[1][2] or (lis[1][2] and (lis[1][0] == parent1 or lis[1][0] == parent2))):
            new_gen = False

        #print(newGeneration,"|",lis[0][1], lis[0][2], "|", lis[1][1], lis[1][2], "|", lis[2][1], lis[2][2], "|", lis[3][1], lis[3][2])

        return lis[0][0], lis[1][0], new_gen, max(lis[0][1], lis[1][1])

    def do_GA(self):
        str_len = 100
        min_bound = 0
        max_bound = 1280
        pop_size = 10
        max_score = 100
        convergence = False

        while pop_size <= 1280:
            good_runs = 0
            avg_num_of_generations = 0
            self.avg_fitness_evaluations = 0
            time_start = time.process_time()
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
                max_runs = 3000
                best_score_found = False
                run_number = 0

                while True:
                    # shuffle parents
                    rand.shuffle(pop)

                    i = 0
                    diff_gen = False
                    while i < pop_size:
                        offspring1, offspring2 = self.cross(pop[i], pop[i + 1])
                        best1, best2, child_chosen, score = self.select_best(pop[i], pop[i + 1], offspring1, offspring2)
                        if child_chosen:
                            diff_gen = True
                        if score == max_score:
                            best_score_found = True
                        pop[i] = best1
                        pop[i + 1] = best2
                        i += 2

                    run_number += 1
                    if run_number >= max_runs or not diff_gen or best_score_found:
                        break

                avg_num_of_generations += run_number

                if best_score_found:
                    good_runs += 1

                pops = []
                for el in pop:
                    pops.append(el)
                self.success_list.append({"pop_size": pop_size, "pops": pops})

            print(pop_size, min_bound, max_bound, good_runs)
            avg_cpu_time = (time.process_time() - time_start) / 25
            avg_num_of_generations = avg_num_of_generations / 25
            self.avg_fitness_evaluations = self.avg_fitness_evaluations / 25
            self.success_list.append({"pop_size": pop_size, "good_runs": good_runs, "avg_num_of_generations": avg_num_of_generations, "avg_fitness_evals": self.avg_fitness_evaluations, "avg_cpu_time": avg_cpu_time})

            if good_runs >= 24:
                convergence = True
                if abs(pop_size - min_bound) == 10:  # best found
                    break
                else: # go down
                    max_bound = pop_size
                    pop_size = int(max_bound - (max_bound - min_bound) / 2)
            else:
                min_bound = pop_size
                if convergence: # go up for difference
                    if abs(max_bound - pop_size) == 10:
                        pop_size = max_bound
                        break
                    else:
                        pop_size = int(max_bound - (max_bound - min_bound) / 2)
                else: # go up for 2x
                    pop_size = pop_size * 2
                #pop_size = pop_size * 2 if not convergence else int(max_bound - (max_bound - min_bound) / 2)

        #print(pop_size)
        return pop_size

    def special_run(self):
        pop_size = 250
        max_score = 100
        str_len = 100

        pop = []
        for i in range(pop_size):
            el = [0] * str_len
            for j in range(str_len):
                el[j] = 1 if rand.random() > 0.5 else 0
            pop.append(el)

        diff_gen = True
        best_score_found = False
        generation_number = 0
        self.cross_type = 1
        self.fitness_type = 1

        generation_info = []
        selection_errors = 0

        while True:

            fitnesses = [self.fit(el) for el in pop]
            sum_fitness = sum(fitnesses)
            avg_fitness = sum_fitness / pop_size
            std_dev_fitness = statistics.stdev(fitnesses)
            proportion = sum_fitness / (pop_size*str_len)
            generation_info.append({"generation": generation_number, "avg": avg_fitness, "std_dev": std_dev_fitness, "proportion": proportion, "selection_errors": selection_errors})
            print("Run:", generation_number, proportion)
            #if not diff_gen or best_score_found:
            if proportion == 1:
                break

            selection_errors = 0
            rand.shuffle(pop)
            i = 0
            diff_gen = False
            while i < pop_size:
                offspring1, offspring2 = self.cross(pop[i], pop[i + 1])
                best1, best2, child_chosen, score = self.select_best(pop[i], pop[i + 1], offspring1, offspring2)
                if child_chosen:
                    diff_gen = True
                if score == max_score:
                    best_score_found = True

                for j in range(str_len):
                    if (pop[i][j] == 1 or pop[i+1][j] == 1) and best1[j] == 0 and best2[j] == 0:
                        selection_errors += 1

                pop[i] = best1
                pop[i + 1] = best2
                i += 2

            generation_number += 1

        return generation_info

    success_list = []
    avg_fitness_evaluations = 0
    cross_type = ""
    fitness_type = ""
    links = []

    def run(self, fitness_type, cross_type):
        self.links = self.rand_links()
        self.success_list = []
        self.cross_type = cross_type
        self.fitness_type = fitness_type
        pop_size = self.do_GA()
        #print(pop_size, self.success_list)
        return pop_size, self.success_list


ga = GA()

"""
print("special ones")
results = ga.special_run()
thefile = open('special ones.txt', 'w')
for item in results:
    thefile.write("%s\n" % item)
thefile.close()
"""

"""
print("ones 2x")
_, results = ga.run(1,1)
thefile = open('2 ones 2x.txt', 'w')
for item in results:
    thefile.write("%s\n" % item)
thefile.close()

print("ones ux")
_, results = ga.run(1,2)
thefile = open('2 ones ux.txt', 'w')
for item in results:
    thefile.write("%s\n" % item)
thefile.close()


print("tight deceptive 2x")
_, results = ga.run(2,1)
thefile = open('2 tight deceptive 2x.txt', 'w')
for item in results:
    thefile.write("%s\n" % item)
thefile.close()

print("tight deceptive ux")
_, results = ga.run(2,2)
thefile = open('2 tight deceptive ux.txt', 'w')
for item in results:
    thefile.write("%s\n" % item)
thefile.close()


print("tight nondeceptive 2x")
_, results = ga.run(3,1)
thefile = open('2 tight nondeceptive 2x.txt', 'w')
for item in results:
    thefile.write("%s\n" % item)
thefile.close()

print("tight nondeceptive ux")
_, results = ga.run(3,2)
thefile = open('2 tight nondeceptive ux.txt', 'w')
for item in results:
    thefile.write("%s\n" % item)
thefile.close()


print("random deceptive 2x")
_, results = ga.run(4, 1)
thefile = open('2 random deceptive 2x.txt', 'w')
for item in results:
    thefile.write("%s\n" % item)
thefile.close()

print("random deceptive ux")
_, results = ga.run(4, 2)
thefile = open('2 random deceptive ux.txt', 'w')
for item in results:
    thefile.write("%s\n" % item)
thefile.close()


print("random nondeceptive 2x")
_, results = ga.run(5, 1)
thefile = open('2 random nondeceptive 2x.txt', 'w')
for item in results:
    thefile.write("%s\n" % item)
thefile.close()


print("random nondeceptive ux")
_, results = ga.run(5, 2)
thefile = open('2 random nondeceptive ux.txt', 'w')
for item in results:
    thefile.write("%s\n" % item)
thefile.close()
"""

"""
print("ones 2x:", ga.run(1,1))
print("ones ux:", ga.run(1,2))

print("tight deceptive 2x:", ga.run(2,1))
print("tight deceptive ux:", ga.run(2,2))

print("tight nondeceptive 2x:", ga.run(3,1))
print("tight nondeceptive ux:", ga.run(3,2))

print("random deceptive 2x:", ga.run(4,1))
print("random deceptive ux:", ga.run(4,2))

print("random nondeceptive 2x:", ga.run(5,1))
print("random nondeceptive ux:", ga.run(5,2))
"""