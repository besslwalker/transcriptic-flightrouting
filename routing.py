# Data structures for toy problem
# Bess L. Walker
# 2-22-13

import math
from collections import deque
from collections import defaultdict
import copy
import heapq

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
        return " -> ".join([str(self.from_city), str(self.to_city)])
        
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
    
    # Returns a list of legs which connect from_city to to_city.
    def itinerary(self, routing):
        route, discoveries = routing.possible_route(self.from_city, self.to_city)
        return route

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
            new_routing.add_implicit_leg(city, city)
            
        return new_routing
        
    # Returns a new Routing, in which the given leg is excluded from the graph
    # and any consequences are also realized
    def exclude_leg(self, from_city, to_city):
        excluded_routing = self.deepleg_copy()
    
        excluded_routing.remove_leg(from_city, to_city)
        
        # Optimization 4a: include necessary path to to_city
        # If to_city is a necessary destination, and only one leg
        # A->to_city is not excluded, we must include A->to_city.
        if to_city.required_destination:
            legs_to_city = [excluded_routing.matrix[A][to_city] for A in excluded_routing.sorted_cities()]
            undecided_legs_to_city = [leg for leg in legs_to_city if leg.undecided]
            excluded_legs_to_city  = [leg for leg in legs_to_city if leg.excluded]
            if len(undecided_legs_to_city) == 1 and len(excluded_legs_to_city) == len(legs_to_city) - 1:
                excluded_routing.add_leg(undecided_legs_to_city[0].from_city, to_city)
            
        # Optimization 4b: include necessary path from from_city
        # If from_city is a necessary origin, and only one leg
        # from_city->B remains, we must include from_city->B.
        if from_city.required_origin:
            legs_from_city = [excluded_routing.matrix[from_city][B] for B in excluded_routing.sorted_cities()]
            undecided_legs_from_city = [leg for leg in legs_from_city if leg.undecided]
            excluded_legs_from_city    = [leg for leg in legs_from_city if leg.excluded]
            if len(undecided_legs_from_city) == 1 and len(excluded_legs_from_city) == len(legs_from_city) - 1:
                excluded_routing.add_leg(from_city, undecided_legs_from_city[0].to_city)
        
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
        
    # Returns a list of legs from from_city to to_city along non-excluded edges,
    # along with a dictionary counting how many times each city was discovered during
    # the BFS.
    def possible_route(self, from_city, to_city):
        cities = self.sorted_cities()
     
        discovered = {}
        processed  = {}
        parent     = {}
        for city in cities:
            discovered[city] = 0
            processed[city]  = False
            parent[city]     = None
            
        discovered[from_city] = 1
        queue = deque([from_city])
        while len(queue) != 0:
            current_city = queue.popleft()

            # Process
            connections = [next_city for next_city in self.matrix[current_city] if not self.matrix[current_city][next_city].excluded]
            for next_city in connections:
                if not discovered[next_city]:
                    discovered[next_city] += 1
                    parent[next_city] = current_city
                    queue.append(next_city)
                elif next_city != current_city:
                    discovered[next_city] += 1
            
            processed[current_city] = True
        
        # Trace parent cities backward to create a list of legs
        reversed_legs = []
        current_city = to_city
        while current_city != from_city:
            reversed_legs.append(self.matrix[parent[current_city]][current_city])
            current_city = parent[current_city]
            
        return list(reversed(reversed_legs)), discovered
        
     
    # Returns None if there are zero or at least two possible routes on non-excluded edges.
    # If there is only one possible route, returns a list of that route's legs.
    def single_possible_route(self, from_city, to_city): 
        route, discoveries = self.possible_route(from_city, to_city)
        
        if discoveries[to_city] != 1:
            return None
        else:
            return route
    
    # Returns True if a path from from_city to to_city exists.
    # Uses what included/excluded information it has, then
    # falls back on BFS.    
    def are_connected(self, from_city, to_city):
        cities = self.sorted_cities()
        
        leg = self.matrix[from_city][to_city]
        
        if leg.included or leg.implicitly_included:
            # Yay, we know there's a path!
            return True
        elif leg.explicitly_excluded:
            # Yay, we know there's no such path!
            return False
        else:
            return to_city in self.connected_cities(from_city)
                
    # Returns a list of Cities to which the given City can connect.
    def connected_cities(self, from_city):
        cities = self.sorted_cities()
        
        discovered = {}
        processed = {}
        for city in cities:
            discovered[city] = False
            processed[city] = False
            
        discovered[from_city] = True
        queue = deque([from_city])
        while len(queue) != 0:
            current_city = queue.popleft()
            
            connections = [next_city for next_city in self.matrix[current_city] if self.matrix[current_city][next_city].exists]
            for next_city in connections:
                if not discovered[next_city]:
                    discovered[next_city] = True
                    queue.append(next_city)
                    
            processed[current_city] = True
            
        return [city for city in cities if discovered[city] == True]
        
    # Returns a list of cities which connect to the given City
    def connecting_cities(self, to_city):
        # We need a backwards BFS.  \
        # No problem, we'll look at connectED cities in a Routing with reversed edges.
        reversed_routing = Routing(self.sorted_cities())
        cities = reversed_routing.sorted_cities()
        
        for old_from_city in cities:
            for old_to_city in cities:
                if self.matrix[old_from_city][old_to_city].exists:
                    reversed_routing.add_leg(old_to_city, old_from_city)
                                        
        return reversed_routing.connected_cities(to_city)
                
    # Given a list of tickets, returns a list of those tickets that can't be satisfied.
    def unconnected_tickets(self, tickets):
        return [ticket for ticket in tickets if not self.are_connected(ticket.from_city, ticket.to_city)]
        
    # Returns True if routes satisfying all tickets exist.  
    def is_valid(self, tickets):
        return len(self.unconnected_tickets(tickets)) == 0
            
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
        
    # Returns a new Routing holding a greedy solution to the problem.
    def greedy(self, miles_cost, takeoff_cost, tickets):
        greedy_routing = Routing(self.sorted_cities())
        if len(tickets) == 0:
            return greedy_routing
                
        cities = greedy_routing.sorted_cities()
        
        ticket_queue = tickets[:]
        for ticket in ticket_queue:
            if ticket.from_city == ticket.to_city:
                ticket.cost = 0
            else:
                ticket.cost = takeoff_cost + \
                              miles_cost * greedy_routing.matrix[ticket.from_city][ticket.to_city].miles
        
        while len(ticket_queue) != 0:
            ticket = min(ticket_queue, key = lambda tt: tt.cost)
            ticket_queue.remove(ticket)
