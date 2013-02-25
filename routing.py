# Data structures for toy problem
# Bess L. Walker
# 2-22-13

import math
from collections import deque
from collections import defaultdict
import copy

# The vertices in our graph are Cities, consisting of an id, x coordinate, and y coordinate.
class City:
    def __init__(self, id, x, y):
        self.id = id
        self.x  = x
        self.y  = y
        
        self.required_origin = False
        self.required_destination = False
        
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
        
        self.undecided = True
        self.included  = False
        self.excluded  = False
        self.implicitly_included = False
        self.explicitly_excluded = False
                
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
        
        self.from_city.required_origin = True
        self.to_city.required_destination = True
        
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
        self.cities = sorted(city_list, key = lambda city: city.id)

        self.matrix = defaultdict(dict)
        for from_city in self.cities:
            for to_city in self.cities:
                self.matrix[from_city][to_city] = Leg(from_city, to_city, exists = False)
                
         
    # Creates a copy with independent Legs but not independent Cities.            
    def deepleg_copy(self):
        cities = self.sorted_cities()
        new_routing = Routing(cities)
        new_routing.undecided = []  # We don't want all legs undecided in the copy
        
        # Copy information from this routing into the new routing
        for from_city in cities:
            for to_city in cities:
                leg = self.matrix[from_city][to_city]
                new_routing.matrix[from_city][to_city] = copy.copy(leg)
                                        
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
        return self.cities
        
    # Removes a leg from the graph, also excluding it
    def remove_leg(self, from_city, to_city):
        leg = self.matrix[from_city][to_city]
        
        leg.exists = False
        if leg.undecided:
            leg.undecided = False
        leg.included = False
        leg.excluded = True
                
    # Adds a leg to the graph
    def add_leg(self, from_city, to_city):
        leg = self.matrix[from_city][to_city]
        
        leg.exists = True
        if leg.undecided:
            leg.undecided = False
        leg.excluded = False
        leg.included = True
                
    # REMOVES a leg from the graph, excluding it, but marks it as implicitly included
    # i.e. to_city is reachable from from_city, just not directly.
    def add_implicit_leg(self, from_city, to_city):
        self.remove_leg(from_city, to_city)
        self.matrix[from_city][to_city].implicitly_included = True
        
    # Removes a leg from the graph, excluding it AND marking it explicitly excluded
    # i.e. no indirect path is possible either
    def remove_explicit_leg(self, from_city, to_city):
        self.remove_leg(from_city, to_city)
        self.matrix[from_city][to_city].explicitly_excluded = True        
    
    # Returns a new Routing in which all the a->a edges are excluded from the graph 
    # and any consequences are realized    
    def exclude_selfloops(self):
        new_routing = self.deepleg_copy()
        
        for city in new_routing.sorted_cities():
            new_routing.remove_leg(city, city)
            
        return new_routing
        
    # Returns a new Routing, in which the given leg is excluded from the graph
    # and any consequences are also realized
    def exclude_leg(self, from_city, to_city):
        excluded_routing = self.deepleg_copy()
    
        excluded_routing.remove_leg(from_city, to_city)
        
        # Optimization: include necessary path to to_city
        # If to_city is a necessary destination, and only one path
        # A->to_city is not excluded, we must include A->to_city.
        if to_city.required_destination:
            legs_to_city = [excluded_routing.matrix[A][to_city] for A in excluded_routing.sorted_cities()]
            undecided_legs_to_city = [leg for leg in legs_to_city if leg.undecided]
            excluded_legs_to_city  = [leg for leg in legs_to_city if leg.excluded]
            if len(undecided_legs_to_city) == 1 and len(excluded_legs_to_city) == len(legs_to_city) - 1:
                excluded_routing.add_leg(undecided_legs_to_city[0].from_city, to_city)
            
                    
        # Optimization: include necessary path from from_city
        # If from_city is a necessary origin, and only one path
        # from_city->B remains, we must include from_city->B.
        
        return excluded_routing
   
    # Returns a new Routing, in which the given leg is included in the graph
    # and any consequences are also realized
    def include_leg(self, from_city, to_city):
        included_routing = self.deepleg_copy()
        
        included_routing.add_leg(from_city, to_city)
        
        if from_city != to_city:
            for A in [city for city in included_routing.sorted_cities() if city not in [from_city, to_city]]:
                # Optimization 1a: exclude redundant paths to to_city
                # If A->from_city is included (or implicitly included)
                # we can exclude A->to_city, since A->from_city->to_city is now a path.
                # And we mark it implicitly included.
                leg = included_routing.matrix[A][from_city]
                if leg.included or leg.implicitly_included:
                    if included_routing.matrix[A][to_city].undecided:
                        included_routing.add_implicit_leg(A, to_city)
                
                # Optimization 1b: exclude redundant paths from from_city
                # If to_city->B is included (or implicitly included)
                # we can exclude from_city->B, since from_city->to_city->B is now a path.
                # And we mark it implicitly included.
                B = A
                leg = included_routing.matrix[to_city][B]
                if leg.included or leg.implicitly_included:
                    if included_routing.matrix[from_city][B].undecided:
                        included_routing.add_implicit_leg(from_city, B)
                        
                # Optimization 2a: exclude paths that would make this one redundant
                # If from_city->C is included (or implicitly included)
                # we can exclude C->to_city and to_city->C, since they would make from_city->to_city redundant.
                # They are NOT implicitly included, however.
                # In fact, no indirect connection corresponding to those legs should be allowed either,
                # so we mark them unreachable.
                C = A
                leg = included_routing.matrix[from_city][C]
                if leg.included or leg.implicitly_included:
                    if included_routing.matrix[C][to_city].undecided:
                        included_routing.remove_explicit_leg(C, to_city)
                    
                    if included_routing.matrix[to_city][C].undecided:
                        included_routing.remove_explicit_leg(to_city, C)
                        
                # Optimization 2b: exclude paths that would make this one redundant
                # If D->to_city is included (or implicitly included)
                # we can exclude from_city->D and D->from_city, since they would make from_city->to_city redundant.
                # And we mark them unreachable.
                D = A
                leg = included_routing.matrix[D][to_city]
                if leg.included or leg.implicitly_included:
                    if included_routing.matrix[from_city][D].undecided:
                        included_routing.remove_explicit_leg(from_city, D)
                    
                    if included_routing.matrix[D][from_city].undecided:
                        included_routing.remove_explicit_leg(D, from_city)
    
        return included_routing
        
    # Returns a list of legs, by default only those which exist.
    # Warning: setting existing_only to False will return a list that's n**2 in the number of cities.    
    def legs(self, existing_only = True):
        # "Incomprehensible list comprehension" to flatten the matrix, taken from 
        # http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
        legs = [leg for from_legs in self.matrix.values() for leg in from_legs.values()]
        
        if existing_only:
            return [leg for leg in legs if leg.exists]
        else:
            return legs
            
    # Returns a list of undecided legs
    def undecided_legs(self):
        return [leg for leg in self.legs(existing_only = False) if leg.undecided]
        
    # Returns a list of excluded legs
    def excluded_legs(self):
        return [leg for leg in self.legs(existing_only = False) if leg.excluded]
        
    # Returns a list of included legs
    def included_legs(self):
        return [leg for leg in self.legs(existing_only = False) if leg.included]
        
    # Returns True if the route from from_city to to_city is marked explicitly excluded
    # i.e. impossible.
    def explicitly_excludes(self, from_city, to_city):
        leg = self.matrix[from_city][to_city]
        if leg.explicitly_excluded:
            return True
            
        return False
        
    # Returns True if routes satisfying all tickets exist.  
    # Uses what information it can, then falls back on a naive BFS.
    def is_valid(self, tickets):
        cities = self.sorted_cities()
        
        for ticket in tickets:
            # Take advantage of what we know
            ticket_leg = self.matrix[ticket.from_city][ticket.to_city]
            if ticket_leg.included or ticket_leg.implicitly_included:
                # Hurrah, it's satisfied, we can check the next ticket.
                continue
                
            if ticket_leg.explicitly_excluded:
                # Well, we can't get there from here -- this isn't valid!
                return False
            
            # Otherwise, determine reachability via BFS
            
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
        takeoffs = len(legs)
                
        return miles * mile_cost + takeoffs * takeoff_cost
        
    # Returns a new Routing holding a simple solution to the problem: just take all the ticket legs.
    def simple(self, tickets):
        simple_routing = Routing(self.sorted_cities())
        
        for ticket in tickets:
            simple_routing.add_leg(ticket.from_city, ticket.to_city)
            
        return simple_routing
        
        
            