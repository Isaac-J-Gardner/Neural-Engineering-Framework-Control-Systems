import CartPole
import numpy as np
from scipy.linalg import solve_continuous_are
import math
import csv
import nengo
from metrics import compute_metrics
import matplotlib.pyplot as plt

class dt_test:

    def __init__(self, seed=0, dt = 0.001):
        self.dt = dt
        self.seed = seed

        with nengo.Network(seed=self.seed) as self.model:
            inp = nengo.Node(output=1.0)  # constant input
            ens = nengo.Ensemble(n_neurons=100, dimensions=1, radius = 1)
            out = nengo.Node(size_in=1)
            
            nengo.Connection(inp, ens)
            nengo.Connection(ens, out)
            
            self.p_in = nengo.Probe(inp)
            self.p_out = nengo.Probe(out, synapse=0.1)

    def step(self):
        with nengo.Simulator(self.model, self.dt) as sim:
            sim.run(1.0)
            return sim.data[self.p_out][-1][0]

points = 50
start = 0.0001
r = 1000
scaler = r**(1/points)
outputs = np.zeros(points)
dt = np.zeros(points)
seeds=1
for i in range(points):
    dt[i] = start*(scaler**i)
    for seed in range(seeds):
        cs = dt_test(seed=seed, dt=start*(scaler**i))
        outputs[i] += cs.step()

outputs /= seeds
lgdt = np.log(dt)
lgout = np.log(outputs)*20

test_outputs = np.zeros(len(dt))
for i in range(len(dt)):
    test_outputs[i] = 0.974/((1 + (dt[i]/0.0034)**5)**1/5)

lgtest = np.log(test_outputs)*20

print(max(outputs), max(lgout))

fig, (ax1,ax2) = plt.subplots(1, 2)

ax1.plot(dt, outputs, 'b-')
ax1.set_ylabel("Output", color='b')
ax1.set_xlabel("Simulation dt")
ax1.set_title("Output attenutation against Simulation dt")
ax1.tick_params(axis='y', labelcolor='b')
ax1.axvline(x=0.001, color='r', linestyle='--', label='Default dt (0.001)')
ax1.grid()
ax1.legend()

ax2.plot(dt, lgout)
ax2.set_xlabel("Log(dt)")
ax2.axvline(x=0.001, color='r', linestyle='--', label='Default dt (0.001)')
ax2.set_ylabel("Output Attenuation (dB)")
ax2.set_xscale('log')
ax2.set_title("dB-Log: Output vs dt")
ax2.grid()
ax2.grid(which="minor", color="0.9")
ax2.legend()

ax3 = ax2.twinx()
ax3.plot(dt, lgtest, 'r-')
ax3.set_xscale('log')



plt.tight_layout()
plt.show()

