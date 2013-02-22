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
        return str(self.id)
    
    # Returns the Euclidean distance between this City and another City    
    def distance_to(self, to_city):
        x_diff = self.x - to_city.x
        y_diff = self.y - to_city.y
        return math.sqrt(x_diff ** 2 + y_diff ** 2)
        
# The (directed) edges of our graph are Legs, consisting of a from_city and a to_city
class Leg:
    def __init__(self, from_city, to_city, exists = True):
        self.from_city = from_city
        self.to_city   = to_city
        self.exists    = exists
        
        self.miles = from_city.distance_to(to_city)
        
    def __repr__(self):
        return "".join(["<Leg:", str(self.from_city.id), "->", str(self.to_city.id), ">"])
        
    def __str__(self):
        return self.__repr__()

# The graph itself is a routing, a set of legs to be flown.
# Since it is a weighted graph, it is most convenient to represent it as a Leg matrix.
# Initially, the graph is unconnected: the legs don't exist    
class Routing:
    # Initialize the empty routing
    def __init__(self, city_list):
        self.matrix = {}
        for from_city in city_list:
            self.matrix[from_city] = {}
            for to_city in city_list:
                self.matrix[from_city][to_city] = Leg(from_city, to_city, exists = False)
                
    def __repr__(self):
        cities = self.matrix.keys()
        cities_str = ",".join([str(city) for city in cities])
        return "".join(["<Routing:", cities_str, ">"])
            