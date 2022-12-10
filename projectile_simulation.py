import matplotlib.pyplot as plt
import math
import astropy.coordinates

# I will leave these functions outside of the class, since all class instances will be having access to them

#Takes a 3D vector, and returns a tuple of the x, y, and z components
def spherical_to_components(magnitude, bearing, trajectory):
    return astropy.coordinates.spherical_to_cartesian(magnitude, math.radians(trajectory), math.radians(bearing))

#Takes the x, y, and z components of a 3D vector, and returns a tuple of magnitude, bearing, and trajectory
def components_to_spherical(x, y, z):
    magnitude, trajectory, bearing = astropy.coordinates.cartesian_to_spherical(x, y, z)

    return magnitude, math.degrees(bearing.to_value()), math.degrees(trajectory.to_value())

#Takes two 3D vectors (each specified by magnitude, bearing, and trajectory) and returns a
#tuple representing the sum of the two vectors
def add_spherical_vectors(magnitude1, bearing1, trajectory1, magnitude2, bearing2, trajectory2):
    x1, y1, z1 = spherical_to_components(magnitude1, bearing1, trajectory1)
    x2, y2, z2 = spherical_to_components(magnitude2, bearing2, trajectory2)

    return components_to_spherical(x1 + x2, y1 + y2, z1 + z2)




class Simulate_Percentile: # I decided to ignore intialize step, since we can do all this stuff in __init__ explicitly
    def __init__(self, startingspeed, startingbearing, startingtrajectory, windspeed, windbearing, targetx, targety, timeinterval, x = 0, y = 0, z = 2.2):
        self.x = x # coordinates: x,y,z
        self.y = y
        self.z = z
        self.speed = startingspeed # speed paramettr (or magnitude)
        self.bearing = startingbearing # bearing
        self.trajectory = startingtrajectory # trajectory, these 3 components form a speed vector
        self.targetx = targetx # location of target
        self.targety = targety
        self.interval = timeinterval
        self.t = 0
        self.gravitation_vector = (9.8*self.interval, 0, -90) # gravitation vector as a constant
        self.x_pos = [self.x] # lists for coordinates positions
        self.y_pos = [self.y]
        self.z_pos = [self.z]
        self.timesteps = [self.t] # list for tracking the time
        self.speed_list = [self.speed] #list for tracking speed
        self.wind_vec  = (windspeed, windbearing, 0) # speed vector as a constant
        


        
    def observe(self): # addind the values to corresponding lists
        self.x_pos.append(self.x)
        self.y_pos.append(self.y)
        self.z_pos.append(self.z)
        self.timesteps.append(self.t)
        self.speed_list.append(self.speed)


    def update(self):
        new_pos_x,new_pos_y,new_pos_z = spherical_to_components(self.speed, self.bearing, self.trajectory) # get new coordinates from velocity vector

        # update old coordinates
        self.x = self.x + new_pos_x * self.interval
        self.y = self.y + new_pos_y * self.interval
        self.z = self.z + new_pos_z * self.interval
        
        # using all the equations in order to update the speed vector in the end (speed, bearing, trajectory)
        
        airvelocity_vec = (-self.speed, self.bearing, self.trajectory) # different magnitude but angles are the same
        
        head_wind_vec = add_spherical_vectors(airvelocity_vec[0],airvelocity_vec[1],airvelocity_vec[2], self.wind_vec[0], self.wind_vec[1], self.wind_vec[2])


        drag_force = 0.003 * (head_wind_vec[0]**2)


        drag_accelaration_mag = drag_force/0.2



        drag_velocity_vec = (drag_accelaration_mag*self.interval, head_wind_vec[1], head_wind_vec[2])



        grav_and_drag_vec = add_spherical_vectors(drag_velocity_vec[0], drag_velocity_vec[1], drag_velocity_vec[2], self.gravitation_vector[0], self.gravitation_vector[1], self.gravitation_vector[2])


        new_speed = add_spherical_vectors(self.speed, self.bearing, self.trajectory, grav_and_drag_vec[0], grav_and_drag_vec[1], grav_and_drag_vec[2]) # updating speed, bearing, trajectory
    


        
        self.speed, self.bearing, self.trajectory = new_speed[0],new_speed[1],new_speed[2] # unpacking


        
        self.t += self.interval


    def hit_the_land(self):
        return True if self.z > 0 else False # condition for while loop, while we are on the height > 0

    def measure_dist(self):
        return math.sqrt((self.x - self.targetx)**2 + (self.y-self.targety)**2) # calculate distance on the ground to our target

    def graph(self): # seperate func to do plots
        plt.figure(1)
        plt.plot(self.timesteps,self.x_pos)
        plt.xlabel("t(s)") 
        plt.ylabel("Distance (x) in m") 
        plt.title("X Position vs time")
        plt.figure(2)
        plt.plot(self.x_pos, self.z_pos)
        plt.xlabel("Distance (x) in m")
        plt.ylabel("Height (z) in m") 
        plt.title("X Position vs Z position (height)")
        plt.figure(3)
        plt.plot(self.x_pos, self.y_pos)
        plt.xlabel("Distance (x) in m")
        plt.ylabel("Distance (y) in m") 
        plt.plot(self.targetx, self.targety,'ro')
        plt.title("X Position vs Y Position")
        plt.figure(4)
        plt.plot(self.timesteps,self.speed_list)
        plt.xlabel("t(s)")
        plt.ylabel("Velocity in m/s") 
        plt.title("Velocity vs Time")
        plt.figure(5)
        ax = plt.axes(projection='3d')
        plt.title("3D Path of Ball")
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")
        ax.set_zlabel("z (m)")
        plt.plot(self.x_pos, self.y_pos, self.z_pos)
        plt.plot(self.targetx, self.targety, 0, 'ro')
        plt.show()



        


    def simulation(self):
        while self.hit_the_land():
            self.update()
            self.observe()


        # after we quit the loop, we'll do the plots via graph() func
        else:
            print(f'Distance to target is : {round(self.measure_dist(), 2)}')
            self.graph()


        
#exm1 = Simulate_Percentile(27, 27.8, 32.9, 20, 170, 10, 20, 0.01)
            
exm1 = Simulate_Percentile(40, -35, 50, 25, 90, 30, 30, .01) #your sample (pdf file)


exm1.simulation()


        










