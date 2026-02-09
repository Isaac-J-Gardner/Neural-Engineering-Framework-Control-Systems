import pygame
import math
import random
import sys
import os
import neat

pygame.init()

class paddle:

    def __init__(self, x, y, W, H, v):
        self.x = x
        self.y = y
        self.v = v
        self.W = W
        self.H = H

    def up(self):
        self.y += self.v

    def down(self):
        self.y -= self.v

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
        self.end = False

        self.game_state = {"x": self.ball.x,
                          "y": self.ball.y,
                          "vx": self.ball.vx,
                          "vy": self.ball.vy,
                          "py": self.paddle.y
                }
        

    def step(self):
        self.ball.step()
        
        self.collision_handler()

        self.game_state = {"x": self.ball.x,
                      "y": self.ball.y,
                      "vx": self.ball.vx,
                      "vy": self.ball.vy,
                      "py": self.paddle.y
            }

        game_info = [self.game_state["x"],
                    self.game_state["y"],
                    self.game_state["vx"],
                    self.game_state["vy"],
                    self.game_state["py"]]
        
        return game_info

    def collision_handler(self):
        if pygame.Rect((self.x_offset + self.paddle.x + self.paddle.W/2, self.disp_H - (self.y_offset + self.paddle.y + self.paddle.H/2)), (self.paddle.W, self.paddle.H)).collidepoint((self.x_offset + self.ball.x - 2.5, self.disp_H - (self.y_offset + self.ball.y))):
            self.ball.bounce_paddle(self.paddle)
            self.score += 1
            
        if self.ball.x - 2.5 < 0:
            self.ball.bounce_vert(-self.ball.x + 2.5)
            self.end = True
            return
            
        if self.ball.x + 2.5 > self.box_W:
            self.ball.bounce_vert(self.box_W - self.ball.x - 2.5)
        if self.ball.y - 2.5 < 0:
            self.ball.bounce_horiz(-self.ball.y + 2.5)
        if self.ball.y + 2.5 > self.box_H:
            self.ball.bounce_horiz(self.box_H - self.ball.y - 2.5)

    def move_paddle(self, up):
        if up == True:
            self.paddle.up()
            if self.paddle.y + self.paddle.H/2 > self.box_H:
                self.paddle.y = self.box_H - self.paddle.H/2
        if up == False:
            self.paddle.down()
            if self.paddle.y - self.paddle.H/2 < 0:
                self.paddle.y = self.paddle.H/2

    def reset(self):
        self.paddle = paddle(5, box_H/2, 6, 100, 5)
        self.ball = ball(box_W/2, box_H/2, 5)

    def display(self, screen: pygame.Surface):
        pygame.draw.rect(screen, ("#EEEEEE"), ((self.x_offset, self.y_offset),(self.box_W, self.box_H)), width = 1)
        pygame.draw.circle(screen, ("#EEEEEE"), (self.x_offset + self.ball.x, self.disp_H - (self.y_offset + self.ball.y)), radius = 5)
        pygame.draw.rect(screen, ("#EEEEEE"), ((self.x_offset + self.paddle.x + self.paddle.W/2, self.disp_H - (self.y_offset + self.paddle.y + self.paddle.H/2)), (self.paddle.W, self.paddle.H)), width = 0)


class NEAT_trainer:

    def __init__(self, dwidth, dheight, bwidth, bheight):
        self.game = game(dwidth, dheight, bwidth, bheight)

    def train_ai(self, genome, config, screen):
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        self.genome = genome
        max_hits = 100
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True

            inp = self.game.step()

            if self.game.end == True:
                self.genome.fitness += self.game.score
                break
            if self.game.score > max_hits:
                self.genome.fitness += self.game.score
                break
            
            output = net.activate((inp[0], inp[1], inp[2], inp[3], inp[4]))
            decision = output.index(max(output))

            if decision == 1:
                self.game.move_paddle(up = True)
            if decision == 2:
                self.game.move_paddle(up = False)

            screen.fill((0, 0, 0))  # background color
            self.game.display(screen)
            pygame.display.flip()

        return False

            
def eval_genomes(genomes, config):
    WIDTH, HEIGHT = 800, 600
    box_W, box_H = 400, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong Neat")
    
    for i, (genome_ID, genome) in enumerate(genomes):
        print(i)
        genome.fitness = 0
        for j in range(5):
            trainer = NEAT_trainer(WIDTH, HEIGHT, box_W, box_H)

            force_quit = trainer.train_ai(genome, config, screen)
            if force_quit:
                quit()

def run_neat(config):
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))

    winner = p.run(eval_genomes, 50)
    with open("best_neat_ai", "wb") as f:
        pickle.dump(winner, f)
            
        
        
if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'Neat_Config.txt')

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    run_neat(config)
    test_best_network(config)  

# ------------------------
# Cleanup
# ------------------------
pygame.quit()
sys.exit()
