-- Step0: Create index on compkey
CREATE UNIQUE INDEX street_compkey ON street (compkey);
--- However, postgresql does not allow me to this because compkey is not unique. Find compkey that is not unique

select compkey,  st_asgeojson(ST_Collect(geom)) from street group by compkey having count(compkey) > 1;
-- 1186 5459 10562 comkey is not unique
/*
   1186 | {"type":"GeometryCollection","geometries":[
   {"type":"MultiLineString","coordinates":[[[1270163.60964943,222794.47695218],[1270157.03659342,222499.175063878],[1270156.79953742,222488.529559866]]]},
   {"type":"MultiLineString","coordinates":[[[1270163.60964943,222794.47695218],[1270157.03659342,222499.175063878],[1270156.79953742,222488.529559866]]]}]}
    5459 | {"type":"GeometryCollection","geometries":[
    {"type":"MultiLineString","coordinates":[[[1259372.97207038,203832.06669277],[1259362.55594237,203500.451460421],[1259352.13776636,203168.812420085]]]},
    {"type":"MultiLineString","coordinates":[[[1259372.97207038,203832.06669277],[1259362.55594237,203500.451460421],[1259352.13776636,203168.812420085]]]},
    {"type":"MultiLineString","coordinates":[[[1259372.97207038,203832.06669277],[1259362.55594237,203500.451460421],[1259352.13776636,203168.812420085]]]}]}
   10562 | {"type":"GeometryCollection","geometries":[
   {"type":"MultiLineString","coordinates":[[[1266653.09598184,239644.483241439],[1266656.93009384,239797.605033591]]]},
   {"type":"MultiLineString","coordinates":[[[1266653.09598184,239644.483241439],[1266656.93009384,239797.605033591]]]}]}
 */
 -- street with compkey includes same geom information. I remove all the repetition. 
DELETE FROM street 
WHERE id IN (
SELECT id
FROM (SELECT id,ROW_NUMBER() OVER (partition BY compkey ORDER BY id) AS rnum FROM street) as t
WHERE t.rnum > 1);
-- Now we can create index
CREATE UNIQUE INDEX street_compkey ON street (compkey);

-- Step1: Select streets
SELECT r.id, s.compkey
FROM street s
LEFT JOIN raw_sidewalks r ON s.compkey = r.segkey
WHERE r.id is null;

SELECT query.artclass, count(query.id)   FROM( 
SELECT r.id, s.compkey, s.artclass
FROM street s
LEFT JOIN raw_sidewalks r ON s.compkey = r.segkey
WHERE r.id is null ) AS query
GROUP by query.artclass;
/*
 artclass | count
----------+-------
          |     0
        4 |    30
        5 |   256
        1 |   124
        2 |    74
        9 |     1
        0 |   730
        3 |    91
(8 rows)
*/

-- See all streets without sidewalk 
SELECT s.id, s.geom
FROM street s
LEFT JOIN raw_sidewalks r ON s.compkey = r.segkey
WHERE (r.id is not null OR s.artclass < 3) 
-- We see it is very accurate that street picked by this sql code does not have sidewalks on the map.
-- Therefore, compkey is useful in two ways.
-- 1. Help us to detect those missing sidewalks. 
-- 2. Optimize polygonizing methods.

-- Step2: Polygonizing
CREATE TABLE boundary_polygons AS
SELECT g.path[1] as gid,geom
FROM(
	SELECT (ST_Dump(ST_Polygonize(picked_sidewalks.geom))).*
	FROM (
		SELECT DISTINCT ON (s.id) s.id, s.geom
		FROM street s
		LEFT JOIN raw_sidewalks r ON s.compkey = r.segkey
		WHERE r.id is not null OR s.artclass < 3) as picked_sidewalks
	) as g;

-- Step3: Remove overlap polygons
DELETE FROM boundary_polygons
WHERE gid in (
SELECT b1.gid FROM boundary_polygons b1, boundary_polygons b2
WHERE ST_Overlaps(b1.geom, b2.geom)
GROUP BY b1.gid HAVING count(b1.gid) > 1);

-- Go to group_sidewalks.sql



