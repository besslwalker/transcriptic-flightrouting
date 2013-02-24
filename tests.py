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
assert str(tri_route.cost(1.0, 0.2, tickets)) == str((1 + 2 * math.sqrt(2)) * 1.0 + 3 * 0.2)

# Test Routing's copy method and leg independence
h = tri_route.deepleg_copy()

assert str(h) == str(tri_route)
assert h.legs(existing_only = False) != tri_route.legs(existing_only = False)
