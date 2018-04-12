#include <iostream>
#include <fstream>
#include <iomanip>
#include <string>
#include <map>
#include <set>
#include <algorithm>
#include <ctime>
#include <vector>
#include <thread>
#include <omp.h>

#define MAX_NON_DIFF_GEN 100
#define POPULATION_SIZE 100
#define VDLS_RUNS 100
#define NUM_COLORS 18
#define EASIER_GRAPH false

#define USE_VDLS true

int numberOfVdlsSwaps = 0;
int numberOfVdlsCalls = 0;

struct Measure
{
	int runNumber;
	int bestScore;
	long long elapsed_time;
	double cpu_time;

	double avgParentFitness;
	double avgChildFitness;

	std::vector<double> parentFitnesses;
	std::vector<double> childFitnesses;

	int numberOfVdlsSwaps = 0;
	int numberOfVdlsCalls = 0;

	std::vector<std::string> parentChildCosts;
};

struct Group
{
	std::vector<int> elements;
};

struct Element
{
	std::vector<Group> colorGroups;
	std::vector<int> vertexColor;
	int cost;
};

int Rand(int n)
{
	return rand() % n;
}

std::vector<std::string> splitString(std::string str, std::string delimiter)
{
	std::vector<std::string> words;
	size_t pos = 0;
	std::string token;
	while ((pos = str.find(delimiter)) != std::string::npos) {
		token = str.substr(0, pos);
		//std::cout << token << std::endl;
		words.push_back(token);
		str.erase(0, pos + delimiter.length());
	}
	words.push_back(str);
	return words;
}

std::vector<Group> readFile(std::string fileName)
{
	std::vector<Group> vertices;

	std::ifstream input(fileName);
	
	for (std::string line; getline(input, line); )
	{
		if (line[0] == 'c')
		{
			continue;
		}
		else if (line[0] == 'p')
		{
			std::vector<std::string> splits = splitString(line, " ");
			int numOfVertices = stoi(splits[2]);
			int maxConnections = stoi(splits[3]);

			for (int i = 0; i < numOfVertices; i++)
				vertices.push_back(Group());
		}
		else if (line[0] == 'e')
		{
			std::vector<std::string> splits = splitString(line, " ");
			int vertex1 = stoi(splits[1]) - 1;
			int vertex2 = stoi(splits[2]) - 1;

			vertices[vertex1].elements.push_back(vertex2);
			vertices[vertex2].elements.push_back(vertex1);
		}
	}

	return vertices;
}

Element createNewElement(int K, const std::vector<Group> &vertices)
{
	Element newElement;
	newElement.cost = 0;
	int size = vertices.size();
	//for (int i = 0; i < K; i++)
	//	newElement.colorGroups.push_back(group());
	for (int i = 0; i < size; i++)
		newElement.vertexColor.push_back(-1);
	return newElement;
}

int checkSolution(Element solution, const std::vector<Group> &vertices)
{
	int numberOfErrors = 0;

	for (size_t i = 0; i < vertices.size(); i++)
	{
		for (size_t j = 0; j < vertices[i].elements.size(); j++)
		{
			if (solution.vertexColor[i] == solution.vertexColor[vertices[i].elements[j]])
				numberOfErrors++;
		}
	}

	return numberOfErrors / 2;
}

int get_two_vertex_cost(Element &solution, int vertex1, int vertex2, const std::vector<Group> &vertices)
{
	int num_of_errors = 0;
	for (size_t i = 0; i < vertices[vertex1].elements.size(); i++)
		if (solution.vertexColor[vertices[vertex1].elements[i]] == solution.vertexColor[vertex1])
			num_of_errors += 1;
	for (size_t i = 0; i < vertices[vertex2].elements.size(); i++)
		if (solution.vertexColor[vertices[vertex2].elements[i]] == solution.vertexColor[vertex2])
			num_of_errors += 1;
	return num_of_errors;
}

std::vector<int> generateArray(int size)
{
	std::vector<int> vec;
	for (int i = 0; i < size; i++)
		vec.push_back(i);
	return vec;
}

