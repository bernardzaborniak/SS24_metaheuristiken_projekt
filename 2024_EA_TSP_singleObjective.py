# -*- coding: utf-8 -*-
"""
Created for Netzwerke & Metaheuristiken (Sommersemester 2024)

Modified version of https://github.com/ezstoltz/genetic-algorithm/blob/master/genetic_algorithm_TSP.ipynb
(description https://towardsdatascience.com/evolution-of-a-salesman-a-complete-genetic-algorithm-tutorial-for-python-6fe5d2b3ca35)

Modified for multicriteria TSP
"""



from itertools import product
import numpy as np, random, operator, pandas as pd, matplotlib.pyplot as plt

#Create necessary classes and functions
#Create class to handle "cities
class City:
    def __init__(self, nr, traffic, x, y):
        self.nr = nr
        #attribute used for stress calculation
        self.traffic = traffic
        #coordinates used for distance calculation
        self.x = x
        self.y = y
    
    #calculate distance to other city  
    def distance(self, city):
        xDis = abs(self.x - city.x)
        yDis = abs(self.y - city.y)
        distance = np.sqrt((xDis ** 2) + (yDis ** 2))
        return distance
    
    #calculate stress on way to other city
    def stress(self,city):
        stress = self.traffic*city.traffic
        if (self.nr > city.nr):
            if self.nr % city.nr == 0:
                stress = stress /2.5
        elif self.nr > 1 and city.nr % self.nr == 0:
            stress = stress /2.5
        return stress

    #provide information about city
    def __repr__(self):
        return "C"+str(self.nr)+"_"+"(" + str(self.x) + "," + str(self.y) + ")_(T:"+str(self.traffic) +")"

#Create a fitness function
class Fitness:
    def __init__(self, route):
        self.route = route
        self.distance = 0
        self.stress = 0
        self.fitnessDistanceBased = 0.0
        self.fitnessStressBased = 0.0
    
    #fitness calculation for objective: distance
    #1. distance calculation
    def routeDistance(self):
        if self.distance ==0:
            pathDistance = 0
            for i in range(0, len(self.route)):
                fromCity = self.route[i]
                toCity = None
                if i + 1 < len(self.route):
                    toCity = self.route[i + 1]
                else:
                    toCity = self.route[0]
                pathDistance += fromCity.distance(toCity)
            self.distance = pathDistance
        return self.distance
    
    #2. fitness = 1/distance
    def routeFitnessDistanceBased(self):
        if self.fitnessDistanceBased == 0:
            self.fitnessDistanceBased = 1 / float(self.routeDistance())
        return self.fitnessDistanceBased
    
    #fitness calculation for objective: stress
    #1. stress calculation
    def routeStress(self):
        if self.stress ==0:
            pathStress = 0
            for i in range(0, len(self.route)):
                fromCity = self.route[i]
                toCity = None
                if i + 1 < len(self.route):
                    toCity = self.route[i + 1]
                else:
                    toCity = self.route[0]
                pathStress += fromCity.stress(toCity)
            self.stress = pathStress
        return self.stress
    
    #2. fitness = 1/stress
    def routeFitnessStressBased(self):
        if self.fitnessStressBased == 0:
            self.fitnessStressBased = 1 / float(self.routeStress())
        return self.fitnessStressBased


#Create our initial population
#Route generator
def createRoute(cityList):
    route = random.sample(cityList, len(cityList))
    return route

#Create first "population" (list of routes)
def initialPopulation(popSize, cityList, specialInitialSolutions):
    population = []
    
    #TODO: Hinzufügen der speziellen Initiallösungen aus specialInitialSolutions
    
    numberInitialSolutions = len(specialInitialSolutions)
    # print ("Number of special initial solutions:" + str(numberInitialSolutions))

    for i in range(0, popSize): #TODO gegebenenfalls anpassen, falls bereits Initiallösungen hinzugefügt
        population.append(createRoute(cityList))
    return population

#Create the genetic algorithm
#Rank individuals
# use 1 = DISTANCE BASED RANKING
# use 2 = STRESS BASED RANKING
def rankRoutes(population, objectiveNrUsed):
    fitnessResults = {}
    if (objectiveNrUsed == 1):
        for i in range(0,len(population)):
            fitnessResults[i] = Fitness(population[i]).routeFitnessDistanceBased()
    elif (objectiveNrUsed == 2):
        for i in range(0,len(population)):
            fitnessResults[i] = Fitness(population[i]).routeFitnessStressBased()
    return sorted(fitnessResults.items(), key = operator.itemgetter(1), reverse = True)

#Create a selection function that will be used to make the list of parent routes
def selection(popRanked, eliteSize):
    selectionResults = []
    #TODO: Z.B. Turnierbasierte Selektion statt fitnessproportionaler Selektion
    # roulette wheel by calculating a relative fitness weight for each individual
    df = pd.DataFrame(np.array(popRanked), columns=["Index","Fitness"])
    df['cum_sum'] = df.Fitness.cumsum()
    df['cum_perc'] = 100*df.cum_sum/df.Fitness.sum()

    #We’ll also want to hold on to our best routes, so we introduce elitism
    for i in range(0, eliteSize):
        selectionResults.append(popRanked[i][0])
    #we compare a randomly drawn number to these weights to select our mating pool
    for i in range(0, len(popRanked) - eliteSize):
        pick = 100*random.random()
        for i in range(0, len(popRanked)):
            if pick <= df.iat[i,3]:
                selectionResults.append(popRanked[i][0])
                break
    return selectionResults

