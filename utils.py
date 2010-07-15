# -*- coding: utf-8 -*-

import random

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
    
