# -*- coding: utf-8 -*-

import random

def line(x1, y1, x2, y2):
    m = (y2 - y1)/(x2 - x1)

    #m*(x - x1) + y1
    return lambda x: m*(x - x1) + y1

def point_in_line(x1, y1, x2, y2, x, y):
    line_func = line(x1, y1, x2, y2)
    #y = m*(x - x1) + y1
    return y == line_func(x)
    
    
def objects_config():
    f = open('objects.conf', 'r')
    config = {}
    for x in f:
        if ':' in x:
            key, value = x.split(':')
            config[key] = [int(y) for y in value.split()]
    return config

def binary(n, digits=8):
    '''http://www.daniweb.com/code/snippet216539.html'''
    return "{0:0>{1}}".format(bin(n)[2:], digits)

def randpos(width, height):
    return (random.randint(20, width-40), random.randint(40, height))
    
