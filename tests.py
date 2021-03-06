# Very basic assert-based testing for the flight routing problem.
# Bess L. Walker
# 2-22-13

import math
import routing
import flightrouting

# Initialize some basic points & edges
p1 = routing.City('a', 0, 0)
p2 = routing.City('b', 1, 1)

e12 = routing.Leg(p1, p2)
e21 = routing.Leg(p2, p1)

# Check __repr__ and __str__ methods
assert repr(p1) == "<City:a(0,0)>"
assert repr(e21) == "<Leg:b->a>"

assert str(p2) == 'b'

# Check distance calculations
# I'm not sure these are actually reliable, what with floating point math and all.
assert p1.distance_to(p1) == 0.0
assert p1.distance_to(p2) == p2.distance_to(p1)

assert e21.miles == p2.distance_to(p1)

# Check leg existence
assert e12.exists == True

# Initialize a routing
g = routing.Routing([p1, p2])

assert g.matrix[p2][p2].exists == False
assert g.sorted_cities() == [p1, p2]

# Test leg addition and removal
assert g.legs() == []
g.add_leg(p2, p1)
assert str(g.legs()) == "[<Leg:b->a>]"
g.remove_leg(p2, p1)
g.remove_leg(p1, p2)
assert g.legs() == []
#assert g.included == set()  # g no longer has .included

# Check __repr__ and __str__ methods for Routing
assert repr(g) == "<Routing:a,b>"
assert str(g)  == \
"""  a b
a 0 0
b 0 0"""

# Check loading cities from file
city_list = flightrouting.load_cities("1_city.csv")
assert len(city_list) == 1
assert repr(city_list[0]) == "<City:c(3,4)>"

# Check creating a graph from loaded cities
g1 = routing.Routing(city_list)
assert str(g1) == \
"""  c
c 0"""

# Create Ticket object
t1 = routing.Ticket(p2, p1)

# Check repr() and str() methods
assert repr(t1) == "<Ticket:b->a>"

# Check routing validation
g.add_leg(p1, p2)
assert g.is_valid([t1]) == False

g.remove_leg(p1, p2)
g.add_leg(p2, p1)
assert g.is_valid([t1]) == True
assert g.is_valid([routing.Ticket(p1, p2)]) == False

g.remove_leg(p2, p1)

# Check city id to City dictionary maker
three_cities = flightrouting.load_cities("3_cities.csv")
d = flightrouting.make_city_dict(three_cities)
assert repr(d["b"]) == "<City:b(1,1)>"

# Check ticket loader
t = flightrouting.load_tickets("2_tickets.csv", d)
assert len(t) == 1
assert repr(t[0]) == "<Ticket:a->c>"

# Test cost method
g.add_leg(p2, p1)
assert g.cost(1.0, 0.2, [t1]) == e21.miles + .2

cities = flightrouting.load_cities("triangle_cities.csv")
assert str(cities) == "[<City:a(1,0)>, <City:b(0,2)>, <City:c(2,2)>, <City:d(1,1)>]"
city_dict = flightrouting.make_city_dict(cities)
tickets = flightrouting.load_tickets("triangle_tickets.csv", city_dict)
assert str(tickets) == "[<Ticket:a->b>, <Ticket:a->c>]"

tri_route = routing.Routing(cities)

# A suboptimal routing
tri_route.add_leg(city_dict["a"], city_dict["b"])
tri_route.add_leg(city_dict["a"], city_dict["c"])
assert str(tri_route) == \
"""  a b c d
a 0 1 1 0
b 0 0 0 0
c 0 0 0 0
d 0 0 0 0"""
assert tri_route.is_valid(tickets) == True
assert tri_route.are_connected(city_dict["a"], city_dict["b"]) == True
assert tri_route.are_connected(city_dict["a"], city_dict["c"]) == True
assert tri_route.connected_cities(city_dict["a"]) == [city_dict["a"], city_dict["b"], city_dict["c"]]
assert tri_route.cost(1.0, 0.2, tickets) == 2 * math.sqrt(5) * 1.0 + 2 * 0.2

