'''
Created on Sep 17, 2015

@author: theo
'''

import math
from acacia.data.util import toGoogle

def distance(p1,p2):
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    return math.sqrt(dx*dx+dy*dy)

def closest_object(query,target):
    closest = None
    dist = 1e99
    p2 = toGoogle(target)
    for obj in query:
        p1 = toGoogle(obj.location)
        d = distance(p1,p2)
        if d < dist:
            closest = obj
            dist = d
    return closest

def sort_objects(query,target):
    objs = []
    p2 = toGoogle(target)
    for obj in query:
        p1 = toGoogle(obj.location)
        obj.distance = distance(p1,p2)
        objs.append(obj)
    return sorted(objs, key=lambda x: x.distance)

def closest(cls, coords, n=1):
    if n < 2:
        return closest_object(cls.objects.all(),coords)
    else:
        objs = sort_objects(cls.objects.all(),coords)
        if len(objs) > n:
            return objs[:n]
        else:
            return objs
