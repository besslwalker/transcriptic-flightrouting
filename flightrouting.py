# Toy problem for Transcriptic
# Bess L. Walker
# 2-22-13

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
