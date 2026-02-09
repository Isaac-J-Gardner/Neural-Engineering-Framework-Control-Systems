import pygame
import math
import random
import sys

class paddle:

    def __init__(self, x, y, W, H, v):
        self.x = x
        self.y = y
        self.v = v
        self.W = W
        self.H = H

    def up(self):
        max_y = 400 - self.H/2
        self.y += self.v
        if self.y > max_y:
            self.y = max_y

    def down(self):
        self.y -= self.v
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

    def move(self):
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

    def step(self):
        self.ball.move()
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
            

    def display(self, screen: pygame.Surface):
        pygame.draw.rect(screen, ("#EEEEEE"), ((self.x_offset, self.y_offset),(self.box_W, self.box_H)), width = 1)
        pygame.draw.circle(screen, ("#EEEEEE"), (self.x_offset + self.ball.x, self.disp_H - (self.y_offset + self.ball.y)), radius = 5)
        pygame.draw.rect(screen, ("#EEEEEE"), ((self.x_offset + self.paddle.x + self.paddle.W/2, self.disp_H - (self.y_offset + self.paddle.y + self.paddle.H/2)), (self.paddle.W, self.paddle.H)), width = 0)

    def alg(self):
        if self.paddle.y < self.ball.y:
            self.paddle.up()
        elif self.paddle.y > self.ball.y:
            self.paddle.down()
    
        
        
        
pygame.init()

WIDTH, HEIGHT = 800, 600
box_W, box_H = 400, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Template")
clock = pygame.time.Clock()
FPS = 60

Pong = game(WIDTH, HEIGHT, box_W, box_H)

running = True

while running:
    dt = clock.tick(FPS) / 1000.0  # delta time in seconds

    # -------- Event handling --------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

        elif event.type == pygame.KEYUP:
            # handle key release
            pass

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # handle mouse click
            # print("Mouse down:", event.pos, event.button)
            pass

        elif event.type == pygame.MOUSEBUTTONUP:
            pass

        elif event.type == pygame.MOUSEMOTION:
            # event.pos, event.rel, event.buttons
            pass

    # -------- Continuous input --------
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        Pong.paddle.up()
    if keys[pygame.K_DOWN]:
        Pong.paddle.down()
    mouse_buttons = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    # Example: continuous movement
    if keys[pygame.K_a]:
        pass
    if keys[pygame.K_d]:
        pass

    # -------- Update game state --------
    # update(dt)   
    Pong.step()
    Pong.alg()
    # -------- Render --------
    screen.fill((0, 0, 0))  # background color

    Pong.display(screen)

    pygame.display.flip()

# ------------------------
# Cleanup
# ------------------------
pygame.quit()
sys.exit()