tri_route.remove_leg(city_dict["a"], city_dict["b"])
tri_route.remove_leg(city_dict["a"], city_dict["c"])

# An optimal routing
tri_route.add_leg(city_dict["a"], city_dict["d"])
tri_route.add_leg(city_dict["d"], city_dict["b"])
tri_route.add_leg(city_dict["d"], city_dict["c"])
assert str(tri_route) == \
"""  a b c d
a 0 0 0 1
b 0 0 0 0
c 0 0 0 0
d 0 1 1 0"""
assert tri_route.is_valid(tickets) == True
assert tri_route.are_connected(city_dict["a"], city_dict["b"]) == True
assert tri_route.are_connected(city_dict["a"], city_dict["c"]) == True
assert tri_route.are_connected(city_dict["d"], city_dict["a"]) == False

assert tri_route.connected_cities(city_dict["a"]) == [city_dict["a"], city_dict["b"], city_dict["c"], city_dict["d"]]
assert tri_route.connected_cities(city_dict["b"]) == [city_dict["b"]]
assert tri_route.connected_cities(city_dict["c"]) == [city_dict["c"]]
assert tri_route.connected_cities(city_dict["d"]) == [city_dict["b"], city_dict["c"], city_dict["d"]]

assert tri_route.connecting_cities(city_dict["a"]) == [city_dict["a"]]
assert tri_route.connecting_cities(city_dict["b"]) == [city_dict["a"], city_dict["b"], city_dict["d"]]
assert tri_route.connecting_cities(city_dict["c"]) == [city_dict["a"], city_dict["c"], city_dict["d"]]
assert tri_route.connecting_cities(city_dict["d"]) == [city_dict["a"], city_dict["d"]]

assert str(tri_route.unconnected_tickets(tickets + [routing.Ticket(city_dict["d"], city_dict["a"])])) == "[<Ticket:d->a>]"

assert str(tri_route.cost(1.0, 0.2, tickets)) == str((1 + 2 * math.sqrt(2)) * 1.0 + 3 * 0.2)

# Test Routing's copy method and leg independence
h = tri_route.deepleg_copy()

assert str(h) == str(tri_route)
assert h.legs(existing_only = False) != tri_route.legs(existing_only = False)

# Test including and excluding legs
included = tri_route.include_leg(city_dict["a"], city_dict["b"])
#assert str(included.included) != str(tri_route.included)  # Routing no longer has .included
assert str(included) == \
"""  a b c d
a 0 1 0 1
b 0 0 0 0
c 0 0 0 0
d 0 1 1 0"""
assert tri_route.are_connected(city_dict["a"], city_dict["b"]) == True
assert tri_route.are_connected(city_dict["a"], city_dict["c"]) == True

excluded = included.exclude_leg(city_dict["d"], city_dict["b"])
#assert str(tri_route.excluded) != str(excluded.excluded)  # Routing no longer has .excluded
assert str(excluded) == \
"""  a b c d
a 0 1 0 1
b 0 0 0 0
c 0 0 0 0
d 0 0 1 0"""
assert excluded.is_valid(tickets) == True
assert excluded.cost(1.0, 0.2, tickets) == 1.0 * (math.sqrt(5) + 1 + math.sqrt(2)) + 0.2 * 3

# Test possible-route counter
one_city = flightrouting.load_cities("1_city.csv")
d = flightrouting.make_city_dict(one_city)
assert routing.Routing(one_city).single_possible_route(d["c"], d["c"]) == []

three_cites = flightrouting.load_cities("3_cities.csv")
d = flightrouting.make_city_dict(three_cities)
assert routing.Routing(three_cities).single_possible_route(d["a"], d["b"]) == None
assert str(routing.Routing(three_cities).exclude_leg(d["a"], d["b"]).single_possible_route(d["a"], d["b"])) == "[<Leg:a->c>, <Leg:c->b>]"