#Create mating pool
def matingPool(population, selectionResults):
    matingpool = []
    for i in range(0, len(selectionResults)):
        index = selectionResults[i]
        matingpool.append(population[index])
    return matingpool

# Create a crossover function for two parents to create one child
def breed(parent1, parent2):
    child = []
    childP1 = []
    childP2 = []
    
    geneA = int(random.random() * len(parent1))
    geneB = int(random.random() * len(parent1))
    
    startGene = min(geneA, geneB)
    endGene = max(geneA, geneB)

    #In ordered crossover, we randomly select a subset of the first parent string
    for i in range(startGene, endGene):
        childP1.append(parent1[i])

    #and then fill the remainder of the route with the genes from the second parent
    #in the order in which they appear, 
    #without duplicating any genes in the selected subset from the first parent      
    childP2 = [item for item in parent2 if item not in childP1]

    child = childP1 + childP2
    return child

#Create function to run crossover over full mating pool
def breedPopulation(matingpool, eliteSize):
    children = []
    length = len(matingpool) - eliteSize
    pool = random.sample(matingpool, len(matingpool))

    #we use elitism to retain the best routes from the current population.
    for i in range(0,eliteSize):
        children.append(matingpool[i])

    #we use the breed function to fill out the rest of the next generation.    
    for i in range(0, length):
        child = breed(pool[i], pool[len(matingpool)-i-1])
        children.append(child)
    return children

#Create function to mutate a single route
#we’ll use swap mutation.
#This means that, with specified low probability, 
#two cities will swap places in our route.
def mutate(individual, mutationRate):
    for swapped in range(len(individual)):
        if(random.random() < mutationRate):
            swapWith = int(random.random() * len(individual))
            
            city1 = individual[swapped]
            city2 = individual[swapWith]
            
            individual[swapped] = city2
            individual[swapWith] = city1
    return individual

#Create function to run mutation over entire population
def mutatePopulation(population, mutationRate):
    mutatedPop = []
    
    for ind in range(0, len(population)):
        mutatedInd = mutate(population[ind], mutationRate)
        mutatedPop.append(mutatedInd)
    return mutatedPop

#Put all steps together to create the next generation
 
#First, we rank the routes in the current generation using rankRoutes.
#We then determine our potential parents by running the selection function,
#    which allows us to create the mating pool using the matingPool function.
#Finally, we then create our new generation using the breedPopulation function 
# and then applying mutation using the mutatePopulation function. 

def nextGeneration(currentGen, eliteSize, mutationRate, objectiveNrUsed):
    popRanked = rankRoutes(currentGen,objectiveNrUsed)
    selectionResults = selection(popRanked, eliteSize)
    matingpool = matingPool(currentGen, selectionResults)
    children = breedPopulation(matingpool, eliteSize)
    nextGeneration = mutatePopulation(children, mutationRate)
    return nextGeneration

#Final step: create the genetic algorithm
def plotPopulationAndObjectiveValues(population,title):
    distance = []
    stress = []
    for route in population:
        distance.append(Fitness(route).routeDistance())
        stress.append(Fitness(route).routeStress())
    plt.scatter(distance,stress,marker = "o",color="black")
    plt.ylabel('Stress')
    plt.xlabel('Distance')
    plt.title(title)
    plt.show()
        

