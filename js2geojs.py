import os
import sys
import json

# .json to .geojson converter
def js2geojs(items):
   
    typ = ""
    properties = []
    
    
    for i in range(len(items)):
        
        if "geometry" in items[i]["shape"]:
            typ = "LineString"
            coord = [items[i]["shape"]["geometry"]["paths"][0]]
        else:
            typ = "Point"
            coord = [items[i]["shape"]["longitude"], items[i]["shape"]["latitude"]]

        
        properties.append({"type": "Feature", #append forces sorting
                            "geometry":{
                                "type": str(typ),
                                "coordinates": coord
                                            },
                            "properties": items[i]
                                         })
    
    
    geojs = {"type": "FeatureCollection", "features": properties}    
    
    return geojs

if __name__ == '__main__': 
    
    input = sys.argv[1]
    output = sys.argv[2]
    
    with open(input) as f:
        jsfile = json.load(f)
        
    geojsfile = js2geojs(jsfile)
    
    with open(output, "w") as f:
        json.dump(geojsfile, f)
