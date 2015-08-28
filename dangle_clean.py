""" For deleting dangles, defined as shortest two points along intersecting line """


#modules
from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
"""
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

# haversine formula
dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r


"""
    Find longest part of polyline and keep coordinates.
    Assumes only four points on along each line.
    """
def dangle_clean(lines_list, tolerance): #first arg is python list
    for num in len(range(lines_list)):
        pts = lines_list[num]
    if len(pts) == 4:
        lat1 = pts[0][0]
        lat2 = pts[1][0]
        lat3 = pts[2][0]
        lat4 = pts[3][0]
        lon1 = pts[0][1]
        lon2 = pts[0][2]
        lon3 = pts[0][3]
        lon4 = pts[0][4]
        
        dis1 = haversine(lon1, lat1, lon2, lat2) #in km
        dis2 = haversine(lon2, lat2, lon3, lat3)
        dis3 = haversine(lon3, lat3, lon4, lat4)
        
        if min(dis1,dis2,dis3) <= tolerance: # define tolerance in km
            new_lines.append(pts)
            continue
        if dis1 = max(dis1,dis2,dis3):
            coord = [(lon1, lat1), (lon2, lat2)]
        elif dis2 = max(dis1,dis2,dis3):
            coord = [(lon2, lat2), (lon3, lat3)]
        else:
            coord = [(lon3, lat3), (lon4, lat4)]
        new_lines.append(coord)
    
    elif len(pts) == 3:
        lat1 = pts[0][0]
        lat2 = pts[1][0]
        lat3 = pts[2][0]
        lon1 = pts[0][1]
        lon2 = pts[0][2]
        lon3 = pts[0][3]
        
        dis1 = haversine(lon1, lat1, lon2, lat2)
        dis2 = haversine(lon2, lat2, lon3, lat3)
        
        if min(dis1,dis2) <= tolerance:
            new_lines.append(pts)
            continue
        if dis1 = max(dis1,dis2):
            coord = [(lon1, lat1), (lon2, lat2)]
        else:
            coord = [(lon2, lat2), (lon3, lat3)]
        new_lines.append(coord)
    
    elif len(pts) == 2:
        coord = pts
        new_lines.append(coord)
    
    else:
        assert 'Error at %d' % num
