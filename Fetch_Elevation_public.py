#  Fetch_Elevation_public.py

import requests
import json
import itertools
import time
import sys
import psycopg2
from psycopg2 import extras
from polyline.codec import PolylineCodec

def get_elevation(database_table_name, api_key):

    """Adds a new table to PostGIS database with elevation and xy coordinates for sidewalks and crossings.
        Elevation data is fetched from Google's Elevation API. See: https://developers.google.com/maps/documentation/elevation/intro.
        :param api: Google API Key
        :type api: str
        """
    
    #Fetch sidewalks/crossings data from database
    ###connect to database or try to to...
    try:
        conn = psycopg2.connect(database="****",
                                user="****",
                                password="****d",
                                host="****",
                                port="****")
    except:
        print "Connection error: Unable to connect to the database"
    
    ###select cursor for dictionary
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    ###specify sql command to fetch sidewalks/crossings data
    fetch_paths = "SELECT id, iscrossing, ST_AsGeoJSON(ST_Transform(geom, 4326)) from " + str(database_table_name)

    ###execute fetch
    dict_cur.execute(fetch_paths)
    geom_list = dict_cur.fetchall()
    
    #Make new dict object with xy coordinates
    ###function to convert psycopg2 string format to dict
    def jsonify(string):
        string_jsformat = string.replace("'", "\"")
        return json.loads(string_jsformat)

    ###make empty dict that will store sidewalks/crossings geometry and eventually elevations
    nrow = len(geom_list)
    geom_dict = dict(geom_id=[None]*nrow,
                     geom_type=[None]*nrow,
                     startpoint=[None]*nrow,
                     endpoint=[None]*nrow,
                     elevation_start=[None]*nrow,
                     elevation_end=[None]*nrow)
    
    ###add start and endpoints
    for i, line in enumerate(geom_list):
        geom_id = line[0] #1st item is either id for either sidewalk or crossing
        if line[1] == 0: #2nd item is 'iscrossing' boolean
            geom_type = 'sidewalk'
        elif line[1] == 1:
            geom_type = 'crossing'
        else:
            print "Error: 'iscrossing' value not found at geom_id: %d" %geom_id
            break
        coords = jsonify(line[2])['coordinates'] #3rd item is string with coords
        startpoint = coords[0]
        endpoint = coords[-1]
        ###replacing null values at index, preferable to appending/inserting
        geom_dict["geom_id"][i] = geom_id
        geom_dict["geom_type"][i] = geom_type
        geom_dict["startpoint"][i] = startpoint
        geom_dict["endpoint"][i] = endpoint

    ###return list of unique points at vertices
    combined_points = geom_dict["startpoint"] + geom_dict["endpoint"]
    unique_combined = list(xy for xy,_ in itertools.groupby(sorted(combined_points)))

    coords_list = []
    for lon, lat in unique_combined:
        coords_list.append([lat, lon])


    #Use Google Elevation API to fetch data

    ###make request params
    url = 'https://maps.googleapis.com/maps/api/elevation/json'
    key_param = {'key': api_key}

    ###define function to grab maximum url length, given API limits
    def find_max_locations(baseurl, current_params, locations):
        ###maximum number of locations (coordinate pairs) per request for the Elevation API (should be 512)
        max_req = 512
        ###maximum total length of the URL before API returns invalid request (should be 2000)
        max_len = 2000
        
        nloc = len(locations)
        
        def get_url_len(baseurl, params):
            r = requests.Request('GET', baseurl, params=params)
            prepped = r.prepare()
            return len(prepped.url)
        
        n = 1
        while n < nloc:
            params = current_params.copy()
            encoded = PolylineCodec().encode(locations[0:n])
            params['locations'] = u'enc:' + encoded
            url_len = get_url_len(baseurl, params)
            if url_len > max_len or n > max_req:
                break
            n += 1
        
        return n
    
    ###check allowable url length
    indices = []
    start = 0
    end = 0
    while end < len(coords_list):
        coords = coords_list[start:]
        n = find_max_locations(url, key_param, coords)
        end = n + start
        indices.append([start, end])
        start = end

    coords_batchlist = [coords_list[s:e] for s, e in indices]
    print 'Number of requests to make: {}'.format(len(coords_batchlist))

    ###make xyz ref dict
    xyz_dict = dict(lonlat=list(),
                elevation=list())

    #Make API call
    for n, batch in enumerate(coords_batchlist):
        print 'Executing batch request %d of %d' %(n+1, len(coords_batchlist))
        encoded_batch = PolylineCodec().encode(batch)
        #Make batch API request, return results
        url_params = {"locations": u'enc:'+ encoded_batch,
                            "key": api_key}
        elevation_response = requests.get(url, params=url_params)
        before = time.time()
        elevation_data = elevation_response.json()
        ###check whether request returned result
        assert elevation_data['status'] == 'OK', 'Error: API request failed at batch %d' %n
        ###check that number of elevations returned by the API is consistent with the number of coordinates in batch
        error_msg = 'number of elevations in API results does not match number of coordinate in batch %d'
        assert len(elevation_data['results']) == len(batch), error_msg
        #Append each elevation in the n^th batch to a new list
        xyz_list = []
        for k, result in enumerate(elevation_data['results']):
            z = result['elevation']
            x = batch[k][1]
            y = batch[k][0]
            ###make sure things match up more or less, Google returns under 3 decimal places at times
            x_used = float("%.2f" % x)
            y_used = float("%.2f" % y)
            x_returned = float("%.2f" % result['location']['lng'])
            y_returned = float("%.2f" % result['location']['lat'])
            error_msg = "Oops! returned coordinate pair don't appear to match pair used for item %d in batch %d" %(k,n)
            assert x_used == x_returned and y_used == y_returned, error_msg
            ###add checked values
            xyz = {'lonlat':[x,y], 'elevation':z}
            xyz_list.append(xyz)
        #Add 0.2 sec timeout
        after = time.time()
        if after - before < 0.2:
            print "Waiting..."
            time.sleep(0.2-after+before)
    
    #Add elevation to geojson file
    for j in range(len(geom_dict['geom_id'])):
        start = geom_dict['startpoint'][j]
        end = geom_dict['endpoint'][j]
        for i, elevation in enumerate(xyz_dict['elevation']):
            if start == xyz_dict['lonlat'][i]:
                geom_dict['elevation_start'].insert(j, elevation)
            if end == xyz_dict['lonlat'][i]:
                geom_dict['elevation_end'].insert(j, elevation)
        assert geom_dict['elevation_start'][j] is not None, "Error at feature %d" %j
        assert geom_dict['elevation_end'][j] is not None, "Error at feature %d" %j
    
    #Write to PostGIS database
    ##make table


    try:
        conn = psycopg2.connect(database="****",
                                user="****",
                                password="****",
                                host="****",
                                port="****")
    except:
        print "Connection error: Unable to connect to the database"

    #default cursor
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE test_elevation (
            ID int primary key,
            startpoint geometry('POINT',2926),
            endpoint geometry('POINT',2926),
            geom_type varchar,
            geom_id int,
            elevation_start float,
            elevation_end float
            );
        """)

    conn.commit()


    ##add rows
    for index in range(len(geom_dict['geom_id'])):
        print index
        cur.execute("""INSERT INTO test_elevation (ID, startpoint, endpoint,geom_type, geom_id, elevation_start, elevation_end)
                VALUES (%s, ST_SetSRID(ST_GeomFromText('POINT(%s %s)'),2926),ST_SetSRID(ST_GeomFromText('POINT(%s %s)'),2926), %s, %s, %s, %s);""", (str(index),
                    geom_dict['startpoint'][index][0],
                    geom_dict['startpoint'][index][1],
                    geom_dict['endpoint'][index][0],
                    geom_dict['endpoint'][index][1],
                    str(geom_dict['geom_type'][index]),
                    str(geom_dict['geom_id'][index]),
                    str(geom_dict['elevation_start'][index]),
                    str(geom_dict['elevation_end'][index])))
    conn.commit()

    return "Database Successfully Updated!"

if __name__ == '__main__':
    assert len(sys.argv) == 3, 'Usage: python <database_table_name> <api_key>'
    database_table_name = sys.argv[1]
    api_key = sys.argv[2]
    
    get_elevation(database_table_name, api_key)