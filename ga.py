from abc import ABC, abstractmethod
from numpy.random import permutation, rand, choice
from hashlib import md5

#python makes a mess if a class has the ABCmeta to determine whether it's a (sub)instance of another class
#so I made my own version
def ga_isinstance(obj,cls):
    return cls in obj.__class__.__mro__

class Individual(ABC):

    def __init__(this):
        this.parents= []
        this.initialise()
        this.id = rand()

    @property
    def id(this):
        return this._id

    @id.setter
    def id(this,id):
        this._id = md5(str(id).encode()).hexdigest()

    def add_parent(this,iter,parent):
        this.parents.append((iter,parent))

    @property
    def fitness(this):
        return  this.calculateFitness()

    @abstractmethod
    def __getitem__(this,key):
        ...

    @abstractmethod
    def __setitem__(this, key,value):
        ...

    @abstractmethod
    def __len__(this):
        ...

    @abstractmethod
    def getSequence(this):
        ...

    @abstractmethod
    def initialise(this):
        ...

    @abstractmethod
    def calculateFitness(this):
        ...

    @abstractmethod
    def is_good(this):
        ...

class GAOperator(ABC):
    def __init__(this):
        ...



class UnaryOperator (GAOperator):

    @abstractmethod
    def apply(this,individual):
        ...

class BinaryOperator (GAOperator):
    @abstractmethod
    def apply(this, a,b):
        ...



class Selection(ABC):

    def __init__(this,size=10):
        this.__size = size

    def __len__(this):
        return this.__size

    @property
    def size(this):
        return len(this)

    @size.setter
    def size(this,new_size):
        this.__size = new_size

    @abstractmethod
    def selectPool(this, population):
        ...

class RandomSelection(Selection):
    def selectPool(this, population):
        return list(permutation(len(population))[:len(this)])






class GeneticAlgorithm:
    def __init__(this,population_size=100,selection=None,individual=None,params=None,operators=None,max_iter=1000,track_parents=False):

        this.population_size = population_size
        this.selection = selection
        this.max_iter = max_iter
        this.track_parents = track_parents

        n = sum(operators.values())
        this.operators = { k:(v/n) for k,v in sorted(operators.items(),key=lambda x:x[1],reverse=True)}

        if (params == None):
            params = []

        this.population = [individual(*params) if type(params)==list else individual(**params) for i in range(population_size)]

    def __str__(this):
        value = ""
        for i in range(len(this.population)):
            value+=(f"Individual {i+1}: {this.population[i].calculateFitness()}\n")

        return value.strip()

    def sort_population(this):
        this.population = sorted(this.population, key=lambda x: x.fitness)

    def evolve(this):
        i=0
        stop = False

        while (i<this.max_iter) and (not stop):
            this.sort_population()



            stop = this.population[0].fitness == 0 #reached global maximum
            if (stop):
                continue

            if (len(this.population)>this.population_size):
                #let's kill individuals with higher fitness
                this.population = this.population[:this.population_size]

            #print iteration:
            print(f"\nIteration ({i+1}/{this.max_iter})")
            print(this)

            pool_idx = this.selection.selectPool(this.population)

            for idx in pool_idx:
                ind = this.population[idx]

                if (not ind.is_good()):
                    continue

                operator_applied = False

                for operator,prob in this.operators.items():
                    x = rand()
                    if (x<=prob):
                        if (ga_isinstance(operator,UnaryOperator)):
                            parent=ind
                            ind = operator.apply(parent)
                            operator_applied = True

                            if (this.track_parents):
                                ind.add_parent(i,parent)
                        elif (ga_isinstance(operator, BinaryOperator)):
                            parent = ind
                            #select a random sample from the selected individuals for mating
                            pool_idx2 = pool_idx.copy()
                            pool_idx2.remove(idx)
                            parent2 = this.population[choice(pool_idx2)]

                            ind = operator.apply(parent,parent2)
                            operator_applied = True

                            if (this.track_parents):
                                ind.add_parent(i,(parent,parent2))

                if (operator_applied):
                    ind.id = rand()
                    ind.calculateFitness()
                    this.population.append(ind)

            i+=1

        this.sort_population()