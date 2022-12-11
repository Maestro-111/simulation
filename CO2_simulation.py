
import scipy.stats as st
import numpy as np
from matplotlib import pyplot as plt, colors
from matplotlib.animation import FuncAnimation
import random
import math
import time
from numpy import mean
import math
from numpy import std
from numpy import percentile

SIDEWALK_WIDTH = 200
SIDEWALK_LENGTH = 940
AVERAGE_TIME = 30 
BUNCH_OF_CARS = 10  
AVERAGE_SPEED = 23
OBGON = 0.15 # prob of overtaking  
S = 5 # at each time step S, more drivers will enter the road
TIMES = []
WAIT = []
TRAFFIC_QUEUE = []
STOP_QUEUE = []

PER_KM = []

IDLING_CO2 = []
ACCEL_CO2 = []
CONSTANT_CO2 = []

SIM_NUM_OF_RUNS = 10 
SIM_TIME = 1500

# traffic light timings
TIME_GREEN = 13
TIME_YELLOW = 7
TIME_ARROW = 9

colourmap = colors.ListedColormap(["lightgrey", "green", "red", "yellow"])
normalizer = colors.Normalize(vmin=0,vmax=3)

def stats(): # stats
    print("%56s" % "------------------------------")
    print("%43s" % "Stats")
    print("%57s" % "------------------------------\n")
    print("Time to drive through the are, on average: ",mean(TIMES))
    print()
    conf_level = 0.95

    interval = st.norm.interval(alpha=conf_level, loc=mean(TIMES), scale=st.sem(TIMES)) # we are assuming that TIME and WAIT are normally distributed, due to the Central limit theorem
    
    print("95% conf level estimate for the population mean of overall driving time: ",interval[0],interval[1]) 
    print()
    print("Sample standart deviation, for overall driving time: ", std(TIMES))
    print()
    print("95th percentile for the overall driving time: ", percentile(TIMES, 95))
    print()
    print("Overall waiting time, on average: ", mean(WAIT))
    print()
    interval = st.norm.interval(alpha=conf_level, loc=mean(WAIT), scale=st.sem(WAIT))
    print("95% conf level estimate for the population mean of overall waiting time: ",interval[0],interval[1])
    print()
    print("Sample standart deviation, for overall waiting time: ", std(WAIT))
    print()
    print("95th percentile for the overall waiting time: " , percentile(WAIT, 95))
    print()
    print("Co2: \n")
    print("Produced during idling, on average: ",mean(IDLING_CO2))
    print()
    print("95th percentile for the CO2 during idling: " , percentile(IDLING_CO2, 95))
    print()
    print("\nProduced during accelarating, on average: ",mean(ACCEL_CO2))
    print()
    print("95th percentile for the CO2 during accelarating: " , percentile(ACCEL_CO2, 95))
    print()
    print("\nProduced during constant driving, on average: ",mean(CONSTANT_CO2))
    print()
    print("95th percentile for the CO2 during constant driving: " , percentile(CONSTANT_CO2, 95))
    print()
    s = IDLING_CO2 + ACCEL_CO2 + CONSTANT_CO2
    print("\nProduced during driving (overall), on average: ",mean(s))
    print()
    print("95th percentile for the CO2 during overall driving: " , percentile(s, 95))
    print()
    print("\nProduced per 1 m , on average: ", mean(PER_KM))


    plt.hist(IDLING_CO2, math.floor(1 + 3.322 * math.log(len(IDLING_CO2))))
    plt.xlabel("CO2") 
    plt.ylabel("Count") 
    plt.title("Idling CO2")
    plt.show()
    plt.hist(ACCEL_CO2, math.floor(1 + 3.322 * math.log(len(ACCEL_CO2))))
    plt.xlabel("CO2") 
    plt.ylabel("Count") 
    plt.title("Accelarating CO2")
    plt.show()
    plt.hist(CONSTANT_CO2, math.floor(1 + 3.322 * math.log(len(CONSTANT_CO2))))
    plt.xlabel("CO2") 
    plt.ylabel("Count") 
    plt.title("Constant CO2")
    plt.show()
    plt.hist(s, math.floor(1 + 3.322 * math.log(len(s))))
    plt.xlabel("CO2") 
    plt.ylabel("Count") 
    plt.title("Overall CO2")
    plt.show()
    

def len_queue(lists): # we will use this function, kidly provided in lab11, to determine the average length of queus (light and stop sign) at each time step
    shortest_length = min([len(l) for l in lists])
    averages = [sum([l[timestep] for l in lists])/len(lists) for timestep in range(shortest_length)]
    return averages



"""
Stop Sign

The idea here is simple. When our cars will eneter the limits (in coords) of our stop sign, we will track them down, in dictionary.
We will specify x,y and a time step when we actually entered the stop sign. So, if we did not update value in dic, meaning that
our driver has driven away from the stop sign, the time stamp will be out dated! It will not correpsond to the current one. If this is the case -
our driver is no longer in the stop sign area, otherwise we update the value (x,y and a time stamp)
"""

class Sign: # stop sign object
    def __init__(self):
        self.lengths = []
        self.go_horizont = True # indicatin  - can we go or not if we are moving by the x axis
        self.go_vertical_1 = False
        self.go_vertical_2 = False
        self.dic = {}
        self.dic_vec = {}
        
        self.limits = [(694-20,716+20),(89,111)]
        self.limits_1 = [(694-19,716+19),(89,111)]


        self.limits_3 = [(694,716),(89-3,111+3)] 
        self.limits_2 = [(694,716),(89,111)] 

    def merge_queues(self):
        value = len(self.dic) + len(self.dic_vec)
        self.lengths.append(value)



    def switch_vec(self,step):  # switching process for the vertical cars    
        cop = {}
        for key,value in self.dic_vec.items():
            x,y,t = value

            if t != step:
                continue

            cop[key] = value

        self.dic_vec = cop

    def where(self,x,y): # function to check whether our driver entered the borders of the stop sign
        if self.limits[0][0] <= x <= self.limits[0][1] and self.limits[1][0] <= y <= self.limits[1][1]:
            return True
        return False        


    def where_2(self,x,y): # function to check whether our driver is located in the stop sign explicitly
        if self.limits_1[0][0] <= x <= self.limits_1[0][1] and self.limits_1[1][0] <= y <= self.limits_1[1][1]:
            return True
        return False
        

    def switch(self,step): # switching process for the horizon cars   
        
        cop = {}

        for key,value in self.dic.items():
            x,y,t = value

            if t != step:
                continue

            cop[key] = value
            
        self.dic = cop
        
        if len(self.dic) > 0:
            self.go_vertical = False
            return
        self.go_vertical = True

"""
Traffic Light

Idea is the following: we will have a storage of the time steps for each traffic light sign: red, yellow and green
If the storage will be full of the time steps for the concrete sign - then empty the storage and change the sign
Also, we added a special sign for the cars turing on the traffic light - arrow_h and arrow_c for horizon and vertical drivers

So, when sigh is green - drivers who are willing to turn, are turning firstly, only when their time for this is gone, rest of the drvires proceed
The goes yellow and red signs

"""

class Light:
    def __init__(self):
        self.cont = []
        self.color_horizon = "green"
        self.color_vertical = "red"
        self.arrow_h = True
        self.arrow_v = True
        self.i = []
        self.lengths = []
        self.queue = {}
        self.coords = [(213,257),(78,122)]

    def monitor_queue(self,time): # monitor current amount of drivers here, for the stats
        cop = {}

        
        for key,value in self.queue.items():
            x,y,t = value

            if t != time:
                continue
            cop[key] = value
            
        self.queue = cop


    def determine_len(self):
        value = len(self.queue)
        self.lengths.append(value)
        return
            

        
    def switch(self): # swtich colors here
        if self.color_horizon == "green" and self.color_vertical == "red":
            if len(self.i)<TIME_ARROW: # firstly, cars will turn if the sign is green
                self.i.append(1)
                return
            else:
                self.arrow_h = False

            
            if len(self.cont)< TIME_GREEN: # then all the other will move forward
                self.cont.append(1)
                return
            else:
                self.color_horizon = "yellow" # and change the sign to yellow
                self.cont = []
                self.i = []
                return
            
        if self.color_horizon == "yellow" and self.color_vertical == "red":
            if len(self.cont)<TIME_YELLOW: # after some time chagnge sign to red one and allow other line move by changing their sign on the green
                self.cont.append(1)
                return
            else:
                self.color_horizon = "red"
                self.color_vertical = "green"
                self.arrow_v = True
                self.cont = []
                return
            
        if self.color_horizon == "red" and self.color_vertical == "green":
            if len(self.i)<TIME_ARROW:
                self.i.append(1)
                return
            else:
                self.arrow_v = False

                
            if len(self.cont)<TIME_GREEN:
                self.cont.append(1)
                return
            else:
                self.color_vertical = "yellow"
                self.cont = []
                self.i = []
                return
        
        if self.color_horizon == "red" and self.color_vertical == "yellow":
            if len(self.cont)<TIME_YELLOW:
                self.cont.append(1)
                return
            else:
                self.color_vertical = "red"
                self.color_horizon = "green"
                self.cont = []
                self.arrow_h = True
                return
                
                
                
        

