import pygame
import math
import random
import sys
import os
import neat
import pickle
import Pong as Pong

class NEAT_trainer:

    def __init__(self, dwidth, dheight, bwidth, bheight):
        self.dwidth = dwidth
        self.dheight = dheight
        self.bwidth = bwidth
        self.bheight = bheight
        self.game = Pong.game(dwidth, dheight, bwidth, bheight, True, False)

    def test_ai(self, config):
        with open("best_neat_ai", "rb") as f:
            winner = pickle.load(f)
        winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
        self.game = Pong.game(self.dwidth, self.dheight, self.bwidth, self.bheight, True, True)
        while not self.game.end:
            self.game.loop()
            inp = self.game.get_game_state()
            
            output = winner_net.activate((inp[0], inp[1], inp[2], inp[3], inp[4], inp[5]))
            decision = output[0] - output[1]
            self.game.change_paddle_vel(0.2*decision)

    def train_ai(self, genome, config):
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        self.genome = genome
        max_hits = 25
        while not self.game.end:
            self.game.loop()
            inp = self.game.get_game_state()


            if self.game.score > max_hits:
                self.game.end = True
                break
            
            output = net.activate((inp[0], inp[1], inp[2], inp[3], inp[4], inp[5]))
            decision = output[0] - output[1]
            self.game.change_paddle_vel(0.2*decision)

        mean_squared_error = self.MSE(self.game.error)
        self.genome.fitness += self.game.score / mean_squared_error
        return False

    def MSE(self, error_vals):
        MeSE = 0
        for error in error_vals:
            MeSE += error * error
        MeSE = MeSE/len(error_vals)
        return MeSE
    
def eval_genomes(genomes, config):
    WIDTH, HEIGHT = 800, 600
    box_W, box_H = 400, 400
    
    for i, (genome_ID, genome) in enumerate(genomes):
        print(i)
        genome.fitness = 0
        for j in range(5):
            trainer = NEAT_trainer(WIDTH, HEIGHT, box_W, box_H)

            force_quit = trainer.train_ai(genome, config)
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
            
def test_winner(config):
    WIDTH, HEIGHT = 800, 600
    box_W, box_H = 400, 400
    tester = NEAT_trainer(WIDTH, HEIGHT, box_W, box_H)
    tester.test_ai(config)
        
if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'Neat_Config.txt')

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    run_neat(config)
    test_winner(config)
    

