
import math
import time
from matplotlib import pyplot as plt, colors
from matplotlib.animation import FuncAnimation
import random
import numpy


SIDEWALK_WIDTH = 10  # This is the y-dimension of the sidewalk
SIDEWALK_LENGTH = 200  # This is the x-dimension of the sidewalk
TRANSPROB = 0.1  # Probability of transmission of virus in 1 time step at distance 1
INFECTED_PROP = 0.1  # The proportion of people who enter the simulation already carrying the virus
INTERARRIVAL = 3 # Average number of time steps between arrivals (each side handled separately)
PASSIVE =  0.2 # 1 - PASSIVE = probability of following distance as soon as possible, if agent was blocked and was unable to move. This probability should low, due to the very narrow width
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
    #print([per.time_stamp for per in person])
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

    print("\nprobability of being infected in 5 mins (in general), on average\n")
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
        self.infected = True if random.random() < INFECTED_PROP else False
        self.func_y = lambda coord: max(min(coord, SIDEWALK_WIDTH - 1), 0)
        self.func_x = lambda coord: max(min(coord, SIDEWALK_LENGTH - 1), 0)
        self.newlyinfected = False
        self.finished = False

    def move_coord(self,pos,x,y,direction): # check for corresponding pos, if we can more there and follow the distance measures
        if pos == "Straight":
            pos_coords = [(self.func_x(x+direction),y),(x,self.func_y(y-1)),(x,self.func_y(y+1)),(self.func_x(x+direction),self.func_y(y-1)),(self.func_x(x+direction),self.func_y(y+1))]
            for pos_x,pos_y in pos_coords:
                if self.sidewalk.storage.isoccupied(pos_x,pos_y):
                    return False
            return True
        elif pos == "Up":
            pos_coords = [(self.func_x(x+direction),y),(self.func_x(x-direction),y),(x,self.func_y(y+1)),(self.func_x(x+direction),self.func_y(y+1)),(self.func_x(x-direction),self.func_y(y+1))]
            for pos_x,pos_y in pos_coords:
                if self.sidewalk.storage.isoccupied(pos_x,pos_y):
                    return False
            return True
        
        else: 
            pos_coords = [(self.func_x(x+direction),y),(self.func_x(x-direction),y),(x,self.func_y(y-1)),(self.func_x(x+direction), self.func_y(y-1)),(self.func_x(x-direction), self.func_y(y-1))]
            for pos_x,pos_y in pos_coords:
                if self.sidewalk.storage.isoccupied(pos_x,pos_y):
                    return False
            return True

    

    def scan_storage(self,direction): # scan stoge for available coords
        merge_dics = lambda one,two: {**one,**two}
        possible_coords = {"Down":(self.x,self.func_y(self.y-1)),"Up":(self.x,self.func_y(self.y+1)),"Straight":(self.func_x(self.x+direction),self.y)} # we can go either straight, up or down
        q = {}

        for pos,coords in possible_coords.items(): # firstly, we obesrve whether above mentioned positions for us are occupied or not
            x,y = coords[0],coords[1]
            if self.sidewalk.storage.isoccupied(x,y):
                continue

            q[pos] = coords
            
        possible_coords = q
        spare = possible_coords.copy()

        if len(possible_coords) == 0: # if there are no pos at all - return 
            return -1

        t_list = []
        
        for position,coordinates in possible_coords.items(): # then, we see - can we move for the available positions and remain distance
            if self.move_coord(position, coordinates[0],coordinates[1],direction):
                t_list.append((position, [coordinates[0],coordinates[1]]))
            else:
                t_list.append((position, False)) # if not - False


        for outcome in t_list: # if we cannot move in this direction and remian dist - del this coord
            if outcome[1] is False:
                del possible_coords[outcome[0]]


        if len(possible_coords) == 3: # if all 3 coords are good to go - return true
            return True
        
        if len(possible_coords) == 0: # if none of them is good to go - we return those coords, in which we can physically move, though we will break the rools of dist
            if "Straight" in spare:
                prob = random.random()
                if prob <= 0.8: # priority to the straight if present
                    value = spare["Straight"]
                    del spare["Straight"]
                    return False,value,spare
                else:
                    sp = {}
                    sp["Straight"] = spare["Straight"]
                    
                    del spare["Straight"]
                    
                    if len(spare) == 0:
                        return False,sp["Straight"],spare
                        
                    lst = [i for i in spare.keys()]
                    choice = random.choice(lst)
                    value = spare[choice]
                    del spare[choice]
                    spare = merge_dics(spare,sp)
                    return False,value,spare
                                    
            else:
                lst = [i for i in spare.keys()]
                choice = random.choice(lst)
                value = spare[choice]
                del spare[choice]
                return False,value,spare


        if len(possible_coords) == 1: # if we have one coord that guarantees us with dist, return this coord plus of the other positions where we can go physically
            lst = [(coord[0],coord[1]) for coord in possible_coords.values()]
            another = list(set(spare).difference(set(possible_coords)))

            pos_1 = dict([(key,spare[key]) for key in another])
            
            return lst[0],pos_1


        if len(possible_coords) == 2: # same as with 1, but here return 2 coords
            if "Straight" in possible_coords:
                prob = random.random()
                if prob <= 0.8:
                    value = possible_coords["Straight"]
                    another = list(set(spare).difference(set(possible_coords)))
                    del possible_coords["Straight"]
                    pos_1 = dict([(key,spare[key]) for key in another])
                    pos_1 = merge_dics(possible_coords,pos_1)
                    return value,pos_1
                else:
                    another = list(set(spare).difference(set(possible_coords)))
                    pos_1 = dict([(key,spare[key]) for key in another])
                    pos_2 = {}
                    pos_2["Straight"] = possible_coords["Straight"]
                    pos_1 = merge_dics(pos_2,pos_1)
                    del possible_coords["Straight"]
                    lst = [(coord[0],coord[1]) for coord in possible_coords.values()]
                    return lst[0],pos_1
            else:
                another = list(set(spare).difference(set(possible_coords)))
                pos_1 = dict([(key,spare[key]) for key in another])
                one,two = possible_coords.keys()
                lst = [one,two]
                choice = random.choice(lst)
                value = possible_coords[choice]
                del possible_coords[choice]
                pos_1 = merge_dics(possible_coords,pos_1)
                return value,pos_1

                

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