class Car: # drivers object
    def __init__(self,goal,label,x,y,road,light,letter,stop_sign,in_letter):
        self.road = road # road object
        self.speed = abs(math.ceil(random.gauss(AVERAGE_SPEED,0.5))) # speed selec
        self.initial = self.speed # record inital speed
        self.func_x = lambda coord: max(min(coord, SIDEWALK_LENGTH - 1), 0)
        self.func_y = lambda coord: max(min(coord, SIDEWALK_WIDTH - 1), 0)
        self.x = x
        self.y = y
        self.direction = self.set_direction(label) # set direction
        self.active = False
        self.light_coords = light.coords #[(213,257),(78,122)]
        self.light = light
        self.line = False
        self.dist = abs(math.ceil(random.gauss(3,1))) # distance for this drivers
        self.letter_goal = letter
        self.line_2 = False
        self.cannot_move = False
        self.say_no_to_obgon = False # this is a special flag, saying that this car will have to turn around at either stop sign or light to reach dest node
        self.initial_x = x
        self.initial_y = y
        self.initial_x_2 = x
        self.initial_y_2 = y
        self.stop_sign = stop_sign
        self.line_3 = False
        self.t = 0
        self.prompt = False
        self.in_letter = in_letter
        self.waiting_time = 0
        self.additional_bark = abs(math.ceil(random.gauss(5,1))) # additional distance when driver will start barking
        self.idling = []
        self.constant = []
        self.accel= []

        self.isBark = 0,None
        self.isAccel = 0,None


        if isinstance(goal[0],int): # we will set goal coords in the list
            self.goal_x = [goal[0]]
        else:
            self.goal_x = [i for i in goal[0]]


        if isinstance(goal[1],int):
            self.goal_y = [goal[1]]
        else:
            self.goal_y = [i for i in goal[1]]


    def enter_road(self, x, y):
        if self.road.enter_road(self,x,y):
            self.active = True

    
    def set_direction(self,label):
        text,value = label[0],label[1]

        if text == "horizont":
            self.coodinate_to_checkx = True
            self.coodinate_to_checky = False
            return value # value is direction
        
        else:
            self.coodinate_to_checky = True
            self.coodinate_to_checkx = False
            return value


    def determine_speed(self): # determine - how many untis we will be able to proceed with the current speed
        for_minute = (self.speed / 60)*1000 # in 1 min
        for_second = int(for_minute/60) # in one sec (time step)
        return for_second

    def empty_road_x(self,future,direction): # check the road in front of us, on the x-axis
        future = abs(future)
        coords = self.road.coords
        current = self.x

        if direction == 1:
            for i in range(1,future+1):
                if coords.isoccupied(current+i,self.y):
                    return False,current+i # if it is occupied - return occupied pos
                
            i = 0 if future == 0 else i
            return True,current+i
        
        else:
            for i in range(1,future+1):
                if coords.isoccupied(current-i,self.y):
                    return False,current-i
            
            i = 0 if future == 0 else i
 
            return True,current-i


    def empty_road_y(self,future,direction): # check the road in front of us, on the y-axis
        future = abs(future)
        coords = self.road.coords
        current = self.y

        if direction == 1:
            for i in range(1,future+1):
                if coords.isoccupied(self.x,current+i):
                    return False,current+i
         
            i = 0 if future == 0 else i
    
            return True,current+i
        else:
            
            for i in range(1,future+1):
                if coords.isoccupied(self.x,current-i):
                    return False,current-i
            i = 0 if future == 0 else i
            
            return True,current-i
    
    """
    Behaviour of our drivers may be divided into the 4 parts

    1) Those who move by the x (horizon) in the positive direction (1)
    2) Those who move by the x (horizon) in the negative direction (-1)
    3) Those who move by the y (vertically) in the positive direction (1)
    4) Those who move by the y (vertically) in the negative direction (-1)

    Overall behaviour for our agents is the same, however those moving vertically are slghtly different
    """

    
    def determine_dist(self):
        a1,a2 = max(self.x,self.initial_x_2), min(self.x,self.initial_x_2)
        b1,b2 = max(self.y,self.initial_y_2), min(self.y,self.initial_y_2)

        return math.ceil((a1 - a2) + (b1 - b2))
        
                    
    def step(self):
        self.bark_rate = self.speed - self.speed * 0.05 # at each time step update both barking and accel rates, derived from the current speed
        self.accel_rate = self.speed + self.speed * 0.05

        ########################################################################

        if self.light_coords[0][0] <= self.x <= self.light_coords[0][1] and self.light_coords[1][0] <= self.y <= self.light_coords[1][1]:
            self.light.queue[self] = (self.x,self.y,self.t)


        time_step1,bol_value1 = self.isBark # for the stats purposes, CO2
        time_step2,bol_value2 = self.isAccel

        if bol_value1 and time_step1 == self.t-1: # if we were barking at the previous time step
            self.idling.append(1)
            pass
        
        if bol_value2 and time_step2 == self.t-1: # if we were accelarating at the previous time step
            self.accel.append(5)
            pass

        if time_step1 != self.t-1 and time_step2 != self.t-1: # if we did not accelarate or bark - then we moved with a constant speed
            self.constant.append(2.5)
            self.isBrak = (0,None)
            self.isAccel = (0,None)
            
        
        if self.coodinate_to_checkx is True and self.coodinate_to_checky is False:                
            if self.direction == 1:
                
                if self.stop_sign.where_2(self.x,self.y):
                    self.stop_sign.dic[self] = (self.x,self.y,self.t)

                
                highway = (101,111)
                goal_horizont = ["5"]

                # you can see, how we will detect if car was barking or not
                # So, if this is the case - we set the copy of the current time step and set bool val as a True
                # If we did not update this tuple, saying that time step became out of date - that means we did not do any barking on the previous time step

                if self.speed > self.initial and random.random() <= 0.5: 
                    self.speed -= max(self.speed - self.bark_rate,0)
                    c_t = self.t
                    self.isBark = (c_t, True) 

                # the same mechanism for the accelarating
                # note that we will accelarate when our current speed will be less than the inital  (prescribed one)
                # and we will bark with the prob of 50% and the fact that our current speed is bigger than the inital one

                if self.speed < self.initial: #and random.random() <= 0.5:
                    c_t = self.t
                    self.isAccel = (c_t, True)
                    self.speed += 6

                
                if self.letter_goal not in goal_horizont: # if drivers goal is not at the end of the highways
                    self.say_no_to_obgon = True

                if self.say_no_to_obgon and self.y != highway[1]: # if our driver is wiling to turn, move to the corresponding line
                    if self.road.coords.isoccupied(self.x,self.y+1):
                        self.speed = max(self.speed - self.bark_rate,0)
                        c_t = self.t
                        self.isBark = (c_t, True)
                        self.waiting_time += 1
                        return
                    else:
                        self.road.attemptmove(self, self.x,self.y+1)
                        self.speed = max(self.speed - self.bark_rate,0)
                        c_t = self.t
                        self.isBark = (c_t, True)
                        return
                
                elif not self.say_no_to_obgon and self.y == highway[1]: # if our driver is not going to turn, but he's located at this special "turining" line - he drivers away from this line
                    if self.road.coords.isoccupied(self.x,self.y-1):
                        self.road.attemptmove(self, self.x+1,self.y)
                        self.waiting_time += 1
                        self.speed = max(self.speed - self.bark_rate,0)
                        c_t = self.t
                        self.isBark = (c_t, True)
                        return
                    else:
                        self.road.attemptmove(self, self.x,self.y-1)
                        self.speed = max(self.speed - self.bark_rate,0)
                        c_t = self.t
                        self.isBark = (c_t, True)
                        return
        

                # check whether we reached to the borders of the stop sign or the traffic light
                if self.light_coords[0][0] - 10 - self.additional_bark <= self.func_x(self.x) <  self.light_coords[0][0] and self.light_coords[1][0] <= self.y <= self.light_coords[1][1]:  #and not self.line:
                    self.speed = max(self.speed - self.bark_rate,0)

                    c_t = self.t
                    self.isBark = (c_t, True)

                if self.stop_sign.limits[0][0] < self.func_x(self.x) < self.stop_sign.limits[0][1]-15-self.additional_bark and self.stop_sign.limits[1][0]<= self.y <= self.stop_sign.limits[1][1]:
                    c_t = self.t
                    self.isBark = (c_t, True)
                    self.speed = max(self.speed - self.bark_rate-5,0)

                    
                                
                how_many_steps = self.determine_speed() # determine amount of steps
                pure_amount = abs(self.direction*how_many_steps) # mulpl by direction
                amount =  pure_amount + self.dist # add required dist
                
                bol,pos_x = self.empty_road_x(amount,1) # check the rooad for availability

                if bol: # if we can proceed without obstacales
                    
                    if self.stop_sign.where(self.x+pure_amount,self.y): # see if our next step will be at the borders of the stop sign

                        if self.stop_sign.where_2(self.x,self.y) and len(self.stop_sign.dic_vec) > 0: # only for the debug reasons...
                            self.road.attemptmove(self, self.x+5,self.y)
                            return

 
                        if len(self.stop_sign.dic_vec) > 0: # so, if we cannot procees, since they are already some drivers moving vertically, despite our advantage - then wait
                            self.speed = max(self.speed - self.bark_rate,0)
                            c_t = self.t
                            self.isBark = (c_t, True)
                            self.idling.append(1)
                            self.waiting_time += 1
                            return


                        if (self.letter_goal == "1" or self.letter_goal == "2") and self.in_letter == "0":
                            self.letter_goal = "0"
                            self.goal_x =  [SIDEWALK_LENGTH-1]
                            self.goal_y = list(range(101,112))
                            
                            


                        if self.letter_goal == "3": # if we need to turn and the goal is port "3"

                            self.road.attemptmove(self, self.stop_sign.limits[0][0],self.y) # move right to the borders of the stop sign

                            lim = self.stop_sign.limits[0][0] + 20 # add 20, because line "3" begins exactly on this coord, by x (694)
                            
                            desired = lim - self.x # determine - how many steps are required to reach line "3"

                            if desired <= 0:
                                desired = 0

                            self.road.attemptmove(self, self.func_x(self.x+desired),self.y) # make this movement


                            width = random.choice(range(11))  # then we have a choice of randomly driving from 0 to 10 additional steps, since width of our line is excactly 10


                            bol_x,pos_x = self.empty_road_x(width,1) # check for availabiity

                            if bol_x: # if we can make this movement
                                
                                self.road.attemptmove(self, self.func_x(self.x+width),self.y)
                                
                            else: # if we cannot - move to the nearest avaliable pos, neglection our dist parametr
                                
                                self.road.attemptmove(self, self.func_x(pos_x-1),self.y)
                            
                            bol_y,pos_y = self.empty_road_y(5,-1) # then make some movements updwards, with the same pattern 
                            
                            if bol_y:
                                
                                self.road.attemptmove(self, self.x,self.y-5)
                            else:
                                self.road.attemptmove(self, self.x,pos_y+1)


                            self.speed = max(self.speed - self.bark_rate,0)
                            c_t = self.t
                            self.isBark = (c_t, True)

                            self.direction = self.set_direction(("vertical",-1)) # finnaly change direction here, fro, horizon to vertical, and direction from 1 to -1
                            self.initial_x = random.choice(range(694,705))
                            self.say_no_to_obgon = False                 
                            return
                            
                            

                        if self.letter_goal == "4": # same logic for the port "4"
                            self.road.attemptmove(self, self.stop_sign.limits[0][0],self.y)
                            
                            lim = self.stop_sign.limits[0][0] + 32
                            desired = lim - self.x

                            if desired <= 0:
                                desired = 0

                            self.road.attemptmove(self, self.func_x(self.x+desired),self.y)

                            width = random.choice(range(11))

                            bol_x,pos_x = self.empty_road_x(width,1)

                            if bol_x:
                                
                                self.road.attemptmove(self, self.func_x(self.x+width),self.y)
                            else:
                                self.road.attemptmove(self, self.func_x(pos_x-1),self.y)
                                
                            bol_y,pos_y = self.empty_road_y(5,1)

                            if bol_y:
                                
                                self.road.attemptmove(self, self.x,self.y+5)
                            else:
                                self.road.attemptmove(self, self.x,pos_y-1)

                            self.speed = max(self.speed - self.bark_rate,0)
                            c_t = self.t
                            self.isBark = (c_t, True)
                            

                            self.direction = self.set_direction(("vertical",1))
                            self.initial_x = random.choice(range(706,717))
                            self.say_no_to_obgon = False

                            return

                            

                        copy = self.speed # if we did not turn or stop - procced
                        self.speed += 6 + self.accel_rate 
                        c_t = self.t
                        self.isAccel = (c_t, True)                        
                        how_many_steps = self.determine_speed()
                        pure_amount = abs(self.direction*how_many_steps)
                        self.road.attemptmove(self, self.func_x(self.x+pure_amount),self.y)
                        self.speed = copy
                        self.road.leave_road(self)
                        return

                    
                    if self.light.color_horizon == "green": # if sign is green
                        if  self.light.arrow_h  and self.say_no_to_obgon and self.light_coords[0][0] <= self.func_x(self.x+pure_amount) <= self.light_coords[0][1] and self.light_coords[1][0] <= self.y <= self.light_coords[1][1]:
                            if self.letter_goal == "1":

                                # here we will check: 1) if we are allowed to turn, 2) if we have to turn, 3) if our next step will be at the borders of the stop sign
                                # if so, turn around with the same logic as it was on the stop sign
                                
                                self.road.attemptmove(self, self.func_x(self.light_coords[0][0]),self.y) 

                                lim = self.light_coords[0][0] + 11
                                desired = lim - self.x

                                if desired <= 0:
                                    desired = 0
                                
                                self.road.attemptmove(self, self.func_x(self.x+desired),self.y)   #[(213,257),(78,122)]
                                width = random.choice(range(11))

                                

                                bol_1,pos_x_1 = self.empty_road_x(width,1)

                                if bol_1:
                                    self.road.attemptmove(self, self.func_x(self.x+width),self.y)
                                else:
                                    self.road.attemptmove(self, pos_x_1 - 1, self.y)


                                bol_2,pos_y_1 = self.empty_road_y(5,-1)

                                if bol_2:
                                    self.road.attemptmove(self, self.x,self.y-5)
                                else:
                                    self.road.attemptmove(self, self.x,pos_y_1+1)
                                    
                                self.direction = self.set_direction(("vertical",-1))
                                self.initial_x = random.choice(range(224,235))
                                self.speed = max(self.speed - self.bark_rate,0)
                                c_t = self.t
                                self.isBark = (c_t, True)
                                self.prompt = True
                                self.say_no_to_obgon = False
                                return
                            
                            elif self.letter_goal == "2":
                                self.road.attemptmove(self, self.func_x(self.light_coords[0][0]),self.y)

                                lim = self.light_coords[0][0] + 23
                                desired = lim - self.x

                                if desired <= 0:
                                    desired = 0
                                
                                self.road.attemptmove(self, self.func_x(self.x+desired),self.y)
                                width = random.choice(range(11))

                                bol_1,pos_x_1 = self.empty_road_x(width,1)

                                if bol_1:
                                    self.road.attemptmove(self, self.func_x(self.x+width),self.y)
                                else:
                                    self.road.attemptmove(self, self.x,self.y-1)
                                    self.road.attemptmove(self, pos_x_1 - 1,self.y)


                                bol_2,pos_y_1 = self.empty_road_y(5,1)

                                if bol_2:
                                    self.road.attemptmove(self, self.x,self.y+5)
                                else:
                                    self.road.attemptmove(self, self.x,pos_y_1-1)
                                
                                self.direction = self.set_direction(("vertical",1))
                                self.initial_x = random.choice(range(236,247))
                                self.speed = max(self.speed - self.bark_rate,0)
                                c_t = self.t
                                self.isBark = (c_t, True)
                                self.prompt = True
                                self.say_no_to_obgon = False
                                return
                            else:
                                pass
                        
                        elif self.light.arrow_h  and not self.say_no_to_obgon and self.light_coords[0][0] <= self.func_x(self.x+pure_amount) <= self.light_coords[0][1] and self.light_coords[1][0] <= self.y <= self.light_coords[1][1]:
                                 # here we are checking if we are not required to turn, although we cannot proceed since they are drivers turining right now
                                
                                if self.line:
                                    c_t = self.t
                                    self.isBark = (c_t, True)
                                    self.speed = max(self.speed - self.bark_rate,0)
                                    self.waiting_time += 1
                                    return
                                
                                self.road.attemptmove(self, self.func_x(self.light_coords[0][0]),self.y)
                                self.line = True
                                return

                            
                        elif not self.light.arrow_h and self.say_no_to_obgon and self.light_coords[0][0] <= self.func_x(self.x+pure_amount) <= self.light_coords[0][1] and self.light_coords[1][0] <= self.y <= self.light_coords[1][1]:
                                # here we are checking if we are required to turn, although we cannot proceed since they are drivers moving forward right now
                                
                                if self.line:
                                    self.speed = max(self.speed - self.bark_rate,0)
                                    c_t = self.t
                                    self.isBark = (c_t, True)
                                    self.waiting_time += 1
                                    return
                                
                                self.road.attemptmove(self, self.func_x(self.light_coords[0][0]),self.y)
                                self.line = True
                                return
                        else:
                            pass


                        # if we made it till here, that means: we are not entering traffic light with out next step
                        # but we have to check here does our driver currently located in the area (not borders) of the traffic light
                        # if so - increase speed and move (with the fact that light is green)
                        if self.light_coords[0][0] < self.func_x(self.x) < self.light_coords[0][1] and self.light_coords[1][0] < self.y < self.light_coords[1][1] and not self.line:
                            copy = self.speed
                            self.speed += 6 + self.accel_rate # 10
                            c_t = self.t
                            self.isAccel = (c_t, True)
                            how_many_steps = self.determine_speed()
                            pure_amount = abs(self.direction*how_many_steps)
                            self.road.attemptmove(self, self.func_x(self.x+pure_amount),self.y)
                            self.speed = copy
                            self.road.leave_road(self)
                            return

                        # if we were waintin in the line: turn on "afterburner" regime and accelarat, since we lost a lot of "speed" power 
                        if self.line or self.line_2:
                            self.speed += 6 + self.accel_rate + random.choice(range(5,21)) #(self.speed * 0.04) + self.initial + 20
                            c_t = self.t
                            self.isAccel = (c_t, True)

                        # make a move afterwards
                        self.road.attemptmove(self, self.func_x(self.x+pure_amount),self.y)
                        self.line = False
                        self.line_2 = False
                        self.road.leave_road(self)
                        return
                    
                    else: # this else means that sign is either red or yellow
                        
                        if self.line: # if we are in the line - wait
                            self.speed = max(self.speed - self.bark_rate, 0)
                            c_t = self.t
                            self.isBark = (c_t, True)
                            self.waiting_time += 1
                            return
                        #if sign is not green, however we are still (somehow) in the area - accelarate and get out of there
                        if self.light_coords[0][0] < self.func_x(self.x) < self.light_coords[0][1] and self.light_coords[1][0] < self.y < self.light_coords[1][1]:
                            copy = self.speed
                            self.speed += 6 + self.accel_rate + random.choice(range(10,16)) #12
                            c_t = self.t
                            self.isAccel = (c_t, True)
                            how_many_steps = self.determine_speed()
                            pure_amount = abs(self.direction*how_many_steps)

                            bol,pos_x = self.empty_road_x(pure_amount,1)

                            if bol:
                                self.road.attemptmove(self, self.func_x(self.x+pure_amount),self.y)
                                self.speed = copy
                                return
                            else:
                                self.road.attemptmove(self, self.func_x(pos_x - 1),self.y)
                                self.speed = copy
                                return
                        
                        # if with out next move if we are reaching the borders of the traffic light - stop
                        if self.light_coords[0][0] <= self.func_x(self.x+pure_amount) <= self.light_coords[0][1] and self.light_coords[1][0] <= self.y <= self.light_coords[1][1]:
                            limit = self.light_coords[0][0]
                            self.road.attemptmove(self, self.func_x(limit),self.y)
                            self.line = True
                            return
                        
                        else: # if not - make a move since we are not reaching traffic light in the next step
                            self.road.attemptmove(self, self.func_x(self.x+pure_amount),self.y)
                            self.road.leave_road(self)
                            return
                else:
                    # this else block, tells us that we were not able to move forward freely - meaning that there was an obtacle on our way
                    
                    if pos_x - self.x < self.dist: # if difference between a postition occupied by another driver and us is less than required distance - we start barking
                        self.speed = max(self.speed - self.bark_rate,0)
                        c_t = self.t
                        self.isBark = (c_t, True)

                    
                    if pos_x-self.dist == self.x: # if difference between a postition occupied by another driver and the required distance is our current location - then we'll have to stop
                        self.speed = max(self.speed - self.bark_rate,0)
                        c_t = self.t
                        self.isBark = (c_t, True)
                        self.waiting_time += 1
                        self.line_2 = True
                        return
                    
                    else:
                        if self.line_2: # if we were waiting in the line..
                            self.speed += 6 + self.accel_rate+random.choice(range(5,21)) #(self.speed * 0.04) + self.initial + 20
                            c_t = self.t
                            self.isAccel = (c_t, True)

                        # here we added the following feature:
                        # if our driver is blocked and cannot move freely - then they will make a move to another line (upwards) to outflank the blocking driver
                        # very primitive way of overtaking, but add more randomness to our simulation
                        # one note - drivers who are turning on the stop sign or traffic lights, they do not overtake, they simly move by their "special" line
                            
                        if random.random() < OBGON and not self.say_no_to_obgon:
                            choice = random.choice([1,-1])
                            if self.y == highway[0]:
                                self.cannot_move = True
                                choice = 1
                            elif self.y == highway[1]:
                                self.cannot_move = True
                                choice = -1
                            else:
                                pass
                            
                            if self.road.coords.isoccupied(self.x,self.y+choice):
                                
                                if not self.cannot_move:
                                    choice = 1 if choice == -1 else -1
                                else:
                                    self.cannot_move = False

                                    
                                if self.road.coords.isoccupied(self.x,self.y+choice):
                                    pass
                                else:
                                    self.road.attemptmove(self, self.x,self.y+choice)
                                    self.speed = max(self.speed - self.bark_rate,0)
                                    c_t = self.t
                                    self.isBark = (c_t, True)
                                    self.line_2 = False
                                    return
                            else:
                                self.road.attemptmove(self, self.x,self.y+choice)
                                self.speed = max(self.speed - self.bark_rate,0)
                                c_t = self.t
                                self.isBark = (c_t, True)
                                self.line_2 = False
                                return

                        # check the next available pos, with the distance in mind and make a movement here
                        go_to = pos_x - self.dist
                        self.line_2 = False
                        self.road.attemptmove(self, self.func_x(go_to),self.y)
                        self.road.leave_road(self)
                        return
                    
