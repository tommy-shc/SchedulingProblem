import simpy
import random
import matplotlib.pyplot as plt

def stage1(env, name, machine_a, machine_b_pool, log):
    yield env.timeout(random.uniform(1, 3))


    with machine_a.request() as req_a:
        yield req_a
        start_a = env.now

        duration_a = 3
        yield env.timeout(duration_a)

        log.append({'Job': name, 'Start': start_a, 'Duration': duration_a, 'Machine': 'A'})
        
    yield env.process(stage2(env, name, machine_b_pool, log))

def stage2(env, name, machine_b_pool, log):

    machine_b = yield machine_b_pool.get() #try and get machine b


    with machine_b['res'].request() as req_b:

        yield req_b
        start_b = env.now
        duration_b = 5
        yield env.timeout(duration_b)
        log.append({'Job': name, 'Start': start_b, 'Duration': duration_b, 'Machine': f"B{machine_b['id']}"})

    yield machine_b_pool.put(machine_b)

def generator(env, machine_a, machine_b_pool, log):

    yield env.timeout(0) #needed for simpy to consider it a generator

    for i in range(10):
        job_name = f'J{i}' 
        env.process(stage1(env, job_name, machine_a, machine_b_pool, log))

env = simpy.Environment()
machine_a = simpy.Resource(env, capacity=1)

b_list = []
for i in range(3):
    machine = {'id': i, 'res': simpy.Resource(env, capacity=1)}
    b_list.append(machine)

b_pool = simpy.Store(env)
for b in b_list:
    b_pool.put(b)

log = []
env.process(generator(env, machine_a, b_pool, log))
env.run()


#visulization

def plot(log):
    fig, ax = plt.subplots(figsize=(12, 5))

    m_names_set = set()
    for x in log:
        m_names_set.add(x['Machine'])

    m_names = sorted(m_names_set)

    m_map = {}
    for i, name in enumerate(m_names):
        m_map[name] = i

    c = plt.cm.tab20.colors

    for i, x in enumerate(log):
        y = m_map[x['Machine']] * 10
        ax.broken_barh([(x['Start'], x['Duration'])], (y, 9), facecolors=c[i % len(c)])
        ax.text(x['Start'] + x['Duration'] / 2, y + 4.5, x['Job'], ha='center', va='center', color='white', fontsize=8)

    yticks = []
    for i in range(len(m_names)):
        yticks.append(i * 10 + 4.5)

    ax.set_yticks(yticks)
    ax.set_yticklabels(m_names)
    ax.set_xlabel('Time')
    ax.set_title('Factory Schedule')
    ax.grid(True)
    plt.tight_layout()
    plt.show()

plot(log)
