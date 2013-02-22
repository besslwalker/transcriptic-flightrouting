# Implementation of toy problem for Transcriptic
# Bess L. Walker
# 2-22-13

import math

# The vertices in our graph are Cities, consisting of an id, x coordinate, and y coordinate.
class City:
    def __init__(self, id, x, y):
        self.id = id
        self.x  = x
        self.y  = y
        
    def __repr__(self):
        return "".join(["<City:", str(self.id), "(", str(self.x), ",", str(self.y), ")>"])
        
    def __str__(self):
        return self.__repr__()
    
    # Returns the Euclidean distance between this City and another City    
    def distance_to(self, to_city):
        x_diff = self.x - to_city.x
        y_diff = self.y - to_city.y
        return math.sqrt(x_diff ** 2 + y_diff ** 2)
        
# The (directed) edges of our graph are Legs, consisting of a from_city and a to_city
class Leg:
    def __init__(self, from_city, to_city):
        self.from_city = from_city
        self.to_city   = to_city
        
        self.miles = from_city.distance_to(to_city)
        
    def __repr__(self):
        return "".join(["<Leg:", str(self.from_city.id), "->", str(self.to_city.id), ">"])
        
    def __str__(self):
        return self.__repr__()