#### Visualize json file using MapBox
##### Step 1: get json file from the data source.
```javascript
var data_url = "https://data.seattle.gov/resource/w47m-dg37";

// set attribute
var attr = [];
var attr_permit = ["permit_status",];
var attr_geo = ["shape","shape_length","permit_location_text"];
var attr_time = ["am_peak_hour_ok_flag", "pm_peak_hour_ok_flag", "night_weekend_only_flag"];
var attr_close = ["sidewalk_closed_flag","sidewalk_close_start_date", "sidewalk_close_end_date"];
var attr_block = ["sidewalk_blocked_flag", "sidewalk_block_start_date","sidewalk_block_end_date"];
attr =  attr.concat(attr_permit,attr_geo,attr_time,attr_close,attr_block);


// set contraints
var constraints = [];
constraints.push("(sidewalk_closed_flag = 'Y' or sidewalk_blocked_flag = 'Y')");
var today = new Date().toJSON().slice(0,10);
var timeConstraint = "(sidewalk_close_end_date >= '" + today + "' and sidewalk_close_end_date <= '"+ today + "')";
timeConstraint += " or ";
timeConstraint += "(sidewalk_block_end_date >= '" + today + "' and sidewalk_block_end_date <= '"+ today + "')";
constraints.push(timeConstraint);

var query = [];
query.push("$select = " + attr.join(','));
query.push("$where = " + constraints.join(' and '));
query.push("$limit = 50000");


var SOCRATA_KEY = "O196O9J9mXavCQov8jBhT1u75"

$.ajax({
    type: 'GET',
    url: data_url,
    data: {
        "$select":attr.join(','),
        "$where":constraints.join(' and '),
        "$limit":50000
    },
    headers:{"X-App-Token":SOCRATA_KEY},
    dataType: 'json',
    success: function(data) {
        // function drawdata is called after the json file is feteched.(I define it in step 2)
        drawdata(data);
    }
});


```

##### Step 2: draw lines/points using MapBox  
2.1 Get a mapbox token and set the basic map background.
```javascript
L.mapbox.accessToken = 'pk.eyJ1IjoieXVuaGFvY3MiLCJhIjoiaXBjOFctNCJ9.4JGjv-vwZz_ERyR5empKRg';
var map = L.mapbox.map('map', 'examples.map-h67hf2ic')
    .setView([47.6097, -122.3331], 14);
```
2.2 Add polylines
```javascript
var polylineList = [];
    function drawdata(data) {
        // For each row from the json file
        for (i = 0; i < data.length; i++) {
            var geoJSON = data[i].shape.geometry.paths[0];
            var path = [];
            // swap latitude & longitude
            for(var j = 0; j < geoJSON.length; j++){
                path.push([geoJSON[j][1],geoJSON[j][0]]);
            }
            var polyline_options = {};
            var polyline = L.polyline(path, polyline_options);
            polyline.bindPopup(L.popup().setContent("<b>Permit: " + data[i].permit_location_text));
            polylineList.push(polyline);
            polyline.addTo(map);
        }
    }
```

2.3 Add points
```javascript
var pointlist = [];
function drawpoints(data) {
    for (i = 0; i < data.length; i++) {
        // find the property that contains the location data
        var geoJSON = data[i].shape.geometry.paths[0][0];
        var path = [];
        var marker = L.marker([geoJSON[1], geoJSON[0]], {
            icon: L.mapbox.marker.icon({
                'marker-size': 'small',
                'marker-color': '#fa0'
            })
        });
        marker.addTo(map);
        marker.bindPopup(L.popup().setContent("<b>Permit: " + data[i]));
        pointlist.push(marker);
    }
}

```