###############################################################################################
                    
            else: # horizon, directio = -1, the same behavior
                
                if self.stop_sign.where_2(self.x,self.y):
                    
                    self.stop_sign.dic[self] = (self.x,self.y,self.t)
                    
                highway = (89,99)

                goal_horizont = ["0"]

                if self.speed > self.initial and random.random() <= 0.5:
                    self.speed = max(self.speed - self.bark_rate,0)
                    c_t = self.t
                    self.isBark = (c_t, True)

                if self.speed < self.initial:
                    self.speed += 6
                    c_t = self.t
                    self.isAccel = (c_t, True)
                

                
                if self.letter_goal not in goal_horizont:
                    self.say_no_to_obgon = True

                if self.say_no_to_obgon and self.y != highway[1]:
                    if self.road.coords.isoccupied(self.x,self.y+1):
                        self.speed = max(self.speed - self.bark_rate,0)
                        c_t = self.t
                        self.isBark = (c_t, True)
                        self.waiting_time += 1
                        return
                    else:
                        self.road.attemptmove(self, self.x,self.y+1)
                        self.speed = max(self.speed - self.bark_rate,0)
                        c_t = self.t
                        self.isBark = (c_t, True)
                        return
                
                elif not self.say_no_to_obgon and self.y == highway[1]:
                    if self.road.coords.isoccupied(self.x,self.y-1):
                        self.road.attemptmove(self, self.x-1,self.y)
                        self.speed = max(self.speed - self.bark_rate,0)
                        c_t = self.t
                        self.isBark = (c_t, True)
                        return
                    else:
                        self.road.attemptmove(self, self.x,self.y-1)
                        self.speed = max(self.speed - self.bark_rate,0)
                        c_t = self.t
                        self.isBark = (c_t, True)
                        return
                
                if self.light_coords[0][1] < self.func_x(self.x) <= self.light_coords[0][1]+10+self.additional_bark and self.light_coords[1][0] < self.y < self.light_coords[1][1]:
                    self.speed = max(self.speed - self.bark_rate,0)
                    c_t = self.t
                    self.isBark = (c_t, True)


                

                if self.stop_sign.limits[0][0]+15+self.additional_bark <= self.func_x(self.x) <= self.stop_sign.limits[0][1] and self.stop_sign.limits[1][0]<= self.y <= self.stop_sign.limits[1][1]:
                    self.speed = max(self.speed - self.bark_rate-5,0)
                    c_t = self.t
                    self.isBark = (c_t, True)

                    
                how_many_steps = self.determine_speed()
                pure_amount = abs(self.direction*how_many_steps)
                amount =  pure_amount + self.dist
                
                bol,pos_x = self.empty_road_x(amount,-1)

                if bol:
                    if self.stop_sign.where(self.x-pure_amount,self.y):

                        if self.stop_sign.where_2(self.x,self.y) and len(self.stop_sign.dic_vec) > 0:
                            self.road.attemptmove(self, self.x-5,self.y)
                            return


                                            
                        if len(self.stop_sign.dic_vec) > 0:
                            self.speed = max(self.speed - self.bark_rate,0)
                            c_t = self.t
                            self.isBark = (c_t, True)
                            self.waiting_time += 1
                            return

                        if self.letter_goal == "4":

                            self.road.attemptmove(self, self.stop_sign.limits[0][1],self.y)

                            lim = self.stop_sign.limits[0][1] - 20
                            desired = self.x - lim

                            if desired <= 0:
                                desired = 0


                            self.road.attemptmove(self, self.func_x(self.x-desired),self.y)
                            width = random.choice(range(11))
                            

                            bol_x,pos_x = self.empty_road_x(width,-1)

                            if bol_x:
                                self.road.attemptmove(self, self.func_x(self.x-width),self.y)
                            else:
                                self.road.attemptmove(self, self.func_x(pos_x+1),self.y)

                            bol_y,pos_y = self.empty_road_y(5,1)
                            if bol_y:
                                
                                self.road.attemptmove(self, self.x,self.y+5)
                            else:
                                self.road.attemptmove(self, self.x,pos_y-1)


                            self.speed = max(self.speed - self.bark_rate,0)
                            c_t = self.t
                            self.isBark = (c_t, True)

                            self.initial_x = random.choice(range(706,717))
                            self.direction = self.set_direction(("vertical",1))
                            self.say_no_to_obgon = False
                            return

    
              
                            

                        if self.letter_goal == "3":

                            self.road.attemptmove(self, self.stop_sign.limits[0][1],self.y)

                            lim = self.stop_sign.limits[0][1]  - 32
                            desired = self.x - lim
                            

                            if desired <= 0:
                                desired = 0


                            self.road.attemptmove(self, self.func_x(self.x-desired),self.y)
                            width = random.choice(range(11))

                            bol_x,pos_x = self.empty_road_x(width,-1)

                            if bol_x:
                                self.road.attemptmove(self, self.func_x(self.x-width),self.y)
                            else:
                                self.road.attemptmove(self, self.func_x(pos_x+1),self.y)

                            bol_y,pos_y = self.empty_road_y(5,-1)
                            
                            if bol_y:
                                self.road.attemptmove(self, self.x,self.y-5)
                            else:
                                self.road.attemptmove(self, self.x,pos_y+1)

                            self.speed = max(self.speed - self.bark_rate,0)
                            c_t = self.t
                            self.isBark = (c_t, True)
                            
                            self.direction = self.set_direction(("vertical",-1))
                            self.initial_x = random.choice(range(694,705))
                            self.say_no_to_obgon = False
                            return               
                        
                        copy = self.speed
                        self.speed += 6 + self.accel_rate
                        c_t = self.t
                        self.isAccel = (c_t, True)
                        how_many_steps = self.determine_speed()
                        pure_amount = abs(self.direction*how_many_steps)
                        self.road.attemptmove(self, self.func_x(self.x-pure_amount),self.y)
                        self.speed = copy
                        self.road.leave_road(self)
                        return

                        
                        
                    if self.light.color_horizon == "green": #[(213,257),(78,122)]
                        if  self.light.arrow_h  and self.say_no_to_obgon and self.light_coords[0][0] <= self.func_x(self.x-pure_amount) <= self.light_coords[0][1] and self.light_coords[1][0] <= self.y <= self.light_coords[1][1]:
                            if self.letter_goal == "2":
                                self.road.attemptmove(self, self.func_x(self.light_coords[0][1]),self.y)

                                lim = self.light_coords[0][1] - 11
                                desired = self.x - lim

                                if desired <= 0:
                                    desired = 0

                                self.road.attemptmove(self, self.func_x(self.x - desired),self.y)

                                width = random.choice(range(11))
                                
                                
                                bol_1,pos_x_1 = self.empty_road_x(width,-1)

                                if bol_1:
                                    self.road.attemptmove(self, self.func_x(self.x-width),self.y)
                                else:
                                    self.road.attemptmove(self, self.func_x(pos_x_1+1),self.y)

                                bol_2,pos_y_1 = self.empty_road_y(5,1)

                                if bol_2:
                                    self.road.attemptmove(self, self.x,self.y+5)
                                else:
                                    self.road.attemptmove(self, self.x,pos_y_1-1)

                                    
                                self.initial_x = random.choice(range(236,247))
                                self.direction = self.set_direction(("vertical",1))
                                self.speed = max(self.speed - self.bark_rate,0)
                                c_t = self.t
                                self.isBark = (c_t, True)
                                self.prompt = True
                                self.say_no_to_obgon = False
                                return
                            
                            elif self.letter_goal == "1":
                                self.road.attemptmove(self, self.func_x(self.light_coords[0][1]),self.y)

                                lim = self.light_coords[0][1] - 23
                                desired = self.x - lim


                                self.road.attemptmove(self, self.func_x(self.x - desired),self.y)

                                width = random.choice(range(11))

                                bol_1,pos_x_1 = bol,pos_x = self.empty_road_x(width,-1)

                                if bol_1:
                                    self.road.attemptmove(self, self.func_x(self.x-width),self.y)
                                else:
                                    self.road.attemptmove(self, self.func_x(pos_x_1+1),self.y)
                                    

                                bol_2,pos_y_1 = self.empty_road_y(5,-1)

                                if bol_2:
                                    self.road.attemptmove(self, self.x,self.y-5)
                                else:
                                    self.road.attemptmove(self, self.x,pos_y_1+1)


                                self.initial_x = random.choice(range(224,235))
                                self.direction = self.set_direction(("vertical",-1))
                                self.speed = max(self.speed - self.bark_rate,0)
                                c_t = self.t
                                self.isBark = (c_t, True)
                                self.prompt = True
                                self.say_no_to_obgon = False
                                return
                            else:
                                pass
                            
                        elif self.light.arrow_h  and not self.say_no_to_obgon and self.light_coords[0][0] <= self.func_x(self.x-pure_amount) <= self.light_coords[0][1] and self.light_coords[1][0] <= self.y <= self.light_coords[1][1]:


                                if self.line:
                                    self.speed = max(self.speed - self.bark_rate,0)
                                    c_t = self.t
                                    self.isBark = (c_t, True)
                                    self.waiting_time += 1
                                    return
                                
                                self.road.attemptmove(self, self.func_x(self.light_coords[0][1]),self.y)
                                self.line = True
                                return

                            
                        elif not self.light.arrow_h and self.say_no_to_obgon and self.light_coords[0][0] <= self.func_x(self.x-pure_amount) <= self.light_coords[0][1] and self.light_coords[1][0] <= self.y <= self.light_coords[1][1]:

                                if self.line:
                                    self.speed = max(self.speed - self.bark_rate,0)
                                    c_t = self.t
                                    self.isBark = (c_t, True)
                                    self.waiting_time += 1
                                    return

                                self.road.attemptmove(self, self.func_x(self.light_coords[0][1]),self.y)
                                self.line = True
                                return

                        else:
                            pass

                        
                        if self.light_coords[0][0] < self.func_x(self.x) < self.light_coords[0][1] and self.light_coords[1][0] < self.y < self.light_coords[1][1] and not self.line:
                            copy = self.speed
                            self.speed += 6 + self.accel_rate  # 10
                            c_t = self.t
                            self.isAccel = (c_t, True)
                            how_many_steps = self.determine_speed()
                            pure_amount = abs(self.direction*how_many_steps)
                            self.road.attemptmove(self, self.func_x(self.x-pure_amount),self.y)
                            self.speed = copy
                            self.road.leave_road(self)
                            return

                            
                        if self.line or self.line_2:
                            self.speed += 6 + self.accel_rate + random.choice(range(5,21)) #(self.speed * 0.04) + self.initial + 20
                            c_t = self.t
                            self.isAccel = (c_t, True)
                        
                        self.road.attemptmove(self, self.func_x(self.x-pure_amount),self.y)
                        self.line = False
                        self.line_2 = False
                        self.road.leave_road(self)
                        return
                    
                    else:
                        if self.line:
                            self.speed = max(self.speed - self.bark_rate,0)
                            c_t = self.t
                            self.isBark = (c_t, True)
                            self.waiting_time += 1
                            return
                        
                        if self.light_coords[0][0] < self.func_x(self.x) < self.light_coords[0][1] and self.light_coords[1][0] < self.y < self.light_coords[1][1]:
                            copy = self.speed
                            self.speed += 6 + self.accel_rate + random.choice(range(10,16)) #12
                            c_t = self.t
                            self.isAccel = (c_t, True)
                            how_many_steps = self.determine_speed()
                            pure_amount = abs(self.direction*how_many_steps)
                            amount =  pure_amount + self.dist
                            bol,pos_x = self.empty_road_x(amount,-1)

                            if bol:
                                self.road.attemptmove(self, self.func_x(self.x-pure_amount),self.y)
                                self.speed = copy
                                return
                            else:
                                new_pos = pos_x + self.dist
                                self.road.attemptmove(self, self.func_x(pos_x + 1),self.y)
                                self.speed = copy
                                return
                            
                        if self.light_coords[0][0] <= self.func_x(self.x-pure_amount) <= self.light_coords[0][1] and self.light_coords[1][0] <= self.y <= self.light_coords[1][1]:
                            limit = self.light_coords[0][1]
                            self.road.attemptmove(self, self.func_x(limit),self.y)
                            self.line = True
                            return
                        else:
                            self.road.attemptmove(self, self.func_x(self.x-pure_amount),self.y)
                            self.road.leave_road(self)
                            return
                else:
                    if self.x  - pos_x < self.dist:
                        self.speed = max(self.speed - self.bark_rate,0)
                        c_t = self.t
                        self.isBark = (c_t, True)
                    
                    if pos_x+self.dist == self.x:
                        self.speed = max(self.speed - self.bark_rate,0)
                        c_t = self.t
                        self.isBark = (c_t, True)
                        self.line_2 = True
                        self.waiting_time += 1
                        return
                    
                    else:
                        if self.line_2:
                            self.speed +=  6 + self.accel_rate + random.choice(range(5,21)) #(self.speed * 0.04) + self.initial + 20
                            c_t = self.t
                            self.isAccel = (c_t, True)
                        
                        if random.random() < OBGON and not self.say_no_to_obgon:
                            choice = random.choice([1,-1])
                            if self.y == highway[0]:
                                self.cannot_move = True
                                choice = 1
                            elif self.y == highway[1]:
                                self.cannot_move = True
                                choice = -1
                            else:
                                pass
                            
                            if self.road.coords.isoccupied(self.x,self.y+choice):
                                
                                if not self.cannot_move:
                                    choice = 1 if choice == -1 else -1
                                else:
                                    self.cannot_move = False

                                    
                                if self.road.coords.isoccupied(self.x,self.y+choice):
                                    pass
                                else:
                                    self.road.attemptmove(self, self.x,self.y+choice)
                                    self.speed = max(self.speed - self.bark_rate,0)
                                    c_t = self.t
                                    self.isBark = (c_t, True)
                                    self.line_2 = False
                                    return
                            else:
                                self.road.attemptmove(self, self.x,self.y+choice)
                                self.speed = max(self.speed - self.bark_rate,0)
                                c_t = self.t
                                self.isBark = (c_t, True)
                                self.line_2 = False
                                return
                            
                        go_to = pos_x + self.dist
                        self.line_2 = False
                        self.road.attemptmove(self, self.func_x(go_to),self.y)
                        self.road.leave_road(self)

