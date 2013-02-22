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
        self.init_from_list(city_list)
                
    def init_from_list(self, city_list):
        self.matrix = {}
        for from_city in city_list:
            self.matrix[from_city] = {}
            for to_city in city_list:
                self.matrix[from_city][to_city] = Leg(from_city, to_city, exists = False)
                
    def __repr__(self):
        alpha_cities = self.sorted_cities()
        cities_str = ",".join([str(city) for city in alpha_cities])
        return "".join(["<Routing:", cities_str, ">"])
        
    def __str__(self):
        alpha_cities = self.sorted_cities()
        label_row = " ".join([" "] + [city.id for city in alpha_cities])
        
        row_strs = [label_row]

        for from_city in alpha_cities:
            adj_dict = self.matrix[from_city]
            adj_exists = [int(adj_dict[to_city].exists) for to_city in alpha_cities]
            exists_str = " ".join([str(from_city)] + [str(exists) for exists in adj_exists])
            row_strs.append(exists_str)
                    
        return "\n".join(row_strs)
    
    # Returns a list of the cities in the graph, sorted by id    
    def sorted_cities(self):
        return sorted(self.matrix.keys(), key = lambda city: city.id)
        
    # Removes a leg from the graph
    def remove_leg(self, from_city, to_city):
        self.matrix[from_city][to_city].exists = False
        
    # Adds a leg to the graph
    def add_leg(self, from_city, to_city):
        self.matrix[from_city][to_city].exists = True
        
    # Returns a new Routing that is the minimum spanning tree of the cities in this Routing.
    # The Legs of the new Routing are independent, but the Cities are not.
    # (For independent Cities, initialize mst with a deep copy of city_list.)
    def minimum_spanning_tree(self):
        city_list = self.matrix.keys()   
        mst = Routing(city_list)
        
        if len(city_list) == 0:
            return mst
        
        # Without a union-find data structure, Kruskal's MST algorithm
        # is really no better than a decent implementation of Prim's.
        # Since I've no desire to write a union-find, I'll just use Prim's.
        # This implementation is based on the one in Steven Skiena's
        # The Algorithm Design Manual, 2nd Edition, pg. 194-195
        
        # Tracking of City traits in the tree needs to happen here
        # rather than through data members of the City class, since
        # the Cities are shared across any graphs which use them.
        mst_cities = mst.sorted_cities()  # if Cities become independent, this gets the right ones.
        connected = {}
        distance  = {}
        parent    = {}
        for city in mst_cities:
            connected[city] = False
            distance[city]  = float("Inf")
            parent[city]    = None
            
        # Choose starting vertex    
        from_city = mst_cities[0]
        distance[from_city] = 0
        
        # Find MST
        while connected[from_city] == False:
            connected[from_city] = True
            
            # Weigh the edges from this city
            for to_city in mst_cities:
                edge = mst.matrix[from_city][to_city]
                if distance[to_city] > edge.miles and not connected[to_city]:
                    distance[to_city] = edge.miles
                    # Update parent and connecting edge
                    if parent[to_city]:  # If we had a parent, disconnect it
                        mst.remove_leg(parent[to_city], to_city)
                    parent[to_city] = from_city
                    mst.add_leg(parent[to_city], to_city)
                 
            from_city = mst_cities[0]
            dist = float("Inf")
            for city in mst_cities:
                if not connected[city] and dist > distance[city]:
                    dist = distance[city]
                    from_city = city
                    
                    
        return mst
                
            
            
        
        
            