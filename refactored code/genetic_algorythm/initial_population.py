from .route import Route
from .city import City
import numpy as np, random, operator, pandas as pd, matplotlib.pyplot as plt

def create_random_route(cityList) -> Route:
    route = random.sample(cityList, len(cityList))
    return Route(route)

def initialPopulation(popSize, cityList, specialInitialSolutions: list[Route]):
    population:list[Route] = []
    
    #TODO: Hinzufügen der speziellen Initiallösungen aus specialInitialSolutions
    for i in range(len(specialInitialSolutions)):
        population.append(specialInitialSolutions[i])

    numberInitialSolutions = len(specialInitialSolutions)
    print ("Number of special initial solutions:" + str(numberInitialSolutions))
    #for i in range(0, popSize):
    for i in range(numberInitialSolutions, popSize):
        population.append(create_random_route(cityList))
    return population

def get_special_initial_solutions(all_cities:list[City]) -> list[Route]:
    
    # initial solution 1 -> distance
    potential_next_cities_d = all_cities.copy()

    initial_solution_low_distance:list[City] = [potential_next_cities_d[0]]
    potential_next_cities_d.remove(potential_next_cities_d[0])

    while len(potential_next_cities_d) > 0:        
        lowest_distance_so_far = float('inf')
        #next_city:City = None
        
        for i in range(len(potential_next_cities_d)):
            
            distance = initial_solution_low_distance[len(initial_solution_low_distance)-1].distance(potential_next_cities_d[i])
            if(distance < lowest_distance_so_far):
                lowest_distance_so_far = distance
                next_city = potential_next_cities_d[i]
                #print(f"distance between {initial_solution_low_distance[len(initial_solution_low_distance)-1]} and {potential_next_cities_d[i]} is {distance}")
                
        initial_solution_low_distance.append(next_city)
        potential_next_cities_d.remove(next_city)
     
    print("\n initial solution cities: ", initial_solution_low_distance)
    distance_optimised_route = Route(initial_solution_low_distance)
    
     # # initial solution 2 -> stress
    # potential_next_cities_s = cityList.copy()

    # initial_solution_low_stress:list[City] = [potential_next_cities_s[0]]
    # potential_next_cities_s.remove(potential_next_cities_s[0])

    # while len(potential_next_cities_s) > 0:        
    #     lowest_stress_so_far = float('inf')
    #     next_city = None
        
    #     for i in range(len(potential_next_cities_s)):
    #         stress = initial_solution_low_distance[len(initial_solution_low_distance)-1].stress(potential_next_cities_s[i])
    #         if(stress < lowest_stress_so_far):
    #             lowest_stress_so_far = stress
    #             next_city = potential_next_cities_s[i]
                
    #     initial_solution_low_distance.append(next_city)
    #     potential_next_cities_s.remove(next_city)
     
     
     
    # print("solution low stress: ", initial_solution_low_stress)
    print("distance_optimised_route type: ",type(distance_optimised_route))
    print("solution low distance: ", initial_solution_low_distance)
    print("solution low distance - distance : ", distance_optimised_route.routeDistance())
    
    
    #return [initial_solution_low_distance, initial_solution_low_stress]
    return [distance_optimised_route,distance_optimised_route,distance_optimised_route,distance_optimised_route]