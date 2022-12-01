# Base for simple simulation of virus transmission between pedestrians on a sidewalk.
# Written by Reid Kerr for use in an assignment in BDA450.
# Please note that this code is not written to be efficient/elegant/etc.!  It is written
# to be brief/simple/transparent, to a reasonable degree.
# There may very well be bugs present!  Moreover, there is very little validation of inputs
# to function calls, etc.  It is generally up to the developer who uses this to build their simulation
# to ensure that their valid state is maintained.

import math

from matplotlib import pyplot as plt, colors
from matplotlib.animation import FuncAnimation
import numpy
import random

rand = random.Random()
SIDEWALK_WIDTH = 10  # This is the y-dimension of the sidewalk
SIDEWALK_LENGTH = 200  # This is the x-dimension of the sidewalk
TRANSPROB = 0.1  # Probability of transmission of virus in 1 time step at distance 1
INFECTED_PROP = 0.1  # The proportion of people who enter the simulation already carrying the virus
INTERARRIVAL = 3 # Average number of time steps between arrivals (each side handled separately)
PROBS = {}
PROBS_2 = {}
PROBS_INITIAL = {}
COUNT_NO_INF = []
OVERALL = []


# Setup for graphical display
colourmap = colors.ListedColormap(["lightgrey", "green", "red", "yellow"])
normalizer = colors.Normalize(vmin=0.0, vmax=3.0)


# stats
def calculate_stats_time(person):
    print("\naverage amount of the time steps to leave the board\n")
    return round(sum([per.time_stamp for per in person])/len(person),0) 


def calculate_stats_rate(probs):
    res = 0
    for key,value in probs.items():
        res += value
        
    plt.plot(probs.keys(), probs.values())
    plt.xlabel("Time") 
    plt.ylabel("Probability") 
    plt.title("Overall infection rate (amount of infected agents)")
    plt.show()

    print("\nprobability of being infected (in general) in 5 mins, on average\n")
    return f"{round((res/len(probs)) * 100, 0)}%"


def calculate_stats_rate_initial(probs_initial):
    res = 0
    for key,value in probs_initial.items():
        res += value
        
    plt.plot(probs_initial.keys(), probs_initial.values())
    plt.xlabel("Time") 
    plt.ylabel("Probability") 
    plt.title("Initial infection rate (amount of red agents)")
    plt.show()
    
    print("\nprobability of being initialy infected in 5 mins, on average\n")
    return f"{round((res/len(probs_initial)) * 100, 0)}%"


def calculate_stats_rate_new(probs_new):
    res = 0
    for key,value in probs_new.items():
        res += value
        
    plt.plot(probs_new.keys(), probs_new.values())
    plt.xlabel("Time") 
    plt.ylabel("Probability") 
    plt.title("Newly infection rate (amount of yellow agents)")
    plt.show()

    print("\nprobability of being newly infected in 5 mins, on average\n")
    return f"{round((res/len(probs_new)) * 100, 0)}%"
    


def calculate_non_infected(non_inf,persons):
    print("\nProbability of leaving the board being uninfected\n")
    return f"{round((len(non_inf)/len(persons)) * 100, 0)}%"


# I will divide agents into the 2 categories, but they will all share smth from this class
class Person:
    def __init__(self, id, sidewalk):
        self.id = id
        self.active = False
        self.sidewalk = sidewalk
        self.infected = True if rand.random() < INFECTED_PROP else False
        self.func_y = lambda coord: max(min(coord, SIDEWALK_WIDTH - 1), 0)
        self.func_x = lambda coord: max(min(coord, SIDEWALK_LENGTH - 1), 0)
        self.newlyinfected = False

    def detect_bump(self,coord): # determine if we will be able to move into desired field
        x,y = coord
        item = self.sidewalk.storage.get_item(x,y)
        if item is None:
            return True       
        return False


    def enter_sidewalk(self, x, y):
        if self.sidewalk.enter_sidewalk(self, x, y):
            self.active = True

    def __str__(self):
        return "id: %d  x: %d  y: %d" % (self.id, self.x, self.y)

    def __repr__(self):
        return str(self.id)+ " " +str(self.active)


