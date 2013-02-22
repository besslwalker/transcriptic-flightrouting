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
