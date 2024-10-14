"""
The classic game of flappy bird. Make with python
and pygame. Features pixel perfect collision using masks :o

Date Modified:  Jul 30, 2019
Author: Tech With Tim
Estimated Work Time: 5 hours (1 just for that damn collision)
"""
import pygame
import random
import os
import time
import neat
import visualize
import pickle        #voegt bibliotheek pickle toe om winnaar op te kunnen slaan
pygame.font.init()  # init font

WIN_WIDTH = 600
WIN_HEIGHT = 800
FLOOR = 730
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)
DRAW_LINES = False

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")).convert_alpha())
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","bg.png")).convert_alpha(), (600, 900))
bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png"))) for x in range(1,4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")).convert_alpha())

gen = 0

class Bird:
    """
    # Bird class vertegenwoordigd de flappy bird
    """
    MAX_ROTATION = 25
    IMGS = bird_images
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        """
        Initialize the object
        :param x: starting x pos (int)
        :param y: starting y pos (int)
        :return: None
        """
        self.x = x
        self.y = y
        self.tilt = 0  # degrees to tilt
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        """
        make the bird jump
        :return: None
        """
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        """
        make the bird move 
        :return: None
        """
        self.tick_count += 1

        # for downwards acceleration 
        displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2  # calculate displacement

        # eindsnelheid 
        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:  # tilt up
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:  # tilt down
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        """
        draw the bird
        :param win: pygame window or surface
        :return: None
        """
        self.img_count += 1

           # For animation of bird, loop through three images 
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # so when bird is nose diving it isn't flapping
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2


        # tilt the bird
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        """
        gets the mask for the current image of the bird
        :return: None
        """
        return pygame.mask.from_surface(self.img)


class Pipe():
    """
    represents a pipe object
    """
    GAP = 160           #1 GAP 160 gemaakt 
    VEL = 5             #2 VEL 5 gemaakt 

    def __init__(self, x):
        """
        initialize pipe object
        :param x: int
        :param y: int
        :return" None
        """
        self.x = x
        self.height = 0

        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        self.passed = False

        self.set_height()

    def set_height(self):
        """
        set the height of the pipe, from the top of the screen
        :return: None
        """
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        """
        move pipe based on vel
        :return: None
        """
        self.x -= self.VEL

    def draw(self, win):
        """
        draw both the top and bottom of the pipe
        :param win: pygame window/surface
        :return: None
        """
        # draw top
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    def collide(self, bird, win):
        """
        returns if a point is colliding with the pipe
        :param bird: Bird object
        :return: Bool
        """
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True

        return False

