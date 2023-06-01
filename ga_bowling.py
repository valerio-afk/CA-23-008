from ga import UnaryOperator, BinaryOperator,Individual
from bowling import Game,Roll
from numpy.random import randint
import numpy as np

rroll = lambda : randint(0,Roll.PINS+1) #get random roll

def fixFrame(rolls,last=False):
    # clip to 0
    rolls = [max(0, x) for x in rolls]
    # clip to 10
    rolls = [min(Roll.PINS, x) for x in rolls]

    if (last):
        if (sum(rolls[:2])<Roll.PINS):
            return fixFrame(rolls[:2],False) #if the first two rolls are less than a strike, then it's an open frame - treat normally and discard the 3rd roll (if any)
        else:
            rolls += [0] * (3 - (len(rolls)))  # add extra rolls if missing (with no points)
            if (rolls[0] == Roll.PINS) and (rolls[1] == Roll.PINS):
                return rolls #all good here
            elif (rolls[0] == Roll.PINS): #strike + 2 rolls (treaded as a normal frame)
                return [rolls[0]] + fixFrame(rolls[1:],False)
            else:
                return fixFrame(rolls[0:2], False) + [rolls[-1]] #first 2 rolls are treated as normal frame + last roll
    else:

        if (rolls[0] == Roll.PINS):
            rolls = [rolls[0]] #if strike, just need first roll

        if (sum(rolls)>Roll.PINS):
            rolls[1] = Roll.PINS - rolls[0] #if two rolls are greater than 10, then it's a spare

        #if a strike is converted in a non-strike, we need to add an extra roll
        if (rolls[0]<Roll.PINS) and (len(rolls)<2):
            rolls.append(0)


        return rolls

class BowlingIndividual(Game,Individual):

    def __init__(this,target_score):
        this.target_score = target_score
        super().__init__()
        super(Game,this).__init__()

    def getSequence(this):
        return this.getFrames()

    def calculateFitness(this):
        return abs(this.target_score-this.score) if this.is_good() else np.Inf

    def is_good(this):
        return True #len(this) == Game.FRAMES

    def initialise(this):
        for i in range(Game.FRAMES):
            rolls = []

            more_rolls = True

            while more_rolls:
                rolls.append(rroll())


                if (i==(Game.FRAMES-1)):
                    if ( (len(rolls)==2) and (sum(rolls[:2]) < Roll.PINS) ) or (len(rolls)==3):
                        more_rolls = False
                else:
                    if (rolls[0] == Roll.PINS) or (len(rolls)==2):
                        more_rolls=False

            rolls = fixFrame(rolls,i == (Game.FRAMES-1))

            this[i] = rolls

class BowlingMutation(UnaryOperator):
    def apply(this,individual):
        new_ind = individual.copy()

        idx = randint(0,Game.FRAMES)

        frame = new_ind[idx]

        values = fixFrame([x + (-1)**randint(2,4) for x in frame], idx == (Game.FRAMES-1))

        new_ind[idx] = values

        return new_ind

class BowlingCrossover(BinaryOperator):
    def apply(this,a,b):
        new_ind = a.copy()

        cut_point = randint(1,Game.FRAMES-1)

        for i in range(cut_point,Game.FRAMES):
            new_ind[i] = b[i]

        return new_ind