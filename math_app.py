import math
from math import radians as rad
from math import acos as acos
from math import sin as sin
from math import cos as cos

def len_of_two_points(ola, olo, dla, dlo):
    r = 6371
    return r * acos(sin(rad(ola)) * sin(rad(dla)) + cos(rad(ola)) * cos(rad(dla)) * cos(rad(dlo) - rad(olo)))


