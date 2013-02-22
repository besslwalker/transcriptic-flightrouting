# Very basic assert-based testing for the flight routing problem.
# Bess L. Walker
# 2-22-13

import routing

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

# Check __repr__ and __str__ methods for Routing
assert repr(g) == "<Routing:a,b>"
assert str(g)  == \
"""  a b
a 0 0
b 0 0"""