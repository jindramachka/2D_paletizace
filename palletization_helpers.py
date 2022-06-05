from copy import deepcopy
import numpy as np

def intersects(game_field, fig_x, fig_y, game_width, game_height, game_fig_img):
    """
    Duplicated function from tetris.py intended for simulation.
    """
    intersection = False
    for i in range(6):
        for j in range(6):
            if i * 6 + j in game_fig_img:
                if i + fig_y > game_height - 1 or \
                   j + fig_x > game_width - 1 or \
                   j + fig_x < 0 or \
                   game_field[i + fig_y][j + fig_x] > 0:
                    intersection = True
    return intersection

def above_threshold(fig_y, game_fig_img, game_threshold):
    """
    Checks if the figure is placed above placement threshold.
    """
    n = 0
    for fig_i in range(6):
        for fig_j in range(6):
            if fig_i * 6 + fig_j in game_fig_img:
                if fig_i + fig_y < game_threshold:
                    n += 1
    if n == len(game_fig_img):
        return True
    return False

def get_sim_field(game_field, fig_x, fig_y, game_fig_img):
    """
    Simulates a field with a fallen figure
    """
    sim_field = deepcopy(game_field)
    for fig_i in range(6):
        for fig_j in range(6):
            if fig_i * 6 + fig_j in game_fig_img:
                sim_field[fig_i + fig_y][fig_j + fig_x] = 1

    return sim_field

def get_lines(game_field, game_height):
    """
    Counts the number of full rows and full_lines them for a given game_field.
    """
    full_lines = 0
    for field_i in range(game_height-1, -1, -1):
        if all([x != 0 for x in game_field[field_i]]):
            full_lines += 1
    return full_lines

def get_holes(game_field, fig_x, fig_y, game_width, game_height, game_fig_img):
    """
    Counts the number of holes in game_field.
    """
    holes = 0

    for fig_i in range(6):
        for fig_j in range(6):
            if fig_i * 6 + fig_j in game_fig_img:
                if fig_j + fig_x < game_width and fig_i + fig_y + 1 < game_height:
                    if game_field[fig_i + fig_y + 1][fig_j + fig_x] == 0:
                        for field_i  in range(fig_i + fig_y + 1, game_height):
                            if game_field[field_i][fig_j + fig_x] == 0:
                                holes+=1
                            else:
                                break

    return holes

def get_height_bumpiness(game_field, game_height):
    """
    Counts the aggregate height and bumpiness of game_field.
    """
    agg_height = 0
    max_height = 0
    columns = []
    bumpiness = 0

    transposed_game_field = np.array(game_field).T.tolist()
    for row in transposed_game_field:
        if all(i == 0 for i in row):
            columns.append(0)
        else:
            for i in range(game_height):
                if row[i] != 0:
                    h = game_height - i
                    if h > max_height:
                        max_height = h
                    agg_height += h
                    columns.append(h)
                    break
    for first, second in zip(columns, columns[1:]):
        bumpiness += abs(first - second)

    return max_height, bumpiness