#############################################################################################################################
              
        else: # vertical, direction = 1
            
            if self.direction == 1:
                if self.stop_sign.limits_2[0][0] < self.x < self.stop_sign.limits_2[0][1] and self.stop_sign.limits_2[1][0] < self.y < self.stop_sign.limits_2[1][1]:
                    self.stop_sign.dic_vec[self] = (self.x,self.y,self.t)

                if self.speed > self.initial and random.random() <= 0.5:
                    self.speed = max(self.speed - self.bark_rate,0)
                    c_t = self.t
                    self.isBark = (c_t, True)
                
                if self.speed < self.initial:
                    self.speed += 6
                    c_t = self.t
                    self.isAccel = (c_t, True)

                # since we may have to lines for this direction, with port entry of 2 or 4, we have to choose the goal
                # if our initial x (x value with which we enetered the road) value will be either in one of these ranges - then we will select an appropriate one
                
                option_1 = range(236,247)
                option_3 = range(706,717)
                

                if self.initial_x in option_1:
                    highway = (236,246)
                    goal_vertical = ["2"]
                    
                else:
                    highway = (706,716)
                    goal_vertical = ["4"]


                if highway == (236,246): # also, make sure we don't go beyong our highways...
                    if self.x > highway[1]:
                        self.x -= (self.x - highway[1]) 
                        pass
                    if self.x < highway[0]:
                        self.x += (highway[0] - self.x)
                        pass

                
                if highway == (706,716):
                    if self.x > highway[1]:
                        self.x -= (self.x - highway[1])
                        pass
                    if self.x < highway[0]:
                        self.x += (highway[0] - self.x)
                        pass


                # then we  check if our letter goal (destination node) is in one of these two goals (lists)
                # if not - then we will have to turn, because our goal is not in the node right in front of us
                

                if self.letter_goal not in goal_vertical: 
                    self.say_no_to_obgon = True

                if self.say_no_to_obgon and self.x != highway[1]:
                    if self.road.coords.isoccupied(self.x+1,self.y):
                        self.speed = max(self.speed - self.bark_rate,0)
                        self.waiting_time += 1
                        c_t = self.t
                        self.isBark = (c_t, True)
                        return
                    else:
                        self.road.attemptmove(self, self.x+1,self.y)
                        self.speed = max(self.speed - self.bark_rate,0)
                        c_t = self.t
                        self.isBark = (c_t, True)
                        return
                
                elif not self.say_no_to_obgon and self.x == highway[1]:
                    if self.road.coords.isoccupied(self.x-1,self.y):
                        self.road.attemptmove(self, self.x,self.y+1)
                        self.speed = max(self.speed - self.bark_rate,0)
                        c_t = self.t
                        self.isBark = (c_t, True)
                        return
                    else:
                        self.road.attemptmove(self, self.x-1,self.y)
                        self.speed = max(self.speed - self.bark_rate,0)
                        c_t = self.t
                        self.isBark = (c_t, True)
                        return

                    
                if self.light_coords[1][0]-10-self.additional_bark <= self.func_y(self.y)< self.light_coords[1][0] and self.light_coords[0][0] <= self.x <= self.light_coords[0][1]:
                    self.speed = max(self.speed - self.bark_rate,0)
                    c_t = self.t
                    self.isBark = (c_t, True)

                if self.stop_sign.limits_3[0][0] <= self.x <= self.stop_sign.limits_3[0][1] and self.stop_sign.limits_3[1][0]-5-self.additional_bark <= self.func_y(self.y) <= self.stop_sign.limits_3[1][0]:
                    self.speed = max(self.speed - self.bark_rate,0)
                    c_t = self.t
                    self.isBark = (c_t, True)


                
                how_many_steps = self.determine_speed()
                pure_amount = abs(self.direction*how_many_steps)
                amount =  pure_amount + self.dist
                
                bol,pos_y = self.empty_road_y(amount,1)

                if bol:
                    if self.stop_sign.limits_3[0][0] <= (self.x) <= self.stop_sign.limits_3[0][1] and self.stop_sign.limits_3[1][0]<= self.func_y(self.y+pure_amount) <= \
                       self.stop_sign.limits_3[1][1]:

                        # if with the next step we will be at the stop sign borde
                        # the pattern here is the same as it was with the horizontally moving cars, but with on difference
                        # our drivers entering from [1,2,3,4] nodes are now willing to reach 0 or 5 node
                        # their goal is reach any node in the [1,2,3,4] except for themselves, for simplicty
                        # so, when they will be turning, we know with the 100% prob, that their goal node is going to be in two other nodes
                        # for example, suppose we are moving from node 3. We reached traffifc light but we have to turn around.
                        # we know that our dest node is not at 1, which is the opposite node to 3. We also know that we do not have our dest node
                        # at 0 (the left one towards the tarffic light). hence, our dest node is either 3 or 4. with this in mind, we will have to just
                        # make our way to the appropriate highway, which is (101,111), since this is a line for the divers moving in post direction, by x - asxis 

                        if self.stop_sign.go_vertical and self.say_no_to_obgon:
                            lim = self.stop_sign.limits_3[1][0] + 3 
                            desired = lim - self.y

                            b,p = self.empty_road_y(desired,1)

                            if not b:
                                return
                            else:
                                pass

                            if desired <= 0:
                                desired = 0
                                
                            self.road.attemptmove(self, self.x, self.func_y(self.y+desired))

                            width = random.choice(range(11))

                            bol_1,pos_y_1 = self.empty_road_y(width,1)

                            if bol_1:
                                self.road.attemptmove(self, self.x, self.func_y(self.y+width))
                            else:
                                self.road.attemptmove(self, self.x, self.func_y(pos_y_1-1))

                            self.direction = self.set_direction(("horizont",-1))
                            self.say_no_to_obgon = False
                            self.speed = max(self.speed - self.bark_rate,0)
                            c_t = self.t
                            self.isBark = (c_t, True)
                            return
                            
                        
                        # if we did not want to turn, but we can pass through the stop sign - make our move, with the fact thay we did not wait (stand) in the line
                        if self.stop_sign.go_vertical and not self.line_3:
                            self.speed += 6 + self.accel_rate #(self.speed * 0.04)  + self.initial
                            c_t = self.t
                            self.isAccel = (c_t, True)
                            self.road.attemptmove(self, self.x, self.func_y(self.y+pure_amount))
                            return
                        
                        elif self.stop_sign.go_vertical and self.line_3: # if we can pass thorugh the stop sign (and do not want to turn), but we were wainting in the line - make our move + accelarate
                            copy = self.speed
                            self.speed += 6 + self.accel_rate + random.choice(range(5,21)) #10 + self.accel_rate ###3
                            c_t = self.t
                            self.isAccel = (c_t, True)
                            
                            how_many_steps = self.determine_speed()
                            pure_amount = abs(self.direction*how_many_steps)
                            self.road.attemptmove(self, self.x,self.func_y(self.y+pure_amount))
                            self.speed = copy
                            self.line_3 = False
                            self.road.leave_road(self)
                            return
                        
                        # if we cannot pass the stop sign at this time, nervertheless we are located in the area of the stop_sign - in this case we will try to reach opposite border
                        # to escape.
                        elif not self.stop_sign.go_vertical and self.stop_sign.limits_2[0][0] <= (self.x) <= self.stop_sign.limits_2[0][1] and self.stop_sign.limits_2[1][0] <= self.func_y(self.y) <= self.stop_sign.limits_2[1][1]:
                            if self.say_no_to_obgon:
                                self.letter_goal = "4"
                                self.goal_y =  [SIDEWALK_WIDTH-1]
                                self.goal_x = list(range(706,717))
                                self.say_no_to_obgon = False
                            

                            lim = self.stop_sign.limits_2[1][1]
                            desired = lim - self.y

                            if desired <= 0:
                                desired = 0

                            self.road.attemptmove(self, self.x,self.func_y(self.y + desired + random.choice([1,2,3])))
                            return
            

                        # if we cannot move vertically, and we are reching stop sign borders - set the "waiter" (self.line_3) and move to the border
                        elif not self.stop_sign.go_vertical and not self.line_3:
                            limit = self.stop_sign.limits_3[1][0]
                            self.road.attemptmove(self, self.x,self.func_y(limit))
                            self.line_3 = True
                            return

                        elif not self.stop_sign.go_vertical and self.line_3: # if we are in line - wait untill it ise clear for us to turn
                            self.speed = max(self.speed - self.bark_rate,0)
                            self.waiting_time += 1
                            c_t = self.t
                            self.isBark = (c_t, True)
                            return
                    
                            

                    # pattern has a lot in common with horizontal ones
                    # but here we have to add one more parametr - self.prompt
                    # remember that some of our cars may turn around in the traffic light
                    # if they turn - they chanage their direction and go here, but for this cars traffic light might be still red
                    # so we say that cars turning will have self.prompt = True and they will be able to pass through even though, sign is red
                    
                    if self.light.color_vertical == "green" or self.prompt: 
                        self.prompt = False
                        if  self.light.arrow_v  and self.say_no_to_obgon and self.light_coords[0][0] <= self.x <= self.light_coords[0][1] and \
                           self.light_coords[1][0] <= self.func_y(self.y+pure_amount) <= self.light_coords[1][1]:

                            # if we have to turn around at the traffic light - logic is the same as it was at the stop sign -
                            # just make our way to the appropriate highway
                            

                            lim = self.light_coords[1][0] + 23 # #[(213,257),(78,122)] 101,111
                            desired = lim - self.y

                            if desired <= 0:
                                desired = 0
                                
                            self.road.attemptmove(self, self.x,self.func_y(self.y + desired))   #[(213,257),(78,122)]
                            
                            width = random.choice(range(11))

                                

                            bol_1,pos_y_1 = self.empty_road_y(width,1)

                            if bol_1:
                                self.road.attemptmove(self, self.x,self.func_y(self.y + width))
                            else:
                                self.road.attemptmove(self, self.x, pos_y_1- 1)

                            width = random.choice(range(3,7))


                            required_to_leave = (self.light_coords[0][1] - self.x)+width

                            if required_to_leave <= 0:
                                required_to_leave = 0

                            bol_2,pos_x_2 = self.empty_road_x(required_to_leave,1)

                            if bol_2:
                                self.road.attemptmove(self, self.func_x(self.x+required_to_leave),self.y)
                            else:
                                self.road.attemptmove(self, self.func_x(pos_x_2-1),self.y)
                                    
                            self.direction = self.set_direction(("horizont",1))
                            self.speed = max(self.speed - self.bark_rate,0)
                            c_t = self.t
                            self.isBark = (c_t, True)
                            self.say_no_to_obgon = False
                            self.line = False
                            return
                        
                        # if it is a time for the ther derivers to turn (and we are reaching light borders at the next step) - we will wait untill we can go forward
                        elif self.light.arrow_v  and not self.say_no_to_obgon and self.light_coords[0][0] <= self.x <= self.light_coords[0][1] and \
                             self.light_coords[1][0] <= self.func_y(self.y + pure_amount) <= self.light_coords[1][1]:
                            
                            if self.line:
                                self.speed = max(self.speed - self.bark_rate,0)
                                self.waiting_time += 1
                                c_t = self.t
                                self.isBark = (c_t, True)
                                return
                                
                            self.road.attemptmove(self, self.x, self.func_y(self.light_coords[1][0]))
                            self.line = True
                            return

                        # if cannot turn ,however we need to turn - we will wait untill there will be such opportunity
                        elif not self.light.arrow_v and self.say_no_to_obgon and self.light_coords[0][0] <= self.x <= self.light_coords[0][1] and \
                             self.light_coords[1][0] <= self.func_y(self.y+pure_amount) <= self.light_coords[1][1]:
                            
                            if self.line:
                                self.speed = max(self.speed - self.bark_rate,0)
                                self.waiting_time += 1
                                c_t = self.t
                                self.isBark = (c_t, True)
                                return
                                
                            self.road.attemptmove(self, self.x, self.func_y(self.light_coords[1][0]))
                            self.line = True
                            return
                        
                        else:
                            pass

                        # if we made it till here - that means: either one of the followign:
                        # 1: we are not required to turn and we are not obligated to wait till the other drivers will turn - no, we can move forward
                        # 2: we did not reeach the boredrs of the traffic light

                        # here, we make sure that if we are within the area of the traffic light - then we make some accelaration and movements
                        if  self.light_coords[1][0]<self.func_y(self.y)<self.light_coords[1][1] and self.light_coords[0][0] < self.x < self.light_coords[0][1] and not self.line:
                            copy = self.speed
                            self.speed += 10 + self.accel_rate
                            c_t = self.t
                            self.isAccel = (c_t, True)
                            
                            how_many_steps = self.determine_speed()
                            pure_amount = abs(self.direction*how_many_steps)
                            self.road.attemptmove(self, self.x,self.func_y(self.y+pure_amount))
                            self.speed = copy
                            self.road.leave_road(self)
                            return

                        
                        # if we were wainting in the line - accelarate
                        # so if on the previous time step we were wainitng (red sign) - line will be True.
                        # we know with the 100% that drivers are wainitng exactly at the borders of the traffic light, so above if block will not work for us
                        if self.line or self.line_2: 
                            self.speed +=  6 + self.accel_rate + random.choice(range(5,21)) #(self.speed * 0.04)  + self.initial + 20
                            c_t = self.t
                            self.isAccel = (c_t, True)


                        # if we are not in area of the traffic light - do nothing just move
                        self.road.attemptmove(self, self.x, self.func_y(self.y+pure_amount))
                        self.line = False
                        self.line_2 = False
                        self.road.leave_road(self)
                        return

                    
                    else: #if sign is red/yellow
                        if self.line:
                            self.speed = max(self.speed - self.bark_rate,0)
                            self.waiting_time += 1
                            c_t = self.t
                            self.isBark = (c_t, True)
                            return

                        # if we somehow are in the are - get out of there
                        if self.light_coords[1][0]<self.func_y(self.y)<self.light_coords[1][1] and self.light_coords[0][0] < self.x < self.light_coords[0][1]:
                            copy = self.speed
                            self.speed += 6 + self.accel_rate + random.choice(range(10,16)) 
                            c_t = self.t
                            self.isAccel = (c_t, True)
                            how_many_steps = self.determine_speed()
                            pure_amount = abs(self.direction*how_many_steps)
                            amount =  pure_amount + self.dist
                            bol,pos_y = self.empty_road_y(amount,1)

                            if bol:
                                self.road.attemptmove(self, self.x,self.func_y(self.y+pure_amount))
                                self.speed = copy
                                return
                            else:
                                self.road.attemptmove(self, self.x,self.func_y(pos_y -1))
                                self.speed = copy
                                return

                        # reaching the light - go to the borderd and stay there untill it is green
                        if self.light_coords[1][0]<=self.func_y(self.y+pure_amount)<=self.light_coords[1][1] and self.light_coords[0][0] <= self.x <= self.light_coords[0][1]:                                                            
                            limit = self.light_coords[1][0]
                            self.road.attemptmove(self, self.x,self.func_y(limit))
                            self.line = True
                            return
                        else:
                            self.road.attemptmove(self, self.x,self.func_y(self.y+pure_amount))
                            self.road.leave_road(self)
                            return
                        
                else: # if we could not freely move forward (the same behavious as for the horizontal ones)

                    
                    if self.line_3:
                        self.waiting_time += 1
                        self.speed = max(self.speed - self.bark_rate,0)
                        c_t = self.t
                        self.isBark = (c_t, True)
                        return
                    
                    if pos_y - self.y < self.dist:
                        self.speed = max(self.speed - self.bark_rate,0)
                        c_t = self.t
                        self.isBark = (c_t, True)
                        

                    
                    if pos_y-self.dist == self.y:
                        self.speed = max(self.speed - self.bark_rate,0)
                        c_t = self.t
                        self.isBark = (c_t, True)
                        self.line_2 = True
                        self.waiting_time += 1
                        return
                    
                    else:
                        if self.line_2:
                            self.speed +=  6 + self.accel_rate + random.choice(range(5,21)) 
                            c_t = self.t
                            self.isAccel = (c_t, True)
                        
                        if random.random() < OBGON and not self.say_no_to_obgon:
                            choice = random.choice([1,-1])
                            if self.x == highway[0]:
                                self.cannot_move = True
                                choice = 1
                            elif self.x == highway[1]:
                                self.cannot_move = True
                                choice = -1
                            else:
                                pass
                            
                            if self.road.coords.isoccupied(self.x+choice,self.y):
                                
                                if not self.cannot_move:
                                    choice = 1 if choice == -1 else -1
                                else:
                                    self.cannot_move = False

                                    
                                if self.road.coords.isoccupied(self.x+choice,self.y):
                                    pass
                                else:
                                    self.road.attemptmove(self, self.x+choice,self.y)
                                    self.speed = max(self.speed -self.bark_rate,0)
                                    c_t = self.t
                                    self.isBark = (c_t, True)
                                    self.line_2 = False
                                    return
                            else:
                                self.road.attemptmove(self, self.x+choice,self.y)
                                self.speed = max(self.speed - self.bark_rate,0)
                                c_t = self.t
                                self.isBark = (c_t, True)
                                self.line_2 = False
                                return
                            
                        go_to = pos_y - self.dist
                        self.line_2 = False
                        self.road.attemptmove(self, self.x,self.func_y(go_to))
                        self.road.leave_road(self)

