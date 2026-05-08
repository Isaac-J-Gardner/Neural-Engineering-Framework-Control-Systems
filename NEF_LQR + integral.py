import CartPole
import numpy as np
from scipy.linalg import solve_continuous_are
import math
import csv
import nengo
from metrics import compute_metrics
import matplotlib.pyplot as plt
from collections import deque

class LQR_NEF_Controller:

    def __init__(self, seed, Ki):
        self.sim = CartPole.Simulation(gravity=9.8, friction_cart=0, start_angle=0.2)
        self.integral = deque(maxlen=100)
        self.inter = 0
        self.Ki = Ki

        self.env_state = {
            "cart_err": 0.0,
            "cart_vel": 0.0,
            "pole_ang": 0.0,
            "pole_vel": 0.0,
        }

        self.controller_out = {
            "action": 0.0
        }

        cm = self.sim.cart.mass  # cm in your code
        m = self.sim.pole.mass
        l = self.sim.pole.length
        g = self.sim.g

        A = np.array([
            [0, 1,           0,  0],
            [0, 0,  -m*g/cm,     0],
            [0, 0,           0,  1],
            [0, 0,  (cm+m)*g/(cm*l), 0]
        ])

        B = np.array([
            [0],
            [1/cm],
            [0],
            [-1/(cm*l)]
        ])

        Q = np.array([[0, 0, 0, 0],
                      [0, 0, 0, 0],
                      [0, 0, 10, 0],
                      [0, 0, 0, 10]])
        
        R = np.array([[0.0001]])

        P = solve_continuous_are(A, B, Q, R)
        self.K = np.linalg.inv(R) @ B.T @ P
        self.model = nengo.Network(seed=seed)
        self.dt = self.sim.dt

        with self.model:
            integral_in = nengo.Node(lambda t: sum(self.integral))
            cart_err_in = nengo.Node(lambda t: self.env_state["cart_err"])
            cart_vel_in = nengo.Node(lambda t: self.env_state["cart_vel"])
            theta_in = nengo.Node(lambda t: self.env_state["pole_ang"])
            theta_dot_in = nengo.Node(lambda t: self.env_state["pole_vel"])

            ens = nengo.Ensemble(100, 1, radius=200)

            cart_con = nengo.Connection(cart_err_in, ens, synapse = 0.0075, transform=-self.K[0][0])
            vel_con = nengo.Connection(cart_vel_in, ens, synapse = 0.0075, transform=-self.K[0][1])
            theta_con = nengo.Connection(theta_in, ens, synapse = 0.0075, transform=-self.K[0][2])
            theta_dot_con = nengo.Connection(theta_dot_in, ens, synapse = 0.0075, transform=-self.K[0][3])
            integral_con = nengo.Connection(integral_in, ens, synapse=0.0075, transform=self.Ki)

            # Output node: stores latest action into Python variable
            def save_action(t, x):
                self.controller_out["action"] = x[0]

            action_sink = nengo.Node(save_action, size_in=1, size_out=0)
            nengo.Connection(ens, action_sink, synapse=0.0075)

        self.simulator = nengo.Simulator(self.model, self.dt)

    def step(self):
        state = self.sim.get_state()
        self.env_state["pole_ang"] = state[2]
        self.env_state["pole_vel"] = state[3]
        self.integral.append(state[2])
        self.simulator.step()
        action = self.controller_out["action"]
        self.sim.step(action)
        return action


n_steps = 2000
dt = 0.01
trials = 5
t = np.arange(n_steps) * dt
ki_steps = 11
iae = np.zeros(ki_steps)
itae = np.zeros(ki_steps)
ki = np.arange(ki_steps)/(ki_steps-1) * 1
metrics = []

for j in range(ki_steps):
    response = np.zeros(n_steps)
    u = np.zeros(n_steps)
    for seed in range(trials):
        cs = LQR_NEF_Controller(seed = seed, Ki = ki[j])
        
        for i in range(n_steps):
            response[i] += cs.sim.pole.angle
            u[i] += cs.step()

    response /= trials
    print(response[len(response)-1])
    u /= trials
    all_metrics = compute_metrics(t, response, u)
    iae[j] = all_metrics[4]
    itae[j] = all_metrics[5]
    metrics.append(all_metrics)
    print(all_metrics)


with open("integral_sweep.csv", 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    csv.QUOTE_NONNUMERIC
    for i in range(0, len(metrics)):
        writer.writerow(metrics[i])
    csvfile.close


fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

ax1.plot(ki, iae)
ax1.set_ylabel("IAE")
ax1.set_title("LQR integral response")

ax2.plot(ki, itae)
ax2.set_ylabel("ITAE")
ax2.set_xlabel("Ki")

plt.tight_layout()
plt.show()