void removeElementByValue(std::vector<int> &el, int value)
{
	el.erase(std::remove(el.begin(), el.end(), value), el.end());
}

void swapColors(Element &solution, int vertex1, int vertex2, const std::vector<Group> &vertices)
{
	
	int color1 = solution.vertexColor[vertex1];
	int color2 = solution.vertexColor[vertex2];

	if (color1 == color2)
		return;

	int total_cost = solution.cost;
	int vertex_cost_before = get_two_vertex_cost(solution, vertex1, vertex2, vertices);

	solution.vertexColor[vertex1] = color2;
	solution.vertexColor[vertex2] = color1;

	removeElementByValue(solution.colorGroups[color1].elements, vertex1);
	//solution.colorGroups[color1].elements.erase(std::remove(solution.colorGroups[color1].elements.begin(), solution.colorGroups[color1].elements.end(), vertex1), solution.colorGroups[color1].elements.end());
	solution.colorGroups[color1].elements.push_back(vertex2);
	

	removeElementByValue(solution.colorGroups[color2].elements, vertex2);
	//solution.colorGroups[color2].elements.erase(std::remove(solution.colorGroups[color2].elements.begin(), solution.colorGroups[color2].elements.end(), vertex2), solution.colorGroups[color2].elements.end());
	solution.colorGroups[color2].elements.push_back(vertex1);

	int vertex_cost_after = get_two_vertex_cost(solution, vertex1, vertex2, vertices);

	solution.cost = total_cost - vertex_cost_before + vertex_cost_after;

	//if (solution.cost > total_cost)
	//	std::cout << "!!!!!!!!!!!!! " << solution.cost << " " << total_cost << " " << vertex_cost_before << " " << vertex_cost_after << std::endl;
}

double test_elapsed = 0;

void VDLS(Element &solution, int K, const std::vector<Group> &vertices)
{
	numberOfVdlsCalls++;

	int verticesSize = vertices.size();
	int maxIterations = VDLS_RUNS;
	int currentIteration = 0;
	
	static std::vector<int> vertexShuffleArray = generateArray(verticesSize);
	auto time_elapsed = std::chrono::milliseconds(0);
	
	while (true)
	{
		auto c_start = std::chrono::system_clock::now();

		//std::cout << "Iteration: " << currentIteration << " out of " << maxIterations << " with best cost " << solution.cost << " in time " << std::fixed << std::setprecision(6) << (float)time_elapsed.count()/1000.0 << std::endl;

		std::random_shuffle(vertexShuffleArray.begin(), vertexShuffleArray.end(), std::pointer_to_unary_function<int, int>(Rand));
		bool changed = false;

		for (int i = 0; i < verticesSize; i++)
		{
			int vertex1 = vertexShuffleArray[i];

			bool swapped = false;

			int bestColor = solution.vertexColor[vertex1];
			int leastErrors = 9999;
			int currentColorErrors = 0;
			for (int j = 0; j < K; j++)
			{
				int numOfErrors = 0;
				for (size_t k = 0; k < vertices[vertex1].elements.size(); k++)
				{
					if (j == solution.vertexColor[vertices[vertex1].elements[k]])
						numOfErrors++;
				}

				if (j == solution.vertexColor[vertex1])
					currentColorErrors += numOfErrors;

				if (numOfErrors < leastErrors)
				{
					bestColor = j;
					leastErrors = numOfErrors;
				}
			}

			if (bestColor != solution.vertexColor[vertex1])
			{
				numberOfVdlsSwaps++;
				changed = true;
				removeElementByValue(solution.colorGroups[solution.vertexColor[vertex1]].elements, vertex1);
				solution.colorGroups[bestColor].elements.push_back(vertex1);
				solution.vertexColor[vertex1] = bestColor;
				solution.cost = solution.cost - currentColorErrors + leastErrors;
			}
		}

		auto c_end = std::chrono::system_clock::now();
		time_elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(c_end - c_start);

		if (!changed)
		{
			currentIteration++;
		}
		else
		{
			currentIteration = 0;
		}
		if (currentIteration == maxIterations)
		{
			return;
		}

		if (solution.cost == 0)
			return;
	}
}