####################################################################################################

            else:
                # vertical, direcction = -1
                
                if self.stop_sign.limits_2[0][0] < self.x < self.stop_sign.limits_2[0][1] and self.stop_sign.limits_2[1][0] < self.y < self.stop_sign.limits_2[1][1]:
                    self.stop_sign.dic_vec[self] = (self.x,self.y,self.t)

                if self.speed > self.initial and random.random() <= 0.5:
                    self.speed = max(self.speed - self.bark_rate,0)
                    c_t = self.t
                    self.isBark = (c_t, True)

                if self.speed < self.initial: 
                    self.speed += 6
                    c_t = self.t
                    self.isAccel = (c_t, True)


                    
                option_2 = range(224,235)
                option_4 = range(694,705)

                

                if self.initial_x in option_2:
                    goal_vertical = ["1"]
                    highway = (224,234)
                else:
                    highway = (694,704)
                    goal_vertical = ["3"]



                                
                if highway == (224,234):
                    if self.x > highway[1]:
                        self.x -= (self.x - highway[1])
                        pass
                    if self.x < highway[0]:
                        self.x += (highway[0] - self.x)
                        pass


                                
                if highway == (694,704):
                    if self.x > highway[1]:
                        self.x -= (self.x - highway[1])
                        pass
                    if self.x < highway[0]:
                        self.x += (highway[0] - self.x)
                        pass


                if self.letter_goal not in goal_vertical:
                    self.say_no_to_obgon = True

                if self.say_no_to_obgon and self.x != highway[1]:
                    if self.road.coords.isoccupied(self.x+1,self.y):
                        self.speed = max(self.speed - self.bark_rate,0)
                        self.waiting_time += 1
                        c_t = self.t
                        self.isBark = (c_t, True)
                        return
                    else:
                            
                        self.road.attemptmove(self, self.x+1,self.y)
                        self.speed = max(self.speed - self.bark_rate,0)
                        c_t = self.t
                        self.isBark = (c_t, True)
                        return
                
                elif not self.say_no_to_obgon and self.x == highway[1]:
                    if self.road.coords.isoccupied(self.x-1,self.y):
                        self.road.attemptmove(self, self.x,self.y-1)
                        self.speed = max(self.speed - self.bark_rate,0)
                        c_t = self.t
                        self.isBark = (c_t, True)
                        return
                    else:
                        self.road.attemptmove(self, self.x-1,self.y)
                        self.speed = max(self.speed - self.bark_rate,0)
                        c_t = self.t
                        self.isBark = (c_t, True)
                        return
                

                if self.light_coords[1][1] < self.func_y(self.y) <= self.light_coords[1][1]+10+self.additional_bark and self.light_coords[0][0] <= self.x <= self.light_coords[0][1]:
                    self.speed = max(self.speed - self.bark_rate,0)
                    c_t = self.t
                    self.isBark = (c_t, True)
                

                if self.stop_sign.limits_3[0][0] <= self.x <= self.stop_sign.limits_3[0][1] and self.stop_sign.limits_3[1][1] <= self.func_y(self.y) <= self.stop_sign.limits_3[1][1]+5+self.additional_bark:
                    self.speed = max(self.speed - self.bark_rate,0)
                    c_t = self.t
                    self.isBark = (c_t, True)


                how_many_steps = self.determine_speed()
                pure_amount = abs(self.direction*how_many_steps)
                amount =  pure_amount + self.dist
                
                bol,pos_y = self.empty_road_y(amount,-1)

                if bol:
                    if self.stop_sign.limits_3[0][0] <= (self.x) <= self.stop_sign.limits_3[0][1] and self.stop_sign.limits_3[1][0]<= self.func_y(self.y-pure_amount) <= \
                       self.stop_sign.limits_3[1][1]:

                        if self.stop_sign.go_vertical and self.say_no_to_obgon:
                            lim = self.stop_sign.limits_3[1][1]-15
                            desired = self.y - lim

                            b,p = self.empty_road_y(desired,-1)

                            if not b:
                                return
                            else:
                                pass

                            if desired <= 0:
                                desired = 0
                                
                            self.road.attemptmove(self, self.x, self.func_y(self.y-desired))

                            width = random.choice(range(11))

                            bol_1,pos_y_1 = self.empty_road_y(width,-1)

                            if bol_1:
                                self.road.attemptmove(self, self.x, self.func_y(self.y-width))
                            else:
                                self.road.attemptmove(self, self.x, self.func_y(pos_y_1+1))

                            self.direction = self.set_direction(("horizont",-1))
                            self.say_no_to_obgon = False
                            self.speed = max(self.speed - self.bark_rate,0)
                            c_t = self.t
                            self.isBark = (c_t, True)
                            return

                        
                        if self.stop_sign.go_vertical and not self.line_3:
                            self.speed += 6 + self.accel_rate  
                            c_t = self.t
                            self.isAccel = (c_t, True)
                            
                            self.road.attemptmove(self, self.x, self.func_y(self.y-pure_amount))
                            return
                        
                        elif self.stop_sign.go_vertical and self.line_3:
                            self.road.attemptmove(self, self.x,self.func_y(self.y-pure_amount))
                            copy = self.speed
                            self.speed += 6 + self.accel_rate + random.choice(range(5,21)) # 10
                            c_t = self.t
                            self.isAccel = (c_t, True)
                            how_many_steps = self.determine_speed()
                            pure_amount = abs(self.direction*how_many_steps)
                            self.road.attemptmove(self, self.x,self.func_y(self.y-pure_amount))
                            self.speed = copy
                            self.road.leave_road(self)
                            self.line_3 = False
                            return

                        elif not self.stop_sign.go_vertical and self.stop_sign.limits_2[0][0] <= (self.x) <= self.stop_sign.limits_2[0][1] and self.stop_sign.limits_2[1][0]<= self.func_y(self.y) <= self.stop_sign.limits_2[1][1]:

                            if self.say_no_to_obgon:
                                self.letter_goal = "3"
                                self.goal_y =  [0]
                                self.goal_x = list(range(694,705))
                                self.say_no_to_obgon = False

                                
                            lim = self.stop_sign.limits_2[1][0]
                            desired = self.y - lim

                            if desired <= 0:
                                desired = 0

                            self.road.attemptmove(self, self.x,self.func_y(self.y - desired - random.choice([1,2,3])))
                            return

                            

                        elif not self.stop_sign.go_vertical and not self.line_3:
                            limit = self.stop_sign.limits_3[1][1]
                            self.road.attemptmove(self, self.x,self.func_y(limit))
                            self.line_3 = True
                            return

                        elif not self.stop_sign.go_vertical and self.line_3:
                            self.speed = max(self.speed - self.bark_rate,0)
                            c_t = self.t
                            self.isBark = (c_t, True)
                            self.waiting_time += 1
                            return

                    
                    if self.light.color_vertical == "green" or self.prompt:
                        self.prompt = False
                        
                        if  self.light.arrow_v  and self.say_no_to_obgon and self.light_coords[0][0] <= self.x <= self.light_coords[0][1] and \
                           self.light_coords[1][0] <= self.func_y(self.y-pure_amount) <= self.light_coords[1][1]:
                     

                            lim = self.light_coords[1][1] - 11 # #[(213,257),(78,122)] 101,111
                            desired = self.y - lim

                            if desired <= 0:
                                desired = 0
                                
                            self.road.attemptmove(self, self.x,self.func_y(self.y - desired))   #[(213,257),(78,122)]
                            
                            width = random.choice(range(11))

                                

                            bol_1,pos_y_1 = self.empty_road_y(width,-1)

                            if bol_1:
                                self.road.attemptmove(self, self.x,self.func_y(self.y - width))
                            else:
                                self.road.attemptmove(self, self.x, pos_y_1+ 1)

                            width = random.choice(range(3,7))

                            required_to_leave = (self.light_coords[0][1] - self.x) + width


                            if required_to_leave <= 0:
                                required_to_leave = 0

                            bol_2,pos_x_2 = self.empty_road_x(required_to_leave,1)

                            if bol_2:
                                self.road.attemptmove(self, self.func_x(self.x+required_to_leave),self.y)
                            else:
                                self.road.attemptmove(self, self.func_x(pos_x_2-1),self.y)
                                    
                                    
                            self.direction = self.set_direction(("horizont",1))
                            self.speed = max(self.speed - self.bark_rate,0)
                            c_t = self.t
                            self.isBark = (c_t, True)
                            self.say_no_to_obgon = False
                            self.line = False
                            return
                        
                        elif self.light.arrow_v  and not self.say_no_to_obgon and self.light_coords[0][0] <= self.x <= self.light_coords[0][1] and \
                             self.light_coords[1][0] <= self.func_y(self.y - pure_amount) <= self.light_coords[1][1]:
                            
                            if self.line:
                                self.speed = max(self.speed - self.bark_rate,0)
                                self.waiting_time += 1
                                c_t = self.t
                                self.isBark = (c_t, True)
                                return
                                
                            self.road.attemptmove(self, self.x, self.func_y(self.light_coords[1][1]))
                            self.line = True
                            return
                            
                        elif not self.light.arrow_v and self.say_no_to_obgon and self.light_coords[0][0] <= self.x <= self.light_coords[0][1] and \
                             self.light_coords[1][0] <= self.func_y(self.y - pure_amount) <= self.light_coords[1][1]:
                            
                            if self.line:
                                self.waiting_time += 1
                                self.speed = max(self.speed - self.bark_rate,0)
                                c_t = self.t
                                self.isBark = (c_t, True)
                                return
                                
                            self.road.attemptmove(self, self.x, self.func_y(self.light_coords[1][1]))
                            self.line = True
                            return
                        
                        else:
                            pass
                        
                        
                        if self.light_coords[1][0]<self.func_y(self.y)<self.light_coords[1][1] and self.light_coords[0][0] < self.x < self.light_coords[0][1] and not self.line:
                            copy = self.speed
                            self.speed += 6 + self.accel_rate # 10
                            c_t = self.t
                            self.isAccel = (c_t, True)
                            how_many_steps = self.determine_speed()
                            pure_amount = abs(self.direction*how_many_steps)
                            self.road.attemptmove(self, self.x,self.func_y(self.y-pure_amount))
                            self.speed = copy
                            self.road.leave_road(self)
                            return
                        
                        if self.line or self.line_2:
                            self.speed += 6 + self.accel_rate + random.choice(range(5,21)) #(self.speed * 0.04)  + self.initial
                            c_t = self.t
                            self.isAccel = (c_t, True)

                        
                        self.road.attemptmove(self, self.x, self.func_y(self.y-pure_amount))
                        self.line = False
                        self.line_2 = False
                        self.road.leave_road(self)
                        return
                    else:
                        if self.line:
                            self.speed = max(self.speed - self.bark_rate,0)
                            c_t = self.t
                            self.isBark = (c_t, True)
                            self.waiting_time += 1
                            return
                        if self.light_coords[1][0]<self.func_y(self.y)<self.light_coords[1][1] and self.light_coords[0][0] < self.x < self.light_coords[0][1]:
                            copy = self.speed
                            self.speed += 6 + self.accel_rate + random.choice(range(10,16)) #10
                            c_t = self.t
                            self.isAccel = (c_t, True)
                            how_many_steps = self.determine_speed()
                            pure_amount = abs(self.direction*how_many_steps)
                            amount =  pure_amount + self.dist
                            bol,pos_y = self.empty_road_y(amount,-1)

                            if bol:
                                self.road.attemptmove(self, self.x,self.func_y(self.y-pure_amount))
                                self.speed = copy
                                return
                            else:
                                self.road.attemptmove(self, self.x,self.func_y(pos_y + 1))
                                self.speed = copy
                                return
                            
                        if self.light_coords[1][0]<=self.func_y(self.y-pure_amount)<=self.light_coords[1][1] and self.light_coords[0][0] <= self.x <= self.light_coords[0][1]:
                            limit = self.light_coords[1][1]
                            self.road.attemptmove(self, self.x,self.func_y(limit))
                            self.line = True
                            return
                        else:
                            self.road.attemptmove(self, self.x,self.func_y(self.y-pure_amount))
                            self.road.leave_road(self)
                            return
                else:
                    if self.line_3:
                        self.waiting_time += 1
                        self.speed = max(self.speed - self.bark_rate,0)
                        c_t = self.t
                        self.isBark = (c_t, True)
                        return

                    if self.y - pos_y  < self.dist:
                        self.speed = max(self.speed - self.bark_rate,0)
                        c_t = self.t
                        self.isBark = (c_t, True)

                    
                    if pos_y+self.dist == self.y:
                        self.speed = max(self.speed - self.bark_rate,0)
                        self.line_2 = True
                        self.waiting_time += 1
                        c_t = self.t
                        self.isBark = (c_t, True)
                        return
                    
                    else:
                        if self.line_2:
                            self.speed += 6 + self.accel_rate+random.choice(range(5,21)) #(self.speed * 0.04) + self.initial + 20
                            c_t = self.t
                            self.isAccel = (c_t, True)
                        
                        if random.random() < OBGON and not self.say_no_to_obgon:
                            choice = random.choice([1,-1])
                            if self.x == highway[0]:
                                self.cannot_move = True
                                choice = 1
                            elif self.x == highway[1]:
                                self.cannot_move = True
                                choice = -1
                            else:
                                pass
                            
                            if self.road.coords.isoccupied(self.x+choice,self.y):
                                
                                if not self.cannot_move:
                                    choice = 1 if choice == -1 else -1
                                else:
                                    self.cannot_move = False

                                    
                                if self.road.coords.isoccupied(self.x+choice,self.y):
                                    pass
                                else:
                                    self.road.attemptmove(self, self.x+choice,self.y)
                                    self.speed = max(self.speed - self.bark_rate,0)
                                    c_t = self.t
                                    self.isBark = (c_t, True)
                                    self.line_2 = False
                                    return
                            else:
                                self.road.attemptmove(self, self.x+choice,self.y)
                                self.speed = max(self.speed - self.bark_rate,0)
                                self.line_2 = False
                                c_t = self.t
                                self.isBark = (c_t, True)
                                return
                            
                        go_to = pos_y + self.dist
                        self.line_2 = False
                        self.road.attemptmove(self, self.x,self.func_y(go_to))
                        self.road.leave_road(self)
                    
                    


