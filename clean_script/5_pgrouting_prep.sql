
DROP TABLE yun_sidewalks_ready_routing;
CREATE TABLE yun_sidewalks_ready_routing AS 
SELECT row_number() over() as id, q.* FROM (
SELECT id as o_id,geom,0 as isCrossing
FROM yun_cleaned_sidewalks
UNION ALL
SELECT id as o_id, geom, 1 as isCrossing
FROM yun_connection) AS q
WHERE geometrytype(q.geom) = 'LINESTRING';