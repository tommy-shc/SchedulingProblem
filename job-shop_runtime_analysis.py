import simpy
import random
import pandas as pd
import time
import matplotlib.pyplot as plt

'''Scenario:
You have N jobs and M machines. 
Each job has a sequence of machines and processing times needed in order to be completed.
Scheduling priority by deadline (minimizing the lateness of a job)'''

NUM_M1 = 1
NUM_M2 = 1
NUM_M3 = 2
flow_times = []
lateness = []

class Job:
    def __init__(self, env, name, route, deadline, flow_times, lateness):
        self.env = env
        self.name = name
        self.route = route
        self.deadline = deadline
        self.starts = [] # list of (machine_name, start_time)
        self.finishes = [] # list of (machine_name, finish_time)

        # global metrics
        self.flow_times = flow_times # Completion time - Arrival time
        self.lateness = lateness

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



#--------- Analysis A) dependent variable = interarrival time of jobs
def measure_interarrival(ir):
    env = simpy.Environment()
    # fixed machines
    m1 = simpy.PriorityResource(env, capacity=NUM_M1)
    m2 = simpy.PriorityResource(env, capacity=NUM_M2)
    m3 = simpy.PriorityResource(env, capacity=NUM_M3)
    m1.name = "M1"
    m2.name = "M2"
    m3.name = "M3"
    machines = [m1,m2,m3]
    flow_times = []
    lateness = []

    env.process(job_generator(env, machines, flow_times, lateness, interarrival=ir))
    t0 = time.perf_counter()
    env.run(until=100)
    t1 = time.perf_counter()
    return t1 - t0

interarrival_rates = [2, 5, 10, 20, 50]
runtimes = []
for ir in interarrival_rates:
    runtimes.append(measure_interarrival(ir))

# build DataFrame
df = pd.DataFrame({
    "Interarrival": interarrival_rates,
    "Runtimes":runtimes}).round(4)
print(df)

# plot
plt.figure(figsize=(7,5))
plt.plot(df["Interarrival"], df["Runtimes"], marker='o')
plt.xlabel("Interarrival time of jobs")
plt.ylabel("Runtime (seconds)")
plt.title("Simulation Runtime vs. Interarrival time of jobs")
plt.grid(True)
plt.tight_layout()
plt.show()


#--------- Analysis B) dependent variable = number machine
def measure_machines(num_machines):
    env = simpy.Environment()

    machines = []
    for i in range(num_machines):
        m = simpy.PriorityResource(env,1)
        m.name = f"M{i+1}"
        machines.append(m)
    flow_times = []
    lateness = []

    env.process(job_generator(env, machines, flow_times, lateness, interarrival=5))
    t0 = time.perf_counter()
    env.run(until=100)
    t1 = time.perf_counter()
    return t1 - t0

machine_counts = [10, 30, 100, 500, 2000]
runtimes = []
for m in machine_counts:
    runtimes.append(measure_machines(m))

# build DataFrame
df = pd.DataFrame({
    "Machines": machine_counts,
    "Runtimes":runtimes}).round(4)
print(df)

# plot
plt.figure(figsize=(7,5))
plt.plot(df["Machines"], df["Runtimes"], marker='o')
plt.xlabel("Number of Machines")
plt.ylabel("Runtime (seconds)")
plt.title("Simulation Runtime vs. Number of Machines")
plt.grid(True)
plt.tight_layout()
plt.show()