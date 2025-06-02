import simpy
import time
import matplotlib.pyplot as plt
import random

PROCESS_TIME_MEAN = 1.0
PROCESS_TIME_STD = 0.1
SEED = 12307987
random.seed(SEED)

def job(env, id):
    process_time = 1
    yield env.timeout(process_time)

def simulate_jobs(num_jobs):
    env = simpy.Environment()
    for i in range(num_jobs):
        env.process(job(env, i))

    start_time = time.time()
    env.run()
    end_time = time.time()

    return end_time - start_time

#job_counts = [10, 100, 500, 1000, 5000, 10000, 20000]
runtimes = []

for count in range(10,10010,1000):
    runtime = simulate_jobs(count)
    runtimes.append(runtime)
    print(f"{count} jobs took {runtime:.4f} seconds")

plt.figure(figsize=(10, 6))
plt.plot(range(10,10010,1000), runtimes, marker='o')
plt.title("SimPy Simulation Runtime vs Number of Jobs")
plt.xlabel("Number of Jobs")
plt.ylabel("Runtime (seconds)")
plt.grid(True)
plt.tight_layout()
plt.show()
