import pygame
import math
import random
import sys
pygame.init()

class paddle:

    def __init__(self, x, y, W, H):
        self.x = x
        self.y = y
        self.vel = 0
        self.acc = 0
        self.W = W
        self.H = H

    def step(self):
        self.vel += self.acc
        max_y = 400 - self.H/2
        self.y += self.vel
        
        if self.y > max_y:
            self.y = max_y
            self.vel = 0
            
        if self.y < self.H/2:
            self.y = self.H/2
            self.vel = 0
    
class ball:

    def __init__(self, x, y, v):
        self.x = x
        self.y = y
        self.v = v
        self.radius = 2.5
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

    def __init__(self, disp_W, disp_H, box_W, box_H, do_display, do_tick):
        self.screen = pygame.display.set_mode((disp_W, disp_H))
        pygame.display.set_caption("Pong Sim")
        self.clock = pygame.time.Clock()
        self.FPS = 60

        self.x_offset = (disp_W - box_W)/2
        self.y_offset = (disp_H - box_H)/2
        
        self.paddle = paddle(5, box_H/2, 6, 100)
        self.ball = ball(box_W, box_H/2, 5)
        
        self.disp_W = disp_W
        self.disp_H = disp_H
        self.box_W = box_W
        self.box_H = box_H

        self.do_display = do_display
        self.do_tick = do_tick
        
        self.score = 0
        self.end = False

        self.game_state = {"x": self.ball.x,
                          "y": self.ball.y,
                          "vx": self.ball.vx,
                          "vy": self.ball.vy,
                          "py": self.paddle.y,
                          "pvel": self.paddle.vel,
                          "pacc": self.paddle.acc
                }
        
    def loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.change_paddle_vel(0.1)
        if keys[pygame.K_DOWN]:
            self.change_paddle_vel(-0.1)

        self.step()

        if self.do_display: 
            self.display(self.screen)
            pygame.display.flip()

        if self.do_tick: 
            self.clock.tick(self.FPS)
        

    def step(self):
        self.ball.step()
        self.paddle.step()
        
        self.collision_handler()

        self.game_state = {"x": self.ball.x,
                          "y": self.ball.y,
                          "vx": self.ball.vx,
                          "vy": self.ball.vy,
                          "py": self.paddle.y,
                          "pvel": self.paddle.vel,
                          "pacc": self.paddle.acc
                }

        game_info = [self.game_state["x"],
                    self.game_state["y"],
                    self.game_state["vx"],
                    self.game_state["vy"],
                    self.game_state["py"],
                    self.game_state["pvel"],
                    self.game_state["pacc"]]
        
        return game_info
    
    def get_game_state(self):
        game_info = [self.game_state["x"],
                    self.game_state["y"],
                    self.game_state["vx"],
                    self.game_state["vy"],
                    self.game_state["py"],
                    self.game_state["pvel"],
                    self.game_state["pacc"]]
        
        return game_info
    
    def change_paddle_vel(self, acc):
        self.paddle.vel += acc

    def collision_handler(self):
        if pygame.Rect((self.x_offset + self.paddle.x + self.paddle.W/2, self.disp_H - (self.y_offset + self.paddle.y + self.paddle.H/2)), (self.paddle.W, self.paddle.H)).collidepoint((self.x_offset + self.ball.x - 2.5, self.disp_H - (self.y_offset + self.ball.y))):
            self.ball.bounce_paddle(self.paddle)
            self.score += 1
            
        if self.ball.x - self.ball.radius < 0:
            self.ball.bounce_vert(-self.ball.x + self.ball.radius)
            self.end = True
            return
            
        if self.ball.x + self.ball.radius > self.box_W:
            self.ball.bounce_vert(self.box_W - self.ball.x - self.ball.radius)
        if self.ball.y - self.ball.radius < 0:
            self.ball.bounce_horiz(-self.ball.y + self.ball.radius)
        if self.ball.y + self.ball.radius > self.box_H:
            self.ball.bounce_horiz(self.box_H - self.ball.y - self.ball.radius)



    def reset(self):
        self.paddle = paddle(5, self.box_H/2, 6, 100, 5)
        self.ball = ball(self.box_W/2, self.box_H/2, 5)

    def display(self, screen: pygame.Surface):
        self.screen.fill("#000000")
        pygame.draw.rect(screen, ("#EEEEEE"), ((self.x_offset, self.y_offset),(self.box_W, self.box_H)), width = 1)
        pygame.draw.circle(screen, ("#EEEEEE"), (self.x_offset + self.ball.x, self.disp_H - (self.y_offset + self.ball.y)), radius = 5)
        pygame.draw.rect(screen, ("#EEEEEE"), ((self.x_offset + self.paddle.x + self.paddle.W/2, self.disp_H - (self.y_offset + self.paddle.y + self.paddle.H/2)), (self.paddle.W, self.paddle.H)), width = 0)

    def end_game(self):
        pygame.quit()
        sys.exit()

        
pong = game(800, 600, 400, 400, True, True)

while True:
    pong.loop()