class Person_Left(Person): # agents willing to reach out to the right border
    def __init__(self, id, sidewalk, direction):
        Person.__init__(self, id, sidewalk)
        self.direction = direction
        self.x = 0
        self.y = self.func_y(int(rand.gauss(SIDEWALK_WIDTH//2,(SIDEWALK_WIDTH%3)+0.5))) # mean,std
        self.time_stamp = id
        self.initial_time = id
        self.goal = SIDEWALK_LENGTH - 1

    def timer(self):
        if self.x != self.goal:
            self.time_stamp += 1
        return


    def step(self):
        self.timer()
        prob = random.random()
        if prob <= 0.8: # with 80% move forward
            coord = (self.func_x(self.x + self.direction), self.y)
            
            if self.detect_bump(coord): # always check if we can move into desired filed, if we are not able to do so - change direction
                self.sidewalk.attemptmove(self, self.func_x(self.x + self.direction), self.y)
            else:
                choice = random.choice([1,-1])
                coord = (self.x, self.func_y(self.y+choice))
                if self.detect_bump(coord):
                    self.sidewalk.attemptmove(self, self.x, self.func_y(self.y+choice))
                else:
                    choice = 1 if choice == - 1 else -1
                    self.sidewalk.attemptmove(self, self.x, self.func_y(self.y+choice))
                
            
        elif prob > 0.8 and prob <= 0.9: # with 10% move downward
            coord = (self.x, self.func_y(self.y-1))
            if self.detect_bump(coord): # always check if we can move into desired filed, if we are not able to do so - change direction
                self.sidewalk.attemptmove(self, self.x, self.func_y(self.y-1))
            else:
                choice = random.choice([1,-1])
                if choice == 1:
                    coord = (self.func_x(self.x+self.direction), self.y)
                    if self.detect_bump(coord):
                        self.sidewalk.attemptmove(self, self.func_x(self.x+self.direction), self.y)
                    else:
                        self.sidewalk.attemptmove(self, self.x, self.func_y(self.y+1))
                        
                else: 
                    coord = (self.x, self.func_y(self.y+1))
                    if self.detect_bump(coord):
                        self.sidewalk.attemptmove(self, self.x, self.func_y(self.y+1))
                    else:
                        self.sidewalk.attemptmove(self, self.func_x(self.x+self.direction), self.y)
            
        else: # with 10% move upward
            coord = (self.x, self.func_y(self.y+1))
            if self.detect_bump(coord): # always check if we can move into desired filed, if we are not able to do so - change direction
                self.sidewalk.attemptmove(self, self.x, self.func_y(self.y+1))

            else:
                choice = random.choice([1,-1])
                if choice == 1:
                    coord = (self.func_x(self.x+self.direction), self.y)
                    if self.detect_bump(coord):
                        self.sidewalk.attemptmove(self, self.func_x(self.x+self.direction), self.y)
                    else:
                        self.sidewalk.attemptmove(self, self.x, self.func_y(self.y-1))  
                else:
                    coord = (self.x, self.func_y(self.y-1))
                    if self.detect_bump(coord):
                        self.sidewalk.attemptmove(self, self.x, self.func_y(self.y-1))
                    else:
                        self.sidewalk.attemptmove(self, self.func_x(self.x+self.direction), self.y)
                    
            
        self.sidewalk.leave_sidewalk(self) # check, if we have to leave the board

class Person_Right(Person): # agents willing to reach out to the left side of the border, the step func is the same, however direction will be opposite
    def __init__(self, id, sidewalk, direction):
        Person.__init__(self,id, sidewalk)
        self.direction = direction
        self.x = SIDEWALK_LENGTH - 1 
        self.y = self.func_y(int(rand.gauss(SIDEWALK_WIDTH//2,(SIDEWALK_WIDTH%3)+0.5)))
        self.time_stamp = id
        self.initial_time = id
        self.goal = 0

    def timer(self):
        if self.x != self.goal:
            self.time_stamp += 1
        return

    def step(self):
        self.timer()
        prob = random.random()
        if prob <= 0.8:
            coord = (self.func_x(self.x + self.direction), self.y)
            
            if self.detect_bump(coord):
                self.sidewalk.attemptmove(self, self.func_x(self.x + self.direction), self.y)
            else:
                choice = random.choice([1,-1])
                self.sidewalk.attemptmove(self, self.x, self.func_y(self.y+choice))
                
            
        elif prob > 0.8 and prob <= 0.9:
            coord = (self.x, self.func_y(self.y-1))
            if self.detect_bump(coord):
                self.sidewalk.attemptmove(self, self.x, self.func_y(self.y-1))
            else:
                choice = random.choice([1,-1])
                if choice == 1:
                    self.sidewalk.attemptmove(self, self.func_x(self.x+self.direction), self.y)
                else:
                    self.sidewalk.attemptmove(self, self.x, self.func_y(self.y+1))
            
        else:
            coord = (self.x, self.func_y(self.y+1))
            if self.detect_bump(coord):
                self.sidewalk.attemptmove(self, self.x, self.func_y(self.y+1))

            else:
                choice = random.choice([1,-1])
                if choice == 1:
                    self.sidewalk.attemptmove(self, self.func_x(self.x+self.direction), self.y)
                else:
                    self.sidewalk.attemptmove(self, self.x, self.func_y(self.y-1))
        self.sidewalk.leave_sidewalk(self)



class Sidewalk:

    def __init__(self):
        self.storage = SWGrid()
        self.left_side_arrivals = {}
        self.right_side_arrivals = {}

        self.bitmap = [[0.0 for i in range(SIDEWALK_LENGTH)] for j in range(SIDEWALK_WIDTH)]

    def enter_sidewalk(self, person, x, y):
        if self.storage.isoccupied(x, y):
            return False
        self.storage.add_item(x, y, person)
        person.x = x
        person.y = y
        return True


    def leave_sidewalk(self, person): # I made a changes here only for stats purposes - they do not reflect in agents behaviour
        
        if person.x != person.goal: # besides this part, I found it more convenient
            return False
        
        if not person.infected:
            COUNT_NO_INF.append(person)


        person.finished = True

        person.time_stamp -= person.initial_time

        OVERALL.append(person)
            
        self.storage.remove_item(person)


    def attemptmove(self, person, x, y):
        if (abs(person.x - x) + abs(person.y - y)) > 1:
            return False

        if self.storage.isoccupied(x, y):
            return False
        person.x = x
        person.y = y
        self.storage.move_item(x, y, person)
        return True

    def spead_infection(self):
        for person in self.storage.get_list():
            currentx = person.x
            currenty = person.y
            if person.infected:
                for x in range(currentx - 2, currentx + 3):
                    for y in range(currenty - 2, currenty + 3):
                        target = self.storage.get_item(x, y)
                        if target is not None and not target.infected:
                            riskfactor = 1 / ((currentx - x) ** 2 + (currenty - y) ** 2)
                            tranmission_prob = TRANSPROB * riskfactor
                            if rand.random() < tranmission_prob:
                                target.infected = True
                                target.newlyinfected = True

    def refresh_image(self):
        self.bitmap = [[0.0 for i in range(SIDEWALK_LENGTH)] for j in range(SIDEWALK_WIDTH)]
        for person in self.storage.get_list():
            x = person.x
            y = person.y
            colour = 1
            if person.newlyinfected:
                colour = 3
            elif person.infected:
                colour = 2
            self.bitmap[y][x] = colour

    def run_step(self, time_step):
        arrival_time_left = math.ceil(time_step + random.expovariate(1/INTERARRIVAL)) # for each time step, set the arrival times for both left and right agents
        arrival_time_right = math.ceil(time_step + random.expovariate(1/INTERARRIVAL))
        p1 = Person_Left(arrival_time_left, self, 1) # create them
        p2 = Person_Right(arrival_time_right, self, -1)
        self.left_side_arrivals[p1] = arrival_time_left # store them
        self.right_side_arrivals[p2] = arrival_time_right

        copy_1 = {} # just the list of agents who are waiting to enter
        copy_2 = {}

        for key,value in self.left_side_arrivals.items():
            if value == time_step: # if time has come for this agent - this agent enters the sidewalk and we do not copy this agent into dic
                key.enter_sidewalk(key.x, key.y)
                continue
            copy_1[key]=value

        for key,value in self.right_side_arrivals.items():
            if value == time_step:
                key.enter_sidewalk(key.x, key.y)
                continue
            copy_2[key]=value

        self.left_side_arrivals = copy_1 # set copies
        self.right_side_arrivals = copy_2

        for person in self.storage.get_list():
            if person.active:
                person.step()
        self.spead_infection()
        self.refresh_image()


  
        # we will record stats each 5 secs
        if time_step % 5 == 0:
            infected_1 = [per for per in p1.sidewalk.storage.get_list() if (per.infected and not per.newlyinfected)]
            ratio_1 = len(infected_1)/len(p1.sidewalk.storage) if len(p1.sidewalk.storage) != 0 else 0 
            PROBS_INITIAL[time_step] = ratio_1

        if time_step % 5 == 0:
            infected = [per for per in p1.sidewalk.storage.get_list() if per.infected]
            ratio = len(infected)/len(p1.sidewalk.storage) if len(p1.sidewalk.storage) != 0 else 0 
            PROBS[time_step] = ratio


        if time_step % 5 == 0:
            infected_2 = [per for per in p1.sidewalk.storage.get_list() if per.newlyinfected]
            ratio_2 = len(infected_2)/len(p1.sidewalk.storage) if len(p1.sidewalk.storage) != 0 else 0 
            PROBS_2[time_step] = ratio_2





    def isoccupied(self, x, y):
        return self.storage.isoccupied(x, y)



class SWGrid:
    def __init__(self):
        self.dic = dict()

    def isoccupied(self, x, y):
        return (x, y) in self.dic

    def add_item(self, x, y, item):
        self.check_coordinates(x, y)
        self.dic[(x, y)] = item
        return True


    def move_item(self, x, y, item):
        self.check_coordinates(x, y)
        if self.isoccupied(x, y):
            raise Exception("Move to occupied square!")

        oldloc = next(key for key, value in self.dic.items() if value == item)
        del self.dic[oldloc]
        self.add_item(x, y, item)


    def remove_item(self, item):
        oldloc = next(key for key, value in self.dic.items() if value == item)
        if oldloc is None:
            raise Exception('Attempt to remove non-existent item!')
        del self.dic[oldloc]

    def get_item(self, x, y):
        return self.dic.get((x, y), None)


    def get_list(self):
        return list(self.dic.values())

    def check_coordinates(self, x, y):
        if x < 0 or x >= SIDEWALK_LENGTH or y < 0 or y >= SIDEWALK_WIDTH:
            print(x,y)
            raise Exception("Illegal coordinates!")

    def __len__(self):
        return len(self.dic)




sw = Sidewalk()

# Set up graphical display
display = plt.figure(figsize=(15, 5))
image = plt.imshow(sw.bitmap, cmap=colourmap, norm=normalizer, animated=True)

# Track time step
t = 0


# The graphical routine runs the simulation 'clock'; it calls this function at each time step.  This function
# calls the sidewalk's run_step function, as well as updating the display.  You should not implement your simulation
# here, but instead should do so in the run_step method.
def updatefigure(*args):
    global t
    t += 1

    if t % 100 == 0:
        print("Time: %d" % t)
    sw.run_step(t)
    sw.refresh_image()
    image.set_array(sw.bitmap)
    return image,


# Sets up the animation, and begins the process of running the simulation.  As configured below, it will
# run for 1000 steps.  After this point, it will simply stop, but the window will remain open.  You can close
# the window to proceed to the code below these lines (where you could add, for example, output of your statistics.
#
# You can change the speed of the simulation by changing the interval, and the duration by changing frames.
anim = FuncAnimation(display, updatefigure, frames=1000, interval=100, blit=True, repeat=False)
plt.show()


print("Done!")

print(calculate_stats_time(OVERALL))
print(calculate_stats_rate(PROBS))
print(calculate_stats_rate_new(PROBS_2))
print(calculate_stats_rate_initial(PROBS_INITIAL))
print(calculate_non_infected(COUNT_NO_INF,OVERALL))