class Base:
    """
    Represnts the moving floor of the game
    """
    VEL = 5                  
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y):
        """
        Initialize the object
        :param y: int
        :return: None
        """
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        """
        move floor so it looks like its scrolling
        :return: None
        """
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        """
        Draw the floor. This is two images that move together.
        :param win: the pygame surface/window
        :return: None
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


    def blitRotateCenter(surf, image, topleft, angle):
       """
       Rotate a surface and blit it to the window
       :param surf: the surface to blit to
       :param image: the image surface to rotate
       :param topLeft: the top left position of the image
       :param angle: a float value for angle
       :return: None
       """
       rotated_image = pygame.transform.rotate(image, angle)
       new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

       surf.blit(rotated_image, new_rect.topleft)

    def draw_window(win, birds, pipes, base, score, gen, pipe_ind):
       """
       draws the windows for the main game loop
       :param win: pygame window surface
       :param bird: a Bird object
       :param pipes: List of pipes
       :param score: score of the game (int)    	    	                
       :param gen: current generation
       :param pipe_ind: index of closest pipe
       """
       if gen == 0:
         gen = 1
         win.blit(bg_img, (0,0))

       for pipe in pipes:
         pipe.draw(win)

       base.draw(win)
       for bird in birds:
          # draw lines from bird to pipe
          if DRAW_LINES:
              try:
                  pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                  pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
              except:
                 pass
       # draw bird
       bird.draw(win)

       # score
       score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
       win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))
    
       # generations
       score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255,255,255))
       win.blit(score_label, (10, 10))
    
       # alive
       score_label = STAT_FONT.render("Alive: " + str(len(birds)),1,(255,255,255))
       win.blit(score_label, (10, 50))

    pygame.display.update()

   #3 veranderingen voor de fitness functie  
   def eval_genomes(genomes, config)
     """
     runs the simulation of the current population of
     birds and sets their fitness based on the distance they
     reach in the game.
     """
     global WIN, gen 
     win = WIN
     gen += 1
    
     # start by creating lists holding the genome itself, the
     # neural network associated with the genome and the
     # bird object that uses that network to play
     nets = []
     birds = []
     ge = []
      
# for genome_id, genome in genomes:
        genome.fitness = 0                          #4 start met een fitness van 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230,350))
        ge.append(genome)

#4 de fitness van elke vogel wordt bekeken, hier zit de pickel maar die hebben we niet kunnen trainen vanwege en error 
   with open('best.pickle', 'rb') as handle:
        net=pickle.load(handle)
    nets.append(net)
    birds.append(Bird(230,350))
    

    base = Base(FLOOR)
    pipes = [Pipe(700)]
    score = 0

    clock = pygame.time.Clock()

    run = True
    while run and len(birds) > 0:
        clock.tick(100)                            #5 framerate 100 gemaakt i.p.v 60

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()                              #6 zorgt ervoor dat niet alleen "loop" stopt maar spel stopt
                break

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width(): 
                pipe_ind = 1     #5 deze code zorgt ervoor dat wanneer het vogeltje de pijp voorbij vliegt dat dan de volgende pijp in frame komt
        else: 
            run: False
            break 
                                                    #7 deze "else" zorgt ervoor dat als er geen vogeltjes zijn het spel stopt

        
        for x, bird in enumerate(birds):            #8 geeft vogeltje 0.1 fitness omdat het weer een frame verder is
            bird.move()
            ge[x].fitness += 0.1
 
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:  
                bird.jump()    
        #9 De output stuurt info naar neurale netwerk; als waarde boven 0.5 is dan moet vogeltje springen

        
        base.move()

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            #10 check voor collision, haalt fitness af van birds als ze collision hebben
            for bird in birds:
                if pipe.collide(bird, win):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
           #11 wanneer een bird door een pipe komt krijgt hij 5 fitness
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        
        for bird in birds:
            if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:    #12 zorgt ervoor dat vogeltje niet over pijpen heen kan vliegen
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        draw_window(WIN, birds, pipes, base, score, gen, pipe_ind)     #13 laat score, hoeveelheid vogels, en gen zien

                                                                       #14 eindig loop na score van 25
        if score > 25:  
           pickle.dump(nets[0],open("best.pickle", "wb"))    #15 kiest "winner" voor pickle
            break           #16 stopt de loop
                            #17 with open('winner.pickle', 'wb') as f: (pickle poging)
                            #18 pickle.dump(winner,f)                  (pickle poging)


                            #19 Laadt de config file in 
  def run(config_path):
      """
      runs the NEAT algorithm to train a neural network to play flappy bird.
      :param config_file: location of config file
      :return: None
      """
      config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)    # config instellen

      #20 populatie creëren
      p = neat.Population(config)

      # Add a stdout reporter to show progress in the terminal.
      p.add_reporter(neat.StdOutReporter(True))
      stats = neat.StatisticsReporter()
      p.add_reporter(stats)
      #p.add_reporter(neat.Checkpointer(5))

      #21 25 generaties runnen
      winner = p.run(eval_genomes, 25)   #22 maakt van vogeltje dat fitness threshold heeft behaald de "winnaar"
    
      #23 score laten zien
      print('\nBest genome:\n{!s}'.format(winner))


    if __name__ == '__main__':
     # Determine path to configuration file. This path manipulation is
     # here so that the script will run successfully regardless of the
     # current working directory.   
      local_dir = os.path.dirname(__file__)     
      config_path = os.path.join(local_dir, 'config-feedforward.txt')    
      run(config_path)


