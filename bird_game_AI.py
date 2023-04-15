import pygame
import random
from collections import namedtuple

pygame.init()

Point = namedtuple('Point', ['x', 'y'])

WHITE = (255, 255, 255)
RED1 = (255, 0, 0)
RED2 = (255, 100, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)

BIRD_SIZE = 20
BLOCK_W = 80
BLOCK_GAP = 150 
SPEED  = 200

font = pygame.font.Font('arial.ttf', 25)

class FlappyAI:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h

        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("Flappy")
        self.clock = pygame.time.Clock()
        self.reset()
        
        
    def reset(self):
        # init game state
        self.bird = [self.w/3, self.h/3, 0] # pos_x, pos_y, vel_y
        self.blocks = [[self.w, random.randint(10, 470-BLOCK_GAP)]]

        self.speed = SPEED
        self.acc = SPEED*11
        self.score = 0

    def _update_ui(self):
        self.display.fill(BLACK)
        
        pygame.draw.rect(self.display, RED1, pygame.Rect(self.bird[0], self.bird[1], BIRD_SIZE, BIRD_SIZE))

        for pt in self.blocks:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt[0], 0, BLOCK_W, pt[1]))
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt[0], pt[1]+BLOCK_GAP, BLOCK_W, self.h-(pt[1]+BLOCK_GAP)))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0]) # displaying on the screen
        pygame.display.flip()


    def _gravity(self):
        t = self.clock.tick(SPEED)/1000
        self.bird[1] = self.bird[1] + self.bird[2]*t + 0.5*self.acc*t**2
        self.bird[2] = self.bird[2] + self.acc*t
        self.bird[2] = min(self.bird[2], SPEED*5)
    
    def _block_control(self):
        for pt in self.blocks:
            pt[0] -= 1
        last_pos = self.blocks[0][0]
        if 640-last_pos>3*BLOCK_W and random.random() < 0.5:
            new_pos = 640
            new_h = random.randint(10, 470-BLOCK_GAP)
        
            self.blocks.insert(0, [new_pos, new_h])

        if self.blocks[-1][0] < -BLOCK_W:
            self.blocks.pop()
    
    def _collisions(self):
        done = False
        if self.bird[1]+BIRD_SIZE > self.h or self.bird[1] < 0:
            done = True
            self.reward = -20
        
        if len(self.blocks)>2:
            pos_x, h = self.blocks[-2]
        else:
            pos_x, h = self.blocks[-1]
        
        bird_x = self.bird[0]
        bird_y = self.bird[1]
        if bird_x-BIRD_SIZE < pos_x + BLOCK_W and bird_x+BIRD_SIZE > pos_x and (bird_y+BIRD_SIZE > h + BLOCK_GAP or bird_y < h):
            done = True
            self.reward = -10
        return done

    def _score_update(self):
        if len(self.blocks)>1 and self.blocks[-2][0]+BLOCK_GAP//2==int(self.bird[0]):
            self.score+=1  
            self.reward = 20   
        elif self.blocks[-1][0]+BLOCK_GAP//2==int(self.bird[0]):
            self.score+=1
            self.reward = 20
    
    def play_step(self, action):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
            if action:
                self.bird[2] = -500

        #mx, my = pygame.mouse.get_pos()
        self.reward = 0

        game_over = self._collisions()
        self._block_control()
        self._gravity()
        self._update_ui()
        self._score_update()
        #self.bird[1] = my
        return self.score, game_over, self.reward