#################################################################

class Person_Left(Person):
    def __init__(self, id, sidewalk, direction):
        Person.__init__(self, id, sidewalk)
        self.direction = direction
        self.x = 0
        self.y = self.func_y(int(random.gauss(SIDEWALK_WIDTH//2,(SIDEWALK_WIDTH%3)+0.5)))
        self.goal = SIDEWALK_LENGTH - 1
        self.time_stamp = id
        self.initial_time = id


    def timer(self):
        if self.x != self.goal:
            self.time_stamp += 1
        return



    def attempt_move_user(self,prob): # general behaviour, if we can move anywhere, simialr to part 1
        if prob <= 0.8:
            coord = (self.func_x(self.x + self.direction), self.y)
            
            if self.detect_bump(coord):
                self.sidewalk.attemptmove(self, self.func_x(self.x + self.direction), self.y)
            else:
                choice = random.choice([1,-1])
                coord = (self.x, self.func_y(self.y+choice))
                if self.detect_bump(coord):
                    self.sidewalk.attemptmove(self, self.x, self.func_y(self.y+choice))
                else:
                    choice = 1 if choice == - 1 else -1
                    self.sidewalk.attemptmove(self, self.x, self.func_y(self.y+choice))
                
            
        elif prob > 0.8 and prob <= 0.9:
            coord = (self.x, self.func_y(self.y-1))
            if self.detect_bump(coord):
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
            
        else:
            coord = (self.x, self.func_y(self.y+1))
            if self.detect_bump(coord):
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

    def step(self):
        self.timer()
        prob = random.random()
        bool_val = self.scan_storage(self.direction) # scan our storage

        if bool_val == -1:
            return
        # here, we know that we cannot move in such order that guarantees us with distance
        # hence, with some fixed prob, we will violate the rules of distance and move in any available direction
        # note that this prob has to be relatively low, because otherwise agents will be stuck
    
        if isinstance(bool_val,tuple) and bool_val[0] is False: 
            possible_coord = bool_val[1]
            wait_prob = random.random()
            if wait_prob <= PASSIVE: # if not - just wait
                self.sidewalk.leave_sidewalk(self)
                return
            else: # else we move
                if self.detect_bump(possible_coord):
                    self.sidewalk.attemptmove(self, possible_coord[0],possible_coord[1])
                    self.sidewalk.leave_sidewalk(self)
                    return
                else:
                    coords = bool_val[2]

                    if len(coords) == 0:
                        return
                    else:
                        for x,y in coords.values():
                            if self.detect_bump((x,y)):
                                self.sidewalk.attemptmove(self, x,y)
                                self.sidewalk.leave_sidewalk(self)
                                return
                            else:
                                continue
                        return            
                
                
        if isinstance(bool_val,tuple) and bool_val[0] is not False: # if we actually can move and be in distance - do it!
            x,y = bool_val[0][0],bool_val[0][1]
            
            if self.detect_bump((x,y)):
                self.sidewalk.attemptmove(self, x, y)
                self.sidewalk.leave_sidewalk(self)
                return
            else:
                coords = bool_val[2]
                if len(coords) == 0:
                    return
                else:
                    for x,y in coords.values():
                        if self.detect_bump((x,y)):
                            self.sidewalk.attemptmove(self, x,y)
                            self.sidewalk.leave_sidewalk(self)
                            return
                        else:
                            continue
                    return


        if bool_val is True: # if we can move anywhere and we will not violate rules
            self.attempt_move_user(prob)
            self.sidewalk.leave_sidewalk(self)
            return

        
            



class Person_Right(Person): # the same as for the left person, although direction and goal are different
    def __init__(self, id, sidewalk, direction):
        Person.__init__(self,id, sidewalk)
        self.direction = direction
        self.x = SIDEWALK_LENGTH - 1 
        self.y = self.func_y(int(random.gauss(SIDEWALK_WIDTH//2,(SIDEWALK_WIDTH%3)+0.5)))
        self.goal = 0
        self.time_stamp = id
        self.initial_time = id


    def timer(self):
        if self.x != self.goal:
            self.time_stamp += 1
        return

    def attempt_move_user(self,prob):
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

    
    def step(self):
        self.timer()
        prob = random.random()
        bool_val = self.scan_storage(self.direction)

        if bool_val == -1:
            return

        if isinstance(bool_val,tuple) and bool_val[0] is False:
            possible_coord = bool_val[1]
            wait_prob = random.random()
            if wait_prob <= PASSIVE:
                self.sidewalk.leave_sidewalk(self)
                return
            else:
                if self.detect_bump(possible_coord):
                    self.sidewalk.attemptmove(self, possible_coord[0],possible_coord[1])
                    self.sidewalk.leave_sidewalk(self)
                    return
                else:
                    coords = bool_val[2]

                    if len(coords) == 0:
                        return
                    else:
                        for x,y in coords.values():
                            if self.detect_bump((x,y)):
                                self.sidewalk.attemptmove(self, x,y)
                                self.sidewalk.leave_sidewalk(self)
                                return
                            else:
                                continue
                        return            
                
                
        if isinstance(bool_val,tuple) and bool_val[0] is not False:
            x,y = bool_val[0][0],bool_val[0][1]
            
            if self.detect_bump((x,y)):
                self.sidewalk.attemptmove(self, x, y)
                self.sidewalk.leave_sidewalk(self)
                return
            else:
                coords = bool_val[2]
                if len(coords) == 0:
                    return
                else:
                    for x,y in coords.values():
                        if self.detect_bump((x,y)):
                            self.sidewalk.attemptmove(self, x,y)
                            self.sidewalk.leave_sidewalk(self)
                            return
                        else:
                            continue
                    return
                

        if bool_val is True:
            self.attempt_move_user(prob)
            self.sidewalk.leave_sidewalk(self)
            return




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


    def leave_sidewalk(self, person): # changes were made only for stats purposes
        if person.x != person.goal:
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
                            if random.random() < tranmission_prob:
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

    def run_step(self, time_step): # the same behaviour as for the 1st part
        arrival_time_left = math.ceil(time_step + random.expovariate(1/INTERARRIVAL))
        arrival_time_right = math.ceil(time_step + random.expovariate(1/INTERARRIVAL))
        p1 = Person_Left(arrival_time_left, self, 1)
        p2 = Person_Right(arrival_time_right, self, -1)
        

        
        self.left_side_arrivals[p1] = arrival_time_left
        self.right_side_arrivals[p2] = arrival_time_right

        copy_1 = {}
        copy_2 = {}

        for key,value in self.left_side_arrivals.items():
            if value == time_step:
                key.enter_sidewalk(key.x, key.y)
                continue
            copy_1[key]=value

        for key,value in self.right_side_arrivals.items():
            if value == time_step:
                key.enter_sidewalk(key.x, key.y)
                continue
            copy_2[key]=value
            


        self.left_side_arrivals = copy_1
        self.right_side_arrivals = copy_2
        

        for person in self.storage.get_list():
            if person.active:
                person.step()
        self.spead_infection()

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