void NSGB(Element &solution, const std::vector<Group> &vertices)
{
	numberOfVdlsCalls++;

	int verticesSize = vertices.size();
	int maxIterations = VDLS_RUNS;
	int currentIteration = 0;

	static std::vector<int> vertexShuffleArray = generateArray(verticesSize);

	auto time_elapsed = std::chrono::milliseconds(0);

	while (true)
	{
		auto c_start = std::chrono::system_clock::now();

		//double t_start = omp_get_wtime();
		//std::cout << "Iteration: " << currentIteration << " out of " << maxIterations << " with best cost " << solution.cost << " in time " << std::fixed << std::setprecision(6) << (float)time_elapsed.count()/1000.0 << std::endl;

		std::random_shuffle(vertexShuffleArray.begin(), vertexShuffleArray.end(), std::pointer_to_unary_function<int, int>(Rand));
		bool changed = false;

		for (int i = 0; i < verticesSize; i++)
		{
			int vertex1 = vertexShuffleArray[i];
			int vertex1Size = vertices[vertex1].elements.size();

			int bestSwapScore = solution.cost;
			int bestSwapVertex1 = 0;
			int bestSwapVertex2 = 0;
			bool swapped = false;

			for (int j = 0; j < vertex1Size; j++)
			{
				int vertex2 = vertices[vertex1].elements[j];
				int vertex2Size = vertices[vertex2].elements.size();

				int color1 = solution.vertexColor[vertex1];
				int color2 = solution.vertexColor[vertex2];

				if (color1 != color2)
				{
					int vertex_cost_before = 0;
					int vertex_cost_after = 0;

					int vertexK = 0;
					int tempColor = 0;

					std::clock_t test_start = std::clock();


					for (int k = 0; k < vertex1Size; k++)
					{
						vertexK = vertices[vertex1].elements[k];
						tempColor = solution.vertexColor[vertexK];
						if (tempColor == color1)
							vertex_cost_before++;
						else if (tempColor == color2 and vertexK != vertex2)
							vertex_cost_after++;
					}
					for (int k = 0; k < vertex2Size; k++)
					{
						vertexK = vertices[vertex2].elements[k];
						tempColor = solution.vertexColor[vertexK];
						if (tempColor == color2)
							vertex_cost_before++;
						else if (tempColor == color1 and vertexK != vertex1)
							vertex_cost_after++;
					}
					int num_of_errors = solution.cost - vertex_cost_before + vertex_cost_after;

					std::clock_t test_end = std::clock();
					test_elapsed = test_elapsed + (test_end - test_start);

					if (num_of_errors <= bestSwapScore)
					{
						if (num_of_errors < bestSwapScore)
							changed = true;

						bestSwapScore = num_of_errors;
						bestSwapVertex1 = vertex1;
						bestSwapVertex2 = vertex2;
						swapped = true;

					}

				}

			}

			if (swapped)
			{
				numberOfVdlsSwaps++;
				swapColors(solution, bestSwapVertex1, bestSwapVertex2, vertices);
			}


			//double t_2 = omp_get_wtime() - t_1;
			//std::cout << t_2 << std::endl;
		}

		auto c_end = std::chrono::system_clock::now();
		time_elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(c_end - c_start);

		if (!changed)
		{
			currentIteration++;
		}
		else
		{
			currentIteration = 0;
		}
		if (currentIteration == maxIterations)
		{
			return;
		}


		if (solution.cost == 0)
			return;

		//t_elapsed = omp_get_wtime() - t_start;
	}
}

