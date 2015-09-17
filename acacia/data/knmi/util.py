'''
Created on Sep 17, 2015

@author: theo
'''

import math

def distance(obj, pnt):
    dx = obj.location.x - pnt.x
    dy = obj.location.y - pnt.y
    return math.sqrt(dx*dx+dy*dy)

def closest_object(query,target):
    closest = None
    dist = 1e99
    for obj in query:
        d = distance(obj, target)
        if d < dist:
            closest = obj
            dist = d
    return closest

def sort_objects(query,target):
    objs = []
    for obj in query:
        obj.distance = distance(obj, target)
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
