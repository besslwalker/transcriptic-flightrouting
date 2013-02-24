# Data structures for toy problem
# Bess L. Walker
# 2-22-13

import math
from collections import deque

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
        return "".join(["<Leg:", str(self.from_city), "->", str(self.to_city), ">"])
        
    def __str__(self):
        return self.__repr__()
        
# A Ticket consists of an origin City, a destination City, and a list of Legs to fly.
class Ticket:
    def __init__(self, from_city, to_city):
        self.from_city = from_city
        self.to_city   = to_city
        
    def __repr__(self):
        return "".join(["<Ticket:", str(self.from_city), "->", str(self.to_city), ">"])
        
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
                
        self.undecided = self.legs(existing_only = False)
        self.included  = []
        self.excluded  = []
    
    # Creates a copy with independent Legs but not independent Cities.            
    def deepleg_copy(self):
        cities = self.sorted_cities()
        new_routing = Routing(cities)
        new_routing.undecided = []  # We don't want all legs undecided in the copy
        
        # Copy information from this routing into the new routing
        for from_city in cities:
            for to_city in cities:
                leg = self.matrix[from_city][to_city]
                new_leg = new_routing.matrix[from_city][to_city]
                if leg.exists:
                    new_routing.add_leg(from_city, to_city)
                    
                if leg in self.included:
                    new_routing.included.append(new_leg)
                elif leg in self.excluded:
                    new_routing.excluded.append(new_leg)
                else:
                    new_routing.undecided.append(new_leg)
                    
        return new_routing
                
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
    # Mostly useful to enforce an order so that output is consistent. 
    def sorted_cities(self):
        return sorted(self.matrix.keys(), key = lambda city: city.id)
        
    # Removes a leg from the graph -- undecided/included/excluded status is unaffected.
    def remove_leg(self, from_city, to_city):
        self.matrix[from_city][to_city].exists = False
        
    # Adds a leg to the graph -- undecided/included/excluded status is unaffected.
    def add_leg(self, from_city, to_city):
        self.matrix[from_city][to_city].exists = True
    
    # Returns a new Routing, in which the given leg is excluded from the graph
    def exclude_leg(self, from_city, to_city):
        excluded_routing = self.deepleg_copy()
    
        leg = excluded_routing.matrix[from_city][to_city]
        
        excluded_routing.undecided.remove(leg)
        excluded_routing.excluded.append(leg)
        excluded_routing.remove_leg(from_city, to_city)
        
        return excluded_routing
   
    # Returns a new Routing in which all the a->a edges are excluded from the graph     
    def exclude_selfloops(self):
        new_routing = self.deepleg_copy()
        
        for city in new_routing.sorted_cities():
            loop_leg = new_routing.matrix[city][city]
            
            new_routing.undecided.remove(loop_leg)
            new_routing.excluded.append(loop_leg)
            new_routing.remove_leg(city, city)
            
        return new_routing
        
        
    # Marks a leg as included in the graph.
    def include_leg(self, from_city, to_city):
        included_routing = self.deepleg_copy()
        
        leg = included_routing.matrix[from_city][to_city]
        
        included_routing.undecided.remove(leg)
        included_routing.included.append(leg)
        included_routing.add_leg(from_city, to_city)
        
        return included_routing
        
    # Returns a list of legs, by default only those which exist.
    # Warning: setting existing_only to False will return a list that's n**2 in the number of cities.    
    def legs(self, existing_only = True):
        legs = []
        for from_city in self.sorted_cities():
            from_legs = [self.matrix[from_city][to_city] for to_city in self.sorted_cities()]
            if existing_only:
                exist_legs = [leg for leg in from_legs if leg.exists]
                legs += exist_legs
            else:
                legs += from_legs
            
        return legs
        
    # Returns True if routes satisfying all tickets exist.  
    # Currently implemented naively.
    def is_valid(self, tickets):
        cities = self.sorted_cities()
        
        for ticket in tickets:
            # Determine reachability via BFS
            
            discovered = {}
            processed  = {}
            for city in cities:
                discovered[city] = False
                processed[city] = False
                
            discovered[ticket.from_city] = True
            queue = deque([ticket.from_city])
            while len(queue) != 0:
                from_city = queue.popleft()
                # If we're at the destination, we're done with this ticket.
                if from_city == ticket.to_city:
                    break
                
                # Process
                connections = [to_city for to_city in self.matrix[from_city] if self.matrix[from_city][to_city].exists]
                for to_city in connections:
                    if not discovered[to_city]:
                        discovered[to_city] = True
                        queue.append(to_city)
                
                processed[from_city] = True
            else: # Whoops, we ran out of cities to check but never found the destination!
                # This ticket can't be satisfied, so...
                return False
                
        return True
    
    # Given costs per mile and per takeoff, and a list of Tickets, 
    # returns the cost of flying those flights with this routing.
    # 
    # Currently ignores the tickets entirely and just calculates the cost of flying
    # each leg of the routing once.        
    def cost(self, mile_cost, takeoff_cost, tickets):
        legs = self.legs()
        miles = sum([leg.miles for leg in legs])
        
        # The number of takeoffs is the same as the number of cities with IN edges
        to_cities = [leg.to_city for leg in legs]
        deduped_to_cities = set(to_cities)
        takeoffs = len(deduped_to_cities)
        
        return miles * mile_cost + takeoffs * takeoff_cost
        
        
            