four_cities = flightrouting.load_cities("triangle_cities.csv")
d = flightrouting.make_city_dict(four_cities)
four = routing.Routing(four_cities)
four.remove_leg(d["a"], d["d"])
assert four.single_possible_route(d["a"], d["d"]) == None
four.remove_leg(d["a"], d["c"])
assert four.single_possible_route(d["a"], d["d"]) == None
four.remove_leg(d["b"], d["d"])
assert str(four.single_possible_route(d["a"], d["d"])) == "[<Leg:a->b>, <Leg:b->c>, <Leg:c->d>]"


# Test solver
best = flightrouting.solve(routing.Routing([]), [], 1.0, 0.2)
assert str(best) == " "

print "ONE CITY, NO TICKETS"
one_city = flightrouting.load_cities("1_city.csv")
best = flightrouting.solve(routing.Routing(one_city), [], 1.0, 0.2)
assert str(best) == \
"""  c
c 0"""

print "ONE CITY, SELFLOOP TICKET"
d = flightrouting.make_city_dict(one_city)
best = flightrouting.solve(routing.Routing(one_city), [routing.Ticket(d["c"], d["c"])], 1.0, 0.2)
assert str(best) == \
"""  c
c 0"""

three_cities = flightrouting.load_cities("3_cities.csv")
d = flightrouting.make_city_dict(three_cities)
three_routing = routing.Routing(three_cities)

print "THREE CITIES, NO TICKETS"
best = flightrouting.solve(three_routing, [], 1.0, 0.2)
assert str(best) == \
"""  a b c
a 0 0 0
b 0 0 0
c 0 0 0"""

print "THREE CITIES, ONE TICKET"
best = flightrouting.solve(three_routing, [routing.Ticket(d["a"], d["c"])], 1.0, 0.2)
assert str(best) == \
"""  a b c
a 0 0 1
b 0 0 0
c 0 0 0"""

two_tickets = [routing.Ticket(d["a"], d["c"]), routing.Ticket(d["a"], d["b"])]
print "THREE CITIES, TWO TICKETS"
best = flightrouting.solve(three_routing.exclude_selfloops(), two_tickets, 1.0, 0.2, three_routing.simple(two_tickets))
assert str(best) == \
"""  a b c
a 0 0 1
b 0 0 0
c 0 1 0"""

# Test the smallest possible use-an-intermediate-point case
tri_cities = flightrouting.load_cities("triangle_cities.csv")
tri_tickets = flightrouting.load_tickets("triangle_tickets.csv", flightrouting.make_city_dict(tri_cities))
tri_routing = routing.Routing(tri_cities)
print "TRIANGLE+CENTER CITIES"
best = flightrouting.solve(tri_routing.exclude_selfloops(), tri_tickets, 1.0, 0.2, tri_routing.simple(tri_tickets))
assert str(best) == \
"""  a b c d
a 0 0 0 1
b 0 0 0 0
c 0 0 0 0
d 0 1 1 0"""
assert str(best.cost(1.0, 0.2, tri_tickets)) == str(1.0 * (1 + 2 * math.sqrt(2)) + 0.2 * 3)

print "TRIANGLE+CENTER CITIES, GREEDY SOLUTION"
greedy = tri_routing.greedy(1.0, 0.2, tri_tickets)
assert str(greedy) == \
"""  a b c d
a 0 1 0 0
b 0 0 1 0
c 0 0 0 0
d 0 0 0 0"""
assert greedy.cost(1.0, 0.2, tri_tickets) == 1.0 * (math.sqrt(5) + 2) + 0.2 * 2

# Test with the greedy solution as the upper bound
print "TRIANGLE+CENTER CITIES, GREEDY UPPER BOUND"
best = flightrouting.solve(tri_routing.exclude_selfloops(), tri_tickets, 1.0, 0.2, tri_routing.greedy(1.0, 0.2, tri_tickets))
assert str(best) == \
"""  a b c d
a 0 0 0 1
b 0 0 0 0
c 0 0 0 0
d 0 1 1 0"""

print "TRIANGLE+CENTER CITIES, CALLING MAIN"
best = flightrouting.main(["flightrouting.py", "triangle_cities.csv", "triangle_tickets.csv"])
assert str(best) == \
"""  a b c d
a 0 0 0 1
b 0 0 0 0
c 0 0 0 0
d 0 1 1 0"""

