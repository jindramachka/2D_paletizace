import pygame as pg
import random
import numpy as np
from palletization_ai import run_ai, best_action

# Possible colors of the figures
colors = [
    (234, 221, 202),
    (193, 154, 107),
    (218, 160, 109),
    (196, 164, 132),
    (150, 121, 105),
    (210, 180, 140),
    (193, 154, 107)
]

class Figure:
    # Generates a list of possible figures in a 6x6 grid
    figures = []
    wh = []
    grid = np.array([
        [ 0,  1,  2,  3,  4,  5],
        [ 6,  7,  8,  9, 10, 11], 
        [12, 13, 14, 15, 16, 17],
        [18, 19, 20, 21, 22, 23],
        [24, 25, 26, 27, 28, 29],
        [30, 31, 32, 33, 34, 35]
    ])
    transposed_grid = grid.T
    pos = -1
    for grid_i in range(2, 6):
        for grid_j in range(2, 6):
            figures.append([[], []])
            pos += 1
            for fig_i in grid[0:grid_i, 0:grid_j].tolist():
                for fig_j in fig_i:
                    figures[pos][0].append(fig_j)
            for fig_i in transposed_grid[0:grid_i, 0:grid_j].tolist():
                for fig_j in fig_i:
                    figures[pos][1].append(fig_j)
            wh.append((grid_i, grid_j))

    def __init__(self, x=0, y=0):
        self.x = x # X coordinates of the figure
        self.y = y # Y coordinates of the figure
        self.type = random.randint(0, len(self.figures)-1) # Random selection of a figure type represented by an index
        self.color = random.randint(1, len(colors)-1) # Random selection of a figure color represented by an index
        self.rotation = 0 # Current rotation of the figure represented by an index

    def image(self):
        """
        Returns the type and rotation of the current figure.
        """
        return self.figures[self.type][self.rotation]

    def rotate(self):
        """
        Sets the next rotation of the figure represented by an index.
        """
        self.rotation = (self.rotation + 1) % len(self.figures[self.type])
    
class Placement:
    level = 2
    score = 0
    state = "start" # Tells us if we are still playing a placement or not
    field = [] # Field of the placement that containes 0s where it is empty, and the colors where there are figures
    x = 100 
    y = 60
    zoom = 15 # width and height of each square in the field grid
    figure = None # The current figure
    lines = []

    def __init__(self, height=0, width=0, threshold=0):
        # Height and width of the field
        self.height = height
        self.width = width
        self.threshold = self.height - threshold
        # Set up the field
        for i in range(height):
            new_line = []
            for j in range(width):
                new_line.append(0)
            self.field.append(new_line)

    def new_figure(self):
        """
        Sets up a new figure.
        """
        if self.state != "done":
            self.figure = Figure(10, 0)

    def intersects(self):
        """
        Checks if the currently flying figure is intersecting with something fixed on the field or is out of placement bounds.
        """
        intersection = False
        for i in range(6):
            for j in range(6):
                if i * 6 + j  in self.figure.image():
                    if i + self.figure.y > self.height - 1 or \
                       j + self.figure.x > self.width - 1 or \
                       j + self.figure.x < 0 or \
                       self.field[i + self.figure.y][j + self.figure.x] > 0:
                            intersection = True

        return intersection
    
    def placement_done(self):
        """
        Checks if the placement of all figures has been sufficiently completed.
        """
        row = self.field[self.threshold]
        counter = 0
        consec_zeros = []

        if all(i == 0 for i in row):
            return False
    
        for i in row:
            if i == 0:
                counter += 1
            else:
                consec_zeros.append(counter)
                counter = 0
        consec_zeros.append(counter)

        if max(consec_zeros) < 7: 
            return True
        return False

    def count_lines(self):
        """
        Destroys every full horizontal line if there are some.
        """
        new_lines = 0
        for i in range(1, self.height):
            if i not in self.lines:
                if all(x != 0 for x in self.field[i]):
                    new_lines += 1
                    self.lines.append(i)

        self.score += new_lines

    def freeze(self):
        """
        Stops the figure and freezes it when it reaches the bottom.
        Determines if placement is over.
        """
        for i in range(6):
            for j in range(6):
                if i * 6 + j  in self.figure.image():
                    self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        self.count_lines()
        self.new_figure()
        if self.placement_done():
            placement.state = "done"

    def go_down(self):
        """
        Moves the figure down by one line if it doesn't reach the bottom or some fixed figure.
        """
        self.figure.y += 1
        if self.intersects():
            self.figure.y -= 1
            self.freeze()

    def go_bottom(self):
        """
        Moves the figure down until it reaches the bottom or some fixed figure.
        """
        while not self.intersects():
            self.figure.y += 1
        self.figure.y -= 1
        self.freeze()

    def go_side(self, dx):
        """
        Moves the figure to a particular side until it goes out of bounds.
        """
        old_x = self.figure.x
        self.figure.x += dx
        if self.intersects():
            self.figure.x = old_x

    def rotate(self):
        """
        Rotates the figure by one rotation if it doesn't go out of bounds/
        """
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            self.figure.rotation = old_rotation

