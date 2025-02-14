import pygame
import random
import os
import time
pygame.font.init()  # init font

WIN_WIDTH = 600
WIN_HEIGHT = 800
PIPE_VEL = 3
FLOOR = 730
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")).convert_alpha())
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","bg.png")).convert_alpha(), (600, 900))
bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png"))) for x in range(1,4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")).convert_alpha())

class Bird:
    """
    # Bird class vertegenwoordigd de flappy bird
    """
    WIN_HEIGHT = 0
    WIN_WIDTH = 0
    MAX_ROTATION = 25
    IMGS = bird_images
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        """
        # Start het object
        :param x: starting x pos (int)
        :param y: starting y pos (int)
        :return: None
        """
        self.x = x
        self.y = y
        self.gravity = 9.8
        self.tilt = 0  # degrees to tilt
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        """
        # de bird springt
        :return: None
        """
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        """
        # laat de bird bewegen 
        :return: None
        """
        self.tick_count += 1

        # for downward acceleration
        displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2  # calculate displacement

        # terminal velocity
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
        # tekent de bird
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

        # wanneer de bird aan het kelderen is de bird niet aan het flapperen 
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2


        # kantelt de bird
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        """
        # haalt het masker voor het actuele plaatje van de bird
        :return: None
        """
        return pygame.mask.from_surface(self.img)


class Pipe():
    """
    # representeerd een pipe object 
    """
    WIN_HEIGHT = WIN_HEIGHT
    WIN_WIDTH = WIN_WIDTH
    GAP = 200
    VEL = 5

    def __init__(self, x):
        """
        # start het pipe object
        :param x: int
        :param y: int
        :return" None
        """
        self.x = x
        self.height = 0
        self.gap = 100  # gap between top and bottom pipe

        # waar de bovenkant en onderkant van de pipe is 
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        self.passed = False

        self.set_height()

    def set_height(self):
        """
        # stelt de hoogte van de pipe in, van de bovenkant van het scherm
        :return: None
        """
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        """
        # verplaatst de pipe gebaseerd op vel
        :return: None
        """
        self.x -= self.VEL

    def draw(self, win):
        """
        # tekent de bovenkant en onderkant van de pipe
        :param win: pygame window/surface
        :return: None
        """
        # teken bovenkant 
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    def collide(self, bird, win):
        """
        # komt terug als een point in aanraking komt met een pipe
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
    # vertegenwoordigd de bewegende vloer van het spel 
    """
    VEL = 5
    WIN_WIDTH = WIN_WIDTH
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y):
        """
        # start het object 
        :param y: int
        :return: None
        """
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        """
        # beweegt de vloer zodat het lijkt op scrollen 
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
        # tekent de vloer, het zijn twee tekeningen die samen bewegen 
        :param win: the pygame surface/window
        :return: None
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


    def blitRotateCenter(surf, image, topleft, angle):
        """
        # kantelt een oppervlak en het blijft bij de window
        :param surf: the surface to blit to
        :param image: the image surface to rotate
        :param topLeft: the top left position of the image
        :param angle: a float value for angle
        :return: None
        """
        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

        surf.blit(rotated_image, new_rect.topleft)

    def menu_screen(win):
        """
        # het menu scherm begint het spel
        :param win: the pygame window surface
        :return: None
        """
        pass

    def end_screen(win):
        """
        # laadt het scherm aan het eind van het spel wanneer de speler verliest 
        :param win: the pygame window surface
        :return: None
        """
        run = True
        text_label = END_FONT.render("Press Space to Restart", 1, (255,255,255))
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.KEYDOWN:
                    main(win)

            win.blit(text_label, (WIN_WIDTH/2 - text_label.get_width()/2, 500))
            pygame.display.update()

        pygame.quit()
        quit()

    def draw_window(win, birds, pipes, base, score):
        """
        # tekent de windows voor het primaire spel rondje 
        :param win: pygame window surface
        :param bird: a Bird object
        :param pipes: List of pipes
        :param score: score of the game (int)
        :return: None
        """
        win.blit(bg_img, (0,0))
    
        for pipe in pipes:
            pipe.draw(win)

        base.draw(win)
        for bird in birds:
            bird.draw(win)

        # score
        score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
        win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

        pygame.display.update()


    def main(genomes, config):
        nets = []
        ge = []
        birds = []

        # Houdt de genomes bij die de birds aanstuurt 
        for _, g in genomes: 
            net = neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)
            birds.append(Bird(230, 350))
            g.fitness = 0
    
        base = Base(FLOOR)
        pipes = [Pipe(700)]
        score = 0

        clock = pygame.time.Clock()
        start = False
        lost = False

        run = True
        while run:
            pygame.time.delay(30)
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    quit()
                    break

        if event.type == pygame.KEYDOWN and not lost:
                if event.key == pygame.K_SPACE:
                    if not start:
                        start = True
                    bird.jump()

        # Beweeg Birds, base en pipes
        if start:
            bird.move()
        if not lost:
            base.move()

            if start:
                rem = []
                add_pipe = False
                for pipe in pipes:
                    pipe.move()
                    for x, bird in enumerate(birds):
                    # check voor collision, haalt fitness af van birds als ze collision hebben
                        if pipe.collide(bird, win):
                        ge [x].fitness -= 1
                        birds.pop(x)
                        nets.pop(x)
                        ge.pop(x)

                        if not pipe.passed and pipe.x < birds.x:
                        pipe.passed = True
                        add_pipe = True
                        
                 if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                        rem.append(pipe)
                else: 
                    run = False 
                    break 

                # wanneer een bird door een pipe komt krijgt hij 5 fitness
                if add_pipe:
                    score += 1
                    for g in ge:
                        g.fitness += 5
                    pipes.append(Pipe(WIN_WIDTH))

                for r in rem:
                    pipes.remove(r)

        # haalt birds weg als ze tegen een pipe aankomen
        for x, bird in enumerate(birds):
                if bird.y + bird_images[0].get_height() - 10 >= FLOOR:
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

        draw_window(WIN, birds, pipes, base, score)

    end_screen(WIN)


    # Laadt de config file in 
    def run(config_path): 
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
                                    neat.DefaultSpeciesSet, neat.DefaultStagnation, 
                                    config_path)
        p = neat.Population(config)
    
        p.add_repoter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats) 

        winner = p.run(main,50) 

    if __name__ == "main__":
        local_dir = os.pass.dirname(__file__)
        config_path = os.path.join(local_dir, "config-feedforward.txt")
        run(config_path) 
