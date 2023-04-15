import torch
import random
import numpy as np
from collections import deque

from bird_game_AI import FlappyAI, Point

from model import LinearQnet, QTrainer

from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 100
LR = 0.0001

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.99
        self.memory = deque(maxlen=MAX_MEMORY)
        self.val = 1

        # model, trianer
        self.model = LinearQnet(4, 256, 1)
        self.trainer = QTrainer(self.model, LR, self.gamma)

    def get_state(self, game):
        game = FlappyAI()
        bird_vals = game.bird # bird_x, bird_y, velocity
        if len(game.blocks)>2:
            nearest_block_vals = game.blocks[-2]
        else:
            nearest_block_vals = game.blocks[-1]

        state = [
            min(game.h-bird_vals[1],bird_vals[1]), bird_vals[2],
            nearest_block_vals[0], nearest_block_vals[1]
        ]

        return np.array(state, dtype=float)
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    
    def train_long_memory(self):
        if len(self.memory)>BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory
        
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
    
    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    
    def get_action(self, state, record):
        # exploration exploitation tradeoff
        self.epsilon = 1/(1+1.002**-self.n_games)
        final_move = 0
        if record == 0:
            if self.n_games%20:
                self.val+=1
        
        if (self.n_games%self.val == 0 and record == 0) or random.random() > self.epsilon:
            final_move = int(random.random()<0.05)
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = int(prediction>0.5) # int
            final_move = move
        
        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0

    agent = Agent()
    game = FlappyAI()

    while True:
        #print(game.blocks[-1][0])
        # get old state
        state_old = agent.get_state(game)

        # get move
        final_move = agent.get_action(state_old, record)

        # perform move and get new state
        score, done, reward = game.play_step(final_move)
        state_new = agent.get_state(game)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train long memory - replay memory, experience replay
            # plot results
            print(reward)
            game.reset()
            agent.n_games+=1
            agent.train_long_memory()
            
            if score > record:
                
                record = score
                agent.model.save()

            print('Game:', agent.n_games, 'Score:', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score/agent.n_games
            plot_mean_scores.append(mean_score)

            plot(plot_scores, plot_mean_scores)

        

if __name__ == '__main__':
    train()
    