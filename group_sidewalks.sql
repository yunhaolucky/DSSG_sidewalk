
---Method1: 6387

--- Step1: Find all sidewalks what are within a polygons
CREATE TABLE grouped_sidewalks AS
SELECT b.gid as b_id, s.id as s_id, s.geom as s_geom
FROM processed_sidewalks as s
LEFT JOIN boundary_polygons  as b ON ST_Within(s.geom,b.geom);
-- 39609 sidewalks are classified in this step.

---  Step2: Find all polygons that is not assigned to any polygons because of offshoots.
UPDATE grouped_sidewalks
SET b_id = query.b_id 
FROM(
SELECT b.gid as b_id, s.s_id, s.s_geom as s_geom FROM 
(SELECT * FROM grouped_sidewalks
WHERE b_id is null) as s
INNER JOIN boundary_polygons as b ON ST_Within(ST_Line_Interpolate_Point(s.s_geom, 0.5),b.geom) = True) AS query
WHERE grouped_sidewalks.s_id = query.s_id;
-- 3222 sidewalks are classified in this step. 1 sidewalks are assiged to 2 groups. 
-- (polygons - 24403 4638, 4698)
-- SELECT ST_Within(ST_Line_Interpolate_Point(c.geom, 0.5),a.geom)  from (select * from boundary_polygons where gid = 4638) as a, (select * from boundary_polygons where gid = 4698) as b, (select * from processed_sidewalks where id = 24403) as c
/*
SELECT * FROM (
(SELECT * FROM grouped_sidewalks
WHERE b_id is null) as s
INNER JOIN boundary_polygons as b ON (ST_Intersects(s.s_geom, b.geom) AND ST_Within(ST_Line_Interpolate_Point(s.s_geom, 0.5),b.geom) = True))
WHERE  ST_Within(ST_Line_Interpolate_Point(s.s_geom, 0.5),b.geom) = False;

SELECT *, ST_Within(ST_Line_Interpolate_Point(a.s_geom, 0.5),a.geom) FROM (
SELECT b.gid as b_id, s.s_id, s.s_geom as s_geom, b.geom FROM 
(SELECT * FROM grouped_sidewalks
WHERE b_id is null) as s
INNER JOIN boundary_polygons as b ON ST_Intersects(s.s_geom, b.geom) AND ST_Within(ST_Line_Interpolate_Point(s.s_geom, 0.5),b.geom) = True) as a
WHERE a.s_id = true

*/


-- highway

--- Not important: For qgis visualization
CREATE VIEW correct_sidewalks AS
SELECT b.id as b_id, s.s_id,ST_MakeLine(ST_Line_Interpolate_Point(s.sidewalk_geom, 0.5),ST_Centroid(b.geom)) as geom FROM 
(SELECT * FROM polygon_sidewalks
WHERE b_id is null) as s
INNER JOIN boundaryPolygons as b ON ST_Intersects(s.sidewalk_geom, b.geom)
WHERE ST_Within(ST_Line_Interpolate_Point(s.sidewalk_geom, 0.5),b.geom) = True;

--- Find a bad polygon(id:666) which looks like a highway.
-- There are 57 Polygons that has centroid outside the polygon. Most of them works well with our algorithm.
CREATE VIEW bad_polygons AS
SELECT * from boundarypolygons as b
WHERE  ST_Within(ST_Centroid(b.geom), b.geom) = False;

SELECT b.id as b_id, s.s_id, FROM 
(SELECT * FROM polygon_sidewalks
WHERE b_id is null) as s
INNER JOIN boundaryPolygons as b ON ST_Intersects(s.sidewalk_geom, b.geom)
WHERE ST_Within(ST_Line_Interpolate_Point(s.sidewalk_geom, 0.5),b.geom) = True



GROUP by b.id, s_id having count(s_id) > 2


-- Step 3: Boundaries
-- There are 2779 sidewalks has not been assigned to any polygons 

SELECT s.* 
FROM (SELECT * FROM grouped_sidewalks WHERE b_id is null) as s, union_polygons as u 
WHERE ST_Intersects(s.s_geom,u.geom)


--CREATE table UNION_poly AS select st_union(geom) from boundary_polygons;
--ALTER TABLE  UNION_poly ADD id int;
--UPDATE UNION_poly
-- SET id = 1;
CREATE VIEW union_polygons AS
SELECT q.path[1] as id,geom
FROM (select (st_dump(st_union(geom))).* from boundary_polygons) AS q

-- For each unAssigned it to the closest polygons
UPDATE grouped_sidewalks
SET b_id = query.b_id
FROM (
SELECT DISTINCT ON (s.s_id) s.s_id as s_id, u.id as b_id
FROM (SELECT * FROM grouped_sidewalks
WHERE b_id is null) as s
INNER JOIN union_polygons  as u
ORDER BY s.s_id, ST_Distance(s.s_geom, u.geom)  ) AS query
WHERE grouped_sidewalks.s_id = query.s_id