void moveToOffspring(Element &solution1, Element &solution2, Element &offspring)
{
	int maxLen = -1;
	int maxLenId = -1;
	int noOfGroups = solution1.colorGroups.size();
	for (int i = 0; i < noOfGroups; i++) // TODO: Why not K instead of size??
	{
		int solution1GroupElementsSize = solution1.colorGroups[i].elements.size();
		if (solution1GroupElementsSize >= maxLen)
		{
			maxLen = solution1GroupElementsSize;
			maxLenId = i;
		}
	}

	if (maxLen <= 0)
	{
		std::cout << "!!!!!!!!!!!!!!!!!!!!!!" << std::endl;
		offspring.colorGroups.push_back(Group());
		return;
	}

	int numOfOffspringGroups = offspring.colorGroups.size();
	offspring.colorGroups.push_back(Group());
	for (int i = 0; i < maxLen; i++)
	{
		int id = solution1.colorGroups[maxLenId].elements[i];

		solution1.vertexColor[id] = -1;
		offspring.vertexColor[id] = numOfOffspringGroups;
		offspring.colorGroups[numOfOffspringGroups].elements.push_back(id);
		removeElementByValue(solution2.colorGroups[solution2.vertexColor[id]].elements, id);
		solution2.vertexColor[id] = -1;
	}

	solution1.colorGroups[maxLenId].elements.clear();

}

Element gpx(Element parent1, Element parent2, int K, const std::vector<Group> &vertices) // pass by value!!!
{
	Element offspring = createNewElement(K, vertices);
	
	for (int i = 0; i < K; i++)
	{
		if (i % 2 == 0)
		{
			moveToOffspring(parent1, parent2, offspring);
		}
		else
		{
			moveToOffspring(parent2, parent1, offspring);
		}
	}

	int length = vertices.size();
	for (int i = 0; i < length; i++)
	{
		if (parent1.vertexColor[i] != -1)
		{
			int colorGroup = rand() % K;
			offspring.vertexColor[i] = colorGroup;
			offspring.colorGroups[colorGroup].elements.push_back(i);
		}
	}
	offspring.cost = checkSolution(offspring, vertices);
	return offspring;
}

int selectBest(Element &parent1, Element &parent2, Element &offspring, Element &best1, Element &best2, bool &childChosen)
{
	Element *elements[] = { &parent1, &parent2, &offspring };
	int costs[] = { parent1.cost, parent2.cost, offspring.cost };

	int maxElementIndex = std::max_element(costs, costs + 3) - costs;
	int minElementIndex = std::min_element(costs, costs + 3) - costs;

	if (maxElementIndex == minElementIndex)
	{
		maxElementIndex = 1;
		minElementIndex = 2;
	}

	if (costs[maxElementIndex] == costs[3 - maxElementIndex - minElementIndex] && minElementIndex != 2) // if worst two are the same prioritize child
	{
		maxElementIndex = 1 - minElementIndex;
	}
		
	best1 = *(elements[minElementIndex]);
	best2 = *(elements[3 - maxElementIndex - minElementIndex]);

	if (maxElementIndex != 2)
		childChosen = true;

	return costs[minElementIndex];
}

