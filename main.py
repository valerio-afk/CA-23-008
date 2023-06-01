from ga_bowling import *
from ga import GeneticAlgorithm,RandomSelection

target_score=300

ga = GeneticAlgorithm(selection=RandomSelection(),
                      individual=BowlingIndividual,
                      params=[target_score],
                      operators={BowlingMutation():0.5,BowlingCrossover():0.5},
                      track_parents=False)
ga.evolve()

print()

for i in range(5):
    ind = ga.population[i]
    print(f"Individual: {ind.id}")
    print(f"{ind}\n")