# Test five cities
# print "FIVE CITIES, FIVE TICKETS"
# best = flightrouting.main(["flightrouting.py", "linear_cities.csv", "linear_tickets.csv"])
# assert str(best) == \
# """  a b c d e
# a 0 1 0 0 0
# b 0 0 1 0 0
# c 0 0 0 1 0
# d 0 0 0 0 1
# e 0 0 0 0 0"""

# Test ticket de-duplicator
dup_tickets = flightrouting.load_tickets("dup_tickets.csv", flightrouting.make_city_dict(tri_cities))
assert repr(dup_tickets) == "[<Ticket:a->b>, <Ticket:a->c>, <Ticket:a->b>]"
deduped_tickets = flightrouting.dedup_tickets(dup_tickets)
assert repr(deduped_tickets) == "[<Ticket:a->b>, <Ticket:a->c>]"

# Test simple heuristic (just take the tickets)
simple = routing.Routing(tri_cities).simple(tri_tickets)
assert str(simple) == \
"""  a b c d
a 0 1 1 0
b 0 0 0 0
c 0 0 0 0
d 0 0 0 0"""

# Test greedy algorithm (optimal when all cities appear on tickets)
print "GREEDY NO TICKETS"
one_city = flightrouting.load_cities("1_city.csv")
assert str(routing.Routing(one_city).greedy(1.0, 0.2, [])) == \
"""  c
c 0"""
print "GREEDY SELF-LOOP TICKET"
d = flightrouting.make_city_dict(one_city)
assert str(routing.Routing(one_city).greedy(1.0, 0.2, [routing.Ticket(d["c"], d["c"])])) == \
"""  c
c 0"""

# Greedy algorithm gives good solution that ignores city d.
print "GREEDY TRIANGLE TICKETS"
tri_cities = flightrouting.load_cities("triangle_cities.csv")
d = flightrouting.make_city_dict(tri_cities)
tri_tickets = flightrouting.load_tickets("triangle_tickets.csv", d)
greedy = routing.Routing(tri_cities).greedy(1.0, 0.2, tri_tickets)
assert str(greedy) == \
"""  a b c d
a 0 1 0 0
b 0 0 1 0
c 0 0 0 0
d 0 0 0 0"""

print "GREEDY LINEAR TICKETS"
linear_cities = flightrouting.load_cities("linear_cities.csv")
linear_dict = flightrouting.make_city_dict(linear_cities)
linear_tickets = flightrouting.load_tickets("linear_tickets.csv", linear_dict)
greedy = routing.Routing(linear_cities).greedy(1.0, 0.2, linear_tickets)
assert str(greedy) == \
"""  a b c d e
a 0 0 1 0 0
b 0 0 0 1 0
c 0 0 0 1 0
d 0 0 0 0 1
e 0 0 0 0 0"""

# Test six cities
print "SIX CITES VEE"
best = flightrouting.main(["flightrouting.py", "6_cities.csv", "vee_tickets.csv"])
assert str(best) == \
"""  a b c d e f
a 0 0 1 0 0 0
b 0 0 0 0 0 0
c 0 0 0 1 0 0
d 0 0 0 0 0 0
e 0 0 1 0 0 0
f 0 0 0 0 0 0"""

print "SIX CITIES FOUR CORNERS"
best = flightrouting.main(["flightrouting.py", "6_cities.csv", "corner_tickets.csv"])
print best
assert str(best) in \
["""  a b c d e f
a 0 1 0 0 1 0
b 0 0 0 0 0 1
c 0 0 0 0 0 0
d 0 0 0 0 0 0
e 0 0 0 0 0 0
f 0 0 0 0 0 0""",
"""  a b c d e f
a 0 0 0 0 1 0
b 0 0 0 0 0 0
c 0 0 0 0 0 0
d 0 0 0 0 0 0
e 0 0 0 0 0 1
f 0 1 0 0 0 0"""]

#print "SEVEN CITIES, TEST TICKETS"
#best = flightrouting.main(["flightrouting.py", "7_cities.csv", "tickets.csv"])
#print best