bool runGA(int runId, int colorCount, std::vector<Group> &vertices)
{
	int K = colorCount;
	int popSize = POPULATION_SIZE;
	numberOfVdlsCalls = 0;
	numberOfVdlsSwaps = 0;

	// Generate population
	std::cout << "Generating population" << std::endl;
	std::vector<Element> population;

	for (int i = 0; i < popSize; i++)
	{
		std::cout << "Run: " << i;

		Element populationElement = createNewElement(K, vertices);
		for (int i = 0; i < K; i++)
			populationElement.colorGroups.push_back(Group());

		for (size_t i = 0; i < vertices.size(); i++)
		{
			int color = rand() % K;
			populationElement.colorGroups[color].elements.push_back(i);
			populationElement.vertexColor[i] = color;
		}

		populationElement.cost = checkSolution(populationElement, vertices);
		std::cout << " Initial cost: " << populationElement.cost;
		double t = omp_get_wtime();

		if (USE_VDLS)
		{
			test_elapsed = 0;
			numberOfVdlsCalls = 0;
			numberOfVdlsSwaps = 0;
			VDLS(populationElement, K, vertices);
		}

		t = omp_get_wtime() - t;
		std::cout << " Time: " << t << " Cost: " << populationElement.cost << " VDLS calls: " << numberOfVdlsCalls << " VDLS swaps: " << numberOfVdlsSwaps << " Test elapsed: " << test_elapsed / 1000 << std::endl;

		population.push_back(populationElement);
	}

	int avgParentFitness = 0;
	for (int i = 0; i < popSize; i++)
	{
		avgParentFitness += population[i].cost;
	}
	avgParentFitness = avgParentFitness / popSize;
	std::cout << "Average fitness: " << avgParentFitness << std::endl;


	int runNumber = 0;
	int runsWithoutImprovement = 0;
	int maxNonDiffGen = MAX_NON_DIFF_GEN;
	bool optimalColoringFound = false;
	int bestScore = 9999;
	Element *bestSolution = nullptr;
	int maxRuns = 200;
	std::vector<int> populationShuffleArray = generateArray(popSize);

	std::vector<Measure> measures;
	std::cout << "Running GA" << std::endl;
	while (true)
	{
		std::cout << "Generation: " << runNumber;

		std::clock_t c_start_cpu = std::clock();
		auto c_start_wall = std::chrono::system_clock::now();

		Measure currentRunMeasure;
		numberOfVdlsCalls = 0;
		numberOfVdlsSwaps = 0;

		bool diffGen = false;
		int i = 0;
		int numChildChosen = 0;

		std::random_shuffle(populationShuffleArray.begin(), populationShuffleArray.end(), std::pointer_to_unary_function<int, int>(Rand));

		// calc avg fitness
		double avgParentFitness = 0;
		double avgChildFitness = 0;
		for (int i = 0; i < popSize; i++)
		{
			avgParentFitness += population[i].cost;
			currentRunMeasure.parentFitnesses.push_back(population[i].cost);
		}
		avgParentFitness = avgParentFitness / popSize;
		bool scoreChanged = false;

		for(int i=0; i<popSize/2; i++)
		{

			int pop1 = populationShuffleArray[i*2];
			int pop2 = populationShuffleArray[i*2 + 1];

			Element offspring = gpx(population[pop1], population[pop2], K, vertices);

			if (USE_VDLS)
			{
				VDLS(offspring, K, vertices);
			}

			avgChildFitness += offspring.cost;
			currentRunMeasure.childFitnesses.push_back(offspring.cost);

			currentRunMeasure.parentChildCosts.push_back("p1: " + std::to_string(population[pop1].cost) + " p2: " + std::to_string(population[pop2].cost) + " off:" + std::to_string(offspring.cost));

			Element best1, best2;
			bool childChosen = false;

			int score = selectBest(population[pop1], population[pop2], offspring, best1, best2, childChosen);

			population[pop1] = best1;
			population[pop2] = best2;

			if (childChosen)
			{
				diffGen = true;
			}

			if (score < bestScore)
			{
				scoreChanged = true;
				bestScore = score;
			}
				
			if (bestScore == 0)
			{
				bestSolution = &(population[pop1]);
				optimalColoringFound = true;
				//break;
			}
		}

		avgChildFitness = avgChildFitness / (popSize / 2);

		maxRuns--;
		runNumber++;

		// do measuring



		std::clock_t c_end_cpu = std::clock();
		auto c_end_wall = std::chrono::system_clock::now();


		double time_elapsed_cpu = (c_end_cpu - c_start_cpu);
		auto time_elapsed_wall = std::chrono::duration_cast<std::chrono::milliseconds>(c_end_wall - c_start_wall);


		currentRunMeasure.bestScore = bestScore;
		currentRunMeasure.cpu_time = time_elapsed_cpu;
		currentRunMeasure.elapsed_time = time_elapsed_wall.count();
		currentRunMeasure.runNumber = runNumber;
		currentRunMeasure.avgParentFitness = avgParentFitness;
		currentRunMeasure.avgChildFitness = avgChildFitness;
		currentRunMeasure.numberOfVdlsCalls = numberOfVdlsCalls;
		currentRunMeasure.numberOfVdlsSwaps = numberOfVdlsSwaps;
		// add coef

		measures.push_back(currentRunMeasure);

		std::cout << " Time Wall: " << time_elapsed_wall.count() << " Time CPU: " << time_elapsed_cpu / 1000 << " Best Score: " << bestScore << " DiffGen: " << diffGen << " ScoreChanged: " << scoreChanged << " Avg Parent Fitness: " << avgParentFitness << " Avg Child Fitness: " << avgChildFitness << std::endl;

		if (optimalColoringFound)
			break;
		if (!diffGen)
		{
			maxNonDiffGen--;
		}
		else
		{
			maxNonDiffGen = MAX_NON_DIFF_GEN;
		}

		if (!scoreChanged)
		{
			runsWithoutImprovement++;
		}
		else
		{
			runsWithoutImprovement = 0;
		}
			

		if (maxNonDiffGen == 0 || maxRuns == 0 || runsWithoutImprovement == MAX_NON_DIFF_GEN)
			break;

	}

	std::string saveFile = std::to_string(runId) + "_coloring_";
	if (USE_VDLS)
		saveFile += "vdls_";
	else
		saveFile += "novdls_";

	saveFile += std::to_string(K) + ".txt";

	std::ofstream myfile(saveFile);
	if (myfile.is_open())
	{
		myfile << "VDLS_calls: " << std::to_string(numberOfVdlsCalls) << std::endl << "VDLS_swaps: " << std::to_string(numberOfVdlsSwaps) << std::endl;

		for (size_t i = 0; i < measures.size(); i++)
		{
			myfile << "run_number: " << measures[i].runNumber << " || " <<
				"best_score: " << measures[i].bestScore << " || " <<
				"cpu_time: " << measures[i].cpu_time << " || " <<
				"elapsed_time: " << measures[i].elapsed_time << " || " <<
				" VDLS_calls: " << std::to_string(measures[i].numberOfVdlsCalls) << " || " <<
				" VDLS_swaps: " << std::to_string(measures[i].numberOfVdlsSwaps) << " || " <<
				"avg_parent_fitness: " << measures[i].avgParentFitness << " || " <<
				"avg_child_fitness: " << measures[i].avgChildFitness << " || ";

			std::cout << "parent_child_fitnesses: {";
			for (size_t j = 0; j < measures[i].parentChildCosts.size(); j++)
			{
				myfile << "{" << measures[i].parentChildCosts[j] << "}";
			}
			myfile << "} ";

			std::cout << "parent_fitnesses: {";
			for (size_t j = 0; j < measures[i].parentFitnesses.size(); j++)
			{
				myfile << std::to_string(measures[i].parentFitnesses[j]) << ",";
			}
			myfile << "} || child_fitnesses: {";
			for (size_t j = 0; j < measures[i].childFitnesses.size(); j++)
			{
				myfile << std::to_string(measures[i].childFitnesses[j]) << ",";
			}
			myfile << "}" << std::endl;
		}
		

		if (bestSolution != nullptr)
		{
			myfile << "best_solution: {";
			for (size_t i = 0; i < bestSolution->colorGroups.size(); i++)
			{
				myfile << "{";
				for (size_t j = 0; j < bestSolution->colorGroups[i].elements.size(); j++)
				{
					myfile << bestSolution->colorGroups[i].elements[j] << ",";
				}
				myfile << "}";
			}
			myfile << "}" << std::endl;
		}
		myfile.close();
	}

	std::cout << std::to_string(runId) << " finished running with K=" << std::to_string(K) << "." << std::endl;
	
	if (bestSolution != nullptr)
		return true;
	else
		return false;
}


int main(int argc, char *argv[])
{
	srand(time(NULL));

	// Read file
	std::cout << "Parsing file" << std::endl;
	std::vector<Group> vertices;
	if (EASIER_GRAPH)
	{
		vertices = readFile("graph1.txt");
	}
	else
	{
		vertices = readFile("real.txt");
	}

	int id = 0;
	int K = NUM_COLORS;
	if (argc > 3)
	{
		id = atoi(argv[1]);
		K = atoi(argv[2]);
	}

	for (int i = 0; i < 10; i++)
	{
		int colorNum = K;
		while (runGA(i, colorNum, vertices)) // Run algorithm with K colors and then decrease it by 1 until no optimal coloring found.
			colorNum--;
	}
	

	getchar();
}