##### Step3: create a HTML page to display the map
```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Bikes</title>
    <meta name="viewport" content="initial-scale=1,maximum-scale=1,user-scalable=no">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
    <script src="https://api.tiles.mapbox.com/mapbox.js/v2.1.4/mapbox.js"></script>
    <link href="https://api.tiles.mapbox.com/mapbox.js/v2.1.4/mapbox.css" rel="stylesheet">
    <style>
    body { margin:0; padding:0; }
    #map { position:absolute; top:0; bottom:0; width:100%; }
    </style>
  </head>
  <body>
    <div id="map">
      <script>
      Copy all your javascript code here.
      </script>
      </div>
    </body>
  </html>
```

#### Step 4:
Save the html file and open it in any browser. You will see the visualization of the json file.

Code:
``` javascript
L.mapbox.accessToken = 'pk.eyJ1IjoieXVuaGFvY3MiLCJhIjoiaXBjOFctNCJ9.4JGjv-vwZz_ERyR5empKRg';
var map = L.mapbox.map('map', 'examples.map-h67hf2ic')
    .setView([47.6097, -122.3331], 14);

var polylineList = [];

function drawlines(data) {
    for (i = 0; i < data.length; i++) {
        // find the property that contains the location data
        var geoJSON = data[i].shape.geometry.paths[0];
        var path = [];
        // swap latitude & longitude
        for(var j = 0; j < geoJSON.length; j++){
            path.push([geoJSON[j][1],geoJSON[j][0]]);
        }
        var polyline_options = {};
        //geoJSON = [[47.6097, -122.3331],[47.6097 + 1, -122.3331 + 1]];
        var polyline = L.polyline(path, polyline_options).addTo(map);
        polyline.bindPopup(L.popup().setContent("<b>Permit: " + data[i].permit_location_text));
        polylineList.push(polyline);
    }
}


var pointlist = [];
function drawpoints(data) {
    for (i = 0; i < data.length; i++) {
        // find the property that contains the location data
        var geoJSON = data[i].shape.geometry.paths[0][0];
        var path = [];
        var marker = L.marker([geoJSON[1], geoJSON[0]], {
            icon: L.mapbox.marker.icon({
                'marker-size': 'small',
                'marker-color': '#fa0'
            })
        });
        marker.addTo(map);
        marker.bindPopup(L.popup().setContent("<b>Permit: " + data[i]));
        pointlist.push(marker);
    }
}



var data_url = "https://data.seattle.gov/resource/w47m-dg37";

// set attribute
var attr = [];
var attr_permit = ["permit_status",];
var attr_geo = ["shape","shape_length","permit_location_text"];
var attr_time = ["am_peak_hour_ok_flag", "pm_peak_hour_ok_flag", "night_weekend_only_flag"];
var attr_close = ["sidewalk_closed_flag","sidewalk_close_start_date", "sidewalk_close_end_date"];
var attr_block = ["sidewalk_blocked_flag", "sidewalk_block_start_date","sidewalk_block_end_date"];
attr = attr.concat(attr_permit,attr_geo,attr_time,attr_close,attr_block);


// set contraints
var constraints = [];
constraints.push("(sidewalk_closed_flag = 'Y' or sidewalk_blocked_flag = 'Y')");
var today = new Date().toJSON().slice(0,10);
var timeConstraint = "(sidewalk_close_end_date >= '" + today + "' and sidewalk_close_end_date <= '"+ today + "')";
timeConstraint += " or ";
timeConstraint += "(sidewalk_block_end_date >= '" + today + "' and sidewalk_block_end_date <= '"+ today + "')";
constraints.push(timeConstraint);

var query = [];
query.push("$select = " + attr.join(','));
query.push("$where = " + constraints.join(' and '));
query.push("$limit = 50000");


var SOCRATA_KEY = "O196O9J9mXavCQov8jBhT1u75"

$.ajax({
    type: 'GET',
    url: data_url,
    data: {
        "$select":attr.join(','),
        "$where":constraints.join(' and '),
        "$limit":50000
    },
    headers:{"X-App-Token":SOCRATA_KEY},
    dataType: 'json',
    success: function(data) {
        console.log(data[0]);
        drawlines(data);
        //layerGroup.bringToBack();
    }
});
```
