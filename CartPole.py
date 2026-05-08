import math
import random
from collections import deque

ANG_COR = -math.pi / 2  # display correction: 0 = up, pi = down


def normalize_angle(a):
    return math.atan2(math.sin(a), math.cos(a))


class Pole:

    def __init__(self, length=2.0, mass=1, start_angle=0.0):
        self.length = length
        self.mass = mass
        self.angle = start_angle
        self.ang_vel = 0.0
        self.ang_acc = 0.0
        self.end_x = 0.0
        self.end_y = 0.0

    def update_end_pos(self):
        self.end_x = math.cos(self.angle + ANG_COR)
        self.end_y = math.sin(self.angle + ANG_COR)


class Cart:

    def __init__(self, mass=5, friction=0.0):
        self.mass = mass
        self.friction = friction
        self.x = 0.0
        self.vel = 0.0
        self.acc = 0.0


class Simulation:

    def __init__(
        self,
        dt = 1/100,
        gravity=9.8,
        friction_cart=5.0,
        start_angle=0.1,
        random_side = 0,
        max_error_history=10000,
    ):

        self.angle = start_angle
        self.dt = dt
        self.pole = Pole(start_angle=self.angle)
        self.cart = Cart(friction=friction_cart)
        self.g = gravity
        self.error_history = deque(maxlen=max_error_history)
        self.latest_error = 0.0
        self.frame = 0

    def step(self, applied_force):
        cart = self.cart
        pole = self.pole

        m = pole.mass
        cm = cart.mass
        l = pole.length
        theta = pole.angle
        theta_dot = pole.ang_vel
        f = applied_force - cart.vel * cart.friction
        g = self.g

        s = math.sin(theta)
        c = math.cos(theta)

        cart.acc = (m * l * s * theta_dot**2 + f - m * g * s * c) / (m * s**2 + cm)
        pole.ang_acc = ((m + cm) * g * s - m * l * s * c * theta_dot**2 - f * c) / (m * l * s**2 + cm * l)

        # Semi-implicit Euler integration
        cart.vel += cart.acc * self.dt
        pole.ang_vel += pole.ang_acc * self.dt

        cart.x += cart.vel * self.dt
        pole.angle = normalize_angle(pole.angle + pole.ang_vel * self.dt)

        pole.update_end_pos()

        self.latest_error = pole.angle
        self.error_history.append(self.latest_error)
        self.frame += 1

    def reset(self):
        self.pole.angle = self.angle
        self.pole.ang_vel = 0.0
        self.pole.ang_acc = 0.0
        self.cart.x = 0.0
        self.cart.vel = 0.0
        self.cart.acc = 0.0
        self.error_history.clear()
        self.latest_error = 0.0
        self.frame = 0

    def get_state(self):
        return [self.cart.x, self.cart.vel, self.pole.angle, self.pole.ang_vel]