#            print ticket
            
            # Add this shortest ticket directly.
            if ticket.from_city == ticket.to_city:
                greedy_routing.add_implicit_leg(ticket.from_city, ticket.to_city)
            else:
                greedy_routing.add_leg(ticket.from_city, ticket.to_city)
                # Now update the other tickets based on this newly available leg.
                
                # For all tickets from cities A which reach from_city,
                # compare the cost of A->B to the cost of to_city->B
                # (since the cost of A->from_city->to_city is already covered).
                # Update the ticket if necessary.
                reaching_from_city = greedy_routing.connecting_cities(ticket.from_city)
                for earlier_city in reaching_from_city:
                    candidate_tickets = [tt for tt in ticket_queue if tt.from_city == earlier_city]
                    for candidate in candidate_tickets:
                        direct_cost = takeoff_cost + \
                                      miles_cost * greedy_routing.matrix[candidate.from_city][candidate.to_city].miles
                        additional_cost = takeoff_cost + \
                                      miles_cost * greedy_routing.matrix[ticket.to_city][candidate.to_city].miles
                        if additional_cost < direct_cost:  # Poor customer, no direct flight for you!
                            new_ticket = Ticket(ticket.to_city, candidate.to_city)
                            new_ticket.cost = additional_cost 
                            ticket_queue.remove(candidate)
                            ticket_queue.append(new_ticket)
                            
                
                # For all tickets to cities B which are reachable from to_city,
                # compare the cost A->B to the cost of A->from_city
                # (since the cost of from_city->to_city->B is already covered).
                # Update the ticket if necessary.
                to_city_reaches = greedy_routing.connected_cities(ticket.to_city)
                for later_city in to_city_reaches:
                    candidate_tickets = [tt for tt in ticket_queue if tt.to_city == later_city]
                    for candidate in candidate_tickets:
                        direct_cost = takeoff_cost + \
                                      miles_cost * greedy_routing.matrix[candidate.from_city][candidate.to_city].miles
                        additional_cost = takeoff_cost + \
                                      miles_cost * greedy_routing.matrix[candidate.from_city][ticket.from_city].miles
                        if additional_cost < direct_cost:  # No direct flight for you!
                            new_ticket = Ticket(candidate.from_city, ticket.from_city)
                            new_ticket.cost = additional_cost
                            ticket_queue.remove(candidate)
                            ticket_queue.append(new_ticket)                                
                                
        return greedy_routing