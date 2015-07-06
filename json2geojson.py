#### Only tested using Sidewalk, Permit and beacon dataset

import sys,json

def convert_to_geojson(json_features):
    
    geojson_features = [];

    ####  Point or Line
    type_feature = ""

    assert len(json_features)!= 0
    assert "shape" in json_features[0]

    if "geometry" in json_features[0]["shape"]:
        type_feature = "LineString"
    elif "longitude" in json_features[0]["shape"] and "latitude" in json_features[0]["shape"]:
        type_feature = "Point"
    else:
        type_feature = "Lack of coordinates information"
        
    assert type_feature != "Lack of coordinates information"

    for feature in json_features:
        new_feature = {"type":"Feature"}
        new_feature["geometry"] = {"type":type_feature}
        if(type_feature == "LineString"):
            new_feature["geometry"]["coordinates"] = feature["shape"]["geometry"]["paths"][0]
        else:
            new_feature["geometry"]["coordinates"] = [feature["shape"]["longitude"],feature["shape"]["latitude"]]
        feature.pop("shape")
        new_feature["properties"] = feature
        geojson_features.append(new_feature)
        
    geojson_file = {"type": "FeatureCollection","features":geojson_features}
    return geojson_file


if __name__ == '__main__':
    assert len(sys.argv) == 3
    input = sys.argv[1]
    output = sys.argv[2]
    with open(input) as f:
        json_features = json.load(f)
    geojson_file = convert_to_geojson(json_features)
    with open(output, "w") as f:
        json.dump(geojson_file, f)