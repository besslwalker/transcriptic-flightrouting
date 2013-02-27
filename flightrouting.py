# Toy problem for Transcriptic
# Bess L. Walker
# 2-22-13

import sys
import routing

# File I/O

# Returns a list of City objects loaded from the given filename.
# Expects a header row; does no format checking whatsoever.
def load_cities(filename):
    city_list = []
    
    fp = open(filename)
    
    # I've never actually found the csv module terribly helpful.
    header_line = True
    for line in fp:
        # Skip the header
        if header_line:
            header_line = False
            continue
            
        stripped = line.strip()
        split    = stripped.split()
        
        id = split[0]
        x  = int(split[1])  # does no format checking
        y  = int(split[2])
        
        city_list.append(routing.City(id, x, y))
    
    fp.close()
    
    return city_list

# Returns a list of Ticket objects loaded from the given filename;
# requires a dictionary mapping city ids to City objects.    
# Expects a header row; does no format checking.
# If a ticket's origin or destination is a nonexistent city, that ticket is
# ignored and not included in the final list of Tickets.
def load_tickets(filename, city_dict):
    tickets = []
    
    fp = open(filename)
    
    header_line = True
    for line in fp:
        # skip the header
        if header_line:
            header_line = False
            continue
            
        stripped = line.strip()
        split    = stripped.split()
        
        from_id = split[0]
        to_id   = split[1]
        
        # Ignore tickets with unknown origins or destinations
        if from_id in city_dict and to_id in city_dict:
            tickets.append(routing.Ticket(city_dict[from_id], city_dict[to_id]))
    
    fp.close()
    
    return tickets
    
# Given a list of City objects, returns a dictionary mapping city ids to Cities
def make_city_dict(cities):
    city_dict = {}
    for city in cities:
        city_dict[city.id] = city
        
    return city_dict
    
# Returns a list of Tickets, sans duplicates
def dedup_tickets(tickets):
    deduped_tickets = []
    ticket_reprs = []
    for ticket in tickets:
        if not repr(ticket) in ticket_reprs:
            deduped_tickets.append(ticket)
            ticket_reprs.append(repr(ticket))
            
    return deduped_tickets
    
# Returns a list of Cities mentioned in the tickets, sorted by city_id.
def ticket_sorted_cities(tickets):
    ticket_cities = []
    for ticket in tickets:
        if ticket.from_city not in ticket_cities:
            ticket_cities.append(from_city)
        if ticket.to_city not in ticket_cities:
            ticket_cities.append(to_city)
            
    return sorted(ticket_cities, key = lambda city: city.id)

# Recursively solves the flight routing problem, returning the current best solution.   
def solve(routing, tickets, mile_cost, takeoff_cost, current_best = None):
    # Have we even got any tickets left to connect?  If not, we're done.
    if len(tickets) == 0:
        if current_best == None:
            current_best = routing
        return current_best
            
    # If we only have one ticket, we simply use the direct route -- or no route if it's a selfloop.
    if len(tickets) == 1:
        if  tickets[0].from_city != tickets[0].to_city:
            return routing.include_leg(tickets[0].from_city, tickets[0].to_city)
        else:
            return routing
        
    # We must include any legs that form the only remaining path to fulfill a ticket.
#     unconnected = routing.unconnected_tickets(tickets)
#     for ticket in unconnected:
#         route = routing.single_possible_route(ticket.from_city, ticket.to_city)
#         if route != None:  # There's exactly one possible route on non-excluded edges.
#             for route_leg in route:
#                 routing = routing.include_leg(route_leg.from_city, route_leg.to_city)
        
    # Backtracks when we've ruled out a ticket's route
    for ticket in tickets:
        if routing.explicitly_excludes(ticket.from_city, ticket.to_city):
            return current_best  # This certainly isn't better, it doesn't even work!

    # Bounds when we already know a better solution.
    if current_best != None:
        best_cost = current_best.cost(mile_cost, takeoff_cost, tickets)
        if routing.cost(mile_cost, takeoff_cost, tickets) >= best_cost:
            return current_best  # Since this one can't do better.
            
    undecided_legs = sorted(routing.undecided_legs(), key = lambda leg: leg.miles)
    
    # We've run out of choices.  Update current_best if necessary, then return it.
    if len(undecided_legs) == 0:
        if routing.is_valid(tickets):
            cost = routing.cost(mile_cost, takeoff_cost, tickets)
            if current_best == None or cost < current_best.cost(mile_cost, takeoff_cost, tickets):
                current_best = routing
#         else:
#             print routing
        return current_best
            
    branch_leg = undecided_legs[-1]
    
    # INCLUSION
    skip_inclusion = False
    
    # Bounds when including the branch leg will be too costly
    if current_best != None:
        best_cost = current_best.cost(mile_cost, takeoff_cost, tickets)
        routing_cost = routing.cost(mile_cost, takeoff_cost, tickets)
        if routing_cost + (branch_leg.miles * mile_cost) + takeoff_cost >= best_cost:
            skip_inclusion = True  # Adding this leg can't do any better
    
    if not skip_inclusion:
        included = routing.include_leg(branch_leg.from_city, branch_leg.to_city)
        current_best = solve(included, tickets, mile_cost, takeoff_cost, current_best)
    
    # EXCLUSION
    skip_exclusion = False
    
    if not skip_exclusion:
        excluded = routing.exclude_leg(branch_leg.from_city, branch_leg.to_city)
        current_best = solve(excluded, tickets, mile_cost, takeoff_cost, current_best)
    
    return current_best
    
def main(args):
    if len(args) != 3:
        print "  Usage: flightrouting.py <city_file> <ticket_file>\n"
    
    city_file = args[1]
    ticket_file = args[2]
    
    cities = load_cities(city_file)
    all_tickets = load_tickets(ticket_file, make_city_dict(cities))
    tickets = dedup_tickets(all_tickets)  # removes duplicates; they affect nothing.
    
    unrouted = routing.Routing(cities).exclude_selfloops()
    current_best = unrouted.greedy(1.0, 0.2, tickets)
    solution = solve(unrouted, tickets, 1.0, 0.2, current_best)
    
    # Show the legs to fly
    print "Legs to fly:"
    for leg in sorted(solution.legs(), key = lambda ll: str(ll.from_city) + str(ll.to_city)):
        print leg
    print
        
    # Show ticket itineraries
    print "Ticket itineraries:"
    for ticket in sorted(all_tickets, key = lambda tt: str(tt.from_city) + str(tt.to_city)):
        print str(ticket) + ": ", ", ".join([str(ll) for ll in ticket.itinerary(solution)])
    print
        
    # Show total miles and total takeoffs:
    print "Total miles:", solution.miles(tickets)
    print "Total takeoffs:", solution.takeoffs(tickets)
    
    return solution
    
if __name__ == "__main__":
    main(sys.argv)
            
        