class Sidewalk:
    """ visualize the motion of cars """

    def __init__(self):
        self.bitmap = [[0.0 for i in range(SIDEWALK_LENGTH)] for j in range(SIDEWALK_WIDTH)]
        self.coords = SWGrid()
        self.arrivals = {}
        self.traffic = Light()
        self.sign = Sign()
        
    def refresh_image(self):
        self.bitmap = [[0.0 for i in range(SIDEWALK_LENGTH)] for j in range(SIDEWALK_WIDTH)]
        for car in self.coords.get_list():
            x = car.x
            y = car.y
            colour = 2
            self.bitmap[y][x] = colour



    def enter_road(self,car,x,y):
        """ enter the road if the space is not occupied"""
        
        if self.coords.isoccupied(x,y):
            return False

        car.x = x
        car.y = y
        self.coords.add_item(x, y, car)
        return True


    def leave_road(self,car):
        """ leave the road if the car got to its destination"""
        
        if car.x in car.goal_x and car.y in car.goal_y: #when we will levave the road, add data to the global lists, for the stats purposes
            TIMES.append(car.t - car.copy_t)
            WAIT.append(car.waiting_time)
            self.coords.remove_item(car)
            IDLING_CO2.append(sum(car.idling))
            ACCEL_CO2.append(sum(car.accel))
            CONSTANT_CO2.append(sum(car.constant))

            s = car.idling + car.accel + car.constant

            #dist = car.determine_dist() # determine, how many step we traveled
            #print(sum(s),dist)
            #print(sum(s)/dist)
            PER_KM.append(sum(s)/car.determine_dist())
                
            
            
            return
        else:
            return False

    def attemptmove(self,car,x,y):
        """ move if the space is not occupied"""
        if self.coords.isoccupied(x, y):
            return False
        
        car.x = x
        car.y = y
        self.coords.move_item(x, y, car)
        return True
    
    def fragment_of_time(self,step):
        if step % S == 0:
            # draw random number of cars for each S step
            amount = abs(int(random.gauss(BUNCH_OF_CARS,0)))

            lst_of_cars = generate_cars(amount,self,self.traffic,self.sign)
    
            for car in lst_of_cars:
                # randomize arrival time for a car
                arrival_time = step + math.ceil(random.expovariate(1/AVERAGE_TIME))
                self.arrivals[car] = arrival_time

            copy = {}

            for key,value in self.arrivals.items():
                if value == step:
                    key.copy_t = key.t = step # when driver entres road - give him a link to the current step, and then we wil always keep it updated
                    key.enter_road(key.x,key.y)
                    continue
                copy[key] = value

            self.arrivals = copy
            
        self.traffic.switch() # stitch the sign of the traffi light

        for car in self.coords.get_list():
            if car.active:
                car.step()
                
        self.sign.switch_vec(step) # switch sign of the stoo sign, if required, for the cars enreting it from south and north
        self.sign.switch(step) # same swtich but for those entering from east and west
        self.sign.merge_queues() # stats...
        self.traffic.monitor_queue(step) # stats...
        self.traffic.determine_len() # stats..
        self.refresh_image()

    def update_time(self): # for eaach car, we will update thier time steps, so that they could remain actual
        for car in self.coords.get_list():
            if car.t == 0:
                continue
            else:
                car.t += 1



