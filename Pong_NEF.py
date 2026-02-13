import pygame
import math
import random
import sys
import nengo
import numpy as np

class paddle:

    def __init__(self, x, y, W, H, v):
        self.x = x
        self.y = y
        self.v = v
        self.W = W
        self.H = H

    def step(self):
        max_y = 400 - self.H/2
        self.y += self.v
        
        if self.y > max_y:
            self.y = max_y
            
        if self.y < self.H/2:
            self.y = self.H/2

    def display(self, screen: pygame.display):
        return
    
class ball:

    def __init__(self, x, y, v):
        self.x = x
        self.y = y
        self.v = v
        theta = (random.random() * 120 - 60) * math.pi / 180
        self.vx = v * math.cos(theta)
        self.vy = v * math.sin(theta)

    def step(self):
        self.x += self.vx
        self.y += self.vy

    def bounce_vert(self, x_corr):
        self.vx = -self.vx
        self.x += 2 * x_corr #x_corr is how far beyond the wall the ball has gone

    def bounce_horiz(self, y_corr):
        self.vy = -self.vy
        self.y += 2 * y_corr

    def bounce_paddle(self, paddle: paddle):
        offset = self.y - paddle.y
        norm_offset = offset/(paddle.H/2)
        max_angle = 60 * math.pi / 180
        angle = norm_offset * max_angle
        self.vx = self.v * math.cos(angle)
        self.vy = self.v * math.sin(angle)

class game:

    def __init__(self, disp_W, disp_H, box_W, box_H):
        self.x_offset = (disp_W - box_W)/2
        self.y_offset = (disp_H - box_H)/2
        
        self.paddle = paddle(5, box_H/2, 6, 100, 5)
        self.ball = ball(box_W/2, box_H/2, 5)
        
        self.disp_W = disp_W
        self.disp_H = disp_H
        self.box_W = box_W
        self.box_H = box_H
        
        self.score = 0

        self.game_state = {"x": self.ball.x,
                      "y": self.ball.y,
                      "vx": self.ball.vx,
                      "vy": self.ball.vy,
                      "py": self.paddle.y
            }

    def step(self):
        self.ball.step()
        self.paddle.step()
        
        if pygame.Rect((self.x_offset + self.paddle.x + self.paddle.W/2, self.disp_H - (self.y_offset + self.paddle.y + self.paddle.H/2)), (self.paddle.W, self.paddle.H)).collidepoint((self.x_offset + self.ball.x - 2.5, self.disp_H - (self.y_offset + self.ball.y))):
            self.ball.bounce_paddle(self.paddle)
            print("hit")
            
        if self.ball.x - 2.5 < 0:
            self.ball.bounce_vert(-self.ball.x + 2.5)
        if self.ball.x + 2.5 > self.box_W:
            self.ball.bounce_vert(self.box_W - self.ball.x - 2.5)
        if self.ball.y - 2.5 < 0:
            self.ball.bounce_horiz(-self.ball.y + 2.5)
        if self.ball.y + 2.5 > self.box_H:
            self.ball.bounce_horiz(self.box_H - self.ball.y - 2.5)

        self.game_state = {"x": self.ball.x,
                      "y": self.ball.y,
                      "vx": self.ball.vx,
                      "vy": self.ball.vy,
                      "py": self.paddle.y
            }

    def display(self, screen: pygame.Surface):
        pygame.draw.rect(screen, ("#EEEEEE"), ((self.x_offset, self.y_offset),(self.box_W, self.box_H)), width = 1)
        pygame.draw.circle(screen, ("#EEEEEE"), (self.x_offset + self.ball.x, self.disp_H - (self.y_offset + self.ball.y)), radius = 5)
        pygame.draw.rect(screen, ("#EEEEEE"), ((self.x_offset + self.paddle.x + self.paddle.W/2, self.disp_H - (self.y_offset + self.paddle.y + self.paddle.H/2)), (self.paddle.W, self.paddle.H)), width = 0)


WIDTH, HEIGHT = 800, 600
box_W, box_H = 400, 400
Pong = game(WIDTH, HEIGHT, box_W, box_H)

model = nengo.Network()
with model:
    
    def input_state(t):
        return np.array([Pong.game_state["x"],
                         Pong.game_state["y"],
                         Pong.game_state["vx"],
                         Pong.game_state["vy"],
                         Pong.game_state["py"]],
                         dtype=np.float32)

    inp = nengo.Node(input_state)

    ens = nengo.Ensemble(n_neurons=300, dimensions=5)
    nengo.Connection(inp, ens)

    def func(x):
        ball_y = x[1]
        vx = x[2]
        paddle_y = x[4]
        u = 2 * (ball_y - paddle_y)
        return np.tanh(u)
                                                                     
    out = nengo.Node(size_in = 1)
    nengo.Connection(ens, out, function=func)

    p_out = nengo.Probe(out, synapse=0.03) #synapse acts as a lowpass filter, smoothing out noise

dt = 1/60
sim = nengo.Simulator(model, dt)
pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Template")
clock = pygame.time.Clock()

running = True

while running:

    # -------- Event handling --------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False 

    # -------- Update game state --------
    # update(dt)   
    Pong.step()
    sim.step()
    Pong.paddle.v = int(100 * sim.data[p_out][-1,0])
    # -------- Render --------
    screen.fill((0, 0, 0))  # background color

    Pong.display(screen)

    pygame.display.flip()

    clock.tick(60)

# ------------------------
# Cleanup
# ------------------------
pygame.quit()
sys.exit()
