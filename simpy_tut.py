import simpy
import random

# Gas Station Simulation

class Car:
    def __init__(self, env, gas_station, name):
        self.env = env # simpy environment in which the car lives
        self.gas_station = gas_station # shared Resource (the pumps)
        self.name = name

    # simulate the amount of time to refuel
    def refuel(self):
        yield self.env.timeout(5) # 5-unit delay at the pump
    
    # the car's behaviour at gas station:
    def action(self):
        with self.gas_station.request() as req: # request a pump
            yield req # wait until a pump is free
            print(f"Time: {self.env.now} , {self.name}: Arrived")
            yield from self.refuel() # refuel takes 5-units of time
            print(f"Time: {self.env.now} , {self.name}: Refueled")

def car_generator(env, gas_station):
    i = 0
    while True:
        t = random.randrange(1,10) 
        yield env.timeout(t) # spawn next car after t time

        c = Car(env, gas_station, name = f"Car {i}")
        env.process(c.action())
        i += 1

env = simpy.Environment()
gas_station = simpy.Resource(env, 2) # define gas station as resource with capactiy 2 (2 pumps)
env.process(car_generator(env, gas_station))

env.run(until=100) # run for 100-units of time