class SWGrid: # remained unchanhed
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



def generate_cars(amount,road,light,stop_sign):
    """
       Generate cars with entry node and destination node (both between 0 and 5).
       Should identify how cars start to move: horizontally or vertically.
       Also, initialize x and y coordinates for cars on entry node (calculated manually).
    """
        
    res = []
    for i in range(amount):
        prob = random.random()
        """ with 80% probability cars start from either 0 or 5 node"""
        if prob <= 0.8:
            start = random.choice([0,5])
            if start == 0:
                prob1 = random.random()
                """ with 85% probability cars will go from 0 to 5"""
                if prob1 <= 0.85:
                    res.append(Car((SIDEWALK_LENGTH-1,list(range(101,112))),("horizont",1),0,random.choice(range(101,112)),road,light,"5",stop_sign,"0"))
                else:
                    """ with 15% probability cars will go from 0 to 1:4 with equal probability"""
                    finish = random.choice([1,2,3,4])
                    if finish == 1:
                        res.append(Car((list(range(224,235)),0),("horizont",1),0,random.choice(range(101,112)),road,light,"1",stop_sign,"0"))
                    elif finish == 2:
                        res.append(Car((list(range(236,247)),SIDEWALK_WIDTH-1),("horizont",1),0,random.choice(range(101,112)),road,light,"2",stop_sign,"0"))
                    elif finish == 3:
                        res.append(Car((list(range(694,705)),0),("horizont",1),0,random.choice(range(101,112)),road,light,"3",stop_sign,"0"))
                    else:
                        res.append(Car((list(range(706,717)),SIDEWALK_WIDTH-1),("horizont",1),0,random.choice(range(101,112)),road,light,"4",stop_sign,"0"))
            
                    
            else:
                prob1 = random.random()
                """ with 85% probability cars will go from 5 to 0"""
                if prob1 <= 0.85:
                    res.append(Car((0,list(range(89,100))),("horizont",-1),SIDEWALK_LENGTH-1,random.choice(range(89,100)),road,light,"0",stop_sign,"5"))
                else:
                    """ with 15% probability cars will go from 5 to 1:4 with equal probability"""
                    finish = random.choice([1,2,3,4])
                    if finish == 1:
                        res.append(Car((list(range(224,235)),0),("horizont",-1),SIDEWALK_LENGTH-1,random.choice(range(89,100)),road,light,"1",stop_sign,"5"))
                    elif finish == 2:
                        res.append(Car((list(range(236,247)),SIDEWALK_WIDTH-1),("horizont",-1),SIDEWALK_LENGTH-1,random.choice(range(89,100)),road,light,"2",stop_sign,"5"))
                    elif finish == 3:
                        res.append(Car((list(range(694,705)),0),("horizont",-1),SIDEWALK_LENGTH-1,random.choice(range(89,100)),road,light,"3",stop_sign,"5"))
                    else:
                        res.append(Car((list(range(706,717)),SIDEWALK_WIDTH-1),("horizont",-1),SIDEWALK_LENGTH-1,random.choice(range(89,100)),road,light,"4",stop_sign,"5"))
            
        
        
        else:
            """ with 20% probability cars are not entering the sidewalk from 0 or 5"""
            start = random.choice([1,2,3,4])
            if start == 1:

                prob_2 = random.random()

                if prob_2 <= 0.7:
                    """ with 70% probability cars are not turning for the whole trip and going straight 
                    (either horizontally or vertically)"""
                    finish = 2
                else:
                    finish = random.choice([3,4])
                
                if finish == 2:
                    res.append(Car((list(range(236,247)),SIDEWALK_WIDTH-1),("vertical",1),random.choice(range(236,247)),0,road,light,"2",stop_sign,"1"))
                elif finish == 3:
                    res.append(Car((list(range(694,705)),0),("vertical",1),random.choice(range(236,247)),0,road,light,"3",stop_sign,"1"))
                else: # 4
                    res.append(Car((list(range(706,717)),SIDEWALK_WIDTH-1),("vertical",1),random.choice(range(236,247)),0,road,light,"4",stop_sign,"1"))
                    
            elif start == 2:
                
                prob_2 = random.random()

                if prob_2 <= 0.7:
                    finish = 1
                else:
                    finish = random.choice([3,4])
        
                if finish == 1:
                    res.append(Car((list(range(224,235)),0),("vertical",-1),random.choice(range(224,235)),SIDEWALK_WIDTH-1,road,light,"1",stop_sign,"2"))
                elif finish == 3:
                    res.append(Car((list(range(694,705)),0),("vertical",-1),random.choice(range(224,235)),SIDEWALK_WIDTH-1,road,light,"3",stop_sign,"2"))
                else: #  4
                    res.append(Car((list(range(706,717)),SIDEWALK_WIDTH-1),("vertical",-1),random.choice(range(224,235)),SIDEWALK_WIDTH-1,road,light,"4",stop_sign,"2"))
                    
            elif start == 3:
                
                prob_2 = random.random()

                if prob_2 <= 0.7:
                    finish = 4
                else:
                    finish = random.choice([1,2])

                if finish == 1:
                    res.append(Car((list(range(224,235)),0),("vertical",1),random.choice(range(706,717)),0,road,light,"1",stop_sign,"3"))
                elif finish == 2:
                    res.append(Car((list(range(236,247)),SIDEWALK_WIDTH-1),("vertical",1),random.choice(range(706,717)),0,road,light,"2",stop_sign,"3"))
                else: # 4
                    res.append(Car((list(range(706,717)),SIDEWALK_WIDTH-1),("vertical",1),random.choice(range(706,717)),0,road,light,"4",stop_sign,"3"))
                    
            else: # 4
                prob_2 = random.random()

                if prob_2 <= 0.7:
                    finish = 3
                else:
                    finish = random.choice([1,2])
                    
                if finish == 1:
                    res.append(Car((list(range(224,235)),0),("vertical",-1),random.choice(range(694,705)),SIDEWALK_WIDTH-1,road,light,"1",stop_sign,"4"))
                elif finish == 2:
                    res.append(Car((list(range(236,247)),SIDEWALK_WIDTH-1),("vertical",-1),random.choice(range(694,705)),SIDEWALK_WIDTH-1,road,light,"2",stop_sign,"4"))
                else: # 3
                    res.append(Car((list(range(694,705)),0),("vertical",-1),random.choice(range(694,705)),SIDEWALK_WIDTH-1,road,light,"3",stop_sign,"4"))
        
    return res


