import simpy

class Car(object):
    def __init__(self,env,bcs,name):

        self.env = env
        self.name = name
        self.action = env.process(self.run())
        self.bcs = bcs

    def run(self):
        while True:

            print(self.name," is trying to charge at", self.env.now)

            with bcs.request() as req:
                yield req
                print(self.name, "found a charger, currently charging at ",self.env.now)
                yield(self.env.process(self.charge(5)))

            print(self.name,'done charging, now driving at',self.env.now)
            trip_duration = 2
            yield(self.env.timeout(trip_duration))
                  
    def charge(self,duration):
        yield self.env.timeout(duration)



env = simpy.Environment()
bcs = simpy.Resource(env,capacity=2)

testCar = Car(env,bcs,"one")
testCar2 = Car(env,bcs,"two")
testCar3 = Car(env,bcs,"three")

env.run(until=30)
