import matplotlib.pyplot as plt
import random


random.seed(7) # set a seed to reflect the same results

rand = random.Random()


class BrakingSim:
    def __init__(self):
        self.pos1 = 0
        self.pos2 = 0
        self.pos3 = 0 # for additional car
        self.vel1 = 0
        self.vel2 = 0
        self.vel3 = 0 # for additional car
        self.isbreaking1 = False
        self.isbreaking2 = False
        self.isbreaking3 = False # for additional car
        self.crash_1_2 = False # we will have 2 crash conditions now
        self.crash_2_3 = False
        self.decelerationrate = 0
        self.reactiontime_2 = 0
        self.reactiontime_3 = 0 # reactiontime for the 3rd driver
        self.interval = 0
        self.t = 0
        self.timesteps = []
        self.bounce_proportion = 0.1

    def initialize(self, gaplength, startingspeed, brakingrate, car1_start_braking_time, minreactiontime, maxreactiontime, timeinterval):
        self.pos1 = gaplength*2
        self.pos2 = gaplength
        self.pos3 = 0
        self.vel1 = startingspeed
        self.vel2 = startingspeed
        self.vel3 = startingspeed 
        self.decelerationrate = brakingrate
        self.brakingstarttime1 = car1_start_braking_time
        self.brakingstarttime2 = None
        self.brakingstarttime3 = None
        self.reactiontime_2 = rand.uniform(minreactiontime, maxreactiontime)
        self.reactiontime_3 = rand.uniform(minreactiontime, maxreactiontime)
        self.interval = timeinterval
        # lists for observing
        self.timesteps = [self.t]
        self.pos1_l = [self.pos1] 
        self.pos2_l = [self.pos2]
        self.pos3_l = [self.pos3]
        self.vel1_l = [self.vel1]
        self.vel2_l = [self.vel2]
        self.vel3_l = [self.vel3]


    def observe(self):        
        self.pos1_l.append(self.pos1)
        self.pos2_l.append(self.pos2)
        self.pos3_l.append(self.pos3)
        self.vel1_l.append(self.vel1)
        self.vel2_l.append(self.vel2)
        self.vel3_l.append(self.vel3)
        self.timesteps.append(self.t)

    def update(self):
        oldpos1 = self.pos1
        oldpos2 = self.pos2
        oldpos3 = self.pos3 # one more position
        newpos1 = self.pos1 + self.vel1 * self.interval
        newpos2 = self.pos2 + self.vel2 * self.interval
        newpos3 = self.pos3 + self.vel3 * self.interval # one more position

        
        if oldpos1 > oldpos2 and newpos1 < newpos2: # crash for 1 and 2
            self.crash_1_2 = True
            
            net_impact_speed_1 = self.vel2 - self.vel1
            print(f"car2 crashed into car1") # indicate a crash
            print("Time of impact: %0.3f" % self.t)
            print("Net impact speed: %0.3f" % net_impact_speed_1)
            print()

            # New positions for both cars are the average of the original newpositions
            avg_pos_1 = (newpos1 + newpos2) / 2
            newpos1 = avg_pos_1
            newpos2 = avg_pos_1

            

            avg_vel_1= (self.vel1 + self.vel2)/2
            
            self.vel1 = avg_vel_1 + self.bounce_proportion * net_impact_speed_1
            self.vel2 = avg_vel_1 - self.bounce_proportion * net_impact_speed_1


        if oldpos2 > oldpos3 and newpos2 < newpos3: # crash for 2 and 3
            self.crash_2_3 = True

            net_impact_speed_2 = self.vel3 - self.vel2
            print(f"car3 crashed into car2")          
            print("Time of impact: %0.3f" % self.t)
            print("Net impact speed: %0.3f" % net_impact_speed_2)
            print()

            avg_pos_2 = (newpos2 + newpos3) / 2
            
            newpos2 = avg_pos_2
            newpos3 = avg_pos_2

            avg_vel_2= (self.vel2 + self.vel3)/2

            
            self.vel2 = avg_vel_2 + self.bounce_proportion * net_impact_speed_2
            self.vel3 = avg_vel_2 - self.bounce_proportion * net_impact_speed_2



        # barking conditons
        if not self.isbreaking1 and self.t > self.brakingstarttime1:
            print(f"car1 started to brake at time {self.t}\n")
            self.isbreaking1 = True
            self.brakingstarttime2 = self.t + self.reactiontime_2
            
        
        if not self.isbreaking2 and self.brakingstarttime2 and self.t > self.brakingstarttime2:
            print(f"car2 started to brake at time {self.t}\n")
            self.isbreaking2 = True
            self.brakingstarttime3 = self.t + self.reactiontime_3


        if not self.isbreaking3 and self.brakingstarttime3 and self.t > self.brakingstarttime3:
            print(f"car3 started to brake at time {self.t}\n")
            self.isbreaking3 = True
            

            
        self.pos1 = newpos1 # updating pos
        self.pos2 = newpos2
        self.pos3 = newpos3

        if self.isbreaking1: # if car barks - decrase in speed
            self.vel1 = max(self.vel1 - self.decelerationrate * self.interval, 0)
            
        if self.isbreaking2:
            self.vel2 = max(self.vel2 - self.decelerationrate * self.interval, 0)
            
        if self.isbreaking3:
            self.vel3 = max(self.vel3 - self.decelerationrate * self.interval, 0)


        self.t += self.interval
    

    def runsim(self, gaplength, startingspeed, brakingrate, car1_start_braking_time, minreactiontime, 
                   maxreactiontime, timeinterval):
        
        self.initialize(gaplength, startingspeed, brakingrate, car1_start_braking_time, minreactiontime,
                   maxreactiontime, timeinterval)

        while self.vel1 > 0 or self.vel2 > 0 or self.vel3 > 0:
            # more prints! for accuracy if you want to see
            #print(f'\nVelocity::: first: {self.vel1}, second: {self.vel2}, third: {self.vel3}')
            #print(f'Distance::: first: {self.pos1}, second: {self.pos2}, third: {self.pos3}')
            #print(f'Barking1 : {self.isbreaking1}, Barking2 : {self.isbreaking2}, Barking : {self.isbreaking3}')
            #print(f'Time: {self.t}\n')
            self.update()
            self.observe()


        # plots
        plt.figure(1)
        plt.plot(self.timesteps, self.vel1_l)
        plt.plot(self.timesteps, self.vel2_l)
        plt.plot(self.timesteps, self.vel3_l)
        plt.figure(2)
        plt.plot(self.timesteps, self.pos1_l)
        plt.plot(self.timesteps, self.pos2_l)
        plt.plot(self.timesteps, self.pos3_l)

        plt.show()
        


            

def main():
    sim = BrakingSim()
    sim.runsim(10, 28, 12, 2, .5, 1.25, .1)





if __name__ == '__main__':
    main()


        
        
#print(random.uniform(.5, 1.25))



























        
        