def geneticAlgorithm(objectiveNrUsed, specialInitialSolutions, population, popSize, eliteSize, mutationRate, generations):
    #create initial population
    pop = initialPopulation(popSize, population, specialInitialSolutions)
    
    #provide statistics about best initial solution with regard to chosen objective
    # print("Initial objective: " + str(1 / rankRoutes(pop,objectiveNrUsed)[0][1]))
    bestRouteIndex = rankRoutes(pop,objectiveNrUsed)[0][0]
    bestRoute = pop[bestRouteIndex]
    # print("Initial distance : " + str(Fitness(bestRoute).routeDistance()))
    # print("Initial stress:    " + str(Fitness(bestRoute).routeStress()))
    
    # plotRoute(bestRoute, "Best initial route")
    
    #plot intial population with regard to the two objectives
    # plotPopulationAndObjectiveValues(pop, "Initial Population")
    
    #store infos to plot progress when finished
    progressDistance = []
    progressDistance.append(1 / rankRoutes(pop,1)[0][1])
    progressStress = []
    progressStress.append(1 / rankRoutes(pop,2)[0][1])
    
    #create new generations of populations
    for i in range(0, generations):
        pop = nextGeneration(pop, eliteSize, mutationRate,objectiveNrUsed)
        #store infos to plot progress when finished
        progressDistance.append(1 / rankRoutes(pop,1)[0][1])
        progressStress.append(1 / rankRoutes(pop,2)[0][1])
        
    #plot progress - distance
    # plt.plot(progressDistance)
    # plt.ylabel('Distance')
    # plt.xlabel('Generation')
    # plt.title('Progress of Distance Minimization')
    # plt.show()
    #plot progress - stress
    # plt.plot(progressStress)
    # plt.ylabel('Stress')
    # plt.xlabel('Generation')
    # plt.title('Progress of Stress Minimization')
    # plt.show()
    
    #provide statistics about best final solution with regard to chosen objective
    # print("Final objective: " + str(1 / rankRoutes(pop,objectiveNrUsed)[0][1]))
    bestRouteIndex = rankRoutes(pop,objectiveNrUsed)[0][0]
    bestRoute = pop[bestRouteIndex]
    
    print("Final distance : " + str(Fitness(bestRoute).routeDistance()))
    print("Final stress:    " + str(Fitness(bestRoute).routeStress()))
    
    #Provide special initial solutions     <<<<<<<<<<<
    #print city Indizes for initial solution
    bestRouteIndizes = []
    for city in bestRoute:
        bestRouteIndizes.append(city.nr)
        
    # print("---- ")
    # print("City Numbers of Best Route")
    # print(bestRouteIndizes)
    # print("---- ")
    
    #plot final population with regard to the two objectives
    # plotPopulationAndObjectiveValues(pop, "Final Population")
    
    return bestRoute

#Running the genetic algorithm
#Create list of cities
cityList = []

random.seed(44)
for i in range(1,26):
    cityList.append(City(nr= i, traffic=int(random.random()*40), x=int(random.random() * 200), y=int(random.random() * 200)))
    
# print(cityList)


def plotRoute(cityList, title):
    x = []
    y = []
    for item in cityList:
        x.append(item.x)
        y.append(item.y)
        plt.annotate(item.nr,(item.x,item.y))
    x.append(cityList[0].x)
    y.append(cityList[0].y)
    plt.plot(x,y,marker = "x")
    plt.ylabel('Y-Koordinate')
    plt.xlabel('X-Koordinate')
    plt.title(title)
    plt.show()    

def getCityBasedOnNr(cityList,nr):
    if (nr <= 0 or nr > len(cityList)):
        print("Something is wrong!")
        return cityList[0]
    else:
        return cityList[nr-1]  

#Provide special initial solutions     <<<<<<<<<<<
cityNumbersRoute1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]


route1 = []
for nr in cityNumbersRoute1:
    route1.append(getCityBasedOnNr(cityList,nr))
    

initialSolutionsList = []
#TODO: Spezielle Intiallösungen der initialSolutionsList übergeben    
    
#Run the genetic algorithm
#modify parameters popSize, eliteSize, mutationRate, generations to search for the best solution
#modify objectiveNrUsed to use different objectives:
# 1= Minimize distance, 2 = Minimize stress
# bestRoute = geneticAlgorithm(objectiveNrUsed=1, specialInitialSolutions = initialSolutionsList, population=cityList, popSize=500, eliteSize=20, mutationRate=0.02, generations=500)
# print(bestRoute)

def evaluate_ga_parameters(objectiveNrUsed, popSize, eliteSize, mutationRate, generations, cityList, initialSolutionsList):
    print("starting with params: ", popSize, eliteSize, mutationRate, generations)
    bestRoute = geneticAlgorithm(objectiveNrUsed=objectiveNrUsed, specialInitialSolutions=initialSolutionsList,
                                 population=cityList, popSize=popSize, eliteSize=eliteSize, 
                                 mutationRate=mutationRate, generations=generations)
    if objectiveNrUsed == 1:
        return Fitness(bestRoute).routeDistance()
    elif objectiveNrUsed == 2:
        return Fitness(bestRoute).routeStress()

param_space = {
    'popSize': [50, 100, 150],
    'eliteSize': [10, 20, 30],
    'mutationRate': [0.002, 0.001, 0.0005],
    'generations': [450, 500, 550]
}

# List to store results
results = []

n_samples = 20
for _ in range(n_samples):
    popSize = random.choice(param_space['popSize'])
    eliteSize = random.choice(param_space['eliteSize'])
    mutationRate = random.choice(param_space['mutationRate'])
    generations = random.choice(param_space['generations'])
    
    score = evaluate_ga_parameters(objectiveNrUsed=2, popSize=popSize, eliteSize=eliteSize, 
                                   mutationRate=mutationRate, generations=generations, 
                                   cityList=cityList, initialSolutionsList=initialSolutionsList)
    results.append((score, popSize, eliteSize, mutationRate, generations))

# Find the best parameters
best_result = min(results, key=lambda x: x[0])
best_score, best_popSize, best_eliteSize, best_mutationRate, best_generations = best_result

print(f'Best Score: {best_score}')
print(f'Best Parameters - popSize: {best_popSize}, eliteSize: {best_eliteSize}, mutationRate: {best_mutationRate}, generations: {best_generations}')
