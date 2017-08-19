# CS 121: Drawing TreeMaps
# Steven Wei

import sys
import csv
import json
import tree
import drawing

from drawing import ChiCanvas, ColorKey


MIN_RECT_SIDE=0.01
MIN_RECT_SIDE_FOR_TEXT=0.03
X_SCALE_FACTOR=12
Y_SCALE_FACTOR=10


def draw_treemap(t, 
                 bounding_rec_height=1.0,
                 bounding_rec_width=1.0,
                 output_filename=None):

    '''
    Draw a treemap and the associated color key

    Inputs:
        t: a tree

        bounding_rec_height: the height of the bounding rectangle.

        bounding_rec_width: the width of the bounding rectangle.

        output_filename: (string or None) the name of a file for
        storing a the image or None, if the image should be shown.
    '''

    ### START: DO NOT CHANGE THIS CODE ###
    c = ChiCanvas(X_SCALE_FACTOR, Y_SCALE_FACTOR)

    # define coordinates for the initial rectangle for the treemap
    x_origin_init_rect = 0
    y_origin_init_rect = 0
    height_init_rect = bounding_rec_height
    width_init_rect = bounding_rec_width

    ### END: DO NOT CHANGE THIS CODE ###

    ### YOUR CODE HERE ###

    x0 = x_origin_init_rect
    y0 = y_origin_init_rect
    w = bounding_rec_width
    h = bounding_rec_height

    calculate_weights(t)
    rectangle_list = partition(t, x0, y0, w, h, left_right = True)

    draw_rectangles(c, rectangle_list)

    ### START: DO NOT CHANGE THIS CODE ###
    # save or show the result.
    if output_filename:
        print("saving...", output_filename)
        c.savefig(output_filename)
    else:
        c.show()
    ### END: DO NOT CHANGE THIS CODE ###


def calculate_weights(t):
    """
    Given a tree, this function will update the tree so that the weight of every
    node is the sum of the weights in its child(ren) nodes, and then it returns
    the root node weight

    Input:

    t: a tree

    Returns:

    total: weight of root node in t
    """

    if len(t.get_children_as_list()) == 0:
        return t.weight

    total = 0
    for node in t.get_children_as_list():
        total = total + calculate_weights(node)
    t.weight = total
    return total


def partition(t, x0, y0, w, h, left_right = True):
    """
    Given the inputs, this recursive function will grab the origin(x0, y0) and 
    dimensions(w, h) of a leaf relative to its parent in order to create a 
    rectangle. In doing is, it will return a list of all the coordinates and 
    dimensions of every leaf in the tree

    Inputs:

    t: a tree
    x0: (float) starting x-coordinate of leaf rectangle
    y0: (float) starting y-coordinate of leaf rectangle
    w: (float) width of leaf rectangle, dependent on weight of kid and parent
    h: (float) height of leaf rectangle, dependent on weight of kid and parent

    Returns:

    rectangle_list: (list) a list that contains a list of information for every
                            leaf as [code, label, x0, y0, w, h]
    """

    rectangle_list = []

    if len(t.get_children_as_list()) == 0 or w < MIN_RECT_SIDE or h < MIN_RECT_SIDE:
        return [[t.code, t.label, round(x0, 3), round(y0, 3), round(w, 3), round(h, 3)]]

    else:
        for kid in t.get_children_as_list():

            if left_right:
                w1 = w * kid.weight / t.weight
                leaf_info = partition(kid, x0, y0, w1, h, left_right = not left_right)
                rectangle_list.extend(leaf_info)
                x0 = x0 + w1
                w1 = w
                
            else:
                h1 = h * kid.weight / t.weight
                leaf_info = partition(kid, x0, y0, w, h1, left_right = not left_right)
                rectangle_list.extend(leaf_info)
                y0 = y0 + h1
                h1 = h
                
    return rectangle_list

def draw_rectangles(c, rectangle_list):
    """
    Given a canvas and a list of coordinates and dimensions, this function
    will draw the rectangles from the list of coordinates and dimensions, as 
    well as fill them in for a specific color using a color key and insert 
    the label of the text inside the respective rectangle

    Inputs:
    c: ChiCanvas canvas
    rectangle_list: (list) a list that contains a list of information for every
                            leaf as [code, label, x0, y0, w, h]

    Returns:

    A colored and labeled treemap for the information given in rectangle_list
    """

    codes = []
    for rectangle in rectangle_list:
        codes.append(rectangle[0])

    color_key = ColorKey(set(codes))

    for rectangle in rectangle_list:

        code = rectangle[0]
        color = color_key.get_color(code)
        label = rectangle[1]
        x0 = rectangle[2]
        y0 = rectangle[3]
        w = rectangle[4]
        h = rectangle[5]

        c.draw_rectangle(x0, y0, x0+w, y0+h, fill= color, outline='black',)
        if w >= MIN_RECT_SIDE_FOR_TEXT and h >= MIN_RECT_SIDE_FOR_TEXT:
            if w >= h:   
                c.draw_text(x0+w/2, y0+h/2, w*.95, label, fg="black")
            else:
                c.draw_text_vertical(x0+w/2, y0+h/2, h*.85, label, fg="black")








    