import CartPole
import numpy as np
from scipy.linalg import solve_continuous_are
import math
import csv
import nengo
from metrics import compute_metrics
import matplotlib.pyplot as plt
import time

class LQR_PD_Controller:

    def __init__(self, seed, val):
        self.val = val
        self.sim = CartPole.Simulation(gravity=9.8, friction_cart=0, start_angle=0.2, dt=1/1000)
        
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

        Q = np.array([[1, 0, 0, 0],
                      [0, 1, 0, 0],
                      [0, 0, 10, 0],
                      [0, 0, 0, 10]])
        
        R = np.array([[0.1]])

        P = solve_continuous_are(A, B, Q, R)
        self.K = (np.linalg.inv(R) @ B.T @ P)[0]
        self.model = nengo.Network(seed=seed)
        self.dt = self.sim.dt

        self.X_p = self.K[0]/self.K[2]
        self.X_d = -(self.K[1]/self.K[2])
        self.T_p = -self.K[2]
        self.T_d = self.K[3]


        with self.model:
            cart_err_in = nengo.Node(lambda t: self.env_state["cart_err"])
            cart_vel_in = nengo.Node(lambda t: self.env_state["cart_vel"])
            theta_in = nengo.Node(lambda t: self.env_state["pole_ang"])
            theta_dot_in = nengo.Node(lambda t: self.env_state["pole_vel"])

            theta_err = nengo.Ensemble(self.val, 1, radius=0.5)
            action = nengo.Ensemble(self.val, 1, radius=80)

            con1 = nengo.Connection(cart_err_in, theta_err, synapse=0.005, transform=-self.X_p)
            con2 = nengo.Connection(cart_vel_in, theta_err, synapse=0.005, transform=self.X_d)
            con3 = nengo.Connection(theta_in, theta_err, synapse=0.005, transform=-1)

            con4 = nengo.Connection(theta_err, action, synapse=0.005, transform=self.T_p)
            con5 = nengo.Connection(theta_dot_in, action, synapse=0.005, transform=self.T_d)

            self.action_probe = nengo.Probe(action, synapse=0.005)

        start = time.time()
        self.simulator = nengo.Simulator(self.model, self.dt)
        build_time = time.time() - start
        print(build_time)

    def step(self):
        state = self.sim.get_state()
        self.env_state["cart_err"] = state[0]
        self.env_state["cart_vel"] = state[1]
        self.env_state["pole_ang"] = state[2]
        self.env_state["pole_vel"] = state[3]
        self.simulator.step()
        action = self.simulator.data[self.action_probe][-1][0]
        self.sim.step(-action)
        return -action


n_steps = 10000
dt = 0.001
trials = 1

t = np.arange(n_steps) * dt
metrics = []
syn_vals = [2, 512]
for n in range(0, len(syn_vals)):
    val = syn_vals[n]
    print(val)
    response = np.zeros(n_steps)
    response_x = np.zeros(n_steps)
    Q_weighted = np.zeros(n_steps)
    u = np.zeros(n_steps)
    for seed in range(trials):
        cs = LQR_PD_Controller(seed=seed, val=val)
        for i in range(n_steps):
            response[i] += cs.sim.pole.angle
            response_x[i] += cs.sim.cart.x
            Q_weighted[i] = cs.sim.pole.angle * 10 + cs.sim.cart.x
            u[i] += cs.step()
    response /= trials
    response_x/= trials
    u /= trials

    pole_metrics = compute_metrics(t, response, u)
    Q_metrics = compute_metrics(t, Q_weighted, u)
    mets = [pole_metrics[1], Q_metrics[3], Q_metrics[4], Q_metrics[5], Q_metrics[6]]
    metrics.append(mets)

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

    ax1.plot(t, response, 'b-')
    ax1.set_ylabel("Pole Angle (rad)", color='b')
    ax1.set_title("LQR Controller Response")
    ax1.tick_params(axis='y', labelcolor='b')

    ax1_2 = ax1.twinx()
    ax1_2.plot(t, response_x, 'r-')
    ax1_2.set_ylabel("x (m)", color='r')
    ax1_2.tick_params(axis='y', labelcolor='r')

    ax2.plot(t, u)
    ax2.set_ylabel("Control Input")
    ax2.set_xlabel("Time (s)")

    plt.tight_layout()
    plt.show()
    
with open("LQR_NEF_syn_vals.csv", 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    csv.QUOTE_NONNUMERIC
    for i in range(0, len(metrics)):
        writer.writerow(metrics[i])
    csvfile.close