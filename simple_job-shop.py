import simpy
import random
import pandas as pd

'''Scenario:
You have N jobs and M machines. 
Each job has a sequence of machines and processing times needed in order to be completed.
Scheduling priority by deadline (minimizing the lateness of a job)'''

NUM_M1 = 1
NUM_M2 = 1
NUM_M3 = 2

all_jobs = []

class Job:
    def __init__(self, env, name, route, deadline, flow_times, lateness):
        self.env = env
        self.name = name
        self.route = route
        self.deadline = deadline

        # per-job metrics
        self.flow_time = None
        self.lateness_val = None

        # global metrics
        self.flow_times = flow_times # Completion time - Arrival time
        self.lateness = lateness

        # for display purposes
        self.starts = []   # list of (machine_name, start_time)
        self.finishes = []   # list of (machine_name, finish_time)
        self.arrival = None
        self.completion = None
        all_jobs.append(self)
        route_str = " → ".join(f"{m.name}({p})" for m,p in self.route)
        print(f"{self.name} created with route: {route_str}")

        self.action = env.process(self.run()) # start the process as soon as the job is created

    def run(self):
        self.arrival = self.env.now

        for machine, process_time in self.route:
            with machine.request(priority=self.deadline) as req:
                yield req
                start = self.env.now
                self.starts.append((machine.name, start))

                yield self.env.timeout(process_time)
                finish = self.env.now
                self.finishes.append((machine.name, finish))

        self.completion = self.env.now
        self.flow_time = self.completion - self.arrival
        self.lateness_val = self.completion - self.deadline
 
        # append globally for overall stats
        flow_times.append(self.flow_time)
        lateness.append(self.lateness_val)

        
def job_generator(env, machines, flow_times, lateness, interarrival):
    '''
    Generates a batch of 3 to 5 new jobs.
    Each job has a random processing time (1-9) on a random order of 'machines' for its route
    '''

    job_id = 0
    while True:
        num_jobs = random.randint(3, 6)   # spawn 3-5 jobs
        # build a random route
        for _ in range(num_jobs):
            machine_order = random.sample(machines, k=len(machines))
            route = []
            total_process_time = 0
            for machine in machine_order:
                process_time = random.randint(1,5)
                route.append((machine,process_time))
                total_process_time += process_time

            deadline = env.now + total_process_time + random.randint(0,10)#random slack
            
            name = f"Job{job_id}"
            Job(env, name, route, deadline, flow_times, lateness)
            job_id += 1

        # pause job_generator for a random amount of time
        interval = random.expovariate(1.0 / interarrival)
        yield env.timeout(interval) 

def print_schedule_table():
    records = []
    for job in all_jobs:
        if job.arrival is None or job.completion is None:
            continue
        route_str = " → ".join(f"{m.name}({t})" for m, t in job.route)
        records.append({"Job":job.name,
                        "Arrival":job.arrival,
                        "Completion":job.completion,
                        "Flow Time":job.flow_time,
                        "Lateness":job.lateness_val,
                        "Route":route_str})
    df = pd.DataFrame(records).round(2)
    print("\nSCHEDULE TABLE")
    print(df.to_string())



env = simpy.Environment()

# define three machines
m1 = simpy.PriorityResource(env, capacity=NUM_M1)
m2 = simpy.PriorityResource(env, capacity=NUM_M2)
m3 = simpy.PriorityResource(env, capacity=NUM_M3)
m1.name = "M1"
m2.name = "M2"
m3.name = "M3"
machines = [m1,m2,m3]

flow_times = []
lateness = []

env.process(job_generator(env, machines, flow_times, lateness, interarrival=5))
env.run(until=30)

print_schedule_table() 

print ("\nSCHEDULE SUMMARY")
if flow_times:
    print("Avg flow time:", sum(flow_times) / len(flow_times))
if lateness:
    print("Avg lateness:", sum(lateness)/len(lateness))
    print("Max lateness:", max(lateness), "\n")

