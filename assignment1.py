import random as rand
from operator import itemgetter


def doCrossover(parent1, parent2):
    return doCrossover1(parent1, parent2)
    #doCrossover2(parent1, parent2, offspring1, offspring2)


def calcFintess(element):
    return calcFintess1(element)
    #return calcFintess2(element)
    #return calcFintess3(element)


def doCrossover1(parent1, parent2):
    point1 = rand.randint(0, len(parent1))
    point2 = rand.randint(point1, len(parent1))

    offspring1 = [0]*len(parent1)
    offspring2 = [0]*len(parent2)
    for i in range(point1):
        offspring1[i] = parent1[i]
        offspring2[i] = parent2[i]

    for i in range(point2-point1):
        offspring1[point1+i] = parent2[point1+i]
        offspring2[point1+i] = parent1[point1+i]

    for i in range(len(parent1)-point2):
        offspring1[point2+i] = parent1[point2+i]
        offspring2[point2+i] = parent2[point2+i]

    return offspring1, offspring2


def doCrossover2(parent1, parent2):
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


def calcFintess1(element):
    score = 0
    for i in range(len(element)):
        if element[i] == 1:
            score += 1
    return score


def calcFintess2(element):
    score = 0
    i = 0
    scores = [3,2,1,0,4]
    while i<len(element):
        numOfOnes = element[i] + element[i + 1] + element[i + 2] + element[i + 3]
        score += scores[numOfOnes]
        i += 4
    return score


def calcFintess3(element):
    score = 0
    i = 0
    scores = [1.5,1,0.5,0,4]
    while i<len(element):
        numOfOnes = element[i] + element[i + 1] + element[i + 2] + element[i + 3]
        score += scores[numOfOnes]
        i += 4
    return score


def calcFintess4(element):
    # TODO: randomly linked
    return 0


def calcFintess5(element):
    # TODO: randomly linked
    return 0


def selectBest(parent1, parent2, offspring1, offspring2):
    lis = [(offspring1, calcFintess(offspring1), True),
           (offspring2, calcFintess(offspring2), True),
           (parent1, calcFintess(parent1), False),
           (parent2, calcFintess(parent2), False)
           ]

    lis = sorted(lis, key=itemgetter(1), reverse=True)
    newGeneration = True
    if (lis[0][2] == False or (lis[0][2] == True and (lis[0][0] == parent1 or lis[0][0] == parent2))) and \
            (lis[1][2] == False or (lis[1][2] == True and (lis[1][0] == parent1 or lis[1][0] == parent2))):
        newGeneration = False

    #print(newGeneration,"|",lis[0][1], lis[0][2], "|", lis[1][1], lis[1][2], "|", lis[2][1], lis[2][2], "|", lis[3][1], lis[3][2])

    return lis[0][0], lis[1][0], newGeneration, max(lis[0][1], lis[1][1])


def main():
    stringLength = 100
    lastPopulationSize = 0
    populationSize = 10
    bestPossibleScore = 100

    while populationSize < 1280:
        successfulRuns = 0

        # do 25 runs
        for k in range(25):
            population = []
            for i in range(populationSize):
                el = [0] * stringLength
                for j in range(stringLength):
                    el[j] = 1 if rand.random() > 0.5 else 0
                population.append(el)



            # do GA
            maxNumberOfRuns = 1000
            differentGeneration = False
            bestScoreFound = False
            while True:
                # shuffle parents
                for el in population:
                    rand.shuffle(el)

                i = 0
                while i < populationSize:
                    offspring1, offspring2 = doCrossover(population[i], population[i + 1])
                    best1, best2, childChosen, score = selectBest(population[i], population[i + 1], offspring1, offspring2)
                    if childChosen:
                        differentGeneration = True
                    if score == bestPossibleScore:
                        bestScoreFound = True
                    population[i] = best1
                    population[i+1] = best2
                    i += 2

                maxNumberOfRuns -= 1
                if maxNumberOfRuns <= 0 or not differentGeneration or bestScoreFound:
                    break

            if bestScoreFound:
                successfulRuns += 1

        print(populationSize, lastPopulationSize, successfulRuns)
        if successfulRuns >= 24:
            if abs(populationSize - lastPopulationSize) == 10:  # best found
                break
            else:
                tmp = populationSize
                populationSize = int(populationSize - (populationSize - lastPopulationSize) / 2)
                lastPopulationSize = tmp
        else:
            lastPopulationSize = populationSize
            populationSize *= 2

    print(populationSize)

main()