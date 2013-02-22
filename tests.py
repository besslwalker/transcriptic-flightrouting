# Very basic assert-based testing for the flight routing problem.
# Bess L. Walker
# 2-22-13

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

# Check __repr__ and __str__ methods for Routing
assert repr(g) == "<Routing:a,b>"
assert str(g)  == \
"""  a b
a 0 0
b 0 0"""

# Check loading cities from file
city_list = flightrouting.load_cities("testfiles/1_city.csv")
assert len(city_list) == 1
assert repr(city_list[0]) == "<City:c(3,4)>"

# Check creating a graph from loaded cities
g1 = routing.Routing(city_list)
assert str(g1) == \
"""  c
c 0"""

# Check minimum spanning tree
# On zero nodes:
g0 = routing.Routing([])
assert str(g0.minimum_spanning_tree()) == " "
# On one node:
assert str(g1.minimum_spanning_tree()) == \
"""  c
c 0"""
# On two nodes:
g2 = g
assert str(g.minimum_spanning_tree()) == \
"""  a b
a 0 1
b 0 0"""
# On three nodes:
c3 = flightrouting.load_cities("testfiles/3_cities.csv")
g3 = routing.Routing(c3)
assert str(g3.minimum_spanning_tree()) == \
"""  a b c
a 0 0 1
b 0 0 0
c 0 1 0"""