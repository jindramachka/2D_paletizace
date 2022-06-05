import pygame as pg
from math import inf
from palletization_helpers import *

class Event():
    def __init__(self, type=None, key=None):
        self.type = type
        self.key = key

counter = 0
def run_ai(placement_fig, rotation, position):
    # Move the figure to the best position and set the best rotation of the figure
    if placement_fig.rotation != rotation:
        e = Event(pg.KEYDOWN, pg.K_UP)
    elif placement_fig.x < position:
        e = Event(pg.KEYDOWN, pg.K_RIGHT)
    elif placement_fig.x > position:
        e = Event(pg.KEYDOWN, pg.K_LEFT)
    else:
        e = Event(pg.KEYDOWN, pg.K_SPACE)

    return [e]


def simulate(placement_field, fig_x, fig_y, placement_width, placement_height, placement_fig_img, placement_threshold):
    """
    Counts the number of holes and height of a tower if the figure is 
    at position fig_x, fig_y and has a rotation image placement_fig_img.
    """

    # Simulates fall of a figure
    while not intersects(placement_field, fig_x, fig_y, placement_width, placement_height, placement_fig_img):
        fig_y += 1
    fig_y -= 1

    sim_field = get_sim_field(placement_field, fig_x, fig_y, placement_fig_img)

    if above_threshold(fig_y, placement_fig_img, placement_threshold):
        return -inf

    full_lines = get_lines(sim_field, placement_height)
    holes = get_holes(sim_field, fig_x, fig_y, placement_width, placement_height, placement_fig_img)
    agg_height, bumpiness = get_height_bumpiness(sim_field, placement_height)
    

    return -0.510066*agg_height + 0.760666*full_lines + -0.35663*holes + -0.184483*bumpiness
    #return agg_height, full_lines, holes, bumpiness


def best_action(placement_field, placement_fig, placement_width, placement_height, placement_threshold):
    """
    Tries all possible positions and rotations of the figure and chooses the best one.
    """
    best_position = None
    best_rotation = None
    
    prev_score = -inf
    score = -inf

    # Loop through all possible rotations of a given figure
    for rotation in range(len(placement_fig.figures[placement_fig.type])):
        fig = placement_fig.figures[placement_fig.type][rotation]
        # Loop through all possible positions
        for position in range(-5, placement_width):
            if not intersects(placement_field, position, 0, placement_width, placement_height, fig):
                score = simulate(placement_field, position, 0, placement_width, placement_height, fig, placement_threshold)
                if score > prev_score:
                    best_position = position
                    best_rotation = rotation
                    prev_score = score

    return best_position, best_rotation