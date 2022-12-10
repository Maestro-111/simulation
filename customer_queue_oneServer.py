
import simpy
import numpy as np
import random
import matplotlib.pyplot as plt


rand = random.Random()

avg = []
std = []
disperssion = []

PROB = 0.2 # probability of printing summary

class MM1Sim:

    def __init__(self,flag):
        # Aggregation of data
        self.number_delayed = 0
        self.total_delay = 0
        self.min_delay = None
        self.max_delay = None
        self.delay_step =  []
        self.flag = flag


    def report(self):
        print("Number of customers: %d" % self.number_delayed)
        print("Total delay: %0.4f" % self.total_delay)
        print("Average delay: %0.4f" % (self.avg))
        print("Minimum delay: %0.4f" % self.min_delay)
        print("Maximum delay: %0.4f" % self.max_delay)
        print(f"Disspersion: {round(self.disperssion, 4)}, std: {round(self.std, 4)}, Expected Value of Delay: {round(self.expected_val,4)}")
        

    def runsim(self, number_of_customers, mean_interarrival, mean_service):
        env = simpy.Environment()
        server = simpy.Resource(env, capacity=2) # 2
        env.process(sim.source(env, server, number_of_customers, mean_interarrival, mean_service))
        env.run()

        self.avg = (self.total_delay/self.number_delayed)
        self.disperssion = sum([(i-self.avg)**2 for i in self.delay_step])
        self.std = (self.disperssion)**0.5
        self.expected_val = MM1Sim.expect(self.delay_step)  # basically, the same as mean

        std.append(self.std)
        avg.append(self.avg)
        disperssion.append(self.disperssion)

        if self.flag:
            self.report()
        else:
            pass
        


    # Time between arrivals and service time are now random, so pass in parameters for distributions
    def source(self, env, server, number_of_customers, mean_interarrival, mean_service):
        """Source generates customers randomly"""
        for i in range(number_of_customers):
            # Wait a random amount of time before creating and scheduling customer
            yield env.timeout(rand.expovariate(1/mean_interarrival))

            # Customer service time determined randomly
            c = self.customer(env, i+1, rand.expovariate(1/mean_service), server)
            env.process(c)

    def customer(self, env, id, service_time, server):
        arrival = env.now
        #print("ID %d arriving at: %0.1f" % (id, arrival))

        with server.request() as request:
            yield request
            self.number_delayed += 1
            wait_time = env.now - arrival
            self.total_delay += wait_time
            self.delay_step.append(wait_time)
            if self.min_delay is None or wait_time < self.min_delay:
                self.min_delay = wait_time
            if self.max_delay is None or wait_time > self.max_delay:
                self.max_delay = wait_time

            yield env.timeout(service_time)


    
    @staticmethod   # we don't need a link for self, just make it static then       
    def expect(mean:list): # to calculate expected val
        values,freques = np.unique(mean, return_counts = True)
        #print(freques)
        s = sum(freques)
        freques2 = []
        for i in range(len(freques)):
             freques2.append(freques[i]/s) # to obtain the frequnecy of the particular value
             
        #print(sum(freques2)) should be 1
        
        return sum([values[i]*freques2[i] for i in range(len(freques2))])
            


if __name__ == '__main__':
    display_rep = False # we will randomy pick only one summary from 1000 runs
    for i in range(500):
        if not display_rep and random.random() < PROB: # if so, display summary
            sim = MM1Sim(True)
            sim.runsim(1000, 0.5, 1.5)
            display_rep = True
            print("\n")
        else: # if not, ignor
            sim = MM1Sim(False)
            sim.runsim(1000, 0.5, 1.5)
    else:
        if not display_rep: # if display_rep is still False, hence we did not print summary report
            sim = MM1Sim(True)
            sim.runsim(1000, 0.5, 1.5)
        else:
            sim = MM1Sim(False)
            sim.runsim(1000, 0.5, 1.5)

    # graphs
    plt.figure(1)
    plt.hist(avg)
    plt.title("average")
    plt.figure(2)
    plt.hist(disperssion)
    plt.title("disp")
    plt.figure(3)
    plt.hist(std)
    plt.title("std")
    plt.show()