# Initializes the placement engine
pg.init()

# Defines some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GREY = (128, 128, 128)

size = (700, 900) # Change the width and height of the window here
screen = pg.display.set_mode(size)

# Sets up the caption
pg.display.set_caption("Palletization")

# placement loop variables
done = False
clock = pg.time.Clock()
fps = 25
placement = Placement(50, 32, 40) # Change the height, width and placement threshold of the field here
counter = 0
pressing_down = False

# placement loop
while not done:
    # Generates a new figure
    if placement.figure is None:
        placement.new_figure()
        best_position, best_rotation = best_action(placement.field, placement.figure, placement.width, placement.height, placement.threshold)

    # Slows down the falling of the figure
    counter += 1
    if counter > 100000:
        counter = 0
    
    # Moves the figure down
    if counter % (fps // placement.level // 2) == 0 or pressing_down:
        if placement.state == "start":
            placement.go_down()
    

    for event in list(pg.event.get()) + run_ai(placement.figure, best_rotation, best_position): # Loops through user's actions
        if event.type == pg.QUIT:
            done = True
        # If a button is pressed
        if event.type == pg.KEYDOWN:
            # User rotates by pressing upper arrow key
            if event.key == pg.K_UP:
                placement.rotate()
            # User moves the figure down by one row by pressing (and holding) lower arrow key
            if event.key == pg.K_DOWN:
                pressing_down = True
            # User moves the figure left by one column by pressing left arrow key
            if event.key == pg.K_LEFT:
                placement.go_side(-1)
            # User moves the figure right by one column by pressing right arrow key
            if event.key == pg.K_RIGHT:
                placement.go_side(1)
            # User moves the figure down until it reaches the bottom or a fixed figure by pressing spacebar
            if event.key == pg.K_SPACE:
                placement.go_bottom()
                best_position, best_rotation = best_action(placement.field, placement.figure, placement.width, placement.height, placement.threshold)
        # If a button is released
        if event.type == pg.KEYUP:
            # Stops the figure from moving down if the user releases lower arrow key
            if event.key == pg.K_DOWN:
                pressing_down = False

    screen.fill(WHITE)

    # Draws the field and fixed figures
    for i in range(placement.height):
        for j in range(placement.width):
            # Draws a field lattice
            pg.draw.rect(screen, GREY, 
                         [placement.x + placement.zoom * j, placement.y + placement.zoom * i, placement.zoom, placement.zoom], 2)
            
            # Draws the fixed figures
            if placement.field[i][j] > 0:
                for z in range(0, placement.zoom, 3):
                    pg.draw.rect(screen, colors[placement.field[i][j]], 
                                 [placement.x + placement.zoom * j + 1, placement.y + placement.zoom * i + 1, placement.zoom - 2, placement.zoom - 1])
    
    # Draws the falling figures
    if placement.figure is not None:
        for i in range(6):
            for j in range(6):
                if i * 6 + j in placement.figure.image():
                    for z in range(0, placement.zoom, 3):
                        pg.draw.rect(screen, colors[placement.figure.color],
                                    [placement.x + placement.zoom * (j + placement.figure.x) + 1,
                                      placement.y + placement.zoom * (i + placement.figure.y) + 1,
                                      placement.zoom - 2, placement.zoom - 2])

    # Draws threshold line
    pg.draw.line(screen, RED, (placement.x, placement.y + placement.threshold*placement.zoom), (placement.x + placement.width*placement.zoom, placement.y + placement.threshold*placement.zoom), 5)
 
    # Text
    font = pg.font.SysFont('Calibri', 25, True, False)
    font1 = pg.font.SysFont('Calibri', 65, True, False)
    text_score = font.render("Score: " + str(placement.score), True, BLACK)
    text_placement_over = font1.render("Placement Completed", True, BLACK)

    # Draws the text
    screen.blit(text_score, (0, 0))
    if placement.state == "done":
        screen.blit(text_placement_over, [10, 100])
        
    # Updates the entire surface
    pg.display.flip()

    # fps
    clock.tick(fps)

pg.quit()
