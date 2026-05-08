import CartPole
import numpy as np
from scipy.linalg import solve_continuous_are
import matplotlib.pyplot as plt
from metrics import compute_metrics
import csv

class LQR_Controller:

    def __init__(self):
        self.sim = CartPole.Simulation(gravity=9.8, friction_cart=0, start_angle=0.2, dt=1/1000)

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
        
        R = np.array([[0.0001]])

        P = solve_continuous_are(A, B, Q, R)
        self.K = np.linalg.inv(R) @ B.T @ P
        print(self.K)

        self.X_p = self.K[0][0]/self.K[0][2]
        self.X_d = -(self.K[0][1]/self.K[0][2])
        self.T_p = -self.K[0][2]
        self.T_d = self.K[0][3]

        self.theta_err = []
        self.action1 = []
        self.action2 = []
    
    def step(self):
        state = self.sim.get_state()
        x = np.array([state[0], state[1], state[2], state[3]])
        action = -self.K @ x
        self.sim.step(action[0])
        return action[0]



cs = LQR_Controller()
n_steps = 20000
dt = 0.001

t = np.arange(n_steps) * dt
response = np.zeros(n_steps)
response_x = np.zeros(n_steps)
u = np.zeros(n_steps)
max_x = 0
max_vel_x = 0
max_vel_theta = 0

for i in range(n_steps):
    response[i] = cs.sim.pole.angle
    response_x[i] = cs.sim.cart.x
    u[i] = cs.step()
    if abs(cs.sim.cart.x) > max_x:
        max_x = abs(cs.sim.cart.x)
    if abs(cs.sim.cart.vel) > max_vel_x:
        max_vel_x = abs(cs.sim.cart.vel)
    if abs(cs.sim.pole.ang_vel) > max_vel_theta:
        max_vel_theta = abs(cs.sim.pole.ang_vel)

all_metrics = compute_metrics(t, response, u)
print(all_metrics)

with open("LQR_metrics.csv", 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    csv.QUOTE_NONNUMERIC
    writer.writerow(all_metrics)
    csvfile.close


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