def update(*args):
    """ updating image """
    global t
    t += 1
    #if t% 100 == 0:
    #    print(t)
    sw.update_time()
    sw.fragment_of_time(t)
    sw.refresh_image()
    image.set_array(sw.bitmap)

    return image,


for i in range(SIM_NUM_OF_RUNS):
    """ run simulation for fixed number of times (10)"""
    sw = Sidewalk()
    display = plt.figure(figsize=(10, 20))
    image = plt.imshow(sw.bitmap, cmap=colourmap, norm=normalizer, animated=True,interpolation='nearest',aspect = "auto")
    t = 0
    anim = FuncAnimation(display, update, frames=SIM_TIME, interval=1, blit=True, repeat=False)
    plt.show()
    STOP_QUEUE.append(sw.sign.lengths)
    TRAFFIC_QUEUE.append(sw.traffic.lengths)
    print(i)

stats()

plt.plot(len_queue(STOP_QUEUE))
plt.xlabel("Time_Steps") 
plt.ylabel("Count") 
plt.title("Stop Sign Queue length at each tim step, on average")
plt.show()


plt.plot(len_queue(TRAFFIC_QUEUE))
plt.xlabel("Time_Steps") 
plt.ylabel("Count") 
plt.title("Traffic Light Queue length at each tim step, on average")
plt.show()
