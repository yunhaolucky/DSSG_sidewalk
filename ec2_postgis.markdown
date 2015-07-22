#### Import shape file to PostGIS
1. upload shapefile to EC2 server
```shell
# On the local machine
# get into the directory that has the private key
scp -i pgrouting.pem file_to_sent.zip ubuntu@52.11.192.158:~
```

2. Log into the EC2 server
```shell
ssh -i pgrouting.pem ubuntu@52.11.192.158
```
unzip
```
unzip file_to_sent.zip
```

3. Use shp2psql to transfer shapefile to sql
```
cd file_to_send
shp2psql file_to_send.shp new_table_name > new.sql
```

4. Run sql in the psql
```
psql -U postgres -t test new.sql
```

#### Export geojson file from PostGIS
```sql
### in the psql terminal
\o file_to_export.txt
SELECT row_to_json(fc)
 FROM ( SELECT 'FeatureCollection' As type, array_to_json(array_agg(f)) As features
 FROM (SELECT 'Feature' As type
    , ST_AsGeoJSON(lg.geom)::json As geometry
    , row_to_json((SELECT l FROM (SELECT *) As l
      )) As properties
   FROM shifted As lg   ) As f )  As fc;
\o
```

#### Export file to local machine
```
scp -i pgrouting.pem  ubuntu@52.11.192.158:~\file_to_sent.zip .
```
